# systems/combat_system.rpy
# Combat semi-real-time simulat printr-un loop cu cooldown-uri independente.
# Playerul si inamicul au propriile actiuni, propriile delay-uri si propriile ferestre de parare.

default combat_return_label = "grid_map"

# Date combat curent.
default combat_enemy_id = None
default combat_enemy_name = "Inamic"
default combat_enemy_max_health = 40
default combat_enemy_health = 40
default combat_enemy_base_damage = 8

# Ceas intern pentru lupta. Nu este timp real continuu, ci timp simulat.
default combat_time = 0.0

# Starea playerului.
default combat_player_busy_until = 0.0
default combat_player_action = None
default combat_player_action_damage = 0
default combat_player_parry_until = 0.0

# Starea inamicului.
default combat_enemy_busy_until = 0.0
default combat_enemy_action = None
default combat_enemy_action_damage = 0
default combat_enemy_parry_until = 0.0
default combat_enemy_pattern_index = 0

# Mesaj scurt afisat in HUD.
default combat_status_message = ""

# Vizual
default combat_enemy_visual = None
default combat_player_visual = None

init python:
    import random

    # Mutarile sunt definite la comun. Inamicul foloseste aceleasi tipuri de miscari,
    # dar damage-ul lui este calculat din dificultatea inamicului.
    COMBAT_MOVES = {
        "light": {
            "label": "Light blow",
            "delay": 1.0,
            "player_damage": (7, 11),
            "enemy_damage_multiplier": 0.75,
        },
        "heavy": {
            "label": "Heavy blow",
            "delay": 2.8,
            "player_damage": (18, 26),
            "enemy_damage_multiplier": 1.45,
        },
        "parry": {
            "label": "Parare",
            "delay": 2.0,
            "player_damage": (0, 0),
            "enemy_damage_multiplier": 0.0,
        },
    }

    # Pattern-ul default cerut: light blow -> parare -> heavy blow -> repeat.
    DEFAULT_ENEMY_PATTERN = ["light", "parry", "heavy"]

    def combat_get_enemy_sprite(enemy_id, state):
        data = ENEMIES.get(enemy_id, {})
        key = state + "_sprite"
        return data.get(key, None)

    def get_enemy_combat_stats(enemy_id):
        data = ENEMIES.get(enemy_id, {})
        difficulty = data.get("difficulty", 1)

        return {
            "name": data.get("name", "Inamic"),
            "max_health": 30 + difficulty * 20,
            "base_damage": 5 + difficulty * 4,
        }

    def clamp_player_health():
        global player_health
        player_health = max(0, min(player_health, player_max_health))

    def player_take_damage(amount):
        global player_health
        player_health -= amount
        clamp_player_health()

    def heal_player(amount):
        global player_health
        player_health += amount
        clamp_player_health()

    def combat_is_player_parrying():
        return combat_time < combat_player_parry_until

    def combat_is_enemy_parrying():
        return combat_time < combat_enemy_parry_until

    def combat_roll_player_damage(move_id):
        low, high = COMBAT_MOVES[move_id]["player_damage"]
        return random.randint(low, high) + player_level

    def combat_roll_enemy_damage(move_id):
        mult = COMBAT_MOVES[move_id]["enemy_damage_multiplier"]
        raw = int(round(combat_enemy_base_damage * mult))
        return max(1, random.randint(max(1, raw - 2), raw + 2))

    def combat_next_enemy_move():
        global combat_enemy_pattern_index
        move_id = DEFAULT_ENEMY_PATTERN[combat_enemy_pattern_index % len(DEFAULT_ENEMY_PATTERN)]
        combat_enemy_pattern_index += 1
        return move_id

label start_combat(enemy_id="haiduc", return_label="grid_map"):
    $ combat_return_label = return_label
    $ enemy_stats = get_enemy_combat_stats(enemy_id)
    $ combat_enemy_id = enemy_id
    $ combat_enemy_name = enemy_stats["name"]
    $ combat_enemy_max_health = enemy_stats["max_health"]
    $ combat_enemy_health = combat_enemy_max_health
    $ combat_enemy_base_damage = enemy_stats["base_damage"]

    $ combat_time = 0.0
    $ combat_player_busy_until = 0.0
    $ combat_player_action = None
    $ combat_player_action_damage = 0
    $ combat_player_parry_until = 0.0
    $ combat_enemy_busy_until = 0.0
    $ combat_enemy_action = None
    $ combat_enemy_action_damage = 0
    $ combat_enemy_parry_until = 0.0
    $ combat_enemy_pattern_index = 0
    $ combat_status_message = ""

    $ combat_enemy_visual = combat_get_enemy_sprite(enemy_id, "fight")
    $ combat_player_visual = None

    "Simți că urmează o luptă. Jocul îți recomandă să salvezi acum."

    menu:
        "Ce faci?"
        "Salvez înainte de luptă":
            call screen save
            jump start_combat_after_save_check
        "Încep lupta":
            jump start_combat_after_save_check
        "Mă retrag":
            jump expression combat_return_label

