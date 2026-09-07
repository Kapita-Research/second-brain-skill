#!/usr/bin/env python3
"""Inventory a folder or a repository so a bulk import can read six files instead of four hundred.

**"Record everything you know about this project" is the most expensive request in this skill.** Done
naively it reads the whole tree into the conversation - vendored libraries, lock files, build output,
every notebook cell - and most of it turns out to hold nothing worth a note.

This walks the tree, skips what is never worth reading, and prints **one line per file**: size, kind,
and the strongest signal it can get cheaply - a heading, a docstring, a CSV header, a commit subject.

    python scripts/survey.py <folder> [--out <dir>] [--max-files 4000] [--all]

**Read the inventory, pick the files that carry meaning, and open only those.** The rest stay on disk
and cost nothing.

## What it reports, in the order a bulk import needs it

1. **What this is** - languages, file counts, whether it is a git repository.
2. **The narrative files first** - `README`, docs, notebooks, `CHANGELOG`: where a project explains
   itself. **These are almost always the six files worth reading.**
3. **Recent commit subjects** when it is a repo - *the cheapest record of decisions that exists*, and
   usually the only one written at the time.
4. **Data files with their headers and row counts** - enough to know what a table holds without
   opening it.
5. **Everything else, grouped by directory**, one line each.
6. **And what it skipped**, with the rule that skipped it - so absence is never mistaken for emptiness.

⛔ **It reads no file content into your context.** Signals are extracted here and truncated hard.
`survey.json` holds the full inventory if you want to filter it with a script rather than by eye.
"""
import argparse
import io
import json
import os
import re
import subprocess
import sys

SKIP_DIRS = {".git", ".svn", "node_modules", "__pycache__", ".venv", "venv", "env", ".idea",
             ".vscode", "dist", "build", ".next", "target", ".pytest_cache", ".mypy_cache",
             "site-packages", ".cache", "coverage", ".tox", "vendor", "bower_components"}
SKIP_EXT = {".pyc", ".pyo", ".so", ".dll", ".dylib", ".exe", ".bin", ".lock", ".map", ".min.js",
            ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp", ".mp4", ".mp3", ".wav",
            ".zip", ".gz", ".tar", ".7z", ".rar", ".pdf", ".woff", ".woff2", ".ttf", ".eot"}
# Deliberately narrow. A bare "note" matches half of any vault and every template, and a list
# that surfaces everything surfaces nothing.
NARRATIVE = re.compile(r"^(readme|changelog|contributing|architecture|overview|roadmap|"
                       r"methodology|findings|conclusions|decisions|plan|spec|design|brief)"
                       r"|(_|-|)(architecture|methodology|design-doc|post-?mortem|retro)", re.I)
CODE = {".py", ".js", ".ts", ".tsx", ".jsx", ".r", ".sql", ".sh", ".ps1", ".java", ".go", ".rb",
        ".c", ".cpp", ".cs", ".rs", ".php", ".m"}
DATA = {".csv", ".tsv", ".json", ".jsonl", ".xlsx", ".parquet", ".geojson", ".xml", ".yaml", ".yml"}
DOC = {".md", ".txt", ".rst", ".org", ".ipynb"}


def head(path, n=4000):
    try:
        with io.open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read(n)
    except OSError:
        return ""


def signal(path, ext):
    """One line that says what this file is, got as cheaply as possible."""
    if ext in (".csv", ".tsv"):
        t = head(path, 2000).splitlines()
        cols = (t[0] if t else "")[:120]
        try:
            rows = sum(1 for _ in io.open(path, encoding="utf-8", errors="replace")) - 1
        except OSError:
            rows = -1
        return "%s rows | %s" % (rows if rows >= 0 else "?", cols)
    if ext == ".ipynb":
        try:
            nb = json.loads(head(path, 400000) or "{}")
        except ValueError:
            return "notebook (unparsed)"
        md = [c for c in nb.get("cells", []) if c.get("cell_type") == "markdown"]
        first = " ".join("".join(md[0].get("source", [])).split())[:110] if md else ""
        return "%d cells, %d markdown | %s" % (len(nb.get("cells", [])), len(md), first)
    t = head(path)
    if ext == ".md":
        for line in t.splitlines():
            if line.startswith("#"):
                return line.lstrip("# ").strip()[:120]
        return " ".join(t.split())[:110]
    if ext in CODE:
        m = re.search(r'"""(.+?)"""', t, re.S) or re.search(r"^\s*(?://|#)\s?(.+)$", t, re.M)
        return " ".join(m.group(1).split())[:110] if m else ""
    if ext == ".json":
        try:
            d = json.loads(t if len(t) < 3900 else t + "}")
            return "keys: " + ", ".join(list(d)[:8]) if isinstance(d, dict) else "array"
        except ValueError:
            return ""
    return " ".join(t.split())[:90]


