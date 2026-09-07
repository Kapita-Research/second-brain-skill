# Working on this repository, and how an update reaches fifteen machines

**Two people edit this: Murtadha and Mohammed Mustafa. Anyone else who edits it follows the same
rules.** They are short, and two of the three are enforced by the machine rather than by memory.

---

## What is in here, and what is not

**Everything that has to be updated on somebody's machine lives here.** The skill, the firm's layer,
the templates and dashboards, the tools, the install checklist.

> ## Nothing personal, ever.
> **No note from anyone's vault. No `Judgements/`. Nothing from `~/.claude/CLAUDE.md`.** A person's own
> record is theirs and it is not distributed, not even to help.

**`MANIFEST.json` is the one file that knows where things go.** It maps every path in this repository
to a destination and a rule, and `update.py` does only what it says. When a file moves or is added,
`python tools/manifest.py` regenerates it, and the gate refuses a push where it is stale.

| rule | what an update does with it |
|---|---|
| `replace-tree` | mirrored whole, **and a file the release retired is deleted** |
| `replace-file` | overwritten, previous copy kept as `.bak` |
| `create-if-missing` | written only if absent. **Never overwritten** |
| `none` | lives here, installs nowhere |

---

## The three rules

### 1 · Pull before you push, and read what came in

**Enforced.** The pre-push hook fetches and refuses if anything landed on the branch while you worked.

> **A clean text merge is not proof of agreement.** `KAPITA.md` overrides the skill silently, so two
> edits can merge without conflict and still contradict each other. **Test 3 is what catches that** -
> run the gate after any merge, not only before the push.

### 2 · Nothing half-finished is pushed

**Enforced, twice.** The pre-push hook runs `tools/test_all.py`; the GitHub Action runs it again on
every push and pull request, because a hook can be skipped with `--no-verify` and an Action cannot.

### 3 · Machines install a tag, not `main`

**`main` is where you work. A tag is what fifteen machines pick up.** So a commit that turns out to be
wrong reaches nobody until somebody tags it, and a bad release is undone by pointing at the previous
tag.

---

## The gate — seven tests

```bash
python tools/test_all.py
```

| | |
|---|---|
| **1** | A vault built from nothing validates: **0 errors, 0 warnings** |
| **2** | Every fixture vault in `skill/evals/files/` still validates |
| **3** | `KAPITA.md` uses no vocabulary that disagrees with the skill |
| **4** | `MANIFEST.json` is current, and every file in the repository is claimed by a rule |
| **5** | A full install into an empty machine passes its own check |
| **6** | `SKILL.md`, the CHANGELOG's newest entry and `MANIFEST.json` agree on the version |
| **7** | **This version is not already released.** A released number has to keep meaning one thing, so a distributed file may not change under a tag that already exists. *Editing the tools, the docs or a test changes nothing anybody installs and is not affected* |

> **Tests 1 and 5 are the ones that matter most, because they are written from the receiving end.**
> *Everything else here runs on a machine where it already works, which is exactly the machine that
> cannot tell you it is broken.* **Test 1 caught a scaffold that crashed on any Windows box whose code
> page was not UTF-8. It had never failed on the author's machine, because a scaffold runs once and the
> maintainer is the one person who stops running it.**

---

## Setting up your clone, once

```bash
git clone <repo> && cd <repo>
git config core.hooksPath .githooks
python tools/test_all.py
```

**The second line is what installs the pre-push hook.** Without it nothing stops you pushing a broken
release; the Action will still catch it, but after the fact.

---

## Making a change

1. `git pull --rebase`
2. Edit. **If you touched the skill and the layer together, read both** - the layer wins silently.
3. `python tools/test_all.py`
4. Commit and push. The hook re-runs the gate.

**A change that people should receive also needs three things**, and test 6 refuses without them:
`metadata.version` in `skill/SKILL.md`, an entry at the top of `skill/CHANGELOG.md`, and a regenerated
manifest.

---

## Cutting a release

```bash
python tools/release.py
```

Regenerates the manifest, refuses a dirty tree, runs the gate, tags `v<version>`, pushes both.

**Then it is done.** Every machine's daily check sees the new tag within a day and offers it. **Nothing
installs by itself**, because a skill replaced under a running conversation is not re-read by it.

---

## How it lands on a machine

**A daily routine asks the repository for the newest tag.** If it matches what is installed it says
nothing at all. If it is newer it sends one notification naming the release and what changed.

**The person says *"update the second brain"* whenever it suits them.** Then:

1. `update.py` verifies the clone against the manifest. **One wrong hash and nothing is touched** - a
   half-downloaded release never reaches the skill folder.
2. It installs by the manifest's rules.
3. **It verifies what landed, file by file, by hash.** *A copy that reported success while silently
   skipping files has happened on this project before.*
4. It syncs the vault scaffold - additive, it overwrites nothing - and runs the install check.

**It takes seconds, and nothing is unavailable meanwhile.** The conversation that ran it keeps the old
copy; the next one gets the new.

---

## Rolling back

```bash
git checkout v<previous>
python tools/update.py
```

**That is the whole reason the release is a tag.**
