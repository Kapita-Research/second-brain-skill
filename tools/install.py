#!/usr/bin/env python3
"""Install the whole second brain on a machine that has nothing, in one run.

    python install.py                    # everything, with sensible defaults
    python install.py --vault "<path>"   # put the notes folder somewhere specific
    python install.py --dry-run          # say what it would do, change nothing

**Written to be run by somebody's Claude, not by them.** The person says one sentence and answers no
questions: every choice here has a defensible default, and a person who has not used the thing yet has
no basis for choosing anyway. **Anything genuinely theirs - their own name, what they work on - belongs
in the first conversation, not in a form.**

## What it does, in order

1. **Checks Python**, and stops with the download link if it is too old.
2. **Finds the release** - the shared Drive folder if it is on this machine, otherwise the clone this
   script sits in - **and verifies the archive against `latest.json` before unpacking it.**
3. **Creates the notes folder and scaffolds it**: folders, templates, dashboards, property types.
4. **Installs the skill and the two root files** through `update.py`, which verifies every file by hash
   after it lands.
5. **Merges three hooks into `~/.claude/settings.json`** and appends the standing block to
   `~/.claude/CLAUDE.md` - the two things outside the vault that the skill does not work properly
   without.
6. **Runs the install check** and prints it.

⛔ **Nothing is overwritten that belongs to the person.** `settings.json` is merged and backed up, the
standing block is appended only if absent, and an existing vault is scaffolded additively.

## What it deliberately leaves to Claude

**The daily update routine, the index of installed skills, and the owner's own person note.** Those
need a scheduler, a reading pass, or a conversation - not a script - and the checklist tells Claude to
do them right after this finishes.
"""
import argparse
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")
CLAUDE_DIR = os.path.join(HOME, ".claude")
SETTINGS = os.path.join(CLAUDE_DIR, "settings.json")
GLOBAL_MD = os.path.join(CLAUDE_DIR, "CLAUDE.md")

SESSION_RULE = (
    "STANDING RULE - second brain. This user keeps a vault of Markdown notes, read and written "
    "through the obsidian-second-brain skill. Every conversation is one of two things: it has prior "
    "context in that vault, or it produces context for it - there is no third kind. So: before "
    "answering anything that involves a person, a project, a client, a decision, a commitment, a "
    "figure or a date, SEARCH THE VAULT FIRST and do not answer from this conversation alone. The "
    "moment something worth keeping is said, RECORD IT. Keep doing both as the conversation goes on, "
    "not only at the start. Reading one note is not searching. Do not announce either action, do not "
    "ask permission to write a note, and do ask before anything leaves the vault. The vault path and "
    "the full rules are in ~/.claude/CLAUDE.md.")
PROMPT_RULE = (
    "Second brain: if this turn touches a person, project, client, decision, commitment, figure or "
    "date - search the vault before answering. If it produces one - record it. Neither is announced.")

VERSION_RE = r'^\s*version:\s*"?([0-9.]+)"?'
steps = []