label start_combat_after_save_check:
    $ in_combat = True
    $ renpy.block_rollback()
    "Începi lupta. Din momentul acesta nu mai poți salva până la finalul confruntării."
    jump combat_loop

label combat_loop:
    if player_health <= 0:
        jump player_death

    if combat_enemy_health <= 0:
        jump combat_victory

    # Daca inamicul nu face nimic, isi incepe automat urmatoarea actiune din pattern.
    if combat_enemy_action is None and combat_time >= combat_enemy_busy_until:
        $ enemy_move = combat_next_enemy_move()
        $ combat_enemy_action = enemy_move
        $ combat_enemy_visual = combat_get_enemy_sprite(combat_enemy_id, enemy_move)
        $ combat_enemy_busy_until = combat_time + COMBAT_MOVES[enemy_move]["delay"]
        if enemy_move == "parry":
            $ combat_enemy_parry_until = combat_enemy_busy_until
            $ combat_status_message = combat_enemy_name + " ridică garda."
        elif enemy_move == "light":
            $ combat_enemy_action_damage = combat_roll_enemy_damage("light")
            $ combat_status_message = combat_enemy_name + " pregătește o lovitură rapidă."
        else:
            $ combat_enemy_action_damage = combat_roll_enemy_damage("heavy")
            $ combat_status_message = combat_enemy_name + " pregătește o lovitură grea."

    # Ecranul de combat ramane mereu pe ecran. Butoanele exista permanent,
    # dar sunt sensibile doar cand playerul nu are o actiune in cooldown.
    $ frame_end_time = combat_time + 0.05
    $ screen_result = renpy.call_screen("combat_live_tick", 0.05, combat_time, frame_end_time)

    if screen_result == "parry" and combat_player_action is None and combat_time >= combat_player_busy_until:
        jump combat_start_player_parry
    elif screen_result == "light" and combat_player_action is None and combat_time >= combat_player_busy_until:
        jump combat_start_player_light
    elif screen_result == "heavy" and combat_player_action is None and combat_time >= combat_player_busy_until:
        jump combat_start_player_heavy

    # Daca nu s-a ales nimic, timpul continua sa curga.
    $ combat_time = frame_end_time

    # Evenimentele pot expira in acelasi frame. Enemy-ul ramane rezolvat primul,
    # ca in versiunea veche, pentru consistenta.
    if combat_enemy_action is not None and combat_enemy_busy_until <= combat_time + 0.001:
        jump combat_resolve_enemy_action

    if combat_player_action is not None and combat_player_busy_until <= combat_time + 0.001:
        jump combat_resolve_player_action

    jump combat_loop

label combat_start_player_parry:
    $ combat_player_action = "parry"
    $ combat_player_visual = "player_parry"
    $ combat_player_busy_until = combat_time + COMBAT_MOVES["parry"]["delay"]
    $ combat_player_parry_until = combat_player_busy_until
    $ combat_status_message = "Ridici garda. Timp de 2 secunde nu primești damage."
    jump combat_loop

label combat_start_player_light:
    $ combat_player_action = "light"
    $ combat_player_visual = "player_light"
    $ combat_player_busy_until = combat_time + COMBAT_MOVES["light"]["delay"]
    $ combat_player_action_damage = combat_roll_player_damage("light")
    $ combat_status_message = "Pregătești un light blow."
    jump combat_loop

label combat_start_player_heavy:
    $ combat_player_action = "heavy"
    $ combat_player_visual = "player_heavy"
    $ combat_player_busy_until = combat_time + COMBAT_MOVES["heavy"]["delay"]
    $ combat_player_action_damage = combat_roll_player_damage("heavy")
    $ combat_status_message = "Pregătești un heavy blow. Ești expus mai mult timp."
    jump combat_loop

