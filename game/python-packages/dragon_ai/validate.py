# -*- coding: utf-8 -*-


import json
import re

from dragon_ai import schemas


def escape_renpy(text):
    if text is None:
        return u""
    text = text.replace("[", "[[").replace("{", "{{")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def curata_text(text, maxim):
    text = escape_renpy(text)
    if len(text) <= maxim:
        return text

    taiat = text[:maxim]
    for semn in (". ", "! ", "? ", "; "):
        poz = taiat.rfind(semn)
        if poz > maxim * 0.5:
            return taiat[:poz + 1].strip()
    return taiat.rstrip() + u"…"


def parse_json_lax(raw):
    if not raw:
        return None

    try:
        date = json.loads(raw)
        return date if isinstance(date, dict) else None
    except (ValueError, TypeError):
        pass

    inceput = raw.find("{")
    sfarsit = raw.rfind("}")
    if inceput != -1 and sfarsit > inceput:
        try:
            date = json.loads(raw[inceput:sfarsit + 1])
            if isinstance(date, dict):
                return date
        except (ValueError, TypeError):
            pass

    return _repara_json_trunchiat(raw)


def _repara_json_trunchiat(raw):
    inceput = raw.find("{")
    if inceput == -1:
        return None

    bucata = raw[inceput:]
    for candidat in (bucata + '"}', bucata + "}", bucata.rstrip().rstrip(",") + "}"):
        try:
            date = json.loads(candidat)
            if isinstance(date, dict):
                return date
        except (ValueError, TypeError):
            continue

    perechi = re.findall(r'"(\w+)"\s*:\s*"((?:[^"\\]|\\.)*)"', bucata)
    if perechi:
        return dict(perechi)
    return None


def _text_din(date, *chei):
    for cheie in chei:
        valoare = date.get(cheie)
        if isinstance(valoare, str) and valoare.strip():
            return valoare.strip()
    return None


def validate_dialog(raw, efecte_permise=None):
    date = parse_json_lax(raw)
    if date is None:
        return None

    replica = _text_din(date, "replica", "reply", "raspuns", "text", "mesaj")
    if not replica:
        return None

    if efecte_permise is None:
        efecte_permise = list(schemas.EFECTE_DIALOG.keys())

    efect = _text_din(date, "efect", "effect", "consecinta") or schemas.EFECT_NIMIC
    efect = efect.strip().lower().replace("-", "_").replace(" ", "_")
    if efect not in efecte_permise:
        efect = schemas.EFECT_NIMIC

    return {
        "replica": curata_text(replica, schemas.MAX_REPLICA),
        "efect": efect,
        "motiv": curata_text(_text_din(date, "motiv", "reason", "explicatie") or u"", schemas.MAX_MOTIV),
    }


def validate_chronicler(raw, evenimente_permise):
    date = parse_json_lax(raw)
    if date is None:
        return None

    eveniment = _text_din(date, "eveniment", "event", "id", "event_id")
    if not eveniment:
        return None
    eveniment = eveniment.strip().lower().replace("-", "_").replace(" ", "_")
    if eveniment not in evenimente_permise:
        return None

    text = _text_din(date, "text", "naratiune", "descriere", "narrative")
    if eveniment == "nimic":
        text = u""
    elif not text:
        return None

    return {
        "eveniment": eveniment,
        "text": curata_text(text, schemas.MAX_NARATIUNE),
        "motiv": curata_text(_text_din(date, "motiv", "reason", "explicatie") or u"", schemas.MAX_MOTIV),
    }


_MARCAJE_ROMANA = (
    " și ", " să ", " nu ", " de ", " la ", " te ", " ce ", " un ", " o ",
    " este ", " ești ", " am ", " ai ", " mai ", " pe ", " cu ", " în ",
)


def pare_romana(text):
    if not text:
        return False
    joasa = " " + text.lower() + " "
    if any(marca in joasa for marca in _MARCAJE_ROMANA):
        return True
    return any(litera in text for litera in u"ăâîșțĂÂÎȘȚ")
