# Note Types — schemas & templates

Ready-to-use templates for every note type. Each uses the controlled vocabulary from `properties-and-tags.md`. Copy the template, fill it in, file it per the triage tree. Keep frontmatter consistent — that's what keeps the vault queryable. Put reusable copies in `Templates/`.

> **How to use these templates.** They use `{{placeholder}}` markers. By default just fill them in — Claude does this automatically when it creates a note, and `{{date:…}}`, `{{time:…}}`, and `{{title}}` also work as-is in Obsidian's **core Templates** plugin. Markers that require computation (e.g. *yesterday's* date, or a dropdown picker) are **Templater-only** — they're flagged inline and shown as `tp` calls in `community-plugins.md`. **Nothing here requires a community plugin:** without Templater, the dynamic values are simply filled by you or by Claude. One gotcha: the `- [[ ]]` lines below are fill-in placeholders — fill them or **delete** them; an empty `[[ ]]` renders as a literal broken link in Obsidian.

> **Use what fits.** Many professional vaults run entirely on tasks, meetings, people, groups, and projects. Daily notes, journaling, and book/source notes are **optional habits**, not requirements — offer them when the user's work would benefit, don't impose them.

> Ready-made copies of these templates ship in the skill's `assets/templates/` (with `.base` dashboards in `assets/bases/`) — `scripts/bootstrap_vault.py` installs them into a new vault.

> **Inline `- [ ]` vs. task notes — Golden Rule 7 (SKILL.md) governs every template here.** A meeting's `## Action items`, a project's `## Tasks`, a client's `## Next actions`, and a person's `## Commitments` all *point to* task notes (list them as `[[links]]` or embed a filtered Base) — they are **not** a place to park bare checkboxes. The one legitimate home for inline `- [ ]` is a task's own `## Steps`.

---

## Daily note — `Daily/YYYY-MM-DD.md`

```markdown
---
type: daily
domain: shared
created: {{date:YYYY-MM-DD}}
tags:
  - daily
---
# {{date:dddd, MMMM D, YYYY}}

## 🎯 Focus
<!-- Link the task note(s) you're advancing today, e.g. - [[Ship landing page]]. If today's focus isn't a trackable task, write it as a plain line — don't open a bare - [ ] here. -->
- [[ ]]

## 📝 Log


## 💭 Notes & captures


## 🔗 Linked
- Yesterday: [[YYYY-MM-DD]]   <!-- previous day's note: Claude/you fill the date. Templater: [[<% tp.date.now("YYYY-MM-DD", -1) %>]] -->
```

---

## Weekly review — `Daily/YYYY-[W]ww.md`

Weeklies live beside dailies so all periodic notes share one chronological folder; if the user prefers a separate `Reviews/` folder, adapt and record the choice in the vault `CLAUDE.md`.

```markdown
---
type: weekly
domain: shared
created: {{date:YYYY-MM-DD}}
tags:
  - weekly
---
# Week {{date:ww}}, {{date:YYYY}}

## ✅ Wins


## 📉 Misses / dropped


## 🧹 Task lifecycle sweep
<!-- Overdue: do / reschedule / cancel each. Stale in-progress + month-old not-started: ask. -->


## 🎯 Focus score
> What % of my time went to what I said mattered this week?

## ➡️ Next week — top 3
<!-- Link the task notes (or projects) they map to. Promote anything trackable to a task note. -->
- [[ ]]
- [[ ]]
- [[ ]]
```
(If daily notes exist, optionally add a "Dailies this week" section with a Base/Dataview list. Weeklies live in `Daily/` beside dailies; a vault without that folder can create it just for periodic notes — record the choice in the vault `CLAUDE.md`.)

---

## Journal — `Personal/Journal/` (optional habit)

```markdown
---
type: journal
domain: personal
created: {{date:YYYY-MM-DD}}
tags:
  - personal/journal
---
# {{date:YYYY-MM-DD}} — {{title}}

<!-- Private reflection. Sensitive by default (Golden Rule 11): never surfaced in work outputs. -->
```

---

## Project — `Work/Projects/` or `Personal/Projects/`

