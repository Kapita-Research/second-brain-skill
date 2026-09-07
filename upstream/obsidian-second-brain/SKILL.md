---
name: obsidian-second-brain
description: >
  Run an Obsidian vault as a second brain through Claude (chat, Cowork, or Claude Code): capture, triage
  work vs. personal, organize, link, retrieve, and review notes — and create/edit Markdown, Bases (.base),
  and Canvas (.canvas) with correct, current syntax. Use for any Obsidian or PKM task: vault setup,
  capturing or filing a note, inbox triage, daily/weekly notes and reviews, projects, meetings, people,
  book/chapter/source notes, reading, ideas, atomic notes, MOCs, tags and frontmatter, search, web clipping, automation.
  Trigger on: Obsidian, vault, second brain, PKM, note, capture, inbox, daily note, journal,
  project/meeting/people/book/chapter/source/literature note, MOC, wikilink, frontmatter, callout, tag, Bases, .base,
  Canvas, .canvas, Dataview, Templater, Obsidian CLI, "file this", "organize my notes",
  donations, debts, transactions, funds, "who owes me". Do NOT use for general coding, for file management outside a vault,
  or for standalone documents (docx/pdf/pptx) unrelated to vault notes.
metadata:
  version: "2.9.2"
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
3. **No `CLAUDE.md`?** If the vault already has a structure, adapt to it (Golden Rules still apply) and offer to write a `CLAUDE.md` capturing its conventions. If the vault is empty or brand-new, run the **onboarding interview** in `references/onboarding.md` — five questions about the owner's work, then the scaffold (`scripts/bootstrap_vault.py`) and a `CLAUDE.md` written from the answers. Never scaffold before the interview.

---

## The Operating Loop

Almost every request maps to one stage of this cycle. Identify the stage, then act.

| Stage | Trigger phrases | What you do |
|---|---|---|
| **Capture** | "note this", "remember", "add to inbox", "action points from my meeting" | Write a minimal note to `Inbox/` fast. Any actionable to-do becomes one **task note** per item by default — Golden Rule 7. Dictated/transcribed input: resolve names against `aliases` first (`references/capture-and-web.md`). Don't over-structure yet. |
| **Triage** | "file this", "where does this go", "process my inbox" | Classify (work/personal + type) and move to the right folder with correct frontmatter. **See the Triage decision tree below.** |
| **Organize** | "link this", "add to the MOC", "tag", "restructure" | Add wikilinks, attach to a MOC, apply the tag/property schema. |
| **Distill** | "summarize", "extract the key idea", "make an atomic note" | Pull durable ideas into atomic/permanent notes; progressive summarization. |
| **Express** | "draft", "write up", "turn my notes into…" | Produce output (doc, post, slides) from existing notes. Emails, status updates, minutes, memos, talking points → pull person/org/task context first per `references/communication.md`. |
| **Review** | "daily note", "weekly review", "what's on my plate" | Run the review rituals; surface open **task notes** (`Tasks.base`) with **overdue first**, confirm statuses that look moved or stale (Rule 8), commitments, and stale items. |
| **Retrieve** | "find", "what do I know about…", "show me notes on…" | **Search first** (see Golden Rules), then synthesize. |

---

## Operating Modes — detect the environment first

The same skill behaves differently depending on where Claude is running. **Check which applies before acting.**

| Mode | How to tell | How to act |
|---|---|---|
| **Cowork** (file access) | A vault folder is connected/mounted; you have Read/Write/Edit tools | Read and write vault files **directly**. This is the primary mode for filing, organizing, and editing. Sandboxed — no `obsidian-cli`, no running Obsidian app. |
| **Claude Code** (terminal in vault) | You're in a shell at the vault root | Use the filesystem **and** the official `obsidian-cli` (`obsidian search`, `create`, `append`, `daily:append`, etc.) for live operations and automation. See `references/cli-and-automation.md`. |
| **Chat** (no file access) | No connected folder | Produce **copy-paste-ready** output: complete notes with frontmatter, full `.base`/`.canvas` blocks, and tell the user exactly where to save each file. |

If a request needs file access you don't have, say so and fall back to copy-paste output.

**Running bundled scripts** (`scripts/*.py` — bootstrap, validator, live dashboard server): execute them from the skill's install location; it is **read-only, which is fine** — they write only to the vault. Locate the skill root (the folder holding this SKILL.md): Claude Code → `${CLAUDE_SKILL_DIR}` if set, else the path this file loaded from; Cowork → search the mounts (e.g. `find /sessions -maxdepth 6 -path '*skills/obsidian-second-brain/SKILL.md' 2>/dev/null`) and note the shell may see different paths than the file tools. Scripts need `python3` (PyYAML optional, for stricter validation); without it, use the manual fallbacks in `references/vault-structure.md`.

