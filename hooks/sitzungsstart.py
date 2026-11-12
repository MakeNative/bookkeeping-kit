#!/usr/bin/env python3
"""Sitzungsstart: meldet den Einrichtungsstand und die Regelwerksversion.

Zweck ist die **Versionsdrift**: Das Regelwerk liegt im Plugin und wird aktualisiert, der
Mandanten-Context nennt die Version, gegen die zuletzt gerechnet wurde. Laufen die
auseinander, ändern sich Ergebnisse ohne erkennbaren Anlass. Das soll am Anfang auffallen,
nicht im Abgleich.

Der Hook informiert nur. Er blockiert nichts.
"""
import re, sys, os, pathlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kontext import eingabe, projektwurzel, CONTEXT


def version(text):
    m = re.search(r"REGELWERK_VERSION:\s*(\S+)", text)
    return m.group(1) if m else None


daten = eingabe()
wurzel = projektwurzel(daten)
ctx = wurzel / CONTEXT

if not ctx.exists():
    # Kein Mandanten-Context: nur melden, wenn hier überhaupt gebucht wird.
    if (wurzel / ".claude" / "bookkeeping-log").exists():
        print("bookkeeping-kit: COMPANY_CONTEXT.md fehlt — zuerst /bookkeeping-kit:adopt.")
    sys.exit(0)

text = ctx.read_text(encoding="utf-8", errors="replace")
v_mandant = version(text)

plugin = pathlib.Path(os.environ.get("CLAUDE_PLUGIN_ROOT", "")) / "docs" / "REGELWERK.md"
v_plugin = None
if plugin.exists():
    kopf = plugin.read_text(encoding="utf-8", errors="replace")
    v_plugin = version(kopf)
    if not v_plugin:
        zeilen = re.findall(r"^\|\s*(\d+)\s*\|", kopf, re.M)
        v_plugin = zeilen[-1] if zeilen else None

if v_mandant and v_plugin and v_mandant != v_plugin:
    print(
        f"bookkeeping-kit: Regelwerk im Plugin ist Version {v_plugin}, der Mandant "
        f"rechnete zuletzt gegen {v_mandant}. Vor dem nächsten Lauf die Änderungshistorie "
        f"prüfen — geänderte Regeln wirken nur ab ihrem gilt_ab."
    )

sys.exit(0)
