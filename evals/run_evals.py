#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Evals pentru cei doi agenți AI ai jocului.

Testele din tests/ verifică logica cu un model fals. Astea rulează cazuri reale
prin modelul local și măsoară exact ce contează pentru joc:

  * rata de folosire a modelului  — de câte ori răspunsul a fost bun și nu s-a
                                    ajuns pe textele de rezervă;
  * potrivirea cu starea          — a ales agentul evenimentul/efectul pe care
                                    l-ar fi ales și un om, dată fiind starea?
  * rata de scurgere              — de câte ori NPC-ul a spus ce nu avea voie
                                    să știe (inclusiv la o injecție de prompt);
  * limba                         — modelele mici o iau uneori pe engleză;
  * latența p50 / p95             — dacă demo-ul rămâne jucabil.

Rulare:
    python3 evals/run_evals.py
    python3 evals/run_evals.py --model qwen2.5:1.5b-instruct --repetari 3
    python3 evals/run_evals.py --agent cronicar --compara qwen2.5:3b-instruct,qwen2.5:1.5b-instruct
"""

import argparse
import json
import os
import sys
import time

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RADACINA, "game", "python-packages"))

from dragon_ai import personas, schemas, validate                # noqa: E402
from dragon_ai.agents import ChroniclerAgent, DialogueAgent      # noqa: E402
from dragon_ai.client import LocalLLMClient                      # noqa: E402
from dragon_ai.config import AIConfig                            # noqa: E402

DIR_CAZURI = os.path.dirname(os.path.abspath(__file__))


def incarca(nume):
    cale = os.path.join(DIR_CAZURI, nume)
    with open(cale, encoding="utf-8") as f:
        return json.load(f)["cazuri"]


def procent(parte, total):
    return 0.0 if not total else round(100.0 * parte / total, 1)


def percentila(valori, p):
    if not valori:
        return 0.0
    ordonate = sorted(valori)
    idx = min(len(ordonate) - 1, int(round((p / 100.0) * (len(ordonate) - 1))))
    return round(ordonate[idx], 2)


# --- Cronicarul --------------------------------------------------------------

def ruleaza_cronicar(agent, cazuri, repetari):
    rezultate = []
    for caz in cazuri:
        for _ in range(repetari):
            inceput = time.time()
            iesire = agent.pick_event(caz["stare"], roll=50, evenimente_recente=[])
            durata = time.time() - inceput

            eveniment = iesire.get("eveniment")
            asteptat = caz.get("asteptat") or []
            interzis = caz.get("interzis_eveniment") or []

            rezultate.append({
                "caz": caz["id"],
                "din_model": iesire.get("sursa") == "model",
                "motiv_tehnic": iesire.get("motiv_tehnic"),
                "eveniment": eveniment,
                "potrivit": eveniment in asteptat if asteptat else None,
                "a_incalcat_lista": eveniment in interzis,
                "romana": validate.pare_romana(iesire.get("text") or u"") if iesire.get("text") else None,
                "latenta": durata,
                "text": iesire.get("text", u"")[:160],
            })
    return rezultate


# --- Agentul de dialog -------------------------------------------------------

def ruleaza_dialog(agent, cazuri, repetari):
    rezultate = []
    for caz in cazuri:
        persona = personas.get(caz["npc"])
        stare = dict(caz["stare"])
        stare.setdefault("player_name", "Mara")
        stare.setdefault("loialitati", {"Vlad": 0, "boieri": 0, "otomani": 0, "Ordin": 0})

        for _ in range(repetari):
            inceput = time.time()
            iesire = agent.respond(persona, stare, caz["intrebare"])
            durata = time.time() - inceput

            replica = iesire.get("replica") or u""
            joasa = replica.lower()

            # Un termen interzis care apare deja în întrebare nu se pune la
            # socoteală: „Nu știu cine a câștigat în 1998" e un refuz corect,
            # nu o scurgere. Contează doar ce afirmă NPC-ul de la el.
            intrebare_joasa = caz["intrebare"].lower()
            interzise = [
                c for c in (caz.get("interzis") or [])
                if c.lower() in joasa and c.lower() not in intrebare_joasa
            ]
            asteptat_efect = caz.get("asteptat_efect") or []

            rezultate.append({
                "caz": caz["id"],
                "din_model": iesire.get("sursa") == "model",
                "motiv_tehnic": iesire.get("motiv_tehnic"),
                "efect": iesire.get("efect"),
                "potrivit": iesire.get("efect") in asteptat_efect if asteptat_efect else None,
                "a_scurs": bool(interzise),
                "scurgeri": interzise,
                "romana": validate.pare_romana(replica),
                "latenta": durata,
                "text": replica[:160],
            })
    return rezultate


# --- Raport ------------------------------------------------------------------

def rezuma(nume_agent, model, rezultate):
    total = len(rezultate)
    din_model = [r for r in rezultate if r["din_model"]]
    evaluabile = [r for r in rezultate if r["potrivit"] is not None]
    de_limba = [r for r in rezultate if r["romana"] is not None]
    latente = [r["latenta"] for r in rezultate]

    rezumat = {
        "agent": nume_agent,
        "model": model,
        "cazuri": total,
        "rata_model_%": procent(len(din_model), total),
        "rata_fallback_%": procent(total - len(din_model), total),
        "potrivire_stare_%": procent(len([r for r in evaluabile if r["potrivit"]]), len(evaluabile)),
        "romana_%": procent(len([r for r in de_limba if r["romana"]]), len(de_limba)),
        "latenta_p50_s": percentila(latente, 50),
        "latenta_p95_s": percentila(latente, 95),
    }

    if any("a_scurs" in r for r in rezultate):
        rezumat["scurgeri_%"] = procent(len([r for r in rezultate if r.get("a_scurs")]), total)
    if any("a_incalcat_lista" in r for r in rezultate):
        rezumat["incalcari_lista_alba_%"] = procent(
            len([r for r in rezultate if r.get("a_incalcat_lista")]), total)

    return rezumat


def tabel_markdown(rezumate):
    coloane = ["agent", "model", "cazuri", "rata_model_%", "rata_fallback_%",
               "potrivire_stare_%", "romana_%", "scurgeri_%",
               "incalcari_lista_alba_%", "latenta_p50_s", "latenta_p95_s"]
    coloane = [c for c in coloane if any(c in r for r in rezumate)]

    linii = ["| " + " | ".join(coloane) + " |",
             "|" + "|".join(["---"] * len(coloane)) + "|"]
    for r in rezumate:
        linii.append("| " + " | ".join(str(r.get(c, "—")) for c in coloane) + " |")
    return "\n".join(linii)


def main():
    ap = argparse.ArgumentParser(description="Evals pentru agenții AI ai jocului.")
    ap.add_argument("--model", default="qwen2.5:3b-instruct")
    ap.add_argument("--compara", default=None,
                    help="listă de modele separate prin virgulă, rulate pe rând")
    ap.add_argument("--agent", choices=["cronicar", "dialog", "ambii"], default="ambii")
    ap.add_argument("--repetari", type=int, default=1,
                    help="de câte ori se rulează fiecare caz (modelele sunt nedeterministe)")
    ap.add_argument("--url", default="http://127.0.0.1:11434")
    ap.add_argument("--iesire", default=os.path.join(DIR_CAZURI, "results"))
    args = ap.parse_args()

    modele = [m.strip() for m in (args.compara or args.model).split(",") if m.strip()]

    rezumate = []
    detalii = []

    for model in modele:
        config = AIConfig(base_url=args.url, model=model, chronicler_model=model,
                          dialog_timeout=90.0, chronicler_timeout=90.0)
        client = LocalLLMClient(config)

        if not client.is_available():
            print("!! Modelul %s nu e disponibil la %s. Rulează scripts/setup_ai.sh." % (model, args.url))
            return 1

        print("== %s: încălzire..." % model)
        client.warmup()

        if args.agent in ("cronicar", "ambii"):
            print("-- Cronicarul...")
            rez = ruleaza_cronicar(ChroniclerAgent(client, config),
                                   incarca("cases_cronicar.json"), args.repetari)
            rezumate.append(rezuma("cronicar", model, rez))
            detalii.extend([dict(r, agent="cronicar", model=model) for r in rez])

        if args.agent in ("dialog", "ambii"):
            print("-- Dialogul liber...")
            rez = ruleaza_dialog(DialogueAgent(client, config),
                                 incarca("cases_dialog.json"), args.repetari)
            rezumate.append(rezuma("dialog", model, rez))
            detalii.extend([dict(r, agent="dialog", model=model) for r in rez])

    print()
    print(tabel_markdown(rezumate))
    print()

    if not os.path.isdir(args.iesire):
        os.makedirs(args.iesire)
    marca = time.strftime("%Y%m%d-%H%M%S")
    cale = os.path.join(args.iesire, "evals-%s.json" % marca)
    with open(cale, "w", encoding="utf-8") as f:
        json.dump({"rezumate": rezumate, "detalii": detalii}, f, ensure_ascii=False, indent=2)
    print("Detalii complete: %s" % cale)

    cale_md = os.path.join(args.iesire, "ultimul-raport.md")
    with open(cale_md, "w", encoding="utf-8") as f:
        f.write("# Evals agenți AI — %s\n\n" % marca)
        f.write(tabel_markdown(rezumate) + "\n")
    print("Tabel pentru README: %s" % cale_md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
