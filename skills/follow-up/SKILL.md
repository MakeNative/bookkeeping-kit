---
name: follow-up
description: "Arbeitet das Register offener Punkte ab: Belege, die beim Monatslauf fehlten, Portale ohne Login, verspätet ausgestellte Rechnungen. Entscheidet je Fund, ob er in den alten Zeitraum gehört oder in den laufenden. Triggers on: /bookkeeping-kit:follow-up [YYYY-MM]"
disable-model-invocation: true
argument-hint: "[YYYY-MM]"
---

Ein Monatslauf endet fast nie vollständig. Rechnungen erscheinen später, Portale waren nicht
erreichbar, ein Anbieter stellt grundsätzlich erst Wochen danach aus.

Ohne diesen Schritt bleiben solche Belege für immer liegen: Der nächste Monatslauf sucht nur
seinen eigenen Zeitraum, und niemand kommt auf den vorherigen zurück.

## Eingabe

`.claude/bookkeeping-open-items.md` — das Register, das `collect` fortschreibt. Ohne
Argument arbeitest du alle offenen Einträge ab, mit `YYYY-MM` nur die eines Zeitraums.

## Schritt 1 — Nachsehen

Je offenem Eintrag die Quelle erneut prüfen, in der Reihenfolge aus `collect`: Ordner,
Postfach, Portal. Portale erst zum Schluss und mit gebündeltem Login-Bedarf (P-02).

## Schritt 2 — Die eigentliche Frage: welcher Zeitraum?

Das ist die einzige schwierige Entscheidung dieser Skill, und sie hat zwei getrennte
Antworten — eine für die Umsatzsteuer, eine für die Ablage.

| Lage | Zuordnung |
|---|---|
| Rechnung trägt ein Datum **im** alten Zeitraum, dieser ist **noch nicht** übermittelt | in den alten Zeitraum, normal erfassen |
| Rechnung trägt ein Datum **im** alten Zeitraum, dieser ist **bereits** übermittelt | → `correction`, nicht hier |
| Rechnung wurde **erst später ausgestellt** (Muster M-08, Regel E-12) | in den Zeitraum der Ausstellung — das ist keine Nachmeldung, sondern der richtige Monat |

Der dritte Fall ist der häufigste und wird regelmäßig falsch behandelt: Eine Rechnung, die im
Oktober für eine Septemberleistung ausgestellt wird, gehört beim Vorsteuerabzug in den
Oktober. Sie ist kein versäumter Septemberbeleg.

Bei Reverse Charge und innergemeinschaftlichem Erwerb kann die Steuer dagegen an den
Leistungszeitpunkt anknüpfen — prüfe das am Regelwerk, statt die Datumsregel der
Inlandsvorsteuer zu übertragen.

## Schritt 3 — Wirkung prüfen, bevor etwas passiert

Rechne je Fund aus, was er in seinem Zielzeitraum bewirkt:

```
<beleg> → Zeitraum <x> · Kennziffer <kz> · Wirkung auf die Zahllast <betrag>
```

Nenne ausdrücklich, was **zahllastneutral** ist. Ein nachgetragener Reverse-Charge-Beleg
verschiebt zwei gegengleiche Kennziffern und sonst nichts — das zu wissen erspart dem Nutzer
die Frage, ob es eilt.

## Schritt 4 — Erfassen

Für Belege, die in einen **offenen** Zeitraum gehören: über die `record`-Skill, mit
derselben Dublettenprüfung. Ein nachgetragener Beleg ist der klassische Kandidat für eine
Doppelbuchung, weil zwischen Erstlauf und Nachtrag Zeit vergangen ist (P-04).

Für Belege in einen bereits übermittelten Zeitraum: nicht erfassen, sondern an `correction`
übergeben.

## Schritt 5 — Register fortschreiben

Je Eintrag: erledigt mit Fundstelle, oder weiter offen mit **neuem Prüfdatum und Grund**.

Ein Eintrag, der dreimal ohne Fortschritt verschoben wurde, ist eine eigene Meldung wert —
entweder ist der Beleg nicht zu beschaffen, oder die Erwartung war von Anfang an falsch
(etwa eine Guthabenaufladung, die nie eine Rechnung erzeugt, Regel E-11). Schlage dann vor,
die Erwartung zu streichen, statt sie weiterzuschleppen.

## Rückgabe

```
<n> offene Punkte geprüft

Erledigt
  <lieferant> — <datei> — Zeitraum <x> — <erfasst|an correction>

Weiter offen
  <lieferant> — <grund> — nächste Prüfung <datum> — <n>. Versuch

Zur Streichung vorgeschlagen
  <lieferant> — <warum die Erwartung nicht zutrifft>

Zahllastwirkung gesamt je Zeitraum: <x> <betrag>
```
