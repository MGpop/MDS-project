init python:
    ITEM_IMAGE_DIR = "images/items"
    ITEM_IMAGE_EXTENSIONS = ("png", "webp", "jpg", "jpeg")

    def item_data(item_id):
        return ITEMS.get(item_id, {})

    def item_name(item_id):
        return item_data(item_id).get("name", item_id)

    def item_description(item_id):
        return item_data(item_id).get("description", "Nu ai informații despre acest obiect.")

    def item_type(item_id):
        return item_data(item_id).get("type", "misc")

    def item_is_stackable(item_id):
        return bool(item_data(item_id).get("stackable", False))

    def item_image_path(item_id):
        data = item_data(item_id)

        custom_path = data.get("image")
        if custom_path and renpy.loadable(custom_path):
            return custom_path

        for ext in ITEM_IMAGE_EXTENSIONS:
            path = ITEM_IMAGE_DIR + "/" + item_id + "." + ext
            if renpy.loadable(path):
                return path

        return None

    def item_icon_displayable(item_id, size=72):
        path = item_image_path(item_id)

        if path:
            return Transform(
                path,
                xysize=(size, size),
                fit="contain",
                xalign=0.5,
                yalign=0.5,
            )

        return Transform(
            Solid("#2A2A2A"),
            xysize=(size, size),
            xalign=0.5,
            yalign=0.5,
        )

    def inventory_item_ids():
        ids = []

        for item_id, count in store.inventory.items():
            if count > 0:
                ids.append(item_id)

        ids.sort(key=lambda item_id: item_name(item_id).lower())
        return ids

    def inventory_rows(columns=3):
        ids = inventory_item_ids()
        return [ids[i:i + columns] for i in range(0, len(ids), columns)]

    def inventory_item_count_text(item_id):
        count = store.inventory.get(item_id, 0)

        if count <= 1 and not item_is_stackable(item_id):
            return ""

        return "x" + str(count)

    def inventory_item_tooltip(item_id):
        lines = [
            item_name(item_id),
            "",
            item_description(item_id),
            "",
            "Tip: " + item_type(item_id),
        ]

        count = store.inventory.get(item_id, 0)
        if count > 1:
            lines.append("Cantitate: " + str(count))

        return "\n".join(lines)


screen inventory_item_slot(item_id):
    $ _count_text = inventory_item_count_text(item_id)

    button:
        xsize 250
        ysize 150
        background Solid("#17110BCC")
        hover_background Solid("#352312DD")
        action NullAction()
        tooltip inventory_item_tooltip(item_id)

        vbox:
            xalign 0.5
            yalign 0.5
            spacing 8

            fixed:
                xsize 82
                ysize 82
                xalign 0.5

                add item_icon_displayable(item_id, 72):
                    xalign 0.5
                    yalign 0.5

                if _count_text:
                    frame:
                        xalign 1.0
                        yalign 1.0
                        background Solid("#000000CC")
                        xpadding 5
                        ypadding 2

                        text _count_text size 16 color "#FFFFFF"

            text item_name(item_id):
                xalign 0.5
                text_align 0.5
                size 20
                color "#E8D5A3"
                outlines [(1, "#000000", 1, 1)]

            text item_type(item_id).capitalize():
                xalign 0.5
                text_align 0.5
                size 15
                color "#A58E68"


screen inventory_screen():
    modal True

    $ _tooltip = GetTooltip()
    $ _rows = inventory_rows(3)

    add Solid("#000000DD")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 940
        ysize 690
        background Solid("#090704F2")
        xpadding 24
        ypadding 22

        vbox:
            spacing 16

            hbox:
                xfill True
                ysize 46

                text "Inventar":
                    size 34
                    color "#D4AF37"
                    outlines [(1, "#000000", 1, 1)]
                    yalign 0.5

                null width 20

                text "I / Esc pentru închidere":
                    size 18
                    color "#A58E68"
                    yalign 0.5

                textbutton "Închide":
                    xalign 1.0
                    yalign 0.5
                    action Return(None)
                    style "inventory_close_btn"

            if not _rows:
                frame:
                    xfill True
                    ysize 500
                    background Solid("#120D08CC")
                    xpadding 20
                    ypadding 20

                    text "Inventarul este gol.":
                        xalign 0.5
                        yalign 0.5
                        size 26
                        color "#C0A080"
            else:
                viewport:
                    xfill True
                    ysize 500
                    mousewheel True
                    draggable True
                    scrollbars "vertical"

                    vbox:
                        spacing 14

                        for row in _rows:
                            hbox:
                                spacing 14

                                for item_id in row:
                                    use inventory_item_slot(item_id)

                                for i in range(3 - len(row)):
                                    null width 250 height 150

            frame:
                xfill True
                ysize 82
                background Solid("#120D08DD")
                xpadding 16
                ypadding 10

                if _tooltip:
                    text _tooltip:
                        size 18
                        color "#E8D5A3"
                        line_spacing 2
                else:
                    text "Treci cu mouse-ul peste un obiect pentru descriere.":
                        size 18
                        color "#8F7A5B"
                        yalign 0.5

    key "K_ESCAPE" action Return(None)
    key "K_i" action Return(None)


label open_inventory:
    call screen inventory_screen
    return


style inventory_close_btn:
    xpadding 14
    ypadding 8
    background Solid("#2A1A0A")
    hover_background Solid("#5A3A1A")

style inventory_close_btn_text:
    color "#E8D5A3"
    hover_color "#FFD700"
    size 18