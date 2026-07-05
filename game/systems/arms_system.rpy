init python:
    ARM_IMAGE_DIR = "images/arms"
    ARM_IMAGE_EXTENSIONS = ("png", "webp", "jpg", "jpeg")

    ARM_TYPES = ["dagger", "sword", "shield"]

    ARM_TYPE_LABELS = {
        "dagger": "Pumnal",
        "sword": "Sabie",
        "shield": "Scut",
    }

    ARM_TYPE_PLURAL_LABELS = {
        "dagger": "Pumnale",
        "sword": "Săbii",
        "shield": "Scuturi",
    }

    ARM_TYPE_ORDER = {
        "dagger": 0,
        "sword": 1,
        "shield": 2,
    }

    ARM_TYPE_IMAGE_DIRS = {
        "dagger": ARM_IMAGE_DIR + "/light_weapons",
        "sword": ARM_IMAGE_DIR + "/heavy_weapons",
        "shield": ARM_IMAGE_DIR + "/shields",
    }

    ARM_SET_FALLBACK_IDS = {
        "soldat": ["pumnal_soldat", "sabie_soldat", "scut_soldat"],
        "haiduc": ["pumnal_haiduc", "sabie_haiduc", "scut_haiduc"],
    }

    ARM_DATA_OVERRIDES = {
        "pumnal_soldat": {
            "name": "Pumnal de soldat",
            "type": "dagger",
            "set": "soldat",
            "damage": 9,
            "speed": 1.15,
            "defense": 0,
            "description": "Un pumnal scurt, simplu, făcut pentru lovituri rapide.",
        },
        "sabie_soldat": {
            "name": "Sabie de soldat",
            "type": "sword",
            "set": "soldat",
            "damage": 18,
            "speed": 0.95,
            "defense": 0,
            "description": "O sabie dreaptă, grea, dar de încredere.",
        },
        "scut_soldat": {
            "name": "Scut de soldat",
            "type": "shield",
            "set": "soldat",
            "damage": 0,
            "speed": 0.90,
            "defense": 8,
            "description": "Un scut solid. Încetinește puțin pararea, dar oferă protecție bună.",
        },
        "pumnal_haiduc": {
            "name": "Pumnal de haiduc",
            "type": "dagger",
            "set": "haiduc",
            "damage": 11,
            "speed": 1.30,
            "defense": 0,
            "description": "Un pumnal ușor, bun pentru atacuri rapide și murdare.",
        },
        "sabie_haiduc": {
            "name": "Sabie de haiduc",
            "type": "sword",
            "set": "haiduc",
            "damage": 21,
            "speed": 1.05,
            "defense": 0,
            "description": "O sabie purtată în ambuscade. Mai rapidă decât o sabie de soldat.",
        },
        "scut_haiduc": {
            "name": "Scut de haiduc",
            "type": "shield",
            "set": "haiduc",
            "damage": 0,
            "speed": 1.25,
            "defense": 5,
            "description": "Un scut ușor, potrivit pentru mișcare rapidă, dar mai slab la protecție.",
        },
    }

    BASE_COMBAT_MOVE_DELAYS = {
        "light": 1.0,
        "heavy": 2.8,
        "parry": 2.0,
    }

    def ensure_arm_state():
        if not hasattr(store, "owned_arms") or store.owned_arms is None:
            store.owned_arms = []

        if not hasattr(store, "equipped_arms") or not isinstance(store.equipped_arms, dict):
            store.equipped_arms = {}

        for arm_t in ARM_TYPES:
            if arm_t not in store.equipped_arms:
                store.equipped_arms[arm_t] = None

    def normalize_renpy_path(path):
        if not path:
            return path

        fixed = path.replace("\\", "/")
        if fixed.startswith("game/"):
            fixed = fixed[5:]

        return fixed

    def _arm_file_id(path):
        filename = normalize_renpy_path(path).split("/")[-1]
        if "." not in filename:
            return None
        return filename.rsplit(".", 1)[0]

    def _arm_type_from_path(path):
        lower = normalize_renpy_path(path).lower()

        if "/light_weapons/" in lower:
            return "dagger"
        if "/heavy_weapons/" in lower:
            return "sword"
        if "/shields/" in lower:
            return "shield"

        return None

    def discover_arm_image_info():
        info = {}
        prefix = ARM_IMAGE_DIR + "/"

        try:
            files = renpy.list_files()
        except Exception:
            files = []

        for raw_path in files:
            path = normalize_renpy_path(raw_path)
            lower = path.lower()

            if not lower.startswith(prefix):
                continue
            if not any(lower.endswith("." + ext) for ext in ARM_IMAGE_EXTENSIONS):
                continue

            arm_id = _arm_file_id(path)
            if not arm_id:
                continue

            if arm_id not in info:
                info[arm_id] = {
                    "path": path,
                    "type": _arm_type_from_path(path),
                }

        return info

    def discover_arm_image_ids():
        return list(discover_arm_image_info().keys())

    def infer_arm_type(arm_id):
        info = discover_arm_image_info().get(arm_id)
        if info and info.get("type"):
            return info["type"]

        lower = arm_id.lower()

        if "pumnal" in lower or "dagger" in lower or "cutit" in lower or "cuțit" in lower:
            return "dagger"
        if "scut" in lower or "shield" in lower:
            return "shield"
        if "sabie" in lower or "sword" in lower:
            return "sword"

        return "sword"

    def infer_arm_set(arm_id):
        if "_" in arm_id:
            return arm_id.rsplit("_", 1)[1]
        return "necunoscut"

    def _stable_arm_score(arm_id):
        total = 0
        for index, char in enumerate(arm_id):
            total += (index + 1) * ord(char)
        return total

    def inferred_arm_data(arm_id):
        arm_t = infer_arm_type(arm_id)
        arm_set_id = infer_arm_set(arm_id)
        score = _stable_arm_score(arm_id)

        if arm_t == "dagger":
            base_damage = 8
            base_speed = 1.05
            base_defense = 0
        elif arm_t == "shield":
            base_damage = 0
            base_speed = 0.95
            base_defense = 4
        else:
            base_damage = 16
            base_speed = 0.90
            base_defense = 0

        if arm_set_id == "soldat":
            set_damage = 1
            set_speed = 0.03
            set_defense = 2
        elif arm_set_id == "haiduc":
            set_damage = 3
            set_speed = 0.16
            set_defense = 1
        else:
            set_damage = score % 4
            set_speed = (score % 7) / 100.0
            set_defense = score % 3

        return {
            "name": arm_id.replace("_", " ").title(),
            "type": arm_t,
            "set": arm_set_id,
            "damage": base_damage + set_damage + (score % 3),
            "speed": round(base_speed + set_speed + ((score % 5) / 100.0), 2),
            "defense": base_defense + set_defense + (score % 2),
            "description": "Armă descoperită automat din game/images/arms.",
        }

    def arm_data(arm_id):
        if arm_id in ARM_DATA_OVERRIDES:
            return ARM_DATA_OVERRIDES[arm_id]
        return inferred_arm_data(arm_id)

    def arm_name(arm_id):
        return arm_data(arm_id).get("name", arm_id)

    def arm_type(arm_id):
        return arm_data(arm_id).get("type", infer_arm_type(arm_id))

    def arm_set(arm_id):
        return arm_data(arm_id).get("set", infer_arm_set(arm_id))

    def all_arm_ids():
        ids = set(ARM_DATA_OVERRIDES.keys())
        for arm_id in discover_arm_image_ids():
            ids.add(arm_id)

        return sorted(ids, key=lambda arm_id: (ARM_TYPE_ORDER.get(arm_type(arm_id), 99), arm_name(arm_id).lower()))

    def arm_damage(arm_id):
        if not arm_id:
            return 0
        return int(arm_data(arm_id).get("damage", 0))

    def arm_speed(arm_id):
        if not arm_id:
            return 1.0
        return float(arm_data(arm_id).get("speed", 1.0))

    def arm_defense(arm_id):
        if not arm_id:
            return 0
        return int(arm_data(arm_id).get("defense", 0))

    def arm_description(arm_id):
        return arm_data(arm_id).get("description", "Fără descriere.")

    def arm_image_path(arm_id):
        data = arm_data(arm_id)

        custom_path = normalize_renpy_path(data.get("image"))
        if custom_path and renpy.loadable(custom_path):
            return custom_path

        discovered = discover_arm_image_info().get(arm_id)
        if discovered:
            discovered_path = normalize_renpy_path(discovered.get("path"))
            if discovered_path and renpy.loadable(discovered_path):
                return discovered_path

        arm_t = arm_type(arm_id)
        type_dir = ARM_TYPE_IMAGE_DIRS.get(arm_t)

        if type_dir:
            for ext in ARM_IMAGE_EXTENSIONS:
                path = type_dir + "/" + arm_id + "." + ext
                if renpy.loadable(path):
                    return path

        for folder in ARM_TYPE_IMAGE_DIRS.values():
            for ext in ARM_IMAGE_EXTENSIONS:
                path = folder + "/" + arm_id + "." + ext
                if renpy.loadable(path):
                    return path

        for ext in ARM_IMAGE_EXTENSIONS:
            path = ARM_IMAGE_DIR + "/" + arm_id + "." + ext
            if renpy.loadable(path):
                return path

        return None

    def arm_icon_displayable(arm_id, size=86):
        path = arm_image_path(arm_id)

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

    def arm_combat_displayable(arm_id, size=260):
        path = arm_image_path(arm_id)

        if path:
            return Transform(
                path,
                xysize=(size, size),
                fit="contain",
                xalign=0.5,
                yalign=0.5,
            )

        return None

    def arm_ids_for_set(set_id):
        suffix = "_" + set_id
        discovered = [arm_id for arm_id in all_arm_ids() if arm_id.endswith(suffix)]

        if discovered:
            return sorted(discovered, key=lambda arm_id: ARM_TYPE_ORDER.get(arm_type(arm_id), 99))

        return ARM_SET_FALLBACK_IDS.get(set_id, [])

    def player_owns_arm(arm_id):
        ensure_arm_state()
        return arm_id in store.owned_arms

    def player_has_arm_set(set_id):
        ensure_arm_state()
        ids = arm_ids_for_set(set_id)
        if not ids:
            return False

        for arm_id in ids:
            if arm_id not in store.owned_arms:
                return False

        return True

    def grant_arm(arm_id, equip_if_empty=False):
        ensure_arm_state()

        if arm_id not in store.owned_arms:
            store.owned_arms.append(arm_id)

        arm_t = arm_type(arm_id)
        if equip_if_empty and not store.equipped_arms.get(arm_t):
            store.equipped_arms[arm_t] = arm_id

        sync_combat_move_stats()

    def grant_arm_set(set_id, equip=False):
        ensure_arm_state()
        ids = arm_ids_for_set(set_id)

        for arm_id in ids:
            grant_arm(arm_id, equip_if_empty=False)

        if equip:
            for arm_id in ids:
                equip_arm(arm_id, restart=False)

        ensure_default_equipment()
        sync_combat_move_stats()
        renpy.restart_interaction()
        return ids

    def equip_arm(arm_id, restart=True):
        ensure_arm_state()

        if arm_id not in store.owned_arms:
            return False

        arm_t = arm_type(arm_id)
        if arm_t not in ARM_TYPES:
            return False

        store.equipped_arms[arm_t] = arm_id
        sync_combat_move_stats()

        if restart:
            renpy.restart_interaction()

        return True

    def equipped_arm(arm_t):
        ensure_arm_state()
        return store.equipped_arms.get(arm_t)

    def ensure_default_equipment():
        ensure_arm_state()
        changed = False

        for arm_t in ARM_TYPES:
            current = store.equipped_arms.get(arm_t)
            if current and current in store.owned_arms and arm_type(current) == arm_t:
                continue

            options = owned_arms_by_type(arm_t)
            if options:
                store.equipped_arms[arm_t] = options[0]
                changed = True
            else:
                store.equipped_arms[arm_t] = None

        if changed:
            sync_combat_move_stats()

        return changed

    def unequipped_arms_by_type(arm_t):
        ensure_arm_state()
        equipped_id = equipped_arm(arm_t)
        ids = []

        for arm_id in store.owned_arms:
            if arm_type(arm_id) == arm_t and arm_id != equipped_id:
                ids.append(arm_id)

        return sorted(ids, key=lambda arm_id: arm_name(arm_id).lower())

    def owned_arms_by_type(arm_t):
        ensure_arm_state()
        ids = []

        for arm_id in store.owned_arms:
            if arm_type(arm_id) == arm_t:
                ids.append(arm_id)

        return sorted(ids, key=lambda arm_id: arm_name(arm_id).lower())

    def arm_damage_range(arm_id):
        base = arm_damage(arm_id)
        if base <= 0:
            return (0, 0)

        spread = max(1, int(round(base * 0.15)))
        return (max(1, base - spread), base + spread)

    def sync_combat_move_stats():
        ensure_arm_state()

        if "COMBAT_MOVES" not in globals():
            return

        dagger = equipped_arm("dagger")
        sword = equipped_arm("sword")
        shield = equipped_arm("shield")

        if dagger:
            COMBAT_MOVES["light"]["player_damage"] = arm_damage_range(dagger)
            COMBAT_MOVES["light"]["delay"] = round(BASE_COMBAT_MOVE_DELAYS["light"] / max(0.25, arm_speed(dagger)), 2)

        if sword:
            COMBAT_MOVES["heavy"]["player_damage"] = arm_damage_range(sword)
            COMBAT_MOVES["heavy"]["delay"] = round(BASE_COMBAT_MOVE_DELAYS["heavy"] / max(0.25, arm_speed(sword)), 2)

        if shield:
            COMBAT_MOVES["parry"]["delay"] = round(BASE_COMBAT_MOVE_DELAYS["parry"] / max(0.25, arm_speed(shield)), 2)

    def combat_visual_for_player_action(action_id):
        ensure_arm_state()

        if action_id == "light":
            return arm_combat_displayable(equipped_arm("dagger"), 260) or "player_light"
        if action_id == "heavy":
            return arm_combat_displayable(equipped_arm("sword"), 300) or "player_heavy"
        if action_id == "parry":
            return arm_combat_displayable(equipped_arm("shield"), 300) or "player_parry"
        return None

    def arm_tooltip(arm_id):
        if not arm_id:
            return "Nimic echipat."

        lines = [
            arm_name(arm_id),
            "",
            arm_description(arm_id),
            "",
            "Tip: " + ARM_TYPE_LABELS.get(arm_type(arm_id), arm_type(arm_id)),
            "Set: " + arm_set(arm_id),
            "Damage: " + str(arm_damage(arm_id)),
            "Viteză: " + str(arm_speed(arm_id)) + "x",
        ]

        if arm_type(arm_id) == "shield":
            lines.append("Apărare: " + str(arm_defense(arm_id)))

        return "\n".join(lines)


