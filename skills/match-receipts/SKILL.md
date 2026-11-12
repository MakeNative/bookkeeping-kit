---
name: match-receipts
description: "Führt den Menschen in einem Durchgang von den offenen Kontoumsätzen im Buchhaltungssystem zu hochgeladenen, verknüpften Belegen: Umsätze ziehen, fehlende Belege bestimmen, aus Postfächern und Portalen holen, ablegen, auslesen, klassifizieren, hochladen und mit der Zahlung verbinden. Ruft dafür die vorhandenen Skills und Agenten des Kits auf und holt den Menschen nur dazu, wenn sein Input nötig ist. Triggers on: /bookkeeping-kit:match-receipts [YYYY-MM]"
disable-model-invocation: true
argument-hint: "[YYYY-MM]"
---

Du bist der Orchestrator eines Durchgangs, der bei den **Kontoumsätzen** beginnt und erst
endet, wenn jeder Umsatz des Zeitraums mit einem Beleg verknüpft ist oder einen benannten
Grund hat, warum nicht.

**Du baust nichts nach, was das Kit schon kann.** Sammeln, Logins, Ablage, Auslesen,
Prüfen, Klassifizieren, Erfassen, Zuordnen und Korrektur gibt es als Skills und Agenten. Diese
Skill steuert nur drei Dinge selbst: die Kontoumsätze als Ausgangspunkt, die Übergaben an den
Menschen und die Schlusskontrolle. Alles andere rufst du auf, und deren Regeln gelten
unverändert — auch ihre Gates.

| Baustein | Aufgabe in diesem Durchgang |
|---|---|
| `collect` | Bezugsweg, Postfach, Login-Check, Portale, Ablage, Soll-Liste, Register |
| `receipt-reader`, `plausibility-gate` | Auslesen und Gate B, wie `monthly-run` Phase 2 und 3a |
| `tax-classifier` | Klassifikation und Gate C, wie `monthly-run` Phase 3b |
| `record` | Hochladen, Dublettenprüfung, Kategorie, Zahlung zuordnen (Schritt 3b) |
| `check-return` | Prüfung 7 „Zuordnungsstatus der Kontoumsätze" als Schlusskontrolle |
| `correction` | Belege, deren Datum in einem gemeldeten Zeitraum liegt |
| `follow-up` | was am Ende offen bleibt, beim nächsten Mal |

Abgrenzung zu `monthly-run`: Der Monatslauf rechnet die Voranmeldung und prüft sie. Dieser
Durchgang sorgt dafür, dass die Belege dafür vollständig und zugeordnet sind. Er übermittelt
nie etwas (P-01).

## Der Mensch im Loop

Der Mensch muss nicht danebensitzen, soll aber auch nicht suchen müssen, was du von ihm
willst. Du holst ihn nur bei diesen **Übergaben** dazu, jeweils gebündelt und mit dem
passenden Fenster im Vordergrund:

| Übergabe | Wann | Quelle |
|---|---|---|
| Freigaben | einmal am Anfang | Schritt 0 |
| Logins | einmal, nach der Postfachsuche | `collect` Schritt 3 |
| Entscheidungen | einmal, nach der Klassifikation | `monthly-run` „Entscheidungsvorlagen" |
| Nicht auffindbar | einmal, vor dem Hochladen | Schritt 4 |
| Ohne Beleg zuordnen | am Ende | Schritt 6 |

Frag mit AskUserQuestion und festen Optionen, nie mit einer bloßen Frage am Ende einer
Antwort — sonst sieht es aus, als sei der Durchgang stehen geblieben. Zwischen den Übergaben
arbeitest du durch, ohne Rückfrage. Gib nie Zugangsdaten ein (P-02).

## Laufdateien

Im Laufverzeichnis `.claude/bookkeeping-log/<zeitraum>/`. Die Dateien der aufgerufenen Skills
(`10-soll-liste.md`, `20-belege.jsonl`, `30-klassifikation.jsonl`, `40-erfassung.jsonl`,
`agents.md`) entstehen dort wie gewohnt; bestehende werden fortgeschrieben, nicht ersetzt.
Eigene Datei dieses Durchgangs:

```
70-umsaetze.jsonl   ein Eintrag je Kontoumsatz:
                    umsatz_id · datum · betrag · empfaenger · verwendungszweck
                    status · beleg (Datei oder Beleg-ID) · grund
```

