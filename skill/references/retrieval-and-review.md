# Retrieval & Review

How to **find** things without burning context, and how to run the **review** rituals that make a second brain "think back." This is where context economy lives — the discipline that keeps the vault fast and cheap as it grows past hundreds of notes.

## The retrieval ladder (cheapest first)

> ## ⛔ Before the ladder: who is going to read what you write?
>
> **If it is anyone but the owner — a deliverable, a handover, a review, an email, a summary someone
> else receives — then `Judgements/` and `type: judgement` are excluded from every rung below.**
> **Not read and set aside. *Not read.*** *A judgement you have read has already changed what you would
> write, and no rule can un-read it.* Full rule: `references/note-types.md` → *Judgement*.

Never load the whole vault. Climb only as far as you need:

0. **Translate the query into the vault's own language first, then expand it.** ⛔ **This vault's filenames are English by rule and most of its prose is too, so an Arabic query is searching for something that by construction is not there.** Turn every content word into the English a note would actually use — *أقساط* → `fees` / `tuition`, *مدارس أهلية* → `private schools` — **and if the question names a person, an organisation or a project, search every form of that name you can think of.** `aliases` lists are a supplement, never the source. See *Expanding a query* below.
1. **Name match** — guess the note title / use Quick Switcher logic. If you know the file, open just that file.
   - **No name in the question? Ask first — there is no shame in it.** *"Do you mean Uruk the client, or the Uruk study?"* · *"Which pricing — ours, or the market's?"* **One question, in one line, when two readings would send you to different parts of the vault.** It costs a sentence; guessing wrong costs a wide search, a weak answer, and some of the owner's trust.
   - ⛔ **But asking must never block.** **One question, not a questionnaire** — and if the answer is *"no names, just look"*, or no answer comes, **go and search with what you have.** Say what you assumed, and correct course after. **The rungs below work fine without a name; they are simply less direct.**
   - **Still no name, and searching anyway?** If it is *topical* — *"what did we learn about pricing"* — **open the topic's MOC in `Maps/` first.** A MOC is a hub someone curated by hand; it often answers directly, and when it doesn't it hands you the right five notes. **A topical question with no MOC is worth one: offer to create it from whatever the search does find.**
   - **Scoped to a time?** — *"last month's meetings"*, *"what closed this week"* — **filter on `created`, `due` or the `Daily/` filenames.** Dates are exact, cheap and never ambiguous; **falling through to text search for a question that was really about a date is pure waste.**
2. **Metadata filter** — filter by `type`, `domain`, `status`, `tags` (via a Base, or `grep` on frontmatter). Narrow to a candidate set.
3. **Keyword search** — full-text search / `grep` for terms across the candidate set.
4. **Open the few** — read the handful of notes that matched, not the folder.
5. **Synthesize** — answer from those notes; cite them as `[[wikilinks]]`.

> Rule of thumb: if you're about to read more than ~5–10 notes to answer something, stop and narrow with a filter or a Base instead.

### Expanding a query — required for any non-Latin script

**`grep` is literal, and note bodies are raw prose you cannot normalise. So widen the query instead — and you are the one who widens it.**

#### First: the language, not just the spelling

🔴 **The vault's naming rule puts filenames in English. Its notes are written in English. So a question asked in Arabic will match almost nothing — and that is a property of the vault, not a fact about its contents.**

**Translate every content word before searching — topic, thing, place, field — not only names:**

| Asked | Searched |
|---|---|
| *أقساط المدارس الأهلية ببغداد* | `school` · `tuition` · `fees` · `private schools` · `Baghdad` |
| *أسعار الإيجار* | `rent` · `rental` · `housing` · `price` |
| *اجتماع الفريق* | `meeting` · `team` · `standup` · `sync` |

**Search the broadest single English word before the exact phrase.** *`school` finds a project, five findings and a task; `أقساط المدارس الأهلية` finds nothing, and both are the same question.*

#### ⛔ And "there is nothing in the vault" is a claim, held to the same standard as an answer

**A wrong "we do not have this" is the most expensive failure this skill has**, because it does not look like a failure. **The owner does not go and check; they act on it.** *Building a scraper for data a recorded finding says is not published — when the recorded decision was to telephone instead — costs a day and looks like helpfulness the whole time.*

**So before saying it, you must have searched in English.** And when you say it, **say what you searched:**

> ✅ *"I searched for `school`, `tuition`, `fees` and `private` across titles and full text and found nothing."*
> ❌ *"There is nothing in the vault about this."*


**You already know that `عصام` is `Essam`, that `آيه` is `آية`, that `Hussain` is `Hussein`. Use that.** ⛔ **Do not wait to find a variant in an `aliases` list before trying it** — the list is what a *machine* consults; you generate the forms yourself and are better at it than any list will be.