screen arm_card(arm_id, equipped=False):
    button:
        xsize 170
        ysize 150
        background Solid("#17110BCC")
        hover_background Solid("#352312DD")
        selected_background Solid("#3A2A0ADD")
        action If(equipped, NullAction(), Function(equip_arm, arm_id))
        tooltip arm_tooltip(arm_id)

        vbox:
            xalign 0.5
            yalign 0.5
            spacing 6

            add arm_icon_displayable(arm_id, 76):
                xalign 0.5

            text arm_name(arm_id):
                xalign 0.5
                text_align 0.5
                size 16
                color "#E8D5A3"

            if equipped:
                text "Echipat":
                    xalign 0.5
                    size 14
                    color "#FFD700"
            else:
                text "Click pentru echipare":
                    xalign 0.5
                    size 13
                    color "#A58E68"


screen equipped_arm_panel(arm_t):
    $ ensure_arm_state()
    $ _arm_id = equipped_arm(arm_t)
    $ _label = ARM_TYPE_LABELS.get(arm_t, arm_t)

    frame:
        xfill True
        ysize 160
        background Solid("#120D08CC")
        xpadding 14
        ypadding 12

        hbox:
            spacing 12

            if _arm_id:
                add arm_icon_displayable(_arm_id, 86)
            else:
                add Solid("#2A2A2A", xsize=86, ysize=86)

            vbox:
                spacing 4
                text _label size 20 color "#D4AF37"

                if _arm_id:
                    text arm_name(_arm_id) size 18 color "#E8D5A3"
                    text "Damage: [arm_damage(_arm_id)]" size 16 color "#C0A080"
                    text "Viteză: [arm_speed(_arm_id)]x" size 16 color "#C0A080"
                    if arm_t == "shield":
                        text "Apărare: [arm_defense(_arm_id)]" size 16 color "#C0A080"
                else:
                    text "Nimic echipat" size 18 color "#8F7A5B"


