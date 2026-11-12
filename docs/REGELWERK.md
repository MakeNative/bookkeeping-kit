# Regelwerk — Umsatzsteuer-Voranmeldung

```
REGELWERK_VERSION: 6
STAND: 2026-10
GELTUNG: Deutschland, Regelbesteuerung
```

Dieses Dokument ist die Entscheidungsgrundlage des `tax-classifier`. Es ist
**mandantenneutral** — keine Firmennamen, keine Kontonummern, keine Ordnerpfade. Alles
Mandantenspezifische steht in `COMPANY_CONTEXT.md` des jeweiligen Projekts.

> **Kein Steuerrat.** Das Regelwerk bildet die Praxis ab, die ein Buchhaltungsagent
> anwenden soll. Schwellenwerte und Pflichten ändern sich. Jede Regel mit
> `wert_pruefen: ja` muss gegen die aktuelle Rechtslage bestätigt werden, bevor sie
> produktiv greift. Im Zweifel entscheidet die Steuerkanzlei, nicht der Agent.

## Aufbau einer Regel

```
ID          Kurztitel
regel:      Was gilt.
gilt_ab:    JJJJ-MM-TT        gilt_bis: offen | JJJJ-MM-TT
pruefung:   Woran der Agent es erkennt.
folge:      Welche Kennziffer / welche Kategorie / welche Konsequenz.
wert_pruefen: ja|nein         # Schwellenwert gegen aktuelle Rechtslage bestätigen
```

Regeln werden nie gelöscht, nur mit `gilt_bis` geschlossen. Ein Lauf für einen
zurückliegenden Zeitraum verwendet die Regeln, die **damals** galten.

---

## G — Grundlagen

### G-01 Besteuerungsart wird ausgelesen, nie angenommen
- **regel:** Ob Soll- oder Ist-Versteuerung gilt, wird aus den Einstellungen des
  Buchhaltungssystems gelesen und in `COMPANY_CONTEXT.md` festgeschrieben.
- **pruefung:** Einstellungsseite des Systems. Fehlt die Angabe → Lauf stoppt.
- **folge:** Steuert G-02 und A-01. Eine falsche Annahme verschiebt die gesamte
  Umsatzseite eines Monats.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### G-02 Steuerentstehung
- **regel:** Bei **Soll**-Versteuerung entsteht die Umsatzsteuer mit Ablauf des Zeitraums,
  in dem die Leistung ausgeführt wurde. Bei **Ist**-Versteuerung mit Ablauf des Zeitraums,
  in dem das Entgelt **vereinnahmt** wurde.
- **pruefung:** Bei Ist: Zahlungseingang belegen, nicht das Rechnungsdatum verwenden.
- **folge:** Bei Ist gehören unbezahlte Ausgangsrechnungen **nicht** in den Zeitraum.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### G-03 Vorsteuerabzug ist nicht zahlungsabhängig
- **regel:** Der Vorsteuerabzug setzt eine ordnungsgemäße Rechnung und die ausgeführte
  Leistung voraus — auch beim Ist-Versteuerer, der seine Ausgangsumsätze nach Zahlung
  versteuert.
- **folge:** Eingangsrechnungen gehören in den Zeitraum des Rechnungseingangs, nicht der
  Zahlung.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### G-04 Maßgebliches Datum
- **regel:** Für die Zuordnung zählt das Rechnungs- bzw. Leistungsdatum auf dem Beleg.
  Bestelldatum, Lieferdatum der Ware und Zahlungsdatum sind **nicht** maßgeblich.
- **pruefung:** Datum aus dem Belegtext, nicht aus Dateiname, Bestellübersicht oder
  Kontoauszug.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### G-07 Numerische Datumsangaben sind mehrdeutig
- **regel:** Ein Datum der Form `09/01/2026` ist **nicht** auflösbar, ohne die Herkunft des
  Ausstellers zu kennen. Dasselbe Schriftbild bedeutet je nach Anbieter Tag/Monat oder
  Monat/Tag.
- **pruefung:** Belegt an zwei Rechnungen desselben Zeitraums: ein deutscher Anbieter
  schrieb `09/01/2026` für den 9. Januar, ein ausländischer `09/15/2026` für den 15. September.
  Eine Zahl über 12 an zweiter Stelle beweist Monat/Tag — darunter beweist nichts.
