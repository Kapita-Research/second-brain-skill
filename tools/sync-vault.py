#!/usr/bin/env python3
"""Bring a vault's scaffold up to date with the skill.

The skill is replaced wholesale on every update. **A vault is not.** Three things were copied into
it once, at creation, and do not update themselves:

    .obsidian/types.json      property types - without them a date shows as plain text
    Templates/*.md            the note templates
    Maps/Dashboards/*.base    the views

So a person can be running skill 3.0 against a vault scaffolded by 2.9.2, with no error anywhere -
a `Findings` view that filters on a property the vault has never heard of simply returns nothing.

    python tools/sync-vault.py "<vault>"          # report
    python tools/sync-vault.py "<vault>" --fix    # apply

Exit 0 = nothing to do.

## What --fix will and will not touch

**Merges** new property types. **Never overwrites an existing one** - if the vault says a property
is `text` and the skill says `date`, that is a disagreement a person has to settle, and it is
reported, not resolved.

**Copies** templates the vault does not have. **Never overwrites one it does** - a template is
edited by its owner.

⛔ **Bases are reported, never copied.** A missing `.base` usually means a module was deliberately
not enabled, and adding it back would undo that choice silently.

⛔ **Nothing is deleted, and no note is touched.** The retired `publish:` key is reported with its
line numbers; removing it stays a decision, taken with the file open.
"""
import io
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def find_assets():
    """The skill folder is named `skill/` in the repo and `obsidian-second-brain/` in the archive."""
    for name in ("skill", "obsidian-second-brain"):
        p = os.path.join(ROOT, name, "assets")
        if os.path.exists(os.path.join(p, "types.json")):
            return p
    for name in sorted(os.listdir(ROOT)):
        p = os.path.join(ROOT, name, "assets")
        if os.path.exists(os.path.join(p, "types.json")):
            return p
    return None


ASSETS = find_assets()


def load(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main(argv):
    if len(argv) < 2:
        print(__doc__.split("##")[0].strip())
        return 2
    vault = os.path.abspath(argv[1])
    fix = "--fix" in argv[2:]

    if not os.path.isdir(vault):
        print("no such folder: " + vault)
        return 2
    if not ASSETS:
        print("cannot find the skill's assets/ next to " + ROOT)
        return 2

    todo = []      # things --fix can do
    decide = []    # things only a person can settle

    # 1 - property types
    vt_path = os.path.join(vault, ".obsidian", "types.json")
    if not os.path.exists(vt_path):
        decide.append("no .obsidian/types.json - is this a vault, or has Obsidian never opened it?")
    else:
        skill_types = load(os.path.join(ASSETS, "types.json"))["types"]
        vault_doc = load(vt_path)
        vault_types = vault_doc.get("types", {})
        missing = {k: v for k, v in skill_types.items() if k not in vault_types}
        clash = [k for k in skill_types if k in vault_types and skill_types[k] != vault_types[k]]
        for k in sorted(missing):
            todo.append(("property", k, "add as " + missing[k]))
        for k in sorted(clash):
            decide.append("property `%s`: vault says %s, skill says %s - settle by hand"
                          % (k, vault_types[k], skill_types[k]))
        if fix and missing:
            vault_types.update(missing)
            vault_doc["types"] = vault_types
            with io.open(vt_path, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(vault_doc, fh, indent=2, ensure_ascii=False)
                fh.write("\n")

    # 2 - templates
    tdir = os.path.join(vault, "Templates")
    if os.path.isdir(tdir):
        src = os.path.join(ASSETS, "templates")
        for f in sorted(os.listdir(src)):
            if f.endswith(".md") and not os.path.exists(os.path.join(tdir, f)):
                todo.append(("template", f, "copy into Templates/"))
                if fix:
                    shutil.copy2(os.path.join(src, f), os.path.join(tdir, f))

    # 3 - bases, reported only
    have = set()
    for base, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        have.update(f for f in files if f.endswith(".base"))
    for f in sorted(os.listdir(os.path.join(ASSETS, "bases"))):
        if f.endswith(".base") and f not in have:
            decide.append("no `%s` - copy it in only if you want that module; absence is usually "
                          "a choice" % f)

    # 4 - the retired publish: key
    hits = []
    for base, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if f.endswith(".md"):
                p = os.path.join(base, f)
                try:
                    text = io.open(p, encoding="utf-8").read()
                except (UnicodeDecodeError, OSError):
                    continue
                for i, line in enumerate(text.splitlines(), 1):
                    if re.match(r"^publish:", line):
                        hits.append("%s:%d" % (os.path.relpath(p, vault), i))
    if hits:
        decide.append("`publish:` on %d note(s) - dormant until somebody subscribes to Obsidian "
                      "Publish, and then every one of them goes live at once. Delete by hand: %s"
                      % (len(hits), ", ".join(hits[:8]) + (" ..." if len(hits) > 8 else "")))

    # report
    if todo:
        print(("applied %d change(s):" if fix else "%d change(s) --fix would make:") % len(todo))
        for kind, name, what in todo:
            print("  %-9s %-28s %s" % (kind, name, what))
        print("")
    if decide:
        print("%d thing(s) --fix will not touch:" % len(decide))
        for d in decide:
            print("  - " + d)
        print("")
    if not todo and not decide:
        print("vault scaffold matches the skill")
        return 0
    if todo and not fix:
        print("re-run with --fix to apply.")
    return 1 if (decide or (todo and not fix)) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
