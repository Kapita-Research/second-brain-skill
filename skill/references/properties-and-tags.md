# Properties & Tags — the controlled vocabulary

This is the **schema backbone** of the vault. Consistent properties are what make a Markdown vault queryable instead of a pile of text. ## The rule: you may add, you may not redefine

📐 **A new property is free.** `died: 1998-04-02` on a person, `github: someone`, `venue:` on an event —
**write it and it exists.** Bases read frontmatter directly, so a new field is queryable the moment it
is written; a missing entry in `types.json` only means Obsidian shows it as plain text. **Nothing
breaks, and nobody needs permission.**

⛔ **Two things are forbidden, and both are the same mistake — taking a word that already means
something:**

| | |
|---|---|
| **Reusing a shared name for a new meaning** | `status: buried` on a person. **`status` carries the task lifecycle everywhere else**, so every board built on it now shows a dead relative |
| **Coining a synonym for something you already wrote** | `death_date` here and `died` there. **A base filtering one silently misses the other**, and nothing reports it |

> **The second is avoided by looking, not by obeying:** before inventing a field, **check what this vault
> already calls that thing.** Golden Rule 2 already says this for names — it holds for fields too.

### 🔴 Two fields point at an organisation, and they are not synonyms

**`company:` and `org:` both link to a `type: business` note. The difference is the *relationship*, not
the destination — the field name is carrying what kind of link it is.**

| | On | Means |
|---|---|---|
| **`company:`** | a **person**, a **group**, a **task** | **belongs to** — where someone works, whose group it is, whose work the task is |
| **`org:`** | an **engagement** | **the counterparty** — who the deal is *with* |

> **Someone employed by a company and a deal made with one are different facts.** Collapsing them into
> one field would lose that, and **the local dashboard already relies on the distinction** — it opens a
> tab per `company:` value found in tasks.

**This is what a relationship type looks like when it is cheap: the field name carries it.**

**The values below are the shared vocabulary — the fields that carry meaning *across* notes.** ⛔ **Their
names and their values must stay identical everywhere**, because `status: active` does not match
`Active` and the row vanishes with no error. **Everything else is yours to invent.**

### 🔴 Invent a type, and record it in the same breath

**A new *field* needs nothing — write it and it exists.** A new **`type:`** is different, because
`validate_vault.py` checks `type` against a fixed list and an unknown one is an **error**, not a warning:

```
ERRORS: 12
  - Data Engineering 101.md: off-vocabulary type `lecture`
```

> ⛔ **Those twelve notes were written correctly.** The tool simply does not know a word this skill
> told you to invent — **and nothing anywhere records that you invented it.**

**So inventing a type is two actions, never one:**

1. **Write the note.** `type: lecture` — no permission, no migration, as always.
2. **Add the word to the vault's `CLAUDE.md`**, on one line:

```
extra-types: lecture, workshop
extra-statuses: awaiting-client
```

**Same for a new `status:` value**, which is checked the same way. **Ordinary fields need no entry —
only these two lists are validated against a fixed vocabulary.**

**The vault then carries its own vocabulary**, so the health check reads it instead of asking anyone to
remember it — see *Vault validation* in `references/cli-and-automation.md`.

## Frontmatter property types (Obsidian)

Properties live in YAML frontmatter at the very top of a note:

```yaml
---
title: My Note
type: project
domain: work
status: active
created: 2026-06-16
due: 2026-07-01
tags:
  - work/project
related:
  - "[[Other Note]]"
---
```

| Type | Example | Notes |
|---|---|---|
| Text | `title: My Note` | |
| Number | `priority: 2` | |
| Checkbox | `archived: false` | true/false |
| Date | `created: 2026-06-16` | `YYYY-MM-DD` |
| Date & time | `start: 2026-07-01T14:30:00` | an exact moment |
| List | `tags: [a, b]` or YAML block list | |
| Link | `related: "[[Note]]"` | wrap wikilinks in quotes in YAML |

Default Obsidian properties with special behavior: `tags`, `aliases` (alt names for link suggestions), `cssclasses`.

> **Dates vs. date+time for tasks.** Keep `due` a plain **Date** (`YYYY-MM-DD`) — it's shared with projects — and put the time in a separate `due_time` (`HH:mm`, 24-hour) only when a task needs one. Obsidian assigns one type per property name vault-wide, so this lets date-only and timed tasks coexist without forcing a clock onto every task.

## Property types — `.obsidian/types.json`

**Obsidian assigns one type per property *name*, vault-wide** (official docs: "Once a property type is assigned to a property name, all properties with that name across your vault will use the same type"). It's stored in `.obsidian/types.json` as `{"types": {"<name>": "<id>"}}`. The six UI types map to five ids plus two specials:

