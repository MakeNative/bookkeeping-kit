---
name: record
description: "Legt klassifizierte Belege im Buchhaltungssystem an — einzeln, mit Dublettenprüfung davor und Sichtprüfung danach. Schreibt fortlaufend mit, damit ein Abbruch ohne Doppelbuchung wiederaufgenommen werden kann. Triggers on: /buchhaltung-kit:record <YYYY-MM>"
disable-model-invocation: true
argument-hint: "<YYYY-MM>"
---

Du schreibst in ein fremdes System. Das ist die einzige Phase des Laufs, die sich nicht durch
einen weiteren Durchlauf reparieren lässt — eine doppelt angelegte Rechnung muss jemand von
Hand suchen und löschen, und Löschen ist dir verboten (P-03).

Deshalb gilt hier eine andere Haltung als in den Lesephasen: **langsam, einzeln, mit
Gegenprüfung nach jedem Schritt.**

Diese Skill läuft im Hauptkontext. Sie bedient einen Browser, stößt auf Sitzungen, die
ablaufen, und auf Dialoge, die nicht im Drehbuch stehen — sie muss fragen können.

## Vorbedingungen

Brich ab, wenn eines davon nicht gilt:

- `30-klassifikation.jsonl` liegt vor und Gate C ist durchlaufen
- keine offene `entscheidung_noetig` auf einem Beleg, den du anlegen sollst
- jeder Fremdwährungsbeleg hat einen entschiedenen Umrechnungskurs (F-01)
- jeder `ig_erwerb_satz_offen` hat einen zugewiesenen Satz (E-05)

Belege, die Gate A oder Gate B blockiert hat, werden **nicht** erfasst. Sie fehlen im Ergebnis
und stehen im Bericht — das ist richtig so.

## Vor dem ersten Beleg

Lies `docs/LEXOFFICE_UI.md` bzw. das Bedienwissen zum System aus dem Context. Halte den
Ausgangsstand fest: **Anzahl der Belege im Zeitraum vor Beginn.** Ohne diese Zahl kannst du
später nicht beweisen, dass genau die angelegt wurden, die du anlegen wolltest.

## Je Beleg — in dieser Reihenfolge

### 1. Dublettenprüfung **vor** dem Anlegen (P-04)

Suche im System nach dem Schlüssel:

```
lieferant + belegnummer + belegdatum + betrag
```

Treffer → **nicht anlegen**, Status `bereits_vorhanden` mit der gefundenen Beleg-ID. Das ist
kein Fehler, sondern der Normalfall bei einem wiederaufgenommenen Lauf.

Teiltreffer (gleiche Nummer, anderer Betrag) → nicht anlegen, als Prüffall melden. Ein
abweichender Betrag bei gleicher Nummer ist entweder eine Korrekturrechnung oder ein
Lesefehler; beides entscheidest du nicht.

### 2. Anlegen

Felder aus der Klassifikation, nichts aus dem Gedächtnis.

Zwei wiederkehrende Fallen:

- **Die Steuerbehandlung hängt oft an der Kategorie, nicht am Steuersatzfeld.** Reverse
  Charge und innergemeinschaftlicher Erwerb werden über eine eigene Kategorie gebucht; wer
  den Steuersatz auf 0 % setzt und die Standardkategorie lässt, erzeugt einen steuerfreien
  Inlandsbezug statt der gegengleichen Position. Die Zahllast stimmt dann zufällig, die
  Kennziffern nicht.
- **Die Belegnummer ist Pflicht**, auch wenn der Anbieter keine vergibt. Dann nimm die
  Bezeichnung aus dem Context-Schema, nie eine erfundene fortlaufende Nummer.

### 3. Speichern — und nachsehen

Ein Klick, der nicht gelandet ist, sieht aus wie ein Klick, der gelandet ist.

- **Vor jedem Klick ein frischer Bildschirmabzug.** Koordinaten aus einem älteren Abzug
  treffen nicht, sobald sich die Fensterskalierung ändert.
