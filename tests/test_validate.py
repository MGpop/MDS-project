# -*- coding: utf-8 -*-
"""Testele stratului de validare.

Modelele mici greșesc des și în feluri previzibile: JSON stricat, text pe lângă
JSON, chei în engleză, efecte inventate, replici de un paragraf, engleză în loc
de română. Fiecare dintre cazurile de mai jos a fost gândit ca joculsă supraviețuiască
exact acestor greșeli.
"""

from dragon_ai import schemas, validate


TOATE_EFECTELE = list(schemas.EFECTE_DIALOG.keys())
EVENIMENTE = ["nimic", "ambient", "order_watch", "ambuscada"]


# --- escape_renpy ------------------------------------------------------------

def test_escape_paranteze_care_ar_arunca_exceptie_in_renpy():
    # Ren'Py ar încerca să interpoleze [player_name] și să citească {b} ca tag.
    iesire = validate.escape_renpy("Salut [player_name], vezi {b}asta{/b}?")
    assert "[[player_name]" in iesire
    assert "{{b}" in iesire


def test_escape_normalizeaza_spatiile():
    assert validate.escape_renpy("  a\n\n  b  ") == "a b"


def test_escape_accepta_none():
    assert validate.escape_renpy(None) == ""


def test_textul_lung_e_taiat_la_limita_de_propozitie():
    text = ("Prima propoziție e scurtă. " * 30)
    iesire = validate.curata_text(text, 100)
    assert len(iesire) <= 100
    assert iesire.endswith(".")


# --- parse_json_lax ----------------------------------------------------------

def test_json_curat():
    assert validate.parse_json_lax('{"a": 1}') == {"a": 1}


def test_json_inconjurat_de_palavrageala():
    raw = 'Sigur! Iată răspunsul:\n{"a": 1}\nSper că ajută.'
    assert validate.parse_json_lax(raw) == {"a": 1}


def test_json_complet_stricat():
    assert validate.parse_json_lax("nu e json deloc") is None
    assert validate.parse_json_lax("") is None
    assert validate.parse_json_lax('{"a": ') is None


def test_lista_json_nu_e_acceptata():
    assert validate.parse_json_lax('[1, 2, 3]') is None


# --- validate_dialog ---------------------------------------------------------

def test_dialog_valid():
    raw = '{"replica": "Nu am ce vorbi cu tine.", "efect": "incredere_minus", "motiv": "l-a jignit"}'
    rezultat = validate.validate_dialog(raw, TOATE_EFECTELE)
    assert rezultat["replica"] == "Nu am ce vorbi cu tine."
    assert rezultat["efect"] == "incredere_minus"


def test_dialog_accepta_chei_in_engleza():
    raw = '{"reply": "Vorbește mai încet.", "effect": "niciun_efect"}'
    rezultat = validate.validate_dialog(raw, TOATE_EFECTELE)
    assert rezultat["replica"] == "Vorbește mai încet."


def test_efectul_inventat_devine_inofensiv_dar_replica_ramane():
    raw = '{"replica": "Bine.", "efect": "ii_dai_toate_banii"}'
    rezultat = validate.validate_dialog(raw, TOATE_EFECTELE)
    assert rezultat["efect"] == schemas.EFECT_NIMIC
    assert rezultat["replica"] == "Bine."


def test_efectul_nepermis_acum_e_respins():
    # Ostilitatea nu e în lista permisă (ex. jucătorul e prea rănit ca să lupte).
    raw = '{"replica": "Gardă!", "efect": "ostil"}'
    permise = [schemas.EFECT_NIMIC, schemas.EFECT_INCREDERE_PLUS]
    rezultat = validate.validate_dialog(raw, permise)
    assert rezultat["efect"] == schemas.EFECT_NIMIC


def test_dialog_fara_replica_e_inutilizabil():
    assert validate.validate_dialog('{"efect": "ostil"}', TOATE_EFECTELE) is None
    assert validate.validate_dialog('{"replica": "   "}', TOATE_EFECTELE) is None


def test_dialog_pe_json_stricat():
    assert validate.validate_dialog("modelul a uitat de JSON", TOATE_EFECTELE) is None


def test_replica_e_scapata_pentru_renpy():
    raw = '{"replica": "Zi-i lui [player_name] sa taca.", "efect": "niciun_efect"}'
    rezultat = validate.validate_dialog(raw, TOATE_EFECTELE)
    assert "[[player_name]" in rezultat["replica"]


