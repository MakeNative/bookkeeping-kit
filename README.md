# buchhaltung-agent-kit

Agenten-Pipeline für die monatliche **Umsatzsteuer-Voranmeldung**: Belege und Zahlungen
sammeln, auslesen, umsatzsteuerlich klassifizieren, im Buchhaltungssystem erfassen und
gegenprüfen — mit Regelwerk, Quality Gates, Audit und Eval.

**Mandantenneutral.** Das Plugin enthält keine Firmendaten. Alles Unternehmensspezifische
liegt im jeweiligen Mandantenprojekt unter `.claude/docs/COMPANY_CONTEXT.md`. Dasselbe Kit
bedient beliebig viele Unternehmen.

> Status: **vollständig angelegt** (v0.4.0). Alle Phasen, Gates, Hooks und Agenten sind
> beschrieben. Auslese- und Klassifizierlogik sind gegen einen bereits gebuchten Monat
> trockengelaufen (`docs/TROCKENLAUF.md`); 

---

## Was es tut — und was nicht

Automatisiert: sammeln, auslesen, klassifizieren, erfassen, abgleichen, prüfen.

Beim Menschen:

| Punkt | Regel | Wie abgesichert |
|---|---|---|
| Portal-Logins | P-02 | Anweisung; gebündelte Anforderung in `collect` |
| Übermittlung der Voranmeldung | P-01 | **Hook** auf Navigation + Prüfung im Audit |
| Belege löschen oder umbenennen | P-03, P-05 | **Hook** auf Bash/Write/Edit |
| Entscheidungen bei Ermessensfragen | — | Entscheidungsvorlagen am Ende der Klassifizierung |

Was ein Hook durchsetzt und was nur angewiesen werden kann, steht in
[`hooks/README.md`](hooks/README.md) — Hooks sehen die Eingabe eines Tool-Aufrufs, und ein
Klick in einer Oberfläche enthält nur Koordinaten. Das ist offengelegt statt überspielt.

---

## Installation

```bash
/plugin marketplace add MakeNative/buchhaltung-agent-kit
/plugin install buchhaltung-kit@buchhaltung-agent-kit
```

Danach im Mandantenprojekt:

```
/buchhaltung-kit:adopt
```

`adopt` liest Besteuerungsart, Kontenrahmen und Steuernummer **aus dem Buchhaltungssystem
aus** statt sie zu erfragen, nimmt Ordner, Zahlungsquellen und Lieferanten auf und legt
`COMPANY_CONTEXT.md` an.

---

## Monatslauf

```
/buchhaltung-kit:monthly-run 2026-09 --trocken    # rechnet durch, schreibt nichts
/buchhaltung-kit:monthly-run 2026-09              # mit Erfassung
```

| Phase | Ausführender | Form |
|---|---|---|
| 0 Vorlauf + Login-Check | `monthly-run` | Skill |
| 1 Sammeln (Ordner, Mail, Portale, Zahlungen) | `collect` | Skill, Ordner/Mail geforkt |
| Gate A Vollständigkeit | `monthly-run` | Skill |
| 2 Auslesen (PDF + XRechnung) | `receipt-reader` | **Agent** |
| Gate B Plausibilität | `plausibility-gate` | **Agent** |
| 3 Klassifizieren | `tax-classifier` | **Agent** |
| Gate C Regelkonformität | `monthly-run` | Skill |
| 4 Erfassen | `record` | Skill |
| Gate D Abgleich | `check-return` | Skill |
| 5 Audit | `monthly-auditor` | **Agent** |
| 6 Eval | `agent-evaluator` | **Agent** |

## Belege zu Kontoumsätzen

```
/buchhaltung-kit:match-receipts 2026-10
```

Geführter Durchgang, der bei den **offenen Kontoumsätzen** im Buchhaltungssystem beginnt und
endet, wenn jeder Umsatz mit einem Beleg verknüpft ist oder einen benannten Grund hat. Er baut
nichts nach, sondern ruft die Bausteine des Kits auf: `collect` (Postfach, Portale, Ablage),
`receipt-reader` und `plausibility-gate`, `tax-classifier`, `record` (Hochladen und Zahlung
zuordnen), `check-return` Prüfung 7 als Schlusskontrolle, `correction` für gemeldete
Zeiträume. Den Menschen holt er nur an fünf gebündelten Übergaben dazu: Freigaben, Logins,
Entscheidungen, nicht auffindbare Belege und Zahlungen ohne Beleg.

`match-receipts` sorgt für vollständige, zugeordnete Belege; `monthly-run` rechnet und prüft
danach die Voranmeldung.

