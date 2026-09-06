# -*- coding: utf-8 -*-
"""Testele agenților, cu un model fals.

Ce verificăm aici e proprietatea de care depinde demo-ul: indiferent ce face
modelul — e oprit, cade, întârzie, întoarce gunoi — agentul întoarce mereu ceva
utilizabil, iar jocul nu vede niciodată o excepție.
"""

from dragon_ai import fallbacks, schemas
from dragon_ai.agents import ChroniclerAgent, DialogueAgent
from dragon_ai.client import FakeLLMClient
from dragon_ai.config import AIConfig


CONFIG = AIConfig()

STARE_CRONICAR = {
    "zona": "han",
    "zona_nume": "Hanul Corbului Negru",
    "capitol": 1,
    "loialitati": {"Vlad": 0, "boieri": 0, "otomani": 0, "Ordin": 0},
    "suspiciune": 0,
    "obiecte": ["Pumnal"],
}

PERSONA = {
    "nume": "Mircea Bălan",
    "factiune": "boyars",
    "rol": "boier conspirator",
    "ton": "mieros",
    "stie": "că boierii uneltesc",
    "nu_stie": "planurile Ordinului",
    "indiciu": "La miezul nopții, la han.",
    "enemy_id": "boier_garda",
}

STARE_DIALOG = {
    "player_name": "Mara",
    "capitol": 1,
    "locatie": "Hanul Corbului Negru",
    "loialitati": {"Vlad": 0, "boieri": 1, "otomani": 0, "Ordin": 2},
    "obiecte": ["Pumnal"],
    "relatie": 1,
    "fapte": [],
}


def cronicar(raspunsuri, disponibil=True):
    return ChroniclerAgent(FakeLLMClient(raspunsuri, disponibil=disponibil), CONFIG)


def dialog(raspunsuri, disponibil=True):
    return DialogueAgent(FakeLLMClient(raspunsuri, disponibil=disponibil), CONFIG)


# --- Cronicarul --------------------------------------------------------------

def test_cronicarul_foloseste_modelul_cand_raspunsul_e_bun():
    raw = '{"eveniment": "ambient", "text": "Cineva ridică paharul spre tine.", "motiv": "atmosferă"}'
    rezultat = cronicar([raw]).pick_event(STARE_CRONICAR, roll=50)
    assert rezultat["sursa"] == "model"
    assert rezultat["eveniment"] == "ambient"


def test_cronicarul_cade_pe_euristica_daca_modelul_e_oprit():
    rezultat = cronicar([], disponibil=False).pick_event(STARE_CRONICAR, roll=10)
    assert rezultat["sursa"] == "fallback"
    assert "nu e pornit" in rezultat["motiv_tehnic"]


def test_cronicarul_cade_pe_euristica_la_json_stricat():
    rezultat = cronicar(["asta nu e JSON"]).pick_event(STARE_CRONICAR, roll=10)
    assert rezultat["sursa"] == "fallback"
    assert "invalid" in rezultat["motiv_tehnic"]


def test_cronicarul_respinge_ambuscada_intr_o_zona_nepotrivita():
    raw = '{"eveniment": "ambuscada", "text": "Cineva sare la tine."}'
    stare = dict(STARE_CRONICAR, zona="curtea_domneasca")
    rezultat = cronicar([raw]).pick_event(stare, roll=90)
    assert rezultat["sursa"] == "fallback"
    assert rezultat["eveniment"] != "ambuscada"


def test_cronicarul_respinge_ambuscada_cand_jucatorul_e_ranit():
    raw = '{"eveniment": "ambuscada", "text": "Cineva sare la tine."}'
    stare = dict(STARE_CRONICAR, zona="padure")
    rezultat = cronicar([raw]).pick_event(stare, roll=90, poate_lupta=False)
    assert rezultat["eveniment"] != "ambuscada"


def test_cronicarul_primeste_in_prompt_doar_evenimentele_permise():
    client = FakeLLMClient(['{"eveniment": "nimic"}'])
    ChroniclerAgent(client, CONFIG).pick_event(dict(STARE_CRONICAR, zona="curtea_domneasca"), roll=1)
    prompt = client.apeluri[0]["user"]
    assert "ambuscada" not in prompt
    assert "ambient" in prompt


