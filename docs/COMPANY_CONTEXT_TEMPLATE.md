# COMPANY_CONTEXT — Vorlage

```
CONTRACT_VERSION: 2
```

Diese Datei wird von `/bookkeeping-kit:adopt` im **Mandantenprojekt** erzeugt und liegt dort
unter `.claude/docs/COMPANY_CONTEXT.md`. Sie gehört **nicht** ins Plugin-Repo.

Die Agenten und Skills des Kits sind generisch. Alles Unternehmensspezifische steht hier.
Fehlt die Datei, bricht jeder Lauf ab.

> Felder mit `AUSLESEN` werden von `adopt` aus dem Buchhaltungssystem gelesen, nicht erfragt.
> Eine Annahme an dieser Stelle kann einen ganzen Monat verfälschen.

---

```yaml
CONTRACT_VERSION: 2
REGELWERK_VERSION: 1          # Version, unter der zuletzt gebucht wurde

unternehmen:
  name:
  frühere_firmierungen: []     # erscheinen noch auf Rechnungen alter Lieferanten
                               # Zugleich Ausschlussliste bei der Lieferantenerkennung
                               # (E-18): die eigene Anschrift steht auf jedem Beleg und
                               # würde sonst als Leistender gelesen
  rechtsform:
  ust_id:                      # AUSLESEN
  steuernummer:                # AUSLESEN
  finanzamt:                   # AUSLESEN
  handelsregister:

steuer:
  besteuerungsart:             # AUSLESEN — ist | soll. NIE annehmen.
  gewinnermittlung:            # AUSLESEN — bilanzierung | einnahmen_ueberschuss
  kontenrahmen:                # AUSLESEN — z. B. SKR03 | SKR04
  turnus:                      # monatlich | quartal
  dauerfristverlängerung:      # ja | nein
  frist_regel:                 # z. B. "10. des Folgemonats"

zustaendigkeiten:
  ustva:                       # mandant | steuerkanzlei
  jahresabschluss:
  steuerkanzlei:
    name:
    kontakt:
  kanzlei_bucht_mit:           # ja | nein — bei ja kein paralleler Schreiblauf

buchhaltungssystem:
  name:                        # z. B. lexoffice
  url:
  ui_doku: docs/LEXOFFICE_UI.md   # systemabhängige Bedienhinweise im Plugin

ordner:
  eingangsrechnungen:          # absoluter Pfad, <JJJJ> als Platzhalter erlaubt
  ausgangsrechnungen:
  namensschema:                # z. B. "<lieferant>_<JJJJ-MM-TT>_<belegnr>.pdf"
  originale_unveraendert: true # P-05: nie umbenennen, Zuordnung über Mappingdatei

zahlungsquellen:
  - name:                      # Bank, Zahlungsdienst, Kreditkarte
    rolle:                     # hauptkonto | zahlungsmittel
    benachrichtigung:          # woher die Zahlungsmeldungen kommen (Mail-Absender o. Ä.)

mail:
  konten:                      # Postfächer, in denen Rechnungen eingehen
    - adresse:
      verbunden:               # ja | nein — durchsuchbar über die Mail-Anbindung
      empfaengt: []            # alle Adressen, deren Mails hier ankommen (Aliasse,
                               # Weiterleitungen) — von adopt geprüft, nicht erfragt

lieferanten:
  # Wiederkehrende Lieferanten. Wächst durch den Lauf; bekannte Anbieter-Fakten
  # stehen in docs/LIEFERANTEN_BEKANNT.md und müssen hier nicht wiederholt werden.
  - name:
      entitaet:                # abrechnende Gesellschaft + deren USt-IdNr.
      behandlung:              # inland_19 | inland_7 | §13b_eu | §13b_drittland
                               # | ig_erwerb | kein_vorsteuerabzug | pro_rechnung_pruefen
      kategorie:               # Kategoriename im Buchhaltungssystem
      beleg_quelle:            # Mail-Absender oder Portal — der übliche Weg
      portal:                  # Rechnungsseite im Anbieterkonto, auch wenn die Rechnung
                               # meist per Mail kommt: der Weg, wenn die Mail ausbleibt
      login:                   # ja | nein
      zwei_faktor:             # ja | nein
      domain_freigabe_noetig:  # ja | nein — Browser-Erweiterung
      nur_manuell:             # ja | nein — z. B. bei Passkey-Pflicht
      besonderheit:            # z. B. "stellt erst im Folgemonat aus"

ausschluesse:
  # Belege, die regelmäßig auflaufen, aber einer anderen Gesellschaft zuzurechnen sind (E-13)
  - lieferant:
    grund:

altbestand:
  # Einmalig von adopt erfasst, vom Monatslauf nicht angefasst, aber nicht vergessen
  erfasst_am:
  offene_belege_vorperioden:
  hinweis:
```

---

## Pflege

- `adopt` erneut ausführen aktualisiert die `AUSLESEN`-Felder und ergänzt neue Lieferanten,
  ohne von Hand gepflegte Einträge zu überschreiben.
- Der Sammler schreibt gelernte Portalwege und Login-Eigenschaften zurück — Skills haben
  kein eigenes Gedächtnis, diese Datei ist ihr Gedächtnis.
- Ändert sich die Besteuerungsart, der Turnus oder die Dauerfristverlängerung, muss der
  nächste Lauf das erkennen. Deshalb werden diese Felder bei jedem Lauf gegen das System
  geprüft, nicht nur bei `adopt`.
