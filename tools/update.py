#!/usr/bin/env python3
"""Install a release onto this machine, from a clone of the repository.

    python tools/update.py                  # install what is in this clone
    python tools/update.py --pull           # fetch, move to the newest release tag, then install
    python tools/update.py --check          # say whether a newer release exists. Changes nothing
    python tools/update.py --vault "<path>" # when the vault cannot be found automatically

**Nothing is guessed.** `MANIFEST.json` says where each file goes and how it is written, and this
script does only what the manifest tells it.

## The order, and why it is this order

1. **Verify the clone against the manifest first.** A half-downloaded release must never reach the
   skill folder - if one hash is wrong, nothing at all is touched.
2. **Install**: the skill tree is mirrored **and files retired in this release are deleted**; the
   firm's layer is replaced with the previous copy kept as `.bak`; the owner's own files are written
   only if they are missing.
3. **Verify what landed**, by hash, file by file. A copy that reports success while silently skipping
   files has happened on this project before.
4. **Run the vault scaffold sync** - additive only, it overwrites nothing - then the install check.

A skill replaced while a conversation is open is not re-read by that conversation. It takes effect in
the next one. The update itself takes seconds; nothing is unavailable in between.
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

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HOME = os.path.expanduser("~")
CLAUDE_DIR = os.path.join(HOME, ".claude")
SKILLS = os.path.join(CLAUDE_DIR, "skills")
STATE = os.path.join(CLAUDE_DIR, "second-brain-release.json")


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


def git(*args):
    try:
        r = subprocess.run(("git",) + args, cwd=ROOT, capture_output=True, text=True, timeout=120)
        return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()
    except (OSError, subprocess.SubprocessError) as e:
        return 1, "", str(e)


def find_vault(named):
    if named and os.path.isdir(named):
        return named
    g = os.path.join(CLAUDE_DIR, "CLAUDE.md")
    m = re.search(r"`([A-Za-z]:\\[^`]+|/[^`]+)`", read(g)) if os.path.exists(g) else None
    if m and os.path.isdir(m.group(1)):
        return m.group(1)
    oj = os.path.join(os.environ.get("APPDATA", ""), "obsidian", "obsidian.json")
    if os.path.exists(oj):
        try:
            vaults = json.loads(read(oj)).get("vaults", {})
            for v in sorted(vaults.values(), key=lambda x: x.get("ts", 0), reverse=True):
                p = v.get("path", "")
                if os.path.isdir(p) and os.path.exists(os.path.join(p, "KAPITA.md")):
                    return p
        except (ValueError, OSError):
            pass
    return None


def newest_tag():
    """The newest release tag on the remote, in version order rather than by date."""
    code, out, _ = git("ls-remote", "--tags", "--refs", "origin")
    if code != 0:
        return None
    tags = [l.split("refs/tags/")[-1] for l in out.splitlines() if "refs/tags/" in l]
    rel = [t for t in tags if re.fullmatch(r"v?\d+(\.\d+)*", t)]
    if not rel:
        return None
    return sorted(rel, key=lambda t: [int(x) for x in t.lstrip("v").split(".")])[-1]


def installed_release():
    if os.path.exists(STATE):
        try:
            return json.loads(read(STATE)).get("release")
        except ValueError:
            pass
    m = re.search(r'^\s*version:\s*"?([0-9.]+)"?',
                  read(os.path.join(SKILLS, "obsidian-second-brain", "SKILL.md")), re.M)
    return m.group(1) if m else None


def mirror(src, dst, manifest_files, prefix):
    """Replace a whole tree. Files the release retired are deleted - a copy-only update leaves them."""
    keep = set()
    for rel in manifest_files:
        if rel.startswith(prefix + "/"):
            keep.add(os.path.normpath(rel[len(prefix) + 1:]))
    copied = removed = 0
    for b, _dirs, fs in os.walk(src):
        r = os.path.relpath(b, src)
        tb = dst if r == "." else os.path.join(dst, r)
        os.makedirs(tb, exist_ok=True)
        for f in fs:
            s, d = os.path.join(b, f), os.path.join(tb, f)
            if not os.path.exists(d) or sha(s) != sha(d):
                shutil.copy2(s, d)
                copied += 1
    for b, _dirs, fs in os.walk(dst, topdown=False):
        for f in fs:
            p = os.path.join(b, f)
            if os.path.normpath(os.path.relpath(p, dst)) not in keep:
                os.remove(p)
                removed += 1
        if b != dst and not os.listdir(b):
            os.rmdir(b)
    return copied, removed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pull", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--vault")
    ap.add_argument("--skills-dir", default=SKILLS)
    ap.add_argument("--no-checks", action="store_true", help="skip the vault sync and install check")
    a = ap.parse_args()

    mpath = os.path.join(ROOT, "MANIFEST.json")
    if not os.path.exists(mpath):
        print("no MANIFEST.json beside this script - is this a clone of the repository?")
        return 2
    man = json.loads(read(mpath))
    here_release = man["release"]
    have = installed_release()

    if a.check or a.pull:
        code, _, err = git("fetch", "--tags", "--quiet")
        if code != 0:
            print("could not reach the repository: " + (err.splitlines()[0][:120] if err else "no network"))
            print("installed: %s. Nothing changed." % (have or "unknown"))
            return 0 if a.check else 1
        tag = newest_tag()
        if a.check:
            print("installed %s - newest release %s" % (have or "unknown", tag or "unknown"))
            newer = bool(tag and have and tag.lstrip("v") != have)
            # Recorded on disk so the session hook can mention a release that has sat unclaimed
            # for days without ever going near the network itself.
            notice = os.path.join(CLAUDE_DIR, "second-brain-update.json")
            if newer:
                if not (os.path.exists(notice) and
                        json.loads(read(notice) or "{}").get("release") == tag.lstrip("v")):
                    with io.open(notice, "w", encoding="utf-8") as fh:
                        json.dump({"release": tag.lstrip("v"), "tag": tag, "installed": have}, fh, indent=1)
                print("A newer release is available. To take it, say: update the second brain")
                return 3
            if os.path.exists(notice):
                os.remove(notice)
            print("Up to date. Nothing to do.")
            return 0
        if tag:
            code, _, err = git("checkout", "--quiet", tag)
            if code != 0:
                print("could not move to %s: %s" % (tag, err[:160]))
                return 1
            man = json.loads(read(mpath))
            here_release = man["release"]
            print("moved to %s" % tag)

    bad = [rel for rel, want in man["files"].items()
           if not os.path.exists(os.path.join(ROOT, rel)) or sha(os.path.join(ROOT, rel)) != want]
    if bad:
        print("This clone does not match its own manifest - %d file(s). NOTHING was installed." % len(bad))
        for rel in bad[:10]:
            print("  " + rel)
        print("Fix with: git status, then git checkout -- .   (or clone again)")
        return 1

    vault = find_vault(a.vault)
    print("installing release %s%s" % (here_release, ("  (was %s)" % have) if have else ""))

    dests = {"skills": a.skills_dir, "vault": vault or ""}
    installed = []
    for e in man["entries"]:
        if e["rule"] == "none":
            continue
        src = os.path.join(ROOT, e["source"])
        if "{vault}" in e["dest"] and not vault:
            print("  skipped %s - no vault found. Re-run with --vault \"<path>\"" % e["source"])
            continue
        dst = e["dest"].format(**dests).replace("/", os.sep)
        if e["rule"] == "replace-tree":
            c, r = mirror(src, dst, man["files"], e["source"])
            print("  skill: %d file(s) written, %d retired file(s) removed" % (c, r))
            installed.append((e["source"], dst))
        elif e["rule"] == "replace-file":
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if os.path.exists(dst) and sha(dst) != sha(src):
                shutil.copyfile(dst, dst + ".bak")
                print("  kept your copy as %s.bak" % os.path.basename(dst))
            shutil.copy2(src, dst)
            print("  %s -> %s" % (e["source"], dst))
            installed.append((e["source"], dst))
        elif e["rule"] == "create-if-missing":
            if os.path.exists(dst):
                print("  %s already there, left alone (it is yours)" % os.path.basename(dst))
            else:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                print("  %s -> %s (new)" % (e["source"], dst))
                installed.append((e["source"], dst))

    wrong = []
    for source, dst in installed:
        if os.path.isdir(dst):
            for rel, want in man["files"].items():
                if rel.startswith(source + "/"):
                    p = os.path.join(dst, rel[len(source) + 1:].replace("/", os.sep))
                    if not os.path.exists(p) or sha(p) != want:
                        wrong.append(rel)
        elif sha(dst) != man["files"].get(source, ""):
            wrong.append(source)
    if wrong:
        print("\nINSTALL VERIFY FAILED - %d file(s) did not land:" % len(wrong))
        for w in wrong[:10]:
            print("  " + w)
        return 1
    print("  verified by hash: %d file(s) match the manifest" % len(man["files"]))

    with io.open(STATE, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"release": here_release, "from": ROOT}, fh, indent=1)

    if not a.no_checks and vault:
        sync = os.path.join(HERE, "sync-vault.py")
        if os.path.exists(sync):
            print("")
            subprocess.run([sys.executable, sync, vault, "--fix"])
        chk = os.path.join(HERE, "check-install.py")
        if os.path.exists(chk):
            print("")
            subprocess.run([sys.executable, chk, vault])

    print("\nRelease %s is installed." % here_release)
    print("A conversation already open keeps the old copy - open a new one for this to take effect.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