# --- validate_chronicler -----------------------------------------------------

def test_cronicar_valid():
    raw = '{"eveniment": "order_watch", "text": "O umbră te urmărește.", "motiv": "suspiciune"}'
    rezultat = validate.validate_chronicler(raw, EVENIMENTE)
    assert rezultat["eveniment"] == "order_watch"
    assert rezultat["text"] == "O umbră te urmărește."


def test_cronicarul_nu_poate_alege_un_eveniment_nepermis_aici():
    # Ambuscada nu e permisă în Curtea Domnească; agentul trebuie respins.
    raw = '{"eveniment": "ambuscada", "text": "Cineva sare la tine."}'
    assert validate.validate_chronicler(raw, ["nimic", "ambient"]) is None


def test_cronicarul_nu_poate_inventa_evenimente():
    raw = '{"eveniment": "dragon_zburator", "text": "Un dragon."}'
    assert validate.validate_chronicler(raw, EVENIMENTE) is None


def test_evenimentul_nimic_are_voie_sa_fie_fara_text():
    rezultat = validate.validate_chronicler('{"eveniment": "nimic"}', EVENIMENTE)
    assert rezultat["eveniment"] == "nimic"
    assert rezultat["text"] == ""


def test_evenimentul_cu_efect_are_nevoie_de_text():
    assert validate.validate_chronicler('{"eveniment": "order_watch"}', EVENIMENTE) is None


# --- euristica de limbă (folosită de evals) ----------------------------------

def test_pare_romana_recunoaste_romana_si_engleza():
    assert validate.pare_romana("Nu știu ce vrei de la mine.")
    assert validate.pare_romana("Vino mai aproape si taci")   # fără diacritice
    assert not validate.pare_romana("The merchant looks at you.")


# --- listele albe ------------------------------------------------------------

def test_ambuscada_e_permisa_doar_in_locuri_ferite():
    assert "ambuscada" in schemas.evenimente_permise("padure")
    assert "ambuscada" not in schemas.evenimente_permise("curtea_domneasca")


def test_ambuscada_dispare_cand_jucatorul_nu_poate_lupta():
    assert "ambuscada" not in schemas.evenimente_permise("padure", poate_lupta=False)


def test_evenimentele_neutre_sunt_mereu_disponibile():
    for zona in ("targoviste", "curtea_domneasca", "padure", "un_drum_oarecare"):
        permise = schemas.evenimente_permise(zona)
        assert "nimic" in permise and "ambient" in permise


# --- JSON tăiat de limita de tokeni ------------------------------------------
# Cea mai frecventă greșeală reală a modelelor mici: rămân fără tokeni în mijlocul
# unui șir. Înainte de reparație, asta arunca 70% din răspunsurile Cronicarului
# pe fallback degeaba.

def test_json_taiat_in_mijlocul_unui_sir_e_recuperat():
    raw = '{"eveniment": "boyar_whisper", "text": "Un servitor îți strecoară o șoaptă'
    date = validate.parse_json_lax(raw)
    assert date is not None
    assert date["eveniment"] == "boyar_whisper"


def test_json_taiat_dupa_o_virgula_e_recuperat():
    raw = '{"eveniment": "ambient", "text": "Se aude un scârțâit.",'
    date = validate.parse_json_lax(raw)
    assert date is not None
    assert date["text"] == "Se aude un scârțâit."


def test_cronicarul_recupereaza_un_raspuns_taiat():
    raw = '{"eveniment": "order_watch", "text": "Simți o privire în ceafă", "motiv": "suspiciune mar'
    rezultat = validate.validate_chronicler(raw, EVENIMENTE)
    assert rezultat is not None
    assert rezultat["eveniment"] == "order_watch"
    assert "privire" in rezultat["text"]


def test_evenimentul_nimic_nu_afiseaza_naratiune_chiar_daca_modelul_scrie_una():
    # Modelele mici completează „text" din reflex, chiar când au ales „nimic".
    # Altfel jucătorul ar citi un eveniment care nu s-a întâmplat.
    raw = '{"eveniment": "nimic", "text": "Un corb trece pe cer.", "motiv": "stare neutră"}'
    rezultat = validate.validate_chronicler(raw, EVENIMENTE)
    assert rezultat["eveniment"] == "nimic"
    assert rezultat["text"] == ""