label combat_advance_to_next_event:
    # Pastrat doar ca fallback pentru compatibilitate. Flow-ul principal foloseste
    # acum combat_live_tick, deci timpul nu se mai opreste pentru decizia playerului.
    jump combat_loop

label combat_resolve_enemy_action:
    if combat_enemy_action == "parry":
        $ combat_status_message = combat_enemy_name + " coboară garda."
    elif combat_enemy_action == "light":
        if combat_time < combat_player_parry_until:
            $ combat_status_message = combat_enemy_name + " lovește rapid, dar pararea ta oprește damage-ul."
        else:
            $ player_take_damage(combat_enemy_action_damage)
            $ combat_status_message = combat_enemy_name + " te lovește rapid pentru " + str(combat_enemy_action_damage) + " damage."
    elif combat_enemy_action == "heavy":
        if combat_time < combat_player_parry_until:
            $ combat_status_message = combat_enemy_name + " lovește greu, dar pararea ta ține."
        else:
            $ player_take_damage(combat_enemy_action_damage)
            $ combat_status_message = combat_enemy_name + " te lovește puternic pentru " + str(combat_enemy_action_damage) + " damage."

    $ combat_enemy_action = None
    $ combat_enemy_action_damage = 0
    $ combat_enemy_visual = combat_get_enemy_sprite(combat_enemy_id, "fight")

    if player_health <= 0:
        jump player_death

    # Daca si playerul termina in acelasi moment, rezolva-l imediat dupa inamic.
    if combat_player_action is not None and combat_player_busy_until <= combat_time + 0.001:
        jump combat_resolve_player_action

    jump combat_loop

label combat_resolve_player_action:
    if combat_player_action == "parry":
        $ combat_status_message = "Cobori garda. Pararea s-a terminat."
    elif combat_player_action == "light":
        if combat_time < combat_enemy_parry_until:
            $ combat_status_message = "Light blow-ul tău este blocat de pararea lui " + combat_enemy_name + "."
        else:
            $ combat_enemy_health = max(0, combat_enemy_health - combat_player_action_damage)
            $ combat_status_message = "Îl lovești rapid pe " + combat_enemy_name + " pentru " + str(combat_player_action_damage) + " damage."
    elif combat_player_action == "heavy":
        if combat_time < combat_enemy_parry_until:
            $ combat_status_message = "Heavy blow-ul tău este oprit de pararea lui " + combat_enemy_name + "."
        else:
            $ combat_enemy_health = max(0, combat_enemy_health - combat_player_action_damage)
            $ combat_status_message = "Îl lovești puternic pe " + combat_enemy_name + " pentru " + str(combat_player_action_damage) + " damage."

    $ combat_player_action = None
    $ combat_player_action_damage = 0
    $ combat_player_visual = None

    if combat_enemy_health <= 0:
        jump combat_victory

    jump combat_loop

label combat_victory:
    $ in_combat = False
    $ combat_player_action = None
    $ combat_enemy_action = None
    $ combat_player_parry_until = 0.0
    $ combat_enemy_parry_until = 0.0
    $ combat_last_result = "victory"

    if combat_enemy_id == "lup":
        $ wolf_tutorial_done = True
        $ wolf_tutorial_active = False
        $ unlock_zone("zhan", unlock_fast=False)

    if combat_enemy_id == "boier_han":
        $ boier_fight_done = True
        $ boier_attacked = True
        $ boier_defeated = True
        $ got_city_seal = True
        $ city_seal_method = "stolen_from_boier"
        $ add_item("pecete_targoviste")

    if combat_enemy_id == "haiduc_cufar":
        $ haiduc_cufar_fight_done = True
        $ haiduc_cufar_defeated = True
        $ add_item("cufar_boier")

    "[combat_enemy_name] cade. Lupta s-a terminat."
    jump expression combat_return_label

label player_death:
    $ in_combat = False
    $ combat_player_action = None
    $ combat_enemy_action = None
    $ combat_player_parry_until = 0.0
    $ combat_enemy_parry_until = 0.0
    $ combat_last_result = "death"
    $ renpy.block_rollback()
    "Ai murit."
    "Trebuie să revii la o salvare anterioară."
    $ renpy.full_restart()


