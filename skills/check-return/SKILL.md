---
name: check-return
description: "Gleicht die klassifizierten Belege gegen die Voranmeldung im Buchhaltungssystem ab: Kennziffern, Rundungsmodell, gegengleiche Positionen, offene Posten und Zuordnungsstatus. Meldet jede Abweichung mit Centbetrag. Triggers on: /bookkeeping-kit:check-return <YYYY-MM>"
disable-model-invocation: true
---

Du rechnest nach. Aus den Klassifikationen ergibt sich eine **erwartete** Voranmeldung; im
Buchhaltungssystem steht eine **tatsächliche**. Deine Aufgabe ist, jede Differenz zu finden
und zu benennen.

Du korrigierst nichts und du übermittelst nichts (P-01).

Diese Skill läuft im Hauptkontext: Es ist Arithmetik auf kleinen Daten plus das Lesen einer
Seite — ein isolierter Subagent brächte hier keinen Gewinn, nur einen verlustbehafteten
Übergang.

## Eingaben

- `30-klassifikation.jsonl` des Zeitraums
- `10-soll-liste.md` — für die Vollständigkeitsprüfung
- Die Voranmeldungsseite des Buchhaltungssystems für den Zeitraum
- Die Offene-Posten-Liste (bei Ist-Versteuerung zwingend)
- `docs/RUNDUNGSMODELL.md`

## Modus

**Trockenlauf:** Es wurde nichts erfasst. Du weist die **erwartete** Voranmeldung aus und
vergleichst sie mit dem aktuellen Stand im System. Für einen bereits gebuchten Monat ist das
ein Regressionstest: Weichen erwartete und tatsächliche Werte ab, liegt es entweder an der
Klassifikation oder an der vorhandenen Buchung — beides ist ein Befund.

**Nach der Erfassung:** Du prüfst, ob das System das abbildet, was klassifiziert wurde.

## Prüfungen

### 1. Bemessungsgrundlagen

Je Kennziffer: angezeigte Basis == abgerundete Summe der zugeordneten Nettobeträge.
Abrundung auf volle Einheiten ist deterministisch, Toleranz 0,00.

### 2. Steuerbeträge — beide Rundungsvarianten prüfen

Buchhaltungssysteme rechnen **nicht einheitlich**. Prüfe je Kennziffer:

```
a) exakte Basis    × Satz
b) gerundete Basis × Satz
```

Trifft eine Variante zu → in Ordnung, halte fest **welche**. Trifft keine zu → blockierend.

Die festgestellte Variante je Kennziffer gehört ins Laufprotokoll. Weicht ein späterer Lauf
davon ab, ist das ein Hinweis auf eine Systemänderung und wird gemeldet.

### 3. Gegengleiche Positionen

```
Steuer aus Reverse Charge == Vorsteuer aus Reverse Charge
Erwerbsteuer              == Vorsteuer aus innergemeinschaftlichem Erwerb
```

Diese Paare müssen sich aufheben. Tun sie es nicht, **melde** die Differenz mit beiden
Quellwerten und dem Centbetrag — **blockiere nicht**. Die Ursache kann eine
Rundungsunschärfe des Systems sein; ob das hinnehmbar ist, entscheidet der Mensch oder die
Steuerkanzlei vor der Übermittlung.

### 4. Summen

```
Umsatzsteuer gesamt == Summe der Steuerpositionen
Vorsteuer gesamt    == Summe der Vorsteuerpositionen
Zahllast            == Umsatzsteuer − Vorsteuer
```

### 5. Zuordnung der Belege

Jede Kennziffer mit Wert hat mindestens einen zugeordneten Beleg. Umgekehrt: jeder
klassifizierte Beleg wirkt auf genau die Kennziffer, die seine Behandlung vorsieht.

### 6. Ausgangsseite und offene Posten

Bei **Ist**-Versteuerung: Die Summe der offenen Posten muss den unbezahlten
Ausgangsrechnungen entsprechen. Jede unbezahlte Rechnung darf **nicht** in der
Bemessungsgrundlage stecken (A-01).

Prüfe zusätzlich den Nummernkreis der Ausgangsrechnungen auf Lücken und auf Stornoketten
(A-02).

### 7. Zuordnungsstatus der Kontoumsätze

Belege, die keinem Kontoumsatz zugeordnet sind, blähen die offenen Posten auf — und die sind
bei Ist-Versteuerung die Grundlage von Prüfung 6. Melde unzugeordnete Belege.

Prüfe auch die Gegenrichtung: **Kontoumsätze des Zeitraums ohne Zuordnung.** Jeder davon ist
entweder ein Beleg, der fehlt, oder eine Verknüpfung, die fehlt — beides sieht man sonst erst
in der Bankansicht des Systems. Gliedere jeden nach Ursache:

```
beleg_fehlt          Soll-Liste führt ihn als offen        → Vorsteuer fehlt in der Meldung
beleg_unverknuepft   Beleg liegt im System, ohne Zuordnung → Zuordnung nachholen (`record`)
beleg_anderer_monat  Beleg datiert in einem anderen Zeitraum, etwa Rechnung 30.09., Zahlung 01.10.
kein_beleg_erwartet  Steuer, Sozialversicherung, Lohn      → ohne Beleg zuordnen (Mensch)
unerklaert           in keiner Liste                       → blockierend: die Soll-Liste ist unvollständig
```

`unerklaert` blockiert, weil dann die Erwartung aus Phase 1 nicht alle Zahlungen kennt. Die
Summe je Ursache gehört in den Bericht. Umsätze früherer Zeiträume nur zählen und auf das
Register verweisen, sie gehören in die Korrektur.

### 8. Zusammenfassende Meldung

Gibt es Ausgangsumsätze an Kunden mit ausländischer USt-IdNr., weise auf die getrennte
Meldepflicht hin (A-05). Die Meldung selbst gehört nicht zum Automatisierungsumfang.

## Ergebnis

`.claude/bookkeeping-log/<zeitraum>/50-gates.md`, Abschnitt „Gate D":

```
erwartet vs. tatsächlich je Kennziffer
  <kennziffer> | erwartet <basis>/<steuer> | tatsächlich <basis>/<steuer> | <ok|abweichung>

Rundungsvariante je Kennziffer: <a|b>

Befunde
  blockierend: <Liste mit Centbeträgen>
  gemeldet:    <Liste, u. a. gegengleiche Positionen>

Zahllast erwartet: <x>   tatsächlich: <y>
```

## Haltung

Keine pauschale Toleranzschwelle. Ein Cent Toleranz verdeckt genau die Fehler, die du finden
sollst. Prüfe deterministische Varianten, melde Unerklärtes — und schreibe nie eine Differenz
klein, nur weil sie klein ist.
