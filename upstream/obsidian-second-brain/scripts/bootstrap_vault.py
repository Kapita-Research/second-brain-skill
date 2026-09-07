#!/usr/bin/env python3
"""Deterministic vault scaffold for the obsidian-second-brain skill.

Usage:
    python3 bootstrap_vault.py /path/to/vault [--modules core,work] [--dry-run] [--force]

Modules:
    core       Inbox, Tasks, People, Maps(/Dashboards), Archive, Templates, Attachments
    work       Work/{Projects,Areas,Business,Meetings}
    personal   Personal/{Projects,Areas,Journal,Ideas}
    resources  Resources/{Research,Sources,Books,Notes}
    daily      Daily/
    money      Money/ + Money/Transactions/ (funds & transaction ledger)

Also installs the skill's assets/templates/*.md into Templates/ and
assets/bases/*.base into Maps/Dashboards/ (existing files are never overwritten),
and creates a starter Maps/Home.md.

Safety: refuses to run if the vault already has a CLAUDE.md (it's not a fresh
vault) unless --force is given. This script only scaffolds — Claude writes the
vault CLAUDE.md afterwards, from the onboarding interview answers
(references/onboarding.md).
"""
import argparse, pathlib, shutil, sys

MODULES = {
    "core":      ["Inbox", "Tasks", "People", "Maps", "Maps/Dashboards", "Archive", "Templates", "Attachments"],
    "work":      ["Work/Projects", "Work/Areas", "Work/Business", "Work/Meetings"],
    "personal":  ["Personal/Projects", "Personal/Areas", "Personal/Journal", "Personal/Ideas"],
    "resources": ["Resources/Research", "Resources/Sources", "Resources/Books", "Resources/Notes"],
    "daily":     ["Daily"],
    "money":     ["Money", "Money/Transactions"],
}

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
{pipeline_line}{ledger_line}
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vault")
    ap.add_argument("--modules", default="core,work")  # also available: personal, resources, daily, money
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    V = pathlib.Path(a.vault).expanduser()
    mods = [m.strip() for m in a.modules.split(",") if m.strip()]
    bad = [m for m in mods if m not in MODULES]
    if bad:
        print(f"Unknown module(s): {bad}. Valid: {list(MODULES)}"); sys.exit(1)
    if "core" not in mods:
        mods.insert(0, "core")
    if (V / "CLAUDE.md").exists() and not a.force:
        print(f"ABORT: {V}/CLAUDE.md exists — this is not a fresh vault. "
              "Adapt to the existing structure instead (First Contact), or rerun with --force.")
        sys.exit(1)

    assets = pathlib.Path(__file__).resolve().parent.parent / "assets"
    actions = []
    for m in mods:
        for d in MODULES[m]:
            p = V / d
            if not p.exists(): actions.append(("mkdir", p))
    if (assets / "templates").is_dir():
        for t in sorted((assets / "templates").glob("*.md")):
            dest = V / "Templates" / t.name
            if not dest.exists(): actions.append(("copy", t, dest))
    if (assets / "bases").is_dir():
        for b in sorted((assets / "bases").glob("*.base")):
            if b.name == "Pipeline.base" and "work" not in mods: continue
            if b.name == "Ledger.base" and "money" not in mods: continue
            if b.name == "Reading.base" and "resources" not in mods: continue
            dest = V / "Maps/Dashboards" / b.name
            if not dest.exists(): actions.append(("copy", b, dest))
    # Obsidian property-type registry — types are keyed by property NAME vault-wide
    if (assets / "types.json").is_file():
        dest = V / ".obsidian/types.json"
        if not dest.exists(): actions.append(("copy", assets / "types.json", dest))
    home = V / "Maps/Home.md"
    if not home.exists(): actions.append(("home", home))

    import datetime
    for act in actions:
        label = f"{act[0]}: {act[-1].relative_to(V) if act[-1].is_absolute() else act[-1]}"
        print(("DRY  " if a.dry_run else "  ") + label)
        if a.dry_run: continue
        if act[0] == "mkdir": act[1].mkdir(parents=True, exist_ok=True)
        elif act[0] == "copy":
            act[2].parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(act[1], act[2])
        elif act[0] == "home":
            act[1].parent.mkdir(parents=True, exist_ok=True)
            pl = "- Pipeline: `Maps/Dashboards/Pipeline.base`\n" if "work" in mods else ""
            ll = "- Ledger: `Maps/Dashboards/Ledger.base`\n" if "money" in mods else ""
            act[1].write_text(HOME_MD.format(today=datetime.date.today().isoformat(), pipeline_line=pl, ledger_line=ll))
    print(f"\n{'Would perform' if a.dry_run else 'Done:'} {len(actions)} action(s) in {V}")
    if not a.dry_run:
        print("Next (Claude): write the vault CLAUDE.md from the onboarding interview "
              "(references/onboarding.md), then capture the user's first 2-3 real tasks.")

if __name__ == "__main__":
    main()
