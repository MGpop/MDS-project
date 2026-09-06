# Agenții AI din *Ordinul Dragonului*

Jocul conține **doi agenți AI care rulează un model de limbaj mic, local**, ca parte
din funcționalitate — nu ca unelte de scris cod. Fără internet, fără cheie de API,
fără cont: totul rulează pe laptopul care ține demo-ul.

| Agent | Unde apare în joc | Ce decide | Fișiere |
|---|---|---|---|
| **Cronicarul** | La fiecare intrare într-o zonă nouă | Ce eveniment se întâmplă și cum e povestit | `game/ai/environment_director.rpy`, `dragon_ai/agents.py` |
| **Dialogul liber** | „Vorbește liber" cu orice NPC (tasta ● / Enter pe hartă) | Ce răspunde NPC-ul și ce efect are discuția asupra stării jocului | `game/ai/dialogue_agent.rpy`, `dragon_ai/personas.py` |

Al treilea agent, evaluatorul de recompense (`game/ai/reward_evaluator.rpy`), și
adaptarea inamicului în luptă (`game/ai/combat_adaptation.rpy`) sunt euristici
deterministe, fără model de limbaj. Le-am păstrat pentru că sunt utile în joc,
dar nu ele sunt cei doi agenți ceruți.

## Cum se instalează modelul

```bash
bash scripts/setup_ai.sh                        # qwen2.5:3b-instruct (implicit)
bash scripts/setup_ai.sh qwen2.5:1.5b-instruct  # varianta rapidă
```

Scriptul instalează Ollama în `~/.local` (fără `sudo`), pornește serverul pe
`127.0.0.1:11434` și descarcă modelul. Rulează-l o singură dată per laptop.

Din joc, modelul se schimbă din **Opțiuni → Agenți AI**, unde se vede și dacă
modelul local răspunde în momentul acela.

## Cum funcționează, pas cu pas

Amândoi agenții urmează același traseu, iar fiecare pas există dintr-un motiv:

```
starea jocului
   -> prompt (dragon_ai/prompts.py)
   -> model local, mod JSON (dragon_ai/client.py)
   -> validare strictă (dragon_ai/validate.py)
   -> efect din listă albă (dragon_ai/schemas.py)
   -> fallback determinist dacă ceva a mers prost (dragon_ai/fallbacks.py)
```

**Modelul alege și scrie; jocul aplică.** Consecința mecanică nu vine niciodată
din text liber, ci e legată de id-ul ales, dintr-o listă albă. Un model care
halucinează poate cel mult alege prost evenimentul — nu poate strica starea.

Ce oprește fiecare fel de greșeală tipică a unui model mic:

| Ce greșește modelul | Ce se întâmplă |
|---|---|
| JSON stricat sau text pe lângă JSON | `parse_json_lax` recuperează obiectul; dacă nu poate, se trece pe fallback |
| Inventează un efect („îi dai toți banii") | Efectul e respins, replica rămâne, starea nu se schimbă |
| Alege un eveniment nepermis aici (ambuscadă la Curtea Domnească) | Răspuns respins, se folosește euristica |
| Scrie `[player_name]` sau `{b}` în text | `escape_renpy` le dublează, altfel Ren'Py ar arunca o excepție |
| Scrie un paragraf întreg | Textul e tăiat la ultima limită de propoziție |
| Nu răspunde / e oprit / e prea lent | Se așteaptă cel mult câteva secunde, apoi preia textul scris de mână |
| Încearcă să spună secrete din capitolele următoare | Persona îi spune explicit ce NU știe; evals măsoară rata de scurgere |

**Demo-ul merge și fără model.** Oprește Ollama și joacă din nou aceleași scene:
totul funcționează identic, pe textele deterministe. E și un test de acceptare,
nu doar o promisiune (vezi mai jos).

## De ce agenții nu ajung în save file

Clientul are un `threading.Lock`, iar Ren'Py încearcă să serializeze în save orice
variabilă din store modificată după `init`. De aceea instanțele vii ale agenților
stau ca atribute de modul, în `dragon_ai/runtime.py`, nu în store-ul Ren'Py.
Variabilele temporare din label-uri încep toate cu `_`, pe care Ren'Py oricum nu
le salvează.

## Capcana Ren'Py de evitat: `pause` sub un ecran modal

Ecranul „se gândește" **trebuie** să aibă propriul `timer ... action Return()`, iar
bucla de așteptare să-l reafișeze cu `call screen`:

```renpy
screen ai_thinking(mesaj):
    modal True
    timer 0.15 action Return()      # asta ține bucla în mișcare
    ...

label ai_wait_screen(cutie, timeout, mesaj):
    $ _ai_limita = ai_deadline(timeout)
    while ai_still_waiting(cutie, _ai_limita):
        call screen ai_thinking(mesaj)
    return
```

Varianta care pare mai naturală — `show screen` plus `pause 0.1` într-un `while` —
**blochează jocul la infinit**: sub un ecran `modal True`, `pause` nu se mai
termină niciodată, deci bucla nu ajunge să vadă că răspunsul a sosit. A fost un
bug real, iar modelul răspundea corect tot timpul. Același tipar corect e folosit
și de `screen combat_wait`.

Traseul complet (fir separat + ecran + citirea rezultatului) se poate verifica cu
`tests/renpy_selftest.rpy.disabled` — instrucțiunile sunt în capul fișierului.

## A doua capcană Ren'Py: `None` într-un meniu

`renpy.display_menu` sare peste orice intrare a cărei valoare e `None`
(`renpy/exports/menuexports.py`: `if val is None: continue`) — o folosește ca
titlu de meniu, nu ca buton. O opțiune de tip „Anulează" cu valoarea `None` apare
pe ecran, dar nu poate fi apăsată. Folosește un marcaj propriu:

```renpy
$ _items.append((u"Nu acum", "__inapoi__"))     # NU None
```

## Latență

Măsurat pe CPU (fără GPU), pentru răspunsuri de 60–90 de tokeni:

- `qwen2.5:3b-instruct` — ~18 tok/s
- `qwen2.5:1.5b-instruct` — de circa 2–3 ori mai rapid, cu o română mai șchioapă

Două lucruri țin latența sub control:

1. **`keep_alive: 45m`** la fiecare cerere — fără el, Ollama descarcă modelul din
   RAM după 5 minute, iar prima replică de după o pauză durează zeci de secunde.
2. **Încălzire la pornirea jocului** (`label splashscreen`) — primul apel după
   pornirea calculatorului citește ~2GB de pe disc; îl facem în fundal, înainte
   să aibă cineva nevoie de el.

Cronicarul poate rula pe un model mai mic decât dialogul (`chronicler_model` în
`dragon_ai/config.py`): el intră în funcțiune la fiecare schimbare de zonă, deci
contează viteza; la dialog contează calitatea limbii.

## Teste și evals

```bash
bash scripts/test.sh                 # teste automate, fără model local
python3 evals/run_evals.py           # evals pe modelul real
python3 evals/run_evals.py --compara qwen2.5:3b-instruct,qwen2.5:1.5b-instruct
```

**Testele** (`tests/`) rulează agenții cu un LLM fals și verifică logica: validare,
liste albe, fallback-uri, ce intră și ce nu intră în prompt. Rulează în CI, unde
nu există niciun model.

**Evals** (`evals/`) rulează cazuri reale prin modelul local și măsoară:

| Metrică | Ce înseamnă |
|---|---|
| `rata_model_%` | de câte ori răspunsul modelului a fost bun și nu s-a ajuns pe fallback |
| `potrivire_stare_%` | a ales agentul ce ar fi ales și un om, dată fiind starea |
| `scurgeri_%` | de câte ori NPC-ul a spus ce nu avea voie să știe (inclusiv la injecție de prompt) |
| `romana_%` | modelele mici o iau uneori pe engleză |
| `latenta_p50_s`, `latenta_p95_s` | dacă demo-ul rămâne jucabil |

### Cum se citesc cifrele

`potrivire_stare_%` compară alegerea agentului cu o listă de variante pe care le-ar
fi ales și un om. E o metrică cu variație mare: modelele rulează cu temperatură
0.8, iar unele cazuri au o singură variantă acceptată. Rulează cu `--repetari 3`
sau mai mult înainte să tragi concluzii dintr-o diferență de câteva procente.

`scurgeri_%` numără doar ce afirmă NPC-ul de la el. Un termen interzis care apare
deja în întrebarea jucătorului nu se pune la socoteală — „Nu știu cine a câștigat
în 1998" e un refuz corect, nu o scurgere.

Rezultatele se scriu în `evals/results/`. Fiecare apel către model e jurnalizat în
`logs/llm_calls.jsonl` (prompt, răspuns brut, latență, valid/invalid) — util și
pentru raportul despre folosirea AI.

## Ce se vede la prezentare

Tasta **F9** pe hartă deschide panoul de debug al agenților: ce agent a rulat, pe
ce model, dacă răspunsul a venit de la model sau de la fallback, latența, motivul
pe care l-a dat agentul pentru alegerea lui și JSON-ul brut. Fără el, nu se vede
că în spate chiar rulează un model.
