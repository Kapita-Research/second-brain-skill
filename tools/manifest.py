#!/usr/bin/env python3
"""Write MANIFEST.json - what each file in this repository is, and where it goes.

**This is the only file that knows a destination.** `update.py` installs from it, `test_all.py`
checks it, and nothing else hard-codes a path. When a file moves, one line changes here.

    python tools/manifest.py            # write MANIFEST.json
    python tools/manifest.py --check    # exit 1 if it is stale (a file changed, or is unclaimed)

## The four rules a destination can carry

| rule | what happens on update |
|---|---|
| `replace-tree` | the whole folder is mirrored, **and files no longer in the release are deleted** |
| `replace-file` | overwritten, with the previous copy kept as `.bak` |
| `create-if-missing` | written only when it is not there. **Never overwritten** - it is the owner's |
| `none` | ships in the repository, installs nowhere (docs, upstream sources, the tools) |

⛔ **Every file must be claimed by exactly one rule.** An unclaimed file is how a reference file that
was added in a release quietly never reaches anybody, so `--check` fails on it.
"""
import argparse
import hashlib
import io
import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# source (repo-relative)     rule                dest template
ENTRIES = [
    ("skill",                 "replace-tree",     "{skills}/obsidian-second-brain"),
    ("kapita-vault-KAPITA.md", "replace-file",    "{vault}/KAPITA.md"),
    ("dist/CLAUDE.md",        "create-if-missing", "{vault}/CLAUDE.md"),
    ("dist/CHECKLIST.md",     "none",             ""),
    ("dist/START-HERE.md",    "none",             ""),
    ("tools",                 "none",             ""),
    ("upstream",              "none",             ""),
    ("discarded",             "none",             ""),
    ("README.md",             "none",             ""),
    ("FORK-NOTES.md",         "none",             ""),
    ("FORK-PLAN.md",          "none",             ""),
    ("UPDATING.md",           "none",             ""),
    (".githooks",             "none",             ""),
    (".github",               "none",             ""),
    ("MANIFEST.json",         "none",             ""),
    (".gitignore",            "none",             ""),
    (".gitattributes",        "none",             ""),
]

SKIP_DIRS = {".git", "__pycache__", ".pytest_cache"}
SKIP_NAMES = {".DS_Store", "Thumbs.db"}


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def walk_files():
    for b, dirs, fs in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in sorted(fs):
            if f in SKIP_NAMES or f.endswith((".zip", ".pyc", ".bak")):
                continue
            p = os.path.join(b, f)
            yield os.path.relpath(p, ROOT).replace("\\", "/")


def claim(rel):
    """Which entry owns this file. Longest source wins, so `dist/CLAUDE.md` beats `dist`."""
    best = None
    for src, rule, dest in ENTRIES:
        if rel == src or rel.startswith(src.rstrip("/") + "/"):
            if best is None or len(src) > len(best[0]):
                best = (src, rule, dest)
    return best


def version():
    t = io.open(os.path.join(ROOT, "skill", "SKILL.md"), encoding="utf-8").read(4000)
    m = re.search(r'^\s*version:\s*"?([0-9.]+)"?', t, re.M)   # nested under `metadata:`
    return m.group(1) if m else "0"


def build():
    files, unclaimed = {}, []
    for rel in walk_files():
        if rel == "MANIFEST.json":
            continue
        c = claim(rel)
        if c is None:
            unclaimed.append(rel)
            continue
        files[rel] = sha(os.path.join(ROOT, rel))
    return {
        "release": version(),
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "entries": [{"source": s, "rule": r, "dest": d} for s, r, d in ENTRIES
                    if os.path.exists(os.path.join(ROOT, s))],
        "files": files,
    }, unclaimed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    fresh, unclaimed = build()
    path = os.path.join(ROOT, "MANIFEST.json")

    if unclaimed:
        print("UNCLAIMED - no rule says where these go (add one to ENTRIES):")
        for u in unclaimed:
            print("  " + u)
        return 1

    if a.check:
        if not os.path.exists(path):
            print("MANIFEST.json is missing. Run: python tools/manifest.py")
            return 1
        old = json.load(io.open(path, encoding="utf-8"))
        if old.get("files") != fresh["files"] or old.get("release") != fresh["release"]:
            added = sorted(set(fresh["files"]) - set(old.get("files", {})))
            gone = sorted(set(old.get("files", {})) - set(fresh["files"]))
            changed = sorted(k for k in fresh["files"]
                             if k in old.get("files", {}) and old["files"][k] != fresh["files"][k])
            print("MANIFEST.json is stale. Run: python tools/manifest.py")
            for label, items in (("added", added), ("removed", gone), ("changed", changed)):
                if items:
                    print("  %-8s %s" % (label, ", ".join(items[:8]) +
                                         (" ... +%d" % (len(items) - 8) if len(items) > 8 else "")))
            if old.get("release") != fresh["release"]:
                print("  release  %s -> %s" % (old.get("release"), fresh["release"]))
            return 1
        print("MANIFEST.json is current - release %s, %d files" % (fresh["release"], len(fresh["files"])))
        return 0

    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(fresh, fh, indent=1, ensure_ascii=False, sort_keys=False)
        fh.write("\n")
    print("MANIFEST.json written - release %s, %d files, %d entries"
          % (fresh["release"], len(fresh["files"]), len(fresh["entries"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
