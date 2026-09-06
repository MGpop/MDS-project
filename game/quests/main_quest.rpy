# quests/main_quest.rpy
# Firul principal. Capitolul I trăiește în travel_labels (zone_actions_*).
# Aici punem plata demo-ului: un selector de final care citește loialitatea
# dominantă și arată unul din cele 4 finaluri planificate.

label demo_ending:
    scene black with fade

    python:
        _scores = {
            "vlad": loyalty_vlad,
            "boyars": loyalty_boyars,
            "ottomans": loyalty_ottomans,
            "order": dragon_order_trust,
        }
        _ending = max(_scores, key=lambda k: _scores[k])
        # Dacă nu te-ai aliniat cu nimeni (sau Ordinul te suspectează puternic),
        # ajungi pe ruta „Ordin Independent".
        if all(v == 0 for v in _scores.values()) or order_suspicion >= 3:
            _ending = "order"

    narrator "— Capitolul final (demo) —"
    narrator "Loialități — Vlad: [loyalty_vlad] • Boieri: [loyalty_boyars] • Otomani: [loyalty_ottomans] • Ordin: [dragon_order_trust] (suspiciune: [order_suspicion])."

    if _ending == "vlad":
        narrator "{b}Final: Sabia Dragonului{/b}"
        "L-ai sprijinit pe Vlad și ai zdrobit conspirația. Țara rămâne liberă — dar ai devenit complice la teroare."
    elif _ending == "boyars":
        narrator "{b}Final: Mâna Boierilor{/b}"
        "L-ai slăbit pe Vlad și ai ajutat boierii să recapete controlul. Pare mai uman — dar țara devine vulnerabilă."
    elif _ending == "ottomans":
        narrator "{b}Final: Umbra Semilunii{/b}"
        "L-ai trădat pe Vlad și ai deschis drumul influenței otomane. Primești putere și protecție — dar Ordinul te vânează ca trădător."
    else:
        narrator "{b}Final: Dragonul Liber{/b}"
        "Ai refuzat toate taberele și ai expus manipularea Ordinului. Vlad poate cădea sau supraviețui — dar tu ai devenit o amenințare pentru toți."

    narrator "Sfârșit demo. Mulțumim că ai jucat {i}Ordinul Dragonului: Umbra Țepeșului{/i}."

    menu:
        "Ce vrei să faci?"
        "Înapoi la meniul principal":
            $ renpy.full_restart()
        "Continuă explorarea (demo)":
            jump grid_map