| UI | id | Used for |
|---|---|---|
| Text | `text` | single values, including a single `"[[wikilink]]"` |
| List | `multitext` | any multi-value property |
| Number | `number` | real arithmetic values |
| Checkbox | `checkbox` | booleans |
| Date | `date` | `YYYY-MM-DD` |
| Date & time | `datetime` | timestamps |
| — | `aliases` / `tags` | the two built-ins; always these ids, never `multitext` |

The skill's assignment ships as `assets/types.json` (bootstrap installs it). Rules worth knowing:

- **A property that is a list *anywhere* must be `multitext` everywhere** — a list value in a `text` property shows a type mismatch. `author` is `multitext` for exactly this reason (multi-author books and papers are normal), so a lone author is still written as a one-item list. Consequence for Bases: query it with `author.contains(this)`, **not** `author == this` — the `== this` form is for single-link properties like `book`, `source`, `fund`, `org`, `manager`.
- **`due_time` is `text`, never a date type.** Obsidian has no time-only type; `HH:mm` in a `date`/`datetime` property is corrupted on edit.
- **`pages` is `text`**, because it holds ranges (`45–72`). Only make it `number` in a vault where it means total page count.
- **Leave a property undeclared when a tool writes it as a scalar but a few notes need a list.** Undeclared properties are inferred per note, so neither form is flagged. (Worked example: `company` — the dashboard server's field writer refuses YAML lists, but dual-role people legitimately carry two companies. Declaring it `multitext` would make Obsidian rewrite scalars as lists and break that writer; declaring `text` would flag the dual-role notes. Omitting it satisfies both.)
- Editing `types.json` by hand needs an Obsidian reload; setting a type from the property panel writes the file for you.

## Canonical properties (use on every note)

| Property | Required | Values |
|---|---|---|
| `type` | ✅ | one of the controlled `type` values below |
| `domain` | ✅ | `work` \| `personal` \| `shared` |
| `created` | ✅ | `YYYY-MM-DD` |
| `status` | projects, tasks, reading, captures, engagements, transactions | see status values below (orgs, funds, research use `active`/`archived`) |
| `tags` | recommended | from the tag taxonomy below |
| `aliases` | optional | alternative names |
| `due` | optional | `YYYY-MM-DD` (projects, tasks) |
| `due_time` | optional | `HH:mm` 24-hour — pair with `due` on a task when a specific time matters |
| `priority` | optional | tasks: `high` \| `normal` \| `low` |
| `recurrence` | optional | tasks: `daily` \| `weekly` \| `monthly` \| `quarterly` \| `yearly` — completion advances `due` (see *Task lifecycle*, `retrieval-and-review.md`) |
| `assignee` | tasks | list of `"[[Person]]"`/`"[[Org]]"` links — who is **responsible** for doing the task; defaults to the vault owner; multiple allowed |
| `projects` | optional | list of `"[[Project]]"` links (tasks) |
| `people` | optional | list of `"[[Person]]"` links |
| `parent-task` | optional | `"[[Task]]"` — the parent of a subtask |
| `blocked-by` | optional | list of `"[[Task]]"` links that must finish first (tasks) |
| `related` | optional | list of `"[[wikilinks]]"` |
| `source` / `url` | source/book notes, tasks, concepts | origin of the material / where a task came from / the note or book an idea sprang from. (The *property* `source:` and the note *type* `source` coexist: the type names the note, the property names the origin.) |
| `book` | chapters | `"[[Book]]"` — the parent book; **required** on every `type: chapter` note |
| `chapter` | chapters | number — chapter ordering (filenames carry `Ch01`/`Ch02` prefixes so name-sort works too) |
| `rating` | books | `1`–`5`, set when finished |
| `company` | optional | `"[[Company]]"` link (person, group) |
| `job_title` / `department` | optional | text (person) |
| `manager` | optional | `"[[Person]]"` link (person) |
| `email` / `phone` | optional | text (person) |
| `location` | optional | text — office, city, or remote (person) |
| `contact` | optional | person: `active` (or omit) \| `dormant` \| `none` — do you actually deal with them? See *Contact standing* below |
| `last-contact` | optional | `YYYY-MM-DD` — set when filing an interaction with this person (meaningless for `dormant`/`none`) |
| `groups` | optional | list of `"[[Group]]"` links (person) |
| `members` | groups | list of `"[[Person]]"` links (group) |
| `relationship` | optional | org relationship — `client`, `partner`, `investor`, `vendor`, `prospect`, `competitor`… (free text; stay consistent) |
| `org` | engagements | `"[[Organization]]"` the deal is with (a person note for private individuals). Note: people link orgs via `company`, engagements via `org` — two names, same idea, each reads naturally in context |
| `value` | optional | engagement value (`"30k USD"`, a number, …) |
| `owner` | optional | `"[[Person]]"` driving it on our side (engagements) · `"[[Org/Person]]"` whose money it is (funds) |
| `custodian` | funds | `"[[Person]]"` physically holding the money |
| `amount` / `currency` | transactions | positive number + currency code (`USD`, `IQD`, …) — one currency per transaction, never auto-convert |
| `direction` | transactions | `in` \| `out` |
| `txn` | transactions | `donation` \| `expense` \| `transfer` \| `repayment` \| `pledge` \| `other` |
| `fund` | transactions | `"[[Fund note]]"` the money moved through |
| `initiative` | transactions | `"[[Project/Area/Engagement]]"` earmark, or `general` |
| `counterparty` | transactions | `"[[Person/Org]]"` on the other side — omit for anonymous |

> **`assignee` ≠ `owner` ≠ `people`.** `assignee` = who is responsible for doing a task; `people` = everyone involved/mentioned; `owner` = who drives an engagement / whose money a fund is. Three properties, three meanings — never merge them.

### 🔴 Adding is free. Shadowing and near-duplicating are not

**A new property is welcome when it carries a meaning none of the declared ones carries.** *That is why
`assignee`, `owner` and `people` exist as three names: three real distinctions, and merging them would
lose information.*

⛔ **What fails is a new name used *instead of* an existing one.** *A training note that records who
was there in `attendees` and leaves `people` empty has not added a field, it has hidden itself:* **every
search that asks by `people` now misses it, and nobody will know why.** **Fill the declared property,
and let the new one narrow it.**

> ### And before adding a value to a controlled vocabulary, read the values that are already in it.
>
> ⛔ **If one of them means the same thing in different words, use it.** *`planned` and `planning` are
> not two states; they are one state and a typo with a longer life.* **A board grouped by `status` shows
> them as two columns, with half the work in each, and nothing anywhere says they are the same.**
>
> ⚠️ **Registering the new value in the vault's `CLAUDE.md` makes it legal, not correct** - and it
> silences the validator, which was the one thing that would have told you.

**The test is not "is this new?" - adding a `type` or a property is ordinary.** The test is: ⛔ **would a
reader looking at both be able to say why this is not that?** *If not, there is one of them, and it
already exists.*

## Controlled `type` values

Every note declares exactly one:

| `type` | Lives in | Meaning |
|---|---|---|
| `fleeting` | `Inbox/` | unprocessed capture; transient — becomes another type at triage |
| `daily` | `Daily/` | a daily note |
| `weekly` | `Daily/` | weekly review note |
| `journal` | `Personal/Journal/` | personal reflection |
| `project` | `Work/Projects/` or `Personal/Projects/` | effort with an end state |
| `area` | `Work/Areas/` or `Personal/Areas/` | ongoing responsibility |
| `business` | `Work/Business/` | an **organization** you deal with — client, partner, investor, vendor, NGO (the entity, not the deal) |
| `government` | `Work/Business/` | a government/regulatory body — ministry, commission, regulator (same schema as `business`) |
| `engagement` | `Work/Business/` | one deal/opportunity with an org — its stage lives in `status:` |
| `fund` | `Money/` | a wallet/account/pot of money — `owner:` (whose it is), `custodian:` (who holds it) |
| `transaction` | `Money/Transactions/` | one money event — see `money.md` for the four direction+status meanings |
| `meeting` | `Work/Meetings/` | meeting notes |
| `task` | `Tasks/` | a single actionable to-do (status, optional deadline, links) |
| `person` | `People/` | a person |
| `group` | `People/` | a named set of people — team, committee, volunteer cohort, client circle (`members:`) |
| `source` | `Resources/Sources/` | notes on a source you're consuming — external article/paper/video/clip **or** an internal brief/report (formerly `literature`) |
| `book` | `Resources/Books/<Title>/` | a book — the shelf entry; one folder per book, chapters beside it |
| `chapter` | `Resources/Books/<Title>/` | one chapter of a book — always carries `book:` (required) |
| `research` | `Resources/Research/` | a research topic/deep dive |
| `concept` | `Resources/Notes/` | atomic/permanent idea (one idea) |
| `moc` | `Maps/` | Map of Content (hub) |

> **`fleeting` is the one transient type.** A quick capture may carry only `type: fleeting`, `domain`, `created`, and `status: needs-triage` until triage promotes it to a permanent type. Every other note uses its full schema. This is why `type` can always be present (rule: never omit it) without slowing down capture.

## Controlled `status` values

**Projects:** `idea` → `planning` → `active` → `on-hold` → `done` → `archived`
**Tasks:** `not-started` → `in-progress` → `in-review` → `done` (plus `on-hold`, `cancelled`, `delegated-out`). `in-review` = the assignee has delivered and is waiting on someone else's review or feedback — it goes back to `in-progress` if changes are asked for, or forward to `done` when approved. Distinct from `on-hold`, where nobody is working and nobody owes an answer. `delegated-out` = handed to someone else along with its supervision, so it is terminal *for the vault owner* — see *Task lifecycle* in `retrieval-and-review.md`
**Reading (source/book):** `to-read` → `reading` → `done` (chapters carry no status — the book tracks progress)
**Engagements (deals):** `lead` → `talking` → `proposal` → `active` → `done` (won) · plus `lost` and `on-hold`
**Transactions:** `settled` (closed) · `outstanding` (out = receivable owed to the fund's owner; in = pledge not yet received) · `cancelled` (void — excluded from all balance math)
**Organizations (incl. `government`), funds, research topics:** `active` → `archived` (research also allows `done`)
**Inbox:** `needs-triage`

Don't use freeform synonyms ("wip", "complete", "todo", "in progress"). Map them to a canonical value (e.g. for a task, "in progress" → `in-progress`; for a project, → `active`).

`status` is one shared vocabulary across every type — **never add person-standing values to it.** That is what `contact:` is for (below); keeping them apart is why a new person state can't loosen validation for projects, tasks, and deals at the same time.

## Contact standing — `contact:` (person notes)

A `People/` folder collects two populations that need opposite handling: people you **deal with**, and people you only **know about**. The CRM fields (`email`, `phone`, `last-contact`) and the *Conversations*/*Commitments* sections are meaningful only for the first. `contact:` records which — and nothing else:

| Value | Meaning | Effect |
|---|---|---|
| *omitted* (= `active`) | a live contact | the default; appears in the directory, gets follow-up sweeps |
| `dormant` | **was** a contact, isn't now — left the company, dead lead, finished engagement | stays in the directory and stays searchable; **excluded from `last-contact` follow-up sweeps** |
| `none` | never a contact and never will be — book/paper authors, historical figures, celebrities, executives you only cite or track | out of the working directory entirely |

Three rules that keep it from sprawling:

- **The test is your relationship, not their fame or their status.** A well-known CEO you actually report to is `active`. A minor historical figure is `none`. Deceased is not a value — that belongs in the note body.
- **Don't encode what another property already carries.** Work vs. personal is `domain`; which org, and whether that org is a client or a competitor, is `company:` plus the org note's own `relationship:`; team membership is `groups:`. Putting `client`/`partner`/`vendor` on a *person* denormalizes a fact that belongs to the **organization** and will drift.
- **One person is always one note.** When a `none` figure becomes a real contact, change the value — never create a second note. Personas and composite characters from research are **not** people: they belong in the research note or as `type: concept`.

**Querying it (important).** Filter with `not:` around an equality, never `!=`:

```yaml
- not:
    - 'contact == "none"'      # ✅ absent property → equality is false → note is included
# - 'contact != "none"'        # ❌ comparison against a missing value is undefined in the Bases docs
```
Because the default is *omitted*, most notes have no `contact:` at all — an `!=` filter that treats a missing value as non-matching would silently empty the directory. See `bases.md` → *People directory & groups*.

## Tag taxonomy

Tags complement properties; they're for cross-cutting facets and quick filtering. Keep topic/domain facets **nested and shallow** (2–3 levels); the bare type tag (below) is deliberately flat. Don't duplicate what a property already captures (e.g., don't add `#active` when `status: active` exists).

Top-level facets:

```
#work/…          #work/project  #work/client  #work/meeting
#personal/…      #personal/health  #personal/finance  #personal/journal
#topic/…         #topic/ai  #topic/marketing  #topic/productivity
(bare type tag)  the default the templates use: one flat tag mirroring the note's type (`daily`, `task`, `people`, `moc`, …) — useful for graph coloring. `#type/…` nesting is an optional alternative; pick **one** style per vault and record it in the vault `CLAUDE.md`
#status/…        (optional; prefer the status property)
```

Rules:
- Lowercase, hyphenate multi-word tags (`#topic/machine-learning`).
- Tags may contain letters, numbers (not first char), `_`, `-`, and `/` for nesting.
- Prefer **properties for structured facts** (type, domain, status, dates) and **tags for themes** (`#topic/...`). This keeps Bases/Dataview queries clean.

## Why this matters (the consistency rule)

The single biggest failure mode of an AI-managed vault is **schema drift** — the same fact written three different ways across sessions, so nothing can be found or filtered later. Always:
- reuse the exact property names and values above,
- check an existing similar note for the established pattern before creating a new one,
- when the user introduces a new recurring concept, add it here deliberately rather than improvising.

A consistent schema is what lets `bases.md` and `retrieval-and-review.md` actually work.
