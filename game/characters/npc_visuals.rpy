init python:
    NPC_IMAGE_EXTENSIONS = ("png", "webp", "jpg", "jpeg")

    NPC_IMAGE_CANDIDATES = {
        "batran": [
            "images/enemies/npc_friendly/batranul.png",
        ],
        "boier": [
            "images/enemies/boier/boier_default.png",
        ],
        "haiduc": [
            "images/enemies/haiduc/haiduc_default.png",
        ],
        "lup": [
            "images/lup/lup_default.png",
            "images/enemies/lup/lup_default.png",
        ],
        "ghicitor": [
            "images/enemies/npc_friendly/ghicitorul.png",
        ],
    }

    NPC_IMAGE_KEYWORDS = {
        "batran": ["batranul", "batran", "bătrân"],
        "boier": ["boier"],
        "haiduc": ["haiduc"],
        "lup": ["lup"],
        "ghicitor": ["ghicitorul", "ghicitor"],
    }

    GRID_ACTOR_CELLS = {
        (26, 5): "batran",
        (14, 9): "boier",
        (3, 3): "haiduc",
        (22, 7): "lup",
    }

    def normalize_npc_image_path(path):
        if not path:
            return path
        fixed = path.replace("\\", "/")
        if fixed.startswith("game/"):
            fixed = fixed[5:]
        return fixed

    def is_supported_npc_image_path(path):
        lower = normalize_npc_image_path(path).lower()
        return any(lower.endswith("." + ext) for ext in NPC_IMAGE_EXTENSIONS)

    def npc_image_path(npc_id):
        for candidate in NPC_IMAGE_CANDIDATES.get(npc_id, []):
            path = normalize_npc_image_path(candidate)
            if renpy.loadable(path):
                return path

        keywords = NPC_IMAGE_KEYWORDS.get(npc_id, [npc_id])

        try:
            files = renpy.list_files()
        except Exception:
            files = []

        for raw_path in files:
            path = normalize_npc_image_path(raw_path)
            lower = path.lower()

            if not lower.startswith("images/"):
                continue
            if not is_supported_npc_image_path(path):
                continue
            if any(keyword in lower for keyword in keywords):
                return path

        return None

    def npc_displayable(npc_id, width=520, height=720):
        path = npc_image_path(npc_id)

        if path:
            return Transform(
                path,
                xysize=(width, height),
                fit="contain",
                xalign=0.5,
                yalign=1.0,
            )

        return Null(1, 1)

    def grid_actor_visible(actor_id):
        if actor_id == "boier":
            return not bool(getattr(store, "boier_defeated", False))

        if actor_id == "haiduc":
            return not bool(getattr(store, "haiduc_cufar_defeated", False))

        if actor_id == "lup":
            return not bool(getattr(store, "wolf_tutorial_done", False))

        if actor_id == "ghicitor":
            try:
                return riddler_is_here()
            except Exception:
                return False

        return True

    def grid_actor_at(row, col):
        try:
            if riddler_is_here(row, col):
                return "ghicitor"
        except Exception:
            pass

        actor_id = GRID_ACTOR_CELLS.get((row, col))

        if not actor_id:
            return None

        if not grid_actor_visible(actor_id):
            return None

        return actor_id

transform npc_interaction_right:
    xalign 0.82
    yalign 1.0
    zoom 0.62

transform npc_interaction_left:
    xalign 0.18
    yalign 1.0
    zoom 0.62

transform actor_batran:
    xalign 0.65
    yalign 0.9
    zoom 0.8

transform actor_boier:
    xalign 0.3
    yalign 0.8
    zoom 1.0
    xzoom -1.0

transform actor_haiduc:
    xalign 0.5
    yalign 1.0
    zoom 1.0

transform actor_lup:
    xalign 0.55
    yalign 0.75
    zoom 0.48

transform actor_ghicitor:
    xalign 0.5
    yalign 1.0
    zoom 1.0