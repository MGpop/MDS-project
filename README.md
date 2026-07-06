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

---

## Universul jocului

Acțiunea pornește în contextul întoarcerii lui Vlad Țepeș la tron. Ordinul Dragonului își trimite agentul în teren cu o misiune aparent clară, însă intriga este construită în jurul ideii că informațiile primite inițial sunt incomplete sau manipulate.

Direcția dorită pentru joc este una de:
- mister politic;
- tensiune între facțiuni;
- conspirații;
- dezvăluiri treptate;
- explorare semi-liberă a lumii.

---

## Stack și organizare

Proiectul folosește:
- `Ren'Py 8.5.2`
- scripturi `.rpy` pentru logică, UI și narațiune;
- asset-uri UI în `game/gui/`;
- background-uri și sprite-uri în `game/images/`.

Structura logică principală:

- `game/script.rpy` — flow-ul de start și intro-ul;
- `game/systems/` — sisteme de gameplay;
- `game/locations/` — hartă, locații și intrări în zone;
- `game/characters/` — personaje și definiții vizuale;
- `game/data/` — iteme, rewards, flags, inamici;
- `game/quests/` — progres narativ și quest-uri;
- `game/ai/` — module planificate pentru sisteme adaptive.

---

# Status curent

## Rezumat

În forma actuală, proiectul este un **prototype / pre-alpha** cu:
- explorare funcțională;
- bază de UI;
- sistem minim de combat;
- fundaluri și prezentare vizuală coerentă;
- primele interacțiuni dinamice cu inamici.

Fundația tehnică a jocului există deja, iar accentul actual al dezvoltării este pe:
- integrarea sistemelor;
- conținut narativ;
- extinderea combatului;
- iterarea pe flow-ul general al gameplay-ului.

---

# Ce funcționează acum

## Intro și flow de bază

- Intro-ul jocului este funcțional și folosește asset-uri dedicate.
- Jucătorul își poate introduce numele.
- Flow-ul dintre intro și gameplay este stabil.
- Jocul pornește direct către sistemul de explorare.

---

## Explorare și hartă

- Există un sistem de explorare pe o **grilă 12×12**.
- Locațiile principale sunt definite în date.
- Există conectori și drumuri între regiuni.
- Background-urile sunt legate la locații reale.
- Harta afișează fundaluri atât pentru locații, cât și pentru drumurile importante.

Locații implementate parțial:
- Han;
- Curtea Domnească;
- Pădure;
- Tabăra otomană.

---

## Combat (versiune minimă)

Proiectul include acum o primă versiune funcțională a sistemului de combat.

Implementarea actuală este intenționat minimalistă și servește drept bază pentru dezvoltări ulterioare.

### Sistemul actual

Combatul funcționează pe baza unor cooldown-uri independente:
- jucătorul și inamicul acționează separat;
- fiecare acțiune are delay propriu;
- damage-ul este aplicat la finalul acțiunii;
- pararea anulează damage-ul pe durata efectului.

### Acțiunile jucătorului

Momentan există trei acțiuni:
- `Parare`
- `Light blow`
- `Heavy blow`

### Pattern-ul inamicilor

Inamicii folosesc momentan un pattern simplu:
- `light → parry → heavy`

Acesta este temporar și va fi înlocuit ulterior cu:
- AI contextual;
- variații de stil de luptă;
- arme diferite;
- statistici;
- comportamente adaptive.

---

## Sănătate și moarte

Sistemul include:
- HP pentru jucător;
- HP pentru inamici;
- blocarea salvării în timpul luptei;
- game over simplu.

Înainte de luptă:
- jocul recomandă salvarea.

La moarte:
- apare un mesaj de deces;
- jucătorul este informat că trebuie să revină la o salvare anterioară;
- următorul ecran trimite către meniul principal.

---

## Întâlniri dinamice cu inamici

Există acum primele evenimente dinamice legate de inamici.

Exemplu:
- în Han există o șansă de 50% ca un soldat otoman să fie prezent;
- dacă este prezent, există o șansă separată de 50% să înceapă el lupta;
- dacă nu este agresiv, jucătorul îl poate ignora sau confrunta.

Sistemul este construit pentru extindere către:
- patrule;
- ambuscade;
- reputație între facțiuni;
- reacții bazate pe progresul narativ.

---

## Prezentare vizuală

Combatul afișează:
- background-ul locației;
- sprite-ul inamicului;
- imaginile asociate acțiunilor playerului;
- UI pentru HP și status.

### Sprite-uri pentru inamici

Structura actuală folosește stări separate:
- `default`
- `spotted`
- `fight`
- `parry`
- `light`
- `heavy`

Această organizare permite extinderea ulterioară fără refactorizare majoră.

---

# Ce este implementat doar parțial

- **Fast travel** există ca logică, dar depinde încă de progresul narativ.
- **Combatul** există într-o formă minimală și necesită extindere.
- Interacțiunile cu NPC-uri sunt încă limitate.
- Zonele există vizual, dar nu sunt populate consistent cu conținut.
- Quest-urile principale și secundare sunt încă în fază de structură.

---

# Ce nu este încă implementat

Următoarele sisteme există doar ca structură sau placeholder:

- `game/quests/main_quest.rpy`
- `game/quests/side_quests.rpy`
- `game/quests/quest_data.rpy`
- `game/systems/inventory_system.rpy`
- `game/systems/npc_system.rpy`
- `game/systems/quest_system.rpy`
- `game/ai/environment_director.rpy`
- `game/ai/combat_adaptation.rpy`
- `game/ai/reward_evaluator.rpy`

---

# Asset-uri și direcție vizuală

Proiectul folosește:
- UI custom în `game/gui/`;
- background-uri dedicate;
- sprite-uri pentru inamici;
- icon-uri pentru combat.

Prezentarea vizuală a depășit etapa de placeholder și începe să funcționeze ca un demo jucabil coerent.

---

# Direcție de dezvoltare

Pașii următori vizați:
- extinderea sistemului de combat;
- integrarea quest-urilor reale;
- dezvoltarea NPC-urilor;
- reputație și facțiuni;
- evenimente dinamice;
- progresie narativă ramificată;
- inventar și rewards reale;
- polish vizual și audio.

---

# Concluzie

În forma actuală, proiectul nu este încă „feature complete”, însă are:
- o bază tehnică stabilă;
- identitate vizuală clară;
- flow minim jucabil;
- fundație bună pentru extindere rapidă.

Accentul dezvoltării a trecut de la construirea structurii către:
- integrarea sistemelor;
- conținut;
- gameplay;
- iterație narativă.