```markdown
---
type: project
domain: work        # or personal
status: active
created: {{date:YYYY-MM-DD}}
due: 
people: []
tags:
  - work/project    # or personal/project
---
# {{title}}

## Outcome
> One sentence: what "done" looks like.

## Why / context


## Tasks
<!-- This project's to-dos are task notes in Tasks/ (type: task; projects: [[this project]]; source: as relevant) — they roll up in Tasks.base and via this project's backlinks. List them here as links or embed a filtered Base; don't park bare `- [ ]` checkboxes here. -->
- [[ ]]

## Notes & decisions


## Links
- Area: [[ ]]
- MOC: [[ ]]
```

---

## Area — `Work/Areas/` or `Personal/Areas/`

```markdown
---
type: area
domain: work        # or personal
created: {{date:YYYY-MM-DD}}
tags:
  - work/area       # or personal/area
---
# {{title}}

## Standard / what "good" looks like


## Active projects
```
(List projects linked to this area — Base/Dataview or manual `[[links]]`.)
```

## Notes & references
```

---

## Organization — `Work/Business/` (`type: business`)

The **entity** — a client, partner, investor, vendor, NGO, or institution. Deals and opportunities with it are separate `type: engagement` notes (next section) that link back via `org:`. (The type keeps the historical name `business`.)

**Government bodies** — a ministry, commission, regulator, or other state institution — live in the same folder with the same schema but `type: government` (and typically `relationship: regulator | authority | licensor | client …`). They're a separate type so pipelines and org directories can include or exclude the state at a glance; statuses are the org pair `active | archived`.

```markdown
---
type: business
domain: work
status: active      # active | archived
created: {{date:YYYY-MM-DD}}
relationship:       # client | partner | investor | vendor | prospect | competitor … (free text; stay consistent)
sector: 
hq: 
website: 
parent:             # "[[Parent Org]]" if part of a group
aliases: []
people: []          # key people — "[[Person]]" links
tags:
  - work/org
---
# {{title}}

> One line: what they do and why they're in the vault.

## Snapshot
- **Relationship to us:** 
- **Key people:** [[ ]]

## Engagements
<!-- type: engagement notes with org: [[this note]] — list links or embed a filtered Base; the pipeline base aggregates all of them. -->
- [[ ]]

## History / notes


## Links
- MOC: [[ ]]
```

---

## Engagement / deal — `Work/Business/` (`type: engagement`)

One deal, opportunity, or paid ongoing relationship with an organization. The **stage lives in `status:`** — `lead → talking → proposal → active → done` (won), plus `lost` and `on-hold` — so the pipeline base can group by it. Name it after the deal, not the org (`Acme Support Retainer.md`; `Acme.md` is the org note).

```markdown
---
type: engagement
domain: work
status: lead        # lead | talking | proposal | active | on-hold | done | lost
created: {{date:YYYY-MM-DD}}
org:                # "[[Organization]]" it's with
value:              # expected/contracted value ("30k USD", a number, …)
owner:              # "[[Person]]" driving it on our side
people: []          # their side + anyone else involved
related: []
tags:
  - work/engagement
---
# {{title}}

> One line: what winning looks like.

## Current state
<!-- What the stage means right now; latest movement, dated. Update when status changes. -->

## History
<!-- Dated log — link meeting notes as they happen. -->

## Next actions
<!-- Task notes (Golden Rule 7): source: this note, people:/projects: as relevant. -->
- [[ ]]
```

When an engagement closes (`done`/`lost`), record the outcome in *Current state* — don't delete it; the org note and pipeline history stay queryable.

---

## Fund — `Money/Fund Name.md` (`type: fund`, optional module)

A wallet/account/pot. `owner:` is whose money it **is**; `custodian:` is who holds it — a donations pot can be owned by an NGO and custodied by you. Full semantics: `references/money.md`.

```markdown
---
type: fund
domain: work        # work | personal | shared
status: active      # active | archived
created: {{date:YYYY-MM-DD}}
owner:              # "[[Org or Person]]" whose money this is
custodian:          # "[[Person]]" holding it
currency: USD
tags:
  - fund
---
# {{title}}

> What this fund is for, in one line.

## Position
<!-- Balances live in the Ledger base (bases.md → Ledger); add a per-fund view filtered with file.hasLink("this fund"). State cash · receivables · pledges when reporting. -->

## Notes
```

