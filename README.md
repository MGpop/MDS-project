# Ordinul Dragonului

## Despre proiect

**Ordinul Dragonului** este un joc narativ realizat în **Ren'Py**, cu elemente de explorare și RPG ușor, plasat în **Țara Românească a anului 1456**. Jucătorul intră în rolul unui agent al Ordinului Dragonului, trimis la **Târgoviște** pentru a investiga o conspirație care îl vizează pe **Vlad Țepeș**.

Proiectul urmărește să combine:
- narațiune istorică și atmosferă medievală;
- explorare pe hartă;
- progresie prin locații, NPC-uri și quest-uri;
- alegeri cu impact asupra facțiunilor și a direcției poveștii.

La nivel de concept, jocul include mai multe straturi:
- **explorare** între locații importante;
- **interacțiuni narative** cu personaje-cheie;
- **sisteme de progres** pentru inventar, quest-uri și reputație;
- **ramificații** bazate pe loialitate, informații descoperite și decizii ale jucătorului.

### Universul jocului

Acțiunea pornește în contextul întoarcerii lui Vlad Țepeș la tron. Ordinul Dragonului își trimite agentul în teren cu o misiune aparent clară, însă intriga este construită în jurul ideii că informațiile primite inițial sunt incomplete sau manipulate. Direcția dorită pentru joc este una de **mister politic**, **tensiune între facțiuni** și **dezvăluiri treptate**.

### Stack și organizare

Proiectul folosește:
- `Ren'Py 8.5.2`
- scripturi `.rpy` pentru logică, UI și narațiune
- asset-uri de UI în `game/gui/`
- background-uri de gameplay și intro în `game/images/backgrounds/`

Structura logică a proiectului este împărțită astfel:
- `game/script.rpy` — flow-ul de start și intro-ul jocului;
- `game/systems/` — sisteme de gameplay;
- `game/locations/` — locații, hartă și intrări în zone;
- `game/characters/` — definiții de personaje și date NPC;
- `game/data/` — iteme, rewards, flags, inamici;
- `game/quests/` — quest-uri și progres narativ;
- `game/ai/` — module planificate pentru adaptare și evaluare;
- `game/images/backgrounds/` — background-uri folosite în intro și pe hartă.

---

## Agenții AI

Jocul include **doi agenți AI care rulează un model de limbaj mic, local** — parte
din funcționalitatea jocului, nu unelte de dezvoltare:

- **Cronicarul** — la fiecare intrare într-o zonă, citește starea jucătorului
  (loialități, suspiciunea Ordinului, ce are în desagă) și decide ce eveniment se
  întâmplă, scriind narațiunea pe loc.
- **Dialogul liber** — scrii orice text către un NPC, iar acesta răspunde în
  caracter și decide un efect asupra stării jocului: încredere ±1, un indiciu pe
  care nu-l spune oricui, sau ostilitate care duce la luptă.

Modelul alege și scrie; jocul aplică efectul dintr-o listă albă. Dacă modelul e
oprit, lent sau întoarce gunoi, jocul cade automat pe textele scrise de mână și
merge identic mai departe.

```bash
bash scripts/setup_ai.sh     # instalează Ollama în ~/.local și descarcă modelul
```

Tasta **F9** pe hartă arată ce a decis ultimul agent, pe ce model, cu ce latență
și dacă a fost răspuns de la model sau fallback.

### Cum se comportă agenții (măsurat, nu estimat)

Rulat cu `python3 evals/run_evals.py --repetari 3`, pe CPU, fără GPU:

| agent | model | rata_model_% | potrivire_stare_% | română_% | scurgeri_% | încălcări listă albă_% | latență p50 | p95 |
|---|---|---|---|---|---|---|---|---|
| cronicar | qwen2.5:3b-instruct | 100 | 85.7 | 100 | — | 0 | 4.0s | 7.6s |
| dialog | qwen2.5:3b-instruct | 100 | 50.0 | 100 | 0 | 0 | 4.8s | 7.2s |
| cronicar | qwen2.5:1.5b-instruct | 95.2 | 57.1 | 100 | — | 0 | 1.7s | 3.5s |
| dialog | qwen2.5:1.5b-instruct | 100 | 58.3 | 90 | 0 | 0 | 2.2s | 4.1s |

