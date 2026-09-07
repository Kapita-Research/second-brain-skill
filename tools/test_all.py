#!/usr/bin/env python3
"""The tests that must pass before anything is pushed or tagged.

    python tools/test_all.py            # run them all
    python tools/test_all.py -k install # run the ones whose name contains "install"

**These are the agreed gate, not a suggestion.** The pre-push hook runs them and refuses the push on a
failure; the GitHub Action runs them again, because a hook can be skipped with `--no-verify` and an
Action cannot.

## What they are for

Two of them matter more than the rest, and they are the two written from the **receiving** end rather
than the authoring end: **a vault built from nothing** (test 1) and **a full install into an empty
machine** (test 5). Every other check on this project runs on a machine where the thing already works,
which is exactly the machine that cannot tell you it is broken. *Test 1 is what caught a scaffold that
crashed on any Windows box whose code page was not UTF-8; it had never failed here, because a scaffold
runs once and the maintainer is the one person who stops running it.*

Every test builds what it needs in a temporary folder and deletes it. **Nothing reads or writes the
real vault, the real `~/.claude`, or anything on the network.**
"""
import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = sys.executable
SKILL = os.path.join(ROOT, "skill")

results = []


def run(cmd, **kw):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    env.update(kw.pop("env", {}))
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600, env=env, **kw)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def test(name):
    def deco(fn):
        fn._name = name
        return fn
    return deco


@test("1 - a vault built from nothing validates clean")
def t_fresh():
    """The receiving end. A scaffold runs once per machine, so its bugs are invisible to whoever
    maintains it - and UTF-8 mode is forced off here because the author's machine had it on."""
    with tempfile.TemporaryDirectory() as tmp:
        v = os.path.join(tmp, "vault")
        os.makedirs(v)
        code, out = run([PY, os.path.join(SKILL, "scripts", "bootstrap_vault.py"), v,
                         "--modules", "core,work,findings"], env={"PYTHONUTF8": "0"})
        if code != 0:
            return False, "bootstrap failed:\n" + out[-800:]
        code, out = run([PY, os.path.join(SKILL, "scripts", "validate_vault.py"), v])
        errs = re.search(r"ERRORS:\s*(\d+)", out)
        warns = re.search(r"WARNINGS:\s*(\d+)", out)
        if not errs or errs.group(1) != "0":
            return False, "a fresh vault does not validate:\n" + out[-800:]
        if warns and warns.group(1) != "0":
            return False, "a fresh vault has warnings:\n" + out[-800:]
        return True, "0 errors, 0 warnings"


@test("2 - the fixture vaults still validate")
def t_fixtures():
    """Vaults committed to the repository, so a change to the vocabulary that breaks real notes is
    caught here rather than in somebody's vault."""
    base = os.path.join(SKILL, "evals", "files")
    bad = []
    for name in sorted(os.listdir(base)):
        v = os.path.join(base, name)
        if not os.path.isdir(v):
            continue
        extra = extra_types(os.path.join(v, "CLAUDE.md"))
        code, out = run([PY, os.path.join(SKILL, "scripts", "validate_vault.py"), v] + extra)
        m = re.search(r"ERRORS:\s*(\d+)", out)
        if not m or m.group(1) != "0":
            bad.append("%s:\n%s" % (name, out[-500:]))
    return (not bad), ("all fixtures clean" if not bad else "\n".join(bad))


@test("3 - the firm's layer agrees with the skill")
def t_layer():
    """The layer overrides the skill, so a word here that disagrees wins silently."""
    code, out = run([PY, os.path.join(HERE, "check-kapita-layer.py"),
                     os.path.join(ROOT, "kapita-vault-KAPITA.md")])
    return code == 0, out.strip().splitlines()[-1] if out.strip() else "clean"


@test("4 - the manifest is current and claims every file")
def t_manifest():
    code, out = run([PY, os.path.join(HERE, "manifest.py"), "--check"])
    return code == 0, out.strip().splitlines()[-1] if out.strip() else ""


@test("5 - a full install into an empty machine passes its own check")
def t_install():
    """Nothing here touches the real ~/.claude: the skills folder and the vault are both temporary."""
    with tempfile.TemporaryDirectory() as tmp:
        skills = os.path.join(tmp, "skills")
        v = os.path.join(tmp, "vault")
        os.makedirs(skills)
        os.makedirs(v)
        code, out = run([PY, os.path.join(SKILL, "scripts", "bootstrap_vault.py"), v,
                         "--modules", "core,work,findings"])
        if code != 0:
            return False, "bootstrap failed:\n" + out[-600:]
        code, out = run([PY, os.path.join(HERE, "update.py"), "--vault", v,
                         "--skills-dir", skills, "--no-checks"])
        if code != 0:
            return False, "install failed:\n" + out[-900:]
        if "verified by hash" not in out:
            return False, "the install did not verify itself:\n" + out[-600:]
        code, out = run([PY, os.path.join(HERE, "check-install.py"), v])
        # The person note and the hooks belong to a human, not to a release: their absence in a
        # temporary vault is correct. Anything else required must pass.
        allowed = ("Your own person note", "Automatic capture configured", "and it names the skill",
                   "Standing reminder enforced by hooks", "Installed copy matches this package",
                   "Vault opened in Obsidian", "Obsidian installed", "Obsidian CLI enabled",
                   "Judgement guard armed", "Installed skills indexed",
                   "Daily update check scheduled")
        failed = [l.strip() for l in out.splitlines()
                  if l.strip().startswith("[ ]") and not any(a in l for a in allowed)]
        return (not failed), ("install clean" if not failed else "\n".join(failed))


