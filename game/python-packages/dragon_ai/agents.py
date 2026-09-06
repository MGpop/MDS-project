# -*- coding: utf-8 -*-
"""
aceeasi structura
prompt -> model local -> validare stricta -> fallback determinist
rezultatul spune intotdeauna de unde vine ("sursa": "model" sau "fallback") si
de ce, ca panoul de debug din joc sa poata arata rationamentul agentului.
"""

from dragon_ai import fallbacks, prompts, schemas, validate


class AgentResult(dict):
    @property
    def din_model(self):
        return self.get("sursa") == "model"


def _rezultat(date, sursa, motiv_tehnic, latenta=0.0, raw=None):
    rez = AgentResult(date)
    rez["sursa"] = sursa
    rez["motiv_tehnic"] = motiv_tehnic
    rez["latenta"] = latenta
    rez["raw"] = (raw or u"")[:600]
    return rez


class ChroniclerAgent(object):

    nume = u"Cronicarul"

    def __init__(self, client, config):
        self.client = client
        self.config = config

    def pick_event(self, stare, roll, evenimente_recente=None, poate_lupta=True):
        zona = stare.get("zona")
        permise = schemas.evenimente_permise(zona, poate_lupta=poate_lupta)

        rezerva = fallbacks.chronicler_event(
            zona,
            stare.get("loialitati", {}).get(u"Vlad", 0),
            stare.get("loialitati", {}).get(u"boieri", 0),
            stare.get("loialitati", {}).get(u"otomani", 0),
            stare.get("suspiciune", 0),
            stare.get("capitol", 1),
            roll,
        )

        if not self.client.is_available():
            return _rezultat(rezerva, "fallback", u"modelul local nu e pornit")

        raspuns = self.client.chat_json(
            system=prompts.SISTEM_CRONICAR,
            user=prompts.build_chronicler_user(stare, permise, evenimente_recente),
            timeout=self.config.chronicler_timeout,
            agent="cronicar",
            max_tokens=160,
            model=self.config.chronicler_model,
        )

        if not raspuns.ok:
            return _rezultat(rezerva, "fallback", raspuns.error or u"apel eșuat", raspuns.latency)

        validat = validate.validate_chronicler(raspuns.text, permise)
        if validat is None:
            return _rezultat(
                rezerva, "fallback",
                u"răspuns invalid (JSON stricat sau eveniment nepermis)",
                raspuns.latency, raspuns.text,
            )

        if validat["eveniment"] == "nimic" and not validat["text"]:
            validat["motiv"] = validat["motiv"] or u"Agentul a decis că nu se întâmplă nimic."

        return _rezultat(validat, "model", u"răspuns valid", raspuns.latency, raspuns.text)


class DialogueAgent(object):

    nume = u"Dialog liber"

    def __init__(self, client, config):
        self.client = client
        self.config = config

    def respond(self, persona, stare, intrebare, istoric=None, efecte_permise=None):
        rezerva = {
            "replica": fallbacks.dialog_reply(persona.get("factiune"), len(istoric or [])),
            "efect": schemas.EFECT_NIMIC,
            "motiv": u"Replică de rezervă, fără model.",
        }

        intrebare = (intrebare or u"").strip()
        if not intrebare:
            return _rezultat(rezerva, "fallback", u"întrebare goală")

        if not self.client.is_available():
            return _rezultat(rezerva, "fallback", u"modelul local nu e pornit")

        raspuns = self.client.chat_json(
            system=prompts.build_dialog_system(persona),
            user=prompts.build_dialog_user(stare, intrebare, istoric),
            timeout=self.config.dialog_timeout,
            agent="dialog",
            max_tokens=130,
        )

        if not raspuns.ok:
            return _rezultat(rezerva, "fallback", raspuns.error or u"apel eșuat", raspuns.latency)

        validat = validate.validate_dialog(raspuns.text, efecte_permise)
        if validat is None:
            return _rezultat(
                rezerva, "fallback", u"răspuns invalid (JSON stricat sau fără replică)",
                raspuns.latency, raspuns.text,
            )

        return _rezultat(validat, "model", u"răspuns valid", raspuns.latency, raspuns.text)
