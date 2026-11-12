# Hooks — was sie durchsetzen und was nicht

Ein Hook sieht die **Eingabe** eines Tool-Aufrufs, bevor er ausgeführt wird. Mehr nicht.
Daraus folgt, welche Regeln durchsetzbar sind und welche nur angewiesen werden können.

Das ist keine Einschränkung, die sich wegformulieren lässt. Eine Regel in eine Prompt zu
schreiben und sie „durchgesetzt" zu nennen, erzeugt genau die falsche Sicherheit, gegen die
das ganze Kit gebaut ist.

## Durchgesetzt

| Hook | Regel | Greift bei |
|---|---|---|
| `guard-originale.py` | P-03, P-05 | `Bash`, `Write`, `Edit`, `NotebookEdit` — Löschen, Verschieben, Überschreiben im Belegordner |
| `guard-uebermittlung.py` | P-01 | Navigation auf Übermittlungsziele der Finanzverwaltung |
| `guard-agenten.py` | Schreibrechte der Agenten | `Bash`, `Write`, `Edit`, `NotebookEdit` aus einem Kit-Agenten (`agent_type` = `bookkeeping-kit:<agent>`): Write/Edit nur ins eigene Memory und in `agents.md` des Laufs, Bash nur lesend |

Alle drei blockieren mit Exit-Code 2; die Begründung geht an das Modell zurück.

Die geschützten Pfade kommen aus `.claude/docs/COMPANY_CONTEXT.md` des Mandanten. Ohne
Context gibt es keine geschützten Pfade — dann ist das Kit noch nicht eingerichtet.

**Projektwurzel.** `cwd` in der Hook-Eingabe folgt jedem `cd` der Sitzung. Die Hooks suchen
den Context deshalb von `cwd` aufwärts und danach unter `CLAUDE_PROJECT_DIR`. Vorher reichte
ein `cd` in den Laufordner, und `guard-originale.py` fand keinen Context und ließ alles durch
(beobachtet im Lauf 2026-10).

**Grenze von `guard-agenten.py`:** Die Bash-Sperre erkennt Schreibbefehle an Mustern
(Umleitung mit Leerzeichen davor, `tee`, `cp`, `mv`, `rm`, `sed -i`, `open(…, 'w')`). Ein
Python-Einzeiler, der anders schreibt, oder `cmd>datei` ohne Leerzeichen kommt durch. Write
und Edit dagegen prüft der Hook am Zielpfad, und dorthin verweisen die Agenten.

## Nicht durchsetzbar

Drei Regeln, die sich auf den ersten Blick nach Hooks anfühlen und es nicht sind:

**Der Klick auf „Übermitteln".** Oberflächenbedienung läuft über Bildkoordinaten. Die
Tool-Eingabe enthält `x` und `y` — keine URL, keinen Beschriftungstext, nichts, woran sich
die Absicht erkennen ließe. Ein Hook, der bei jedem Klick fragt, ist nach dem zehnten Klick
abgeschaltet.
→ Abgedeckt durch die Navigationssperre davor, die Anweisung in `record` und Prüfung 6 des
`monthly-auditor`.

**Das Löschen eines Belegs im Buchhaltungssystem.** Gleicher Grund: ein Klick ohne lesbaren
Inhalt.
→ Abgedeckt durch den Bestandsabgleich vorher/nachher in `record`.

**Die Vollständigkeit einer Erfassung.** Ein Hook läuft vor dem Tool-Aufruf und kennt dessen
Ergebnis nicht. Ob ein Beleg tatsächlich angelegt wurde, zeigt erst der Bestand danach.
→ Abgedeckt durch die Sichtprüfung nach jedem Beleg und `40-erfassung.jsonl`.

## Nur Beobachtung

| Hook | Zweck |
|---|---|
| `spur-navigation.py` | schreibt jede Navigation nach `.claude/bookkeeping-log/navigation.jsonl` — die Grundlage, auf der das Audit prüfen kann, dass nichts übermittelt wurde |
| `sitzungsstart.py` | meldet Versionsdrift zwischen Regelwerk im Plugin und dem Stand, gegen den der Mandant zuletzt gerechnet hat |

**Grenze von `SessionStart`:** Der Hook läuft einmal beim Sitzungsbeginn. Wird das Plugin
**mitten in einer Sitzung** installiert oder aktualisiert, ist er längst gelaufen und meldet
nichts — die Drift bleibt unbemerkt, obwohl sie besteht. Deshalb prüft `monthly-run` die
Version in Phase 0 zusätzlich selbst. Ein Hook, dessen einziger Auslöser vor dem Ereignis
liegt, ist keine Absicherung.

Beide blockieren nie und fangen jeden Fehler ab. Ein Protokoll-Hook, der einen Lauf aufhält,
ist schlimmer als kein Protokoll.

## Grundsatz

Im Zweifel durchlassen. Ein Hook, der berechtigte Arbeit verhindert, wird abgeschaltet — und
dann schützt er gar nichts mehr. Die Sperren hier sind eng gefasst und treffen genau die
Fälle, die sich nicht rückgängig machen lassen.

## Prüfen

```bash
python3 hooks/selbsttest.py
```

Deckt beide Sperren in blockierender und durchlassender Richtung ab. Ein Guard, der nur
blockiert, ist genauso falsch wie einer, der nie blockiert.
