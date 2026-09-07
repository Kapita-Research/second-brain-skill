#!/usr/bin/env python3
"""Cut a release: manifest, gate, tag, push, and publish it to the shared Drive folder.

    python tools/release.py              # the whole thing
    python tools/release.py --dry-run    # everything except the tag, the push and the publish
    python tools/release.py --no-publish # tag and push only. Use only if Drive is not on this machine

**Two audiences, one command.** The repository is for the two people who work on the skill; **the
shared Drive folder is how the other thirteen receive it**, and most of them have no GitHub account and
no reason to get one. So publishing is not a separate thing anybody has to remember: it is the last
step of cutting the release, and a release that fails to publish fails.

## What lands in the Drive folder

    latest.json                 release, archive name, sha256, date
    second-brain-<version>.zip  every file the manifest claims, at its own path
    install.py                  the entry point, unzipped

**`install.py` is copied in unzipped on purpose.** *Somebody with nothing installed cannot run a script
that is inside an archive they have not unpacked*, so the one command they are given has to point at a
file that is simply there.

**`latest.json` is what a machine reads** - one small file, compared by version rather than by
modification date. *A date changes when somebody re-uploads the same bytes and does not change when it
matters; a version says exactly whether what you have is older.* **The hash is what makes an unverified
copy impossible to install**, including one that is only half synced.

## What it refuses to do

* **Tag a dirty tree.** What is tagged has to be what was tested.
* **Tag when the gate fails.** `test_all.py` runs first, every time.
* **Reuse a version.** Test 7 already refuses when a distributed file has changed under a tag that
  exists; this refuses the duplicate tag outright.
"""
import argparse
import datetime
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = sys.executable
sys.path.insert(0, HERE)
import update as up                                                   # noqa: E402


def git(*args):
    r = subprocess.run(("git",) + args, cwd=ROOT, capture_output=True, text=True)
    return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()


def build_archive(man, out_dir, version):
    """Every file the manifest claims, at its repository path. The updater unpacks and installs it."""
    name = "second-brain-%s.zip" % version
    path = os.path.join(out_dir, name)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(os.path.join(ROOT, "MANIFEST.json"), "MANIFEST.json")
        for rel in sorted(man["files"]):
            zf.write(os.path.join(ROOT, rel), rel)
    h = hashlib.sha256(io.open(path, "rb").read()).hexdigest()
    return name, path, h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-publish", action="store_true")
    ap.add_argument("--remote", default="origin")
    a = ap.parse_args()

    print("regenerating the manifest...")
    if subprocess.run([PY, os.path.join(HERE, "manifest.py")]).returncode != 0:
        return 1
    man = json.load(io.open(os.path.join(ROOT, "MANIFEST.json"), encoding="utf-8"))
    version = man["release"]
    tag = "v" + version

    code, out, _ = git("status", "--porcelain")
    if out:
        print("\nThe working tree is not clean. Commit first - what is tagged must be what was tested:")
        for line in out.splitlines()[:12]:
            print("  " + line)
        return 1

    folder = up.drive_dir()
    if not folder and not a.no_publish and not a.dry_run:
        print("\nThe shared Drive folder was not found on this machine.")
        print("Thirteen people receive the release from there, so a release that does not reach it")
        print("reaches almost nobody. Install Google Drive for desktop and sync '%s'," % up.FOLDER)
        print("or set its path:  %s  ->  {\"drive_dir\": \"...\"}" % up.CONFIG)
        print("If you really mean to tag without publishing, pass --no-publish.")
        return 1

    print("\nrunning the gate...")
    if subprocess.run([PY, os.path.join(HERE, "test_all.py")]).returncode != 0:
        print("\nThe gate failed. No tag, and nothing published.")
        return 1

    code, out, _ = git("tag", "-l", tag)
    if out.strip():
        print("\n%s already exists. Bump metadata.version in SKILL.md and add its CHANGELOG entry." % tag)
        return 1

    if a.dry_run:
        print("\nDRY RUN - would tag %s, push it to %s, and publish to %s."
              % (tag, a.remote, folder or "(no Drive folder found)"))
        return 0

    code, _, err = git("tag", "-a", tag, "-m", "release " + version)
    if code != 0:
        print("could not tag: " + err[:200])
        return 1
    for what in ("HEAD", tag):
        code, _, err = git("push", a.remote, what)
        if code != 0:
            print("could not push %s: %s" % (what, err[:300]))
            print("The tag exists locally. Fix the remote, then: git push %s %s" % (a.remote, tag))
            return 1
    print("\npushed %s" % tag)

    if a.no_publish:
        print("--no-publish: the Drive folder was not written. Nobody outside the repository has this yet.")
        return 0

    print("publishing to %s ..." % folder)
    name, path, h = build_archive(man, folder, version)
    # install.py goes in unzipped, because it is the entry point: somebody with nothing installed
    # has no way to run a script that is inside the archive they have not unpacked yet.
    shutil.copy2(os.path.join(HERE, "install.py"), os.path.join(folder, "install.py"))
    meta = {"release": version, "zip": name, "sha256": h,
            "date": datetime.date.today().isoformat(),
            "size_kb": round(os.path.getsize(path) / 1024)}
    with io.open(os.path.join(folder, "latest.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=1)
        fh.write("\n")

    # Read both back the way a receiving machine will, so a failed write is caught here rather
    # than by thirteen people tomorrow.
    seen, archive, _ = up.drive_latest()
    if seen != version or archive in (None, "PARTIAL"):
        print("PUBLISH VERIFY FAILED - the folder does not read back as release %s." % version)
        print("The tag is pushed. Fix the folder before telling anybody.")
        return 1

    print("published %s (%d KB) and latest.json - verified by reading them back." % (name, meta["size_kb"]))
    print("\nReleased %s." % tag)
    print("Every machine's daily check will offer it within a day. Nothing installs by itself.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
