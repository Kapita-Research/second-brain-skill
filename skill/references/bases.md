# Obsidian Bases (.base)

Bases is Obsidian's **native** database (core feature). A `.base` file is YAML that turns your notes into filtered, sorted, grouped table/card/list views using their frontmatter. This replaces most Dataview `TABLE`/`LIST` needs with zero plugins — ideal for the core-first vault.

**This syntax is verified against Obsidian's official Bases docs.** (A common third-party mistake is using `display:`, `taggedWith()`, or a bare-string `groupBy` — those are wrong. Use the forms below.)

> **Bases query notes and properties, not inline checkboxes.** A `.base` can't list `- [ ]` lines that live *inside* a note — it sees frontmatter and file metadata only. The fix is to model tracked tasks as **notes** (`type: task`), which a Base *can* aggregate — see the **Open tasks** base below and `retrieval-and-review.md` → *Tracking tasks & commitments*. (Inline `- [ ]` remain for quick sub-steps; to roll *those* up you'd need the Tasks/Dataview plugins.)

## File skeleton

```yaml
filters:            # optional: applies to ALL views
formulas:           # optional: computed properties
properties:         # optional: display names / config per property
summaries:          # optional: custom aggregations
views:              # one or more views
  - type: table     # table | cards | list | map
    name: "View"
    order: [ ... ]
```

## Filters

Either a single string, or an object with exactly one of `and` / `or` / `not` (nestable):

```yaml
filters:
  and:
    - 'status != "done"'
    - file.hasTag("project")
    - not:
        - file.inFolder("Archive")
```

> **A single condition still needs the wrapper.** Write `filters: 'status != "done"'` (a string) or wrap it in `and:` — **never** a bare top-level list (`filters:` then a `- '…'` item). Some Obsidian versions reject the bare-list form with *"filters may only have one of an `and`, `or`, or `not` keys."*

Useful filter functions & comparisons (these go inside the `and`/`or`/`not` lists above):

```text
file.hasTag("work", "client")      # true if any of these tags
file.hasLink("Some Note")          # links to that note
file.inFolder("Work/Projects")     # in folder (or subfolders)
file.ext == "md"
'status == "active"'   'priority > 2'   'due < now()'
```

Operators: `==  !=  >  <  >=  <=` and boolean `&&  ||  !`.

**Exclude `Templates/` from every view — this is not optional.** A template is a note with real frontmatter (`type: task`, `type: transaction`, …), so **Obsidian counts it as data**: a ledger reports the transaction template as a transaction, a pipeline shows the engagement template as a live deal, a task dashboard is off by one. Every filter block gets:

```yaml
    filters:
      and:
        - not:
            - file.inFolder("Templates")
        - type == "task"
```

It bites hardest where it is least visible — a view with a `due`-date or `status` filter often excludes the (undated, statusless) template by accident, so the leak shows up on the *unfiltered* views while the narrow ones look clean. Audit **every** block, not the one you happened to test. Same reasoning for `Archive/` and `Attachments/` where a view should ignore them.

## Properties (column display)

