# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the game

The Ren'Py 8.5.2 SDK lives at `/home/stefi/MDS/renpy-8.5.2-sdk/`.

```bash
# Launch the game directly
/home/stefi/MDS/renpy-8.5.2-sdk/renpy.sh /home/stefi/MDS/Ordinul_Dragonului/MDS-project

# Open the Ren'Py launcher (GUI) to run, build, or lint
/home/stefi/MDS/renpy-8.5.2-sdk/renpy.sh
```

Ren'Py has no separate build or test step — syntax errors surface when you launch the game. The launcher's "Check Script (Lint)" option (`renpy.sh <project> lint`) validates `.rpy` files.

## Architecture

This is a Ren'Py visual novel RPG called **Order of the Dragon**. All game code lives under `game/` and is split into focused modules that Ren'Py loads automatically at startup.

### Implementation recommendation
Try utilizing class incapsulations when possible and when you think it would make the code more feasible.

### Global state (`game/systems/game_state.rpy`)

The single source of truth for runtime state, initialised via `label init_game_state:`:

| Variable | Type | Purpose |
|---|---|---|
| `player_location` | string | current location key |
| `unlocked_locations` | list | zones the player can visit |
| `active_quests` | list | in-progress quest IDs |
| `completed_quests` | list | finished quest IDs |
| `inventory` | dict | item_id → count |
| `player_level` | int | player level |

All other systems read/write these variables directly — there is no central state manager object.

### Module responsibilities

| Directory / file | Responsibility |
|---|---|
| `systems/` | Core mechanics: map travel, fast travel, quest tracking, combat, inventory, NPC interaction |
| `quests/` | Quest definitions (`quest_data.rpy`), main quest flow (`main_quest.rpy`), side quests |
| `ai/` | Three planned AI subsystems: `environment_director` (dynamic world events), `combat_adaptation` (enemy behaviour), `reward_evaluator` (loot/XP balancing) |
| `locations/` | Static location definitions and travel entry-point labels |
| `characters/` | Character `define` declarations, NPC data, shared dialogue snippets |
| `data/` | Pure data files: items, enemies, rewards, boolean flags |
| `script.rpy` | Entry point (`label start:`); delegates to systems, not inline logic |
| `gui.rpy` / `screens.rpy` | UI layout and custom screens |

### Fonts

Five custom fonts in `game/fonts/`, all medieval/gothic in style: **Cinzel** (headings), **Cormorant Upright** (body text), **UnifrakturMaguntia** (decorative), **Lavishly Yours**, **Mea Culpa**.

### Video assets

`game/video/` contains looping fire/flame `.webm` clips (`descending_flames`, `fire_particles`, `flames`) used for atmospheric UI backgrounds or intro sequences.

## Current state (updated 2026-06-08 — playable demo)

The project is a playable vertical slice that runs and passes lint. Implemented:

- **Core loop:** `script.rpy` (intro → name input → grid) → `systems/map_system.rpy` (12×12 grid,
  D-pad/WASD, minimap) → zone interactions in `locations/travel_labels.rpy`.
- **Chapter I complete** (`q01_investigatie`): Călin → Han (eavesdrop/search choice, secret letter,
  Mircea encounter with optional fight) → return choice that shifts loyalty.
- **3 zones activated** with loyalty-shifting choices: `curtea_domneasca` (Vlad), `padure`
  (Pădurea Țepelor moral beat), `tabara_otomana` (Kemal). Unlocked progressively; one-shot via
  `zone_event_done`.
- **Demo ending selector** (`quests/main_quest.rpy` `label demo_ending`): reads dominant loyalty →
  one of 4 endings. Reachable from the quest journal after Chapter I.
- **Combat** (`systems/combat_system.rpy`): semi-real-time with parry/cooldown; enemy sprite
  fallback so any enemy renders; stats read from `ENEMIES`; death offers load/main-menu (no hard restart).
- **3 deterministic AI agents** (no LLM, demo-safe), each with a visible in-game effect:
  - `ai/combat_adaptation.rpy` — enemy adapts its moves to player performance; HUD shows its reasoning.
  - `ai/reward_evaluator.rpy` — scales XP/loot by difficulty + performance; wired into combat victory
    and `give_quest_reward`.
  - `ai/environment_director.rpy` — state/loyalty-driven world events fired on zone entry.
  Pure decision functions (`combat_decide_enemy_move`, `reward_evaluate_combat`,
  `environment_director_pick_event`) are kept side-effect-free for future eval tests.
- **UI:** loyalty panel + inventory (`I`) + quest journal (`J`) + fast-travel (`T`) on the grid screen
  (`systems/inventory_system.rpy`, `systems/quest_system.rpy`, `systems/fast_travel.rpy`).

Still stubbed / not done: Chapters II–V proper, `quests/quest_data.rpy` & `side_quests.rpy`,
`systems/npc_system.rpy`, audio. The "component B" deliverables (tests/evals, CI, diagrams, user
stories, AI-usage report — half the lab grade per `MDS.txt`) are NOT yet started.

# VERY IMPORTANT
We are three (3) people working on this project!!!