Gibt es sie schon, setz dort fort: Umsätze mit Status `verknuepft` oder
`ohne_beleg_bestaetigt` fasst du nicht mehr an.

## Bestand zuerst — nichts doppelt

Vor **jedem** Schritt stellst du fest, was es schon gibt, und arbeitest nur die Differenz ab.
Ein Zeitraum hat oft schon einen `monthly-run`, einen früheren Durchgang oder Handarbeit im
System hinter sich. Was davon schon erledigt ist, wird übernommen, nicht neu gemacht:

| Schritt | Schon erledigt, wenn … | Quelle |
|---|---|---|
| Umsatz einordnen | er im System zugeordnet ist (`bookingState`) | System, nicht Datei |
| Beleg suchen | Soll-Liste ihn `vorhanden` führt oder eine Datei im Belegordner bzw. in `belege/` des Laufs ihm zugeordnet ist | `10-soll-liste.md`, Feld `beleg` in `70-umsaetze.jsonl` |
| Bezugsweg ermitteln | der Lieferant im Context `beleg_quelle` **und** `portal` hat | Context |
| Auslesen | die Datei in `20-belege.jsonl` steht (gleicher Pfad oder gleicher Hash) | `20-belege.jsonl` |
| Gate B | ein Urteil zur Datei in `50-gates.md` steht | `50-gates.md` |
| Klassifizieren | der Beleg in `30-klassifikation.jsonl` steht und keine neue Entscheidung ihn ändert | `30-klassifikation.jsonl` |
| Entscheidung | sie in `60-entscheidungen.md` beantwortet ist oder im Context steht | beides |
| Hochladen | der Beleg im System liegt (Dedup-Schlüssel P-04) oder `40-erfassung.jsonl` ihn `angelegt` führt | System **und** Datei |
| Zuordnen | der Umsatz im System verknüpft ist | System |

Bei Widerspruch gilt das System vor der Datei: Steht ein Beleg in `40-erfassung.jsonl`, fehlt
aber im System, ist er gelöscht oder nie gelandet → melden, nicht still neu anlegen.

Beginne den Durchgang mit einer **Bestandsaufnahme** in `00-lauf.md`: je Schritt, wie viel
erledigt ist und wie viel offen. Der Mensch sieht so, dass nichts doppelt läuft, und du
rufst jeden Baustein nur mit der offenen Restmenge auf.

## Schritt 0 — Vorlauf

1. Context lesen; fehlt er, Abbruch mit Verweis auf `adopt`.
2. Zeitraum: Argument, sonst der letzte abgeschlossene Monat. Meldestatus prüfen wie in
   `monthly-run` Phase 0.
3. **Übergabe Freigaben**, in einer Frage:
   - Zuordnungsregel für `record` Schritt 3b: nur exakter Betrag und Lieferant, oder mit
     Toleranz bei Fremdwährung (Belastung laut Bank)
   - Hochladen und Verknüpfen, oder nur vorbereiten (dann endet der Durchgang nach Schritt 4)

## Schritt 1 — Kontoumsätze ziehen und einordnen