```yaml
properties:
  status:
    displayName: Status
  formula.days_left:
    displayName: "Days Left"
  file.mtime:
    displayName: "Modified"
```
(Display names are for views only; they aren't used in filters/formulas.)

## Formulas

```yaml
formulas:
  # arithmetic / strings
  label: 'if(done, "✅", "⏳")'
  # dates: subtracting dates yields a duration — take .days for a number
  days_left: 'if(due, (date(due) - today()).days, "")'
  age_days: '(now() - file.ctime).days'
```
Reference note props as `note.prop` or just `prop`; file props as `file.name`, `file.mtime`, etc.; other formulas as `formula.name`. Guard optional props with `if(prop, …, "")` so empty notes don't error.

Key functions: `date()`, `now()`, `today()`, `if()`, `link()`, `file()`, `duration()`, plus type methods like `string.contains()`, `list.contains()`, `number.round()`, `date.format("YYYY-MM-DD")`.

## Views

```yaml
views:
  - type: table
    name: "Active"
    limit: 50
    filters:
      and:
        - not:
            - file.inFolder("Templates")
        - 'status == "active"'
    groupBy:
      property: status        # groupBy is an OBJECT
      direction: ASC          # ASC | DESC
    order:                    # columns, in order
      - file.name
      - status
      - due
      - formula.days_left
    summaries:                # aggregate a column
      formula.days_left: Average
```
Default summaries include `Sum, Average, Min, Max, Median, Range, Earliest, Latest, Filled, Empty, Unique, Checked, Unchecked`.

Card view uses the same shape with `type: cards`; list view `type: list`; map view `type: map` (needs lat/long props + Map plugin).

## Embedding & `this`

A base renders inside a note two ways: embed a `.base` file with `![[Reading.base]]`, or write the same YAML inline in a ` ```base ` code block. In both cases the keyword **`this`** points at the **embedding note** (verified against the official Bases docs), and **link properties compare directly to files** — a filter like `book == this` matches every note whose `book:` wikilink resolves to the note the base is embedded in. That's what powers self-assembling views:

```yaml
# inline in a book note — lists that book's chapters, no hand-maintained list
filters:
  and:
    - not:
        - file.inFolder("Templates")
    - 'type == "chapter"'
    - 'book == this'
views:
  - type: table
    name: "Chapters"
    order: [file.name, chapter]
```

(In a standalone `.base` file opened directly, `this` is the base file itself — `this` filters belong in embeds.)

## Ready-made bases for this vault

Save each as a `.base` file (e.g., `Maps/Dashboards/Active Projects.base`) or embed in a note with `![[Active Projects.base]]`.

### Active projects (work + personal)
```yaml
formulas:
  days_left: 'if(due, (date(due) - today()).days, "")'
properties:
  formula.days_left:
    displayName: "Days Left"
  domain:
    displayName: Domain
views:
  - type: table
    name: "Active Projects"
    filters:
      and:
        - not:
            - file.inFolder("Templates")
        - 'type == "project"'
        - 'status == "active"'
    groupBy:
      property: domain
      direction: ASC
    order:
      - file.name
      - domain
      - due
      - formula.days_left
    summaries:
      formula.days_left: Average
```

### Open tasks (the task dashboard)
Tasks are notes (`type: task`), so a Base aggregates them natively. **`assets/bases/Tasks.base` is the authoritative copy** — it is what the bootstrap installs and what a vault actually runs. The listing below is a teaching version: its view set is **not** a subset of the asset's — it carries an extra *In review* view the shipped asset does not include, as an illustration of the pattern. Where the two disagree about a view they both have, the asset wins; and a given vault's own dashboard may differ from both (discover its views with a wrong `view=`). Don't infer one file's contents from the other — read the one you mean. Save as `Maps/Dashboards/Tasks.base` and embed on `Maps/Home.md` with `![[Tasks.base]]`.
```yaml
formulas:
  days_left: 'if(due, (date(due) - today()).days, "")'
properties:
  status:
    displayName: Status
  due:
    displayName: Due
  due_time:
    displayName: Time
  formula.days_left:
    displayName: "Days Left"
  projects:
    displayName: Projects
  people:
    displayName: People
  assignee:
    displayName: Assignee
views:
  - type: table
    name: "Open — by status"
    filters:
      and:
        - not:
            - file.inFolder("Templates")
        - 'type == "task"'
        - 'status != "done"'
        - 'status != "cancelled"'
        - 'status != "delegated-out"'
    groupBy:
      property: status
      direction: ASC
    order:
      - file.name
      - status
      - priority
      - due
      - due_time
      - formula.days_left
      - projects
      - people
      - assignee
  - type: table
    name: "By assignee"
    filters:
      and:
        - not:
            - file.inFolder("Templates")
        - 'type == "task"'
        - 'status != "done"'
        - 'status != "cancelled"'
        - 'status != "delegated-out"'
    groupBy:
      property: assignee
      direction: ASC
    order:
      - file.name
      - status
      - priority
      - due
      - due_time
      - formula.days_left
      - projects
      - people
  - type: table
    name: "In review"
    filters:
      and:
        - not:
            - file.inFolder("Templates")
        - 'type == "task"'
        - 'status == "in-review"'
    order:
      - file.name
      - priority
      - due
      - due_time
      - assignee
      - projects
  - type: table
    name: "Overdue"
    filters:
      and:
        - not:
            - file.inFolder("Templates")
        - 'type == "task"'
        - 'status != "done"'
        - 'status != "cancelled"'
        - 'status != "delegated-out"'
        - 'due < today()'
    order:
      - due
      - due_time
      - file.name
      - projects
      - people
      - assignee
  - type: table
    name: "Done & cancelled"
    filters:
      and:
        - not:
            - file.inFolder("Templates")
        - 'type == "task"'
        - or:
            - 'status == "done"'
            - 'status == "cancelled"'
    order:
      - file.name
      - status
      - file.mtime
  - type: table
    name: "Delegated out"
    filters:
      and:
        - not:
            - file.inFolder("Templates")
        - 'type == "task"'
        - 'status == "delegated-out"'
    order:
      - file.name
      - assignee
      - projects
      - due
      - file.mtime
```

**"On my plate" — the lossless way to delegate.** Filtering by `assignee` separates *my* tasks from *tasks I've reassigned* without hiding anything: a reassigned task keeps its `due`, still flags overdue, still shows up in reviews, and simply drops off this view. Substitute the vault owner's own note name:

```yaml
  - type: table
    name: "On my plate"
    filters:
      and:
        - not:
            - file.inFolder("Templates")
        - 'type == "task"'
        - 'status != "done"'
        - 'status != "cancelled"'
        - 'status != "delegated-out"'
        - 'assignee.contains(link("Your Name"))'
    order:
      - file.name
      - status
      - priority
      - due
      - formula.days_left
```

Prefer this over `delegated-out` whenever the owner still wants to know how the work ends — see *Task lifecycle* in `retrieval-and-review.md`.

The three open views exclude `delegated-out` alongside `done` and `cancelled`: it means someone else owns both the work and the follow-up, so it must not sit in an open list or count as overdue (*Task lifecycle* in `retrieval-and-review.md`). *Delegated out* is the audit view — the record stays reachable without being in the owner's face.

### Inbox triage queue
```yaml
views:
  - type: table
    name: "Needs Triage"
    filters:
      and:
        - not:
            - file.inFolder("Templates")
        - or:
            - 'status == "needs-triage"'
            - file.inFolder("Inbox")
    order:
      - file.name
      - file.ctime
```

### Reading list
Ships ready-made as `assets/bases/Reading.base` → `Maps/Dashboards/Reading.base`. Chapters never appear here (they carry no `status`); each book's chapters and sparked ideas live in the book note's own inline views (*Embedding & `this`* above).
```yaml
views:
  - type: table
    name: "Reading now"
    filters:
      and:
        - not:
            - file.inFolder("Templates")
        - or:
            - 'type == "book"'
            - 'type == "source"'
        - 'status == "reading"'
    order:
      - file.name
      - author
      - status
  - type: table
    name: "To read"
    filters:
      and:
        - not:
            - file.inFolder("Templates")
        - or:
            - 'type == "book"'
            - 'type == "source"'
        - 'status == "to-read"'
    order:
      - file.name
      - author
      - created
  - type: table
    name: "Finished"
    filters:
      and:
        - not:
            - file.inFolder("Templates")
        - 'status == "done"'
        - or:
            - 'type == "book"'
            - 'type == "source"'
    order:
      - file.name
      - author
      - rating
```

### People directory & groups
```yaml
properties:
  job_title:
    displayName: Title
  department:
    displayName: Department
  company:
    displayName: Company
  last-contact:
    displayName: Last contact
views:
  - type: table
    name: "Directory"
    filters:
      and:
        - not:
            - file.inFolder("Templates")
        - 'type == "person"'
        - not:
            - 'contact == "none"'
    order:
      - file.name
      - job_title
      - department
      - company
      - email
      - phone
      - last-contact
  - type: table
    name: "By department"
    filters:
      and:
        - not:
            - file.inFolder("Templates")
        - 'type == "person"'
        - not:
            - 'contact == "none"'
    groupBy:
      property: department
      direction: ASC
    order:
      - file.name
      - job_title
      - last-contact
  - type: table
    name: "Reference (never contacts)"
    filters:
      and:
        - not:
            - file.inFolder("Templates")
        - 'type == "person"'
        - 'contact == "none"'
    order:
      - file.name
      - job_title
      - file.mtime
  - type: table
    name: "Dormant"
    filters:
      and:
        - not:
            - file.inFolder("Templates")
        - 'type == "person"'
        - 'contact == "dormant"'
    order:
      - file.name
      - job_title
      - company
      - last-contact
  - type: table
    name: "Groups"
    filters:
      and:
        - not:
            - file.inFolder("Templates")
        - 'type == "group"'
    order:
      - file.name
      - members
      - file.mtime
```
Ships ready-made as `assets/bases/People.base` → `Maps/Dashboards/People.base`.

> **Excluding a value that most notes don't carry — use `not:` + equality, never `!=`.** `contact:` defaults to *omitted* (see `properties-and-tags.md` → *Contact standing*), so nearly every person note lacks the property. `contact == "none"` against an absent property is reliably **false**, so wrapping it in `not:` includes those notes correctly. The tempting `'contact != "none"'` depends on how a missing value compares — which the Bases docs don't specify — and if it evaluated false the Directory would silently render **empty**. The same reasoning applies to any optional flag you filter on.
A **roster view** for one group filters people by their link to it — add one per group:
```yaml
  - type: table
    name: "Ops Team"
    filters:
      and:
        - not:
            - file.inFolder("Templates")
        - 'type == "person"'
        - file.hasLink("Ops Team")
    order:
      - file.name
      - job_title
      - last-contact
```

### Engagement pipeline
```yaml
properties:
  status:
    displayName: Stage
  org:
    displayName: Org
  value:
    displayName: Value
  owner:
    displayName: Owner
views:
  - type: table
    name: "Pipeline — by stage"
    filters:
      and:
        - not:
            - file.inFolder("Templates")
        - 'type == "engagement"'
        - 'status != "done"'
        - 'status != "lost"'
    groupBy:
      property: status
      direction: ASC
    order:
      - file.name
      - org
      - value
      - owner
      - people
      - file.mtime
  - type: table
    name: "Won & lost"
    filters:
      and:
        - not:
            - file.inFolder("Templates")
        - 'type == "engagement"'
        - or:
            - 'status == "done"'
            - 'status == "lost"'
    order:
      - file.name
      - org
      - value
      - status
      - file.mtime
```

### Ledger (money module)
`cancelled` transactions are excluded from all balance math (the `signed` formula returns empty for them; group views filter them out — only *All transactions* shows them, for audit). Receivables and Pledges get separate summed views (mixing them in one Sum is meaningless). A per-counterparty history is the roster pattern: filter `type == "transaction"` + `file.hasLink("William")`. One currency per transaction; group sums are per-fund **nets** — cash vs receivables vs pledges come from `money.md`'s semantics table.
```yaml
formulas:
  signed: 'if(status == "cancelled", "", if(amount, if(direction == "in", amount, 0 - amount), ""))'
properties:
  formula.signed:
    displayName: "±Amount"
  amount:
    displayName: Amount
  currency:
    displayName: Cur
  txn:
    displayName: Kind
  counterparty:
    displayName: Counterparty
  fund:
    displayName: Fund
  initiative:
    displayName: Initiative
  status:
    displayName: Status
views:
  - type: table
    name: All transactions
    filters:
      and:
        - not:
            - file.inFolder("Templates")
        - type == "transaction"
    order:
      - file.name
      - txn
      - formula.signed
      - currency
      - counterparty
      - fund
      - initiative
      - status
  - type: table
    name: Receivables (owed to us)
    filters:
      and:
        - not:
            - file.inFolder("Templates")
        - type == "transaction"
        - status == "outstanding"
        - direction == "out"
    order:
      - file.name
      - amount
      - currency
      - counterparty
      - fund
    summaries:
      amount: Sum
  - type: table
    name: Pledges (promised in)
    filters:
      and:
        - not:
            - file.inFolder("Templates")
        - type == "transaction"
        - status == "outstanding"
        - direction == "in"
    order:
      - file.name
      - amount
      - currency
      - counterparty
      - fund
    summaries:
      amount: Sum
  - type: table
    name: By fund
    filters:
      and:
        - not:
            - file.inFolder("Templates")
        - type == "transaction"
        - status != "cancelled"
    groupBy:
      property: fund
      direction: ASC
    order:
      - file.name
      - formula.signed
      - currency
      - txn
      - status
    summaries:
      formula.signed: Sum
  - type: table
    name: By initiative
    filters:
      and:
        - not:
            - file.inFolder("Templates")
        - type == "transaction"
        - status != "cancelled"
    groupBy:
      property: initiative
      direction: ASC
    order:
      - file.name
      - formula.signed
      - currency
      - txn
      - counterparty
    summaries:
      formula.signed: Sum
```

### Topic feed (drop inside a MOC)
```yaml
views:
  - type: table
    name: "Notes on this topic"
    filters:
      and:
        - not:
            - file.inFolder("Templates")
        - file.hasTag("topic/ai")
    order:
      - file.name
      - file.mtime
    summaries:
      file.name: Unique
```

## Reading a base's results (Claude Code)
A `.base` is a **definition** — reading the file tells you the filters, not the rows. Where Obsidian is running, `obsidian base:query file="Tasks.base" view="Overdue" format=md` returns the computed view, and a wrong `view=` name lists the available ones. See `cli-and-automation.md` → *Querying bases*. In Cowork or Chat there is no CLI: reason from the definition, and say that's what you're doing.

## Validate before delivering
- Valid YAML; quote strings with special chars (`:` `#` `[` `,` etc.).
- Wrap formulas containing double quotes in single quotes: `'if(x, "a", "b")'`.
- Every `formula.X` referenced in `order`/`properties` is defined in `formulas`.
- `groupBy` is an object (`property` + `direction`), never a bare string.
- A single-condition `filters:` is a **string** or wrapped in `and`/`or`/`not` — never a bare top-level list (some Obsidian versions reject it).
- Date subtraction → take `.days` (don't divide-then-round a duration).
- **Every base you deliver excludes `Templates/`** in **every** `filters:` block (above) — count blocks against exclusions before handing it over. (The and/or/not syntax demo earlier in this file is illustrative and deliberately bare.)

References: https://help.obsidian.md/bases/syntax · https://help.obsidian.md/bases/functions
