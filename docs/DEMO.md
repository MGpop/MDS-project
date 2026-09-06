# Scenariu de prezentare (10 minute)

Ordinea e gândită ca profesorul să vadă agenții AI cât mai devreme și cât mai clar.

## Înainte să începi

```bash
# 1. Modelul local trebuie să răspundă
curl -s http://127.0.0.1:11434/api/tags | head -c 120

# 2. Dacă nu răspunde:
bash scripts/setup_ai.sh

# 3. Pornește jocul din timp — încălzirea modelului se face automat la pornire
/cale/catre/renpy-8.5.2-sdk/renpy.sh .
```

**Important:** pornește jocul cu 2–3 minute înainte. La prima rulare după boot,
Ollama citește ~2GB de pe disc; jocul face încălzirea în fundal, dar are nevoie
de acele secunde.

## Minutul 1–2 — Contextul

- Ce e jocul: Ordinul Dragonului, Țara Românească 1456, agent prins între Vlad,
  boieri și otomani.
- Arată harta: grilă 12×12, minimapa cu legendă, zonele blocate întunecate.
- Un pas spre o zonă blocată → mesajul explicativ, nu buton mort.

## Minutul 2–4 — Agentul 1: Cronicarul

1. Apasă **F9** ca să deschizi panoul de debug al agenților.
2. Intră într-o zonă. Se vede „Cronicarul cântărește locul…", apoi narațiunea.
3. În panou: ce model a rulat, latența, **motivul** pentru care agentul a ales
   acel eveniment și JSON-ul brut întors de model.
4. Spune limpede ce face agentul: primește starea jucătorului, alege un eveniment
   dintr-o listă albă și scrie narațiunea pe loc.
5. Arată efectul mecanic: dacă a ales `order_watch`, „Suspiciune Ordin" crește în
   panoul din stânga jos.

**Contrastul care convinge:** intră în aceeași zonă cu loialități diferite (sau
încarcă un save cu altă stare) → alt eveniment, alt text, alt motiv.

## Minutul 4–7 — Agentul 2: Dialogul liber

1. Mergi la un NPC (Călin în Târgoviște, Mircea la han) și apasă **Enter** / ●.
2. Alege „Vorbește liber" și **scrie ceva ce nu e în niciun script** — cere-i
   profesorului o propoziție, e cel mai bun moment al demo-ului.
3. NPC-ul răspunde în caracter. În panoul F9 se vede efectul ales de model.
4. Arată că dialogul chiar schimbă starea: încearcă o replică amenințătoare la
   Mircea → încrederea scade (sau devine ostil și începe lupta).
5. Arată garda: întreabă-l pe Călin despre ceva ce nu are voie să știe (facțiunile
   din Ordin) → refuză în caracter, pentru că persona îi spune explicit ce nu știe.

## Minutul 7–8 — Ce se întâmplă când modelul cade

Cel mai convingător moment tehnic:

```bash
pkill -f "ollama serve"
```

Joacă aceleași scene. Totul funcționează identic, pe textele deterministe, iar
panoul F9 arată „Sursă: FALLBACK". Jocul nu se rupe niciodată, indiferent ce face
modelul.

## Minutul 8–10 — Procesul

- `bash scripts/test.sh` — testele automate rulează fără model local, cu un LLM fals.
- `python3 evals/run_evals.py` — evals pe modelul real: rata de folosire a modelului,
  potrivirea cu starea, rata de scurgere a secretelor, latențe. Arată tabelul din
  `evals/results/ultimul-raport.md`.
- `.github/workflows/ci.yml` — testele rulează la fiecare push și PR.
- `logs/llm_calls.jsonl` — fiecare apel către model, cu prompt, răspuns brut și latență.

## Dacă ceva merge prost

| Problemă | Ce faci |
|---|---|
| Modelul răspunde greu | Opțiuni → Agenți AI → `qwen2.5:1.5b-instruct` |
| Vrei să eviți orice risc | Opțiuni → Agenți AI → oprește agenții; jocul merge pe texte scrise de mână |
| Jocul pare blocat la un agent | Așteaptă — există timeout dur, după care preia fallback-ul automat |
