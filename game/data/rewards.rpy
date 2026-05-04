init python:
    # Recompense per capitol pentru quest-uri completate
    QUEST_REWARDS = {
        "q01_investigatie": {
            "items":         ["sigiliu_ordin"],
            "loyalty_vlad":   1,
            "xp":             10,
        },
        "q02_tradarea_boierilor": {
            "items":         ["document_boieri"],
            "loyalty_vlad":   0,
            "xp":             20,
        },
        "q03_padurea_tepelor": {
            "items":         [],
            "loyalty_vlad":   0,
            "xp":             20,
        },
        "q04_ordinul_se_rupe": {
            "items":         ["relicva_ordin"],
            "loyalty_vlad":   0,
            "xp":             30,
        },
        "q05_alegerea_finala": {
            "items":         [],
            "loyalty_vlad":   0,
            "xp":             50,
        },
    }

    def give_quest_reward(quest_id):
        reward = QUEST_REWARDS.get(quest_id)
        if reward is None:
            return
        for item_id in reward.get("items", []):
            add_item(item_id)
        player_level += reward.get("xp", 0) // 20
