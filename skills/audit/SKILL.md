---
name: audit
description: "Startet die unabhängige Nachprüfung eines Laufs — Stichprobe gegen die Originalbelege und Auswertung der Pipeline über mehrere Zeiträume. Triggers on: /bookkeeping-kit:audit [YYYY-MM] [--eval]"
disable-model-invocation: true
argument-hint: "[YYYY-MM] [--eval]"
---

Du stößt die Nachprüfung an und bereitest ihr Ergebnis zur Entscheidung auf. Die Prüfung
selbst machen zwei Agenten — getrennt von dir und voneinander, weil beide unabhängig sein
müssen von dem, was im Lauf passiert ist.

Ohne Argument nimmst du den jüngsten Zeitraum. `--eval` lässt zusätzlich über alle
vorhandenen Läufe auswerten.

## Schritt 1 — Prüfbarkeit feststellen

Ein Audit auf unvollständiger Grundlage täuscht Sicherheit vor. Prüfe, was vorliegt:

```
10-soll-liste · 20-belege · 30-klassifikation · 40-erfassung · 50-gates · 60-entscheidungen
```

Fehlt eine Datei, läuft das Audit trotzdem — aber die Lücke steht **im Ergebnis**, nicht nur
in deiner Notiz. Ein Lauf ohne `40-erfassung.jsonl` lässt sich nicht gegen den Systembestand
prüfen, und das muss derjenige wissen, der die Voranmeldung freigibt.

## Schritt 2 — Monatsauditor

Spawne `monthly-auditor` mit dem Auftragsrahmen aus `monthly-run` (Abschnitt „Agenten starten“),
dazu Pfad zum Laufverzeichnis und Pfad zum Belegordner.

Gib ihm **keine** Zusammenfassung des Laufs mit. Seine Unabhängigkeit ist der Zweck der
Rolle; ein mitgeliefertes Fazit zieht ihn in dieselbe Spur, die er prüfen soll.

## Schritt 3 — Evaluator

Nur bei `--eval` oder wenn mindestens drei Läufe vorliegen.

Spawne `agent-evaluator` über alle Laufverzeichnisse, mit dem Auftragsrahmen aus `monthly-run`;
sein Protokoll ist `.claude/bookkeeping-eval/agents.md`. Er bewertet die Pipeline, nicht den
Monat — zwei verschiedene Fragen, die nicht in einen Bericht gehören.

## Schritt 4 — Ergebnis schreiben

`.claude/bookkeeping-log/<zeitraum>/80-audit.md`:

```
Audit <zeitraum> · <datum>
Urteil: bestanden | bestanden mit Auflagen | nicht bestanden
Stichprobe: <n> von <m> Belegen

Befunde nach Schwere
  <schwere> | <beleg> | <befund> | <regel> | <centwirkung>

Nicht prüfbar: <was, warum>
```

Bei `--eval` zusätzlich `.claude/bookkeeping-log/90-eval.md` — **außerhalb** des
Zeitraumordners, weil er mehrere Zeiträume umspannt.

## Schritt 5 — Vorlegen

Trenne sauber, was wen betrifft:

- **Befunde am Monat** → der Nutzer muss entscheiden, ob er sie vor der Freigabe behebt. Je
  Befund die Wirkung auf die Zahllast in Cent, und ausdrücklich auch dann, wenn sie null ist:
  Ein zahllastneutraler Befund macht die Voranmeldung trotzdem falsch.
- **Vorschläge an die Pipeline** → Änderungen an Regelwerk, Agentenbeschreibungen oder Memory.
  Lege sie einzeln vor. Übernimm keinen davon selbstständig; eine Regeländerung wirkt auf alle
  künftigen Läufe und gehört nicht als Nebenwirkung eines Audits beschlossen.

## Haltung

Ein Audit, das nichts findet, ist kein Erfolgsnachweis — es ist eine Aussage über die
Stichprobe. Gib immer mit aus, **was nicht geprüft wurde**.

Und auch nach einem bestandenen Audit gilt: Es wurde nichts übermittelt (P-01).
