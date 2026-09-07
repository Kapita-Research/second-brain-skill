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
                   "Judgement guard armed", "Installed skills indexed")
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
