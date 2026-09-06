# -*- coding: utf-8 -*-
"""Configurația agenților AI."""

import os


# Modele mici testate cu jocul. Primul e implicit; al doilea e varianta rapidă
# pentru laptopuri fără GPU, cu prețul unei române mai șchioape.
MODELE_SUGERATE = [
    "qwen2.5:3b-instruct",
    "qwen2.5:1.5b-instruct",
]


class AIConfig(object):
    """Unde stă modelul local și cât are voie să ne facă să așteptăm.

    Timeout-urile sunt calibrate pe latențele măsurate în evals, nu ghicite:
    prea mici înseamnă fallback-uri degeaba, prea mari înseamnă un joc care pare
    blocat. Vezi evals/results/ pentru cifre.
    """

    def __init__(
        self,
        base_url="http://127.0.0.1:11434",
        model=MODELE_SUGERATE[0],
        chronicler_model=None,
        enabled=True,
        # Calibrate pe măsurători reale (evals/results): pe CPU, fără GPU,
        # cronicarul are p95 ~12s și dialogul ~8s cu qwen2.5:3b-instruct.
        # Timeout-urile stau confortabil peste, altfel am cădea pe fallback
        # tocmai când modelul chiar răspundea.
        dialog_timeout=25.0,
        chronicler_timeout=25.0,
        health_timeout=1.5,
        health_ttl=20.0,
        temperature=0.8,
        max_tokens=120,
        log_path=None,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        # Cronicarul intră în funcțiune la fiecare schimbare de zonă, deci contează
        # mai mult viteza decât finețea limbii; dialogul e invers. De aceea pot
        # rula pe modele diferite.
        self.chronicler_model = chronicler_model or model
        self.enabled = enabled
        self.dialog_timeout = dialog_timeout
        self.chronicler_timeout = chronicler_timeout
        self.health_timeout = health_timeout
        self.health_ttl = health_ttl
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.log_path = log_path

    @classmethod
    def from_env(cls, **overrides):
        """Config din variabile de mediu — folosit de evals și de CI."""
        kwargs = {
            "base_url": os.environ.get("DRAGON_AI_URL", "http://127.0.0.1:11434"),
            "model": os.environ.get("DRAGON_AI_MODEL", MODELE_SUGERATE[0]),
            "chronicler_model": os.environ.get("DRAGON_AI_MODEL_CRONICAR") or None,
            "enabled": os.environ.get("DRAGON_AI_ENABLED", "1") != "0",
        }
        kwargs.update(overrides)
        return cls(**kwargs)

    def copy_with(self, **overrides):
        valori = dict(
            base_url=self.base_url,
            model=self.model,
            chronicler_model=self.chronicler_model,
            enabled=self.enabled,
            dialog_timeout=self.dialog_timeout,
            chronicler_timeout=self.chronicler_timeout,
            health_timeout=self.health_timeout,
            health_ttl=self.health_ttl,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            log_path=self.log_path,
        )
        valori.update(overrides)
        return AIConfig(**valori)
