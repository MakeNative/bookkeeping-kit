---
name: monatslauf
description: "Führt den vollständigen Lauf für einen Voranmeldungszeitraum: sammeln, auslesen, prüfen, klassifizieren, erfassen, abgleichen, auditieren. Mit --trocken wird gerechnet, aber nichts geschrieben. Triggers on: /buchhaltung-kit:monatslauf <YYYY-MM> [--trocken]"
disable-model-invocation: true
argument-hint: "<YYYY-MM> [--trocken]"
---

Du bist der Orchestrator. Führe die Schritte **selbst** aus — delegiere die Orchestrierung
nicht an einen Agenten. Zwischen den Phasen musst du sehen, entscheiden und notfalls den
Nutzer fragen; genau deshalb ist das hier eine Skill und kein Subagent.

## Vorbedingungen

**Dieser Lauf gehört ins Mandantenprojekt**, nicht ins Plugin-Repo. Er liest und schreibt
unter `.claude/` des Mandanten.

Suche `.claude/docs/COMPANY_CONTEXT.md` **relativ zum Arbeitsverzeichnis**. Fehlt sie,
unterscheide zwei Lagen, bevor du etwas behauptest:

- Es gibt sie nirgends → der Mandant ist nicht eingerichtet → `/buchhaltung-kit:adopt`.
- Du stehst im falschen Verzeichnis (etwa im Plugin-Repo) → **sag das**, nenne den Pfad, den
  du geprüft hast, und frag nach dem Mandantenprojekt. Auf `adopt` zu verweisen wäre hier
  falsch und würde einen bestehenden Context überschreiben.

Erstes Argument ist der Zeitraum (`YYYY-MM`, bei Quartalsmeldung der erste Monat des
Quartals). `--trocken` überspringt Phase 4.

## Phase 0 — Vorlauf

**Lege das Laufverzeichnis zuerst an, nicht zuletzt.** Ein Lauf, der in Schritt 3 abbricht,
muss eine Spur hinterlassen — sonst ist später nicht nachvollziehbar, dass und warum er
versucht wurde.

1. Laufverzeichnis `.claude/buchhaltung-log/<zeitraum>/` anlegen und `00-lauf.md` beginnen:
   Zeitraum, Modus, Startzeit. Alles Weitere wird **angehängt**, auch ein Abbruch.
2. Zeitraum und Modus festhalten.
3. `COMPANY_CONTEXT.md` lesen. **Besteuerungsart, Turnus und Dauerfristverlängerung gegen das
   System prüfen** — nicht nur die Datei glauben. Ändert sich eines davon, ist das ein
   Befund, bevor irgendetwas gerechnet wird (G-01).
4. Meldestatus prüfen: Ist der Zeitraum schon übermittelt? Dann ist dies ein
   Korrekturvorgang → Abbruchgrund **in `00-lauf.md` festhalten**, auf
   `/buchhaltung-kit:korrektur` verweisen und abbrechen.
5. `REGELWERK_VERSION` aus Plugin und Context vergleichen. Drift melden — und zwar mit
   beiden Ständen und dem Hinweis, dass Regeln nur ab ihrem `gilt_ab` wirken.

   Verlass dich dabei **nicht** auf den Sitzungsstart-Hook. Er meldet Drift nur, wenn die
   Sitzung mit installiertem Plugin beginnt; wird das Plugin mitten in der Sitzung
   installiert oder aktualisiert, hat er längst gelaufen. Die Prüfung hier ist die
   verlässliche.

   Drift ist **nicht blockierend**. Fast alle Regeln gelten rückwirkend ab 2020 — ein Lauf
   unter einer neueren Fassung kann für denselben Zeitraum ein anderes Ergebnis liefern als
   der alte. Genau dafür gibt es den Trockenlauf gegen einen bereits gebuchten Monat
   (`docs/TROCKENLAUF.md`). Nenne die seit der Mandantenversion hinzugekommenen Regel-IDs,
   damit erkennbar ist, was sich geändert haben kann.

