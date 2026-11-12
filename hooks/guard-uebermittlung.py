#!/usr/bin/env python3
"""P-01: Keine Übermittlung an die Finanzverwaltung.

Greift bei der Browser-Navigation, denn dort steht die Ziel-URL in der Tool-Eingabe und
ist damit prüfbar.

Was dieser Hook **nicht** kann: Ein Klick auf „Übermitteln" läuft über Bildkoordinaten.
Die Tool-Eingabe enthält dann nur x und y — keine URL, keinen Beschriftungstext, nichts
Prüfbares. Dieser Hook ist deshalb eine Schranke an der Tür, kein Schloss am Knopf.
Die eigentliche Absicherung ist die Anweisung in den Skills plus die nachträgliche
Prüfung durch den monthly-auditor.
"""
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kontext import eingabe, blockieren, durchlassen

# Portale der Finanzverwaltung — dort gibt es nichts zu lesen, was das Kit braucht.
PORTAL = re.compile(r"\belster(?:online)?\.de\b|\bfinanzamt\.de\b", re.I)

# Eine Aktion als eigenes Pfadsegment ...
AKTION = re.compile(
    r"/(?:senden|uebermitteln|übermitteln|abgeben|freigeben|submit|transmit|efile|file)"
    r"(?:[/?#]|$)", re.I)

# ... zählt nur im steuerlichen Zusammenhang. Sonst träfe sie jedes Formular.
STEUERKONTEXT = re.compile(
    r"ustva|umsatzsteuer|voranmeldung|steuererkl|vat[-_/]?return|tax[-_/]?return", re.I)


def gesperrt(url):
    if PORTAL.search(url):
        return "Portal der Finanzverwaltung"
    if AKTION.search(url) and STEUERKONTEXT.search(url):
        return "Übermittlungsaktion einer Steuermeldung"
    return None


daten = eingabe()
ti = daten.get("tool_input") or {}
url = ti.get("url") or ti.get("uri") or ""

if url and (grund := gesperrt(url)):
    blockieren(
        f"Blockiert (P-01): {url}\n{grund}.\n"
        f"Die Übermittlung der Voranmeldung ist allein Sache des Menschen. Das Kit "
        f"bereitet vor, rechnet nach und legt vor — es meldet nicht.\n"
        f"Lege das Ergebnis vor und halte an."
    )

durchlassen()
