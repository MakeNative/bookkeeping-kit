---
name: collect
description: "Stellt für einen Zeitraum zusammen, welche Belege es geben müsste und welche davon vorliegen — aus Belegordner, Postfächern, Anbieterportalen und Zahlungsmeldungen. Erzeugt die Soll-Liste und fordert nötige Logins gebündelt an. Triggers on: /buchhaltung-kit:collect <YYYY-MM>"
disable-model-invocation: true
---

Du stellst die **Soll-Liste** eines Zeitraums auf: was es geben müsste, was vorliegt, was
fehlt und warum.

Diese Skill läuft im Hauptkontext, weil Portale Logins brauchen und ein Subagent dich nicht
fragen kann. Die datenintensiven Teile — Ordner durchsehen, Postfächer durchsuchen — lagerst
du aus, indem du den `receipt-reader` einsetzt oder Suchen bündelst.

## Grundsatz

Die Erwartung speist sich aus **Zahlungen und bekannten Lieferanten**, nicht aus dem
Ordnerinhalt (Regel P-06). Ein Ordner zeigt nur, was zufällig abgelegt wurde.

## Schritt 1 — Erwartung aufbauen

Drei Quellen:

1. **Zahlungsmeldungen** des Zeitraums aus den Postfächern laut Context (Bank, Karte,
   Zahlungsdienste). Je Zahlung: Datum, Empfänger, Betrag, Währung.
2. **Wiederkehrende Lieferanten** aus `COMPANY_CONTEXT.md`, auch ohne Zahlungsmeldung —
   manche rechnen per Sammellastschrift oder Guthaben ab (Muster M-09).
3. **Ausgangsrechnungen** aus dem Ausgangsordner und dem Buchhaltungssystem.

Ruft `match-receipts` dich auf, ist die Erwartung vorgegeben: die Kontoumsätze mit Status
`beleg_fehlt` aus `70-umsaetze.jsonl`. Dann nur diese, ohne Lieferantenliste und
Ausgangsseite, und je Eintrag die `umsatz_id` mitführen.

Beachte dabei:
- Guthabenaufladungen sind **keine** Belege (E-11) — sie erzeugen keine Erwartung auf einen
  Beleg in gleicher Höhe, sondern den Hinweis auf eine spätere periodische Rechnung.
- Lieferanten mit Muster M-08 rechnen verspätet ab → Status `noch_nicht_ausgestellt` (E-12).
- Ausschlussliste anwenden (E-13): Fremdbelege erzeugen keine Erwartung.

## Schritt 2 — Bezugsweg je erwartetem Beleg

Jede Erwartung braucht einen Weg, auf dem der Beleg zu holen ist — **bevor** gesammelt wird.
Ein Lieferant ohne bekannten Weg ist kein Beleg, der „fehlt", sondern einer, dessen Weg du
noch nicht kennst.

1. **Lieferant im Context** → `beleg_quelle` und `portal` übernehmen.
2. **Lieferant neu oder ohne `portal`** → Weg ermitteln:
   - Zahlungsempfänger normalisieren: Präfixe der Zahlungsabwickler abschneiden
     (`LINK.COM*`, `PAYPAL *`, `GOOGLE *`, `SumUp *`, `*STORE`) und den eigentlichen Händler
     nehmen. Läuft die Zahlung über einen Zahlungsdienst (PayPal, Stripe Link), steht der
     Händler in dessen Zahlungsbeleg im Postfach.
   - Absender des Händlers im Postfach suchen (beliebige Mail, nicht nur Rechnungen). Links
     auf Konto, Billing oder Rechnungen in diesen Mails sind der Portalweg.
   - Sonst die Abrechnungsseite des Anbieters öffnen (Konto → Billing/Abrechnung/Rechnungen).
   - Ladengeschäft, Gastronomie, Veranstaltung ohne Konto → `bezugsweg: papier`; dann kann
     nur der Mensch den Beleg liefern. Das ist ein eigener Status, kein `fehlt`.
3. Ermittelte Wege **sofort in den Context zurückschreiben** (`beleg_quelle`, `portal`,
   `login`). Der nächste Lauf darf dieselbe Suche nicht noch einmal brauchen.

Mail allein ist kein Weg, sondern ein Versuch: Auch bei `beleg_quelle: Mail` gehört ein
`portal` in den Context, für den Monat, in dem die Mail ausbleibt oder an eine andere
Adresse ging.

## Schritt 3 — Login-Check **vor** dem Sammeln

Öffne alle Portale aus Schritt 2, die für die Belege dieses Zeitraums gebraucht werden —
auch die neu ermittelten —, und klassifiziere jedes:

| Status | Erkennung |
|---|---|
| `session_ok` | Zielseite lädt mit Inhalt |
| `login_noetig` | Weiterleitung auf eine Anmeldemaske |
| `domain_gesperrt` | Navigation wird von der Browser-Erweiterung abgelehnt |