**So before step 1:**

1. **Work out who is meant** — from the question, the vault's people, and the conversation.
2. **Search for every plausible form of that name**, generated by you: both scripts, common transliterations, with and without the definite article, surname alone if it is distinctive.
3. **Check `aliases` too** — it may hold a spelling you would not have guessed, such as a nickname or a former name.
4. **Ambiguous → ask which one.** Two people sharing a first name is a fact about the world, not a spelling problem, and it is the one case reasoning cannot settle alone.

> 🔴 **`grep` is literal, and an Arabic word written two ordinary ways does not match itself.** **A single-form search returning nothing is not evidence of absence** — it is evidence that one spelling was not present.

**This is why *say what you searched* matters mechanically, not just politely:** *"I searched titles, aliases and full text for `عصام`, `عصام حسين` and `Essam Hussein` and found nothing"* is a real answer. **"I found nothing" is not.**

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

- **Bases CAN query task notes.** Because a task is a note with frontmatter (`status`, `due`, `due_time`, `priority`, `projects`, `people`, `assignee`, …), a `.base` aggregates them natively — see the ready-made **Open tasks** dashboard in `bases.md`. That's the answer to "what are my open tasks" — but mind *how* you read it. A `.base` file contains the **query, not the rows**: opening it tells you the filters, never the answer. Where Obsidian is running, `obsidian base:query file="Tasks.base" view="Open — by status" format=csv` returns the computed rows (see `cli-and-automation.md` → *Querying bases*); otherwise filter `type == "task"` by `status`/`due` with the file tools. Either way, don't grep checkboxes.
- **Stray-checkbox sweep.** To find action items not yet promoted (in any note type), search `grep -rn "^[[:space:]]*- \[ \] " --include="*.md" .` (or the `line:("- [ ] ")` operator in Obsidian) and offer to promote each hit to a task note. **Skip hits inside a task note that is already `done`, `cancelled` or `delegated-out`** — its unticked steps are a record of what was outstanding when it closed or was handed over, not new work for the owner. Promoting them re-imports work the owner deliberately gave away.
- **Relationships.** `parent-task:` for subtasks, `blocked-by:` for dependencies, `related:` for siblings, `assignee:` for who is *responsible* for doing it (every new task defaults to the vault owner); tasks sharing a `projects:`/`people:` link surface together automatically. "What's on my plate" views can group or filter by `assignee` — the vault owner's own tasks are those assigned to them (an **On my plate** view filtered to `assignee` is the cleanest form; see `bases.md`). Things *others* owe *you* are tasks too — title them "Waiting on …" so both directions show up in the table.

  **Two ways to delegate, and they are not equivalent.** *Reassign* (`assignee:` → the other person, status unchanged) keeps the task fully live: it holds its `due`, still flags overdue, still appears in reviews — it just drops off an `assignee`-filtered *On my plate* view. *`delegated-out`* removes it from every open surface permanently. Reassigning is the **lossless default**; reach for `delegated-out` only when the owner has genuinely stopped supervising the outcome. Offer the reassign route first when it isn't clear which the owner means.

### Task lifecycle — keeping statuses honest

`not-started → in-progress → in-review → done` (plus `on-hold`, `cancelled`, `delegated-out`). The system only works if statuses move (Golden Rule 8):

