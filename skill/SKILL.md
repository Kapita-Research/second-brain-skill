---
name: obsidian-second-brain
description: >
  Your own notes and work, kept as Markdown files in a folder (an Obsidian vault) and run through Claude:
  capture what you say as you say it, file it, link it, and find it again later. Use it whenever someone
  mentions their work, people they dealt with, something they owe or are owed, a decision and why, a meeting,
  a deadline, a task, a figure from research, or anything worth remembering - in any language, and even when
  they never say note, vault, or this skill's name. They talk like: "I met...", "remember that...", "he asked
  me to...", "I need to ... before Thursday", "what did X want", "when did I last talk to...", "we
  decided...", "62% of...". Also for vault work named directly: Obsidian, PKM, inbox triage, daily note,
  journal, weekly review, project/meeting/person/book/source notes, MOC, wikilink, frontmatter, tags, Bases,
  .base, search, web clipping, activity reporting, version history, recovering a deleted note. Do NOT use for
  general coding, or for files outside a vault.
metadata:
  version: "3.3.0"
  upstream_base: "obsidian-second-brain 2.17.0"
---

# Obsidian Second Brain

A single skill for running an Obsidian vault as a **second brain** through Claude — in **chat, Cowork, or Claude Code**. It does two things well:

1. **System** — capture, triage (work vs. personal), organize, link, retrieve, and review notes using proven PKM methods (PARA + MOCs + atomic notes).
2. **Syntax** — produce correct, current Obsidian Flavored Markdown, Bases (`.base`), and Canvas (`.canvas`).

> Core idea: a second brain is only as useful as it is *retrievable*. Every action should keep the vault **consistently structured** (so it can be queried) and **densely linked** (so ideas resurface). Structure is not bureaucracy — it is what lets the vault think back.

**Start here (the fastest win):** the highest-value behavior isn't building folders — it's *asking the vault*. Before or alongside any setup, offer to answer from existing notes, summarize, find commitments, or connect ideas ("what do I know about X?", "what did I tell Sarah I'd do?"). Value should show on day one; structure grows underneath it.

## First Contact — run this sequence before anything else

1. **Find the vault** — a mounted folder (Cowork), a shell at the vault root (Claude Code), or no file access (Chat). This sets your Operating Mode (below).
2. **Read the vault's `CLAUDE.md`** (vault root) if it exists. It is the owner's source of truth and **overrides this skill's defaults** — folder names, vocabulary extensions, workflows, and personal context live there, never in this skill. Re-check it before proposing anything structural.
2b. ⛔ **Never write a placeholder for a fact about the owner.** `[your name]`, `[your title]`, `[your email]`, `[insert role]` — in an email, a bio, a form, a README, anywhere. **The owner has a person note in `People/` (usually `Me.md`): it carries their name and its spellings, title, employer and addresses, and it links out to their projects, the people they deal with and what was decided.** **A card built from that note is put in front of you at the start of every session**: use it for their name, its spellings, their title and addresses, and read the note for anything the card does not carry. Read it, follow the links that bear on what you are writing, and **search the vault for the rest — reading one note is not looking.** **If a fact is genuinely not there, ask one question, and never infer it from an org chart, a table or a filename** — *a placeholder in a finished draft is a defect, not a courtesy*, and the owner is the one person the vault is guaranteed to know about.
2a. **And read any other convention file beside it** — a vault belonging to someone in an organisation often carries a second file at the root (`ACME.md`, `TEAM.md`) holding **the shared rules everyone there follows**, distributed to every member and **replaced wholesale on update**. ⛔ **Never edit that file and never write the owner's personal conventions into it** — those belong in `CLAUDE.md`, which is theirs alone. **Where the two disagree, the organisation's file governs shared vocabulary and sharing rules; `CLAUDE.md` governs everything about how this person works.** The split exists so the shared half can be updated without touching the personal half.
3. **No `CLAUDE.md`?** If the vault already has a structure, adapt to it (Golden Rules still apply) and offer to write a `CLAUDE.md` capturing its conventions. If the vault is empty or brand-new, follow `references/onboarding.md` — **a first session that reads as someone taking their notes, not as configuring a tool.** Ask about their week and their work, **write notes as they talk**, and let the scaffold (`scripts/bootstrap_vault.py`) and the vault's `CLAUDE.md` follow from what they actually said. ⛔ **Never announce a setup, and never narrate the machinery.**