### Im laufenden Betrieb ist der Monatslauf der Ausnahmefall

Ist die Buchhaltung aktuell, sind alle vergangenen Zeiträume übermittelt und `monatslauf`
greift nur für den **laufenden** Zeitraum. Jede Aufarbeitung der Vergangenheit — ein
nachträglich gefundener Beleg, eine korrigierte Behandlung, ein nie gebuchter Sachverhalt —
läuft über `korrektur`, nicht hierüber.

Das ist keine Einschränkung, sondern die Trennlinie: `monatslauf` bereitet eine Meldung vor,
`korrektur` ändert eine abgegebene. Wer das vermischt, meldet versehentlich neu.

## Phase 1 — Sammeln

Rufe die `sammeln`-Skill für den Zeitraum auf. Sie erzeugt `10-soll-liste.md` und, falls
nötig, `05-login-bedarf.md`.

### Gate A — Vollständigkeit

Jeder Eintrag der Soll-Liste hat einen Status. Zulässig ohne Beleg sind nur
`noch_nicht_ausgestellt`, `kein_beleg_erwartet` und `ausgeschlossen` — jeweils mit Begründung.

**Erst nachsuchen, dann urteilen.** Bevor Gate A einen Posten als offen führt:

- Jeder `fehlt` braucht ein ausgefülltes `versucht` mit Portalversuch (sammeln, Schritt 4).
  Fehlt der Portalversuch → zurück an `sammeln`, nur für diese Posten.
- Hat der Nutzer sich zwischendurch angemeldet, werden **alle** `portal_login_noetig` erneut
  versucht, nicht nur die Portale der ersten Login-Liste.

Erst was danach noch fehlt, ist offen.

- Alles sauber → weiter.
- Offene Posten → **nicht den ganzen Lauf stoppen.** Rechne mit dem Vorhandenen weiter und
  merke dir, dass Phase 4 für die betroffenen Belege gesperrt ist. Der Mensch sieht so das
  ganze Bild statt eines halben.

Schreibe das Ergebnis nach `50-gates.md`.

## Phase 2 — Auslesen

Spawne den `beleg-leser` für die vorhandenen Belege. Gib ihm den Zeitraum, die Dateiliste und
den Hinweis, dass er eine JSON-Zeile je Beleg zurückgeben soll.

Er beginnt mit `tools/belege_lesen.py` — dem deterministischen Teil — und arbeitet dann ab,
was Urteil braucht: Scans, strukturierte Rechnungen, Nichtbelege und jede `pruefen`-Marke.
Bei mehr als etwa 30 Belegen in Stapeln aufteilen — nicht ein Agent je Beleg.

Prüfe die Kopfzeile seiner Werkzeugausgabe: Stehen auffällig viele Lieferanten mit nur
**einem** Beleg oder ohne erkannten Lieferanten, trägt die Gruppierung nicht — dann ist ein
Null-Befund in Gate B kein Ergebnis, sondern ein Messfehler (E-16).

Schreibe sein Ergebnis nach `20-belege.jsonl`. **Du** schreibst, nicht er: Er hat keine
Schreibrechte, und das ist Absicht.

## Phase 3a — Gate B: Plausibilität

Spawne das `plausibilitaets-gate` mit den Belegdaten und den Dateipfaden. Es prüft
unabhängig gegen die Dokumente.

- Blockierende Befunde → diese Belege gehen **nicht** weiter. Sammle sie für den Bericht.
- Hinweise → mitführen, sie fließen in die Klassifikation ein.

Ein Lauf ohne jeden Befund über viele Belege ist ein Grund zur Nachfrage, nicht zur Freude.

## Phase 3b — Klassifizieren

Spawne den `steuer-klassifizierer` mit den bestätigten Belegdaten. Schreibe sein Ergebnis
nach `30-klassifikation.jsonl`.

### Gate C — Regelkonformität

