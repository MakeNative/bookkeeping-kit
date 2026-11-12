---
name: correction
description: "Bereitet die Berichtigung einer bereits übermittelten Voranmeldung vor: ermittelt Altstand und Neustand je Kennziffer, stellt die Differenz dar und bewertet, ob berichtigt werden muss. Übermittelt nichts. Triggers on: /buchhaltung-kit:correction <YYYY-MM>"
disable-model-invocation: true
argument-hint: "<YYYY-MM>"
---

Ein Zeitraum ist übermittelt, und es stellt sich heraus, dass etwas fehlte oder falsch war.

Das ist steuerlich kein Routinevorgang. Ob berichtigt werden **muss**, ob es eine Anzeige nach
der Abgabenordnung auslöst und wie das Zusammenspiel mit der Jahreserklärung aussieht, ist
eine Frage an den Steuerberater — nicht an dich.

**Du bereitest vor und rechnest. Du entscheidest nicht, und du übermittelst nicht** (P-01).

## Schritt 1 — Altstand sichern

**Bevor irgendetwas angefasst wird.** Ist die übermittelte Fassung erst überschrieben, lässt
sie sich oft nicht wiederherstellen, und dann ist die Differenz nicht mehr belegbar.

Nach `.claude/buchhaltung-log/<zeitraum>/70-korrektur.md`, Abschnitt „Altstand":

```
übermittelt am <datum>
je Kennziffer: <kz> | <basis> | <steuer>
Zahllast <betrag>
Quelle: <wo abgelesen — Übermittlungsprotokoll, Elster-Abruf, Systemansicht>
```

Findest du die übermittelte Fassung nicht mehr, ist das ein Befund und kein Grund
weiterzumachen. Eine Korrektur ohne gesicherten Altstand ist nicht prüfbar.

## Schritt 2 — Anlass benennen

Was genau hat sich geändert, und seit wann war es bekannt?

| Anlass | typisch |
|---|---|
| Beleg fehlte | Rechnung tauchte später auf, gehört aber in den Zeitraum |
| Beleg falsch klassifiziert | Reverse Charge als Inlandsvorsteuer o. ä. |
| Beleg gehörte nicht dazu | Fremdbeleg (E-13), Nichtbeleg (B-02), Dublette (P-04) |
| Bemessungsgrundlage geändert | Storno, Gutschrift, Entgeltminderung (A-03) |
| Regelwerksänderung | eine Regel galt rückwirkend anders |

Der letzte Fall ist gesondert zu behandeln: Prüfe `gilt_ab` der betroffenen Regel. Eine Regel,
die erst **nach** dem Zeitraum gilt, begründet keine Korrektur des Zeitraums.

## Schritt 3 — Neustand rechnen

Vollständig neu aus den Belegen, nicht als Delta auf den Altstand. Ein Delta übernimmt jeden
Fehler, der schon in der ersten Fassung steckte, ungeprüft.

Lass dafür `check-return` über den berichtigten Belegbestand laufen.

## Schritt 4 — Differenz darstellen

```
Kennziffer | alt (basis/steuer) | neu (basis/steuer) | Differenz
...
Zahllast alt <x> · neu <y> · Differenz <z>
Richtung: Nachzahlung | Erstattung | unverändert
```

**Zahllastneutrale Korrekturen ausdrücklich kennzeichnen.** Verschiebt sich nur die Aufteilung
zwischen gegengleichen Kennziffern — etwa beim innergemeinschaftlichen Erwerb zwischen
Regelsatz und ermäßigtem Satz —, ändert sich die Zahllast um null. Die Voranmeldung war
trotzdem falsch. Beides gehört nebeneinander in den Bericht, weil es die Dringlichkeit
bestimmt, nicht die Notwendigkeit.

## Schritt 5 — Vorlage, keine Handlung

Schreibe `70-korrektur.md` zu Ende und lege vor:

```
Zeitraum <x>, übermittelt am <datum>
Anlass: <beschreibung>
Differenz je Kennziffer: <tabelle>
Zahllastwirkung: <betrag> (<nachzahlung|erstattung|keine>)
Betroffene Belege: <liste mit Regel-ID>

Zur Entscheidung durch Steuerberater oder Nutzer:
  - berichtigte Voranmeldung abgeben?
  - Zeitpunkt und Form?
  - Auswirkung auf Folgezeiträume?

Es wurde nichts übermittelt und nichts berichtigt.
```

Dann halte an. Auch wenn die Sache eindeutig aussieht und der Betrag klein ist.

## Was du änderst — und was nicht

Einen **falsch erfassten Beleg** im System zu berichtigen ist zulässig, wenn der Nutzer es
anweist. Das Löschen eines Belegs bleibt untersagt (P-03); vorgesehen ist der
Korrekturvorgang des Systems, der eine Spur hinterlässt.

Die Originaldatei bleibt in jedem Fall unverändert (P-05). Stellt sich ein Beleg als
Nichtbeleg heraus, wird er aus der Buchung genommen, nicht aus dem Ordner.