def say(ok, what, detail=""):
    steps.append((ok, what, detail))
    print("  %s %-42s %s" % ("[x]" if ok else "[!]", what, detail))


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read(p):
    try:
        with io.open(p, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def find_release(tmp):
    """Unpack the newest release somewhere usable, from wherever this machine can reach one."""
    # (a) this script sitting in the shared folder, beside latest.json and the archive
    meta_path = os.path.join(HERE, "latest.json")
    if os.path.exists(meta_path):
        try:
            meta = json.loads(read(meta_path))
        except ValueError:
            meta = {}
        z = os.path.join(HERE, meta.get("zip", ""))
        if os.path.exists(z):
            if meta.get("sha256") and sha(z) != meta["sha256"]:
                return None, ("the archive in this folder does not match latest.json - it is probably "
                              "still syncing. Try again in a minute.")
            with zipfile.ZipFile(z) as zf:
                zf.extractall(tmp)
            root = tmp
            if not os.path.exists(os.path.join(root, "MANIFEST.json")):
                for d in os.listdir(tmp):
                    if os.path.exists(os.path.join(tmp, d, "MANIFEST.json")):
                        root = os.path.join(tmp, d)
                        break
            return root, "release %s, from the shared folder" % meta.get("release", "?")
    # (b) this script inside a clone
    repo = os.path.dirname(HERE)
    if os.path.exists(os.path.join(repo, "MANIFEST.json")):
        return repo, "this clone"
    # (c) a Drive folder somewhere else on the machine
    sys.path.insert(0, HERE)
    try:
        import update as up
        release, archive, folder = up.drive_latest()
        if archive and archive != "PARTIAL":
            with zipfile.ZipFile(archive) as zf:
                zf.extractall(tmp)
            return tmp, "release %s, from %s" % (release, folder)
    except Exception:                                            # noqa: BLE001 - fall through
        pass
    return None, ("no release found. Put this script in the shared folder beside latest.json, or run "
                  "it from a clone of the repository.")


def default_vault():
    """Somewhere synced, because these are the person's notes and a lost laptop should not take them."""
    from_global = re.search(r"`([A-Za-z]:\\[^`]+|/[^`]+)`", read(GLOBAL_MD))
    if from_global and os.path.isdir(from_global.group(1)):
        return from_global.group(1)
    for base in (os.path.join(HOME, "OneDrive", "Documents"),
                 os.path.join(HOME, "Documents"),
                 HOME):
        if os.path.isdir(base):
            return os.path.join(base, "Second Brain")
    return os.path.join(HOME, "Second Brain")


def standing_block(root, vault):
    """The block for ~/.claude/CLAUDE.md, taken from the skill's own onboarding reference.

    Lifted rather than copied: two texts that must agree is the drift this project keeps paying for.
    """
    t = read(os.path.join(root, "skill", "references", "onboarding.md")) or \
        read(os.path.join(root, "obsidian-second-brain", "references", "onboarding.md"))
    m = re.search(r"```markdown\n(## Every conversation is one of two things.*?)```", t, re.S)
    if not m:
        return None
    return m.group(1).replace("<their vault path>", vault).strip() + "\n"


def merge_hooks(root, dry):
    """Three hooks, merged into whatever is already there. A malformed file loses every setting in it."""
    guard = os.path.join(CLAUDE_DIR, "skills", "obsidian-second-brain", "scripts",
                         "guard_judgements.py").replace("\\", "/")
    pending = os.path.join(CLAUDE_DIR, "skills", "obsidian-second-brain", "scripts",
                           "pending_update.py").replace("\\", "/")

    def echo(event, text):
        return ("echo '{\"hookSpecificOutput\": {\"hookEventName\": \"%s\", "
                "\"additionalContext\": \"%s\"}}'" % (event, text))

    wanted = [
        ("SessionStart", None, echo("SessionStart", SESSION_RULE)),
        ("SessionStart", None, 'python "%s"' % pending),
        ("UserPromptSubmit", None, echo("UserPromptSubmit", PROMPT_RULE)),
        ("PreToolUse", "Read|Grep|Glob|Bash", 'python "%s"' % guard),
    ]

    os.makedirs(CLAUDE_DIR, exist_ok=True)
    data = {}
    if os.path.exists(SETTINGS):
        try:
            data = json.loads(read(SETTINGS))
        except ValueError:
            say(False, "settings.json parses",
                "it is malformed - fix it before anything else, a broken file disables every setting")
            return
    added = 0
    hooks = data.setdefault("hooks", {})
    for event, matcher, command in wanted:
        groups = hooks.setdefault(event, [])
        # Compare against the parsed commands. Searching json.dumps() instead looks right and never
        # matches, because the dump escapes every quote the command contains - so every run would
        # append the same four hooks again.
        existing = [h.get("command", "") for g in groups for h in g.get("hooks", [])]
        key = (os.path.basename(command.split('"')[1]) if command.startswith("python")
               else '"hookEventName": "%s"' % event)
        if any(key in e for e in existing):
            continue
        entry = {"hooks": [{"type": "command", "command": command, "timeout": 5}]}
        if matcher:
            entry["matcher"] = matcher
        groups.append(entry)
        added += 1
    if added and not dry:
        if os.path.exists(SETTINGS):
            shutil.copyfile(SETTINGS, SETTINGS + ".bak")
        io.open(SETTINGS, "w", encoding="utf-8", newline="\n").write(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        json.loads(read(SETTINGS))                               # parse it back, or raise
    say(True, "Hooks installed", "%d added, %d already there" % (added, len(wanted) - added))


def check_only():
    """One small file read. The daily routine runs this, so it must be cheap and quiet."""
    meta, where = None, None
    local = os.path.join(HERE, "latest.json")
    if os.path.exists(local):
        try:
            meta, where = json.loads(read(local)), HERE
        except ValueError:
            meta = None
    if not meta:
        sys.path.insert(0, HERE)
        try:
            import update as up
            folder = up.drive_dir()
            if folder and os.path.exists(os.path.join(folder, "latest.json")):
                meta, where = json.loads(read(os.path.join(folder, "latest.json"))), folder
        except Exception:                                        # noqa: BLE001 - report, never crash
            meta = None

    have, st = None, os.path.join(CLAUDE_DIR, "second-brain-release.json")
    if os.path.exists(st):
        try:
            have = json.loads(read(st)).get("release")
        except ValueError:
            pass
    if not have:
        m = re.search(VERSION_RE,
                      read(os.path.join(CLAUDE_DIR, "skills", "obsidian-second-brain", "SKILL.md")),
                      re.M)
        have = m.group(1) if m else "unknown"

    if not meta or not meta.get("release"):
        print("installed %s - the shared folder is not on this machine" % have)
        return 4
    there = meta["release"]
    print("installed %s - newest release %s" % (have, there))
    if there == have:
        print("Up to date. Nothing to do.")
        return 0
    z = os.path.join(where, meta.get("zip", ""))
    if meta.get("sha256") and os.path.exists(z) and sha(z) != meta["sha256"]:
        print("The archive is still syncing. It will be ready shortly; nothing to do.")
        return 0
    print("A newer release is available. To take it, say: update the second brain")
    return 3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--check", action="store_true",
                    help="is a newer release waiting? Changes nothing. The daily routine runs this, "
                         "so it reads one small file and never unpacks the archive")
    a = ap.parse_args()

    if a.check:
        return check_only()

    print("Second brain - full install\n")
    v = sys.version_info
    if v < (3, 8):
        print("  [!] Python %d.%d is too old. Install 3.8 or newer from python.org," % (v[0], v[1]))
        print("      ticking 'Add python.exe to PATH', then run this again.")
        return 2
    say(True, "Python 3.8+", "%d.%d.%d" % (v[0], v[1], v[2]))

    tmp = tempfile.mkdtemp()
    try:
        root, how = find_release(tmp)
        if not root:
            say(False, "Release found", how)
            return 1
        say(True, "Release found", how)

        vault = a.vault or default_vault()
        existed = os.path.isdir(vault) and os.listdir(vault)
        if not a.dry_run:
            os.makedirs(vault, exist_ok=True)
        say(True, "Notes folder", vault + ("  (already there, nothing removed)" if existed else "  (new)"))

        skill_dir = "skill" if os.path.isdir(os.path.join(root, "skill")) else "obsidian-second-brain"
        boot = os.path.join(root, skill_dir, "scripts", "bootstrap_vault.py")
        if not a.dry_run:
            r = subprocess.run([sys.executable, boot, vault, "--modules", "core,work,findings"],
                               capture_output=True, text=True,
                               env=dict(os.environ, PYTHONIOENCODING="utf-8"))
            if r.returncode != 0:
                say(False, "Vault scaffolded", (r.stdout + r.stderr)[-200:])
                return 1
            n = sum(1 for _b, _d, fs in os.walk(vault) for _f in fs)
            say(True, "Vault scaffolded", "%d files - folders, templates, dashboards, property types" % n)
        else:
            say(True, "Vault scaffolded", "(dry run)")

        upd = os.path.join(root, "tools", "update.py")
        if not a.dry_run:
            r = subprocess.run([sys.executable, upd, "--from-repo", "--vault", vault, "--no-checks"],
                               capture_output=True, text=True,
                               env=dict(os.environ, PYTHONIOENCODING="utf-8"))
            ok = "verified by hash" in r.stdout
            line = next((l.strip() for l in r.stdout.splitlines() if "verified by hash" in l), "")
            say(ok, "Skill and the two root files installed",
                line if ok else (r.stdout + r.stderr)[-200:])
            if not ok:
                return 1
        else:
            say(True, "Skill and the two root files installed", "(dry run)")

        merge_hooks(root, a.dry_run)

        block = standing_block(root, vault)
        if not block:
            say(False, "Standing block appended", "could not find it in the release - report this")
        elif "Every conversation is one of two things" in read(GLOBAL_MD):
            say(True, "Standing block appended", "already there, left alone")
        elif not a.dry_run:
            with io.open(GLOBAL_MD, "a", encoding="utf-8", newline="\n") as fh:
                fh.write(("\n\n" if os.path.exists(GLOBAL_MD) and read(GLOBAL_MD).strip() else "") + block)
            say(True, "Standing block appended", GLOBAL_MD)
        else:
            say(True, "Standing block appended", "(dry run)")

        print("")
        chk = os.path.join(root, "tools", "check-install.py")
        if not a.dry_run and os.path.exists(chk):
            subprocess.run([sys.executable, chk, vault],
                           env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("")
    print("=" * 78)
    print("STILL TO DO - these need Claude rather than a script, and the checklist says how:")
    print("  1. The daily update routine   - a scheduled task, so releases arrive on their own")
    print("  2. The index of installed skills - one note of pointers to what else is on this machine")
    print("  3. The owner's own person note   - written from the first conversation, never invented")
    print("  4. Obsidian, optional            - obsidian.md, then Open folder as vault:")
    print("     %s" % (a.vault or default_vault()))
    print("=" * 78)
    return 0 if all(s[0] for s in steps) else 1


if __name__ == "__main__":
    sys.exit(main())
