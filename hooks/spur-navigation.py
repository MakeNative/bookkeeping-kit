#!/usr/bin/env python3
"""Navigationsspur für die nachträgliche Prüfung.

Weil der Klick auf „Übermitteln" nicht blockierbar ist (siehe guard-uebermittlung.py),
muss wenigstens **nachweisbar** sein, wo gearbeitet wurde. Diese Spur liest der
monthly-auditor in Prüfung 6.

Der Hook schreibt nur und blockiert nie. Er darf unter keinen Umständen einen Lauf
aufhalten — deshalb fängt er jeden Fehler ab und endet still.
"""
import json, sys, os, datetime, pathlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kontext import eingabe, projektwurzel

try:
    daten = eingabe()
    ti = daten.get("tool_input") or {}
    url = ti.get("url") or ti.get("uri")
    if url:
        ziel = projektwurzel(daten) / ".claude" / "bookkeeping-log"
        ziel.mkdir(parents=True, exist_ok=True)
        zeile = {
            "zeit": datetime.datetime.now().isoformat(timespec="seconds"),
            "tool": daten.get("tool_name"),
            "url": url,
        }
        with open(ziel / "navigation.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(zeile, ensure_ascii=False) + "\n")
except Exception:
    pass

sys.exit(0)