- Jede Klassifikation nennt eine Regel-ID (P-07). Fehlt sie → zurück an den Klassifizierer.
- Widersprüche blocken: Reverse-Charge-Vermerk **und** Inlandsvorsteuer, oder Vorsteuerabzug
  trotz fehlender Pflichtangaben.
- Alle `entscheidung_noetig` sammeln.

### Entscheidungsvorlagen — gebündelt

Schreibe `60-entscheidungen.md` und lege sie dem Nutzer **am Stück** vor, nicht einzeln
während der Klassifikation. Je Vorlage: Sachverhalt, Optionen, Empfehlung, Auswirkung auf die
Zahllast in Cent.

Nenne ausdrücklich, welche Entscheidungen die Zahllast **nicht** ändern — bei
zahllastneutralen Sachverhalten ist das häufig so, und der Nutzer soll seine Aufmerksamkeit
auf das Wesentliche richten können.

Warte die Antworten ab. Übernimm sie in die Klassifikation und schlage vor, die Zuordnung ins
Lieferanten-Memory aufzunehmen, damit dieselbe Frage nicht wiederkehrt.

## Phase 4 — Erfassen

**Bei `--trocken` überspringen.**

Rufe die `erfassen`-Skill mit der Klassifikation auf. Sie prüft vor jedem Anlegen gegen den
Bestand (Dedup-Schlüssel Lieferant + Belegnummer + Belegdatum + Betrag, P-04) und schreibt
`40-erfassung.jsonl` fortlaufend — das ist der Wiederaufnahmepunkt, falls der Lauf abbricht.

Belege, die Gate A oder Gate B blockiert hat, werden **nicht** erfasst.

## Phase 5 — Gate D: Abgleich

Rufe die `abgleich`-Skill auf. Im Trockenlauf weist sie die erwartete Voranmeldung aus und
vergleicht sie mit dem Systemstand.

Blockierende Abweichungen → melden und den Lauf als unvollständig kennzeichnen. Gemeldete
Abweichungen (etwa gegengleiche Positionen, die um Cent auseinanderlaufen) → im Bericht
hervorheben, ohne zu blockieren.

## Phase 6 — Audit und Eval

Nicht im Trockenlauf.

Spawne `monats-auditor` (Stichprobe gegen die Dokumente) und anschließend `agent-evaluator`.

## Abschlussbericht

Immer, auch bei Abbruch:

```
Zeitraum <x> · Modus <trocken|voll> · Besteuerungsart <ist|soll>

Erwartete Voranmeldung
  <kennziffer> | <basis> | <steuer>
  Zahllast: <betrag>

Belege       <n> gesammelt, <m> ausgelesen, <k> klassifiziert, <e> erfasst
Gates        A <status> · B <status> · C <status> · D <status>
Blockiert    <Belege mit Grund>
Offen        <fehlende Belege, Logins, Entscheidungen>
Zu klären    <gemeldete, nicht blockierende Abweichungen>
```

Schließe mit dem ausdrücklichen Hinweis: **Es wurde nichts übermittelt.** Die Übermittlung
ist allein Sache des Menschen (P-01).

### Regelwerksversion nachziehen

Lief der Lauf **vollständig** durch und wurde die Drift aus Phase 0 vom Nutzer zur Kenntnis
genommen, schlage vor, `REGELWERK_VERSION` in `COMPANY_CONTEXT.md` auf den Plugin-Stand zu
setzen. Ohne das steht die Drift bei jedem künftigen Lauf erneut im Bericht und wird zum
Rauschen, das man wegliest.

Ziehe sie **nicht** selbstständig nach und **nicht** nach einem abgebrochenen Lauf: Die
Version sagt aus, gegen welches Regelwerk zuletzt tatsächlich gerechnet wurde.

## Haltung

Blockierende Gates stoppen die **Schreibphasen**, nicht die Analyse. Rechne immer bis zur
erwarteten Voranmeldung durch — ein halbes Ergebnis hilft niemandem bei der Entscheidung,
was als Nächstes zu tun ist.
