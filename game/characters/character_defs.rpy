init python:
    COLOR_PLAYER  = "#e8d5a3"
    COLOR_VLAD    = "#cc2200"
    COLOR_BOIER   = "#8a7040"
    COLOR_OTOMAN  = "#1a6b3c"
    COLOR_ORDIN   = "#4a4a8a"

define narrator = Character(None)

define player = Character("[player_name]", color="#e8d5a3")

define batran = Character("Bătrânul", color="#b8a27a")

define boier = Character("Boierul", color="#8a7040")

define soldat_roman = Character("Soldatul român", color="#7a8a55")

define haiduc = Character("Haiducul", color="#5f8a4a")



define vlad = Character("Vlad Țepeș", color="#cc2200")

define mircea = Character("Mircea Bălan", color="#8a7040")

define radu = Character("Radu din Craiova", color="#8a7040")

define kemal = Character("Kemal Pașa", color="#1a6b3c")

define calin = Character("Călin — Maestrul Ordinului", color="#4a4a8a")

define voce_necunoscuta = Character("???", color="#555555")





# Definitii clandestine (nu merg bine in alta parte)
image player_parry = "images/player/scut.png"
image player_light = "images/player/pumnal.png"
image player_heavy = "images/player/sabie.png"

image lup_default = "images/enemies/lup/lup_default.png"
image lup_spotted = "images/enemies/lup/lup_default.png"
image lup_fight = "images/enemies/lup/lup_default.png"
image lup_parry = "images/enemies/lup/lup_default.png"
image lup_light = "images/enemies/lup/lup_default.png"
image lup_heavy = "images/enemies/lup/lup_default.png"

image boier_default = "images/enemies/boier/boier_default.png"
image boier_spotted = "images/enemies/boier/boier_default.png"
image boier_fight = "images/enemies/boier/boier_default.png"
image boier_parry = "images/enemies/boier/boier_default.png"
image boier_light = "images/enemies/boier/boier_default.png"
image boier_heavy = "images/enemies/boier/boier_default.png"

image haiduc_default = "images/enemies/haiduc/haiduc_default.png"
image haiduc_spotted = "images/enemies/haiduc/haiduc_default.png"
image haiduc_fight = "images/enemies/haiduc/haiduc_default.png"
image haiduc_parry = "images/enemies/haiduc/haiduc_default.png"
image haiduc_light = "images/enemies/haiduc/haiduc_default.png"
image haiduc_heavy = "images/enemies/haiduc/haiduc_default.png"

image otoman_default = "images/enemies/otoman/otoman_default.png"
image otoman_spotted = "images/enemies/otoman/otoman_spotted.png"
image otoman_fight = "images/enemies/otoman/otoman_fight.png"
image otoman_parry = "images/enemies/otoman/otoman_parry.png"
image otoman_light = "images/enemies/otoman/otoman_light.png"
image otoman_heavy = "images/enemies/otoman/otoman_heavy.png"

image bg han = im.Scale("images/backgrounds/han.png", config.screen_width, config.screen_height)

transform enemy_idle_pos:
    xalign 0.75
    yalign 1.0
    zoom 0.5

transform enemy_alert_pos:
    xalign 0.72
    yalign 1.0
    zoom 0.6

transform combat_enemy_left:
    xalign 0.06
    yalign 0.88
    zoom 0.45

transform combat_player_right:
    xalign 0.94
    yalign 0.88
    zoom 0.38