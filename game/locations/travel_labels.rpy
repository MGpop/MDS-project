# Entry point-uri pentru fiecare locație.
# Apelate de grid_map când jucătorul intră într-o nouă zonă.
# Returnează după narațiune — grid_map continuă.

label enter_targoviste:
    $ player_location = "targoviste"
    scene expression location_background_displayable("targoviste") with dissolve
    "Târgoviște. Zgomotul orașului te înconjoară — roți pe pietre, strigăte de negustori, și priviri care nu te privesc direct."
    return

label enter_curtea_domneasca:
    $ player_location = "curtea_domneasca"
    scene expression location_background_displayable("curtea_domneasca") with dissolve
    "Porțile Curții Domnești se deschid în fața ta. Soldații te urmăresc cu privirea. Fiecare pas e numărat."
    return

# luptă demo
label enter_han:
    scene bg han with dissolve

    $ han_has_ottoman = renpy.random.randint(1, 100) <= 50

    if han_has_ottoman:

        $ otoman_starts_fight = renpy.random.randint(1, 100) <= 50

        if otoman_starts_fight:
            show otoman_spotted at enemy_alert_pos with dissolve
            "Soldatul otoman te vede și pune mâna pe armă."

            hide otoman_spotted with dissolve
            call start_combat("soldat_otoman", "grid_map")
            return

        else:
            show otoman_default at enemy_idle_pos with dissolve
            "Un soldat otoman stă în han, dar nu pare interesat de tine."

            menu:
                "Ce faci?"
                "Îl ignor":
                    "Îți vezi de treabă."
                    return

                "Îl confrunt":
                    hide otoman_default with dissolve
                    call start_combat("soldat_otoman", "grid_map")
                    return

    "Hanul e liniștit."
    return

label zone_actions_targoviste:
    scene expression location_background_displayable("targoviste") with dissolve

    if "q01_investigatie" not in active_quests and "q01_investigatie" not in completed_quests:
        calin "Bine că ai ajuns, [player_name]. Ordinul te-a trimis la momentul potrivit."
        calin "Se vorbește că boierii din han uneltesc ceva — o alianță secretă cu otomanii. Poate mai mult."
        calin "Du-te la Hanul Corbului Negru. Ascultă. Caută. Dacă găsești dovezi, adu-mi-le."
        $ start_quest("q01_investigatie")
        $ add_item("pumnal")
        "Călin îți întinde un pumnal cu lama înnegrită."
        narrator "Ai primit: {b}Pumnal{/b}. Misiune activă: {i}Investighează Hanul{/i}."

    elif "q01_investigatie" in active_quests and has_item("scrisoare_secreta"):
        calin "Ai revenit. Și cu dovezi, se pare."
        calin "Această scrisoare poate schimba multe. Ce vrei să faci cu ea?"

        menu:
            "Îi dai scrisoarea lui Călin":
                $ remove_item("scrisoare_secreta")
                $ has_secret_letter = False
                $ dragon_order_trust += 1
                calin "Bine. Ordinul va ști ce să facă cu asta. Ai acționat corect."
                narrator "Scrisoarea a ajuns în mâinile Ordinului. Ordinul are încredere în tine."

            "O păstrezi pentru Vlad":
                $ loyalty_vlad += 1
                calin "Înțeleg. Ai grijă cu ea — și cu tine."
                narrator "Ai păstrat scrisoarea. Poate fi mai utilă direct la Curtea Domnească."

        $ complete_quest("q01_investigatie")
        "[last_reward_message]"
        $ current_chapter = 2
        $ unlock_location("curtea_domneasca")
        $ unlock_location("padure")
        narrator "— Capitolul I: Investigația — {b}Completat{/b} —"
        narrator "Noi drumuri s-au deschis: {b}Curtea Domnească{/b} și {b}Pădurea Vlăsiei{/b}. Explorează-le (Fast-travel: tasta T)."
        narrator "Când ești gata, deschide {b}Jurnalul (J){/b} și alege «Vezi finalul (demo)»."

    elif "q01_investigatie" in active_quests:
        calin "Încă nu ai fost la Han? Nu avem timp de pierdut, [player_name]."

    else:
        calin "Ai dovedit că ești un agent de nădejde al Ordinului."

    return