---

## Golden Rules (context economy + consistency)

These make the difference between a vault that scales and one that collapses. Follow them always.

1. **Search before you read; read before you load.** Never ingest the whole vault into context. Use filename/Quick-Switcher matches, then `grep`/search operators, then open only the handful of relevant notes. Markdown is not a database — see `references/retrieval-and-review.md`.
2. **Search before you create — names AND aliases.** Before making a new person, project, or concept note, search for an existing one (including `aliases`) and extend it instead of duplicating; always link the canonical note name. Dictated/transcribed input gets its names resolved first — ambiguous match → ask, new spelling variant → add it to the note's `aliases` (see `references/capture-and-web.md` → *Dictated & multilingual capture*). Duplicate entities (`Sarah.md` *and* `Sarah Chen.md`) are the quiet way a vault becomes unsearchable.
3. **Every note gets consistent frontmatter.** Always set `type`, `domain` (work/personal/shared), and `created` — *including* quick captures (use `type: fleeting` until triaged). Use the controlled vocabulary in `references/properties-and-tags.md`; never invent property names or status values ad hoc.
4. **Link, don't orphan.** Every note connects to at least one other note or a MOC. Prefer `[[wikilinks]]`.
5. **One idea per atomic note.** When distilling, split multi-topic notes so each concept is independently linkable and reusable.
6. **Triage explicitly.** Decide work vs. personal and the note type *before* filing. When genuinely ambiguous, leave it in `Inbox/` (`type: fleeting`, `status: needs-triage`) and ask.
7. **Actionable to-dos become task notes — wherever they surface.** *(Canonical statement — other files point here, don't restate it.)* Any trackable to-do — from a meeting, a project, a person (what you owe them), a daily note, an inbox capture, an email, or a passing remark in chat; whether the user dictates it or you extract it — becomes its own `type: task` note in `Tasks/` (link `source:` and the relevant `projects:`/`people:`), so it rolls up in `Tasks.base`. This is the default: do it without being asked, and don't stop at checkboxes. If the deadline is unclear, create the task anyway (no `due`) and confirm after. Reserve inline `- [ ]` strictly for trivial sub-steps *of a single task*. The worked example (meetings, the most common trigger) is in `references/note-types.md` → *Task*.
8. **Close the loop on tasks — statuses must move.** Capture without lifecycle is how task dashboards die (a wall of `not-started` tells you nothing). Whenever a conversation, capture, or meeting reveals a task has moved — started, finished, blocked, cancelled — update its `status` in that same session and log the date in the task's body. Surface overdue tasks any time tasks are shown. **Never delete or auto-archive:** moving long-done tasks to `Archive/` is only ever *offered*, with explicit confirmation. See `references/retrieval-and-review.md` → *Task lifecycle*.
9. **Proactively connect and resurface.** A second brain should *think back*: when you touch a topic, surface related notes the user may have forgotten, flag missing links, and offer to add them — don't wait to be asked. See `references/retrieval-and-review.md`.
10. **Confirm before destructive or bulk actions.** Deleting, overwriting, mass-moving, or bulk-retagging — describe the change and get a yes first.
11. **Protect personal content.** Treat `Personal/Journal/` and anything `domain: personal` as sensitive: don't surface private reflections in work outputs, don't publish or share them without explicit confirmation, and handle them with discretion.
12. **Mind concurrent edits.** If Obsidian may be open on the same vault, prefer the `obsidian-cli` (Claude Code) so the app stays in sync; when writing files directly, don't clobber a note the user may be editing, and tell them to reload. Never have two writers on one file at once.
13. **Match current syntax.** Use the syntax in the reference files (verified against Obsidian's official docs); check the reference rather than guessing.

---

## Triage & Routing — the work/personal decision tree

This is the heart of the system. When filing anything, walk this top-down; stop at the first match.

**Compound captures:** one utterance often contains several items — a meeting *plus* its action points *plus* a payment *plus* a new person. Decompose into items first, then route **each item** through the tree (it routes items, not messages); a single capture legitimately yields several notes of different types.

```
1. Is it a half-formed capture you can't classify yet?
   → Inbox/   (status: needs-triage)

2. Is it an actionable TO-DO (something to *do*, with a status and maybe a deadline)?
   → Tasks/<Short Imperative Title>.md   (type: task; link its projects/people + source)

3. Is it a MONEY EVENT (payment, donation, expense, transfer, debt, pledge)?
   → Money/Transactions/   (type: transaction; fund: + earmark; see references/money.md — restate balances after;
                            no Money/ module → offer to add it, or log in the org/engagement note meanwhile)

4. Is it about a specific PERSON (colleague, client, friend, author)?
   → People/<Name>.md   (set domain: work | personal)
   …or a named SET of people (team, committee, volunteer cohort, client circle)?
   → People/<Group Name>.md   (type: group; roster in members:; each member points back via groups:)

5. Is it a SOURCE you're taking notes on (article, paper, video, web clip, internal brief/report)?
   → Resources/Sources/   (type: source)
   …a BOOK? → Resources/Books/<Title>/<Title>.md   (type: book — one folder per book;
              chapter notes beside it: type: chapter, book: "[[Title]]")

6. Is it a durable, standalone IDEA or CONCEPT (one idea, reusable)?
   → Resources/Notes/   (atomic/permanent note; link it to a MOC)

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
```

**How to decide work vs. personal when blurry:** ask "who is this *for* / who benefits?" Work = job, clients, business, professional growth. Personal = you, family, health, hobbies, private reflection. People and Resources are **shared** folders — distinguish inside them with `domain:`. If still unclear, file to `Inbox/` and ask one quick question. Full rules, examples, and the `CLAUDE.md` you should drop in the vault root are in `references/vault-structure.md`.

**Action items → tasks (any source).** A note that *contains* to-dos is not a substitute for task notes — apply **Golden Rule 7** to every action item the tree routes (branch 2), whatever kind of note it surfaced in.

---

## Default Vault Structure

Top level (the triage tree above shows what routes where; full annotated tree + rationale in `references/vault-structure.md`):

- `Inbox/` — fast capture · `Daily/` — daily notes · `Tasks/` — task notes (`type: task`)
- `Work/` → `Projects` · `Areas` · `Business` · `Meetings`
- `Personal/` → `Projects` · `Areas` · `Journal` · `Ideas`
- `Resources/` (shared) → `Research` · `Sources` · `Books` (one folder per book) · `Notes`
- `People/` (one per person + `type: group` rosters) · `Maps/` (MOCs) · `Archive/` · `Templates/` · `Attachments/`
- `Money/` (OPTIONAL module) → fund notes + `Transactions/` (see `references/money.md`)

This is the default. If the user already has a structure, **adapt to theirs** — read it first, then apply the same routing logic to their folders. Setup, a `mkdir`/CLI bootstrap, and a *Day 1 — minimal start* are in `references/vault-structure.md`.

**New to this?** Don't build everything at once. Start minimal — `Inbox/`, `Tasks/`, and a capture habit (daily notes are optional) — then grow into the full structure as real notes accumulate. See *Day 1 — minimal start* in `references/vault-structure.md`.

---

## Reference Router — load only what the task needs

Read the **one or two** files relevant to the request. Do not load everything.

| Read this file | When |
|---|---|
| `references/onboarding.md` | **First run in a new/empty vault** — the 5-question interview, answer→structure mapping, scaffold + first capture |
| `references/vault-structure.md` | Folder design details, routing notes, the vault `CLAUDE.md` template, migration, sync |
| `references/methodologies.md` | Explaining/choosing PARA, Zettelkasten, LYT/MOCs; how the blend works |
| `references/note-types.md` | Creating any note — exact frontmatter schema + body template per type |
| `references/properties-and-tags.md` | Frontmatter property types, the controlled vocabulary, tag taxonomy |
| `references/markdown-syntax.md` | Wikilinks, embeds, callouts, tags, math, mermaid, footnotes, comments |
| `references/bases.md` | Building `.base` dashboards/queries; ready-made vault bases |
| `references/canvas.md` | Creating/editing `.canvas` files; layouts (mind map, board, flow) |
| `references/retrieval-and-review.md` | Finding things, query patterns, **tasks & commitments**, context economy, daily/weekly/monthly reviews |
| `references/communication.md` | Drafting emails, status updates, meeting minutes, memos, talking points — from vault context |
| `references/money.md` | Money: funds, donations, expenses, transfers, debts/receivables, pledges, balances ("who owes me") |
| `references/capture-and-web.md` | Inbox capture, processing, dictated/transcribed input, web clipping (Defuddle / Web Clipper) |
| `references/cli-and-automation.md` | Obsidian CLI commands, scheduled recaps, the live dashboard server, automation (Code/Desktop) |
| `references/community-plugins.md` | OPTIONAL: Dataview, Templater, Tasks syntax (only if user uses them) |
| `references/publish-and-sharing.md` | OPTIONAL: Obsidian Publish, exporting/sharing notes |

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
status: not-started    # not-started | in-progress | in-review | done | on-hold | cancelled
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
- After bulk or vault-wide changes: **run** `scripts/validate_vault.py <vault>` (see `references/cli-and-automation.md`) and report findings.
- In Chat mode: tell the user the exact **filename and folder** to save to.
