#!/usr/bin/env python3
"""Schreibrechte der Kit-Agenten: nur das eigene Memory und das Laufprotokoll.

Die Agenten lesen fremde Dokumente — Belege, Mails, Portalseiten. Was darin steht, darf
nichts verändern können. Deshalb schreibt ein Agent des Kits genau zwei Orte:

  .claude/agent-memory/bookkeeping-kit-<agent>/          sein Memory
  .claude/bookkeeping-log/<zeitraum>/agents.md           sein Abschnitt im Laufprotokoll
  .claude/bookkeeping-eval/agents.md                     (Auswertungen über mehrere Läufe)

Erkannt wird ein Kit-Agent am Feld `agent_type` der Hook-Eingabe
(`bookkeeping-kit:<agent>`). Fehlt es, kommt der Aufruf aus dem Hauptkontext, und dieser
Hook lässt durch — dort gelten die übrigen Guards.

Bash wird für Kit-Agenten auf Lesen beschränkt: Umleitungen in Dateien, `tee`, `cp`, `mv`,
`rm`, `sed -i` und Verwandte sind gesperrt. Geschrieben wird mit Write/Edit, denn nur deren
Zielpfad ist hier zuverlässig prüfbar.
"""
import re, sys, os, pathlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kontext import eingabe, blockieren, durchlassen, projektwurzel

PLUGIN = "bookkeeping-kit"

SCHREIBEND = re.compile(
    r"(?:^|[\s;|&)])\d?>{1,2}\s*(?!&|/dev/null)[^\s&>]"    # > datei, >> datei, 2> datei
    r"|(?:^|[;&|(]|\s)\s*(tee|cp|mv|rm|rmdir|touch|mkdir|ln|install|rsync|truncate|"
    r"shred|unlink|chmod|chown)\s"
    r"|\bdd\b.*\bof="
    r"|\b(sed|perl|ruby)\b[^|;&]*\s-i"
    r"|\bopen\([^)]*['\"][wax]\+?b?['\"]"
    r"|\.write_(text|bytes)\(",
    re.I,
)

daten = eingabe()
typ = daten.get("agent_type") or ""
if not typ.startswith(PLUGIN + ":"):
    durchlassen()
name = typ.split(":", 1)[1]
tool = daten.get("tool_name", "")
ti = daten.get("tool_input") or {}
wurzel = projektwurzel(daten)


def erlaubt(pfad):
    p = pathlib.Path(pfad)
    if not p.is_absolute():
        p = pathlib.Path(daten.get("cwd") or os.getcwd()) / p
    p = pathlib.Path(os.path.normpath(p))
    c = wurzel / ".claude"
    if p.is_relative_to(c / "agent-memory" / f"{PLUGIN}-{name}"):
        return True
    if p.name == "agents.md" and (p.parent.parent == c / "bookkeeping-log"
                                  or p.parent == c / "bookkeeping-eval"):
        return True
    return False


if tool in ("Write", "Edit", "NotebookEdit"):
    ziel = ti.get("file_path") or ti.get("notebook_path") or ""
    if ziel and not erlaubt(ziel):
        blockieren(
            f"Blockiert: Der Agent {name} schreibt nur in sein Memory "
            f"(.claude/agent-memory/{PLUGIN}-{name}/) und in agents.md des Laufs, "
            f"nicht nach {ziel}.\n"
            f"Gib das Ergebnis im Bericht zurück; die aufrufende Skill schreibt es weg."
        )
elif tool == "Bash":
    cmd = ti.get("command", "") or ""
    if SCHREIBEND.search(cmd):
        blockieren(
            f"Blockiert: Der Agent {name} darf in Bash nur lesen. Schreiben geht über "
            f"Write/Edit und nur in das eigene Memory oder agents.md des Laufs.\n"
            f"Ausgaben, die du brauchst, liest du direkt von stdout."
        )

durchlassen()
