# -*- coding: utf-8 -*-
"""Plasa de siguranță: ce se întâmplă când modelul local lipsește sau greșește.

Astea sunt euristicile deterministe scrise de mână. Jocul rulează identic pe ele,
fără nicio eroare vizibilă — de aceea demo-ul e sigur chiar și fără Ollama pornit.
"""

# Pragul de la care o facțiune e considerată dominantă pentru evenimente.
PRAG_FACTIUNE = 2


def chronicler_event(zona, loyalty_vlad, loyalty_boyars, loyalty_ottomans,
                     order_suspicion, chapter, roll):
    """Alege un eveniment fără model. Funcție pură, deci ușor de testat.

    Regulile sunt în ordinea priorității: cel mai puternic semnal de stare câștigă,
    dar fiecare e „poartă" cu un roll (0..99), ca să nu apară la fiecare pas.
    """
    if order_suspicion >= PRAG_FACTIUNE and roll < 60:
        return {
            "eveniment": "order_watch",
            "text": u"Simți o privire în ceafă. O umbră a Ordinului te urmărește de la distanță — bănuiala lor crește.",
            "motiv": u"Ordinul te suspectează (suspiciune %d)." % order_suspicion,
        }

    if loyalty_ottomans >= PRAG_FACTIUNE and roll < 55:
        return {
            "eveniment": "ottoman_patrol",
            "text": u"O patrulă otomană trece pe lângă tine. Un soldat îți face un semn discret din cap — ești cunoscut printre ei.",
            "motiv": u"Ai legături cu otomanii (loialitate %d)." % loyalty_ottomans,
        }

    if loyalty_vlad >= PRAG_FACTIUNE and roll < 55:
        return {
            "eveniment": "vlad_salute",
            "text": u"Un soldat al lui Vlad te recunoaște și își duce pumnul la piept. Numele tău circulă la Curte.",
            "motiv": u"Ești în grațiile lui Vlad (loialitate %d)." % loyalty_vlad,
        }

    if loyalty_boyars >= PRAG_FACTIUNE and roll < 50:
        return {
            "eveniment": "boyar_whisper",
            "text": u"Un servitor îți strecoară în treacăt o șoaptă: «Boierii își amintesc cine le e prieten.»",
            "motiv": u"Boierii te consideră aliat (loialitate %d)." % loyalty_boyars,
        }

    if roll < 18:
        ambient = {
            "han": u"În han, cineva ridică paharul în tăcere către tine. Nu știi cine, nu știi de ce.",
            "padure": u"Pădurea foșnește mai tare ca de obicei. Pași? Vânt? Greu de spus.",
            "tabara_otomana": u"Fumul focurilor otomane se ridică drept în aerul rece. Tabăra e neobișnuit de tăcută.",
            "curtea_domneasca": u"De undeva din Curte se aude un țipăt scurt, apoi liniște. Justiția lui Vlad nu doarme.",
            "targoviste": u"Un copil aleargă pe lângă tine strigând că «vin țepele». Apoi dispare după colț.",
        }
        text = ambient.get(zona)
        if text:
            return {"eveniment": "ambient", "text": text, "motiv": u"Atmosferă de zonă."}

    return {"eveniment": "nimic", "text": u"", "motiv": u"Starea e neutră, nu se întâmplă nimic."}


# Replici scrise de mână, per facțiune. Se folosesc când modelul nu e disponibil,
# ca dialogul liber să rămână jucabil (chiar dacă evident mai sărac).
REPLICI_FALLBACK = {
    "order": [
        u"Nu e loc și nu e vreme de vorbe lungi. Spune-mi doar ce ai găsit.",
        u"Ordinul ascultă, dar Ordinul nu iartă greșelile. Fii scurt.",
    ],
    "vlad": [
        u"Vorbește limpede. Nu-mi plac oamenii care ocolesc.",
        u"Ai grijă ce ceri. Aici, cuvintele au preț de sânge.",
    ],
    "boyars": [
        u"Hm. Poate. Poate nu. Depinde cine întreabă și pentru cine.",
        u"Boierii au urechi lungi, agentule. Și memorie și mai lungă.",
    ],
    "ottomans": [
        u"Sultanul răsplătește răbdarea. Tu ai răbdare, agentule?",
        u"Vorbim, dar nu aici. Zidurile astea aud prea bine.",
    ],
}

REPLICA_IMPLICITA = u"Omul te măsoară din priviri și nu-ți răspunde. Nu e momentul potrivit."


def dialog_reply(faction, seed=0):
    """Replică de rezervă, aleasă determinist ca să fie reproductibilă în teste."""
    replici = REPLICI_FALLBACK.get(faction)
    if not replici:
        return REPLICA_IMPLICITA
    return replici[seed % len(replici)]
