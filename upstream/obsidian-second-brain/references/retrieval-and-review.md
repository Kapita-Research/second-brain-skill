# Retrieval & Review

How to **find** things without burning context, and how to run the **review** rituals that make a second brain "think back." This is where context economy lives — the discipline that keeps the vault fast and cheap as it grows past hundreds of notes.

## The retrieval ladder (cheapest first)

Never load the whole vault. Climb only as far as you need:

1. **Name match** — guess the note title / use Quick Switcher logic. If you know the file, open just that file.
2. **Metadata filter** — filter by `type`, `domain`, `status`, `tags` (via a Base, or `grep` on frontmatter). Narrow to a candidate set.
3. **Keyword search** — full-text search / `grep` for terms across the candidate set.
4. **Open the few** — read the handful of notes that matched, not the folder.
5. **Synthesize** — answer from those notes; cite them as `[[wikilinks]]`.

> Rule of thumb: if you're about to read more than ~5–10 notes to answer something, stop and narrow with a filter or a Base instead.

## Search operators (core Search plugin)

```
path:Work/Projects        in a folder
tag:#topic/ai             has a tag
file:meeting              filename match
line:(action item)        terms on one line
section:(results)         terms in one section
content:revenue           body only
/\d{4}-\d{2}-\d{2}/        regex
```
Combine: `path:Work tag:#work/client status active`. Embed a live search in a note with a ```` ```query ```` block.

## Searching from the shell (Cowork / Claude Code)

```bash
# notes of a given type
grep -rl '^type: project' --include='*.md' .
# active work projects
grep -rlZ '^type: project' --include='*.md' . | xargs -0 grep -l '^domain: work' | xargs grep -l '^status: active'
# everything mentioning a person
grep -rli 'Sarah Chen' --include='*.md' .
# recently modified
ls -t **/*.md | head -20
```
In Claude Code you also have `obsidian search query="..."` (see `cli-and-automation.md`), which respects the live index.

## Structured queries → use Bases

For anything you'd ask repeatedly ("all active projects", "unread books", "people I haven't logged in 30 days"), build a **Base** instead of re-searching each time (`bases.md`). Bases are the queryable layer that keeps Markdown viable at scale. If the user has Dataview installed, `community-plugins.md` has equivalent queries.

## Answering "what do I know about X?"

1. Filter to candidates: `tag:#topic/X` or the topic's MOC in `Maps/`.
2. Open the MOC first — it's the curated hub and often answers directly.
3. Pull the 3–8 most relevant notes; synthesize in your own words.
4. Cite sources as wikilinks so the user can jump in.
5. If you spot a missing connection, **offer** to add a link or a new atomic note.

## Proactive connections — the "think back" habit

The payoff of a second brain isn't just retrieval on demand — it's the system *surfacing what you'd have forgotten*. Build this into ordinary work; don't wait to be asked:

- **On capture/triage:** name 1–3 existing notes the new item relates to and offer to link them. If it completes a cluster, suggest (or create) a MOC.
- **On retrieval:** after answering, point out an adjacent note or a non-obvious connection ("this also touches [[X]] from three months ago").
- **Before events:** prepping for a 1:1 or meeting → surface the person's note, open commitments, and the last few interactions unprompted.
- **Missing links & orphans:** when a note clearly *should* link somewhere but doesn't, flag it and offer the link.
- **Resurface the stale:** during reviews, pull forward relevant notes untouched for a while ("you have an old note on [[Y]] that fits this project").

Keep it an **offer**, not an automatic edit — propose the connection, let the user confirm. This is what makes the vault feel like it thinks back.

## Tracking tasks & commitments

A top second-brain job is answering *"what's on my plate / what did I commit to?"* Tasks are notes per **Golden Rule 7** (SKILL.md — the canonical statement); this section covers the *query and review* side.

- **Bases CAN query task notes.** Because a task is a note with frontmatter (`status`, `due`, `due_time`, `priority`, `projects`, `people`, `assignee`, …), a `.base` aggregates them natively — see the ready-made **Open tasks** dashboard in `bases.md`. That's the answer to "what are my open tasks": read `Tasks.base` (or filter `type == "task"` by `status`/`due`), don't grep checkboxes.
- **Stray-checkbox sweep.** To find action items not yet promoted (in any note type), search `grep -rn "^[[:space:]]*- \[ \] " --include="*.md" .` (or the `line:("- [ ] ")` operator in Obsidian) and offer to promote each hit to a task note.
- **Relationships.** `parent-task:` for subtasks, `blocked-by:` for dependencies, `related:` for siblings, `assignee:` for who is *responsible* for doing it (every new task defaults to the vault owner); tasks sharing a `projects:`/`people:` link surface together automatically. "What's on my plate" views can group or filter by `assignee` — the vault owner's own tasks are those assigned to them. Things *others* owe *you* are tasks too — title them "Waiting on …" so both directions show up in the table.

### Task lifecycle — keeping statuses honest

`not-started → in-progress → in-review → done` (plus `on-hold`, `cancelled`). The system only works if statuses move (Golden Rule 8):

- **Update on evidence, immediately.** "I sent the proposal" / "we dropped that" — in any conversation, capture, or meeting — means set the task `done` / `cancelled` / `in-progress` in the same session, add a one-line dated note in the task body, and confirm what changed.
- **`in-review` is the handoff state.** The assignee has delivered the work and is waiting on someone else — a reviewer, a manager, a client — to approve it or ask for changes. "I sent it to X for review" / "waiting on their feedback" sets `in-review`; it then goes **back to `in-progress`** if changes are requested, or **forward to `done`** when approved. It is *not* `on-hold` (nobody working, nobody owes an answer) and not `done` (nothing is finished until someone says so). Because someone owes a reply, `in-review` tasks are the first thing to chase in a review — name the reviewer and how long it's been sitting.
- **Overdue is a decision, not wallpaper.** Overdue items lead every task display; each one gets a choice — do it, reschedule `due`, or consciously `cancelled` — never silent carry-over. An `in-review` task past its due date still counts as overdue: the work isn't accepted yet.
- **Stale check (reviews).** List `in-progress` untouched ~2 weeks, `in-review` sitting more than ~1 week (chase the reviewer), and `not-started` older than a month; ask the user, don't assume.
- **Never delete or auto-archive.** Done/cancelled tasks stay in `Tasks/` (the *Done & cancelled* view hides them from open lists). An `Archive/` sweep of long-done tasks may be *offered* in a monthly review — explicit confirmation only; their `source:`/`projects:` links are useful history.
- **Recurring tasks** — `recurrence: daily | weekly | monthly | quarterly | yearly`. On completion, **don't** mark `done`: log the completion date in the body and advance `due` to the next occurrence (default — keeps `Tasks/` tidy). If per-occurrence history matters, spawn a dated copy instead (`Send weekly report 2026-07-10.md`) and mark *that* one done.

When asked "what are my open tasks" / "what's on my plate," default to reading every `type: task` note where `status` is not `done`/`cancelled` (or `Tasks.base`) and **presenting them as a Markdown table in chat** with columns `# | Task | Priority | Due | Thread`:

- **Sort** by priority (`high` → `normal` → `low`), then `due` (dated before undated, earliest first), then alphabetical — highest-leverage first.
- **Task** = the note title. **Priority** = `High`/`Normal`/`Low` (`—` if unset). **Due** = `due` (append `due_time` when set; `—` if none). **Thread** = the line of work it belongs to — its `projects:` link, falling back to `source:` then `related:`, with the `[[ ]]` stripped. Add an optional **Assignee** column when tasks are assigned to anyone besides the vault owner.
- Exclude `done`/`cancelled`; **overdue rows lead and are flagged**. After the table, add a one-line read: total open, how many are high-priority, the nearest deadline, and the busiest thread. Then close the loop (Rule 8): ask about anything that looks moved or stale, and offer status updates, due dates/priorities, or — with confirmation — an archive sweep of long-done tasks.

(If the user prefers inline-checkbox tasks instead, the optional **Tasks**/Dataview plugins can aggregate those — see `community-plugins.md`.)

