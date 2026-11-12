# Lieferanten — Erkennungsmuster

Dieses Dokument enthält **keine Anbieternamen**. Es beschreibt, **woran** ein Lieferantentyp
erkannt wird. Die konkrete Lieferantentabelle eines Unternehmens entsteht bei
`/bookkeeping-kit:adopt` aus dessen eigenen Belegen und liegt ausschließlich mandantenseitig
in `.claude/docs/COMPANY_CONTEXT.md`.

> **Warum keine Namensliste im Plugin.** Welche Dienste ein Unternehmen einkauft, ist eine
> Aussage über dieses Unternehmen — Infrastruktur, Werkzeuge, Größenordnung. Eine solche
> Liste gehört nicht in ein wiederverwendbares, womöglich öffentliches Repository.

---

## Muster

### M-01 EU-Dienstleister mit Reverse Charge
**Erkennung:** USt-IdNr. des Leistenden beginnt mit einem EU-Länderkürzel (nicht DE) ·
0 % ausgewiesen · Hinweistext auf Steuerschuldnerschaft des Leistungsempfängers bzw.
Art. 196 MwStSystRL · eigene USt-IdNr. auf der Rechnung abgedruckt.
**Behandlung:** § 13b EU → Regel E-03. Zahllastneutral.
**Typische Vertreter:** Software-Abonnements, Cloud- und Werbedienste, die über eine
europäische Konzerngesellschaft abrechnen.

### M-02 Drittlandsdienstleister mit Reverse Charge
**Erkennung:** Sitz des Leistenden außerhalb der EU · 0 % · Reverse-Charge-Hinweis.
**Behandlung:** § 13b Drittland → Regel E-04.
**Fallstrick:** Die Rechnungswährung sagt nichts über den Sitz. Maßgeblich ist die
abrechnende Gesellschaft, nicht der Markenname — viele US-Marken rechnen über eine
irische oder luxemburgische Tochter ab und sind dann M-01.

### M-03 Inländischer Anbieter
**Erkennung:** Deutsche USt-IdNr. oder Steuernummer · offener Steuerausweis.
**Behandlung:** Inlandsvorsteuer → Regel E-01, Satz vom Beleg übernehmen (E-02).

### M-04 Marktplatz mit Drittanbietern
**Erkennung:** Bestellplattform, aber als Verkäufer steht ein Dritter auf der Rechnung.
**Behandlung:** `pro_rechnung_pruefen` → Regel E-06. Innerhalb eines Monats können
Inlandsumsatz, innergemeinschaftlicher Erwerb und Drittlandsbezug nebeneinander auftreten —
auch plattformeigene Gesellschaften rechnen aus verschiedenen Ländern ab.
**Nie** vom Plattformnamen auf das Steuerregime schließen.

### M-05 Innergemeinschaftlicher Erwerb
**Erkennung:** Warenlieferung · Versendungsland im EU-Ausland · 0 % · Vermerk „steuerfreie
innergemeinschaftliche Lieferung" bzw. Art. 138 MwStSystRL.
**Behandlung:** eigene Kategorie → Regel E-05. Weder § 13b noch Inlandsvorsteuer.

### M-06 Beleg ohne belastbaren Steuerausweis
**Erkennung:** Zahlungsbestätigung oder „Receipt" statt Rechnung · keine USt-IdNr. des
Empfängers · kein Reverse-Charge-Hinweis · allgemeine Floskel wie „VAT paid where applicable".
**Behandlung:** kein Vorsteuerabzug → Regel E-10. Begründung dokumentieren, Lieferant zur
Korrektur der Rechnungsdaten vormerken.

### M-07 Prepaid-/Guthabenmodell
**Erkennung:** Zahlungen sind Aufladungen eines Guthabenkontos; die Leistungsabrechnung
erfolgt periodisch und getrennt.
**Behandlung:** Aufladung ist kein Beleg → Regel E-11. Die periodische Rechnung erwarten.

### M-08 Verspätet abrechnender Anbieter
**Erkennung:** Rechnung für einen Zeitraum erscheint erst im Folgemonat, oft an einen
Werktag gebunden.
**Behandlung:** Status `noch_nicht_ausgestellt` → Regel E-12, Eintrag ins
Offene-Punkte-Register.

### M-09 Anbieter mit mehreren Rechnungen je Zeitraum
**Erkennung:** Mehrere Belege pro Monat, nicht jeder löst eine Zahlungsbenachrichtigung aus
(Sammellastschrift, Guthabenverrechnung).
**Behandlung:** Erwartungsliste aus dem Anbieterportal ziehen, nicht aus den
Zahlungsmeldungen → Regel P-06.

### M-10 Fremdbeleg
**Erkennung:** Rechnungsadressat oder Portal-Organisation gehört zu einer anderen
Gesellschaft, obwohl die Benachrichtigung im eigenen Postfach landet.
**Behandlung:** nicht erfassen → Regel E-13. In die Ausschlussliste des Mandanten aufnehmen.

---

## Zugangsmuster

| Muster | Erkennung | Folge für den Context |
|---|---|---|
| Portal ohne Login erreichbar | Zielseite lädt mit Inhalt | `login: nein` |
| Portal mit Login | Redirect auf Anmeldemaske | `login: ja` — Mensch loggt ein |
| Browser-Erweiterung blockt die Domain | Navigation wird abgelehnt | `domain_freigabe_noetig: ja` — **kein** Login-Problem |
| Zweiter Faktor / Passkey-Pflicht | Anbieter kündigt Pflicht an oder erzwingt sie | `nur_manuell: ja` |
| PDF öffnet im Browser-Viewer statt als Download | Viewer-Toolbar erscheint | Browser auf „PDFs herunterladen" umstellen |

---

## Was `adopt` daraus macht

`adopt` liest die Belege der letzten zwölf Monate, gruppiert nach Lieferant, ordnet jedem
ein Muster zu und schreibt das Ergebnis in `COMPANY_CONTEXT.md` — mit Beleg-Quelle,
Login-Bedarf und Besonderheiten. Je Lieferant werden genau zwei Dinge erfragt, die sich nicht
aus dem Beleg ergeben: **wo die Rechnung liegt** und **ob ein Login nötig ist**.

Der `tax-classifier` bestätigt die Zuordnung bei jedem Lauf am konkreten Beleg
(Regel B-01) und hält im Mandantenkontext fest, wann sie zuletzt bestätigt wurde. Anbieter
wechseln ihre Abrechnungsgesellschaft — ein einmal gesetztes Muster ist eine Vermutung, kein
Dauerzustand.