- **Update on evidence, immediately.** "I sent the proposal" / "we dropped that" — in any conversation, capture, or meeting — means set the task `done` / `cancelled` / `in-progress` / `delegated-out` in the same session, add a one-line dated note in the task body, and confirm what changed.
- **`in-review` is the handoff state.** The assignee has delivered the work and is waiting on someone else — a reviewer, a manager, a client — to approve it or ask for changes. "I sent it to X for review" / "waiting on their feedback" sets `in-review`; it then goes **back to `in-progress`** if changes are requested, or **forward to `done`** when approved. It is *not* `on-hold` (nobody working, nobody owes an answer) and not `done` (nothing is finished until someone says so). Because someone owes a reply, `in-review` tasks are the first thing to chase in a review — name the reviewer and how long it's been sitting.
- **`delegated-out` is the handover state — and it is terminal for the owner.** Use it when the owner gives away both the work *and* its supervision: someone else now owns the outcome and nobody expects the owner to chase it. Treat it like `done`/`cancelled` in every display — excluded from open views and from the open count, never flagged overdue, hidden by default.
  - **The test is supervision, not who does the work.** If the owner delegated the doing but still has to follow up, that is `in-progress`/`in-review` with the other person as `assignee:`. Using `delegated-out` there is how an accountable task silently disappears.
  - **Ask before applying it; never infer it.** "I handed it to X", "X is taking it from here", "it's with them now" do **not** settle the question — they describe who is doing the work, not who reports the outcome. Put the question to the owner: *"Do you still need to know whether that lands, or is it off you completely?"* Still needs to know → keep it open and reassign. Off completely → `delegated-out`. This is a one-way door in practice (the task leaves every list the owner reads), so it gets a confirmation, in the spirit of Golden Rule 10.
  - **On the transition:** set the new owner as `assignee:` (required — a delegated-out task with no assignee is a record of nothing), keep the note in `Tasks/`, and log a dated handover line naming who took it. Leave `due`/`due_time` as they are: the date is now the delegate's, it stops driving overdue for the owner, and keeping it preserves what was promised. Clear `recurrence:` (or hand the recurring task over as a fresh note) — a repeat cannot advance on a terminal status, so leaving it set silently ends the series.
  - **Check the dependents before closing.** If any open task lists this one in `blocked-by:`, or it is a `parent-task:` of open subtasks, say so: the owner is about to stop watching something another of their own tasks waits on. Reassign instead, or record who now unblocks it.
  - **Reversing it** (the handover fell through): set `in-progress` — or `not-started` if nothing has happened — put `assignee:` back to the owner, log a second dated line saying it came back and why, and reset `due` to something real rather than letting the old date snap straight to overdue.
  - **What the *Delegated out* view is, honestly:** a place to look on demand, not a queue anyone is told to work. By design, **no review ritual raises delegated-out tasks** — that silence is the point of the status. What guards the record instead is `validate_vault.py`, which warns when a delegated-out task has no `assignee:` or still carries a live `recurrence:`. Neither warning asks the owner to chase the delegate.
  - Not every vault needs this state — offer it when the owner describes fully handing tasks off, rather than assuming it. A vault that would rather keep handovers visible should reassign and use an *On my plate* view instead (above).
- **Overdue is a decision, not wallpaper.** Overdue items lead every task display; each one gets a choice — do it, reschedule `due`, or consciously `cancelled` — never silent carry-over. An `in-review` task past its due date still counts as overdue: the work isn't accepted yet.
- **Stale check (reviews).** List `in-progress` untouched ~2 weeks, `in-review` sitting more than ~1 week (chase the reviewer), and `not-started` older than a month; ask the user, don't assume.
- **Never delete or auto-archive.** Done/cancelled/delegated-out tasks stay in `Tasks/` (the *Done & cancelled* and *Delegated out* views hide them from open lists). An `Archive/` sweep of long-*done* tasks may be *offered* in a monthly review — explicit confirmation only; their `source:`/`projects:` links are useful history. **Delegated-out tasks are not archive fodder:** the work may still be live in someone else's hands, and `Archive/` is for the inactive. Leave them in `Tasks/`.
- **Recurring tasks** — `recurrence: daily | weekly | monthly | quarterly | yearly`. On completion, **don't** mark `done`: log the completion date in the body and advance `due` to the next occurrence (default — keeps `Tasks/` tidy). If per-occurrence history matters, spawn a dated copy instead (`Send weekly report 2026-07-10.md`) and mark *that* one done.

When asked "what are my open tasks" / "what's on my plate," default to reading every `type: task` note where `status` is not `done`/`cancelled`/`delegated-out` (or `Tasks.base`) and **presenting them as a Markdown table in chat** with columns `# | Task | Priority | Due | Thread`:

- **Sort** by priority (`high` → `normal` → `low`), then `due` (dated before undated, earliest first), then alphabetical — highest-leverage first.
- **Sourcing it from a base:** the view must actually carry `priority` in its `order:`, and not every view does — check, rather than assuming from the view's name. `Open — by status` carries the full set. Query that (`cli-and-automation.md` → *Querying bases*), or read the notes; never silently drop a mandated column because the view you picked lacked it.
- **Task** = the note title. **Priority** = `High`/`Normal`/`Low` (`—` if unset). **Due** = `due` (append `due_time` when set; `—` if none). **Thread** = the line of work it belongs to — its `projects:` link, falling back to `source:` then `related:`, with the `[[ ]]` stripped. Add an optional **Assignee** column when tasks are assigned to anyone besides the vault owner.
- Exclude `done`/`cancelled`/`delegated-out`; **overdue rows lead and are flagged**. After the table, add a one-line read: total open, how many are high-priority, the nearest deadline, and the busiest thread. Then close the loop (Rule 8): ask about anything that looks moved or stale, and offer status updates, due dates/priorities, or — with confirmation — an archive sweep of long-done tasks.

(If the user prefers inline-checkbox tasks instead, the optional **Tasks**/Dataview plugins can aggregate those — see `community-plugins.md`.)

