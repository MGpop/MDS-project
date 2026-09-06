# -*- coding: utf-8 -*-
"""Instanțele vii ale agenților și rularea apelurilor pe fir separat.

De ce trăiesc aici și nu în store-ul Ren'Py: clientul are un threading.Lock, iar
Ren'Py încearcă să serializeze în save orice variabilă din store modificată după
init. Ținute ca atribute de modul, agenții nu ajung niciodată în save file.
"""

import threading

from dragon_ai.agents import ChroniclerAgent, DialogueAgent
from dragon_ai.client import LocalLLMClient
from dragon_ai.config import AIConfig

_stare = {
    "config": None,
    "client": None,
    "chronicler": None,
    "dialogue": None,
}


def configure(**kwargs):
    """(Re)construiește agenții. Apelat la pornire și când se schimbă setările."""
    config = AIConfig(**kwargs)
    client = LocalLLMClient(config)
    _stare["config"] = config
    _stare["client"] = client
    _stare["chronicler"] = ChroniclerAgent(client, config)
    _stare["dialogue"] = DialogueAgent(client, config)
    return config


def _asigura():
    if _stare["config"] is None:
        configure()


def config():
    _asigura()
    return _stare["config"]


def client():
    _asigura()
    return _stare["client"]


def chronicler():
    _asigura()
    return _stare["chronicler"]


def dialogue():
    _asigura()
    return _stare["dialogue"]


def is_available(force=False):
    return client().is_available(force=force)


def _warmup_toate():
    c = client()
    cfg = config()
    ok = c.warmup(model=cfg.model)
    if cfg.chronicler_model != cfg.model:
        ok = c.warmup(model=cfg.chronicler_model) and ok
    return ok


def warmup_async():
    """Încălzește în fundal, la pornirea jocului, modelele folosite de agenți."""
    return run_async(_warmup_toate)


def run_async(fn, *args, **kwargs):
    """Pornește apelul pe alt fir și întoarce o cutie pe care jocul o poate urmări.

    Firul nu atinge nimic din Ren'Py — doar HTTP și dicționare — deci partea de
    joc rămâne liberă să deseneze ecranul „se gândește" cât timp modelul lucrează.
    """
    cutie = {"done": False, "value": None, "error": None}

    def worker():
        try:
            cutie["value"] = fn(*args, **kwargs)
        except Exception as exc:               # nimic nu are voie să scape spre joc
            cutie["error"] = "%s: %s" % (type(exc).__name__, exc)
        finally:
            cutie["done"] = True

    fir = threading.Thread(target=worker)
    fir.daemon = True
    fir.start()
    return cutie