def test_cronicarul_nu_arunca_niciodata_indiferent_de_gunoi():
    gunoaie = ["", "null", "{}", "[]", '{"eveniment": 42}', "<html>eroare</html>"]
    for gunoi in gunoaie:
        rezultat = cronicar([gunoi]).pick_event(STARE_CRONICAR, roll=5)
        assert "text" in rezultat and "eveniment" in rezultat


# --- Agentul de dialog -------------------------------------------------------

def test_dialogul_foloseste_modelul_cand_raspunsul_e_bun():
    raw = '{"replica": "Nu te cunosc, străine.", "efect": "niciun_efect", "motiv": "prudent"}'
    rezultat = dialog([raw]).respond(PERSONA, STARE_DIALOG, "Cine ești?")
    assert rezultat["sursa"] == "model"
    assert rezultat["replica"] == "Nu te cunosc, străine."


def test_dialogul_cade_pe_replica_scrisa_de_mana_fara_model():
    rezultat = dialog([], disponibil=False).respond(PERSONA, STARE_DIALOG, "Cine ești?")
    assert rezultat["sursa"] == "fallback"
    assert rezultat["replica"] in fallbacks.REPLICI_FALLBACK["boyars"]


def test_intrebarea_goala_nu_ajunge_la_model():
    client = FakeLLMClient(['{"replica": "..."}'])
    rezultat = DialogueAgent(client, CONFIG).respond(PERSONA, STARE_DIALOG, "   ")
    assert rezultat["sursa"] == "fallback"
    assert client.apeluri == []


def test_promptul_contine_starea_jocului():
    client = FakeLLMClient(['{"replica": "Da."}'])
    DialogueAgent(client, CONFIG).respond(PERSONA, STARE_DIALOG, "Ce știi despre han?")
    prompt = client.apeluri[0]["user"]
    assert "Mara" in prompt
    assert "Pumnal" in prompt
    assert "Ce știi despre han?" in prompt


def test_promptul_ii_spune_personajului_ce_nu_are_voie_sa_stie():
    client = FakeLLMClient(['{"replica": "Da."}'])
    DialogueAgent(client, CONFIG).respond(PERSONA, STARE_DIALOG, "Ce plănuiește Ordinul?")
    system = client.apeluri[0]["system"]
    assert "planurile Ordinului" in system
    assert "NU știi" in system


def test_istoricul_conversatiei_ajunge_in_prompt():
    client = FakeLLMClient(['{"replica": "Da."}'])
    istoric = [("player", "Bună seara."), ("npc", "Ce vrei?")]
    DialogueAgent(client, CONFIG).respond(PERSONA, STARE_DIALOG, "Caut pe cineva.", istoric)
    prompt = client.apeluri[0]["user"]
    assert "Bună seara." in prompt
    assert "Ce vrei?" in prompt


def test_efectul_e_limitat_la_lista_permisa_in_momentul_acela():
    raw = '{"replica": "Gardă!", "efect": "ostil"}'
    permise = [schemas.EFECT_NIMIC]
    rezultat = dialog([raw]).respond(PERSONA, STARE_DIALOG, "Te omor.", efecte_permise=permise)
    assert rezultat["efect"] == schemas.EFECT_NIMIC


def test_dialogul_nu_arunca_niciodata_indiferent_de_gunoi():
    for gunoi in ["", "null", "{}", '{"replica": null}', "eroare 500"]:
        rezultat = dialog([gunoi]).respond(PERSONA, STARE_DIALOG, "Salut")
        assert rezultat["replica"]


# --- Euristica deterministă --------------------------------------------------

def test_euristica_prioritizeaza_suspiciunea_ordinului():
    rezultat = fallbacks.chronicler_event("han", 0, 0, 0, order_suspicion=3, chapter=1, roll=10)
    assert rezultat["eveniment"] == "order_watch"


def test_euristica_tace_cand_starea_e_neutra():
    rezultat = fallbacks.chronicler_event("han", 0, 0, 0, order_suspicion=0, chapter=1, roll=99)
    assert rezultat["eveniment"] == "nimic"


def test_euristica_e_reproductibila():
    argumente = ("padure", 3, 0, 0, 0, 2, 20)
    assert fallbacks.chronicler_event(*argumente) == fallbacks.chronicler_event(*argumente)
