#!/usr/bin/env python3
"""Selbsttest der Hooks.

Jede Sperre wird in **beide** Richtungen geprüft: Sie muss blockieren, was sie blockieren
soll, und durchlassen, was erlaubt ist. Ein Guard, der alles blockiert, besteht einen
einseitigen Test und macht das Kit unbenutzbar.
"""
import json, subprocess, sys, tempfile, pathlib, os

HOOKS = pathlib.Path(__file__).resolve().parent
BLOCK, PASS = 2, 0


def lauf(skript, daten, cwd):
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
    p = subprocess.run([sys.executable, str(HOOKS / skript)],
                       input=json.dumps(daten), text=True,
                       capture_output=True, cwd=cwd, env=env)
    return p.returncode, (p.stderr or "").strip()


def mandant(tmp):
    """Minimaler Mandant mit Belegordnern, wie adopt ihn anlegt."""
    d = pathlib.Path(tmp)
    (d / ".claude" / "docs").mkdir(parents=True)
    (d / ".claude" / "docs" / "COMPANY_CONTEXT.md").write_text(
        "ordner:\n"
        f"  eingangsrechnungen: {d}/Rechnungen/<JJJJ>\n"
        f"  ausgangsrechnungen: {d}/Rechnungen_Umsatz/<JJJJ>\n"
        "  originale_unveraendert: true\n", encoding="utf-8")
    return d


FAELLE = [
    # (Name, Skript, tool_name, tool_input-Vorlage, erwartet[, agent_type, cwd-Unterordner])
    ("rm im Belegordner blockiert", "guard-originale.py", "Bash",
     {"command": "rm {EIN}/2026/beleg.pdf"}, BLOCK),
    ("mv im Belegordner blockiert", "guard-originale.py", "Bash",
     {"command": "mv {EIN}/2026/a.pdf {EIN}/2026/b.pdf"}, BLOCK),
    ("Write in den Belegordner blockiert", "guard-originale.py", "Write",
     {"file_path": "{EIN}/2026/neu.pdf", "content": "x"}, BLOCK),
    ("Lesen im Belegordner erlaubt", "guard-originale.py", "Bash",
     {"command": "pdftotext -layout {EIN}/2026/beleg.pdf -"}, PASS),
    ("ls im Belegordner erlaubt", "guard-originale.py", "Bash",
     {"command": "ls {EIN}/2026"}, PASS),
    ("rm ausserhalb erlaubt", "guard-originale.py", "Bash",
     {"command": "rm /tmp/scratch/zwischenergebnis.json"}, PASS),
    ("Write ins Laufprotokoll erlaubt", "guard-originale.py", "Write",
     {"file_path": "{ROOT}/.claude/bookkeeping-log/2026-09/20-belege.jsonl"}, PASS),

    ("Elster blockiert", "guard-uebermittlung.py", "mcp__claude-in-chrome__navigate",
     {"url": "https://www.elster.de/eportal/formulare-leistungen"}, BLOCK),
    ("Uebermittlungspfad blockiert", "guard-uebermittlung.py", "mcp__claude-in-chrome__navigate",
     {"url": "https://app.example.com/ustva/2026-09/uebermitteln"}, BLOCK),
    ("Belegansicht erlaubt", "guard-uebermittlung.py", "mcp__claude-in-chrome__navigate",
     {"url": "https://app.example.com/vouchers/12345"}, PASS),
    ("Voranmeldung ansehen erlaubt", "guard-uebermittlung.py", "mcp__claude-in-chrome__navigate",
     {"url": "https://app.example.com/ustva/2026-09"}, PASS),
    ("Lieferantenportal erlaubt", "guard-uebermittlung.py", "mcp__claude-in-chrome__navigate",
     {"url": "https://portal.example.com/invoices"}, PASS),
    ("Datei-Upload beim Lieferanten erlaubt", "guard-uebermittlung.py", "mcp__claude-in-chrome__navigate",
     {"url": "https://portal.example.com/documents/file"}, PASS),
    ("Voranmeldung senden blockiert", "guard-uebermittlung.py", "mcp__claude-in-chrome__navigate",
     {"url": "https://app.example.com/voranmeldung/2026-09/senden"}, BLOCK),
    ("Steuererklaerung abgeben blockiert", "guard-uebermittlung.py", "WebFetch",
     {"url": "https://app.example.com/steuererklaerung/abgeben?id=7"}, BLOCK),

    # Schreibrechte der Kit-Agenten
    ("Agent: Write ins eigene Memory erlaubt", "guard-agenten.py", "Write",
     {"file_path": "{ROOT}/.claude/agent-memory/bookkeeping-kit-receipt-reader/MEMORY.md"},
     PASS, "bookkeeping-kit:receipt-reader"),
    ("Agent: Write in fremdes Memory blockiert", "guard-agenten.py", "Write",
     {"file_path": "{ROOT}/.claude/agent-memory/bookkeeping-kit-tax-classifier/MEMORY.md"},
     BLOCK, "bookkeeping-kit:receipt-reader"),
    ("Agent: Edit an agents.md des Laufs erlaubt", "guard-agenten.py", "Edit",
     {"file_path": "{ROOT}/.claude/bookkeeping-log/2026-10/agents.md"},
     PASS, "bookkeeping-kit:plausibility-gate"),
    ("Agent: Phasendatei blockiert", "guard-agenten.py", "Write",
     {"file_path": "{ROOT}/.claude/bookkeeping-log/2026-10/20-belege.jsonl"},
     BLOCK, "bookkeeping-kit:receipt-reader"),
    ("Agent: Context blockiert", "guard-agenten.py", "Edit",
     {"file_path": "{ROOT}/.claude/docs/COMPANY_CONTEXT.md"},
     BLOCK, "bookkeeping-kit:tax-classifier"),
    ("Agent: Memory relativ aus Unterordner erlaubt", "guard-agenten.py", "Write",
     {"file_path": "../agent-memory/bookkeeping-kit-monthly-auditor/MEMORY.md"},
     PASS, "bookkeeping-kit:monthly-auditor", ".claude/bookkeeping-log"),
    ("Agent: Pfad mit .. aus dem Memory heraus blockiert", "guard-agenten.py", "Write",
     {"file_path": "{ROOT}/.claude/agent-memory/bookkeeping-kit-receipt-reader/../../docs/x.md"},
     BLOCK, "bookkeeping-kit:receipt-reader"),
    ("Agent: Evaluator schreibt bookkeeping-eval/agents.md", "guard-agenten.py", "Write",
     {"file_path": "{ROOT}/.claude/bookkeeping-eval/agents.md"},
     PASS, "bookkeeping-kit:agent-evaluator"),
    ("Agent: Bash lesen erlaubt", "guard-agenten.py", "Bash",
     {"command": "pdftotext -layout {EIN}/2026/a.pdf - 2>/dev/null | grep -n '<cbc:ID>' | head"},
     PASS, "bookkeeping-kit:receipt-reader"),
    ("Agent: Bash mit stderr-Umleitung erlaubt", "guard-agenten.py", "Bash",
     {"command": "python3 tools/belege_lesen.py --zeitraum 2026-10 2>&1 | tail -5"},
     PASS, "bookkeeping-kit:receipt-reader"),
    ("Agent: Bash-Umleitung in Datei blockiert", "guard-agenten.py", "Bash",
     {"command": "echo x > {ROOT}/.claude/docs/COMPANY_CONTEXT.md"},
     BLOCK, "bookkeeping-kit:receipt-reader"),
    ("Agent: Bash tee blockiert", "guard-agenten.py", "Bash",
     {"command": "cat a.json | tee {ROOT}/.claude/bookkeeping-log/2026-10/20-belege.jsonl"},
     BLOCK, "bookkeeping-kit:receipt-reader"),
    ("Agent: Bash sed -i blockiert", "guard-agenten.py", "Bash",
     {"command": "sed -i '' 's/a/b/' {ROOT}/.claude/docs/COMPANY_CONTEXT.md"},
     BLOCK, "bookkeeping-kit:tax-classifier"),
    ("Hauptkontext: Write ins Laufprotokoll erlaubt", "guard-agenten.py", "Write",
     {"file_path": "{ROOT}/.claude/bookkeeping-log/2026-10/20-belege.jsonl"}, PASS, ""),
    ("Fremder Agent unberührt", "guard-agenten.py", "Write",
     {"file_path": "{ROOT}/.claude/docs/COMPANY_CONTEXT.md"}, PASS, "general-purpose"),

    # Arbeitsverzeichnis unterhalb des Mandanten: Context wird trotzdem gefunden
    ("Unterordner: Write in den Belegordner blockiert", "guard-originale.py", "Write",
     {"file_path": "{EIN}/2026/neu.pdf", "content": "x"}, BLOCK, "", ".claude/bookkeeping-log"),
]