## Story
Vreau ca jocul să fie despre Ordinul Dragonului, dar o istorie rescrisă, legată mai mult de domnia lui Vlad Țepeș, dar personajul principal să nu fie Vlad Țepeș. Trebuie ca personajul principal să poată alege pe parcursul jocului dacă vrea să fie de partea lui Țepeș sau a inamicilor săi (otomani sau trădători). Assassin's Creed vibes. Ne trebuie o poveste intersantă, dar nu foarte lungă, pe care să o putem expanda dacă e nevoie. Și pe care o putem implementa în Ren'Py, urmând această direcție.

Da. Aș merge pe o poveste semi-istorică, cu ramificații morale, nu pe o biografie a lui Vlad Țepeș.

Titlu provizoriu

Ordinul Dragonului: Umbra Țepeșului

Premisă

Personajul principal este un tânăr/o tânără agent al Ordinului Dragonului, trimis în Țara Românească într-o perioadă în care Vlad Țepeș încearcă să-și consolideze domnia.

Ordinul nu este prezentat ca „bun” sau „rău”. Oficial, apără creștinătatea și stabilitatea politică. În realitate, are facțiuni interne: unii îl susțin pe Vlad, alții îl consideră prea brutal și instabil.

Personajul ajunge prins între trei tabere:

Vlad Țepeș — ordine prin frică, independență, cruzime justificată politic.
Boierii trădători — supraviețuire, influență, compromisuri cu otomanii.
Otomanii — putere imperială, diplomație, manipulare, promisiunea unei păci false.
Personaj principal

Nume provizoriu: Mihail / Mara Drăculea sau ceva mai neutru: Alexandru / Ilinca Corvin

Mai bine ar fi un personaj personalizabil:

default player_name = "Mara"
default loyalty_vlad = 0
default loyalty_boyars = 0
default loyalty_ottomans = 0
default dragon_order_trust = 0

Personajul este copilul unui fost membru al Ordinului Dragonului, dispărut după o misiune secretă. Intriga personală: află că tatăl/mama nu a murit eroic, ci a fost implicat/ă într-o trădare care a schimbat cursul domniei lui Vlad.

Structură scurtă, bună pentru Ren’Py
Capitolul 1 — Sosirea la Târgoviște

Personajul este trimis de Ordin să investigheze zvonuri despre o conspirație împotriva lui Vlad.

Misiuni implementabile:

deplasare pe hartă: Târgoviște, Curtea Domnească, Han, Pădure, Tabără otomană;
interacțiuni cu NPC-uri;
primul choice important: raportezi direct lui Vlad sau păstrezi informația pentru Ordin?
Capitolul 2 — Trădarea boierilor

Personajul descoperă că un grup de boieri pregătește o alianță secretă cu otomanii.

Choice major:

îi dai pe mâna lui Vlad;
îi avertizezi și îi folosești ca informatori;
vinzi informația emisarului otoman.

Aici poate intra sistemul de reputație.

Capitolul 3 — Pădurea Țepelor

Vlad își arată cruzimea. Personajul vede consecințele reale ale politicii lui.

Nu trebuie prezentat simplu ca monstru. Ideea bună ar fi: metodele lui funcționează, dar costul moral e uriaș.

Choice major:

îl susții pe Vlad, acceptând frica drept armă politică;
începi să-l sabotezi discret;
rămâi neutru și cauți adevărul despre Ordin.
Capitolul 4 — Ordinul se rupe

Personajul află că Ordinul Dragonului are două facțiuni:

una vrea ca Vlad să rămână pe tron;
alta vrea să-l sacrifice pentru o pace cu otomanii.

Aici apare conflictul Assassin’s Creed-like: nu doar țări, ci organizații secrete care controlează istoria.

Capitolul 5 — Alegerea finală

Finalul se decide pe baza loialităților.

Posibile finaluri:

Final Vlad:
Îl ajuți pe Vlad să distrugă conspirația. Țara rămâne liberă, dar personajul devine complice la teroare.

Final Otoman:
Îl trădezi pe Vlad și deschizi drumul influenței otomane. Primești putere și protecție, dar Ordinul te consideră trădător.

Final Boieri:
Îl slăbești pe Vlad și ajuți boierii să recapete controlul. Pare o soluție mai „umană”, dar țara devine vulnerabilă.

Final Ordin Independent:
Refuzi toate taberele și expui manipularea Ordinului. Vlad poate cădea sau supraviețui, dar personajul devine o amenințare pentru toți.

Hook narativ bun

Secretul central:

Ordinul Dragonului nu încearcă doar să apere Țara Românească. Încearcă să controleze legenda lui Vlad înainte ca ea să se nască.

Asta permite o istorie rescrisă fără să fie nevoie să respectăm perfect istoria reală.

Pentru implementare în Ren’Py

Povestea se potrivește bine cu:

hartă cu zone deblocate treptat;
fast-travel între locații;
quest principal cu pași multipli;
side-quest-uri locale;
NPC-uri cu dialoguri ramificate;
sistem de loialitate;
inventar simplu: sigilii, scrisori, pumnal, documente, relicve;
combat foarte simplificat prin alegeri, nu prin mecanici grele.

Exemplu de variabile:
default loyalty_vlad = 0
default loyalty_ottomans = 0
default loyalty_boyars = 0
default order_suspicion = 0
default has_secret_letter = False
default knows_order_truth = False

Direcția cea mai bună: poveste scurtă, 5 capitole, 3-4 locații principale, 4 finaluri, dar construită modular ca să puteți adăuga side-quest-uri fără să rupeți firul principal.

