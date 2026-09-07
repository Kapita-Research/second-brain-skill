# Fork plan — `obsidian-second-brain` v2.9.2 → ours

**Status:** **items 1–14 applied** (8 closed with no change). Three deferred, listed below. `upstream/` is the untouched original, `skill/` is ours.
**What shipped is in [`skill/CHANGELOG.md`](skill/CHANGELOG.md); what lives outside the skill is in [`FORK-NOTES.md`](FORK-NOTES.md).** This file holds what was *intended*, before any of it was built — kept as the record of the original scope.

---

## The decision

**Fork, not overlay.** Settled — item 4 below changes a golden rule, and an overlay cannot.

**The price:** upstream updates stop flowing to us.
**The condition that makes it acceptable:** **keep the diff small and written down**, so it can be
re-applied to a newer upstream if one ships. **This file is that record.**

---

## The scope, stated before anything is touched

> **The skill's world has exactly one inhabitant, and it stays that way. We are not widening it to
> fifteen people — we are adding an exit door.**

**This is the sentence that keeps the fork small.** Four things follow, and every one of them is
something we now do **not** have to build:

| | |
|---|---|
| **No multi-user anything** | no permissions, no visibility tiers, no shared editing, no conflict resolution |
| **One direction only** | the skill **writes out** and never reads back — so there is still exactly one writer, no sync and nothing to reconcile |
| **Nothing returns to the vault** | a colleague's notes never appear among the owner's files. Firm knowledge reaches them as an **answer from Claude**, through a different door |
| **The folder is a drop point, not a space** | so item 5 shrinks to *move a file*, with two refusals |

### And that settles the name — `Outbox/`

**`Shared/` was wrong twice over.** `domain: shared` is already taken upstream and means *shared
between work and personal* — but the deeper problem is the word itself: **"shared" implies a two-way
space, and this is a one-way exit.**

**`Outbox/` pairs with the `Inbox/` that already exists:** unsorted things arriving · decided things
leaving. **Understood at a glance, no collision, and still generic** — an outbox makes sense for anyone
sharing with anyone: a team, a client, a co-author.

---

## The changes

Ordered by how independent they are. **1–3 add without touching anything that exists.**

### 1 · Arabic normalisation — `NFKC` first

**Missing entirely.** `grep NFKC` returns zero. The onboarding asks about language and aliases resolve
names, but there are **no normalisation rules**, so the same name written two ordinary ways does not
match.

**The seven steps:** NFKC → strip bidi/zero-width → strip diacritics → strip tatweel → fold
`أ إ آ ٱ → ا`, `ة → ه`, `ى → ي`, `ؤ → و`, `ئ → ي` → Arabic-Indic digits → ASCII → lowercase Latin,
collapse whitespace. **Applied identically when writing an alias and when searching for one.**

> 🔴 **NFKC is step 1 and everything depends on it.** Text extracted from a PDF carries the *drawn
> shape* of a letter, not the letter — `مدير` typed and `ﻣﺪﻳﺮ` extracted **share no trigram at all.**

> ⛔ **Never fold `چ گ پ ڤ`.** They are distinct in Iraqi — چاي is not جاي.

**Lands in:** `references/capture-and-web.md` (it already has *Dictated & multilingual capture*) ·
a pointer from Golden Rule 2 in `SKILL.md`.

---

### 2 · `type: finding` — the research module

**Missing entirely.** For a research firm this is the product.

**Fields, all required:** `measure` · `population` · `base_n` *(the base of **this** number)* ·
`sample_n` *(the study's achieved sample)* · `collected` *(fieldwork dates)* · `describes` *(the period
the figure is about)* · `basis` *(survey | desk | expert | supplied)* · `caveat`.

**The two traps that actually happen:**
- **`base_n` is not `sample_n`.** A figure computed on 340 people inside a study of 1,200 has a base of 340.
- **`collected` is not `describes`.** Fieldwork in March 2025 describing 2024 is not a 2025 figure.

**Behaviour:** quote a finding **whole** — number, base, dates, caveat, in one sentence. **Never the
number alone, however short the question.** A finding missing a field is a **draft that is not quoted.**
Two findings combine only if measure, population and unit all match; otherwise list them with their
differences.

