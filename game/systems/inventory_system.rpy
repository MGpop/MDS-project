# systems/inventory_system.rpy
# Inventar vizibil. Helperii de date (add_item/remove_item/has_item) trăiesc în
# data/items.rpy; aici e doar UI-ul care citește dict-ul `inventory` și `ITEMS`.

screen inventory_screen():
    modal True
    zorder 250
    add Solid("#000000DD")

    frame:
        align (0.5, 0.5)
        xsize 900
        ysize 620
        background Solid("#150D06EE")
        padding (30, 26)

        vbox:
            spacing 16

            text "Inventar" style "grid_zone_title" size 36
            text "Nivel [player_level]  •  XP [player_xp]/[XP_PER_LEVEL]" size 20 color "#9a8260"

            null height 6

            if inventory:
                for item_id, count in inventory.items():
                    hbox:
                        spacing 12
                        text "• [ITEMS.get(item_id, {}).get('name', item_id)]" size 22 color "#e8d5a3"
                        if count > 1:
                            text "x[count]" size 22 color "#cca35a"
                    text "   [ITEMS.get(item_id, {}).get('description', '')]" size 16 color "#9a8260"
            else:
                text "   Inventarul e gol." size 18 color "#7a6a50"

            null height 10
            textbutton "Închide (I)" action Return() xalign 1.0

    key "K_i" action Return()
    key "K_ESCAPE" action Return()
