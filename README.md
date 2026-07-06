# IMPORTANT!!!

Secțiunea **Releases** de pe GitHub (în dreapta) conține fișierele necesare pentru folosirea AI-ului.

Fișierele dezarhivate se adăugă în folder-ul principal al jocului. Nu în folder-ul game.



# Ordinul Dragonului

## Despre proiect

**Ordinul Dragonului** este un joc narativ realizat în **Ren'Py**, cu elemente de explorare, combat simplificat, inventar și interacțiuni asistate de AI. Acțiunea este plasată în **Țara Românească a anului 1456**, într-un context istoric-fantastic inspirat de întoarcerea lui **Vlad Țepeș** la tron.

Jucătorul pornește dintr-un sat și ajunge treptat către han, pădure, Târgoviște, Curtea Domnească și alte zone importante. Proiectul urmărește să combine:

- explorare pe hartă;
- interacțiuni cu NPC-uri;
- quest-uri principale și secundare;
- combat tactic simplificat;
- inventar, arme și recompense;
- agenți AI locali pentru dialog și decizii adaptive.

---

## Status curent

Proiectul este în stadiu de **prototype / demo jucabil**. Nu este încă feature complete, dar are deja un flow de joc funcțional:

- start în sat;
- explorare pe hartă;
- NPC-uri vizibile pe hartă;
- întâlnire cu bătrânul satului;
- tutorial cu lupul;
- han și boier;
- pădure și haiduc;
- acces condiționat către Târgoviște;
- inventar;
- sistem de arme;
- consum de merinde pentru vindecare;
- side-quest demonstrativ cu ghicitorul și AI local.

---

## Tehnologii folosite

- **Ren'Py 8.5.2** pentru joc;
- scripturi `.rpy` pentru logică, UI, hartă, combat și quest-uri;
- **Python 3.11 embeddable** pentru serverul AI local;
- **FastAPI** și **Uvicorn** pentru backend-ul AI;
- **GPT4All** pentru rularea unui model local `.gguf`;
- fișiere JSON pentru date AI, precum ghicitori și configurare.

---

## Structura proiectului

Fișiere importante:

- `game/systems/map_system.rpy` — navigația pe hartă;
- `game/locations/location_data.rpy` — grila lumii, zone, culori minimap și background-uri;
- `game/locations/travel_labels.rpy` — interacțiuni de zonă;
- `game/systems/combat_system.rpy` — combatul;
- `game/systems/inventory_system.rpy` — inventarul;
- `game/systems/health_system.rpy` — consumul de merinde și vindecarea;
- `game/systems/arms_system.rpy` — arme, echipare și seturi de arme;
- `game/quests/riddler_quest.rpy` — side-quest-ul cu ghicitorul;
- `game/ai/ai_client.rpy` — clientul Ren'Py care comunică cu serverul AI;
- `ai/server.py` — serverul AI local;
- `ai/data/riddles.json` — ghicitorile folosite de ghicitor.

---

## Gameplay implementat

### Hartă și explorare

Jocul folosește o hartă pe grilă de **30×40** celule. Fiecare celulă are un tip vizual și o zonă logică. Navigația se poate face:

- cu tastele direcționale;
- cu `W`, `A`, `S`, `D`;
- cu butoanele de pe ecran;
- în 8 direcții, inclusiv diagonal.

Sistemul are și un mic delay pentru input diagonal: jocul citește prima tastă, apoi așteaptă foarte scurt o a doua tastă compatibilă pentru a decide dacă mișcarea este diagonală.

### Zone importante

Zonele principale implementate în date sunt:

- `zsat` — satul de început;
- `zhan` — Hanul Corbului Negru;
- `zpadure` — Pădurea Vlăsiei;
- `ztargoviste` — Târgoviște;
- `zcurte` — Curtea Domnească;
- `zotomani` — tabăra otomană.

Fast travel-ul există ca sistem și folosește variabile separate pentru:

- zonă deblocată;
- punct de fast travel deblocat.

---

## NPC-uri și interacțiuni

NPC-urile importante au sprite-uri afișate direct pe hartă:

- bătrânul satului;
- boierul de la han;
- haiducul din pădure;
- lupul din tutorial;
- ghicitorul din lanurile de grâu.

NPC-urile pot fi ascunse sau afișate în funcție de progresul jucătorului. De exemplu, boierul dispare după ce este învins, iar lupul nu mai apare după tutorial.

---

## Combat

Combatul este funcțional într-o formă simplificată. Jucătorul are trei acțiuni principale:

- `Parare`;
- `Light blow`;
- `Heavy blow`.

Sistemul include:

- HP pentru jucător;
- HP pentru inamici;
- cooldown-uri pentru acțiuni;
- damage aplicat la finalul acțiunii;
- parare care poate anula damage-ul;
- game over simplu la moarte;
- recompense după victorie.

Inamici implementați în demo:

- lup;
- boier;
- haiduc.

---

## Inventar, arme și merinde

Inventarul este funcțional și afișează itemele cu iconițe din `game/images/items/`.

Item important:

```text
merinde
```

Merindele sunt provizii consumabile. Jucătorul începe jocul cu **1 merinde**.

Merindele pot fi consumate:

- cu tasta `H`;
- cu butonul `Merinde xN (H)` din HUD.

Efect:

- vindecă maximum **15 HP**;
- nu trece peste `player_max_health`;
- nu se consumă dacă jucătorul are deja HP maxim;
- afișează mesaj dacă jucătorul nu are merinde.

Sistemul de arme include seturi de arme, echipare și sincronizare cu statistici de combat.

---

## Side-quest: Ghicitorul

Ghicitorul este primul side-quest demonstrativ cu AI.

Fișiere relevante:

```text
game/quests/riddler_quest.rpy
ai/data/riddles.json
game/images/enemies/npc_friendly/ghicitorul.png
```

Mecanica actuală:

- ghicitorul poate apărea pe celule de tip `G`, adică lanuri de grâu;
- prima întâlnire are o șansă mai mare de spawn;
- întâlnirile următoare au o șansă mai mică;
- după interacțiune, ghicitorul dispare;
- după dispariție, intră într-un cooldown real de 5 minute;
- ghicitorul pune o ghicitoare în engleză;
- jucătorul scrie răspunsul;
- AI-ul local sau fallback-ul verifică răspunsul;
- dacă răspunsul este corect, jucătorul primește `+1 merinde`.

Valorile de spawn pot fi ajustate în:

```text
game/quests/riddler_quest.rpy
```

```renpy
RIDDLER_FIRST_SPAWN_CHANCE = 0.10
RIDDLER_REPEAT_SPAWN_CHANCE = 0.03
RIDDLER_COOLDOWN_SECONDS = 5 * 60
```

Pentru testare rapidă, se poate forța apariția ghicitorului din consola Ren'Py:

```renpy
riddler_debug_force_spawn_here()
```

---

## Integrarea AI

Proiectul are un server AI local în:

```text
ai/server.py
```

Ren'Py comunică cu serverul prin:

```text
game/ai/ai_client.rpy
```

Funcții Ren'Py importante:

```renpy
ai_dialogue(...)
ai_get_riddle()
ai_evaluate_riddle(...)
ai_environment_event(...)
ai_ensure_server_running()
```

Serverul AI oferă endpoint-uri precum:

```text
GET  /health
POST /dialogue
GET  /riddle/random
POST /riddle/evaluate
POST /environment/update
GET  /environment/state
```

Jocul încearcă să pornească automat serverul AI dacă nu este deja pornit, folosind Python-ul local din:

```text
runtime/python311/python.exe
```

### Modelul AI local

Modelul `.gguf` nu este inclus în repository, deoarece poate fi foarte mare. Fișierele de model sunt ignorate prin `.gitignore`:

```text
/ai/models/*.gguf
```

Pentru rulare locală, este nevoie de un fișier:

```text
ai/config.json
```

Exemplu de configurare:

```json
{
  "model_backend": "gpt4all",
  "model_path": "ai/models/model.gguf",
  "server_host": "127.0.0.1",
  "server_port": 8765,
  "ai_dialogue_enabled": true,
  "riddle_evaluator_enabled": true,
  "max_tokens": 140,
  "temperature": 0.7
}
```

`model_path` trebuie modificat ca să corespundă exact numelui modelului local.

Dacă modelul nu există sau serverul AI nu poate genera un răspuns, jocul folosește fallback-uri hardcodate, astfel încât demo-ul să rămână jucabil.

---

## Instalare și rulare pentru dezvoltare

### 1. Clonarea proiectului

```bash
git clone <repo-url>
cd MDS
```

### 2. Pregătirea Python-ului local pentru AI

Proiectul folosește un Python portabil în:

```text
runtime/python311/
```

Instalează dependințele AI cu:

```bash
runtime\python311\python.exe ai\install_ai_deps.py
```

Dacă fișierul de instalare nu este prezent local, dependințele din `ai/requirements.txt` pot fi instalate manual cu pip în Python-ul portabil.

### 3. Configurarea modelului local

Copiază modelul `.gguf` în:

```text
ai/models/
```

Apoi creează sau actualizează:

```text
ai/config.json
```

cu path-ul corect către model.

### 4. Pornirea jocului

Jocul se pornește din Ren'Py Launcher sau din executabilul local al proiectului.

Serverul AI poate fi pornit automat de joc. Pentru testare manuală:

```bash
runtime\python311\python.exe ai\server.py
```

Test health:

```text
http://127.0.0.1:8765/health
```

---

## Ce este implementat parțial

- sistemul principal de quest-uri;
- progresia narativă completă;
- reputația pe facțiuni;
- agenții AI pentru combat și reward-uri adaptive;
- conținutul final pentru oraș, curte și tabăra otomană;
- distribuția finală cu launcher și model AI.

---

## Direcție de dezvoltare

Pașii următori probabili:

- rafinarea side-quest-ului cu ghicitorul;
- adăugarea quest-ului cu soldatul de la fântână și cupa de aur;
- conectarea Environment Director Agent la mai multe alegeri;
- extinderea sistemului de combat;
- integrarea reward evaluator-ului;
- pregătirea unui launcher care pornește jocul și AI-ul împreună;
- polish vizual și narativ.

---

## Concluzie

În forma actuală, **Ordinul Dragonului** are o bază tehnică solidă pentru un demo: explorare, NPC-uri, combat, inventar, vindecare, arme și un prim side-quest AI funcțional. Proiectul nu este încă finalizat, dar poate demonstra deja direcția de gameplay și integrarea agenților AI locali.
