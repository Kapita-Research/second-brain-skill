#!/usr/bin/env python3
"""Is the second brain actually working on this machine?

Two dozen checks, each with the one thing to do when it fails. Nothing is changed - this only looks.

**Some of what the skill needs is outside the skill** - a block in `~/.claude/CLAUDE.md`, two hooks in
`~/.claude/settings.json`, the vault's two root files, the owner's own person note, Obsidian's CLI. Those are the ones people skip, so they
are checked here and marked REQUIRED when the skill will not work properly without them.

    python tools/check-install.py                 # find the vault automatically
    python tools/check-install.py "<vault>"       # or name it

Exit 0 = nothing REQUIRED is missing. Exit 1 = at least one required thing to fix.
Optional lines never fail the run; they print what you give up by not having them.

Written to be run by someone else's Claude in a fresh conversation: paste the output back and the
failing lines say what to do.
"""
import io
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HOME = os.path.expanduser("~")
CLAUDE_DIR = os.path.join(HOME, ".claude")
INSTALLED = os.path.join(CLAUDE_DIR, "skills", "obsidian-second-brain")

rows = []          # (ok, name, detail, fix, required)


def check(ok, name, detail="", fix="", required=True):
    """required=False -> a real capability, but the skill works without it. Never fails the run."""
    rows.append((bool(ok), name, detail, fix, required))
    return bool(ok)


