#!/usr/bin/env python3
"""Vault scaffold for the obsidian-second-brain skill — deterministic for a
given platform and flag set (the launcher installed matches the running OS).

Usage:
    python3 bootstrap_vault.py /path/to/vault [--modules core,work] [--dry-run] [--force]
                               [--no-dashboard | --dashboard-only] [--dashboard-dir REL]

Modules:
    core       Inbox, Tasks, People, Maps(/Dashboards), Archive, Templates, Attachments
    work       Work/{Projects,Areas,Business,Meetings}
    personal   Personal/{Projects,Areas,Journal,Ideas}
    resources  Resources/{Research,Sources,Books,Notes}
    daily      Daily/
    money      Money/ + Money/Transactions/ (funds & transaction ledger)
    findings   Findings/ (one note per research figure — see references/findings.md)

Also installs the skill's assets/templates/*.md into Templates/ and
assets/bases/*.base into Maps/Dashboards/ (existing files are never overwritten),
and creates a starter Maps/Home.md.

Live dashboard: dashboard_server.py and this platform's launcher (macOS
"Start Dashboard.command", Windows "Start Dashboard.bat", otherwise
start-dashboard.sh) are installed into Maps/Dashboards/ too, so a new vault gets
the interactive dashboard without a manual copy step. These are program code,
not user content — they are the one thing this script replaces, and only when
the installed bytes differ from the skill's (which makes a re-run the upgrade
path after a skill update). An existing copy is preserved as <name>.bak before
it is replaced, so a locally edited dashboard is never lost. Skip the dashboard
with --no-dashboard, refresh only it (no scaffolding, no CLAUDE.md guard) with
--dashboard-only, and install it somewhere other than Maps/Dashboards with
--dashboard-dir (the vault path is then baked into the launcher, since the
server only infers its vault from <vault>/Maps/Dashboards).

Safety: refuses to run if the vault already has a CLAUDE.md (it's not a fresh
vault) unless --force is given. This script only scaffolds — Claude writes the
vault CLAUDE.md afterwards, from the onboarding interview answers
(references/onboarding.md).
"""
import argparse, os, pathlib, shutil, sys

MODULES = {
    "core":      ["Inbox", "Tasks", "People", "Maps", "Maps/Dashboards", "Archive", "Templates", "Attachments"],
    "work":      ["Work/Projects", "Work/Areas", "Work/Business", "Work/Meetings"],
    "personal":  ["Personal/Projects", "Personal/Areas", "Personal/Journal", "Personal/Ideas"],
    "resources": ["Resources/Research", "Resources/Sources", "Resources/Books", "Resources/Notes"],
    "daily":     ["Daily"],
    "money":     ["Money", "Money/Transactions"],
    "findings":  ["Findings"],
}

DEFAULT_DASH_DIR = "Maps/Dashboards"   # the only location the server can infer its vault from
# Per-platform dashboard launcher. Only the running platform's launcher is
# installed; a vault shared across platforms gets the others by running
# --dashboard-only once on each machine.
LAUNCHERS = {"darwin": "Start Dashboard.command", "win32": "Start Dashboard.bat"}
DEFAULT_LAUNCHER = "start-dashboard.sh"

HOME_MD = """---
type: moc
domain: shared
created: {today}
tags:
  - moc
---
# 🗺️ Home

> The front door. Ask Claude: "what's on my plate?", "what do I know about X?", "capture: …"

## Boards
![[Tasks.base]]

## Go to
- People directory: `Maps/Dashboards/People.base`
{pipeline_line}{ledger_line}{dashboard_line}
"""

def launcher_name(plat=None):
    return LAUNCHERS.get(plat if plat is not None else sys.platform, DEFAULT_LAUNCHER)

