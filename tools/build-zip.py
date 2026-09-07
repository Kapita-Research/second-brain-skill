#!/usr/bin/env python3
"""Assemble the archive that goes to a person.

    python tools/build-zip.py

Writes `../second-brain-<version>.zip`, version read from the skill's own frontmatter - so the
archive cannot be named one thing and contain another.

## What goes in, and what does not

    obsidian-second-brain/      the skill, minus evals/
    kapita-vault-KAPITA.md      the firm's layer -> becomes the vault's KAPITA.md
    dist/CLAUDE.md              the owner's starter file -> becomes the vault's CLAUDE.md
    (the skill's own CHANGELOG.md travels inside obsidian-second-brain/)
    START-HERE.md               the first thing opened; both branches
    tools/sync-vault.py         needed by an update
    tools/check-install.py      the install check every recipient runs
    CHECKLIST.md                the nine install steps, and the command that verifies them

⛔ **Excluded:** `evals/`, `upstream/`, `FORK-PLAN.md`, `discarded/`, and `check-kapita-layer.py` -
development material. **The layer checker in particular is ours: it compares two files a recipient
does not edit.**
"""
import io
import os
import re
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skill")


def version():
    text = io.open(os.path.join(SKILL, "SKILL.md"), encoding="utf-8").read(4000)
    m = re.search(r"^\s*version:\s*\"?([0-9.]+)\"?", text, re.M)
    return m.group(1) if m else None


def main():
    v = version()
    if not v:
        print("cannot read metadata.version from skill/SKILL.md")
        return 2

    out = os.path.join(os.path.dirname(ROOT), "second-brain-%s.zip" % v)
    n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for base, dirs, files in os.walk(SKILL):
            dirs[:] = [d for d in dirs if d not in ("evals", "__pycache__")]
            for f in files:
                p = os.path.join(base, f)
                z.write(p, "obsidian-second-brain/" + os.path.relpath(p, SKILL).replace("\\", "/"))
                n += 1
        for src, dst in (("kapita-vault-KAPITA.md", "kapita-vault-KAPITA.md"),
                         ("dist/CLAUDE.md", "dist/CLAUDE.md"),
                         ("dist/START-HERE.md", "START-HERE.md"),
                         ("dist/CHECKLIST.md", "CHECKLIST.md"),
                         ("tools/check-install.py", "tools/check-install.py"),
                         ("tools/sync-vault.py", "tools/sync-vault.py")):
            z.write(os.path.join(ROOT, src), dst)
            n += 1

    print("%s\n%d files, %.0f KB" % (out, n, os.path.getsize(out) / 1024.0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