screen combat_hud(can_choose=False, shown_time=None):
    modal True
    zorder 200

    add "bg han"

    $ hud_time = combat_time if shown_time is None else shown_time
    $ player_ready = combat_player_action is None and hud_time >= combat_player_busy_until
    $ player_remaining = max(0.0, combat_player_busy_until - hud_time)
    $ enemy_remaining = max(0.0, combat_enemy_busy_until - hud_time)
    $ player_parry_remaining = max(0.0, combat_player_parry_until - hud_time)
    $ enemy_parry_remaining = max(0.0, combat_enemy_parry_until - hud_time)

    frame:
        xalign 0.5
        yalign 0.06
        xsize 940
        padding (24, 18)

        vbox:
            spacing 10
            text "Luptă: [combat_enemy_name]" size 34
            text "Timp luptă: [hud_time:.1f]s" size 20
            text "Sănătatea ta: [player_health] / [player_max_health]"
            bar value player_health range player_max_health xmaximum 860
            text "Sănătatea inamicului: [combat_enemy_health] / [combat_enemy_max_health]"
            bar value combat_enemy_health range combat_enemy_max_health xmaximum 860

            # Player action row. The row always keeps the same visual height,
            # so the combat HUD does not jump when the player becomes ready.
            if combat_player_action is not None:
                $ player_action_label = COMBAT_MOVES[combat_player_action]["label"]
                $ player_action_delay = COMBAT_MOVES[combat_player_action]["delay"]
                text "Tu: [player_action_label] — cooldown [player_remaining:.1f]s"
                bar value player_remaining range player_action_delay xmaximum 860
            elif player_ready:
                text "Tu: liber — poți alege o mișcare"
                bar value 0.0 range 1.0 xmaximum 860
            else:
                text "Tu: cooldown [player_remaining:.1f]s"
                bar value player_remaining range 1.0 xmaximum 860

            # Parry row. It is always present to avoid flashing/reflow.
            if player_parry_remaining > 0.0:
                text "Pararea ta este activă încă [player_parry_remaining:.1f]s" size 18
            else:
                text "Pararea ta nu este activă" size 18

            # Enemy action row. The bar is always visible, even when the enemy is idle.
            # This prevents the UI from resizing and feeling like flashing images.
            if combat_enemy_action is not None:
                $ enemy_action_label = COMBAT_MOVES[combat_enemy_action]["label"]
                $ enemy_action_delay = COMBAT_MOVES[combat_enemy_action]["delay"]
                text "[combat_enemy_name]: [enemy_action_label] — impact în [enemy_remaining:.1f]s"
                bar value enemy_remaining range enemy_action_delay xmaximum 860
            elif enemy_parry_remaining > 0.0:
                text "[combat_enemy_name]: parare activă încă [enemy_parry_remaining:.1f]s"
                bar value enemy_parry_remaining range COMBAT_MOVES["parry"]["delay"] xmaximum 860
            else:
                text "[combat_enemy_name]: liber"
                bar value 0.0 range 1.0 xmaximum 860

            if combat_status_message:
                text "[combat_status_message]" size 22

    frame:
        xalign 0.5
        yalign 0.84
        padding (24, 18)

        vbox:
            spacing 12
            if player_ready:
                text "Mișcări disponibile:" size 28
            else:
                text "Mișcări în cooldown:" size 28

            hbox:
                spacing 16
                textbutton "Parare" action Return("parry") sensitive player_ready
                textbutton "Light blow" action Return("light") sensitive player_ready
                textbutton "Heavy blow" action Return("heavy") sensitive player_ready

            if player_ready:
                text "Parare: 2s fără damage. Light: 1s, damage mic. Heavy: 2.8s, damage mare." size 20
            else:
                text "Așteaptă să se termine acțiunea curentă. Lupta continuă între timp." size 20

    if combat_enemy_visual is not None:
        add combat_enemy_visual at combat_enemy_left

    if combat_player_visual is not None:
        add combat_player_visual at combat_player_right

screen combat_live_tick(wait_time=0.05, start_time=0.0, end_time=0.0):
    modal True
    zorder 200

    default display_time = start_time

    timer wait_time action Return("tick")
    use combat_hud(can_choose=True, shown_time=display_time)

screen combat_wait(wait_time=0.5, start_time=0.0, end_time=0.0):
    # Fallback pentru cod vechi. Flow-ul live foloseste combat_live_tick.
    modal True
    zorder 200

    default display_time = start_time

    if wait_time <= 0.0:
        timer 0.01 action Return()
    else:
        timer 0.05 repeat True action If(
            display_time + 0.05 >= end_time,
            Return(),
            SetScreenVariable("display_time", min(end_time, display_time + 0.05))
        )

    use combat_hud(can_choose=False, shown_time=display_time)