**Lands in:** `references/note-types.md` · `assets/types.json` · a new
`assets/templates/Finding Template.md` · a new `assets/bases/Findings.base` · a branch in the triage
tree in `SKILL.md`.

---

### 3 · Remove Obsidian Publish

🔴 **A hazard, not a feature.** A person says *"publish this"* meaning *"share it with my team"*, and
the mechanism puts it **on the public internet**. The rarest kind of mistake: one that cannot be taken
back.

**Remove:** `references/publish-and-sharing.md` · its row in the reference router · the `publish:`
frontmatter key · every mention in `SKILL.md`, `capture-and-web.md`, `community-plugins.md`.

*(`grep -ril publish` currently hits 5 files.)*

---

### 4 · The filtered working record — **changes a golden rule**

**For a substantive session, do not summarise.**

> **Summarising re-reads and rewrites in other words, so it loses.**
> **Filtering removes the scaffolding and keeps the content as it was said.**

**Scaffolding:** *"let me check"*, *"yes exactly"*, restated explanations, anything read back.
**Content:** what was decided, what was rejected and why, any figure, any name, doubts, open questions
— **in the person's own words, verbatim where the wording matters.**

**Written during the session, not after**, so an interruption loses nothing.

**Lands in:** `references/capture-and-web.md` · and it **modifies** the Capture row of the Operating
Loop in `SKILL.md`. **This is the change that forces a fork.**

---

### 5 · `Outbox/` — the exit door

**Missing entirely.** Nothing upstream models *"this belongs to my organisation."*

**Behaviour:** a note the person has decided belongs to the firm **moves** into `Outbox/`. Nothing else
about it changes — same Markdown, same frontmatter. **It is a move, not a copy and not a sync.**

| | |
|---|---|
| ⛔ | **`domain: personal` never enters it.** A rule in the path, not a judgement |
| ⛔ | **Nothing moves there on Claude's initiative** — even when obviously work |
| ✅ | The destination lives in the vault's `CLAUDE.md`, never in the skill |

**Why staging and not sending:** whatever reads the vault later reads **that folder and nothing else**,
so nobody ever sorts months of notes retroactively. **The sorting happens once, at writing time, when
the person already knows the answer.**

**Lands in:** the triage tree and vault structure in `SKILL.md` · `references/vault-structure.md`.

---

### 6 · Rename preserves the old name as an alias

**Upstream renames and rewrites links. It does not keep the old name.**

📐 **Three steps, not two:** rename the file → rewrite every link → **add the old name to `aliases`.**

**Step 3 is the valuable one:** a link missed anywhere still resolves, search on the old name still
works, and anything reading the vault later can tell that both names are one thing.

**Lands in:** `SKILL.md` (a golden rule or a short section) · `references/vault-structure.md`.

---

### 7 · Seed from what already exists

**Upstream asks five questions, scaffolds, then captures.** Value arrives at "minute ten", from notes
the person types **in that session**.

📐 **Add one step before the questions:** *"point me at anything you already have — a folder of
documents, old notes, a chat log — and I will read it, organise it, and then you can ask me about it."*

**Two things follow:** the person sees value from **their own existing material** before writing a line,
and **the vault is not empty on day one** — which at fifteen people is how the corpus gets built
without anyone being asked to fill anything.

**Lands in:** `references/onboarding.md`.

---

### 8 · ⚠️ Re-check: the local dashboard as the default view

**The original plan (4.1) said:** make `dashboard_server.py` the default view, and demote the six
`.base` files to an optional add-on for Obsidian users.

🔁 **That was decided before Obsidian became part of the skill. It now partly reverses.**

**Bases are primary, not an add-on** — a consistently written `status` field becomes a board, `due`
becomes a calendar, `type` becomes a filter. **The views nobody built come free from fields already
being written.** The dashboard stays for people who decline Obsidian.

**Lands in:** `references/cli-and-automation.md` · `references/bases.md` · the reference router.

---

## Do not change

**Keeping the diff small is the whole condition of forking.** Leave alone:

- The **reference router** and the load-one-or-two rule — it is why the skill stays cheap
- The **triage tree** structure — add a branch, do not restructure
- **Golden rules 7 and 8** (task notes, statuses must move) — they are the Notion post-mortem, correct
- **`in-review`** as distinct from `on-hold` — already exactly what was asked for elsewhere
- The **three operating modes** (Chat / Cowork / Claude Code)
- The **money module** — irrelevant to the firm, but the rule is *does it serve the vault's owner*,
  and stripping personal life turns this into a company tool in a personal costume