@test("6 - the version agrees with itself")
def t_version():
    sk = io.open(os.path.join(SKILL, "SKILL.md"), encoding="utf-8").read(4000)
    m = re.search(r'^\s*version:\s*"?([0-9.]+)"?', sk, re.M)
    if not m:
        return False, "no metadata.version in SKILL.md"
    v = m.group(1)
    cl = io.open(os.path.join(SKILL, "CHANGELOG.md"), encoding="utf-8").read(4000)
    top = re.search(r"^##\s*([0-9.]+)\s", cl, re.M)
    if not top:
        return False, "no version heading at the top of CHANGELOG.md"
    if top.group(1) != v:
        return False, "SKILL.md says %s, the CHANGELOG's newest entry says %s" % (v, top.group(1))
    man = json.load(io.open(os.path.join(ROOT, "MANIFEST.json"), encoding="utf-8"))
    if man.get("release") != v:
        return False, "MANIFEST.json says %s, SKILL.md says %s" % (man.get("release"), v)
    return True, "%s everywhere" % v


@test("7 - this version has not already been released")
def t_not_released():
    """Refuse to change what a released version contains.

    **A tag is what fifteen machines install, so a released number has to keep meaning one thing.**
    This does not ask you to bump the version on every push - editing the tools, the docs or a test
    changes nothing anybody installs. It fails only when a file that **is** distributed differs from
    what the tag of the same number already carries. *Then the choice is a new version, not a quieter
    tag.*

    Skipped when there is no remote or no network: it is a check about what other people have, and
    with no remote nobody has anything yet.
    """
    man = json.load(io.open(os.path.join(ROOT, "MANIFEST.json"), encoding="utf-8"))
    v = man["release"]
    tag = "v" + v
    code, out = run(["git", "-C", ROOT, "remote"])
    if code != 0 or not out.strip():
        return True, "no remote yet - nothing is released, so nothing can be overwritten"
    code, _ = run(["git", "-C", ROOT, "fetch", "--tags", "--quiet"])
    if code != 0:
        return True, "could not reach the remote - skipped"
    code, out = run(["git", "-C", ROOT, "rev-parse", "--verify", "--quiet", tag + "^{commit}"])
    if code != 0 or not out.strip():
        return True, "%s is not released yet" % tag
    paths = [e["source"] for e in man["entries"] if e["rule"] != "none"]
    code, out = run(["git", "-C", ROOT, "diff", "--name-only", tag, "HEAD", "--"] + paths)
    changed = [l for l in out.splitlines() if l.strip()]
    if changed:
        listed = os.linesep.join("  " + c for c in changed[:10])
        return False, ("%s is already released and these distributed files differ from it:%s%s%s"
                       "Bump metadata.version in SKILL.md and add its CHANGELOG entry."
                       % (tag, os.linesep, listed, os.linesep))
    return True, "%s released, and nothing distributed has changed since" % tag


@test("8 - the shared folder is not behind the newest tag")
def t_published():
    """Thirteen people read the Drive folder, not the repository.

    A tag that was pushed and never published is a release that reached two machines. This compares
    what the folder says with the newest tag, and skips itself on a machine that has neither.
    """
    sys.path.insert(0, HERE)
    import update as up
    release, _archive, folder = up.drive_latest()
    if not folder:
        return True, "no shared folder on this machine - skipped"
    # Released means pushed, not tagged locally. A local tag that has not left the machine is a
    # release in progress - and release.py creates the tag before it pushes, so reading local tags
    # here made the gate fail during the very release it was waiting for.
    code, out = run(["git", "-C", ROOT, "ls-remote", "--tags", "--refs", "origin"])
    if code != 0:
        return True, "could not reach the remote - skipped"
    tags = [l.split("refs/tags/")[-1].strip().lstrip("v") for l in out.splitlines()
            if "refs/tags/v" in l]
    tags = [t for t in tags if t and all(x.isdigit() for x in t.split("."))]
    if not tags:
        return True, "nothing released yet - skipped"
    newest = sorted(tags, key=lambda t: [int(x) for x in t.split(".") if x.isdigit()])[-1]
    if release != newest:
        return False, ("the folder offers %s, the newest tag is v%s. Run: python tools/release.py"
                       % (release or "nothing", newest))
    return True, "folder and newest tag both %s" % newest


def extra_types(claude_md):
    """A vault may register its own type and status names; the validator has to be told."""
    out = []
    if not os.path.exists(claude_md):
        return out
    t = io.open(claude_md, encoding="utf-8", errors="replace").read()
    for key, flag in (("extra-types", "--extra-types"), ("extra-statuses", "--extra-statuses")):
        m = re.search(r"^%s:\s*(.+)$" % key, t, re.M)
        if m and m.group(1).strip():
            out += [flag, m.group(1).strip()]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-k", help="run only tests whose name contains this")
    a = ap.parse_args()

    tests = [v for v in sorted(globals().values(), key=lambda x: getattr(x, "_name", ""))
             if callable(v) and hasattr(v, "_name")]
    if a.k:
        tests = [t for t in tests if a.k.lower() in t._name.lower()]

    print("second brain - release gate (%d test%s)\n" % (len(tests), "" if len(tests) == 1 else "s"))
    failed = 0
    for t in tests:
        try:
            ok, detail = t()
        except Exception as e:                                   # noqa: BLE001 - report, never crash
            ok, detail = False, "%s: %s" % (type(e).__name__, e)
        print("%s %s" % ("PASS" if ok else "FAIL", t._name))
        if detail:
            for line in str(detail).splitlines():
                print("       " + line[:150])
        if not ok:
            failed += 1
        print("")

    if failed:
        print("%d of %d failed. Do not push." % (failed, len(tests)))
        return 1
    print("All %d pass." % len(tests))
    return 0


if __name__ == "__main__":
    sys.exit(main())