---

## Transaction — `Money/Transactions/YYYY-MM-DD What — Counterparty.md` (`type: transaction`)

One money event. The four `direction`+`status` combinations (cash in · cash out · receivable · pledge) are defined in `references/money.md` — **restate the fund's position after every capture.**

```markdown
---
type: transaction
domain: work
status: settled     # settled | outstanding | cancelled (out+outstanding = owed back; in+outstanding = pledge; cancelled = void, excluded from balances)
created: {{date:YYYY-MM-DD}}
fund:               # "[[Fund]]"
amount:             # positive number
currency: USD
direction: in       # in | out
txn: donation       # donation | expense | transfer | repayment | pledge | other
counterparty:       # "[[Person/Org]]" — omit for anonymous (note it below)
initiative:         # "[[Project/Area/Engagement]]" earmark, or general
related: []         # e.g. the original transaction a repayment settles
tags:
  - transaction
---
# {{title}}

> One line: what happened.

## Notes
<!-- Context, receipt link, anonymous-donor note, partial-payment log. -->
```

---

## Meeting — `Work/Meetings/`

```markdown
---
type: meeting
domain: work
created: {{date:YYYY-MM-DD}}
people: []
tags:
  - work/meeting
related: []
---
# {{title}} — {{date:YYYY-MM-DD}}

**Attendees:** 
**Project:** [[ ]]

## Agenda


## Notes


## Decisions


## Action items
<!-- Promote each action item to its own task note in Tasks/ (status: not-started; source: [[this meeting]]; link the relevant people/projects). List the resulting task notes here as links — do not leave bare `- [ ]` checkboxes. -->
- [[ ]]
```

---

## Task — `Tasks/Short Imperative Title.md`

A single actionable to-do. Tracked tasks are **notes**, not inline checkboxes (Golden Rule 7), so one task can link several projects/people, carry a status and an optional deadline, relate to other tasks, and roll up in a Base. Statuses must then *move* — Golden Rule 8 and *Task lifecycle* in `retrieval-and-review.md`.

```markdown
---
type: task
status: not-started        # not-started | in-progress | in-review | done | on-hold | cancelled
domain: work               # work | personal | shared
priority:                  # high | normal | low (optional)
due:                       # YYYY-MM-DD (optional)
due_time:                  # HH:mm 24-hour — only when a specific time matters
recurrence:                # daily | weekly | monthly | quarterly | yearly (optional)
assignee: []               # ["[[Person or Org]]", ...] — who's responsible; defaults to the vault owner
projects: []               # ["[[Project]]", ...] — a task can serve several
people: []                 # ["[[Person]]", ...]
parent-task:               # "[[Parent Task]]" for a subtask
blocked-by: []             # ["[[Task]]", ...] that must finish first
related: []                # ["[[Task or Note]]", ...]
source:                    # "[[Meeting or note it came from]]"
created: {{date:YYYY-MM-DD}}
tags:
  - task
---
# {{title}}

> What "done" looks like, in one sentence.

## Steps
- [ ] 

## Notes


## Links
- Source: [[ ]]
- Projects: [[ ]]
- People: [[ ]]
```

Filenames are short imperative Title Case (`Send Acme MoU draft.md`). Status lives in the note, so the dashboard (`bases.md` → *Open tasks*) and a project/person's backlinks show it without duplicating the task.

