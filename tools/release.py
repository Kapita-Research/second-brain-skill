#!/usr/bin/env python3
"""Cut a release: regenerate the manifest, run the gate, tag, push.

    python tools/release.py            # tag the version in SKILL.md
    python tools/release.py --dry-run  # everything except the tag and the push

**A tag is the only thing anybody's machine installs.** `main` is where the two of you work; the tag is
what fifteen machines pick up. That separation is the whole safety mechanism: a half-finished commit on
`main` reaches nobody, and a release that turns out to be wrong is undone by pointing at the previous
tag rather than by finding an old archive.

## What it refuses to do

* **Tag a dirty tree.** What is tagged has to be what was tested.
* **Tag when the gate fails.** `test_all.py` runs first, every time.
* **Reuse a tag.** Bump `metadata.version` in `SKILL.md` and add the CHANGELOG entry first; test 6
   already refuses when those two disagree.
"""
import argparse
import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = sys.executable


def git(*args, capture=True):
    r = subprocess.run(("git",) + args, cwd=ROOT, capture_output=capture, text=True)
    return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--remote", default="origin")
    a = ap.parse_args()

    sk = io.open(os.path.join(ROOT, "skill", "SKILL.md"), encoding="utf-8").read(4000)
    m = re.search(r'^\s*version:\s*"?([0-9.]+)"?', sk, re.M)
    if not m:
        print("no metadata.version in skill/SKILL.md")
        return 1
    version = m.group(1)
    tag = "v" + version

    print("regenerating the manifest...")
    if subprocess.run([PY, os.path.join(HERE, "manifest.py")]).returncode != 0:
        return 1

    code, out, _ = git("status", "--porcelain")
    if out:
        print("\nThe working tree is not clean. Commit first - what is tagged must be what was tested:")
        for line in out.splitlines()[:12]:
            print("  " + line)
        return 1

    print("\nrunning the gate...")
    if subprocess.run([PY, os.path.join(HERE, "test_all.py")]).returncode != 0:
        print("\nThe gate failed. No tag.")
        return 1

    code, out, _ = git("tag", "-l", tag)
    if out.strip():
        print("\n%s already exists. Bump metadata.version in SKILL.md and add its CHANGELOG entry." % tag)
        return 1

    if a.dry_run:
        print("\nDRY RUN - would tag %s and push it to %s." % (tag, a.remote))
        return 0

    code, _, err = git("tag", "-a", tag, "-m", "release " + version)
    if code != 0:
        print("could not tag: " + err[:200])
        return 1
    code, _, err = git("push", a.remote, "HEAD")
    if code != 0:
        print("could not push the branch: " + err[:300])
        return 1
    code, _, err = git("push", a.remote, tag)
    if code != 0:
        print("could not push the tag: " + err[:300])
        return 1

    print("\nReleased %s." % tag)
    print("Every machine's daily check will offer it from now on. Nothing installs by itself.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