def start_hint(rel_launcher, plat=None):
    """How the owner starts the dashboard, in one phrase."""
    plat = plat if plat is not None else sys.platform
    verb = "double-click" if plat in LAUNCHERS else "run"
    return f"{verb} `{rel_launcher}`"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vault")
    ap.add_argument("--modules", default="core,work")  # also available: personal, resources, daily, money, findings
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--no-dashboard", action="store_true",
                    help="don't install the live dashboard server into Maps/Dashboards/")
    ap.add_argument("--dashboard-only", action="store_true",
                    help="only (re)install the dashboard server + launcher — no folders, templates, or bases")
    ap.add_argument("--dashboard-dir", default=DEFAULT_DASH_DIR,
                    help=f"where the dashboard program goes, relative to the vault (default {DEFAULT_DASH_DIR})")
    a = ap.parse_args()
    if a.dashboard_only and a.no_dashboard:
        print("--dashboard-only and --no-dashboard are contradictory."); sys.exit(1)
    a.dashboard_dir = a.dashboard_dir.strip().rstrip("/\\") or DEFAULT_DASH_DIR
    dd = pathlib.Path(a.dashboard_dir)
    if dd.is_absolute() or ".." in dd.parts:
        print("--dashboard-dir must be a relative path inside the vault, e.g. 'Tools/Dashboards'."); sys.exit(1)
    V = pathlib.Path(a.vault).expanduser()
    mods = [m.strip() for m in a.modules.split(",") if m.strip()]
    bad = [m for m in mods if m not in MODULES]
    if bad:
        print(f"Unknown module(s): {bad}. Valid: {list(MODULES)}"); sys.exit(1)
    if "core" not in mods:
        mods.insert(0, "core")
    if (V / "CLAUDE.md").exists() and not (a.force or a.dashboard_only):
        print(f"ABORT: {V}/CLAUDE.md exists — this is not a fresh vault. "
              "Adapt to the existing structure instead (First Contact), or rerun with --force.")
        sys.exit(1)

    assets = pathlib.Path(__file__).resolve().parent.parent / "assets"
    actions = []
    for m in [] if a.dashboard_only else mods:
        for d in MODULES[m]:
            p = V / d
            if not p.exists(): actions.append(("mkdir", p))
    if (assets / "templates").is_dir() and not a.dashboard_only:
        for t in sorted((assets / "templates").glob("*.md")):
            dest = V / "Templates" / t.name
            if not dest.exists(): actions.append(("copy", t, dest))
    if (assets / "bases").is_dir() and not a.dashboard_only:
        for b in sorted((assets / "bases").glob("*.base")):
            if b.name == "Pipeline.base" and "work" not in mods: continue
            if b.name == "Ledger.base" and "money" not in mods: continue
            if b.name == "Reading.base" and "resources" not in mods: continue
            dest = V / "Maps/Dashboards" / b.name
            if not dest.exists(): actions.append(("copy", b, dest))
    # Obsidian property-type registry — types are keyed by property NAME vault-wide
    if (assets / "types.json").is_file() and not a.dashboard_only:
        dest = V / ".obsidian/types.json"
        if not dest.exists(): actions.append(("copy", assets / "types.json", dest))
    # Live dashboard — program code, so keep it current rather than preserving a
    # stale copy (the only files this script replaces; the old copy is kept as
    # .bak). Only this platform's launcher is installed.
    here = pathlib.Path(__file__).resolve().parent
    dash_dir = V / a.dashboard_dir
    dash_dest = launcher_rel = None
    if not a.no_dashboard:
        server = here / "dashboard_server.py"
        if server.is_file():
            dash_dest = dash_dir / server.name
            if not dash_dest.exists():
                actions.append(("copy", server, dash_dest))
            elif dash_dest.read_bytes() != server.read_bytes():
                actions.append(("update", server, dash_dest))
        lname = launcher_name()
        launcher = here / lname
        if launcher.is_file() and dash_dest is not None:
            text = launcher.read_text(encoding="utf-8")
            # Installed outside <vault>/Maps/Dashboards the server can't infer its
            # vault, so bake the path in — relative, so moving the vault is fine.
            if os.path.normpath(a.dashboard_dir) != os.path.normpath(DEFAULT_DASH_DIR):
                rel = os.path.relpath(V.resolve(), dash_dir.resolve())
                if lname.endswith(".bat"): rel = rel.replace("/", "\\")
                baked = text.replace("dashboard_server.py ", f'dashboard_server.py "{rel}" ')
                if baked == text:
                    print(f"Can't bake the vault path into {lname} — unexpected launcher layout."); sys.exit(1)
                text = baked
            dest = dash_dir / lname
            if not dest.exists() or dest.read_text(encoding="utf-8") != text:
                actions.append(("launcher", text, dest))
            launcher_rel = f"{a.dashboard_dir}/{lname}"
    home = V / "Maps/Home.md"
    if not home.exists() and not a.dashboard_only: actions.append(("home", home))

    import datetime
    def keep_backup(dest):
        """Preserve a copy the owner may have edited, before replacing it."""
        if not dest.exists(): return
        bak = dest.with_name(dest.name + ".bak")
        shutil.copyfile(dest, bak)
        print(f"    kept your copy as {bak.name}")

    for act in actions:
        label = f"{act[0]}: {act[-1].relative_to(V) if act[-1].is_absolute() else act[-1]}"
        print(("DRY  " if a.dry_run else "  ") + label)
        if a.dry_run: continue
        if act[0] == "mkdir": act[1].mkdir(parents=True, exist_ok=True)
        elif act[0] in ("copy", "update"):
            act[2].parent.mkdir(parents=True, exist_ok=True)
            if act[0] == "update": keep_backup(act[2])
            shutil.copyfile(act[1], act[2])
        elif act[0] == "launcher":
            act[2].parent.mkdir(parents=True, exist_ok=True)
            keep_backup(act[2])
            act[2].write_text(act[1], encoding="utf-8"); act[2].chmod(0o755)
        elif act[0] == "home":
            act[1].parent.mkdir(parents=True, exist_ok=True)
            pl = "- Pipeline: `Maps/Dashboards/Pipeline.base`\n" if "work" in mods else ""
            ll = "- Ledger: `Maps/Dashboards/Ledger.base`\n" if "money" in mods else ""
            dl = f"- Live dashboard: {start_hint(launcher_rel)}\n" if launcher_rel else ""
            # encoding is explicit everywhere: on Windows the default is the ANSI code page,
            # and HOME_MD carries characters it cannot encode - a fresh vault crashed on it.
            act[1].write_text(HOME_MD.format(today=datetime.date.today().isoformat(),
                                             pipeline_line=pl, ledger_line=ll, dashboard_line=dl),
                              encoding="utf-8")
    print(f"\n{'Would perform' if a.dry_run else 'Done:'} {len(actions)} action(s) in {V}")
    if not a.dry_run and dash_dest is not None:
        print("Dashboard: " + (start_hint(str(dash_dest.parent / launcher_name())) if launcher_rel
                               else f'python3 "{dash_dest}" --open'))
    if not a.dry_run and a.dashboard_only and launcher_rel:
        print(f"If Maps/Home.md doesn't link it yet, add: - Live dashboard: {start_hint(launcher_rel)}")
    if not a.dry_run and not a.dashboard_only:
        print("Next (Claude): write the vault CLAUDE.md from the onboarding interview "
              "(references/onboarding.md), then capture the user's first 2-3 real tasks.")

if __name__ == "__main__":
    main()
