#!/usr/bin/env python3
"""Gemeinsame Helfer der Hooks.

Hooks laufen vor jedem einzelnen Tool-Aufruf. Sie müssen deshalb billig sein, dürfen
nicht blockieren und müssen im Zweifel **durchlassen** statt zu raten: Ein Hook, der
berechtigte Arbeit verhindert, wird abgeschaltet — und dann schützt er gar nichts mehr.
"""
import json, os, re, sys, pathlib

CONTEXT = ".claude/docs/COMPANY_CONTEXT.md"


def eingabe():
    """Hook-Eingabe von stdin. Bei Unlesbarkeit leeres Dict -> der Hook lässt durch."""
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def blockieren(grund):
    """Exit 2 blockiert den Tool-Aufruf; stderr geht an das Modell zurück."""
    print(grund, file=sys.stderr)
    sys.exit(2)


def durchlassen():
    sys.exit(0)


def projektwurzel(daten):
    """Das Mandantenprojekt, auch wenn das Arbeitsverzeichnis darunter liegt.

    `cwd` folgt jedem `cd` der Sitzung. Steht es im Laufordner, läge der Context sonst
    „nicht da", und jeder Guard ließe alles durch. Deshalb nach oben suchen, dann
    `CLAUDE_PROJECT_DIR` versuchen, zuletzt `cwd` selbst nehmen.
    """
    start = pathlib.Path(daten.get("cwd") or os.getcwd())
    for d in (start, *start.parents):
        if (d / CONTEXT).is_file():
            return d
    projekt = os.environ.get("CLAUDE_PROJECT_DIR")
    if projekt and (pathlib.Path(projekt) / CONTEXT).is_file():
        return pathlib.Path(projekt)
    return start


def belegordner(daten):
    """Liest die Belegpfade aus dem Mandanten-Context.

    Ohne Context gibt es keine geschützten Pfade — das Kit ist dann noch nicht
    eingerichtet, und es gibt nichts zu schützen.
    """
    pfad = projektwurzel(daten) / CONTEXT
    try:
        text = pfad.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []
    out = []
    for key in ("eingangsrechnungen", "ausgangsrechnungen"):
        m = re.search(rf"^\s*{key}:\s*(\S.*?)\s*$", text, re.M)
        if not m:
            continue
        wert = m.group(1).split("#")[0].strip().strip("\"'")
        if not wert:
            continue
        # <JJJJ> und ähnliche Platzhalter: nur der Teil davor ist verlässlich
        stamm = re.split(r"<[^>]+>", wert)[0].rstrip("/")
        if stamm:
            out.append(os.path.expanduser(stamm))
    return out


def betrifft(pfadtext, ordner):
    """Berührt ein Kommando oder ein Dateipfad einen geschützten Ordner?"""
    if not pfadtext:
        return None
    for o in ordner:
        if o and o in pfadtext:
            return o
    return None