---

## The Operating Loop

Almost every request maps to one stage of this cycle. Identify the stage, then act.

| Stage | Trigger phrases | What you do |
|---|---|---|
| **Capture** | "note this", "remember", "add to inbox", "action points from my meeting", **a bare URL**, or **“record that whole conversation/project”** | Write a minimal note to `Inbox/` fast. ⛔ **"Record this conversation" never means "save the transcript."** It means **record the subject** — the project it was about, its files, the people, the decisions and why, the numbers with their conditions, what was learned. **The transcript is the index to all of that, not the thing being filed**, and the things it *names* — a folder, a repo, a link, a person — **are each followed in turn.** `scripts/session.py` with no argument digests the current session from the working directory. ⛔ **And an import is not a task that finishes — it is the moment this conversation starts writing things down.** From then on, in that same session: a decision goes on the project note with its reason when it is made, a settled figure about a population becomes a `finding`, a new person gets a note, a commitment becomes a task — and **a question about the project is answered from the vault first**, because it now holds the structured version and *the conversation is the thing that will be compacted.* **The owner said it once; they will not say it again.** `capture-and-web.md` → *Record this conversation* and *Step 9*. ⛔ **A link is never read once and dropped** — follow what comes out of it, as far as the subject is worth, and stop for a reason you can name: `capture-and-web.md` → *A link is an entry point*. Any actionable to-do becomes one **task note** per item by default — Golden Rule 7. Dictated/transcribed input: resolve names against `aliases` first (`references/capture-and-web.md`). Don't over-structure yet. **Recording a whole session — a meeting, a long conversation — is different: filter it, never summarise it**; **importing one in bulk adds three rules on top** (`capture-and-web.md` → *Recording a session*, *Bulk import*). |
| **Triage** | "file this", "where does this go", "process my inbox" | Classify (work/personal + type) and move to the right folder with correct frontmatter. **See the Triage decision tree below.** |
| **Organize** | "link this", "add to the MOC", "tag", "restructure" | Add wikilinks, attach to a MOC, apply the tag/property schema. |
| **Distill** | "summarize", "extract the key idea", "make an atomic note" | Pull durable ideas into atomic/permanent notes; progressive summarization. **Summarise what you *produce*; filter what you *record*** — see Capture. |
| **Express** | "draft", "write up", "turn my notes into…" | Produce output (doc, post, slides) from existing notes. Emails, status updates, minutes, memos, talking points → pull person/org/task context first per `references/communication.md`. |
| **Review** | "daily note", "weekly review", "what's on my plate" | Run the review rituals; surface open **task notes** (`Tasks.base`) with **overdue first**, confirm statuses that look moved or stale (Rule 8), commitments, and stale items. |
| **Retrieve** | "find", "what do I know about…", "show me notes on…" | **Search first** (see Golden Rules), then synthesize. ⛔ **Asked in a non-Latin script? Translate the query into English before searching** — filenames are English by rule, so an Arabic query matches almost nothing and that is a property of the vault, not a fact about its contents. **And "there is nothing in the vault" is a claim: never say it without having searched in English, and say which words you searched.** |
| **Account** | "what did I work on", "prep my review", "what changed since…" | Reconstruct a window of activity from task-body status logs + `created:` dates (+ git history if enabled) — **never from mtime alone**. `references/retrieval-and-review.md` → *Activity reporting*. |

---

## Operating Modes — detect the environment first

The same skill behaves differently depending on where Claude is running. **Check which applies before acting.**

| Mode | How to tell | How to act |
|---|---|---|
| **Cowork** (file access) | A vault folder is connected/mounted; you have Read/Write/Edit tools | Read and write vault files **directly**. This is the primary mode for filing, organizing, and editing. Sandboxed — no `obsidian-cli`, no running Obsidian app. |
| **Claude Code** (terminal in vault) | You're in a shell at the vault root | Use the filesystem, **plus** the official `obsidian-cli` (`obsidian search`, `create`, `append`, `base:query`, …) **when it is available** — it needs Obsidian installed, enabled and *running*. Probe with `obsidian help`; if it fails, work as Cowork-with-a-shell and say so. Never let a scheduled job depend on it. See `references/cli-and-automation.md`. |
| **Chat** (no file access) | No connected folder | Produce **copy-paste-ready** output: complete notes with frontmatter, full `.base`/`.canvas` blocks, and tell the user exactly where to save each file. |

