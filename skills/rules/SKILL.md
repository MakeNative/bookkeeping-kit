---
name: rules
description: "Schlägt die umsatzsteuerlichen Regeln des Kits nach und hilft, neue Regeln aufzunehmen. Nutze dies, wenn eine Belegbehandlung begründet, eine Regel-ID aufgelöst oder eine Lücke im Regelwerk geschlossen werden soll. Triggers on: /bookkeeping-kit:rules [Suchbegriff oder Regel-ID]"
---

Das Regelwerk steht in `docs/REGELWERK.md` des Plugins. Diese Skill bleibt bewusst dünn —
lies die Regeldatei, statt den Inhalt hier zu duplizieren.

## Nachschlagen

Ohne Argument: nenne die Gruppen und wofür sie stehen.

| Gruppe | Inhalt |
|---|---|
| G | Grundlagen — Besteuerungsart, Steuerentstehung, Fristen |
| E | Eingangsseite — Vorsteuer, Reverse Charge, ig. Erwerb, Belegqualität |
| A | Ausgangsseite — Umsatz, Storno, Änderung der Bemessungsgrundlage |
| F | Fremdwährung |
| B | Belegqualität und Erkennung |
| P | Prozess — die harten Grenzen |

Mit Argument: finde die passenden Regeln und gib sie vollständig aus — Regel, Prüfung, Folge,
Gültigkeit. Nenne immer die ID, damit sie zitierbar bleibt.

## Zeitliche Geltung

Jede Regel hat `gilt_ab` und optional `gilt_bis`. Für einen Lauf über einen zurückliegenden
Zeitraum gelten die Regeln, die **damals** galten. Prüfe das, bevor du eine Regel auf einen
alten Monat anwendest.

Regeln mit `wert_pruefen: ja` enthalten einen Schwellenwert, der sich geändert haben kann.
Weise darauf hin, statt den Wert ungeprüft zu verwenden.

## Neue Regel aufnehmen

Eine Regel wird nur aufgenommen, wenn es einen **konkreten Beleg** gibt, an dem sie nötig
wurde. Ohne Anlassfall entsteht totes Regelwerk.

Verlange deshalb:
1. den Sachverhalt am Beispiel
2. die rechtliche Grundlage
3. woran der Agent den Fall erkennt
4. die Folge (Kennziffer, Kategorie, Konsequenz)
5. ab wann sie gilt

Vergib die nächste freie ID in der passenden Gruppe, ergänze die Änderungshistorie und erhöhe
`REGELWERK_VERSION`.

## Regel ändern

Regeln werden **nie gelöscht und nie überschrieben**. Setze `gilt_bis` auf den letzten Tag
der alten Fassung und lege die neue Fassung als neue ID an. Sonst lassen sich alte Läufe
nicht mehr nachvollziehen.