## Activity reporting — "what did I work on?"

A recurring, high-stakes question: performance reviews, self-appraisals, status updates to a manager, invoicing a client, a standup after leave. The owner is usually asking about a **window** ("the last 3 weeks", "since June", "this quarter").

**Rank the evidence — the vault holds four sources and they are not equally trustworthy:**

1. **Dated status bullets in task bodies** (`**Done 2026-08-10.**`, `**Submitted for review 2026-08-06.**`) — the strongest signal. They record *accomplishment*, written deliberately, and they are what Golden Rule 8 exists to produce. Lead with these.
2. **`created:` frontmatter** — reliable and owner-controlled. Shows what was *started* and is the backbone of the reconstruction.
3. **Git history**, if the vault has it (`version-history.md`) — the only complete record of *revisions*. One command answers the whole question.
4. **Filesystem mtime** — last resort, and flag it as such.

**Read mtime skeptically or you will report fiction.** It keeps only the latest touch; it is bumped by Obsidian property rewrites, dashboard writes, and the agent's own edits; and copies or moves destroy it. Two specific traps:

- **A block of files sharing a timestamp to the minute is one bulk operation, not N work sessions.** Twenty task notes all stamped `12:20` is a property migration. Say so; don't count them as activity.
- **Your own edits in this session are in the data.** Exclude them, or name them.

**Method:**

```bash
# created in the window (frontmatter — the reliable pass); handles spaces in filenames
find . -name '*.md' -not -path './.obsidian/*' -not -path './Templates/*' -print0 |
  while IFS= read -r -d '' f; do
    c=$(awk '/^---$/{n++; next} n==1 && /^created:/{sub(/^created: */,""); gsub(/"/,""); print; exit}' "$f")
    [[ -n "$c" && "$c" > "2026-07-22" ]] && echo "$c  $f"
  done | sort

# what actually got finished (task bodies)
grep -rhoE '\*\*(Done|Submitted for review|Started|Cancelled|On hold|Reopened|Delegated out) 2026-0[78]-[0-9]{2}' Tasks/ | sort | uniq -c
# ^ keep this alternation in step with TASK_LOG_LABEL in scripts/dashboard_server.py —
#   a label missing here drops that whole class of movement out of activity reports

# if git is enabled, this replaces the guesswork entirely
git log --since="3 weeks ago" --name-only --pretty=format:'%ad %s' --date=short
```

Templates carry literal `{{date:YYYY-MM-DD}}` in `created:` — filter them out rather than reporting them as notes.

**Present it as work, not as files.** Group by **initiative** — the client, project, or thread — never by folder; "39 notes in People/" tells the owner nothing they can say to a manager. For each strand: what was produced, what closed (with dates), what's still open. Then count what matters: tasks completed, tasks submitted for review, notes created. Close with what the vault *can't* see (below) so they don't over-trust the total.

**State the gaps plainly.** If `Daily/` is empty there is no narrative record of any day, only artifacts. Work done outside the vault — a deck, a meeting, a phone call — is invisible unless a note records it. And if the window predates the vault's git history, say that the reconstruction is inference, not a log. Offering to enable version history (`version-history.md`) is the natural follow-up, with the honest caveat that it fixes the *next* review, not this one.

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
- **People sweep:** run `scripts/sync_last_contact.py` first so the dates are current (`cli-and-automation.md`), then review contacts with an old `last-contact` → reconnect or mark `contact: dormant`. **Skip `dormant` and `none` people entirely** — a former colleague or a dead author is not a follow-up you're behind on, and leaving them in the list is what trains you to ignore it (`properties-and-tags.md` → *Contact standing*). A **blank** `last-contact` means no recorded interaction, not a neglected one: people you deal with by chat or in person generate no meeting note. Don't chase blanks; chase stale dates.
- Re-tag drift: check that `type`/`domain`/`status`/`contact` are still consistent (schema hygiene) — **run** `scripts/validate_vault.py` for the full sweep.

## Vault hygiene checks (run on request)

- **Orphans:** notes with no inbound/outbound links → link them or archive.
- **Schema drift:** notes missing `type`/`domain`, or using off-vocabulary `status`/`contact` values → fix to the controlled set (`properties-and-tags.md`).
- **Stale actives:** `status: active` projects (or `in-progress` tasks) not modified in N days → ask to close or revive.
- **Inbox debt:** count of `needs-triage` items → offer a triage session.

Always **report findings and propose changes**; only bulk-edit after the user confirms.

## Context economy checklist (for Claude itself)

- Did I search/filter before reading? 
- Am I opening the minimum set of notes? 
- For repeat questions, did I suggest a Base instead of re-scanning? 
- Am I summarizing into the answer rather than pasting whole notes back?