**Capture from a meeting (the default, not a special case):** whenever a meeting has action items — whether the user says *"I had X meeting, here are N action points (due DAY at TIME),"* **or you extract them from the meeting notes yourself** — create one task note per item in `Tasks/`, set `due`/`due_time` when known, link `source:` to the meeting plus the relevant `people:`/`projects:`, and default `status: not-started` and `assignee:` to the vault owner (reassign when an item is clearly someone else's to do). Also update each attendee's `last-contact` (person note) to the meeting date. Do this by default, without being asked; don't stop at checkboxes in the meeting note. (Querying and displaying tasks: `retrieval-and-review.md` → *Tracking tasks & commitments*.)

---

## Person — `People/Full Name.md`

All fields beyond the required three are **optional** — fill what you know, extend later. `aliases` is load-bearing: every name variant you encounter goes there (dictation dedup depends on it).

```markdown
---
type: person
domain: work        # work | personal | shared
created: {{date:YYYY-MM-DD}}
aliases: []          # every spelling/nickname you meet — entity resolution depends on these
company:             # "[[Company]]"
job_title: 
department: 
manager:             # "[[Person]]"
email: 
phone: 
location:            # office, city, or remote
last-contact:        # YYYY-MM-DD — update when you log an interaction
groups: []           # ["[[Group]]", ...] — teams/cohorts (mirrored by the group's members:)
tags:
  - people
---
# {{title}}

## About
- Role / relationship: 

## Working style / notes


## Relationship & considerations
<!-- The memory a good colleague keeps: favors done for us ("helped us jump the vendor queue, Jun 2025"), favors we owe, sensitivities, open issues, things to keep in mind. Keep it factual and fair — never write what you couldn't stand behind if the person read it. Private-life matters belong in domain: personal notes or the journal, not here. -->


## Conversations
```
(Reverse-chronological log, or links to meeting notes that reference this person. Update `last-contact` as entries are added.)
```

## Commitments
<!-- Both directions, as task notes in Tasks/ (people: [[this person]]): what you owe them, and what you're waiting on from them (put "Waiting on…" in the task title). That's what makes "what did I tell them I'd do?" and "what am I owed?" answerable from Tasks.base. List them here as links — don't leave bare `- [ ]` checkboxes. -->
- [[ ]]
```

---

## Group — `People/Group Name.md`

A named set of people: a team, committee, volunteer cohort, or client circle. The group note is the roster hub; each member's note points back via `groups:`, so membership is queryable from **both** directions (a Base filters members with `file.hasLink("Group Name")` — see `bases.md`).

```markdown
---
type: group
domain: work        # work | personal | shared
created: {{date:YYYY-MM-DD}}
company:            # "[[Company]]" if the group belongs to one
members:
  - "[[ ]]"
tags:
  - group
---
# {{title}}

> What this group is for, in one line.

## Members
<!-- Human-readable mirror of members:, one line per person with role, e.g. - [[Sarah Chen]] — Ops Manager. The frontmatter members: list is the authoritative one. -->
- [[ ]]

## Notes
<!-- Cadence, rituals, shared context. Open work rolls up via Tasks.base and the members' backlinks. -->
```

When membership changes, update **both** the group's `members:` and the person's `groups:`.

---

## Source — `Resources/Sources/`

Notes on any material you're consuming or annotating — an external article, paper, video, or web clip, **or an internal brief/report/roadmap you didn't author as a note**. (Renamed from `literature` in 2.9.0: real vaults fill this folder with project briefs as much as papers, and none of it is "literature.") `author:` is a wikilink when the person has (or deserves) a note; plain text otherwise.

```markdown
---
type: source
domain: shared
status: to-read     # to-read | reading | done
created: {{date:YYYY-MM-DD}}
source:             # origin — file, publication, site
url: 
author:             # "[[Person]]" or plain text
aliases: []
tags:
  - topic/
---
# {{title}}

> Source: [{{author}}]({{url}})

## Summary (my words)


## Key points / quotes


## How it connects
- Related: [[ ]]
- Ideas spawned: [[ ]]
```

---

## Book — `Resources/Books/<Title>/<Title>.md`

**One folder per book.** The book note sits inside its own folder with the same name; chapter notes (next section) sit beside it. Three layers, only two of them nested:

- **Book note** (`type: book`) — the shelf entry. Stays *thin*: metadata, reading status (`to-read → reading → done`), a dated reading log, and two live views that assemble the rest. No long prose here.
- **Chapter notes** (`type: chapter`, in the same folder) — what the book *says*, faithful to the author.
- **Idea notes** (`type: concept`, in `Resources/Notes/` — **never** inside the book folder) — what *you* think, one idea per note, back-pointing with `source: "[[Title]]"`. Ideas stay outside deliberately: an idea a book sparks is often about your project, not the book, and must be linkable from anywhere. Anything actionable additionally becomes a task note (Golden Rule 7).

`author:` is a **list of wikilinks** — authors get person notes (routing branch 4), so the book shows up on the author's backlinks. The two inline `base` code blocks use the `this` keyword (the embedding note — see `bases.md` → *Embedding & `this`*), so chapters and ideas list themselves; no hand-maintained bullet lists to go stale.

````markdown
---
type: book
domain: shared
status: to-read     # to-read | reading | done
created: {{date:YYYY-MM-DD}}
author:
  - "[[Author Name]]"
year: 
rating:             # 1–5, set when finished
source:             # edition / file / store link, if any
aliases: []
tags:
  - topic/
---
# {{title}}

> One-line takeaway — fill it when it crystallizes.

## Reading log
- {{date:YYYY-MM-DD}} — added to the shelf.

## Chapters
```base
filters:
  and:
    - 'type == "chapter"'
    - 'book == this'
views:
  - type: table
    name: "Chapters"
    order:
      - file.name
      - chapter
```

## Ideas sparked
```base
filters:
  and:
    - 'type == "concept"'
    - 'source == this'
views:
  - type: table
    name: "Ideas"
    order:
      - file.name
      - created
```

## Related
- [[ ]]
````

---

## Chapter — `Resources/Books/<Title>/` (`type: chapter`)

One note per chapter (or per reading session — whatever the book's rhythm is), named `<Title> — Ch01 <Chapter name>.md` so the `NN` prefix keeps them sorted. **`book:` is required** (the validator errors without it). A chapter holds what the book says — summary in your words, quotes with page numbers, questions it raised. Your own thinking does **not** live here: distill it into `Resources/Notes/` concepts with `source: "[[the book]]"`, and they'll appear in the book's *Ideas sparked* view on their own.

```markdown
---
type: chapter
domain: shared
created: {{date:YYYY-MM-DD}}
book: "[[Book Title]]"   # required — the parent book
chapter:                 # number
pages: 
aliases: []              # "the pricing chapter" — dictation resolves against these
tags:
  - topic/
---
# {{title}}

## Summary (my words)


## Quotes / passages
<!-- with page numbers -->


## Questions raised


## Ideas spawned
<!-- distilled to Resources/Notes/ as type: concept, source: the book — link them here if you like -->
```

---

## Research topic — `Resources/Research/`

```markdown
---
type: research
domain: shared
status: active
created: {{date:YYYY-MM-DD}}
tags:
  - topic/
---
# {{title}}

## Question / scope


## What I know so far


## Open questions
- 

## Sources
- [[ ]]

## MOC
- [[Maps/{{title}}]]
```

---

## Concept / atomic note — `Resources/Notes/`

One idea, in your own words, independently linkable. Optionally prefix the filename with a timestamp ID (Zettelkasten style): `202606161045 Idea title.md`.

```markdown
---
type: concept
domain: shared
created: {{date:YYYY-MM-DD}}
tags:
  - topic/
---
# {{title}}

> The single idea, stated plainly in one or two sentences.

Elaboration, reasoning, example.

## Connects to
- [[ ]]   <!-- link to at least one other note or MOC -->
```

---

## MOC — `Maps/Name.md`

A hub: links + light commentary, not primary content. Make one when a cluster of notes grows around a theme. **Dynamic listings (open tasks, rosters, active projects) must be Base embeds — `![[Tasks.base]]` — never hand-maintained link lists, which go stale within days.** Hand-curate only the stable core links.

```markdown
---
type: moc
domain: shared
created: {{date:YYYY-MM-DD}}
tags:
  - moc
---
# 🗺️ {{title}}

> What this map covers.

## Core notes
- [[ ]]

## Sub-topics
- [[ ]]

## Recently updated
```
(Optional Base/Dataview list of notes tagged with this topic, sorted by modified date.)
```

## Related maps
- [[Maps/Home]]
```

---

## Inbox capture (fast)

When capturing, don't reach for a full template — speed matters. Minimum viable note:

```markdown
---
type: fleeting
domain: shared
created: {{date:YYYY-MM-DD}}
status: needs-triage
---
{{the raw thought, link, or quote}}
```

`type: fleeting` keeps the schema valid without slowing capture; triage later promotes it to a permanent type (`concept`, `meeting`, `source`, …) and fills the rest of the frontmatter.

Process it later during triage (see `capture-and-web.md`).