- **folge:** Bevorzuge in dieser Reihenfolge: ausgeschriebener Monat („September 28, 2026"),
  ISO (`2026-09-08`), deutsches Format mit Punkten (`28.09.2026`). Bleibt nur ein
  mehrdeutiges numerisches Datum, wird die Herkunft des Ausstellers herangezogen und das
  Ergebnis als `unsicher` markiert. Lässt sich die Mehrdeutigkeit nicht auflösen →
  `entscheidung_noetig`, nie raten.
- **zusatz:** Ein Beleg, dessen ermitteltes Datum außerhalb des Laufzeitraums liegt, aber
  dessen Dateiname oder Ablageort auf den Zeitraum deutet — und umgekehrt — ist immer ein
  Prüffall.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### G-08 Der Betrag steht am Label, nicht in der größten Zahl
- **regel:** Der Rechnungsbetrag wird an einem Betragslabel gelesen. „Die größte Zahl im
  Dokument" ist keine zulässige Näherung.
- **pruefung:** Belegt an zwei Fällen aus einem realen Lauf: eine Ausgangsrechnung trug die
  Auftragssumme größer als den Rechnungsbetrag, ein Hostingbeleg führte Einzelpositionen
  mehrerer Monate über dem Monatsbetrag. Beide Male hätte die Heuristik zu hoch gegriffen.
- **folge:** Zwei Stufen. Zuerst eindeutige Endbetragslabel (`Gesamtbetrag`,
  `Zu zahlender Betrag`, `Rechnungssumme`, `Zahlbetrag`, `Endbetrag`, `Amount due`,
  `Invoice total`). Nur wenn keines vorkommt, generisches `Total`/`Summe` — und dann das
  **letzte** Vorkommen, weil der Endbetrag am Belegende steht.
- **zusatz:** In Layout-Text stehen Label und Wert regelmäßig über 100 Spalten auseinander.
  Ein enges Suchfenster hinter dem Label findet den Wert nicht und liefert still `null`.
- **umbruch:** Steht hinter dem Label nichts mehr, ist der Wert in eine der **Folgezeilen**
  umgebrochen — oft mit einer Leerzeile dazwischen. Dort nachsehen, aber **nur** in diesem
  Fall: Steht hinter dem Label Fließtext („den Rechnungsbetrag buchen wir ab"), zieht ein
  Blick in die nächste Zeile beliebige fremde Zahlen an.
- **qualifizierte_label:** `Gesamtbetrag netto` ist nicht der Gesamtbetrag. Steht zwischen
  Label und erster Zahl ein einschränkendes Wort (`netto`, `net`, `excl.`, `ohne`), ist es
  eine Teilsumme und scheidet aus.
- **gegenprobe:** Netto + Steuer je Satz muss den gefundenen Betrag ergeben. Geht es nicht
  auf, ist der Betrag nicht bestätigt.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### G-10 Das Vorzeichen gehört zum Betrag
- **regel:** Eine Gutschrift, Stornorechnung oder Rückabwicklung trägt einen **negativen**
  Betrag. Das Vorzeichen ist Teil des Werts, nicht Zierde.
- **pruefung:** Negative Summen im Totalblock (`Gesamtbetrag netto: -156,64 €`) und/oder die
  Belegbezeichnung `Gutschrift`/`Stornorechnung` im Kopf. Der Betrag entscheidet, die
  Bezeichnung stützt: „Gutschrift" bezeichnet im Umsatzsteuerrecht auch die Abrechnung durch
  den Leistungsempfänger und ist für sich allein mehrdeutig.
- **folge:** `belegart: gutschrift`, Betrag mit Vorzeichen, Bemessungsgrundlage **mindernd**
  im Zeitraum der Änderung (A-03).
- **folge_fehler:** Ohne Vorzeichen wird die Gutschrift zur Ausgabe — der Fehler verdoppelt
  sich, weil der Betrag nicht nur fehlt, sondern mit falschem Vorzeichen hinzukommt.
- **belegt:** Mehrere Gutschriften eines Monats wurden als positive Eingangsrechnungen
  gelesen. Die Vorsteuer kehrte dadurch ihr Vorzeichen um, statt sich zu mindern.
- **auswahl:** Enthält eine Zeile mehrere Beträge, ist der betragsmäßig **größte** maßgeblich
  — mit erhaltenem Vorzeichen. Ein Maximum ohne Vorzeichenbetrachtung wählt bei Gutschriften
  die Null.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### G-11 Die Währung steht am Betrag, nicht im Dokument
- **regel:** Die Währung wird im **Umfeld des Gesamtbetrags** gelesen, nicht durch Suche nach
  einem Währungszeichen im Dokument.
- **pruefung:** Produktbezeichnungen enthalten Währungszeichen. Ein Buchtitel wie
  `$100 Muster-Titel` macht aus einer Euro-Rechnung eine Fremdwährungsrechnung.
- **folge_fehler:** Die Folge ist nicht nur ein falsches Feld: Der Beleg wandert in die
  Umrechnung (F-01), verlangt einen Kurs, den es nicht braucht, und blockiert den Lauf mit
  einer Frage, die auf einem Lesefehler beruht.
- **belegt:** Mehrere Inlandsrechnungen eines Monats wurden so zu Fremdwährungsbelegen und
  fielen zugleich aus der Summenbildung der Inlandsvorsteuer.
- gilt_ab: 2020-01-01 · wert_pruefen: nein


### G-09 Schreibweisen der USt-IdNr.
- **regel:** Die USt-IdNr. wird normalisiert gelesen: Großbuchstaben, ohne Punkte,
  Leerzeichen und Bindestriche.
- **pruefung:** Vorkommende Formen sind `DE123456789`, `BE 0123.456.789`, `EU123456789`
  und `EE VAT EE123456789` — bei der letzten steht ein Wort zwischen Präfix und Nummer.
- **folge:** Der Zahlenteil beginnt mit einer Ziffer; ein Muster, das das zulässt, verschluckt
  sonst das Wort `VAT`/`USt-IdNr.` und liefert einen unbrauchbaren Treffer. Das Präfix `EU`
  kennzeichnet nicht ansässige Anbieter im EU-Verfahren und ist **kein Drittland**.
- **folge_fehler:** Eine nicht erkannte USt-IdNr. führt den Beleg in die Drittlandsbehandlung
  — die Kennziffer wird falsch, obwohl der Betrag stimmt.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### G-05 Voranmeldungszeitraum und Frist
- **regel:** Monat oder Quartal gemäß Context. Abgabefrist ist der 10. Tag nach Ablauf des
  Zeitraums; mit Dauerfristverlängerung einen Monat später.
- **folge:** Bei Quartalsmeldung laufen alle Phasen über drei Monate; Zahlungszuordnung und
  Abgleich rechnen über den gesamten Zeitraum.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### G-06 Dauerfristverlängerung und Sondervorauszahlung
- **regel:** Bei Dauerfristverlängerung verschiebt sich die Frist um einen Monat. Die
  Sondervorauszahlung ist jährlich anzumelden und im letzten Voranmeldungszeitraum des
  Jahres anzurechnen.
- **pruefung:** `dauerfristverlängerung` im Context.
- gilt_ab: 2020-01-01 · wert_pruefen: ja

---

## E — Eingangsseite

### E-01 Inlandsleistung mit offenem Steuerausweis
- **regel:** Deutscher Lieferant mit deutscher USt-IdNr./Steuernummer und ausgewiesener
  Steuer → Vorsteuerabzug im Regelsatz oder ermäßigten Satz.
- **folge:** Vorsteuer in die Kennziffer für abziehbare Vorsteuer.
- **kein_default:** Ein inländischer Beleg **ohne** ausgewiesene Steuer ist keine
  Regelsatzleistung. Weist er 0 % aus, ist nichts abzuziehen — ein unterstellter Regelsatz
  erzeugt Vorsteuer, die nie berechnet wurde.
- **pruefung:** Nur ein Satz, zu dem ein Steuerbetrag **ungleich null** gehört, ist wirksam.
  Rechnungsvorlagen führen regelmäßig eine ermäßigte Zeile mit `0,00` mit, ohne dass ein
  ermäßigter Umsatz vorliegt.
- **belegt:** In einem realen Monat wies die Mehrheit der Inlandsbelege ausschließlich 0 % aus
  (Parkgebühren). Ein Default auf den Regelsatz hätte Vorsteuer aus dem Nichts gezogen —
  der einzige Fehlertyp in diesem Regelwerk, der nicht formell, sondern materiell ist.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### E-02 Steuersatz vom Beleg, mehrere Sätze getrennt
- **regel:** Bücher, Zeitschriften und Personenbeförderung unterliegen dem ermäßigten Satz.
  Buchhaltungssysteme schlagen häufig den Regelsatz vor.
- **pruefung:** Steuersatz **vom Beleg** übernehmen, nicht den Vorschlag bestätigen.
- **mehrere_saetze:** Trägt ein Beleg mehrere wirksame Sätze, wird er **je Satz getrennt**
  erfasst, nie auf einen Satz zusammengezogen. Zusammenziehen verschiebt die
  Bemessungsgrundlagen zwischen den Kennziffern, ohne die Summe zu verändern — und bleibt
  dadurch im Abgleich unsichtbar.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### E-03 Reverse Charge bei Leistungen aus dem EU-Ausland
- **regel:** Sonstige Leistung eines im EU-Ausland ansässigen Unternehmers an einen
  inländischen Unternehmer → Steuerschuldnerschaft des Leistungsempfängers.
- **pruefung:** Lieferant mit EU-USt-IdNr., 0 % ausgewiesen, Hinweis auf Reverse Charge
  bzw. Art. 196 MwStSystRL.
- **folge:** Bemessungsgrundlage und Steuer in die § 13b-Kennziffern, Vorsteuer in gleicher
  Höhe gegen — **zahllastneutral**.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### E-17 Ansässigkeit notfalls aus der Anschrift
- **regel:** Ob der Leistende im EU-Ausland oder im Drittland sitzt, entscheidet über E-03
  oder E-04. Fehlt eine USt-IdNr., ist die **Anschrift** auf dem Beleg heranzuziehen.
- **pruefung:** Anbieter außerhalb der EU führen regelmäßig gar keine USt-IdNr. Wer nur auf
  das Länderpräfix einer USt-IdNr. sieht, lässt die Zuordnung offen, obwohl sie im
  Adressblock steht.
- **folge:** Genau ein ermittelbares Nicht-Inlandsland → entsprechende Zuordnung. Mehrere
  oder keines → offen lassen und vorlegen; die Kennziffern unterscheiden sich, die Zahllast
  nicht.
- **vorsicht:** Die eigene Anschrift steht ebenfalls auf dem Beleg. Sie scheidet aus.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### E-04 Reverse Charge bei Drittlandsbezug
- **regel:** Wie E-03, aber Lieferant im Drittland → eigene Kategorie/Konto, getrennt von
  EU-Bezügen.
- **pruefung:** Sitz des Lieferanten, nicht die Währung der Rechnung.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### E-05 Innergemeinschaftlicher Erwerb
- **regel:** Warenlieferung aus einem anderen EU-Mitgliedstaat an einen inländischen
  Unternehmer mit USt-IdNr. → innergemeinschaftlicher Erwerb. Eigene Kategorie, **nicht**
  § 13b und **nicht** Inlandsvorsteuer.
- **pruefung:** Vermerk „steuerfreie innergemeinschaftliche Lieferung" bzw. Art. 138
  MwStSystRL, Versendungsland im EU-Ausland, 0 % ausgewiesen.
- **folge:** Erwerb mit dem für die Ware geltenden Satz versteuern (Regelsatz oder
  ermäßigt), Vorsteuer daraus in gleicher Höhe gegen — zahllastneutral.
- **satz_nicht_vom_beleg:** Der Beleg weist **0 %** aus — er enthält den deutschen
  Erwerbsteuersatz also gar nicht. Der Satz folgt aus der **Ware** (z. B. Bücher ermäßigt,
  Zubehör Regelsatz) und ist aus dem Dokument nicht ableitbar. Ein Default auf den Regelsatz
  ist deshalb keine Extraktion, sondern eine Erfindung.
- **folge_satz:** Satz offen lassen (`ig_erwerb_satz_offen`) und zur Entscheidung vorlegen,
  mit der Leistungsbeschreibung als Grundlage. Weder aus dem Dateinamen ableiten noch raten.
- **wirkung:** Ein falscher Satz bleibt zahllastneutral, weil Erwerbsteuer und Vorsteuer
  gegengleich laufen — aber die Kennziffern der Voranmeldung sind falsch. Das macht den
  Fehler leise und damit gefährlich.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### E-15 Reverse Charge ohne ausdrücklichen Hinweis
- **regel:** Die Steuerschuldnerschaft des Leistungsempfängers folgt aus dem **Sachverhalt**,
  nicht aus der Formulierung auf dem Beleg. Fehlt der Hinweis, ändert das die Behandlung
  nicht — es macht die Rechnung formell mangelhaft.
- **pruefung:** Die Konstellation statt des Wortlauts:
  1. Leistender ist nicht im Inland ansässig (ausländische USt-IdNr. oder Anschrift),
  2. der Beleg weist **keine deutsche Umsatzsteuer** aus,
  3. die **eigene USt-IdNr.** des Leistungsempfängers steht auf dem Beleg.
- **folge:** Reverse Charge wie E-03 (EU) bzw. E-04 (Drittland). Zusätzlich Hinweis auf den
  fehlenden Pflichtvermerk (E-07) — melden, nicht beanstanden, denn der Abzug hängt bei
  gegengleichen Positionen nicht daran.
- **grenze:** Lässt sich die Ansässigkeit des Leistenden nicht feststellen, ist die Zuordnung
  zu EU oder Drittland **offen** (`§13b_verdacht`) und wird vorgelegt. Die Kennziffern
  unterscheiden sich, die Zahllast nicht.
- **belegt:** In einem realen Monat trug ein Teil der Reverse-Charge-Belege keinen
  Hinweis — darunter einer von einem Lieferanten, dessen übrige Rechnungen desselben Monats
  ihn trugen. Eine Erkennung über den Wortlaut hätte sie als nicht abzugsfähige Ausgaben
  behandelt.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### E-16 Ein Lieferant, eine Behandlung
- **regel:** Derselbe Leistende im selben Zeitraum mit zwei verschiedenen Behandlungen ist
  ein Prüffall — ausnahmslos. Dasselbe gilt für zwei verschiedene Ansässigkeitsländer.
- **pruefung:** Belege nach Leistendem gruppieren und die Behandlungen je Gruppe vergleichen.
  Die Prüfung braucht kein Steuerwissen und kostet nichts.
- **gruppierung:** Der Schlüssel ist der **Lieferantenname**; die USt-IdNr. nur hilfsweise,
  wenn kein Name ermittelbar ist. Nicht umgekehrt.
- **warum:** Eine Prüfung, die auf einem Feld gruppiert, das **fehlen kann**, lässt genau die
  Fälle durch, die sie finden soll. Fehlt die USt-IdNr. auf einem Beleg, bildet dieser Beleg
  eine eigene Gruppe von eins — und eine Gruppe mit einem Element ist nie uneinheitlich. Der
  Prüfbericht meldet dann null Befunde und sieht aus wie ein Erfolg.
- **belegt:** Die Belege eines einzigen Lieferanten verteilten sich in einem Monat auf drei
  Behandlungen und zwei Länder. Die Prüfung meldete null Befunde, weil sie nach der USt-IdNr.
  gruppierte — und die stand nur auf einem von ihnen.
- **folge:** Abweichung melden. Entweder unterscheidet sich der Sachverhalt tatsächlich
  (dann ist die Begründung zu nennen), oder einer der Belege ist falsch eingestuft.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### E-18 Lieferanteneigenschaften gelten belegübergreifend
- **regel:** USt-IdNr. und Ansässigkeit sind Eigenschaften des **Lieferanten**, nicht des
  einzelnen Belegs. Trägt ein Beleg des Lieferanten sie, gelten sie für dessen übrige Belege
  mit — im selben Zeitraum und über Zeiträume hinweg via Lieferanten-Memory.
- **pruefung:** Anbieter drucken ihre Steuerregistrierung nicht auf jede Rechnung. Fehlt sie,
  ist das ein formeller Mangel (E-07) und kein anderer Sachverhalt.
- **folge:** Fehlende Angabe aus dem Lieferanten-Memory ergänzen, die Herkunft vermerken
  (`land_quelle: lieferant_memory`) und neu einordnen. Die Übernahme wird **ausgewiesen**,
  nie stillschweigend vorgenommen.
- **grenze:** Nur gleichrichtende Angaben übernehmen. Ein abweichender Betrag, ein anderes
  Datum oder eine andere Leistungsart werden nie ergänzt — nur, wer der Leistende ist.
- **belegt:** Ohne diese Regel wandern Belege desselben Anbieters je nach Druckbild in
  Drittland, EU und „kein Vorsteuerabzug" — mit unterschiedlichen Kennziffern bei identischem
  Sachverhalt.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### E-06 Marktplatzbelege einzeln lesen
- **regel:** Bei Plattformen mit Drittanbietern bestimmt der **jeweilige Verkäufer** das
  Steuerregime, nicht die Plattform. Jede Rechnung wird einzeln ausgewertet.
- **pruefung:** Verkäufer, dessen USt-IdNr., Versendungsland und Steuervermerk je Beleg.
- **folge:** Innerhalb einer Plattform können Inlandsumsatz, ig. Erwerb und Drittlandsbezug
  nebeneinander auftreten.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### E-07 Formelle Rechnungsanforderungen
- **regel:** Der Vorsteuerabzug setzt eine Rechnung mit den gesetzlichen Pflichtangaben
  voraus.
- **pruefung:** Vollständiger Name und Anschrift beider Parteien, Steuernummer oder
  USt-IdNr. des Leistenden, Ausstellungsdatum, fortlaufende Rechnungsnummer, Menge und
  Bezeichnung der Leistung, Entgelt, Steuersatz und Steuerbetrag bzw. Hinweis auf
  Steuerbefreiung.
- **folge:** Fehlt eine Pflichtangabe → `vorsteuerfaehig: nein` mit Benennung der fehlenden
  Angabe. Kein stillschweigender Abzug.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### E-08 Kleinbetragsrechnung
- **regel:** Unterhalb eines Gesamtbetrags-Schwellenwerts genügen erleichterte Angaben
  (Name und Anschrift des Leistenden, Ausstellungsdatum, Leistungsbeschreibung, Entgelt und
  Steuerbetrag in einer Summe, Steuersatz).
- **folge:** E-07 greift unterhalb der Schwelle nur eingeschränkt.
- **schwellenwert:** 250 EUR brutto
- gilt_ab: 2017-01-01 · wert_pruefen: ja

### E-09 Kein Vorsteuerabzug bei nicht abziehbaren Betriebsausgaben
- **regel:** Für Aufwendungen, die ertragsteuerlich nicht abziehbar sind, entfällt der
  Vorsteuerabzug. Bei Bewirtungsaufwendungen gilt die Einschränkung ertragsteuerlich nur
  anteilig, der Vorsteuerabzug bleibt bei ordnungsgemäßem Beleg dagegen in voller Höhe
  erhalten.
- **pruefung:** Geschenke oberhalb der Freigrenze, Repräsentation, private Mitveranlassung.
- **folge:** `vorsteuerfaehig: nein` bzw. anteilig, mit Begründung.
- **schwellenwert Geschenke:** je Empfänger und Jahr — Betrag gegen aktuelle Rechtslage
  prüfen
- gilt_ab: 2020-01-01 · wert_pruefen: ja

### E-10 Belege ohne Steuerausweis und ohne Reverse-Charge-Hinweis
- **regel:** Fehlen sowohl ein Steuerausweis als auch ein Reverse-Charge-Hinweis und die
  USt-IdNr. des Empfängers, ist weder Vorsteuerabzug noch § 13b begründbar.
- **folge:** Als Betriebsausgabe ohne Steuer erfassen, Begründung dokumentieren, Lieferant
  zur Korrektur der Rechnungsdaten vormerken.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### E-11 Guthabenaufladungen sind keine Belege
- **regel:** Vorauszahlungen auf ein Guthabenkonto (Werbekonten, Prepaid-Dienste) sind
  keine Leistungsabrechnung. Maßgeblich ist die periodische Rechnung des Anbieters.
- **folge:** Zahlung nicht als Beleg führen; die zugehörige Rechnung in der Soll-Liste
  erwarten.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### E-12 Verspätet ausstellende Anbieter
- **regel:** Anbieter, die erst im Folgemonat abrechnen, erzeugen im Zeitraum eine Lücke,
  die kein Fehler ist.
- **folge:** Status `noch_nicht_ausgestellt` statt `fehlt`; Eintrag ins Offene-Punkte-Register.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### E-13 Belege fremder Gesellschaften
- **regel:** Rechnungen, die auf eine andere Gesellschaft lauten oder deren Leistung einer
  anderen Gesellschaft zuzurechnen ist, werden nicht erfasst — auch wenn die
  Zahlungsbestätigung im eigenen Postfach landet.
- **pruefung:** Rechnungsadressat und, bei Portalen, die Organisation im Anbieterkonto.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### E-14 Rechnungen auf eine natürliche Person
- **regel:** Belege, die auf eine Privatperson statt auf das Unternehmen lauten, werden
  markiert und nicht stillschweigend gebucht.
- **folge:** Entscheidungsvorlage; parallel Hinweis, die Rechnungsdaten beim Anbieter zu
  korrigieren.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

---

## A — Ausgangsseite

### A-01 Umsatz bei Ist-Versteuerung
- **regel:** Der Ausgangsumsatz zählt im Zeitraum des Zahlungseingangs. Unbezahlte
  Rechnungen bleiben außen vor.
- **pruefung:** Offene-Posten-Liste des Buchhaltungssystems gegen die Ausgangsrechnungen
  des Zeitraums abgleichen.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### A-02 Stornoketten auflösen
- **regel:** Wird eine Rechnung storniert und ersetzt, darf nur die wirksame Rechnung in die
  Bemessungsgrundlage eingehen.
- **pruefung:** Ersatzrechnungen verweisen im Fließtext auf die stornierte Nummer. Der
  Nummernkreis wird zusätzlich auf Lücken geprüft.
- **folge:** Liegt die stornierte Rechnung in einem bereits gemeldeten Zeitraum, ist die
  Berichtigung im Zeitraum der Änderung vorzunehmen.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### A-03 Änderung der Bemessungsgrundlage
- **regel:** Skonto, Teilzahlung, Gutschrift, Rückabwicklung und uneinbringliche Forderungen
  ändern die Bemessungsgrundlage im Zeitraum der Änderung, nicht rückwirkend.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### A-04 Anzahlungen und Teilrechnungen
- **regel:** Teil- und Schlussrechnungen werden getrennt betrachtet. Bei Ist-Versteuerung
  ist jede vereinnahmte Teilzahlung ein eigener Entstehungszeitpunkt.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### A-05 Zusammenfassende Meldung
- **regel:** Innergemeinschaftliche Lieferungen und sonstige Leistungen an Unternehmer in
  anderen EU-Staaten sind zusätzlich in der Zusammenfassenden Meldung zu erklären. Diese
  ist von der Voranmeldung getrennt.
- **pruefung:** Ausgangsrechnung mit ausländischer USt-IdNr. des Kunden.
- **folge:** Hinweis im Abgleich; die Meldung selbst gehört nicht in den Automatisierungsumfang.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

---

## F — Fremdwährung

### F-01 Umrechnung
- **regel:** Fremdwährungsbeträge werden nach einem zulässigen, nachvollziehbar
  dokumentierten Kurs umgerechnet. Zulässig sind der amtlich veröffentlichte
  Durchschnittskurs des Monats oder — praxisüblich und belegbar — der tatsächliche
  Abrechnungskurs des Zahlungsdienstleisters.
- **pruefung:** Kursquelle und Betrag müssen aus einem Beleg oder einer
  Zahlungsbenachrichtigung stammen. Geschätzte Kurse sind unzulässig.
- **folge:** Kurs, Quelle und Ursprungsbetrag im Beschreibungsfeld des Belegs dokumentieren.
- gilt_ab: 2020-01-01 · wert_pruefen: ja

### F-02 Wirkung bei Reverse Charge
- **regel:** Bei zahllastneutralen Sachverhalten (§ 13b, ig. Erwerb) wirkt der
  Umrechnungsbetrag nur auf die Bemessungsgrundlage, nicht auf die Zahllast.
- **folge:** Entschärft F-01 in der Priorität, hebt die Dokumentationspflicht aber nicht auf.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

---

## B — Belegqualität

### B-01 Belegerkennung ist nicht vertrauenswürdig
- **regel:** Automatisch erkannte Felder (Belegtyp, Betrag, Datum, Lieferant) werden gegen
  das Dokument geprüft, bevor sie übernommen werden.
- **pruefung:** Jedes übernommene Feld muss im Dokument auffindbar sein.
- **folge:** Abweichung → Beleg blockiert, Entscheidungsvorlage.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### B-02 Nicht jedes Dokument ist ein Beleg
- **regel:** Gesellschafterbeschlüsse, Verträge, Mahnungen, Lieferscheine,
  Auftragsbestätigungen und Zahlungsbestätigungen sind keine Rechnungen.
- **folge:** Aus der Belegliste entfernen und in der Dokumentenablage führen. Besonders
  kritisch, wenn die Erkennung daraus eine Einnahme gemacht hat.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### B-03 Strukturierte Rechnungen bevorzugen
- **regel:** Liegt eine Rechnung strukturiert vor (XRechnung, ZUGFeRD, Peppol), werden die
  Steuerdaten daraus gelesen, nicht aus dem Sichtbeleg.
- gilt_ab: 2025-01-01 · wert_pruefen: ja

### B-04 Firmierungshistorie
- **regel:** Eine frühere Firmierung auf einer Rechnung macht den Beleg nicht ungültig,
  solange die Rechtsperson identisch ist.
- **folge:** Beleg buchen, Lieferant zur Stammdatenänderung vormerken.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### B-06 Eine Datei ist nicht ein Beleg
- **regel:** Eine PDF-Datei kann **mehrere eigenständige Rechnungen** enthalten — je mit
  eigener Rechnungsnummer, eigenem Datum und eigenem Betrag. Jede davon ist ein eigener
  Beleg und wird einzeln erfasst.
- **pruefung:** Kommt im Dokument mehr als eine **verschiedene** Rechnungsnummer vor, ist es
  eine Sammeldatei. Zerlege sie an den Rechnungsnummern und werte jeden Teil für sich aus.
  Seitenzahl allein beweist nichts: eine Rechnung kann mehrseitig sein, und mehrere
  Rechnungen können auf einer Seite stehen.
- **folge_fehler:** Wer die Datei als einen Beleg liest, erfasst willkürlich **einen** der
  Vorgänge und verliert die übrigen — ohne Fehlermeldung, weil ein Betrag ja gefunden wurde.
- **belegt:** In einem realen Monat bündelte eine Marktplatzdatei mehrere Rechnungen.
  Gelesen wurde nur eine — die zufällig letzte und zugleich betragsmäßig kleinste. Der
  größte Teil von Bemessungsgrundlage und Vorsteuer fiel lautlos aus dem Lauf.
- **dubletten:** Der Dublettenschlüssel ist dann **Dateihash plus Rechnungsnummer**. Über den
  Dateihash allein gelten die Teile einer zerlegten Sammeldatei fälschlich als Dubletten
  voneinander.
- **zeitraum:** Die Teile können verschiedene Rechnungsdaten tragen und damit in verschiedene
  Voranmeldungszeiträume fallen. Das Datum wird je Teil bestimmt, nie für die Datei.
- gilt_ab: 2020-01-01 · wert_pruefen: nein
### B-07 Das Datum steht am Label, aber selten daneben
- **regel:** Wie beim Betrag (G-08) sind Label und Wert getrennt: als **Spaltenkopf** mit der
  Wertzeile darunter (`Rechnungs-/Lieferdatum` über der Datenzeile) oder durch Zeilenumbruch.
- **pruefung:** Trägt die Labelzeile kein Datum, in den folgenden nicht leeren Zeilen
  nachsehen. Zusätzlich zu beachten: Ordinalzahlen (`Mar 11th 2026`) und ISO-Angaben mit
  einstelligem Monat (`2026-6-29`).
- **folge:** Findet sich über Label nichts, das **ganze Dokument** absuchen und das Ergebnis
  als `unsicher` kennzeichnen — ein unsicheres Datum ist weit besser als keines.
- **kein_stilles_verwerfen:** Ein Beleg ohne bestimmbares Datum ist **nicht** „außerhalb des
  Zeitraums", sondern ungeprüft. Er wird als `datum_unbestimmt` gemeldet und ist blockierend.
  Ein Zeitraumfilter, der ihn stillschweigend überspringt, verliert ihn für immer: Der
  nächste Lauf sucht einen anderen Monat und kommt nie auf ihn zurück.
- **belegt:** Zahlreiche Belege eines Jahres trugen Datumsangaben, die keine Labelzeile enthielt.
  Darunter waren Belege zweier bereits geprüfter Monate — gefunden erst, als der Filter sie
  melden musste statt sie zu überspringen.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

### B-05 Belege ohne Textebene fallen durch jeden Filter
- **regel:** Ein Foto oder Scan ohne Textebene liefert kein Datum. Damit greift der
  Zeitraumfilter nicht, und der Beleg verschwindet lautlos aus dem Lauf — er wird weder
  aufgenommen noch verworfen, sondern übersehen.
- **pruefung:** `pdftotext -layout` gibt nichts oder fast nichts zurück; `pdffonts` zeigt
  keine eingebetteten Schriften.
- **folge:** Nicht lesbare Belege sind **blockierend** für den Monatslauf, bis sie als Bild
  gelesen wurden. Sie dürfen nie als „nicht im Zeitraum" gewertet werden — der Lauf weiß das
  nicht, er hat nur nichts gefunden.
- **zusatz:** Das Ablagedatum der Datei grenzt ein, aber nur in eine Richtung: ein Beleg kann
  nicht vor seinem Rechnungsdatum abgelegt worden sein. Liegt die Ablage vor dem Zeitraum,
  ist der Beleg sicher nicht aus dem Zeitraum. Umgekehrt beweist sie nichts.
- gilt_ab: 2020-01-01 · wert_pruefen: nein

---

## P — Prozess

### P-01 Keine Übermittlung
- **regel:** Die Voranmeldung wird vorbereitet, nie abgesendet. Die Übermittlung ist
  ausschließlich eine Handlung des Menschen.
- gilt_ab: immer · wert_pruefen: nein

### P-02 Keine Zugangsdaten
- **regel:** Agenten geben keine Zugangsdaten ein. Logins erfolgen durch den Menschen.
- gilt_ab: immer · wert_pruefen: nein

### P-03 Keine Löschungen
- **regel:** Belege und Belegdatensätze werden nicht durch einen automatisierten Lauf
  gelöscht. Löschen ist ein eigener, manuell angestoßener und einzeln freigegebener Vorgang.
- gilt_ab: immer · wert_pruefen: nein

### P-04 Keine Doppelbuchung
- **regel:** Vor dem Anlegen eines Belegs wird gegen den Bestand geprüft. Dedup-Schlüssel:
  Lieferant, Belegnummer, Belegdatum, Bruttobetrag.
- **folge:** Treffer → überspringen und als `bereits_vorhanden` protokollieren.
- gilt_ab: immer · wert_pruefen: nein

### P-05 Originalbelege bleiben unverändert
- **regel:** Aufbewahrungspflichtige Belege werden nicht verändert oder umbenannt. Sprechende
  Namen entstehen über eine Zuordnungsdatei, jede Bewegung wird protokolliert.
- gilt_ab: immer · wert_pruefen: nein

### P-06 Vollständigkeit über Zahlungen, nicht über den Ordner
- **regel:** Die Erwartungsliste eines Zeitraums speist sich aus den Zahlungsvorgängen und
  den bekannten wiederkehrenden Lieferanten — nicht aus dem, was zufällig im Ordner liegt.
- gilt_ab: immer · wert_pruefen: nein

### P-07 Jede Klassifikation nennt ihre Regel
- **regel:** Jeder klassifizierte Beleg trägt die ID der angewandten Regel. Ohne Regelbezug
  keine Erfassung.
- **folge:** Ermöglicht Audit, Eval und die Begründung gegenüber der Steuerkanzlei.
- gilt_ab: immer · wert_pruefen: nein

---

## Kennziffern-Zuordnung

Die konkreten Kennziffern der Voranmeldung und die Kategoriebezeichnungen des
Buchhaltungssystems stehen in `COMPANY_CONTEXT.md` bzw. in der Systemdokumentation
(`LEXOFFICE_UI.md` für lexoffice), weil sie system- und formularabhängig sind.

Fachliche Zuordnung:

| Sachverhalt | Regel | Wirkung auf die Zahllast |
|---|---|---|
| Inlandsumsatz | A-01 | erhöht |
| Inlandsvorsteuer | E-01, E-02 | mindert |
| § 13b EU / Drittland | E-03, E-04 | neutral (Steuer und Vorsteuer gegengleich) |
| Innergemeinschaftlicher Erwerb | E-05 | neutral |
| Ohne Vorsteuerabzug | E-09, E-10 | keine |

---

## Änderungshistorie

| Version | Datum | Änderung |
|---|---|---|
| 1 | 2026-10 | Erstfassung, abgeleitet aus einem realen Monatslauf |
| 2 | 2026-10 | G-07 ergänzt sowie G-08, G-09, B-05 und E-05 `satz_nicht_vom_beleg` aufgenommen — alle vier aus Befunden eines Trockenlaufs gegen einen bereits gebuchten Monat |
| 3 | 2026-10 | Zweiter Trockenlauf gegen einen anderen Monat: E-15 (Reverse Charge ohne Hinweis) und E-16 (ein Lieferant, eine Behandlung) neu; E-01 um das Verbot des Regelsatz-Defaults, E-02 um die getrennte Erfassung mehrerer Sätze und G-08 um Zeilenumbruch und qualifizierte Label erweitert |
| 4 | 2026-10 | B-06 aufgenommen: eine Datei kann mehrere Rechnungen enthalten. Gefunden beim Wiederholungslauf desselben Monats — eine Sammeldatei mit mehreren Rechnungen wurde als ein Beleg gelesen |
| 5 | 2026-10 | Nachlauf zum zweiten Monat: G-10 (Vorzeichen/Gutschrift), B-07 (Datum am Label, nie stilles Verwerfen) und E-17 (Ansässigkeit aus der Anschrift) aufgenommen |
| 6 | 2026-10 | Dritter Monat: E-18 (Lieferanteneigenschaften gelten belegübergreifend) und G-11 (Währung am Betrag) neu; E-16 um die Wahl des Gruppierungsschlüssels geschärft — eine Prüfung, die auf einem Feld gruppiert, das fehlen kann, meldet null Befunde |