def main():
    fehler = 0
    with tempfile.TemporaryDirectory() as tmp:
        d = mandant(tmp)
        ein = f"{d}/Rechnungen"
        (d / ".claude" / "bookkeeping-log").mkdir(parents=True, exist_ok=True)
        for name, skript, tool, vorlage, erwartet, *rest in FAELLE:
            typ = rest[0] if rest else ""
            wo = d / rest[1] if len(rest) > 1 else d
            ti = {k: (v.replace("{EIN}", ein).replace("{ROOT}", str(d))
                      if isinstance(v, str) else v) for k, v in vorlage.items()}
            daten = {"tool_name": tool, "tool_input": ti, "cwd": str(wo)}
            if typ:
                daten["agent_type"] = typ
            rc, msg = lauf(skript, daten, wo)
            ok = rc == erwartet
            fehler += not ok
            print(f"  [{'OK  ' if ok else 'FEHL'}] {name}"
                  + ("" if ok else f"  (rc={rc}, erwartet {erwartet}) {msg[:90]}"))

        # Ohne Context darf nichts blockiert werden — das Kit ist dann nicht eingerichtet.
        leer = pathlib.Path(tmp) / "ohne"
        leer.mkdir()
        rc, _ = lauf("guard-originale.py",
                     {"tool_name": "Bash", "tool_input": {"command": "rm -rf /tmp/x"},
                      "cwd": str(leer)}, leer)
        ok = rc == PASS
        fehler += not ok
        print(f"  [{'OK  ' if ok else 'FEHL'}] ohne Context wird nicht blockiert")

        # Protokoll-Hooks duerfen nie blockieren, auch bei Unsinn in der Eingabe.
        for skript in ("spur-navigation.py", "sitzungsstart.py"):
            rc, _ = lauf(skript, {"tool_input": {"url": "https://x.example"}, "cwd": str(d)}, d)
            ok = rc == PASS
            fehler += not ok
            print(f"  [{'OK  ' if ok else 'FEHL'}] {skript} blockiert nicht")
        spur = d / ".claude" / "bookkeeping-log" / "navigation.jsonl"
        ok = spur.exists() and "x.example" in spur.read_text()
        fehler += not ok
        print(f"  [{'OK  ' if ok else 'FEHL'}] Navigationsspur wird geschrieben")

    print(f"\n{'alle Hooks grün' if not fehler else str(fehler) + ' Fehler'}")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
