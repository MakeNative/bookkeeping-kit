---
name: adopt
description: "Richtet ein Unternehmen für das buchhaltung-kit ein: liest die Steuereinstellungen aus dem Buchhaltungssystem aus, nimmt Ordner, Zahlungsquellen und Lieferanten auf und erzeugt COMPANY_CONTEXT.md. Jederzeit wiederholbar, um den Kontext aufzufrischen. Triggers on: /buchhaltung-kit:adopt"
disable-model-invocation: true
---

Du richtest dieses Projekt für das buchhaltung-kit ein. Arbeite **direkt** — delegiere das
Schreiben nicht. Für die Belegauswertung darfst du den `receipt-reader` einsetzen.

Diese Skill läuft im Hauptkontext, weil sie mit dem Menschen spricht: Logins, Rückfragen,
Freigaben. Das ist Absicht.

## Grundsatz

Was das System weiß, wird **ausgelesen**. Was nur der Mensch weiß, wird **gefragt**. Nie
raten — eine falsche Besteuerungsart verfälscht einen ganzen Monat.

## Schritt 0 — Modus bestimmen

Prüfe `.claude/docs/COMPANY_CONTEXT.md`:
- fehlt → **Ersteinrichtung**, alle Schritte
- vorhanden → **Auffrischung**: `AUSLESEN`-Felder neu prüfen, neue Lieferanten ergänzen,
  von Hand gepflegte Einträge **nicht** überschreiben. Vergleiche `CONTRACT_VERSION` mit
  `docs/COMPANY_CONTEXT_TEMPLATE.md` des Plugins und ergänze fehlende Abschnitte.

## Schritt 1 — Buchhaltungssystem verbinden und auslesen

Frage, welches System genutzt wird und öffne es im Browser. Ist keine Sitzung aktiv, **bitte
den Nutzer, sich anzumelden** — gib niemals Zugangsdaten ein (Regel P-02).

Lies danach selbst aus den Einstellungen:

| Feld | Warum ausgelesen |
|---|---|
| Besteuerungsart (Ist/Soll) | Entscheidet, ob Ausgangsrechnungen bei Rechnungsstellung oder bei Zahlung zählen |
| Gewinnermittlung | Kontext für Kontenrahmen und Jahresabschluss |
| Kontenrahmen | Bestimmt die Kategoriebezeichnungen |
| USt-IdNr., Steuernummer, Finanzamt | Für Belegprüfung und Meldung |
| Voranmeldungsturnus, Dauerfristverlängerung | Fristen und Zeitraumlänge |
| Hinterlegte Steuerkanzlei und deren Aufgaben | Zuständigkeit und Kollisionsrisiko |

Finde ein Feld nicht, frage gezielt danach — markiere es aber als „erfragt", nicht als
„ausgelesen".

Prüfe zusätzlich den gemeldeten Stand der letzten Zeiträume: Welcher Monat ist zuletzt
übermittelt worden? Das ist der Ausgangspunkt für spätere Läufe und Korrekturen.

## Schritt 2 — Ordner

Frage nach den Pfaden für Eingangs- und Ausgangsrechnungen. Schlage ein Namensschema vor und
prüfe am Ist-Bestand, ob bereits eines gelebt wird — übernimm dann das vorhandene.

Halte fest: Originale werden nie umbenannt oder verändert (Regel P-05).

## Schritt 3 — Zahlungsquellen

Frage nach Banken, Kreditkarten und Zahlungsdiensten und danach, **wo deren Benachrichtigungen
eingehen** (Postfach, Absenderadresse). Diese Quellen speisen später die Vollständigkeits-
prüfung — nicht der Ordnerinhalt (Regel P-06).

Frage ebenfalls nach den Postfächern, in denen Rechnungen eingehen. Prüfe danach selbst,
**welche Adressen** in jedem verbundenen Postfach ankommen: Empfänger der Mails der letzten
drei Monate auszählen. Aliasse und Weiterleitungen tauchen dabei auf, und ein Postfach, das
nicht verbunden ist, kann trotzdem längst mitgelesen werden. Trag das als
`mail.konten[].empfaengt` ein.

## Schritt 4 — Lieferanten-Inventur

