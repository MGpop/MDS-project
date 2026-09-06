# -*- coding: utf-8 -*-
"""Client pentru modelul de limbaj local (Ollama).

Doar stdlib: urllib + json + threading. Fără dependențe de instalat, ca jocul să
ruleze pe orice laptop din echipă exact ca aici.
"""

import json
import os
import threading
import time

try:                                  # Python 3
    from urllib.request import Request, urlopen
    from urllib.error import URLError
except ImportError:                   # pragma: no cover - Ren'Py e pe Python 3
    from urllib2 import Request, urlopen, URLError


class LLMResult(object):
    """Ce s-a întâmplat la un apel — și, mai ales, de ce a eșuat dacă a eșuat."""

    def __init__(self, text=None, error=None, latency=0.0, model=None):
        self.text = text
        self.error = error
        self.latency = latency
        self.model = model

    @property
    def ok(self):
        return self.text is not None and self.error is None

    def __repr__(self):
        return "<LLMResult ok=%s latency=%.2fs error=%r>" % (self.ok, self.latency, self.error)


class LocalLLMClient(object):
    """Vorbește cu Ollama pe localhost. Nu aruncă niciodată — întoarce LLMResult."""

    def __init__(self, config, log_path=None):
        self.config = config
        self.log_path = log_path or config.log_path
        self._lock = threading.Lock()
        self._health = None          # None = încă neverificat
        self._health_checked_at = 0.0

    # --- disponibilitate ------------------------------------------------------

    def is_available(self, force=False):
        """Răspunde repede la 'există un model local acum?'.

        Rezultatul e memorat câteva secunde, ca să nu punem un round-trip în plus
        înaintea fiecărei replici de dialog.
        """
        if not self.config.enabled:
            return False

        acum = time.time()
        with self._lock:
            proaspat = (acum - self._health_checked_at) < self.config.health_ttl
            if self._health is not None and proaspat and not force:
                return self._health

        stare = self._check_health()

        with self._lock:
            self._health = stare
            self._health_checked_at = time.time()
        return stare

    def _check_health(self):
        try:
            cerere = Request(self.config.base_url + "/api/tags", method="GET")
            raspuns = urlopen(cerere, timeout=self.config.health_timeout)
            date = json.loads(raspuns.read().decode("utf-8"))
        except Exception:
            return False

        modele = [m.get("name", "") for m in date.get("models", [])]
        if not modele:
            return False

        # Ollama raportează "qwen2.5:3b-instruct"; acceptăm și potrivirea pe prefix,
        # ca un ":latest" sau un tag de cuantizare să nu strice detecția.
        dorit = self.config.model
        return any(m == dorit or m.startswith(dorit.split(":")[0]) for m in modele)

    # --- apelul propriu-zis ---------------------------------------------------

    def chat_json(self, system, user, timeout, agent="necunoscut", max_tokens=None, temperature=None, model=None):
        """Cere modelului un răspuns în JSON. Întoarce LLMResult, nu aruncă."""
        if not self.config.enabled:
            return LLMResult(error="agenții AI sunt opriți din configurație")

        model = model or self.config.model
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
            "format": "json",          # Ollama forțează ieșire JSON validă
            # Ține modelul în RAM între apeluri. Fără asta, Ollama îl descarcă după
            # 5 minute, iar prima replică de după o pauză ar dura zeci de secunde
            # — exact ce nu vrei în mijlocul unei prezentări.
            "keep_alive": "45m",
            "options": {
                "temperature": self.config.temperature if temperature is None else temperature,
                "num_predict": self.config.max_tokens if max_tokens is None else max_tokens,
                "top_p": 0.9,
            },
        }

        inceput = time.time()
        try:
            cerere = Request(
                self.config.base_url + "/api/chat",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            raspuns = urlopen(cerere, timeout=timeout)
            date = json.loads(raspuns.read().decode("utf-8"))
            text = date.get("message", {}).get("content", "")
            rezultat = LLMResult(text=text, latency=time.time() - inceput, model=model)
        except URLError as exc:
            rezultat = LLMResult(error="modelul local nu răspunde (%s)" % exc, latency=time.time() - inceput)
        except Exception as exc:
            rezultat = LLMResult(error="%s: %s" % (type(exc).__name__, exc), latency=time.time() - inceput)

        if not rezultat.ok:
            # Un apel căzut poate însemna că Ollama tocmai a fost oprit.
            with self._lock:
                self._health = None

        rezultat.model = rezultat.model or model
        self._log(agent, system, user, rezultat)
        return rezultat

    def warmup(self, timeout=90.0, model=None):
        """Încarcă modelul în RAM înainte să aibă cineva nevoie de el.

        Primul apel după pornirea calculatorului ține zeci de secunde, pentru că
        Ollama citește ~2GB de pe disc. Chemat în fundal la pornirea jocului,
        face ca prima replică din joc să vină la fel de repede ca restul.
        """
        if not self.config.enabled:
            return False
        payload = {
            "model": model or self.config.model,
            "messages": [{"role": "user", "content": "salut"}],
            "stream": False,
            "keep_alive": "45m",
            "options": {"num_predict": 1},
        }
        try:
            cerere = Request(
                self.config.base_url + "/api/chat",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            urlopen(cerere, timeout=timeout).read()
            return True
        except Exception:
            return False

    # --- jurnal ---------------------------------------------------------------

    def _log(self, agent, system, user, rezultat):
        """Scrie fiecare apel în JSONL: materie primă pentru evals și pentru raportul AI."""
        if not self.log_path:
            return
        try:
            director = os.path.dirname(self.log_path)
            if director and not os.path.isdir(director):
                os.makedirs(director)
            intrare = {
                "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "agent": agent,
                "model": rezultat.model or self.config.model,
                "latency_ms": int(rezultat.latency * 1000),
                "ok": rezultat.ok,
                "error": rezultat.error,
                "prompt_user": user[:600],
                "raw": (rezultat.text or "")[:600],
            }
            with open(self.log_path, "a") as f:
                f.write(json.dumps(intrare, ensure_ascii=False) + "\n")
        except Exception:
            pass   # jurnalul nu are voie să strice jocul


class FakeLLMClient(object):
    """Client fals pentru teste și evals: întoarce răspunsuri dinainte stabilite."""

    def __init__(self, raspunsuri=None, disponibil=True, latency=0.0):
        self.raspunsuri = list(raspunsuri or [])
        self.disponibil = disponibil
        self.latency = latency
        self.apeluri = []

    def is_available(self, force=False):
        return self.disponibil

    def warmup(self, timeout=90.0, model=None):
        return self.disponibil

    def chat_json(self, system, user, timeout, agent="necunoscut", max_tokens=None, temperature=None, model=None):
        self.apeluri.append({"system": system, "user": user, "agent": agent})
        if not self.disponibil:
            return LLMResult(error="model indisponibil (fals)")
        if not self.raspunsuri:
            return LLMResult(error="nu mai sunt răspunsuri pregătite (fals)")
        urmatorul = self.raspunsuri.pop(0)
        if isinstance(urmatorul, Exception):
            return LLMResult(error=str(urmatorul))
        return LLMResult(text=urmatorul, latency=self.latency, model="fals")
