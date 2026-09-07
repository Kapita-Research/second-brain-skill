# personal-skill

**A fork of the `obsidian-second-brain` skill v2.17.0, adapted for Arabic capture, research figures, and
handing part of a vault to an organisation.**

**This file is orientation only.** Each thing below explains itself.

---

## What is here

| | |
|---|---|
| **`skill/`** | **The fork — what gets installed.** Its own `README.md` describes the skill and how to use it |
| `upstream/` | **The untouched 2.9.2 original.** Kept because a three-way merge needs the base it diverged from. **Never edit it** |
| **`skill/CHANGELOG.md`** | **The skill's history** — the 3.0 entry is every difference from upstream 2.17.0, in the same form as every release before it |
| **`FORK-NOTES.md`** | **What lives outside the skill** — the tools, the two vault files, and **what a future re-base must not undo** |

| `kapita-vault-KAPITA.md` | The firm's layer — **goes in the vault as `KAPITA.md`, never in the skill.** Replaced whole on update |
| **`tools/`** | **`check-kapita-layer.py`** — the layer overrides the skill, so a word that disagrees wins **silently**. **Run before every distribution** · **`sync-vault.py`** — a vault's scaffold does not update itself. **Run after every update**, with `--fix` · **`check-install.py`** — twenty checks on one machine. **The first thing to run when someone says it is not working** |
| `dist/` | **`START-HERE.md`** — the first file a recipient opens · **`CHECKLIST.md`** — the nine install steps and the command that verifies them · **`CLAUDE.md`** — the owner's starter file, **which nothing ever replaces** |
| `discarded/` | A from-scratch draft written before the original was found. A record; used for nothing |

---

## Installing

**1 ·** `skill/` → `~/.claude/skills/`
**2 ·** Any empty folder as a vault
**3 ·** `kapita-vault-KAPITA.md` → the vault root as `KAPITA.md` · `dist/CLAUDE.md` → beside it as `CLAUDE.md`
**4 ·** Obsidian is optional and free. **If you install it, turn on Settings → General → Command line
interface** — the skill checks and says so once.

---

## Distributing

```bash
python tools/build-zip.py
```

**`../second-brain-3.0.zip`** is what goes to a person — **one archive for both cases.** The version
in its name is read from the skill's own frontmatter, so the two cannot disagree.

It carries the skill, both vault files, `sync-vault.py`, and a `START-HERE.md` that
branches:

> **Never used it** → *"Install this skill."* · **Used it before** → *"Update my skill with this."*

**Both branches are written as instructions Claude executes**, so the person does not have to read them.

⛔ **It excludes `evals/`, `upstream/`, `FORK-PLAN.md`, `discarded/` and `check-kapita-layer.py`** —
development material. **`sync-vault.py` is in**, because an update calls it.

## Status

**Thirty-three documented changes, and the fork now sits on upstream 2.17.0** — eight feature releases
brought forward, every one of our decisions re-applied on top.

> **The next step is not another change — it is a week of ordinary use.** Every genuinely new problem
> so far came from **running** something, never from reading it.
