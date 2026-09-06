# -*- coding: utf-8 -*-
"""Listele albe pe care le pot alege agenții.

Modelul are voie să *aleagă* dintre variantele de mai jos și să scrie textul,
dar nu are voie să inventeze efecte. Consecința mecanică e legată determinist de
id, deci un model care halucinează poate cel mult alege prostul eveniment — nu
poate strica starea jocului.
"""

# --- Agentul de dialog -------------------------------------------------------

EFECT_NIMIC = "niciun_efect"
EFECT_INCREDERE_PLUS = "incredere_plus"
EFECT_INCREDERE_MINUS = "incredere_minus"
EFECT_INDICIU = "dezvaluie_indiciu"
EFECT_OSTIL = "ostil"

EFECTE_DIALOG = {
    EFECT_NIMIC: u"NPC-ul răspunde, dar nimic nu se schimbă.",
    EFECT_INCREDERE_PLUS: u"L-ai impresionat sau l-ai liniștit: are mai multă încredere în tine.",
    EFECT_INCREDERE_MINUS: u"L-ai jignit, l-ai amenințat prost sau te-ai dat de gol: are mai puțină încredere.",
    EFECT_INDICIU: u"L-ai convins să-ți spună ceva ce nu spune oricui.",
    EFECT_OSTIL: u"L-ai împins prea departe: pune mâna pe armă.",
}

# Lungimea maximă a unei replici, ca să încapă în caseta de dialog.
MAX_REPLICA = 320
MAX_NARATIUNE = 300
MAX_MOTIV = 160


# --- Agentul cronicar --------------------------------------------------------
# "efect" e citit de partea de Ren'Py și tradus în modificări de stare.
# "zone" gol = evenimentul e permis oriunde.

EVENIMENTE_CRONICAR = {
    "nimic": {
        "descriere": u"Nu se întâmplă nimic demn de povestit.",
        "scurt": u"nu se întâmplă nimic",
        "efect": None,
        "zone": [],
    },
    "ambient": {
        "descriere": u"Un detaliu de atmosferă din zonă, fără consecințe.",
        "scurt": u"detaliu de atmosferă, fără consecințe",
        "efect": None,
        "zone": [],
    },
    "order_watch": {
        "descriere": u"Un om al Ordinului te urmărește de la distanță. Potrivit când Ordinul te suspectează.",
        "scurt": u"Ordinul te urmărește (cere suspiciune mare)",
        "efect": "suspiciune_plus",
        "zone": [],
    },
    "ottoman_patrol": {
        "descriere": u"O patrulă otomană trece pe lângă tine. Potrivit când ai legături cu otomanii.",
        "scurt": u"patrulă otomană (cere legătură cu otomanii)",
        "efect": None,
        "zone": [],
    },
    "vlad_salute": {
        "descriere": u"Un soldat al lui Vlad te recunoaște și te salută. Potrivit când ești în grațiile lui Vlad.",
        "scurt": u"soldat al lui Vlad te salută (cere legătură cu Vlad)",
        "efect": None,
        "zone": [],
    },
    "boyar_whisper": {
        "descriere": u"Un servitor îți strecoară o șoaptă din partea boierilor. Potrivit când boierii te consideră aliat.",
        "scurt": u"șoaptă de la boieri (cere legătură cu boierii)",
        "efect": None,
        "zone": [],
    },
    "informator": {
        "descriere": u"Un informator al Ordinului îți dă pe furiș o informație utilă.",
        "scurt": u"informator al Ordinului îți dă o informație",
        "efect": "incredere_ordin_plus",
        "zone": ["targoviste", "han", "drum_targoviste_han", "drum_targoviste_curtea"],
    },
    "ambuscada": {
        "descriere": u"Cineva te-a urmărit și te atacă. Doar în locuri ferite, și doar dacă jucătorul e în stare să lupte.",
        "scurt": u"cineva te atacă din umbră",
        "efect": "lupta",
        "zone": ["padure", "camp_han_padure", "drum_padure_tabara", "tabara_otomana"],
    },
}

EVENIMENTE_NEUTRE = ("nimic", "ambient")


def evenimente_permise(zona, poate_lupta=True):
    """Ce evenimente au sens aici și acum. Restul sunt respinse la validare."""
    permise = []
    for eid, date in EVENIMENTE_CRONICAR.items():
        zone = date["zone"]
        if zone and zona not in zone:
            continue
        if date["efect"] == "lupta" and not poate_lupta:
            continue
        permise.append(eid)
    return sorted(permise)


def descriere_scurta(eveniment_id):
    """Varianta pentru prompt. Fiecare token din prompt costă timp de prefill,
    iar prefill-ul e cea mai scumpă parte a unui apel pe CPU."""
    date = EVENIMENTE_CRONICAR.get(eveniment_id, {})
    return date.get("scurt") or date.get("descriere", u"")


def efect_eveniment(eveniment_id):
    return EVENIMENTE_CRONICAR.get(eveniment_id, {}).get("efect")
