# init python:
#     # Capitole
#     CHAPTER_1 = 1
#     CHAPTER_2 = 2
#     CHAPTER_3 = 3
#     CHAPTER_4 = 4
#     CHAPTER_5 = 5

#     # Praguri de loialitate pentru ramificații și finaluri
#     LOYALTY_LOW    = -3
#     LOYALTY_MEDIUM =  3
#     LOYALTY_HIGH   =  6

#     # ID-uri locații principale
#     LOC_TARGOVISTE       = "targoviste"
#     LOC_CURTEA_DOMNEASCA = "curtea_domneasca"
#     LOC_HAN              = "han"
#     LOC_PADURE           = "padure"
#     LOC_TABARA_OTOMANA   = "tabara_otomana"

#     # Drumuri / câmpuri — spații de legătură între locații
#     # Folosite ca scene de tranziție unde pot apărea întâlniri sau evenimente
#     LOC_DRUM_TARGOVISTE_CURTEA = "drum_targoviste_curtea"   # centrul orașului → palat
#     LOC_DRUM_TARGOVISTE_HAN    = "drum_targoviste_han"      # oraș → han
#     LOC_CAMP_HAN_PADURE        = "camp_han_padure"          # câmp deschis → pădure
#     LOC_DRUM_PADURE_TABARA     = "drum_padure_tabara"       # pădure → tabără otomană

#     # Rute de deplasare: (origine, destinație) → locație de legătură
#     TRAVEL_ROUTES = {
#         ("targoviste",    "curtea_domneasca"): "drum_targoviste_curtea",
#         ("curtea_domneasca", "targoviste"):    "drum_targoviste_curtea",
#         ("targoviste",    "han"):              "drum_targoviste_han",
#         ("han",           "targoviste"):       "drum_targoviste_han",
#         ("han",           "padure"):           "camp_han_padure",
#         ("padure",        "han"):              "camp_han_padure",
#         ("padure",        "tabara_otomana"):   "drum_padure_tabara",
#         ("tabara_otomana","padure"):           "drum_padure_tabara",
#     }

#     # ID-uri quest principale
#     QUEST_CAP1_INVESTIGATIE  = "q01_investigatie"
#     QUEST_CAP2_TRADAREA      = "q02_tradarea_boierilor"
#     QUEST_CAP3_PADUREA       = "q03_padurea_tepelor"
#     QUEST_CAP4_ORDINUL       = "q04_ordinul_se_rupe"
#     QUEST_CAP5_ALEGEREA      = "q05_alegerea_finala"

#     # ID-uri NPC
#     NPC_VLAD    = "vlad_tepes"
#     NPC_MIRCEA  = "mircea_boier"
#     NPC_RADU    = "radu_boier"
#     NPC_KEMAL   = "kemal_otoman"
#     NPC_CALIN   = "calin_ordin"

#     # Finaluri posibile
#     ENDING_VLAD     = "ending_vlad"
#     ENDING_OTTOMAN  = "ending_ottoman"
#     ENDING_BOYARS   = "ending_boyars"
#     ENDING_ORDER    = "ending_order_independent"
