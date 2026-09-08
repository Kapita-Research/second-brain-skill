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
    """An empty machine, and it has to be genuinely empty.

    HOME is redirected as well as the skills folder. Reading the maintainer's own `~/.claude` is how
    this test passed while the installer crashed on any machine that had never run Claude Code: the
    config directory it writes its state into did not exist there, and here it always did.
    """
    with tempfile.TemporaryDirectory() as tmp:
        v = os.path.join(tmp, "vault")
        home = os.path.join(tmp, "home")
        for d in (v, home):
            os.makedirs(d)
        # No --skills-dir: with HOME redirected the skill lands where it really would, under
        # <home>/.claude/skills, so the check afterwards is looking at the same place the installer
        # wrote to rather than at the maintainer's own copy.
        empty = {"HOME": home, "USERPROFILE": home, "HOMEPATH": home}
        code, out = run([PY, os.path.join(SKILL, "scripts", "bootstrap_vault.py"), v,
                         "--modules", "core,work,findings"], env=empty)
        if code != 0:
            return False, "bootstrap failed:" + os.linesep + out[-600:]
        code, out = run([PY, os.path.join(HERE, "update.py"), "--vault", v, "--no-checks"], env=empty)
        if code != 0:
            return False, "install failed:" + os.linesep + out[-900:]
        if "verified by hash" not in out:
            return False, "the install did not verify itself:" + os.linesep + out[-600:]
        code, out = run([PY, os.path.join(HERE, "check-install.py"), v], env=empty)
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


@test("9 - the one-sentence install works on an empty machine")
def t_full_install():
    """The sentence the team is given has to do everything by itself.

    Runs `install.py` against a temporary HOME, so the real `~/.claude` is never touched: an empty
    machine, an empty vault, and afterwards the skill, the scaffold, the hooks and the standing block
    all have to be in place with the vault validating.
    """
    with tempfile.TemporaryDirectory() as tmp:
        home = os.path.join(tmp, "home")
        os.makedirs(home)
        vault = os.path.join(home, "Second Brain")
        code, out = run([PY, os.path.join(HERE, "install.py"), "--vault", vault],
                        env={"USERPROFILE": home, "HOME": home, "HOMEPATH": home})
        if code != 0:
            return False, "install.py failed:" + os.linesep + out[-900:]
        claude = os.path.join(home, ".claude")
        checks = [
            (os.path.exists(os.path.join(claude, "skills", "obsidian-second-brain", "SKILL.md")),
             "the skill did not land"),
            (os.path.exists(os.path.join(vault, "KAPITA.md")), "the layer did not land"),
            (os.path.exists(os.path.join(vault, "CLAUDE.md")), "the vault CLAUDE.md did not land"),
            ("Every conversation is one of two things" in
             io.open(os.path.join(claude, "CLAUDE.md"), encoding="utf-8", errors="replace").read(),
             "the standing block was not appended"),
            ("0 error(s)" in out, "the vault does not validate after a fresh install"),
        ]
        try:
            hooks = json.load(io.open(os.path.join(claude, "settings.json"), encoding="utf-8"))["hooks"]
            n = sum(len(h.get("hooks", [])) for groups in hooks.values() for h in groups)
        except (OSError, ValueError, KeyError):
            n = 0
        checks.append((n >= 4, "expected four hooks, found %d" % n))
        bad = [why for ok, why in checks if not ok]
        return (not bad), ("skill, vault, hooks and block all in place" if not bad
                           else os.linesep.join(bad))


@test("10 - the skill names no company and no colleague")
def t_generic():
    """The skill is standalone and shareable; the layer is where the firm lives.

    This is not a matter of taste. A skill that names the firm cannot be handed to a friend, and a
    skill that carries a colleague's full name, employer and job title as a worked example has put a
    real person into a file that travels. The names are read from the layer's own roster, so the check
    follows the roster rather than a list that goes stale beside it.
    """
    layer = io.open(os.path.join(ROOT, "kapita-vault-KAPITA.md"), encoding="utf-8").read()
    # Only the roster table: a bolded phrase followed by the Arabic spelling. Matching every bold
    # run in the file pulled in ordinary sentences like "The repository" and failed on them.
    names = set()
    for line in layer.splitlines():
        m = re.match(r"\|\s*\*\*([^*]+)\*\*\s*.\s+[؀-ۿ]", line)
        if m and " " in m.group(1):
            names.add(m.group(1).strip())
    names.add("KAPITA")
    hits = []
    for b, dirs, fs in os.walk(SKILL):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in fs:
            fp = os.path.join(b, f)
            try:
                t = io.open(fp, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            for n in names:
                if n in t:
                    rel = os.path.relpath(fp, ROOT).replace(chr(92), "/")
                    line_no = t[:t.index(n)].count(chr(10)) + 1
                    hits.append("%s:%d  %s" % (rel, line_no, n))
    if hits:
        return False, ("the skill is meant to name no company and no colleague:" + os.linesep +
                       os.linesep.join("  " + h for h in sorted(set(hits))[:12]))
    return True, "clean - %d names checked across the skill" % len(names)


@test("11 - the shared vocabulary has not widened by accident")
def t_vocabulary():
    """A new type or status is personal until somebody decides otherwise.

    The default has to be the vault, because that is what the owner meant when they said "add a type".
    `judgement` went into the skill on a run where the owner expected a word in their own vault, and
    nothing anywhere would have told them. So the shipped vocabulary is pinned in
    tools/vocabulary.lock.json: widening it means editing two files, and the second one says in its own
    text that this reaches every machine.
    """
    src = io.open(os.path.join(SKILL, "scripts", "validate_vault.py"), encoding="utf-8").read()
    types = set(re.findall(r'"([a-z-]+)"', src[src.index("TYPES = {"):src.index("# Task statuses")]))
    i = src.index("STATUSES = {")
    statuses = set(re.findall(r'"([a-z-]+)"', src[i:src.index("DOMAINS = {")]))
    lock = json.load(io.open(os.path.join(HERE, "vocabulary.lock.json"), encoding="utf-8"))
    problems = []
    for what, now, was in (("type", types, set(lock["types"])),
                           ("status", statuses, set(lock["statuses"]))):
        for w in sorted(now - was):
            problems.append("%s `%s` is new to the skill and would reach every machine. If it is one "
                            "person's own, it belongs in their vault CLAUDE.md under extra-%ss "
                            "instead. If it is genuinely for everybody, add it to "
                            "tools/vocabulary.lock.json and say so in the CHANGELOG." % (what, w, what))
        for w in sorted(was - now):
            problems.append("%s `%s` was removed from the skill but is still in the lock file. Vaults "
                            "already use it, so removing it breaks their notes." % (what, w))
    if problems:
        return False, os.linesep.join(problems)
    return True, "%d types, %d statuses, unchanged" % (len(types), len(statuses))


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