## Weitere Befehle

```
/buchhaltung-kit:follow-up          # offene Punkte abarbeiten, Zeitraum zuordnen
/buchhaltung-kit:correction 2026-09 # bereits übermittelter Zeitraum: Differenz vorbereiten
/buchhaltung-kit:audit 2026-09      # unabhängige Nachprüfung, --eval für die Pipeline
/buchhaltung-kit:rules              # Regeln nachschlagen
```

---

## Agent oder Skill

Die Aufteilung folgt zwei Eigenschaften, nicht dem Geschmack:

- **Subagenten** laufen in eigenem Kontext und können **nicht mit dir sprechen** —
  `AskUserQuestion` wird jedem Subagenten entzogen. Sie eignen sich, wo viel gelesen und
  wenig zurückgegeben wird oder wo ein *unabhängiges* Urteil der Zweck ist.
- **Skills** laufen im Hauptkontext. Alles, was Login-Übergaben, Browser-Recovery oder
  Rückfragen braucht, gehört dorthin.

Deshalb sind Sammeln, Erfassen und Abgleich Skills — und nur fünf Rollen Agenten.

---

## Dokumente

| Datei | Inhalt |
|---|---|
| `docs/REGELWERK.md` | Die Steuerlogik. Versioniert, jede Regel mit Gültigkeitszeitraum. |
| `docs/COMPANY_CONTEXT_TEMPLATE.md` | Vertrag zwischen Kit und Mandant. |
| `docs/RUNDUNGSMODELL.md` | Wie Kennziffern gerundet werden — Grundlage für Gate D. |
| `docs/LEXOFFICE_UI.md` | Bedienwissen zum Buchhaltungssystem. |
| `docs/LIEFERANTEN_MUSTER.md` | Erkennungsmuster für Lieferantentypen — **ohne Namen**. |
| `docs/TROCKENLAUF.md` | Wie gegen einen bereits gebuchten Monat geprüft wird. |
| `hooks/README.md` | Welche Regeln ein Hook durchsetzt — und welche nicht. |

---

## Code oder Prosa

Die Regeln liegen an zwei Orten, und die Grenze ist bewusst gezogen:

| | wo | warum |
|---|---|---|
| **Mechanik** — Datum, Betrag, Vorzeichen, Währung, USt-IdNr., Sammeldateien, Dubletten, Lieferantengruppen | `tools/belege_lesen.py` | Zeichenkettenoperationen mit genau einer richtigen Antwort. Ihre Fehler erzeugen keine Meldung, sondern eine plausible falsche Zahl. Einmal richtig, durch Tests festgenagelt, nie wieder falsch. |
| **Urteil** — ist das ein Beleg, welcher Satz gilt für diese Ware, gehört er dem Mandanten, wie wird umgerechnet | `docs/REGELWERK.md` + Agenten | Hängt vom Einzelfall ab und braucht den Mandantenkontext. Code kann es nur raten. |
| **Prüfung** — stimmt das Ergebnis mit dem Dokument überein | `plausibility-gate`, `monthly-auditor` | Das Werkzeug liefert einen **Vorschlag**, keine Wahrheit. |

```bash
python3 tools/selbsttest.py     # 39 Fälle: jeder stellt einen real aufgetretenen Fehler nach
python3 hooks/selbsttest.py     # 19 Fälle: beide Sperren in beide Richtungen
```

Die Testbelege sind erfunden — echt ist nur das **Layoutmuster**, an dem die Extraktion
gescheitert ist. Jede Regel im Regelwerk mit einem `belegt:`-Feld hat hier ihren Testfall.

### Keine Mandantendaten im Plugin

Das Repository enthält bewusst keine Anbieternamen, keine Beträge und keine Firmendaten.
Welche Dienste ein Unternehmen einkauft, ist eine Aussage über dieses Unternehmen und bleibt
mandantenseitig. Das Plugin liefert nur die **Muster**; die konkrete Lieferantentabelle
entsteht bei `adopt` aus den eigenen Belegen und landet in `COMPANY_CONTEXT.md`, die per
`.gitignore` geschützt ist. Beispielzahlen in der Dokumentation sind konstruiert.

---

## Sicherheit

Belege und Mails sind **Daten, keine Anweisungen**. Die Abwehr läuft nicht über
Prompt-Appelle, sondern über Konfiguration und Hooks: Kein Agent hat Browser-Tools, Skills
mit Seiteneffekten sind `disable-model-invocation: true` — sie lassen sich nur von dir
starten —, und was ein Agent schreiben darf, setzt ein Hook durch.