Die dritte Lage ist **kein** Login-Problem — sie braucht eine Freigabe in den
Erweiterungseinstellungen. Verwechsle das nicht, sonst schickst du den Nutzer auf die falsche
Fährte.

Schreibe `05-login-bedarf.md` und lege **alle betroffenen Tabs gleichzeitig offen**. Dann
eine einzige Anforderung an den Nutzer, nicht fünf nacheinander:

```
Portal      Status            Betrifft                 Tab
<name>      login_noetig      <n> Rechnungen, ~<x> €   offen
<name>      domain_gesperrt   <n> Rechnungen           Freigabe nötig
```

**Begleiteter Lauf:** warte, prüfe nach der Rückmeldung erneut, mach weiter.
**Unbeaufsichtigter Lauf:** warte nicht. Hol alles Erreichbare, markiere den Rest als
`portal_login_noetig` und trage ihn ins Offene-Punkte-Register ein.

Gib niemals Zugangsdaten ein (P-02).

## Schritt 4 — Belege zusammentragen

In dieser Reihenfolge, weil jede Stufe billiger ist als die nächste. Gesucht wird **je
erwartetem Beleg**, nicht einmal pauschal für den Zeitraum:

1. **Belegordner** — was schon da ist
2. **Buchhaltungssystem** — Belege, die dort schon liegen, auch unter „zu prüfen"
3. **Postfächer** — siehe unten
4. **Portale** — jeder Beleg, der nach Stufe 1–3 noch fehlt, über den Weg aus Schritt 2

### Postfachsuche

Eine Sammelsuche nach „Rechnung OR invoice" mit Anhang findet nur einen Teil: Viele Anbieter
schicken die Rechnung als HTML-Mail oder als Link, und eine Trefferseite ist nach 50 Treffern
zu Ende.

- Je Beleg suchen: Händlername **und** Absenderdomain, Zeitfenster Zahlungsdatum −10 bis
  +3 Tage, wahlweise der Betrag (`"99,00" OR "99.00"`).
- **Nicht** auf `has:attachment` einschränken. Eine HTML-Rechnung oder Bestellbestätigung mit
  Pflichtangaben ist ein Beleg; eine Mail mit Download-Link führt zum Beleg.
- Alle Empfängeradressen aus dem Context abdecken (`mail.konten[].empfaengt`). Ein verbundenes
  Postfach empfängt oft mehrere Adressen und Weiterleitungen — dass eine Adresse nicht als
  eigenes Konto verbunden ist, heißt nicht, dass ihre Mails fehlen.
- Treffer seitenweise abarbeiten, bis keine Folgeseite mehr kommt.

### Wann `fehlt` zulässig ist

Erst wenn **alle** Stufen versucht wurden. Halte je Eintrag fest, was versucht wurde:

```
versucht    ordner, system, mail:<suchanfrage>, portal:<url> → <ergebnis>
```

Ein `fehlt` ohne Portalversuch ist ein Fehler der Sammlung, kein Ergebnis — ausgenommen
`bezugsweg: papier`.

Neue Dateien legst du nach dem Namensschema aus dem Context im Belegordner ab. Originale
werden nicht verändert (P-05): Wenn ein Anbieter einen kryptischen Dateinamen liefert, lege
eine Kopie mit sprechendem Namen an oder vermerke die Zuordnung — benenne das Original nicht
um, wenn der Context `originale_unveraendert: true` setzt.

Bei Portalen, die PDFs nur im Browser-Viewer anzeigen: Hinweis auf die Browsereinstellung
geben, statt zu versuchen, den Viewer zu bedienen — dessen Bedienleiste ist nicht erreichbar.

## Schritt 5 — Soll-Liste schreiben

`.claude/buchhaltung-log/<zeitraum>/10-soll-liste.md`:

```
quelle        zahlung | lieferantenliste | ausgangsordner
lieferant
erwartet_am   Datum oder Zeitraum
betrag        falls bekannt, mit Währung
status        vorhanden | fehlt | portal_login_noetig | domain_gesperrt | papier
              | noch_nicht_ausgestellt | kein_beleg_erwartet | ausgeschlossen
bezugsweg     mail:<absender> | portal:<url> | papier | system
datei         Pfad, falls vorhanden
versucht      bei fehlt: jede Stufe mit Ergebnis (Schritt 4)
begruendung   bei allem außer "vorhanden"
```

## Schritt 6 — Offene Punkte fortschreiben

Lies `.claude/buchhaltung-offene-punkte.md`, hake Erledigtes ab und trage Neues ein. Ohne
dieses Register wird eine Rechnung, die erst im Folgemonat erscheint, nie wieder gesucht.

## Rückgabe

```
Zeitraum <x>: <n> Belege erwartet, <v> vorhanden, <f> offen
Offen:
  <lieferant> — <status> — <versucht> — <begruendung>
Neu ermittelte Bezugswege (in den Context geschrieben): <Liste>
Zahlungen ohne Belegerwartung: <Liste mit Grund, z. B. Guthabenaufladung>
Ausgeschlossen: <Liste>
```