def git_log(root, n=40):
    try:
        r = subprocess.run(["git", "-C", root, "log", "--oneline", "--no-merges", "-n", str(n)],
                           capture_output=True, text=True, timeout=20)
        return r.stdout.strip().splitlines() if r.returncode == 0 else []
    except (OSError, subprocess.SubprocessError):
        return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--out")
    ap.add_argument("--max-files", type=int, default=4000)
    ap.add_argument("--all", action="store_true", help="do not skip the usual noise directories")
    a = ap.parse_args()

    root = os.path.abspath(a.folder)
    if not os.path.isdir(root):
        print("no such folder: " + root)
        return 2

    files, skipped, n = [], {}, 0
    for b, dirs, fs in os.walk(root):
        if not a.all:
            for d in list(dirs):
                if d in SKIP_DIRS or d.startswith("."):
                    skipped[d] = skipped.get(d, 0) + 1
                    dirs.remove(d)
        for f in sorted(fs):
            ext = os.path.splitext(f)[1].lower()
            if not a.all and (ext in SKIP_EXT or f.startswith(".")):
                skipped[ext or "dotfile"] = skipped.get(ext or "dotfile", 0) + 1
                continue
            p = os.path.join(b, f)
            try:
                size = os.path.getsize(p)
            except OSError:
                continue
            n += 1
            if n > a.max_files:
                break
            kind = ("doc" if ext in DOC else "data" if ext in DATA else
                    "code" if ext in CODE else "other")
            files.append({"path": os.path.relpath(p, root).replace("\\", "/"), "kind": kind,
                          "ext": ext, "bytes": size,
                          "narrative": bool(NARRATIVE.search(f)) and kind == "doc",
                          "signal": signal(p, ext) if size < 2_000_000 else "(large - not sampled)"})

    log = git_log(root)
    out = a.out or root
    with io.open(os.path.join(out, "survey.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"root": root, "files": files, "commits": log, "skipped": skipped}, fh,
                  indent=1, ensure_ascii=False)

    kinds = {}
    for f in files:
        kinds[f["kind"]] = kinds.get(f["kind"], 0) + 1
    print("%s\n%d files - %s%s\n" % (root, len(files),
          " · ".join("%d %s" % (v, k) for k, v in sorted(kinds.items(), key=lambda x: -x[1])),
          " · git repo" if log else ""))

    def show(rows, title):
        if not rows:
            return
        print("== %s ==" % title)
        for f in rows:
            print("  %-52s %7d  %s" % (f["path"][:52], f["bytes"], f["signal"][:90]))
        print("")

    show([f for f in files if f["narrative"]], "Where the project explains itself - read these first")
    if log:
        print("== Recent commits - the cheapest record of decisions there is ==")
        for line in log[:25]:
            print("  " + line[:110])
        print("")
    show([f for f in files if f["kind"] == "data"], "Data - headers and row counts")
    rest = [f for f in files if not f["narrative"] and f["kind"] != "data"]
    by_dir = {}
    for f in rest:
        by_dir.setdefault(os.path.dirname(f["path"]) or ".", []).append(f)
    for d in sorted(by_dir):
        show(by_dir[d][:40], d + ("  (+%d more)" % (len(by_dir[d]) - 40) if len(by_dir[d]) > 40 else ""))

    if skipped:
        print("== Skipped, so that absence is not mistaken for emptiness ==")
        print("  " + " · ".join("%s (%d)" % (k, v) for k, v in
                                sorted(skipped.items(), key=lambda x: -x[1])[:12]))
        print("  Re-run with --all to include them.")
    print("\nFull inventory: %s" % os.path.join(out, "survey.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
