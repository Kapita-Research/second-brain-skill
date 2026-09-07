# The second brain skill

**A fork of the public `obsidian-second-brain` skill, adapted for research figures, Arabic capture, and
handing part of a vault to an organisation.** Built on upstream **2.17.0**; this repository is at
**3.3**.

> ## Start here
>
> **If you were sent this link and told to set it up, say this to Claude:**
>
> ### *"Read the README at this repository and do what it says."*
>
> **Everything below is written for Claude as much as for you.**

---

## 1. Install it on this machine

```bash
git clone https://github.com/Kapita-Research/second-brain-skill.git
cd second-brain-skill
python tools/install.py
```

**That is the whole install.** It finds the release, verifies it by hash before unpacking, creates the
notes folder and scaffolds it, installs the skill and both root files, merges the hooks, and runs the
install check. **It asks nothing**, because somebody who has not used the thing yet has no basis for
choosing a folder layout.

**Then do the four things a script cannot.** The installer names them when it finishes and
[`dist/CHECKLIST.md`](dist/CHECKLIST.md) spells them out: the daily update routine, the index of the
other skills on this machine, the owner's own person note, and Obsidian.

**If something is wrong afterwards**, in any conversation: *"run the second brain install check"*. Every
failing line prints the one thing to do about it.

---

## 2. Understand what the fork does

**Read in this order.** It is the difference between using this and being able to maintain it.

| | |
|---|---|
| [`skill/CHANGELOG.md`](skill/CHANGELOG.md) | **From the top down to and including the 3.0 entry.** Every difference from upstream 2.17.0: what was added, what testing found, and why each decision went the way it did |
| [`UPDATING.md`](UPDATING.md) | **How this repository works.** The working rules, the gate, and how a release reaches fifteen machines |
| [`FORK-NOTES.md`](FORK-NOTES.md) | **What lives outside the skill**, and what a future rebase on upstream must not undo |

---

## 3. Work on it

**Read [`UPDATING.md`](UPDATING.md) before your first change.** The short version:

- **Pull before you push, and read what came in.** Enforced by a hook.
- **Nothing half finished is pushed.** The gate runs on your machine and again in CI.
- **Push freely; release rarely.** A version number changes only when what people install changes, and
  a release is a separate act you ask for.
- **Machines install a tag, not `main`**, so a commit that turns out to be wrong reaches nobody.
- **Claude does not push and does not release** unless you say so.

```bash
git config core.hooksPath .githooks    # once per clone: installs the pre-push gate
python tools/test_all.py               # the gate, any time
```

---

## What is in here

| | |
|---|---|
| **`skill/`** | **The fork. This is what gets installed.** Generic and standalone: it names no company and no colleague, and a test enforces that |
| **`kapita-vault-KAPITA.md`** | **The firm's layer.** Goes in the vault as `KAPITA.md` and is replaced whole on every update. **Never inside the skill** |
| **`tools/`** | `install.py` and `update.py` install a release; `release.py` cuts one; `test_all.py` is the gate; `manifest.py` writes the file that knows every destination; `check-install.py` verifies one machine |
| **`MANIFEST.json`** | **The only file that knows where anything goes.** Generated, and the gate refuses a push where it is stale |
| **`dist/`** | `CHECKLIST.md`, the install runbook, and `CLAUDE.md`, the vault starter file that nothing ever replaces |
| **`upstream/`** | The untouched originals, kept because a three-way merge needs the base it diverged from. **Never edit** |

> ## Nothing personal is ever committed here.
> **No note from anyone's vault, nothing from `Judgements/`, nothing from a personal `CLAUDE.md`.** A
> person's own record is theirs, and it is not distributed even to help.
