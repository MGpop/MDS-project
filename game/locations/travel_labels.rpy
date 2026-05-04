label curtea_domneasca:

    scene bg room

    vlad "Ordinul Dragonului trimite copii să-mi judece domnia acum?"

    p "Trimite ochi. Și urechi."

    vlad "Atunci vezi bine. Țara asta nu se ține cu milă."

    menu:
        "Îi spui că îl vei ajuta":
            $ loyalty_vlad += 1
            vlad "Bine. Atunci începe cu hanul. Acolo se vând secretele."

        "Îi spui că Ordinul nu are încredere în el":
            $ loyalty_boyars += 1
            vlad "Atunci Ordinul ar trebui să se teamă să nu ajungă pe lista mea."

    $ quest_stage = 0
    jump map_demo


label han:

    scene bg room

    hangi "Nu pari de pe aici."

    p "Caut oameni care vorbesc prea mult."

    hangi "Atunci ai venit unde trebuie."

    boier "Hangiule, lasă-ne."

    n "Boierul îți strecoară o scrisoare sigilată."

    boier "Du-o cui trebuie. Sau arde-o. Dar nu i-o da lui Vlad."

    $ has_secret_letter = True
    $ quest_stage = 1

    menu:
        "Duci scrisoarea lui Vlad":
            $ loyalty_vlad += 1
            jump curtea_cu_scrisoare

        "Protejezi boierul":
            $ loyalty_boyars += 1
            jump padure

        "Cauți emisarul otoman":
            $ loyalty_ottomans += 1
            jump padure


label curtea_cu_scrisoare:

    scene bg room

    p "Am găsit dovada unei trădări."

    vlad "Nu. Ai găsit dovada că încă sunt prea blând."

    $ has_secret_letter = False

    jump combat_demo


label padure:

    scene bg room

    n "Părăsești hanul prin spate. Pădurea e rece, umedă, tăcută."

    if has_secret_letter:
        n "Scrisoarea pare tot mai grea în mâna ta."

    jump combat_demo