Nimm die Belege der letzten zwölf Monate aus dem Eingangsordner. Setze den `receipt-reader` auf
eine Stichprobe je Lieferant an — nicht auf alle Belege; es geht um das Muster, nicht um die
Vollständigkeit.

Ordne jedem Lieferanten ein Muster aus `docs/LIEFERANTEN_MUSTER.md` zu und leite daraus
Behandlung und Kategorie ab.

Frage je Lieferant **nur zwei Dinge**, die nicht auf dem Beleg stehen:
1. Wo liegt die Rechnung? (Portal-URL oder Mail-Absender)
2. Braucht es dafür ein Login?

Kommt die Rechnung per Mail, ermittle trotzdem die Rechnungsseite im Anbieterkonto und trag
sie als `portal` ein. Sie ist der Ausweg in dem Monat, in dem die Mail fehlt.

Ergänze, was du beim Öffnen selbst feststellst: Zwei-Faktor, Domain-Freigabe der
Browser-Erweiterung nötig, Passkey-Pflicht angekündigt.

Erkennst du ein Muster M-04 (Marktplatz), trage `pro_rechnung_pruefen` ein und **nicht** eine
feste Behandlung.

## Schritt 5 — Ausschlüsse

Frage nach Konten, Organisationen oder Lieferanten, deren Rechnungen zwar im Postfach landen,
aber einer anderen Gesellschaft zuzurechnen sind. Prüfe bei Portalen zusätzlich, auf welche
Organisation das Konto läuft.

Ohne diesen Schritt werden regelmäßig Fremdbelege gebucht (Regel E-13).

## Schritt 6 — Altbestand aufnehmen

Zähle im Buchhaltungssystem, was aus Vorperioden offen ist: ungeprüfte Belege, überfällige
Posten, Entwürfe. Schreibe die Summen und den Stichtag in den Context und lege
`.claude/buchhaltung-offene-punkte.md` an.

Der Monatslauf fasst diesen Altbestand **nicht** an — aber er darf auch nicht verschwinden.

## Schritt 7 — Umgebung prüfen

Melde dem Nutzer in **einer** Liste, was einmalig umzustellen ist:

- `pdftotext` verfügbar? (`command -v pdftotext`)
- Browser-Erweiterung: Domain-Freigaben für alle Portale aus Schritt 4
- Browser-PDF-Einstellung auf „PDFs herunterladen" statt Anzeige im Viewer
- Schreibrechte auf den Belegordnern

## Schritt 8 — Dateien anlegen

1. `.claude/docs/COMPANY_CONTEXT.md` nach der Vorlage des Plugins
2. `.claude/agent-memory/buchhaltung-kit-<agent>/` für die Agenten des Kits. Bei einer
   Auffrischung die Memory-Ordner der alten deutschen Agentennamen umziehen, Inhalt
   unverändert (bis Plugin 0.2.x):
   `beleg-leser` → `receipt-reader`, `steuer-klassifizierer` → `tax-classifier`,
   `plausibilitaets-gate` → `plausibility-gate`, `monats-auditor` → `monthly-auditor`.
   Existiert der neue Ordner schon, nicht überschreiben, sondern beide dem Nutzer zeigen.
3. `.claude/buchhaltung-log/` und `.claude/buchhaltung-eval/`
4. Hooks aus `hooks/hooks.json` in `.claude/settings.json` mergen — **vorhandene Hooks nicht
   überschreiben**, nur ergänzen
5. `.gitignore` des Projekts ergänzen:
   ```
   .claude/docs/COMPANY_CONTEXT.md
   .claude/buchhaltung-log/
   .claude/buchhaltung-eval/
   .claude/buchhaltung-offene-punkte.md
   ```

## Abschluss

Fasse zusammen: ausgelesene Steuerdaten, gefundene Lieferanten mit Muster, Ausschlüsse,
Altbestand, offene Umstellungen.

Nenne als nächsten Schritt einen **Trockenlauf** für einen abgeschlossenen Monat:

```
/buchhaltung-kit:monthly-run <YYYY-MM> --trocken
```

Weise darauf hin, dass Schwellenwerte im Regelwerk mit `wert_pruefen: ja` vor dem produktiven
Einsatz gegen die aktuelle Rechtslage zu bestätigen sind — am besten durch die Steuerkanzlei.