screen arms_collection_row(arm_t):
    $ ensure_arm_state()
    $ _label = ARM_TYPE_PLURAL_LABELS.get(arm_t, ARM_TYPE_LABELS.get(arm_t, arm_t))
    $ _arms = unequipped_arms_by_type(arm_t)

    frame:
        xfill True
        ysize 190
        background Solid("#120D08CC")
        xpadding 12
        ypadding 10

        vbox:
            spacing 8
            text _label + " disponibile" size 22 color "#D4AF37"

            if _arms:
                viewport:
                    xfill True
                    ysize 150
                    draggable True
                    mousewheel True
                    scrollbars "horizontal"

                    hbox:
                        spacing 10
                        for arm_id in _arms:
                            use arm_card(arm_id)
            else:
                text "Nu ai arme neechipate din această categorie." size 17 color "#8F7A5B"


screen arms_screen():
    modal True

    $ ensure_arm_state()
    $ ensure_default_equipment()
    $ _tooltip = GetTooltip()

    add Solid("#000000DD")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 1180
        ysize 720
        background Solid("#090704F2")
        xpadding 24
        ypadding 22

        vbox:
            spacing 16

            hbox:
                xfill True
                ysize 44

                text "Arme":
                    size 34
                    color "#D4AF37"
                    outlines [(1, "#000000", 1, 1)]
                    yalign 0.5

                null width 20

                text "P / Esc pentru închidere":
                    size 18
                    color "#A58E68"
                    yalign 0.5

                textbutton "Închide":
                    xalign 1.0
                    yalign 0.5
                    action Return(None)
                    style "arms_close_btn"

            hbox:
                spacing 18

                frame:
                    xsize 380
                    ysize 530
                    background Solid("#0E0A06DD")
                    xpadding 14
                    ypadding 14

                    vbox:
                        spacing 12
                        text "Echipate" size 26 color "#E8D5A3"
                        use equipped_arm_panel("dagger")
                        use equipped_arm_panel("sword")
                        use equipped_arm_panel("shield")

                frame:
                    xsize 720
                    ysize 530
                    background Solid("#0E0A06DD")
                    xpadding 14
                    ypadding 14

                    vbox:
                        spacing 12
                        text "Arme de schimb" size 26 color "#E8D5A3"
                        use arms_collection_row("dagger")
                        use arms_collection_row("sword")
                        use arms_collection_row("shield")

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
                    text "Treci cu mouse-ul peste o armă pentru stats. Click pe o armă neechipată pentru echipare.":
                        size 18
                        color "#8F7A5B"
                        yalign 0.5

    key "K_ESCAPE" action Return(None)
    key "K_p" action Return(None)


label open_arms:
    $ ensure_arm_state()
    $ ensure_default_equipment()
    $ sync_combat_move_stats()
    call screen arms_screen
    $ ensure_arm_state()
    $ ensure_default_equipment()
    $ sync_combat_move_stats()
    return


style arms_close_btn:
    xpadding 14
    ypadding 8
    background Solid("#2A1A0A")
    hover_background Solid("#5A3A1A")

style arms_close_btn_text:
    color "#E8D5A3"
    hover_color "#FFD700"
    size 18