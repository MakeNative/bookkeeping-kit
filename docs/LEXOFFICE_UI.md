# lexoffice / Lexware Office — Bedienhinweise

Systemwissen für die `record`-Skill. Gilt für jeden Mandanten, der lexoffice nutzt —
deshalb plugin-seitig und nicht im Mandantenkontext.

Stand: 2026-10. Beobachtet an `app.lexware.de`.

---

## Reverse Charge läuft über die Kategorie, nicht über den Steuersatz

Das Feld **Steuer** kennt nur `19 %`, `7 %` und `Keine`. Es gibt dort **keine**
Reverse-Charge-Option. Die Steuerschuldnerschaft wird über die **Kategorie** gesteuert.

Im Kategorie-Suchfeld `13b` eintippen → es erscheinen die § 13b-Kategorien, jeweils in einer
EU- und einer Drittland-Variante. Beobachtete Liste (alphabetisch):

```
Bauleistungen §13b
Beratung §13b                      Beratung §13b Drittland
Fortbildung §13b                   Fortbildung §13b Drittland
Fremdleistungen §13b               Fremdleistungen §13b Drittland
Lizenzen und Konzessionen §13b     Lizenzen und Konzessionen §13b Drittland
...
```

Jede § 13b-Kategorie behält das Aufwandskonto ihrer Normalvariante — der Wechsel von
„Lizenzen und Konzessionen" auf „Lizenzen und Konzessionen §13b" ändert also nur die
Steuerbehandlung, nicht die Kontierung.

Nach der Auswahl blendet lexoffice einen Hinweis ein:

> **Reverse Charge Verfahren** — Erfasse im Feld Gesamtbetrag den Rechnungsbetrag. Der
> Steuerbetrag wird intern für den Ausweis in der Umsatzsteuer-Voranmeldung hinzugerechnet
> aber nicht angezeigt.

Das Feld **Steuer** springt dabei auf `19 %`, und im Feld **Gesamtbetrag** bleibt der
**Rechnungsbetrag** stehen — nicht Betrag plus Steuer.

## Innergemeinschaftlicher Erwerb ist eine eigene Kategorie

Suchbegriff `erwerb` → **„Innergemeinschaftlicher Erwerb"**. Eine einzige Kategorie, die alle
Sätze abdeckt; der Satz wird anschließend im Feld **Steuer** gewählt (dort stehen dann nur
`19 %` und `7 %` zur Auswahl). Gleicher Hinweistext wie bei § 13b, gleiche Logik:
Rechnungsbetrag eintragen, Steuer wird intern ergänzt.

Das ist **nicht** § 13b und **nicht** Inlandsvorsteuer — eine dritte Kategorie.

## Pflichtfelder

**Belegnummer ist Pflicht.** Belege ohne Rechnungsnummer (Zahlungsbestätigungen, Receipts)
lassen sich sonst nicht speichern. Behelf: die Transaktions-ID des Belegs verwenden und die
Herkunft im Beschreibungsfeld dokumentieren.

## Vorbelegungen sind oft falsch

- Der vorgeschlagene Steuersatz ist regelmäßig `19 %`, auch bei Büchern und
  Personenbeförderung (→ Regelwerk E-02).
- Der Belegtyp wird bei Zahlungsbestätigungen gelegentlich als **Einnahme** statt Ausgabe
  erkannt.
- Beträge und Belegdaten werden mitunter frei erfunden, wenn das Dokument keine Rechnung ist.

Jedes vorbelegte Feld gegen das Dokument prüfen (→ Regelwerk B-01).

## Der Beleg-Editor ist ein eigenes Fenster

Das wirkt sich auf die Automatisierung aus:

- Die Zugänglichkeitsstruktur der Seite zeigt den Editor **nicht** — Element-Referenzen
  greifen dort nicht, nur Koordinaten.
- Die Fenstergeometrie driftet. Screenshots kommen mal 1:1, mal verkleinert zurück. **Vor
  jedem Klick ein frischer Screenshot**, Koordinaten daraus ableiten, Ergebnis verifizieren.
- Ein über dem Fenster liegender Dialog kann den Speichern-Button verdecken. Reagiert
  Speichern nicht, ist das die wahrscheinlichste Ursache.
- Nach Auswahl einer § 13b- oder Erwerb-Kategorie schiebt der Hinweiskasten alle darunter
  liegenden Felder nach unten — Koordinaten danach neu bestimmen.
- Speichern greift nicht immer beim ersten Klick. Nach dem Klick prüfen, ob der Zähler
  („Beleg x von y") gesunken ist; sonst wiederholen.

## Navigation im Belegstapel

„Speichern + nächster Beleg" rückt im gefilterten Stapel vor. Die Pfeile oben rechts
blättern **ohne** zu speichern — der richtige Weg, um einen Beleg zu überspringen.

## Anmeldung kann unbemerkt ablaufen

Der Aufruf von `app.lexoffice.de` kann auf die Lexware-Anmeldemaske umleiten, obwohl die
Sitzung als aktiv galt. **Nach jeder Navigation prüfen**, ob eine Anmeldemaske sichtbar ist,
bevor geklickt wird.

## PDF-Anzeige im Browser

Manche Portale (z. B. Händler-Rechnungen) öffnen PDFs im Chrome-Viewer statt sie
herunterzuladen. Die Toolbar dieses Viewers gehört **nicht** zur Webseite und ist für
Automatisierung nicht erreichbar. Abhilfe: in Chrome unter
`chrome://settings/content/pdfDocuments` auf „PDFs herunterladen" umstellen.

## Upload

Die Belegliste nimmt Dateien per Datei-Eingabefeld entgegen — PDF, JPEG, PNG **und XML**.
Der XML-Pfad ist für strukturierte E-Rechnungen der verlässlichere (→ Regelwerk B-03).
Mehrere Dateien gleichzeitig sind möglich und deutlich schneller als einzeln.

## Bankvorschläge beim Speichern

Zeigt der Beleg-Editor einen Bankvorschlag an, **übernimmt das Speichern ihn**, ohne eigene
Rückfrage. Der Vorschlag kann falsch sein: beobachtet wurde eine Amazon-Zahlung als Vorschlag
für eine Sortlist-Rechnung gleichen Betrags. Den richtigen Umsatz schlägt das System dann
nicht vor; er bleibt in der Bankansicht offen. Deshalb Vorschlag vor dem Speichern prüfen und
den passenden Umsatz notfalls selbst suchen (→ `record`, Schritt 3b).

## Was nicht geht

Kein Verschieben eines Belegs aus der Belegliste in eine reine Dokumentenablage. Für
Dokumente, die keine Belege sind (→ B-02), bleibt nur: liegen lassen oder löschen. Löschen
ist ein manueller, einzeln freizugebender Vorgang (→ P-03).