De aceea implicit rulează `qwen2.5:3b-instruct`: nu ajunge niciodată pe fallback,
scrie mereu în română și nu a scăpat niciun secret. `qwen2.5:1.5b-instruct` e de
2–3 ori mai rapid și se poate alege din Opțiuni dacă laptopul de demo e mai lent.

Detalii complete: **[docs/AI_AGENTS.md](docs/AI_AGENTS.md)**.
Scenariul de prezentare: **[docs/DEMO.md](docs/DEMO.md)**.

---

## Cum rulezi

```bash
# Jocul
/cale/catre/renpy-8.5.2-sdk/renpy.sh .

# Verificarea scriptului Ren'Py
/cale/catre/renpy-8.5.2-sdk/renpy.sh . lint

# Teste automate (nu au nevoie de model local)
bash scripts/test.sh

# Evals pentru agenți (au nevoie de modelul local)
python3 evals/run_evals.py
```

---

## Status curent

Proiectul e un **vertical slice jucabil**: rulează, trece de lint și poate fi
prezentat cap-coadă.

### Ce funcționează

- **Bucla de joc:** intro → introducerea numelui → hartă în grilă 12×12 cu
  deplasare celulă cu celulă (D-pad sau WASD), minimapă cu legendă și zone blocate,
  fast-travel (`T`), inventar (`I`), jurnal de quest-uri (`J`).
- **Capitolul I complet** (`q01_investigatie`): Călin → Hanul Corbului Negru
  (alegere între a trage cu urechea și a căuta direct) → scrisoarea secretă →
  întâlnirea cu Mircea, cu luptă opțională → alegerea finală care mută loialitățile.
- **Trei zone active** cu alegeri morale: Curtea Domnească (Vlad), Pădurea Țepelor,
  Tabăra otomană (Kemal). Se deblochează treptat, iar evenimentele lor se consumă o
  singură dată.
- **Patru finaluri demo**, alese după loialitatea dominantă, accesibile din jurnal.
- **Combat** semi-real-time, cu parare și cooldown-uri independente.
- **Doi agenți AI cu model de limbaj local** (vezi mai sus), plus două euristici
  deterministe fără LLM: evaluatorul de recompense și adaptarea inamicului în luptă.
- **Harta se auto-verifică la pornire:** `validate_world_grid()` refuză în tăcere
  să lase două zone să se atingă direct, un drum fără nume sau o zonă inaccesibilă.
  Aceleași verificări rulează și în teste.

### Ce urmează

- Capitolele II–V propriu-zise (`quests/quest_data.rpy`, `side_quests.rpy`).
- Audio.
- Restul livrabilelor de proces (vezi mai jos).

---

## Procesul de dezvoltare (componenta B)

| Cerință | Unde se găsește | Stare |
|---|---|---|
| User stories, backlog | — | de făcut |
| Diagrame | — | de făcut |
| Source control cu git | istoricul repo-ului, branch-uri, PR-uri | în lucru |
| Teste automate + evals pentru agenți | [`tests/`](tests/) (56 de teste), [`evals/`](evals/), `bash scripts/test.sh` | gata |
| Raportare bug + rezolvare prin PR | — | de făcut |
| Pipeline CI/CD | [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | gata |
| Raport despre folosirea AI | jurnal brut în `logs/llm_calls.jsonl` | de făcut |

### Structura codului

- `game/script.rpy` — flow-ul de start;
- `game/systems/` — hartă, fast-travel, combat, inventar, quest-uri, NPC-uri;
- `game/locations/` — locații și intrările în zone;
- `game/characters/` — personaje și date NPC;
- `game/data/` — iteme, recompense, flags, inamici;
- `game/quests/` — quest-uri și progres narativ;
- `game/ai/` — legătura dintre joc și agenții AI;
- `game/python-packages/` — Python pur, fără Ren'Py, deci testabil cu pytest:
  - `dragon_world/` — grila lumii și validarea ei;
  - `dragon_ai/` — agenții, prompturile, validarea răspunsurilor, fallback-urile.