If a request needs file access you don't have, say so and fall back to copy-paste output.

**In Claude Code, check the CLI once — it is off by default and people do not know it exists.** Run
`obsidian help`. If the command is missing **and the vault has a `.obsidian/` folder** — meaning the app
*is* installed and in use — **say so once, in one line:**

> *"You're using Obsidian but its command line interface is off. Turning it on (Settings → General →
> Command line interface) lets me use its live index — backlinks, alias resolution and property search
> instead of text matching. One switch, nothing else changes."*

**Then carry on with the file tools regardless.** ⛔ **Say it once per vault and never again** — a
recommendation repeated is a requirement in disguise. **Record the outcome in the vault's `CLAUDE.md`**
so a later session does not ask twice.

**Running bundled scripts** (`scripts/*.py` — bootstrap, validator, `last-contact` sync, live dashboard server): execute them from the skill's install location; it is **read-only, which is fine** — they write only to the vault. Locate the skill root (the folder holding this SKILL.md): Claude Code → `${CLAUDE_SKILL_DIR}` if set, else the path this file loaded from; Cowork → search the mounts (e.g. `find /sessions -maxdepth 6 -path '*skills/obsidian-second-brain/SKILL.md' 2>/dev/null`) and note the shell may see different paths than the file tools. Scripts need `python3` (PyYAML optional, for stricter validation); without it, use the manual fallbacks in `references/vault-structure.md`.

---

## Golden Rules (context economy + consistency)

These make the difference between a vault that scales and one that collapses. Follow them always.

