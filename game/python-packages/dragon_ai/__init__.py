# -*- coding: utf-8 -*-
"""Agenții AI ai jocului, ca Python pur (fără Ren'Py) — deci testabili cu pytest.

Doi agenți folosesc un model de limbaj mic, rulat local:

  * DialogueAgent  — NPC-urile răspund în caracter la text scris liber de jucător
                     și decid un efect asupra stării jocului.
  * ChroniclerAgent — la intrarea într-o zonă alege ce eveniment se întâmplă și
                     scrie narațiunea pe loc.

Amândoi trec prin același traseu: prompt -> model local -> validare strictă ->
fallback determinist. Dacă modelul e oprit, lent sau scoate gunoi, jocul merge
mai departe pe textele scrise de mână, fără nicio eroare vizibilă.
"""

from dragon_ai.config import AIConfig
from dragon_ai.client import LocalLLMClient
from dragon_ai.agents import ChroniclerAgent, DialogueAgent

__all__ = ["AIConfig", "LocalLLMClient", "ChroniclerAgent", "DialogueAgent"]
