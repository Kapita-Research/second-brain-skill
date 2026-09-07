#!/usr/bin/env python3
"""Install a release onto this machine.

    python tools/update.py --check          # is there a newer one? Changes nothing
    python tools/update.py                  # install the newest release this machine can reach
    python tools/update.py --from-zip PATH  # install a release archive downloaded by hand
    python tools/update.py --vault "<path>" # when the vault cannot be found automatically

## Where a release comes from, in order

1. **The shared Drive folder**, if Google Drive for desktop is running. It holds `latest.json` and the
   archive it names, and reading it costs one file read and no network at all.
2. **This clone**, for the two people who work on the repository.
3. **A file the owner downloaded from Drive in a browser** - `--from-zip`. The fallback for a machine
   with no Drive app on it, and it needs no account, no token and no repository.

**Nothing is guessed.** `MANIFEST.json` says where each file goes and how it is written; this script
does only what the manifest says.

## The order, and why it is this order

1. **Verify the source against its own manifest first.** A half-downloaded release must never reach the
   skill folder - if one hash is wrong, nothing at all is touched.
2. **Install**: the skill tree is mirrored **and files retired in this release are deleted**; the firm's
   layer is replaced with the previous copy kept as `.bak`; the owner's own files are written only if
   they are missing.
3. **Verify what landed**, by hash, file by file. A copy that reports success while silently skipping
   files has happened on this project before.
4. **Sync the vault scaffold** - additive only, it overwrites nothing - then run the install check.

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
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
HOME = os.path.expanduser("~")
CLAUDE_DIR = os.path.join(HOME, ".claude")
SKILLS = os.path.join(CLAUDE_DIR, "skills")
STATE = os.path.join(CLAUDE_DIR, "second-brain-release.json")
NOTICE = os.path.join(CLAUDE_DIR, "second-brain-update.json")
CONFIG = os.path.join(CLAUDE_DIR, "second-brain-source.json")

# Where Google Drive for desktop puts a shared folder, per platform. The folder name is the
# firm's; the rest is the app's own layout.
FOLDER = "KAPITA Second Brain"


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


def load_json(p, default=None):
    try:
        return json.loads(read(p))
    except ValueError:
        return default


def config():
    return load_json(CONFIG, {}) or {}


def drive_dir():
    """The shared folder, from the config file or by looking where the Drive app puts things."""
    c = config().get("drive_dir")
    if c and os.path.isdir(c):
        return c
    roots = []
    if sys.platform == "win32":
        for letter in "GHIJKLMNOPQRSTUVWXYZ":
            roots += [letter + ":\\My Drive", letter + ":\\Shared drives"]
        roots += [os.path.join(HOME, "Google Drive"), os.path.join(HOME, "My Drive")]
    else:
        roots += [os.path.join(HOME, "Google Drive", "My Drive"),
                  os.path.join(HOME, "Library", "CloudStorage")]
    for r in roots:
        if not os.path.isdir(r):
            continue
        cand = os.path.join(r, FOLDER)
        if os.path.isdir(cand):
            return cand
        try:                                   # one level in, for Shared drives / CloudStorage
            for d in os.listdir(r):
                cand = os.path.join(r, d, FOLDER)
                if os.path.isdir(cand):
                    return cand
        except OSError:
            pass
    return None


def drive_latest():
    """(release, archive path, folder) from the Drive folder, or (None, None, folder)."""
    d = drive_dir()
    if not d:
        return None, None, None
    meta = load_json(os.path.join(d, "latest.json"))
    if not meta or not meta.get("release"):
        return None, None, d
    z = os.path.join(d, meta.get("zip") or "")
    if not os.path.exists(z):
        return meta["release"], None, d
    want = meta.get("sha256")
    if want and sha(z) != want:
        # A file still syncing, or a truncated copy. Say so; do not install it.
        return meta["release"], "PARTIAL", d
    return meta["release"], z, d


def installed_release():
    st = load_json(STATE, {}) or {}
    if st.get("release"):
        return st["release"]
    m = re.search(r'^\s*version:\s*"?([0-9.]+)"?',
                  read(os.path.join(SKILLS, "obsidian-second-brain", "SKILL.md")), re.M)
    return m.group(1) if m else None


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


def install(root, vault, skills_dir, run_checks):
    """Install the release unpacked at `root`. Returns an exit code."""
    man = load_json(os.path.join(root, "MANIFEST.json"))
    if not man:
        print("no MANIFEST.json in %s - that is not a release." % root)
        return 2
    release, have = man["release"], installed_release()

    bad = [rel for rel, want in man["files"].items()
           if not os.path.exists(os.path.join(root, rel)) or sha(os.path.join(root, rel)) != want]
    if bad:
        print("This release does not match its own manifest - %d file(s). NOTHING was installed."
              % len(bad))
        for rel in bad[:10]:
            print("  " + rel)
        return 1

    print("installing release %s%s" % (release, ("  (was %s)" % have) if have else ""))
    dests = {"skills": skills_dir, "vault": vault or ""}
    installed = []
    for e in man["entries"]:
        if e["rule"] == "none":
            continue
        src = os.path.join(root, e["source"])
        if not os.path.exists(src):
            continue
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

    with io.open(STATE, "w", encoding="utf-8") as fh:
        json.dump({"release": release, "from": root}, fh, indent=1)
    if os.path.exists(NOTICE):
        os.remove(NOTICE)

    if run_checks and vault:
        for script in ("sync-vault.py", "check-install.py"):
            p = os.path.join(HERE, script)
            if os.path.exists(p):
                print("")
                subprocess.run([sys.executable, p, vault] + (["--fix"] if "sync" in script else []))

    print("\nRelease %s is installed." % release)
    print("A conversation already open keeps the old copy - open a new one for this to take effect.")
    return 0


def no_drive_message(release, folder_missing=True):
    """What to tell the owner when a release exists and this machine cannot reach the folder."""
    url = config().get("drive_url") or "the shared Drive folder"
    print("")
    print("Release %s is available, and this machine cannot see the shared folder." % release)
    if folder_missing:
        print("Google Drive for desktop is either not installed, or not syncing the folder.")
    print("")
    print("Two ways forward, and the first one is worth doing once:")
    print("  1. Install Google Drive for desktop and let it sync %s." % FOLDER)
    print("     After that every update is automatic and costs nothing.")
    print("  2. Open %s in a browser, download the archive," % url)
    print("     and run:  python tools/update.py --from-zip \"<the file you downloaded>\"")
    print("")
    print("Nothing was changed.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--from-zip")
    ap.add_argument("--from-repo", action="store_true", help="install this clone, not the Drive copy")
    ap.add_argument("--vault")
    ap.add_argument("--skills-dir", default=SKILLS)
    ap.add_argument("--no-checks", action="store_true")
    a = ap.parse_args()

    have = installed_release()
    vault = find_vault(a.vault)

    if a.check:
        release, archive, folder = drive_latest()
        if not folder:
            print("installed %s - the shared Drive folder is not on this machine" % (have or "unknown"))
            print("Set it up, or use: python tools/update.py --from-zip \"<downloaded file>\"")
            return 4
        if not release:
            print("installed %s - the shared folder has no latest.json yet" % (have or "unknown"))
            return 0
        print("installed %s - newest release %s" % (have or "unknown", release))
        if have and release != have:
            with io.open(NOTICE, "w", encoding="utf-8") as fh:
                json.dump({"release": release, "installed": have,
                           "archive": archive if archive != "PARTIAL" else None}, fh, indent=1)
            if archive == "PARTIAL":
                print("The archive is still syncing (its hash does not match latest.json yet).")
                print("It will be ready shortly; nothing to do.")
                return 0
            print("A newer release is available. To take it, say: update the second brain")
            return 3
        if os.path.exists(NOTICE):
            os.remove(NOTICE)
        print("Up to date. Nothing to do.")
        return 0

    if a.from_zip:
        z = a.from_zip
        if not os.path.exists(z):
            print("no such file: " + z)
            return 2
        with tempfile.TemporaryDirectory() as tmp:
            try:
                with zipfile.ZipFile(z) as zf:
                    zf.extractall(tmp)
            except (zipfile.BadZipFile, OSError) as e:
                print("that file is not a readable archive: %s" % e)
                return 1
            root = tmp
            if not os.path.exists(os.path.join(root, "MANIFEST.json")):
                subs = [d for d in os.listdir(tmp) if os.path.isdir(os.path.join(tmp, d))]
                for d in subs:
                    if os.path.exists(os.path.join(tmp, d, "MANIFEST.json")):
                        root = os.path.join(tmp, d)
                        break
            return install(root, vault, a.skills_dir, not a.no_checks)

    if not a.from_repo:
        release, archive, folder = drive_latest()
        if folder and archive and archive != "PARTIAL":
            with tempfile.TemporaryDirectory() as tmp:
                with zipfile.ZipFile(archive) as zf:
                    zf.extractall(tmp)
                root = tmp
                if not os.path.exists(os.path.join(root, "MANIFEST.json")):
                    for d in os.listdir(tmp):
                        if os.path.exists(os.path.join(tmp, d, "MANIFEST.json")):
                            root = os.path.join(tmp, d)
                            break
                return install(root, vault, a.skills_dir, not a.no_checks)
        if folder and archive == "PARTIAL":
            print("The archive in the shared folder is still syncing. Try again in a minute.")
            return 1
        if not os.path.exists(os.path.join(REPO, "MANIFEST.json")):
            no_drive_message(release or "the newest", folder_missing=not folder)
            return 4

    return install(REPO, vault, a.skills_dir, not a.no_checks)


if __name__ == "__main__":
    sys.exit(main())
