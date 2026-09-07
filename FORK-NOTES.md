# Fork notes — what lives outside the skill

**The skill's own history is in [`skill/CHANGELOG.md`](skill/CHANGELOG.md), in the same form as every
upstream release.** *That file ships inside the skill, so it describes the skill and nothing else.*

**This file holds the rest** — the workspace tools, the firm's layer, and the handful of decisions a
future re-base has to know about. **Nothing here is part of the skill.**

---

## The tools

| | |
|---|---|
| **`tools/check-kapita-layer.py`** | `KAPITA.md` **overrides the skill**, so a word in it that disagrees wins **silently**. Nothing else notices. **Takes a path**, so it can be run against a vault's own copy — which is where drift actually happens |
| **`tools/sync-vault.py`** | A vault's scaffold — property types, templates, views — is copied in once at creation and **never updates itself**. Merges what is missing; ⛔ **overwrites nothing**, because a disagreeing property type, an edited template and an absent `.base` are all decisions a person has to make |
| **`tools/build-zip.py`** | The archive, built rather than assembled. **The version comes from `SKILL.md`'s own frontmatter**, so the name and the contents cannot disagree |
| **`tools/check-install.py`** | **Two dozen checks on one machine** — skill, vault, both root files, property types, templates, every view's `Templates/` exclusion, Obsidian and its CLI, automatic capture, whether the vault validates, and whether the machine's other installed skills are indexed in it. **The first thing to run when somebody says it is not working**, and each failure prints the one thing to do. Ships in the archive with `dist/CHECKLIST.md` |

**Run the layer checker and the vault sync before every distribution.**

> 🔴 **The install check earned itself on its first run.** Against a vault somebody had actually
> used it reported **94 errors across 47 findings** — `type: finding` and its statuses shipped with a
> template, a view and a reference file, and were never added to the validator's vocabulary. **It was
> invisible for as long as the development vault had no findings in it.**

---

## The two vault files, and why they are two

| In the vault | Whose | On update |
|---|---|---|
| **`KAPITA.md`** | the firm's | **replaced whole** |
| **`CLAUDE.md`** | the owner's | ⛔ **never touched** |

**One file mixing the two cannot be replaced without risking someone's own conventions — so in practice
it never is, and every vault drifts.** *That is not a hypothetical: a live vault was found five changes
behind, still pointing at a folder that had been renamed.*

**`extra-types:` / `extra-statuses:` live in `CLAUDE.md`**, not `KAPITA.md`: what one vault invents is
that vault's.

⚠️ **And the layer teaches by example, which the checker cannot see.** Its person template shipped
`domain: work` and a `role:` field — **contradicting the rule that a person is always `domain: personal`,
and naming a field the skill calls `job_title`.** *A checker compares names that exist; it cannot tell
that an example is teaching the wrong thing to fifteen people.* **Read the layer's examples against the
rules whenever either changes.**

---

## Things a future re-base must not undo

**Upstream is at 2.17.0 and moves quickly. Each of these will look like an easy thing to drop.**

**1 · The four onboarding questions.** Upstream's `onboarding.md` is built around *five answers →
structure*; ours around *what they said → notes*. **The four question slots are what let upstream's next
addition land somewhere** — without them the two files are different floor plans and every release costs
a judgement call.

**2 · `company` is not declared in `types.json`, deliberately.** `properties-and-tags.md` gives it as
**the worked example of a property to leave undeclared**: `multitext` breaks the dashboard's field
writer, `text` flags people who legitimately carry two companies. **It was declared once, in error, and
reverted.** The `company:` / `org:` *distinction* is ours and stays — **belongs-to** versus **the
counterparty** — but the declaration must not come back.

**3 · The layer never enumerates a vocabulary the skill owns.** A list of task statuses written into
`KAPITA.md` is correct on the day it is written and a **silent cap** the day the skill gains a value.
**The checker flags three or more such values on one line**, reading the sets out of
`validate_vault.py` rather than hard-coding them.

**4 · No personal detail is copied into `~/.claude/CLAUDE.md`.** The block installed there teaches the
**search** — read the owner's person note, follow its links, search the vault — and carries no name,
title or address. **Anything written there is a frozen subset that goes stale while the vault stays
live**, and two copies of a fact is the drift this project keeps paying for. **C15: one writer of
truth.**

**5 · `validate_vault.py` exempts root-level `.md` by depth, not by the name `CLAUDE.md`.** An
organisation layer is a convention file too, and its prose carries illustrative `[[wikilinks]]` that are
examples rather than references. **This is the one place patching upstream's script is right — it is the
consequence of our own design change, not a fix to their behaviour.**

**6 · The installed-skills index is pointers, and the rule says so.** `capture-and-web.md` teaches that
the machine's other skills are context the vault should carry, **and that nothing is copied out of one
into a note** — not a colour, not a template, not a threshold. **The temptation on any re-base is to
make the note more useful by filling it in.** ⛔ That inverts C15: the skill is maintained and the copy
is not, and the copy is what gets read six months later, wrong, by somebody who never opens the skill.
**The generic rule names no company**, and `check-install.py` reports how many installed skills the
index names.

---

## Still open

| | |
|---|---|
| **The four fork evals (19–22) have never been run.** | They ship as specifications |
| **`Outbox/` and inbound links** | Moving a note to `Outbox/` has not been exercised on a note with inbound links. Upstream's 2.16.2 tested that a *move* keeps links resolving by basename — **but not in a vault set to `useMarkdownLinks: true`**, where the folder is stored inside the link |
| **`KAPITA.md` distribution** | The split makes it *safe* to replace. **Nothing yet delivers it to fifteen vaults** — though `check-install.py` now *detects* a stale copy |
| ~~The version number~~ | ✅ **Settled: `3.0`.** `2.18` would have collided with a real upstream release while claiming to be one. 🔴 **And upstream's own major bump was, in its words, *"a renumbering release — identical content to 1.8.0"*** — there is no `2.0.0`, and everything before `1.5.0` is retroactive because the skill carried no version at all. **The major number there never meant magnitude**, so nothing was being claimed by taking one. `upstream_base` is what says where this sits |
| **The skill's name** | still `obsidian-second-brain` |
