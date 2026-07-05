default player_name = "Mara"

# Coordonatele interne ale grilei sunt (row, col).
# Pentru punctul vizual (x=0, y=29), în cod înseamnă row=29, col=0.
default player_location = "zsat"
default player_grid_row = 29
default player_grid_col = 0

default unlocked_zone = {
    "zsat": True,
    "zhan": False,
    "zpadure": False,
    "ztargoviste": False,
    "zcurte": False,
    "zotomani": False,
}

default unlocked_fast = {
    "zsat": True,
    "zhan": False,
    "zpadure": False,
    "ztargoviste": False,
    "zcurte": False,
    "zotomani": False,
}



default active_quests = []
default completed_quests = []
default inventory = {}
default player_level = 1
default current_chapter = 1

default player_max_health = 100
default player_health = 100
default in_combat = False
default combat_parry_active = False
default combat_last_result = None

# zsat
default unlocked_locations = ["zsat"]
default talked_to_old_man = False
default road_to_wolf_unlocked = False
default wolf_tutorial_done = False
default wolf_tutorial_active = False
default unlocked_cells = []

# zhan
default han_entry_reached = False
default met_boier_han = False
default boier_chest_quest_started = False
default boier_chest_returned = False
default boier_fight_done = False
default boier_attacked = False
default boier_defeated = False
default got_city_seal = False
default forest_unlocked_by_boier = False
default city_seal_method = None

# zpadure
default met_haiduc_cufar = False
default haiduc_cufar_accused = False
default haiduc_cufar_fight_done = False
default haiduc_cufar_defeated = False

# default loyalty_vlad = 0
# default loyalty_boyars = 0
# default loyalty_ottomans = 0
# default dragon_order_trust = 0
# default order_suspicion = 0

# default has_secret_letter = False
# default knows_order_truth = False
# default knows_parent_secret = False
# default vlad_knows_player = False
# default boyars_trust_player = False
# default ottoman_contact_made = False

# met_old_man = False
# han_unlocked_by_old_man = False
# met_boier_han = False
# forest_unlocked_by_boier = False
# got_pass_document = False
# targoviste_unlocked = False
# court_access_granted = False
# met_vlad = False
# ottoman_zone_unlocked = False

# boier_document_method = None
# # "helped_boier", "robbed_boier", "deal_with_haiduc"






label init_game_state:
    $ player_location = "zsat"
    $ player_grid_row = 29
    $ player_grid_col = 0

    $ unlocked_zone = {
        "zsat": True,
        "zhan": False,
        "zpadure": False,
        "ztargoviste": False,
        "zcurte": False,
        "zotomani": False,
    }

    $ unlocked_fast = {
        "zsat": True,
        "zhan": False,
        "zpadure": False,
        "ztargoviste": False,
        "zcurte": False,
        "zotomani": False,
    }

    $ unlocked_locations = ["zsat"]
    $ active_quests = []
    $ completed_quests = []
    $ inventory = {}
    $ player_level = 1
    $ current_chapter = 1
    $ player_max_health = 100
    $ player_health = player_max_health
    $ in_combat = False
    $ combat_parry_active = False
    $ combat_last_result = None
    $ loyalty_vlad = 0
    $ loyalty_boyars = 0
    $ loyalty_ottomans = 0
    $ dragon_order_trust = 0
    $ order_suspicion = 0
    $ has_secret_letter = False
    $ knows_order_truth = False
    $ knows_parent_secret = False
    $ vlad_knows_player = False
    $ boyars_trust_player = False
    $ ottoman_contact_made = False

    # zsat
    $ talked_to_old_man = False
    $ road_to_wolf_unlocked = False
    $ wolf_tutorial_done = False
    $ wolf_tutorial_active = False
    $ unlocked_cells = []

    #zhan
    $ han_entry_reached = False
    $ met_boier_han = False
    $ boier_chest_quest_started = False
    $ boier_chest_returned = False
    $ boier_fight_done = False
    $ boier_attacked = False
    $ boier_defeated = False
    $ got_city_seal = False
    $ forest_unlocked_by_boier = False
    $ city_seal_method = None

    # zpadure
    $ met_haiduc_cufar = False
    $ haiduc_cufar_accused = False
    $ haiduc_cufar_fight_done = False
    $ haiduc_cufar_defeated = False

    return