def read(p):
    with io.open(p, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def source_skill():
    """The skill folder shipped beside this script: `skill/` in the repo, `obsidian-second-brain/` in the archive."""
    for n in ("skill", "obsidian-second-brain"):
        p = os.path.join(ROOT, n)
        if os.path.exists(os.path.join(p, "SKILL.md")):
            return p
    return None


def find_vault(argv):
    """Named on the command line, or in ~/.claude/CLAUDE.md, or the last vault Obsidian opened."""
    if len(argv) > 1 and os.path.isdir(argv[1]):
        return argv[1], "named on the command line"
    g = os.path.join(CLAUDE_DIR, "CLAUDE.md")
    if os.path.exists(g):
        m = re.search(r"`([A-Za-z]:\\[^`]+|/[^`]+)`", read(g))
        if m and os.path.isdir(m.group(1)):
            return m.group(1), "from ~/.claude/CLAUDE.md"
    oj = os.path.join(os.environ.get("APPDATA", ""), "obsidian", "obsidian.json")
    if os.path.exists(oj):
        try:
            vaults = json.loads(read(oj)).get("vaults", {})
            best = sorted(vaults.values(), key=lambda v: v.get("ts", 0), reverse=True)
            for v in best:
                p = v.get("path", "")
                if os.path.isdir(p) and os.path.exists(os.path.join(p, "KAPITA.md")):
                    return p, "the vault Obsidian opened most recently"
        except (ValueError, OSError):
            pass
    return None, "not found"


def main(argv):
    print("Second brain - install check")
    print("")

    # 1 - python
    v = sys.version_info
    check(v >= (3, 8), "Python 3.8+", "%d.%d.%d" % (v[0], v[1], v[2]),
          "install Python 3 and make sure `python` runs it")

    # 2..3 - the skill itself
    sk = os.path.join(INSTALLED, "SKILL.md")
    if check(os.path.exists(sk), "Skill installed", INSTALLED,
             "copy the `obsidian-second-brain` folder into " + os.path.join(CLAUDE_DIR, "skills")):
        head = read(sk)[:4000]
        ver = re.search(r'version:\s*"?([^"\n]+)"?', head)
        base = re.search(r'upstream_base:\s*"?([^"\n]+)"?', head)
        check(ver, "Skill version readable", ver.group(1).strip() if ver else "-",
              "SKILL.md frontmatter is damaged - reinstall the skill folder")
        if base:
            check(True, "Built on upstream", base.group(1).strip())
        src = source_skill()
        if src:
            import hashlib
            h = lambda p: hashlib.sha256(io.open(p, "rb").read()).hexdigest()
            diff = []
            for b, d, fs in os.walk(src):
                d[:] = [x for x in d if x not in ("evals", "__pycache__")]
                for f in fs:
                    a = os.path.join(b, f)
                    t = os.path.join(INSTALLED, os.path.relpath(a, src))
                    if not os.path.exists(t) or h(a) != h(t):
                        diff.append(os.path.relpath(a, src))
            check(not diff, "Installed copy matches this package",
                  "identical" if not diff else "%d file(s) differ" % len(diff),
                  "re-copy the whole `obsidian-second-brain` folder over the installed one")

    # 4 - the vault
    vault, how = find_vault(argv)
    if not check(vault, "Vault folder found", (vault or "") + ("  (%s)" % how if vault else ""),
                 "run again as: python tools/check-install.py \"<path to your notes folder>\""):
        report()
        return 1

    # 5..7 - the two root files
    ck = os.path.join(vault, "CLAUDE.md")
    kk = os.path.join(vault, "KAPITA.md")
    check(os.path.exists(ck), "Vault CLAUDE.md (yours)", "",
          "copy `dist/CLAUDE.md` from the package into the vault root")
    if check(os.path.exists(kk), "Vault KAPITA.md (the firm's)", "",
             "copy `kapita-vault-KAPITA.md` into the vault root, renamed KAPITA.md"):
        t = read(kk)
        check("Shared/" not in t and "Outbox" in t, "KAPITA.md is current",
              "up to date" if "Shared/" not in t else "still says Shared/ - it is out of date",
              "replace KAPITA.md with the copy from this package (it is replaced whole, always)")

    # 8 - property types
    tj = os.path.join(vault, ".obsidian", "types.json")
    src = source_skill()
    if check(os.path.exists(tj), "Obsidian property types present", "",
             "open the vault in Obsidian once, then run tools/sync-vault.py \"<vault>\" --fix"):
        try:
            have = set(json.loads(read(tj))["types"])
            want = set(json.loads(read(os.path.join(src, "assets", "types.json")))["types"]) if src else set()
            missing = sorted(want - have)
            check(not missing, "Property types up to date",
                  "%d defined" % len(have) if not missing else "%d missing: %s" % (len(missing), ", ".join(missing[:6])),
                  "python tools/sync-vault.py \"%s\" --fix" % vault)
        except (ValueError, KeyError, OSError):
            check(False, "Property types up to date", "types.json will not parse",
                  "restore it: python tools/sync-vault.py \"%s\" --fix" % vault)

    # 9 - templates
    td = os.path.join(vault, "Templates")
    n = len([f for f in os.listdir(td)]) if os.path.isdir(td) else 0
    check(n >= 10, "Templates installed", "%d files" % n,
          "python tools/sync-vault.py \"%s\" --fix" % vault)

    # 10 - the views, and the leak that hides
    bases = []
    for b, d, fs in os.walk(vault):
        d[:] = [x for x in d if not x.startswith(".")]
        bases += [os.path.join(b, f) for f in fs if f.endswith(".base")]
    if check(bases, "Dashboard views installed", "%d .base files" % len(bases),
             "copy assets/bases/*.base into the vault (usually Maps/Dashboards/)"):
        bad = [os.path.basename(p) for p in bases
               if read(p).count("name:") > read(p).count('inFolder("Templates")')]
        check(not bad, "Views exclude Templates/",
              "all views" if not bad else "missing in: " + ", ".join(bad),
              "replace those .base files with the ones in this package - without this, "
              "your templates are counted as real data")

    # 11 - the owner's own record. Without it, "look it up before writing anything about me"
    #      has nothing to look at.
    pd = os.path.join(vault, "People")
    me = os.path.join(pd, "Me.md")
    found = os.path.exists(me)
    if not found and os.path.isdir(pd):
        for f in os.listdir(pd):
            if f.endswith(".md") and "vault owner" in read(os.path.join(pd, f)).lower():
                found, me = True, os.path.join(pd, f)
                break
    check(found, "Your own person note", os.path.basename(me) if found else "",
          "tell Claude: \"write my own note\" - your name, its spellings, title, employer and "
          "addresses. Without it, anything written on your behalf has nothing to look up and "
          "falls back to [your name]")

    # 11b - the index of what else is installed. Optional, but it is the difference between
    #       owning a capability and remembering it on the day it is needed.
    sk_root = os.path.join(os.path.expanduser("~"), ".claude", "skills")
    installed = sorted(d for d in (os.listdir(sk_root) if os.path.isdir(sk_root) else [])
                       if os.path.isdir(os.path.join(sk_root, d)))
    if len(installed) > 1:
        index, named = None, 0
        for b, _, fs in os.walk(vault):
            if ".obsidian" in b or "Templates" in b:
                continue
            for f in fs:
                if not f.endswith(".md"):
                    continue
                t = read(os.path.join(b, f))
                if "claude/skills" in t.replace("\\", "/"):
                    hits = sum(1 for d in installed if d in t)
                    if hits > named:
                        index, named = os.path.join(b, f), hits
        check(index, "Installed skills indexed in the vault",
              "%s - %d of %d named" % (os.path.basename(index), named, len(installed))
              if index else "%d skills installed, none recorded" % len(installed),
              "tell Claude: \"index my installed skills in the vault\". One note, one line per "
              "skill: what it is for and where it lives. Pointers only - never copy a colour, a "
              "template or a threshold out of a skill, because the skill is maintained and the "
              "copy is not", required=False)

    # 11c - the daily update check. Required: a machine nobody tells about a release runs last
    #       month's rules while everybody else has moved on.
    tasks = os.path.join(CLAUDE_DIR, "scheduled-tasks")
    routine = None
    if os.path.isdir(tasks):
        for d in sorted(os.listdir(tasks)):
            sk = os.path.join(tasks, d, "SKILL.md")
            if os.path.exists(sk) and "update.py" in read(sk):
                routine = d
                break
    rel = os.path.join(CLAUDE_DIR, "second-brain-release.json")
    # 11d - where a release arrives from. Optional: the browser fallback works, it is just the
    #       same work every time instead of once.
    try:
        sys.path.insert(0, HERE)
        import update as _up
        drive = _up.drive_dir()
        rel_avail, _arch, _f = _up.drive_latest()
    except Exception:                                            # noqa: BLE001 - never fail the check
        drive, rel_avail = None, None
    check(drive, "Shared release folder reachable",
          ("%s%s" % (os.path.basename(drive), "  (offers %s)" % rel_avail if rel_avail else ""))
          if drive else "Google Drive for desktop is not syncing it",
          "install Google Drive for desktop and sync the shared folder, and every update becomes a "
          "file read. Without it you will be asked, each time a release comes out, to download the "
          "archive from the browser and hand it over - the same work every time instead of once",
          required=False)

    check(routine, "Daily update check scheduled", routine or "",
          "tell Claude: \"set up the daily second brain update check\". Once a day it asks whether a "
          "newer release exists and says nothing when there is not one. Without it this machine "
          "keeps running whatever it has, and nobody finds out")
    if os.path.exists(rel):
        try:
            check(True, "  ...and a release is recorded",
                  json.loads(read(rel)).get("release", "?"))
        except ValueError:
            check(False, "  ...and a release is recorded", "second-brain-release.json will not parse",
                  "run: python tools/update.py", required=False)

    # 11e - the firm's publishing rules, where every conversation reads them. The layer itself is
    #       only read when the vault is, so a deck built in another folder never sees them.
    gmd = read(os.path.join(CLAUDE_DIR, "CLAUDE.md"))
    check("second-brain:publishing-rules" in gmd, "Publishing rules in ~/.claude/CLAUDE.md",
          "present" if "second-brain:publishing-rules" in gmd else "",
          "run the updater once: python tools/update.py. It copies the short form out of KAPITA.md "
          "into your global CLAUDE.md between markers, and refreshes it on every update - without it "
          "the rule only applies in conversations that happen to open the vault")

    # 12..14 - Obsidian
    app = None
    for p in (os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Obsidian"),
              os.path.join(os.environ.get("LOCALAPPDATA", ""), "Obsidian"),
              os.path.join(os.environ.get("PROGRAMFILES", ""), "Obsidian"),
              "/Applications/Obsidian.app"):
        if p and os.path.exists(p):
            app = p
            break
    check(app, "Obsidian installed", app or "",
          "free, from obsidian.md. Without it every view becomes a question you have to ask "
          "instead of something you can see", required=False)
    check(os.path.isdir(os.path.join(vault, ".obsidian")), "Vault opened in Obsidian at least once", "",
          "open Obsidian -> Open folder as vault -> pick the vault folder", required=False)
    cli = shutil.which("obsidian") or shutil.which("obsidian.com")
    check(cli, "Obsidian CLI enabled", cli or "",
          "Obsidian -> Settings -> General -> Command line interface, then "
          "\"Set up CLI to work in the terminal\" -> Register. The toggle alone is not enough. "
          "Without it, search matches text instead of using the live index", required=False)

    # 14 - automatic capture
    g = os.path.join(CLAUDE_DIR, "CLAUDE.md")
    if check(os.path.exists(g), "Automatic capture configured", g,
             "ask Claude: \"set up automatic capture\". It appends a short block to this file, which is "
             "read at the start of every conversation. Without it the skill only starts when you name "
             "it - and you will not name it, you will just talk about your work"):
        t = read(g)
        check("obsidian-second-brain" in t, "  ...and it names the skill", "",
              "the block is missing or damaged - ask Claude to add it again")

    # A file of instructions can be drifted past over a long conversation. A hook is run by the
    # harness, so it cannot be - which is why both exist.
    st = os.path.join(CLAUDE_DIR, "settings.json")
    events = []
    if os.path.exists(st):
        try:
            hooks = json.loads(read(st)).get("hooks", {})
            for ev in ("SessionStart", "UserPromptSubmit"):
                for entry in hooks.get(ev, []):
                    if any("second brain" in (h.get("command") or "").lower()
                           for h in entry.get("hooks", [])):
                        events.append(ev)
                        break
        except ValueError:
            check(False, "settings.json parses", "malformed",
                  "a broken settings.json silently disables every setting in it - fix the JSON")
    guard = False
    if os.path.exists(st):
        try:
            for entry in json.loads(read(st)).get("hooks", {}).get("PreToolUse", []):
                if any("guard_judgements" in (h.get("command") or "")
                       for h in entry.get("hooks", [])):
                    guard = True
        except ValueError:
            pass
    check(guard, "Judgement guard armed", "PreToolUse" if guard else "",
          "ask Claude: \"arm the judgement guard\". A PreToolUse hook that turns any read of a "
          "judgement note into a prompt you answer. Every other protection for private opinions is "
          "an instruction a model follows; this one the harness runs, and a model cannot approve "
          "its own way past it", required=False)
    check(len(events) == 2, "Standing reminder enforced by hooks",
          " + ".join(events) if events else "",
          "ask Claude: \"enforce the second brain with hooks\". Two hooks in ~/.claude/settings.json - "
          "one per session, one per message. The CLAUDE.md block is an instruction that can be drifted "
          "past in a long conversation; a hook is run by the harness and cannot be")

    # 15 - does the vault actually validate
    if src:
        vs = os.path.join(src, "scripts", "validate_vault.py")
        if os.path.exists(vs):
            # The vault's CLAUDE.md carries the vocabulary it has invented. Running without it
            # reports an error on notes that were written exactly as the skill instructs.
            cmd = [sys.executable, vs, vault]
            if os.path.exists(ck):
                ct = read(ck)
                for key, flag in (("extra-types", "--extra-types"),
                                  ("extra-statuses", "--extra-statuses")):
                    m = re.search(r"^" + key + r":\s*(.+)$", ct, re.M)
                    vals = [v.strip() for v in m.group(1).split(",")] if m else []
                    vals = [v for v in vals if v and not v.startswith("[")]
                    if vals:
                        cmd += [flag, ",".join(vals)]
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                m = re.search(r"ERRORS:\s*(\d+)", r.stdout or "")
                errs = int(m.group(1)) if m else -1
                check(errs == 0, "Vault validates", "%d error(s)" % errs if errs >= 0 else "could not read the result",
                      "python \"%s\" \"%s\"  - and read what it lists" % (vs, vault))
            except (OSError, subprocess.SubprocessError):
                check(False, "Vault validates", "could not run the validator", "")

    return report()


def report():
    width = max(len(n) for _, n, _, _, _ in rows) + 2
    must = [r for r in rows if not r[0] and r[4]]
    opt = [r for r in rows if not r[0] and not r[4]]
    for ok, name, detail, _, req in rows:
        mark = "x" if ok else (" " if req else "-")
        print("  [%s] %-*s %s" % (mark, width, name, detail))
    print("")

    if must:
        print("%d REQUIRED - the skill will not work properly until these are done:" % len(must))
        print("")
        for _, name, _, fix, _ in must:
            print("  ! %s" % name)
            print("      -> %s" % (fix or "no fix recorded"))
        print("")
    if opt:
        print("%d optional - everything works without them, and here is what you give up:" % len(opt))
        print("")
        for _, name, _, fix, _ in opt:
            print("  - %s" % name)
            print("      -> %s" % (fix or ""))
        print("")
    if not must and not opt:
        print("All %d checks pass. Nothing to do." % len(rows))
    elif not must:
        print("Nothing required is missing - the skill works. The optional lines above are capability "
              "you do not have yet.")
    return 1 if must else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