Alle **nicht zugeordneten** Umsätze des Zeitraums aus dem System lesen
(`docs/LEXOFFICE_UI.md`, „Kontoumsätze lesen") und je Umsatz einordnen. Die Ursachen sind die
von `check-return` Prüfung 7, damit Anfang und Ende dieselbe Sprache sprechen:

| Status | Erkennung | Weiter mit |
|---|---|---|
| `kein_beleg_erwartet` | Finanzamt, Krankenkasse, Künstlersozialkasse, Lohn, Umbuchung — **erst** prüfen, ob das System dafür einen Beleg hat (Lohnbelege `LG-…`/`LS-…`, Steuerbescheide); dann `beleg_unverknuepft` | Schritt 6 |
| `beleg_unverknuepft` | passender Beleg liegt im System, auch unter „zu prüfen" | Schritt 5 |
| `beleg_anderer_monat` | passender Beleg mit Datum in einem anderen Zeitraum | Schritt 5 bzw. `correction` |
| `beleg_fehlt` | alles andere | Schritt 2 |

„Passend" heißt wie in `record` Schritt 3b. Mehrere Kandidaten → nicht wählen, beide
notieren und in der Übergabe „Nicht auffindbar" vorlegen.

Umsätze früherer Zeiträume nur zählen und auf das Register verweisen.

## Schritt 2 — Belege holen: `collect`

Rufe `collect` für den Zeitraum auf, mit **den Umsätzen `beleg_fehlt` als Erwartung**
(`collect` Schritt 1, Quelle `zahlung`). `collect` ermittelt die Bezugswege, durchsucht die
Postfächer je Beleg, legt die Login-Übergabe gebündelt vor, holt aus den Portalen, legt die
Dateien nach Namensschema ab, schreibt neue Bezugswege in den Context und die Soll-Liste.

Danach je Umsatz in `70-umsaetze.jsonl` die gefundene Datei eintragen.

## Schritt 3 — Auslesen, prüfen, klassifizieren

Für die neu abgelegten Belege und die `beleg_unverknuepft` unter „zu prüfen":

1. `receipt-reader`, dann `plausibility-gate` — Auftragsrahmen und Ablauf wie `monthly-run`
   Phase 2 und 3a.
2. Je Umsatz prüfen, ob der gelesene Beleg zu ihm passt (Betrag, Lieferant, Datum). Passt er
   nicht, oder blockiert Gate B ihn → zurück auf `beleg_fehlt`.
3. `tax-classifier`, Gate C und die gebündelte **Übergabe Entscheidungen** — wie
   `monthly-run` Phase 3b.

## Schritt 4 — Übergabe Nicht auffindbar

Je Umsatz, der noch `beleg_fehlt` ist, eine Frage mit festen Optionen. Zeig dabei, was
`collect` versucht hat (`versucht` aus der Soll-Liste):

- **liegt woanders** → der Mensch nennt Postfach oder Ort; zurück zu Schritt 2, nur für ihn
- **Papierbeleg** → er legt Foto oder Scan in den Belegordner; zurück zu Schritt 3
- **gibt es nicht** → Eigenbeleg nötig, ins Register
- **privat** → nicht betrieblich, ins Register mit Hinweis auf Umbuchung
- **später** → ins Register für `follow-up`

Höchstens zwei Runden zurück zu Schritt 2 oder 3; was danach fehlt, geht ins Register.

## Schritt 5 — Hochladen und verknüpfen: `record`

Rufe `record` mit der Klassifikation auf, für neue Belege und für die unter „zu prüfen"
liegenden `beleg_unverknuepft`. `record` prüft auf Dubletten, legt an, prüft den Bestand und
ordnet in Schritt 3b die Zahlung nach der Regel aus Schritt 0 zu.

Für einen `beleg_unverknuepft`, der schon fertig im System liegt, braucht es nur `record`
Schritt 3b. Für `beleg_anderer_monat` und jeden Beleg, dessen Datum in einem **gemeldeten**
Zeitraum liegt: nicht anlegen, an `correction` übergeben.

Status je Umsatz in `70-umsaetze.jsonl` aus `40-erfassung.jsonl` fortschreiben.

## Schritt 6 — Übergabe Ohne Beleg, dann Schlusskontrolle

Die `kein_beleg_erwartet`-Umsätze legst du als Liste vor: Datum, Betrag, Empfänger,
vorgeschlagene Kategorie. Zuordnen ohne Beleg ist Sache des Menschen, denn die Kategorie
entscheidet über Bilanz und Lohnbuchhaltung, nicht über die Umsatzsteuer. Bestätigt er,
setzt du `ohne_beleg_bestaetigt`.

Schlusskontrolle: `check-return` **Prüfung 7** gegen den Systemstand, nicht gegen deine
Datei. Jeder Umsatz des Zeitraums ist verknüpft oder hat einen benannten Grund. Ein
`unerklaert` ist ein Befund.

Offenes schreibst du ins Register `.claude/bookkeeping-open-items.md` (`collect`
Schritt 6); dort holt `follow-up` es beim nächsten Mal ab.

## Bericht

```
Zeitraum <x> · offene Umsätze <n> zu Beginn → <m> am Ende

verknüpft            <n>  davon neu hochgeladen <a>, im System fertiggestellt <b>
ohne Beleg           <n>  bestätigt <x>, beim Menschen offen <y>
an correction        <n>  <Beleg — gemeldeter Zeitraum>
nicht auffindbar     <n>  <Umsatz — Grund — nächster Schritt>
Neue Bezugswege      <Lieferant → Weg> (in den Context geschrieben)
Entscheidungen       <n> beantwortet, in den Context übernommen
```

Schließe mit: **Es wurde nichts übermittelt.** Ändern die hochgeladenen Belege den offenen
Zeitraum, sag das und empfiehl `monthly-run <zeitraum>` vor der Übermittlung.
