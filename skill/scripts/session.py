#!/usr/bin/env python3
"""Turn an old Claude Code conversation into something a bulk import can actually use.

**A long session is a 24 MB `.jsonl` of thirteen thousand lines. Almost none of it is worth reading.**
Inside it, though, sit the three things a second brain wants, and they are cheap to extract:

* **the owner's own messages** - 143 of those thirteen thousand lines, and where every decision,
  correction and reason actually lives;
* **the working directory** - so the project's files can be surveyed without being named;
* **every file the session touched**, split into what it *wrote* and what it only *read*.

    python scripts/session.py                      # THIS conversation, resolved from the cwd
    python scripts/session.py --list [filter]      # which conversations exist, newest first
    python scripts/session.py <jsonl | project dir> [--out DIR]

**With no argument it digests the session you are in.** *"Record this conversation" needs no name and no
UUID* - the transcript lives under a folder named after the working directory, and the live one is the
one being written to. ⚠️ **The last few messages may not be flushed yet**, so the run that asked for the
import is usually not in it.

🔴 **This is worth doing even though the conversation is already in context** - a long session has been
compacted, and *the transcript on disk still holds what the context window dropped.*

**Two stages, because the two costs are very different.** The digest it prints is about **three
thousand tokens** - enough to decide what this session was and what to pull from it. The full text of
the owner's messages is written to a file beside it, about **eighteen thousand** for a long session:
**read that only when you are actually extracting**, and read the files it names rather than the
transcript.

## The order it prints in, which is the order a bulk import needs

1. **What this session was** - when, where, which branch, how long.
2. **Files it wrote** - *this is what the project is.* A session's written files are its output;
   everything else is context it consulted.
3. **Files it only read** - what it depended on.
4. **The owner's messages, numbered and clipped** - skim for the decisions, then open the full file
   at the numbers that matter.
5. **What to run next** - `survey.py` on the working directory, which the transcript just told you.

⛔ **It reads no assistant output and no tool results into your context.** Those are the ninety-five
percent, and they are re-derivable from the files; the owner's own words are not.
"""
import argparse
import glob
import io
import json
import os
import re
import sys
import time

PROJECTS = os.path.join(os.path.expanduser("~"), ".claude", "projects")
NOISE = ("<", "[Request interrupted", "Caveat:", "This session is being continued")
PATH_KEYS = ("file_path", "path", "notebook_path")
WRITERS = {"Write", "Edit", "NotebookEdit", "MultiEdit"}


def lines(path):
    with io.open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                yield json.loads(line)
            except ValueError:
                continue


def text_of(content):
    if isinstance(content, str):
        return content
    return " ".join(b.get("text", "") for b in (content or [])
                    if isinstance(b, dict) and b.get("type") == "text")


def scan(path):
    """One pass. Returns the owner's messages, the paths, and what kind of session this was."""
    msgs, wrote, read_, tools, cwds, branches, stamps = [], {}, {}, {}, {}, {}, []
    for d in lines(path):
        if d.get("cwd"):
            cwds[d["cwd"]] = cwds.get(d["cwd"], 0) + 1
        if d.get("gitBranch"):
            branches[d["gitBranch"]] = branches.get(d["gitBranch"], 0) + 1
        if d.get("timestamp"):
            stamps.append(d["timestamp"][:19])
        m = d.get("message")
        if not isinstance(m, dict):
            continue
        if d.get("type") == "user" and m.get("role") == "user":
            t = text_of(m.get("content")).strip()
            if t and not t.startswith(NOISE):
                msgs.append(t)
        c = m.get("content")
        if isinstance(c, list):
            for b in c:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    name = b.get("name") or "?"
                    tools[name] = tools.get(name, 0) + 1
                    i = b.get("input") or {}
                    for k in PATH_KEYS:
                        if i.get(k):
                            (wrote if name in WRITERS else read_)[i[k]] = \
                                (wrote if name in WRITERS else read_).get(i[k], 0) + 1
    return msgs, wrote, read_, tools, cwds, branches, stamps


def current_session():
    """The transcript of the session we are running inside, found from the working directory.

    Claude Code names a project folder after its cwd with every non-alphanumeric character
    replaced by a dash, so a Windows path becomes `C--Users-me-x`. The slug is tried first
    because it is instant; if it misses, every project's first line is checked for a matching
    `cwd`, which is exact.
    """
    cwd = os.getcwd()
    cand = os.path.join(PROJECTS, re.sub(r"[^A-Za-z0-9]", "-", cwd))
    pools = [cand] if os.path.isdir(cand) else sorted(glob.glob(os.path.join(PROJECTS, "*")))
    best, best_mt = None, -1
    for pool in pools:
        for f in glob.glob(os.path.join(pool, "*.jsonl")):
            try:
                mt = os.path.getmtime(f)
            except OSError:
                continue
            if mt <= best_mt:
                continue
            if pool is not cand:                       # verify by the cwd the file records
                ok = False
                for d in lines(f):
                    if d.get("cwd"):
                        ok = os.path.normcase(d["cwd"]) == os.path.normcase(cwd)
                        break
                if not ok:
                    continue
            best, best_mt = f, mt
    return best, best_mt


