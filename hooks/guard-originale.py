#!/usr/bin/env python3
"""P-03 und P-05: Originalbelege werden nicht gelöscht und nicht verändert.

Greift bei Bash, Write, Edit und NotebookEdit. Geprüft wird gegen die Belegordner aus
dem Mandanten-Context — ohne Context gibt es keine geschützten Pfade.

Grenze dieses Hooks: Er sieht die Eingabe des Tools, nicht dessen Wirkung. Ein
Löschvorgang in der Oberfläche des Buchhaltungssystems geht über Bildkoordinaten und ist
hier **nicht** sichtbar. Das deckt die nachträgliche Prüfung im Audit ab, nicht dieser
Hook; siehe hooks/README.md.
"""
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kontext import eingabe, blockieren, durchlassen, belegordner, betrifft

ZERSTOEREND = re.compile(
    r"(?:^|[;&|]|\s)\s*(rm|rmdir|shred|unlink|srm|trash)\s+(?!-h|--help)"
    r"|(?:^|[;&|]|\s)\s*(mv|rename)\s+"
    r"|\btruncate\b|\bdd\b.*\bof=",
    re.I,
)

daten = eingabe()
tool = daten.get("tool_name", "")
ti = daten.get("tool_input") or {}
ordner = belegordner(daten)
if not ordner:
    durchlassen()

if tool == "Bash":
    cmd = ti.get("command", "") or ""
    o = betrifft(cmd, ordner)
    if o and ZERSTOEREND.search(cmd):
        blockieren(
            f"Blockiert (P-03/P-05): Das Kommando verändert oder entfernt Dateien im "
            f"Belegordner {o}.\n"
            f"Originalbelege bleiben unverändert — auch Umbenennen zählt dazu. "
            f"Lege stattdessen eine Kopie an oder vermerke die Zuordnung in einer "
            f"Mappingdatei.\n"
            f"Ist das Löschen wirklich gewollt, muss es der Mensch selbst tun."
        )

elif tool in ("Write", "Edit", "NotebookEdit"):
    ziel = ti.get("file_path") or ti.get("notebook_path") or ""
    o = betrifft(ziel, ordner)
    if o:
        blockieren(
            f"Blockiert (P-05): Schreibzugriff auf {ziel} im Belegordner {o}.\n"
            f"Belege sind Originale und werden nicht überschrieben. Laufergebnisse "
            f"gehören nach .claude/bookkeeping-log/."
        )

durchlassen()