- Öffnet das System den Bearbeiten-Dialog in einem eigenen Fenster, kann dieses Fenster die
  Schaltfläche darunter verdecken. Reagiert ein Klick wiederholt nicht, liegt es häufiger an
  einem überlagernden Fenster als am Klick.
- **Erfolg wird am Bestand geprüft, nicht an der Rückmeldung der Oberfläche.** Nach jedem
  Beleg: Zähler bzw. Liste neu laden und prüfen, dass genau **ein** Beleg hinzugekommen ist.

Zwei hinzugekommene Belege → sofort anhalten und melden. Weiterarbeiten vervielfacht den
Fehler.

### 3b. Zahlung zuordnen

Ein gebuchter Beleg ohne Kontoumsatz bleibt in der Bankansicht offen, und der Umsatz auch.
Prüfe den Bankvorschlag **vor** dem Speichern, denn das Speichern kann ihn übernehmen
(`docs/LEXOFFICE_UI.md`).

- Vorschlag passt (Lieferant, Betrag, Datum im Fenster −10 bis +5 Tage) → übernehmen.
- Vorschlag passt nicht → ablehnen **und** den passenden Umsatz selbst suchen: offene
  Kontoumsätze des Zeitraums mit gleichem Betrag (bei Fremdwährung: Belastung laut Bank) und
  passendem Empfänger.
- Genau ein Treffer → zuordnen, sofern die Freigabe des Laufs das deckt. Mehrere oder keiner
  → nicht raten; als `zuordnung_offen` mit den Kandidaten mitschreiben.

Was die Freigabe deckt, legt der Mensch einmal je Lauf fest (etwa „nur bei exaktem Betrag und
Lieferanten"). Frag das **vor** dem ersten Beleg, nicht beim ersten Treffer.

### 4. Mitschreiben — sofort, nicht am Ende

Hänge **nach jedem Beleg** eine Zeile an `.claude/buchhaltung-log/<zeitraum>/40-erfassung.jsonl`:

```
datei · lieferant · belegnummer · belegdatum · betrag · waehrung
behandlung · kategorie · regel
status      angelegt | bereits_vorhanden | uebersprungen | fehlgeschlagen
zuordnung   zugeordnet <umsatz> | zuordnung_offen <kandidaten> | keine_zahlung
beleg_id    Kennung im System
zeitpunkt
begruendung bei allem außer "angelegt"
```

Diese Datei ist der Wiederaufnahmepunkt. Bricht der Lauf ab — Sitzung abgelaufen, Fenster zu,
Kontext voll —, beginnt der nächste Durchgang mit genau den Belegen, die hier **nicht**
stehen. Sammelst du erst am Ende, ist nach einem Abbruch unklar, was passiert ist, und
jemand muss von Hand nachzählen.

## Sitzungsabbruch

Wirst du auf eine Anmeldemaske umgeleitet, **gib keine Zugangsdaten ein** (P-02). Halte an,
lass den Tab offen, sag Bescheid, prüfe nach der Rückmeldung den zuletzt begonnenen Beleg auf
Dublette und mach weiter.

## Was du nicht tust

- **Nicht übermitteln.** Keine Voranmeldung absenden, keine Freigabe erteilen, keinen Schritt
  tun, der eine Meldung an die Finanzverwaltung auslöst (P-01). Auch dann nicht, wenn die
  Oberfläche es als nächsten logischen Schritt anbietet.
- Keinen bestehenden Beleg löschen oder ändern, der nicht aus diesem Lauf stammt (P-03).
- Keine Originaldatei verschieben, umbenennen oder verändern (P-05).
- Keine Zahlung zuordnen, die nicht klassifiziert wurde.

## Rückgabe

```
Zeitraum <x>
Bestand vorher <n>, nachher <m>, Differenz <m-n> — erwartet <angelegt>

angelegt            <n>
bereits vorhanden   <n>
übersprungen        <n>  <Datei — Grund>
fehlgeschlagen      <n>  <Datei — Grund>

Nicht erfasst, weil blockiert: <Liste mit Gate und Grund>
```

Stimmt die Bestandsdifferenz nicht mit der Zahl der angelegten Belege überein, ist das das
wichtigste Ergebnis dieser Phase. Nenne es zuerst.
