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

---

---

## Status curent

### Rezumat

În stadiul actual, proiectul este cel mai bine descris ca un **prototype / pre-alpha** cu un **vertical slice de explorare și atmosferă**. Fundația tehnică este deja construită, iar partea vizuală de bază pentru intro și deplasarea pe hartă este funcțională. În schimb, multe dintre sistemele mari planificate există încă doar ca structură sau placeholder.

### Ce funcționează acum

- Intro-ul jocului există și folosește asset-uri dedicate de opening.
- Jucătorul își poate introduce numele.
- Jocul pornește într-un flow clar către hartă.
- Există un sistem de explorare pe o **grilă 12×12**.
- Locațiile principale și conectorii dintre ele sunt definiți în date.
- Background-urile au fost legate la fișiere reale din `game/images/backgrounds/`.
- Harta afișează acum fundaluri atât pentru locații principale, cât și pentru drumurile/conectorii definiți explicit în grid.
- Există bazele pentru:
  - NPC-uri;
  - iteme;
  - inamici;
  - rewards;
  - flags și identificatori pentru quest-uri/facțiuni.

### Ce este implementat doar parțial

- **Fast travel** există ca logică, dar depinde de deblocarea locațiilor pe măsură ce jocul avansează.
- **Curtea Domnească**, **Pădurea** și **Tabăra otomană** sunt definite și au background-uri, dar progresia completă spre ele nu este încă susținută de quest-uri și evenimente reale.
- Interacțiunile din zone sunt pregătite structural, dar nu sunt încă populate consistent cu conținut.

### Ce nu este încă implementat

Următoarele module există în repo, dar sunt încă goale sau aproape nefolosite:
- `game/quests/main_quest.rpy`
- `game/quests/side_quests.rpy`
- `game/quests/quest_data.rpy`
- `game/systems/combat_system.rpy`
- `game/systems/inventory_system.rpy`
- `game/systems/npc_system.rpy`
- `game/systems/quest_system.rpy`
- `game/ai/environment_director.rpy`
- `game/ai/combat_adaptation.rpy`
- `game/ai/reward_evaluator.rpy`

Cu alte cuvinte, proiectul are deja:
- **scheletul lumii**;
- **identitatea vizuală de bază**;
- **flow-ul minim jucabil**;

dar nu are încă:
- bucla completă de quest-uri;
- interacțiuni narative dezvoltate în fiecare zonă;
- sistem de combat folosit în joc;
- progresie completă între capitole;
- finaluri și ramificații implementate efectiv.

### Asset-uri și prezentare

Partea de UI este deja bine susținută de asset-uri în `game/gui/`. În plus, proiectul folosește acum background-uri reale pentru:
- intro;
- locațiile principale;
- conectorii relevanți de pe hartă.

Asta înseamnă că prezentarea vizuală a trecut de etapa de placeholder pur și începe să semene cu un demo jucabil.

### Concluzie

În forma actuală, proiectul nu este încă „feature complete”, dar este într-un punct bun pentru:
- continuarea dezvoltării pe quest-uri și conținut;
- iterarea pe flow-ul narativ;
- transformarea rapidă a prototype-ului într-un demo mai coerent.

Cel mai mare câștig actual este că baza tehnică și direcția artistică sunt deja suficient de clare încât următorii pași să fie despre **conținut și integrare**, nu despre reconstrucția structurii.