## Review rituals

Reviews are what turn a pile of notes into a system. Offer to run these; they pair well with scheduled tasks (`cli-and-automation.md`). **The weekly is the high-value one — start there.** None of these require a daily-note habit: reviews degrade gracefully to `Tasks.base` + `Work/Meetings/` alone.

### Daily (2–5 min) — optional habit
- Create/open today's `Daily/` note.
- Surface open **task notes** due today / overdue (`Tasks.base`); pull any loose action items from yesterday's note, recent meetings, or any note and promote them to task notes.
- Empty quick captures from `Inbox/` that are easy to file.

### Weekly (15–20 min) — the high-value one
- Read the week's meetings, daily notes, and journal entries — whichever exist.
- **Task lifecycle sweep:** overdue first (do / reschedule / cancel each), then `in-review` items sitting over a week (chase the reviewer by name), then stale `in-progress` and month-old `not-started` (see *Task lifecycle*).
- **Wins / misses / dropped.**
- **Focus score:** estimate the % of effort that went to stated priorities; name the gap plainly (e.g., "you said Q3 launch was #1 but 60% went to support"). Be honest, not harsh.
- Triage any lingering `Inbox/` items.
- Pick **top 3** for next week.
- Move finished projects and tasks to `status: done` (projects then `Archive/` when fully closed).

### Monthly / quarterly
- Review `Areas/` against their "what good looks like."
- Prune/merge: find orphan notes (no links) and stale `active` projects.
- Update MOCs; promote recurring themes into a new MOC.
- Re-tag drift: check that `type`/`domain`/`status` are still consistent (schema hygiene) — **run** `scripts/validate_vault.py` for the full sweep.

## Vault hygiene checks (run on request)

- **Orphans:** notes with no inbound/outbound links → link them or archive.
- **Schema drift:** notes missing `type`/`domain`, or using off-vocabulary `status` values → fix to the controlled set (`properties-and-tags.md`).
- **Stale actives:** `status: active` projects (or `in-progress` tasks) not modified in N days → ask to close or revive.
- **Inbox debt:** count of `needs-triage` items → offer a triage session.

Always **report findings and propose changes**; only bulk-edit after the user confirms.

## Context economy checklist (for Claude itself)

- Did I search/filter before reading? 
- Am I opening the minimum set of notes? 
- For repeat questions, did I suggest a Base instead of re-scanning? 
- Am I summarizing into the answer rather than pasting whole notes back?
