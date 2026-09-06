default player_name = "Mara"
default player_location = "targoviste"
default player_grid_row = 2
default player_grid_col = 1
default unlocked_locations = ["targoviste", "han"]
default active_quests = []
default completed_quests = []
default inventory = {}
default player_level = 1
default player_xp = 0
default current_chapter = 1

default player_max_health = 100
default player_health = 100
default in_combat = False
default combat_parry_active = False
default combat_last_result = None

default loyalty_vlad = 0
default loyalty_boyars = 0
default loyalty_ottomans = 0
default dragon_order_trust = 0
default order_suspicion = 0

default has_secret_letter = False
default knows_order_truth = False
default knows_parent_secret = False
default vlad_knows_player = False
default boyars_trust_player = False
default ottoman_contact_made = False

# Evenimente de zonă deja consumate (ca să nu se repete la fiecare vizită).
default zone_event_done = []

# Ultima zonă în care a intrat jucătorul. Ține enter_<zonă> să nu se re-declanșeze
# când ieși un pas pe drum și te întorci.
default last_entered_zone = "targoviste"

label init_game_state:
    $ player_location = "targoviste"
    $ player_grid_row = 2
    $ player_grid_col = 1
    $ unlocked_locations = ["targoviste", "han"]
    $ active_quests = []
    $ completed_quests = []
    $ inventory = {}
    $ player_level = 1
    $ player_xp = 0
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
    $ zone_event_done = []
    $ last_entered_zone = "targoviste"
    return