1. **Search before you read; read before you load.** Never ingest the whole vault into context. Use filename/Quick-Switcher matches, then `grep`/search operators, then open only the handful of relevant notes. Markdown is not a database — see `references/retrieval-and-review.md`. **`scripts/find.py <terms>` is that ladder in one call**: names, aliases, fields and text, ranked, with the lines that matched and a count of what else did. Open a note in full only when those lines are not enough, because every separate search and read re-sends the whole conversation. It never reads a judgement and never shortens a finding, and **it does not translate**: an Arabic question still gets its English words passed in. **When a message names a note, the per-message hook lists it: a head start on the search, never a reason to skip it.**
2. **Search before you create — names AND aliases.** Before making a new person, project, or concept note, search for an existing one (including `aliases`) and extend it instead of duplicating; always link the canonical note name. Dictated/transcribed input gets its names resolved first — ambiguous match → ask, new spelling variant → add it to the note's `aliases` (see `references/capture-and-web.md` → *Dictated & multilingual capture*, and *Matching names across scripts* for how two strings are actually compared — **normalise both sides identically, NFKC first**). Duplicate entities (`Sarah.md` *and* `Sarah Chen.md`) are the quiet way a vault becomes unsearchable. **This rule works inside one script and breaks across two** — a search for `Uruk` will not find `أوروك.md`, and the second note gets created by someone following the rule correctly. **One script for filenames, every other spelling in `aliases`:** `references/vault-structure.md` → *Naming across scripts*.
3. **Every note gets consistent frontmatter — and the rule is: you may add, you may not redefine.** Always set `type`, `domain` (work/personal/shared), and `created` — *including* quick captures (use `type: fleeting` until triaged). **A new type or a new field is free.** `type: lecture`, `died: 1998-04-02`, `github: someone` — **write it and it exists**: no permission, no migration, and no talking the owner into something that nearly fits. ⛔ **What is forbidden is taking a word that already means something** — writing `status: buried` on a person because `status` carries the task lifecycle everywhere else, or coining `death_date` when you already wrote `died` on another note. **A new name costs nothing; a reused name with a new meaning silently breaks every view built on the old one.** 🔴 **And a new value is the owner's own by default: it goes on the vault `CLAUDE.md`'s `extra-types:` / `extra-statuses:` line and nowhere else.** *That line is theirs, it is never overwritten by an update, and it reaches no other vault.* ⛔ **Never widen the skill's own vocabulary on their behalf** — the skill is shared, so a word added there arrives in everybody's vault, and *"add a type for my workouts" does not mean "and give it to my colleagues"*. **Only the person who maintains the skill does that, and only when told to.** The follow-through — those two are validated against a fixed list, so an unrecorded one is reported as an error on notes that were written correctly. Ordinary fields need no entry. ⛔ **And a new field is added *beside* the canonical one, never *instead of* it: every person involved goes in `people` — in every note, whatever their part — and a role field (`trainer`, `attendees`, `logistics`) is the subset saying which of them did what.** *A session that records who was there only in `attendees` is invisible to every search for that person, and nobody will ever know why.* See `references/properties-and-tags.md`.
4. **Link, don't orphan.** Every note connects to at least one other note or a MOC. Prefer `[[wikilinks]]`. ⛔ **And a value more than one note could carry is a link, not a string.** A university, a field of study, an employer, a client, a tool, a certification — **typed as text it creates nothing; written as `[[…]]` it becomes a hub whose backlinks *are* the answer to “who else?”.** **The test is: would you ever want the list?** *If yes it is a note; if no — a phone number, a date, a street — it stays a string.* 🔴 **And such a note may be empty:** a title, a `type` and an `aliases` line are the whole job, because **its value is what points at it, not what is in it.** See `references/note-types.md` → *Hub notes*.
5. **One idea per atomic note.** When distilling, split multi-topic notes so each concept is independently linkable and reusable.
6. **Triage explicitly.** Decide work vs. personal and the note type *before* filing. When genuinely ambiguous, leave it in `Inbox/` (`type: fleeting`, `status: needs-triage`) and ask.
7. **Actionable to-dos become task notes — wherever they surface.** *(Canonical statement — other files point here, don't restate it.)* Any trackable to-do — from a meeting, a project, a person (what you owe them), a daily note, an inbox capture, an email, or a passing remark in chat; whether the user dictates it or you extract it — becomes its own `type: task` note in `Tasks/` (link `source:` and the relevant `projects:`/`people:`), so it rolls up in `Tasks.base`. This is the default: do it without being asked, and don't stop at checkboxes. If the deadline is unclear, create the task anyway (no `due`) and confirm after. Reserve inline `- [ ]` strictly for trivial sub-steps *of a single task*. The worked example (meetings, the most common trigger) is in `references/note-types.md` → *Task*.
8. **Close the loop on tasks — statuses must move.** Capture without lifecycle is how task dashboards die (a wall of `not-started` tells you nothing). Whenever a conversation, capture, or meeting reveals a task has moved — started, finished, blocked, cancelled, or **handed over to someone else along with the follow-up** (`delegated-out`) — update its `status` in that same session and log the date in the task's body. **`delegated-out` is the one status to ask about rather than infer:** "I handed it to X" says who does the work, not who reports the outcome — so ask *"do you still need to know whether that lands?"* Yes → keep it open and set them as `assignee:`. No → `delegated-out`, which removes it from every open view and every review for good. Surface overdue tasks any time tasks are shown. **Never delete or auto-archive:** moving long-done tasks to `Archive/` is only ever *offered*, with explicit confirmation. See `references/retrieval-and-review.md` → *Task lifecycle*.
9. **Proactively connect and resurface.** A second brain should *think back*: when you touch a topic, surface related notes the user may have forgotten, flag missing links, and offer to add them — don't wait to be asked. See `references/retrieval-and-review.md`.
10. **Confirm before destructive or bulk actions.** Deleting, overwriting, mass-moving, or bulk-retagging — describe the change and get a yes first.
11. **Protect personal content.** Treat `Personal/Journal/` and anything `domain: personal` as sensitive: don't surface private reflections in work outputs, don't publish or share them without explicit confirmation, and handle them with discretion. **If the vault has an `Outbox/`, `domain: personal` never enters it** — see *`Outbox/` — the only way anything leaves*. ⛔ **And `type: judgement` — the owner's opinion of a person or a thing — is absolute, with no exception and no confirmation that can unlock it. Whenever what you are writing will be read by anyone but the owner, `Judgements/` and `type: judgement` are excluded from the search: not read and set aside — not read.** *A judgement you have read has already changed what you would write, and no rule can un-read it.* See `references/note-types.md` → *Judgements*.
12. **Mind concurrent edits.** If Obsidian may be open on the same vault, prefer the `obsidian-cli` (Claude Code) so the app stays in sync; when writing files directly, don't clobber a note the user may be editing, and tell them to reload. Never have two writers on one file at once.
13. **Match current syntax.** Use the syntax in the reference files (verified against Obsidian's official docs); check the reference rather than guessing.

---

## Triage & Routing — the work/personal decision tree

This is the heart of the system. When filing anything, walk this top-down; stop at the first match.

**Compound captures:** one utterance often contains several items — a meeting *plus* its action points *plus* a payment *plus* a new person. Decompose into items first, then route **each item** through the tree (it routes items, not messages); a single capture legitimately yields several notes of different types. 🔴 **An incident, the lesson it taught, a decision taken because of it, and whatever is still undone are four items, not one note**: the lesson is a concept (branch 6), the decision goes on the note it belongs to, and **the undone part is a task (branch 2), never a sentence in a caveat.**

```
1. Is it a half-formed capture you can't classify yet?
   → Inbox/   (status: needs-triage)

2. Is it an actionable TO-DO (something to *do*, with a status and maybe a deadline)?
   → Tasks/<Short Imperative Title>.md   (type: task; link its projects/people + source)

3. Is it a MONEY EVENT (payment, donation, expense, transfer, debt, pledge)?
   → Money/Transactions/   (type: transaction; fund: + earmark; see references/money.md — restate balances after;
                            no Money/ module → offer to add it, or log in the org/engagement note meanwhile)

4. Is it about a specific PERSON (colleague, client, friend, author, historical/public figure)?
   → People/<Name>.md   (set domain: work | personal)
                        someone you'll never deal with (author, historical figure, cited
                        executive)? add contact: none — keeps them out of the working
                        directory. One person is always ONE note; never split by role.
   …or a named SET of people (team, committee, volunteer cohort, client circle)?
   → People/<Group Name>.md   (type: group; roster in members:; each member points back via groups:)

5. Is it a SOURCE you're taking notes on (article, paper, video, web clip, internal brief/report,
   or a tool, API, site or dataset you have tested, for how it behaves)?
   → Resources/Sources/   (type: source)
   A fact ABOUT a source (what it covers, a defect in it, how it counts, how it behaves) goes in
   THAT source's note, even when it carries a number. No note for the source yet? Create it.
   …a BOOK? → Resources/Books/<Title>/<Title>.md   (type: book — one folder per book;
              chapter notes beside it: type: chapter, book: "[[Title]]")

6. Is it a durable, standalone IDEA or CONCEPT (one idea, reusable)?
   → Resources/Notes/   (atomic/permanent note; link it to a MOC)
   A LESSON or an INCIDENT is this too: the title is the claim that could be wrong, the body is
   what was believed, what happened, what is true now; tag lesson/ and set source: to the work
   that taught it.

6b. Is it a FIGURE ABOUT A POPULATION (a quantity of some group of people, households, firms,
    items or cases, that someone could quote to a reader)?
    The number must BE the claim. If the note would still say something with the number removed,
    or it describes how a document, dataset, tool, site or our own pipeline behaves, it is not a
    finding: it is branch 5 or 6, and cites the number. A score measured on a set of cases (a
    model on a benchmark, a test on held-out data) IS a finding: the cases are its population.
   → Findings/   (type: finding; base_n, dates and caveat REQUIRED — see references/findings.md;
                  no Findings/ module → offer to add it, or keep the figure inside the source note
                  with its base and caveat in the same sentence)

7. Is it WORK?
   ├─ Active effort with an outcome/deadline?     → Work/Projects/
   ├─ An ORGANIZATION you deal with (client, partner, investor, NGO, vendor)?
   │                                               → Work/Business/  (type: business — the entity;
   │                                                 a ministry/regulator/state body → type: government)
   ├─ A specific DEAL/OPPORTUNITY with an org?     → Work/Business/  (type: engagement; org: [[…]]; stage lives in status:)
   ├─ A meeting?                                   → Work/Meetings/  ·  then promote each action item to a task note (branch 2)
   └─ An ongoing responsibility (a role, an area)? → Work/Areas/

8. Is it PERSONAL?
   ├─ Reflection / journaling?  → standalone entry → Personal/Journal/ ; today's running log → Daily/ note
   ├─ A spark/idea for yourself?                   → Personal/Ideas/
   ├─ Active personal effort with an end state?    → Personal/Projects/
   └─ Ongoing life area (health, finance, home)?   → Personal/Areas/

9. Research/topic you're building knowledge in (work or personal)?
   → Resources/Research/   (hub it with a MOC in Maps/)

10. Nothing above fits?
   → Make a new type only if you can name the view, check or exclusion that will treat it
     differently from every existing type. If what you can name is a field on an existing type,
     add the field instead. A new type is the owner's own (Golden Rule 3).
```

**A decision is written where it was made**, on the project or meeting note it belongs to, as `### Decision YYYY-MM-DD: <what was decided>` with the reason on the next line. One fixed heading is what makes *"what did we decide about X"* answerable by search across every project.

**How to decide work vs. personal when blurry:** ask "who is this *for* / who benefits?" Work = job, clients, business, professional growth. Personal = you, family, health, hobbies, private reflection. People and Resources are **shared** folders — distinguish inside them with `domain:`. If still unclear, file to `Inbox/` and ask one quick question. Full rules, examples, and the `CLAUDE.md` you should drop in the vault root are in `references/vault-structure.md`.

**Action items → tasks (any source).** A note that *contains* to-dos is not a substitute for task notes — apply **Golden Rule 7** to every action item the tree routes (branch 2), whatever kind of note it surfaced in.

### `Outbox/` — the only way anything leaves

Some owners share part of their work with an organisation, a client, or a co-author. **If the vault has an `Outbox/`, it is the single exit** — whatever reads this vault from outside reads that folder and nothing else.

**This needs no rule to protect everything else.** Drafts, private notes, `Inbox/`, `Personal/`, half-finished work — they stay simply because nothing outside ever reads them. **The default is already privacy; `Outbox/` is the deliberate exception.**

| | |
|---|---|
| **What goes** | **Finished** notes that belong to the organisation. A draft about work stays out until it is done |
| ⛔ **`domain: personal` never enters it** | Refuse it in the path — this is not a judgement call |
| ⛔ **Never move anything there on your own initiative** | Not even when it is obviously work. **Deciding what other people see is the owner's act, every time** |
| **How** | **Move** the file, do not copy it. Set `domain: shared`. Then say which file moved and where |

**Withdrawing is moving it back out** — clean while nobody has used it, and worth a word of warning once they might have.

**Where that folder goes afterwards — a synced drive, a repository, nothing at all — belongs in the vault's `CLAUDE.md`, never in this skill.**

---

## Default Vault Structure

Top level (the triage tree above shows what routes where; full annotated tree + rationale in `references/vault-structure.md`):

- `Inbox/` — fast capture · `Daily/` — daily notes · `Tasks/` — task notes (`type: task`)
- `Work/` → `Projects` · `Areas` · `Business` · `Meetings`
- `Personal/` → `Projects` · `Areas` · `Journal` · `Ideas`
- `Resources/` (shared) → `Research` · `Sources` · `Books` (one folder per book) · `Notes`
- `People/` (one per person + `type: group` rosters) · `Maps/` (MOCs) · `Archive/` · `Templates/` · `Attachments/`
- `Money/` (OPTIONAL module) → fund notes + `Transactions/` (see `references/money.md`)
- `Outbox/` (OPTIONAL) — finished notes the owner has decided belong to their organisation. **The only folder anything ever leaves by.**
- `Findings/` (OPTIONAL module) — one note per research figure (see `references/findings.md`)

This is the default. If the user already has a structure, **adapt to theirs** — read it first, then apply the same routing logic to their folders. Setup, a `mkdir`/CLI bootstrap, and a *Day 1 — minimal start* are in `references/vault-structure.md`.

**New to this?** Don't build everything at once. Start minimal — `Inbox/`, `Tasks/`, and a capture habit (daily notes are optional) — then grow into the full structure as real notes accumulate. See *Day 1 — minimal start* in `references/vault-structure.md`.

---

## Reference Router — load only what the task needs

Read the **one or two** files relevant to the request. Do not load everything.

| Read this file | When |
|---|---|
| `references/onboarding.md` | **First run in a new/empty vault** — seeding from what they already have, the first session *(taking their notes, not configuring a tool)*, and the scaffold that follows from it |
| `references/vault-structure.md` | Folder design details, routing notes, the vault `CLAUDE.md` template, **renaming**, migration, sync |
| `references/methodologies.md` | Explaining/choosing PARA, Zettelkasten, LYT/MOCs; how the blend works |
| `references/note-types.md` | Creating any note — exact frontmatter schema + body template per type |
| `references/properties-and-tags.md` | Frontmatter property types, the controlled vocabulary, tag taxonomy |
| `references/markdown-syntax.md` | Wikilinks, embeds, callouts, tags, math, mermaid, footnotes, comments |
| `references/bases.md` | Building `.base` dashboards/queries; ready-made vault bases |
| `references/canvas.md` | Creating/editing `.canvas` files; layouts (mind map, board, flow) |
| `references/retrieval-and-review.md` | Finding things, query patterns, **tasks & commitments**, context economy, daily/weekly/monthly reviews |
| `references/communication.md` | Drafting emails, status updates, meeting minutes, memos, talking points — from vault context |
| `references/money.md` | Money: funds, donations, expenses, transfers, debts/receivables, pledges, balances ("who owes me") |
| `references/findings.md` | Findings: quoting a research number whole, base vs sample, comparability, superseding |
| `references/capture-and-web.md` | Inbox capture, processing, **recording a session**, **bulk import** of a conversation or archive, dictated/transcribed input, web clipping, **following a link — a URL is an entry point, never a destination**, **surveying a folder or repo before importing it**, and **importing a whole past conversation from its transcript**, and **indexing the skills already installed on the machine as pointers** |
| `references/cli-and-automation.md` | Obsidian CLI commands, scheduled recaps, the live dashboard server, automation (Code/Desktop), **and receiving or applying an update to this skill** |
| `references/version-history.md` | OPTIONAL: git version history — "what did I work on", recovering deleted content, revision tracking, automated snapshots |
| `references/community-plugins.md` | OPTIONAL: Dataview, Templater, Tasks syntax (only if user uses them) |
| `references/sharing-and-export.md` | OPTIONAL: handing a note to an organisation, exporting, team tools, backup. **"Publish this" is routed here** |

---

## Quick Syntax Cheat-Sheet (no file load needed)

```markdown
[[Note]]                      internal link
[[Note|shown text]]           link with display text
[[Note#Heading]]              link to a heading
[[Note#^block-id]]            link to a block (note the #^)
![[Note]]  ![[image.png|400]] embed note / image (width 400)
#tag  #work/project  #personal/health   inline + nested tags
==highlight==   %%hidden comment%%
> [!note] Title
> Callout body.            (types: note tip warning info success question example quote …)
- [ ] task    - [x] done    # inline steps only — tracked tasks are notes in Tasks/
```

```yaml
---
type: project          # controlled value — see properties-and-tags.md
domain: work           # work | personal | shared
status: active
created: 2026-06-16
tags:
  - work/project
---
```

```yaml
---
type: task             # task notes live in Tasks/ — see note-types.md
status: not-started    # not-started | in-progress | in-review | done | on-hold | cancelled | delegated-out
domain: work
priority: normal       # high | normal | low (optional)
due: 2026-06-25        # optional; add due_time: "14:00" only when a time matters
recurrence:            # daily | weekly | monthly | quarterly | yearly (optional)
assignee: ["[[Me]]"]   # who does it — person/org notes; defaults to the vault owner
projects: ["[[Project]]"]
people: ["[[Person]]"]
created: 2026-06-18
tags:
  - task
---
```

Default to lowercase callout types (`[!note]`). For block links the syntax is `#^` (e.g. `[[Note#^id]]`).

---

## Before Finishing Any Task

- Frontmatter present and uses **only** controlled `type`/`domain`/`status` values.
- Note is **filed** in the right folder per the triage tree, or explicitly left in `Inbox/`.
- Note is **linked** to at least one other note or a MOC.
- If the note **records any action items, to-dos, or commitments**: every one has its own task note per **Golden Rule 7** — no stray checkboxes.
- No leftover template placeholders: every `- [[ ]]` is filled in or deleted (an empty `[[ ]]` renders as a broken link).
- For `.base`/`.canvas`: the YAML/JSON is **valid** and uses current syntax (validate before delivering).
- **Write every note the request produces, then run** `scripts/validate_vault.py <vault>` **once, at the end** (see `references/cli-and-automation.md`), and report findings. Not after each note: each run is a round trip that re-sends the whole conversation, and the notes are checked together anyway.
- In Chat mode: tell the user the exact **filename and folder** to save to.