def list_sessions(filt):
    rows = []
    for p in sorted(glob.glob(os.path.join(PROJECTS, "*"))):
        proj = os.path.basename(p)
        if filt and filt.lower() not in proj.lower():
            continue
        for f in glob.glob(os.path.join(p, "*.jsonl")):
            try:
                st = os.stat(f)
            except OSError:
                continue
            first, n = "", 0
            for d in lines(f):
                if d.get("type") == "user" and isinstance(d.get("message"), dict):
                    t = text_of(d["message"].get("content")).strip()
                    if t and not t.startswith(NOISE):
                        n += 1
                        if not first:
                            first = " ".join(t.split())[:70]
                if n > 400:
                    break
            rows.append((st.st_mtime, st.st_size, n, proj, os.path.basename(f), first))
    rows.sort(reverse=True)
    print("%-10s %7s %5s  %s" % ("last used", "size", "msgs", "project / opening message"))
    for mt, sz, n, proj, fn, first in rows[:60]:
        print("%-10s %6.1fM %5d  %s" % (time.strftime("%Y-%m-%d", time.localtime(mt)),
                                        sz / 1048576.0, n, proj))
        print("%25s%s\n%25s%s" % ("", fn, "", first))
    print("\n%d conversation(s). Pass one of the .jsonl paths back to this script." % len(rows))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--clip", type=int, default=220)
    a = ap.parse_args()

    if a.list:
        return list_sessions(a.target)

    t = a.target
    if not t:
        t, mt = current_session()
        if not t:
            print("could not find a transcript for this working directory.")
            print("Run --list to pick one, or pass a .jsonl path.")
            return 2
        print("this conversation: %s  (last written %s)"
              % (os.path.basename(t), time.strftime("%H:%M:%S", time.localtime(mt))))
        print("")
    if os.path.isdir(t):
        js = sorted(glob.glob(os.path.join(t, "*.jsonl")), key=os.path.getmtime, reverse=True)
        if not js:
            print("no .jsonl transcripts in " + t)
            return 2
        t = js[0]
        print("(newest transcript in that folder: %s)\n" % os.path.basename(t))
    if not os.path.exists(t):
        print("no such file: " + t)
        return 2

    msgs, wrote, read_, tools, cwds, branches, stamps = scan(t)
    out = a.out or os.path.dirname(os.path.abspath(t))
    sid = os.path.splitext(os.path.basename(t))[0]
    full = os.path.join(out, "session-%s.md" % sid[:8])

    with io.open(full, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# Owner's messages - %s\n\n_%d messages, %s to %s_\n\n" %
                 (sid, len(msgs), stamps[0] if stamps else "?", stamps[-1] if stamps else "?"))
        for i, m in enumerate(msgs, 1):
            fh.write("\n## %d\n\n%s\n" % (i, m))

    print("== What this session was ==")
    print("  %s  ->  %s" % (stamps[0][:10] if stamps else "?", stamps[-1][:10] if stamps else "?"))
    print("  %.1f MB transcript · %d owner messages · %d tool calls"
          % (os.path.getsize(t) / 1048576.0, len(msgs), sum(tools.values())))
    for c, n in sorted(cwds.items(), key=lambda x: -x[1])[:3]:
        print("  worked in: %s" % c)
    if branches:
        print("  branch: %s" % ", ".join(sorted(branches)))
    print("  tools: %s\n" % ", ".join("%s %d" % (k, v) for k, v in
                                      sorted(tools.items(), key=lambda x: -x[1])[:8]))

    def paths(d, title, limit=40):
        if not d:
            return
        print("== %s (%d) ==" % (title, len(d)))
        for p, n in sorted(d.items(), key=lambda x: -x[1])[:limit]:
            print("  %-4d %s" % (n, p))
        if len(d) > limit:
            print("  ... and %d more" % (len(d) - limit))
        print("")

    paths(wrote, "Files it WROTE - this is what the project is")
    paths(read_, "Files it only read - what it depended on", 25)

    print("== The owner's messages, clipped - full text in %s ==" % os.path.basename(full))
    for i, m in enumerate(msgs, 1):
        one = " ".join(m.split())
        print("  %3d  %s%s" % (i, one[:a.clip], " ..." if len(one) > a.clip else ""))
    print("")

    print("== Next ==")
    if cwds:
        top = sorted(cwds.items(), key=lambda x: -x[1])[0][0]
        print('  python scripts/survey.py "%s"' % top)
        print("  - the project's own files, which this transcript just told you where to find")
    print("  Read %s at the numbers that mattered, then extract by the sweeps in" % os.path.basename(full))
    print("  references/capture-and-web.md -> Bulk import.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