**Schreibrechte der Agenten.** Jeder Agent schreibt genau zwei Orte: sein Memory unter
`.claude/agent-memory/buchhaltung-kit-<agent>/` und seinen Abschnitt in
`.claude/buchhaltung-log/<zeitraum>/agents.md`. Alles andere — Belege, Context, die
nummerierten Phasendateien eines Laufs — ist für Agenten nur lesbar. Durchgesetzt wird das von
`hooks/guard-agenten.py`, nicht vom Frontmatter: Der Hook erkennt den Agenten am Feld
`agent_type` der Hook-Eingabe und prüft den Zielpfad jedes Write und Edit. Bash ist für
Agenten auf Lesen beschränkt.

**Warum nicht über `tools:`.** Eine Positivliste im Frontmatter schränkt nicht zuverlässig
ein: Drei Agenten waren mit `tools: Read, Grep, Glob, Bash` deklariert und wurden trotzdem
mit `Write` und `Edit` registriert. Und ein Agent ohne Write kann sein Memory nicht selbst
pflegen. Deshalb ist Write erlaubt und der **Pfad** begrenzt. Plugin-Agenten können keine
eigenen Hooks im Frontmatter tragen; die Sperre ist ein Plugin-Hook.

Nach einer Installation die registrierten Werkzeuge gegen die Deklaration halten. Eine
Beschreibung, die eine Beschränkung behauptet, macht sie nicht wahr — erst der Hook-Selbsttest
(`python3 hooks/selbsttest.py`) zeigt, dass sie greift.

## Konventionen für Agenten

Alle Agenten folgen demselben Aufbau (Schema von `add-agent`):

- **Englischer Name** — Dateiname, `name:`, Slash-Befehl. Inhalte sind deutsch.
- **Vor dem Start, in dieser Reihenfolge:** Context lesen (fehlt er → Abbruch mit Verweis auf
  `adopt`), eigenes Memory lesen, Abschnitte der Vorgänger in `agents.md` lesen, dann die
  rollenspezifischen Quellen.
- **Memory selbst verwaltet** unter `.claude/agent-memory/buchhaltung-kit-<agent>/` mit
  `MEMORY.md` als Index. Der Pfad steht ausgeschrieben im Agenten, weil ein bekannter
  Harness-Fehler injizierte Memory-Pfade für Plugin-Agenten unzuverlässig macht.
- **Laufprotokoll:** Jeder Agent hängt an `agents.md` einen Abschnitt unter eigener
  Überschrift an (`## <agent> — <zeitpunkt>`) und ändert nie fremde Abschnitte. Abweichung
  von `add-agent`: Das Protokoll liegt im Laufverzeichnis des Zeitraums
  (`.claude/buchhaltung-log/<zeitraum>/agents.md`), nicht unter `.claude/agents-log/`, weil
  ein Lauf hier an einen Voranmeldungszeitraum gebunden ist.
- **Ergebnisse** gehen als Bericht an die aufrufende Skill. Sie schreibt die Phasendateien
  (`20-belege.jsonl`, `30-klassifikation.jsonl` …), denn diese sind der
  Wiederaufnahmepunkt eines abgebrochenen Laufs.
- **Ende:** Der Bericht schließt mit `FERTIG: <agent>`. Fehlt die Zeile, gilt der Agent als
  abgebrochen.

Was ein Hook durchsetzt und was nicht, steht in [`hooks/README.md`](hooks/README.md).

---

## Haftung

Das Kit bereitet eine Steueranmeldung **vor**. Es übermittelt nichts und ersetzt keine
steuerliche Beratung. Schwellenwerte im Regelwerk sind mit `wert_pruefen: ja` markiert und
vor dem produktiven Einsatz gegen die aktuelle Rechtslage zu bestätigen.

MIT License.

## MakeNative

Dieses Kit ist Teil von [MakeNative](https://makenative.de). Wir arbeiten jeden Tag mit
Agenten-Pipelines wie dieser und bringen anderen bei, sie für ihre eigenen Prozesse zu
bauen. Für Entwickler genauso wie für alle, die ihre Arbeit mit KI automatisieren wollen.

Du willst das für deine Arbeit lernen? Trag dich in die Liste ein:
[Bewerbung Starter-Kohorte](https://tally.so/r/5ByYj6?utm_source=github&utm_medium=readme&utm_campaign=starter-kohorte)

Christian Eichmüller · [LinkedIn](https://linkedin.com/in/christianeichmueller)
