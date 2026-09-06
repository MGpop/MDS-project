# systems/npc_system.rpy
# Cu cine poți vorbi în locul unde te afli.
#
# Registrul NPC-urilor stă în characters/npc_data.rpy; aici e doar meniul care
# leagă zona curentă de agentul de dialog liber (ai/dialogue_agent.rpy).

init python:
    def npc_talkable_here():
        """NPC-urile prezente aici care au și persona pentru dialog liber."""
        return [
            npc_id for npc_id in npc_at_location(player_location)
            if npc_persona(npc_id) is not None
        ]


label npc_zone_menu:
    $ _npcs_here = npc_talkable_here()

    if not _npcs_here:
        return

    # Atenție: renpy.display_menu afișează o intrare cu valoarea None ca TITLU,
    # nu ca opțiune selectabilă. De aceea opțiunea de retragere are un marcaj
    # propriu, nu None — altfel butonul apare, dar nu se poate apăsa.
    $ _npc_items = [(NPC_REGISTRY[n]["name"], n) for n in _npcs_here]
    $ _npc_items.append((u"Nu acum", "__inapoi__"))

    narrator "Cine e prin preajmă:"
    $ _npc_choice = renpy.display_menu(_npc_items, screen="choice")

    if _npc_choice == "__inapoi__" or _npc_choice is None:
        return

    call npc_free_talk(_npc_choice)
    jump npc_zone_menu