---

## Deferred — known, decided, and not done

**Nothing here is forgotten or unresolved. Each was raised, understood, and postponed deliberately.**

**Four items. One of them — 2 — was found by *running* an eval rather than reading anything, which is
the argument for using the skill before improving it further.**

### 🔴 1 · `Outbox/` collides with the sync guidance

**`Outbox/` is listed inside the vault, and the skill also says *"never stack two sync engines on one
folder."*** Those two cannot both hold once the outbox has to reach a shared drive:

| | |
|---|---|
| **Whole vault in Drive** | 🔴 `Personal/`, `Inbox/` and every draft upload too — **the privacy premise collapses** |
| **Vault on one engine, `Outbox/` on another** | 🔴 **two engines, one tree** — conflicted copies, exactly as warned |

**The fix is to say `Outbox/` may live outside the vault, or be a link to a folder that does** — and to
write down the three workable arrangements with their costs:

1. **Vault unsynced, outbox is a real Drive folder.** Cost: no vault backup without `git`.
2. **Vault in Drive with `Personal/` excluded.** Cost: **one wrong exclusion rule uploads everything.**
3. **Vault on engine A, outbox a link into Drive, A excluding it.** Cost: one-time manual setup.

**And one hard rule regardless: two sync engines never write the same path.**

**Lands in:** `references/vault-structure.md` § *Sync & multi-device* · the structure list in `SKILL.md`.

### 🔴 2 · Moving to `Outbox/` leaves its links behind

**Found by running eval 14, not by reading.** A project note carrying `client: "[[Uruk Technology]]"`
moves alone — **so the receiver holds a link that does not resolve.**

**Moving the linked set is not the answer.** Golden Rule 4 makes every note connect to another, so the
graph is connected by design: **following links transitively pulls the whole vault — and crosses
`domain: personal` on the way.** That turns the outbox from a door into a hole.

**Proposed and not decided: one hop, offered rather than performed** — *"this references X and Y, send
them too?"* — with each candidate checked against the same refusals.

> **And it degrades better than it looks:** `[[Uruk Technology]]` still reads as a name, so a human
> understands it even unresolved. **The link carries meaning without the file** — which is only true
> because links are names rather than identifiers.

⏸️ **Deferred deliberately: the same question is on the list for Mohammed Mustafa**, whose own tension 07
is about exactly this — a link layer that does not know the permission rules. **His answer may be better
than ours, and it costs nothing to wait for it.**

**Lands in:** the `Outbox/` section of `SKILL.md`.

### 3 · `Outbox/` is in no ritual

**The weekly review asks what moved, what is overdue, what is still in `Inbox/`. It never asks *"what
finished this week that belongs to the firm?"*** One line — **and habits form in rituals, not in rules.**

**Lands in:** `references/note-types.md` → *Weekly review* · `references/retrieval-and-review.md`.

### 4 · No home for what you authored

**`source` is defined as material you did *not* author.** A proposal, a report, a questionnaire or a deck
**you produced** has no branch in the triage tree — for a research firm that is half the output.

**Item 9 already makes `type: deliverable` writable.** What is missing is a **routing branch** so it does
not land somewhere arbitrary.

**Lands in:** the triage tree in `SKILL.md`.

---

## Still open

| # | Question |
|---|---|
| ~~1~~ | ~~**The staging folder's name**~~ — ✅ **closed: `Outbox/`.** See *The scope* above |
| 2 | **The skill's name.** Not `kapita-*`; the point is that it survives a departure |
| 3 | **Does `engagement` stay?** It duplicates a project with `status: proposed`. Harmless while standalone; a decision at the crossing |
| 4 | **Does the research module ship enabled or opt-in?** It is a module like `money` — probably opt-in, chosen at onboarding |
| 5 | **Arabic renderings of the team's names** — written but not confirmed. A wrong alias resolves *confidently* to the wrong person |
| 6 | **KAPITA's vocabulary** — deferred deliberately: observed from a month of use, not copied from Notion, which holds two contradictory phase sets |