label zone_actions_han:
    scene bg han with dissolve

    if "q01_investigatie" in active_quests and not has_item("scrisoare_secreta"):
        "Hanul Corbului Negru. Fum, vin acru și prea multe priviri care te ocolesc."

        menu:
            "Cum procedezi?"
            "Asculți discret conversațiile de la mese":
                "Te așezi într-un colț și lași urechea să lucreze."
                "Doi negustori șoptesc despre «o întâlnire la miezul nopții» și despre «omul sultanului»."
                $ dragon_order_trust += 1
                narrator "Indiciu prins. Ordinul va aprecia atenția ta la detalii."
            "Cauți direct, fără să pierzi timpul":
                "Treci hotărât printre mese, cu ochii pe orice nu se potrivește."

        "Sub o masă, ascuns în grabă, găsești un teanc de hârtii legate cu o panglică roșie."
        "Le desfaci rapid. O scrisoare codificată — cu sigiliul unui boier."
        $ add_item("scrisoare_secreta")
        $ has_secret_letter = True
        narrator "Ai găsit: {b}Scrisoare secretă{/b}."

        mircea "Hei! Pune jos ce-ai găsit acolo."

        menu:
            "Mircea Bălan?"
            "Un călător obosit — nu am văzut nimic.":
                mircea "Hmm. Pleacă de-aici. Locul ăsta nu e pentru curioși."
                "[player_name] decide să nu insiste și să ducă scrisoarea lui Călin."

            "Te cunosc, Mircea. Știu ce plănuiești.":
                $ loyalty_boyars += 1
                mircea "Atunci știi că e mai înțelept să taci. Suntem pe aceeași parte, dacă ești deștept."
                narrator "Mircea Bălan pare să te considere un potențial aliat."

            "Pui mâna pe pumnal. Scrisoarea pleacă cu mine.":
                mircea "Greșeală. Gardă!"
                "Un om al lui Mircea se ridică de la masă și trage sabia."
                $ loyalty_boyars -= 1
                narrator "Boierii nu vor uita asta. Va trebui să-ți croiești drum cu forța."
                call start_combat("boier_garda", "grid_map")

    elif has_item("scrisoare_secreta"):
        "Ai scrisoarea. E timpul să te întorci la Călin în Târgoviște."

    else:
        "Hanul e liniștit. Nimic de remarcat."

    return


label zone_actions_curtea_domneasca:
    scene expression location_background_displayable("curtea_domneasca") with dissolve
    if "curtea_intro" not in zone_event_done:
        $ zone_event_done.append("curtea_intro")
        narrator "Porțile se deschid. Pentru prima dată calci în inima puterii lui Vlad."
        vlad "Deci tu ești agentul Ordinului. Am auzit că adulmeci prin hanurile mele."
        menu:
            "Cum răspunzi?"
            "Sunt în slujba Ordinului — și a stabilității, Măria Ta.":
                $ loyalty_vlad += 1
                vlad "Stabilitate. Cuvânt frumos pentru frică. Dar îmi placi. Deocamdată."
                narrator "Loialitatea față de Vlad a crescut."
            "Nu slujesc decât adevărul.":
                $ order_suspicion += 1
                vlad "Adevărul. Periculos lucru, în mâinile cui nu trebuie."
                narrator "Vlad te privește cu răceală. Suspiciunea plutește în aer."
    else:
        "Curtea Domnească. Soldații te urmăresc, dar te lasă să treci. Ești cunoscut acum."
    return


label enter_padure:
    $ player_location = "padure"
    scene expression location_background_displayable("padure") with dissolve
    $ unlock_location("tabara_otomana")
    "Pădurea Vlăsiei te înghite. Lumina dispare imediat ce intri sub coroanele copacilor. Ceva scârțâie în ramuri."
    return

label enter_tabara_otomana:
    $ player_location = "tabara_otomana"
    scene expression location_background_displayable("tabara_otomana") with dissolve
    "Dai semnalul convenit. Un soldat otoman apare din umbră și te conduce înăuntru, fără un cuvânt."
    return


label zone_actions_padure:
    scene expression location_background_displayable("padure") with dissolve
    if "padure_tepe" not in zone_event_done:
        $ zone_event_done.append("padure_tepe")
        narrator "Pădurea se deschide într-un luminiș. Și atunci le vezi."
        "Rânduri de țepe. Trupuri. Trădători, tâlhari, otomani — fără deosebire. Tăcere absolută."
        "Metoda funcționează: drumurile sunt sigure de când Vlad a ridicat pădurea asta. Dar costul..."
        menu:
            "Ce simți?"
            "Frica e o armă. Vlad are dreptate.":
                $ loyalty_vlad += 1
                narrator "Accepți prețul. Loialitatea față de Vlad crește."
            "Asta nu e ordine. E groază. Trebuie oprit.":
                $ loyalty_boyars += 1
                narrator "Ceva în tine se întoarce împotriva lui Vlad."
            "Privești în tăcere și cauți adevărul din spate.":
                $ dragon_order_trust += 1
                narrator "Rămâi rece. Ordinul are nevoie de minți limpezi."
    else:
        "Pădurea Țepelor. Treci repede. Nimeni nu zăbovește aici."
    return


label zone_actions_tabara_otomana:
    scene expression location_background_displayable("tabara_otomana") with dissolve
    if "tabara_kemal" not in zone_event_done:
        $ zone_event_done.append("tabara_kemal")
        $ ottoman_contact_made = True
        kemal "Bine ai venit, agent al Dragonului. Sultanul prețuiește oamenii practici."
        kemal "Vlad arde și trage în țepe. Noi oferim... pace. Și aur. Ai vrea să asculți?"
        menu:
            "Ce faci?"
            "Ascult. O înțelegere nu strică nimănui.":
                $ loyalty_ottomans += 1
                kemal "Înțelept. Vom vorbi din nou, prietene."
                narrator "Loialitatea față de otomani a crescut."
            "Nu mă vând, pașă.":
                $ loyalty_vlad += 1
                kemal "Păcat. Sper să nu regreți, agentule."
                narrator "Ai refuzat târgul. Vlad ar fi mândru."
    else:
        "Tabăra otomană. Kemal Pașa nu e de găsit acum."
    return
