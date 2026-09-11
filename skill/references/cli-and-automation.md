# CLI & Automation

The official **Obsidian CLI** lets an agent operate a *running* Obsidian instance from the shell, and scheduled tasks turn the vault into something that updates itself (daily/weekly recaps). This applies in **Claude Code / Claude Desktop**, where Claude has a real shell and Obsidian is running. The Cowork sandbox can't reach the local Obsidian app — there, use the file tools directly instead.

> **Enabling it takes two steps, not one** (Obsidian → Settings → General → Advanced): turn on **Command line interface**, then use **Set up CLI to work in the terminal → Register**, which puts `obsidian` on `PATH`. Doing only the first leaves every call failing with `command not found`; doing only the second leaves them failing with *"Command line interface is not enabled."* Docs: https://help.obsidian.md/cli

**It is off by default, and most people never learn it exists** — so check for it rather than waiting to
be told. **`obsidian help` failing while the vault has a `.obsidian/` folder means the app is installed
and the interface is simply switched off.** Mention it once, then work with the file tools anyway.

**What the switch actually buys, since "a CLI" undersells it:** these commands read **Obsidian's live
index**, so they answer questions a text search cannot.

| Without it | With it |
|---|---|
| `grep '[[Sarah Chen]]'` — misses `[[Sarah Chen\|Sarah]]` and every alias link | `obsidian backlinks file="Sarah Chen"` — **every** link, resolved |
| Match a filename string | `file=` **resolves like a wikilink**, so any alias finds the note |
| Search words in text | `obsidian search query="status: needs-triage"` — **properties, not prose** |
| Re-read every file, every time | **A prebuilt index** |

> 🔴 **And it sidesteps the script problem entirely.** `obsidian backlinks file="عصام منير"` navigates
> **links**, not characters — so diacritics, alef forms and presentation forms never enter it. **Text
> search inside note bodies still needs the normalisation rules** (`capture-and-web.md`), but everything
> structural stops depending on them.

## Obsidian CLI basics

```bash
obsidian help                         # all commands (authoritative, always current)
```

Syntax: parameters take `=` values (quote spaces); flags are bare switches.
```bash
obsidian create name="My Note" content="# Hello\n\nBody"
obsidian create name="Note" template="Daily Note Template" overwrite
```

File targeting: `file=<name>` resolves like a wikilink; `path=folder/note.md` is exact; omit both to act on the active file. Target a vault with `vault="My Vault"` as the first parameter — `obsidian vaults` lists them and `obsidian vault` shows which one you are pointed at, worth confirming before any write. `total` returns a count where a command supports it. Creating does **not** open the file unless you pass `open` or `newtab`.

**Renaming needs the app; moving usually does not.** `obsidian rename` (and an in-app rename) rewrite inbound `[[wikilinks]]`; an external rename orphans them, because a wikilink resolves by basename. Moves are safe either way **on a default-configured vault**, where the folder is not part of the link — but a vault set to Markdown links or absolute/relative link paths stores the folder in the link, and there moves need the app as well (untested; check `.obsidian/app.json`). See `vault-structure.md`.

**A freshly-changed index lags.** After a bulk edit or an external move, `obsidian unresolved total` briefly disagreed with `obsidian unresolved`'s own list (9 against 10) while re-indexing. Read twice, a second or two apart, before reporting a link-health number.

**Unknown parameters are ignored in silence, and errors do not set an exit code.** A failing call prints `Error: …` on **stdout** and still exits `0`; a misspelled parameter is dropped with no complaint, so `format=json` mistyped as `formt=json` returns valid-looking default output, and `history:list total` ignores the flag and lists files. **Branch on the output text, never on `$?`** — and re-read a parameter name before trusting a surprising result.

Common operations:
```bash
obsidian read file="Q3 Launch"
obsidian append file="Q3 Launch" content="- new note"
obsidian search query='["status":"needs-triage"]' limit=20   # property search needs the bracket form
obsidian daily:read
obsidian daily:append content="- [ ] follow up with Sarah"
obsidian property:set name="status" value="done" file="Q3 Launch"
obsidian tasks daily todo
obsidian backlinks file="Sarah Chen"
obsidian tags sort=count counts
obsidian move file="Q3 Launch" to="Archive"    # always link-safe (a plain mv is fine on a default vault)
obsidian rename file="Q3 Launch" name="Q3 Retro"  # goes through the app, so links follow; never rename externally
obsidian delete file="Scratch"                # trash; `permanent` skips the trash entirely
```

These respect Obsidian's live index, so prefer them over raw `grep` when the app is running.

> **Task notes vs. `obsidian tasks`.** Tracked tasks are notes (Golden Rule 7): create them with `obsidian create name="…" template="Task Template"` (or the file tools) and query them via `Tasks.base`. The `obsidian tasks` command and `daily:append "- [ ]"` touch *inline* checkboxes only — in-note steps, not tracked tasks.

### Querying bases — the dashboard read path

A `.base` file on disk is only the **query definition**; Obsidian computes the rows. `base:query` returns the *computed* view, so read what the owner actually sees instead of re-implementing their filters:

```bash
obsidian base:query file="Tasks.base" view="Open — by status" format=md   # file= wants the .base extension
obsidian base:query path="Maps/Dashboards/Tasks.base" view="By assignee" format=paths
obsidian base:query file="Pipeline.base" format=json                     # no view= → the file's first view
obsidian bases                                                           # every .base in the vault
```

`format=json|csv|tsv|md|paths` (default `json`). **Every format returns the view's configured columns only** — the properties named in its `order:`, not the notes' full frontmatter. So **read the view's `order:` before promising a column**: views differ, and two vaults' `Overdue` will not match. Only `json` adds a `path` key; `csv`, `tsv` and `md` return the configured columns and nothing else, so use `paths` when you need file paths alongside a table. Read the note directly for any property no view exposes. List-valued properties come back joined into one string (`"projects": "[[A]], [[B]]"`) — fine to read, **not** safe to write back as YAML.

- **Discovering view names:** pass a `view=` that doesn't exist — the error lists them all (`Error: View not found: X` / `Available views: …`). Do this rather than assuming: view names are **case-sensitive**, and a vault's own dashboards drift from the bases this skill ships. `base:views` looks like the command for the job, but it takes **no parameters** and reads only the *active* file, so it is unusable non-interactively.
- **Grouping is dropped.** `base:query` applies the view's filters, columns and formulas, but not its `groupBy` — you get one flat table. Usually harmless, because the grouping key is also a column and you can regroup. Watch for the case where it is **not** a column: a pipeline view grouped by `status` whose `order:` omits `status` returns rows with no stage attached and no hint that anything is missing. Check the view's `order:` before promising a grouped answer.
- **Scope before you present.** These queries are whole-vault. Where a vault separates streams of work by a property — two employers under `company:`, work vs. personal under `domain:` — the answer usually needs filtering, and the view whose *name* suggests it may be the wrong tool: a `By company` view that groups by `company` typically omits it from `order:`, so its output cannot tell the streams apart, while `Open — by status` carries the column and can. Filter on the column, not on the view name.
- **`base:create`** adds a note into a base's view (`file=`, `view=`, `name=`, `content=`) and has **no `template=`**, unlike `create`. So prefer `create … template="<Type> Template"` for anything governed — tasks, transactions, engagements — or the type's required frontmatter is simply absent, and for money notes the balance restatement `money.md` mandates never happens. *(Documented from `obsidian help`; not exercised.)*
- **Comparing against the bundled dashboard server.** Two differences are systematic, so a mismatch is expected and is **not** evidence of drift: the server skips `Templates/` and `.trash`, and it does not read the `.base` files at all — its views are Python, so it will not follow an edit you make to a `.base`. Compare path sets, discount those, and treat a residue as worth investigating.

### Property search syntax

Searching a frontmatter property needs Obsidian's **bracket form**, the same thing you'd type in the app's search bar:

```bash
obsidian search query='["status":"in-review"]' limit=10
obsidian search query='["type":"task"]' total
```

Plain `query="status: in-review"` is **not** a property search — it fails with `Error: Operator "status" not recognized`.

**Calibrate before believing a zero.** The bracket form fails *silently*: `["status"="in-review"]` (wrong separator) and `["stautus":"in-review"]` (typo) both return a clean `0` with exit `0`, indistinguishable from a genuine empty result. The old broken syntax at least announced itself; this one does not. So when a property query returns nothing, **prove the syntax on a value you know exists** before reporting "none" — `obsidian search query='["type":"task"]' total` should return a healthy count. Values are matched case-insensitively and a space after the colon is tolerated.

`search:context` adds the matching line for **text** queries, and prints a line once *per match*, so a line matching twice appears twice. It adds nothing to a bracket query — a frontmatter match has no text line, so you get bare paths back.

## Second-brain automations

Pair the CLI with **scheduled tasks** (Claude Desktop scheduled tasks, or cron calling Claude Code) for hands-off upkeep. The machine must be awake when they run.

> The other scheduled job worth running is the **git snapshot** — a periodic commit that gives the vault a permanent revision history. It is unlike the recaps below: it invokes no model, writes nothing to notes, and just records what changed. See `references/version-history.md`.

### Live dashboard server (interactive)

The skill ships `scripts/dashboard_server.py` — a single, fully self-contained script — **execute** it (python3, stdlib-only); don't read it into context:

```bash
python3 "<skill-path>/scripts/dashboard_server.py" "/path/to/vault" --open
```

It serves `http://127.0.0.1:8787` (`--port` to change) with a **tabbed UI** (tab bar sticks on scroll; ◐/☀/☾ button cycles the auto/light/dark theme — dark is a warm charcoal palette): **All Tasks** · one tab per `company:` value found in tasks (e.g. Swibit) · **Personal** (tasks whose company is none of the named companies) · **Overview** (pipeline, projects, organizations, funds, meetings, people). Each task tab has a hideable **view bar** switching between **Table · By Project · By Status · By Assignee · By Due date** (plus **By Company** on All Tasks), remembered per tab. The All Tasks tab shows every task attribute as a column (status, priority, due date, due time, company, projects, people, assignee, recurrence, blocked-by, …); columns can be shown/hidden, each header has a filter button (value checklists, due-date presets like Overdue/Today/This week, text search on the title) plus sorting, and filter/column state persists in the browser. The By Project view groups tasks under each project plus a "No project" group (a task linked to multiple projects appears under each).

Editing happens in the browser: **status pills** on tasks, engagements, and projects; **due-date** and **due-time** editing on tasks; single-select menus for a task's **`priority:`** and **`company:`**; and multi-select pickers for a task's **`projects:`** and **`assignee:`** (people + organizations for assignee). Clicking a pill writes the new `status:` into the note's frontmatter, appends a dated log bullet to the body (Golden Rule 8's close-the-loop, one click), and — for a recurring task marked done — advances `due` to the next occurrence instead, per the recurrence convention. Due edits set, move, or clear `due:` (clearing also blanks `due_time:`, and is refused on a recurring task — clear `recurrence:` first); the due-time editor mirrors it with a 24-hour `HH:mm` picker and refuses a time on a task that has no due date. Priority accepts `high | normal | low` or empty; company is written as a single quoted wikilink that must resolve to an existing note, and clearing it moves the task to the **Personal** tab. Every one of these edits appends the same dated log bullet, and any key the note is missing is inserted at its position in the task template.

It also exposes two endpoints for scripting against a running instance: `/api/health` (is it up, and which vault) and `/api/data` (the whole dataset as JSON). Useful when Obsidian is closed and `base:query` is therefore unavailable.

Safety properties: binds to **127.0.0.1 only**; writes are atomic (same-dir temp + `os.replace`) and confined to the edited frontmatter properties (`status:`, `due:`/`due_time:`, `priority:`, `company:`, `projects:`, `assignee:`) plus the one log bullet; an mtime conflict check rejects a write if the note changed underneath (HTTP 409). Rule 12 still applies — the server writes files directly, so don't have the same note mid-edit in Obsidian when you click; the app re-indexes within a second. Relaunching is idempotent: if the same vault's dashboard already holds the port, it just reopens the browser; a *different* vault on the port gets told to use `--port <n+1>`.

**In-vault install — done for you on new vaults.** `scripts/bootstrap_vault.py` installs `dashboard_server.py` plus **the launcher for the platform it runs on** into `<vault>/Maps/Dashboards/`, marks it executable, and links it from the starter `Maps/Home.md`. Run from there, the server finds the vault two levels up — no argument needed — so the owner starts it by double-clicking, never by typing a path. Pass `--no-dashboard` to skip it.

| Platform | Launcher | How the owner starts it |
|---|---|---|
| macOS | `Start Dashboard.command` | double-click |
| Windows | `Start Dashboard.bat` | double-click (uses `py -3`, falls back to `python`) |
| Linux/BSD | `start-dashboard.sh` | double-click where the file manager allows launching, else `./start-dashboard.sh` |

Only the running platform's launcher is installed. A vault synced across machines gets the others by running `--dashboard-only` once on each — they coexist in the same folder.

**Existing vaults, and after a skill upgrade.** Vault copies don't self-update — `--dashboard-only` is the upgrade path **for the dashboard program only**. It installs (or replaces, when the bytes differ) just the server and launcher, scaffolds nothing, and doesn't mind an existing `CLAUDE.md`:

```bash
python3 "<skill-path>/scripts/bootstrap_vault.py" "/path/to/vault" --dashboard-only
```

> [!warning] The bootstrap never updates a `.base` or a template that already exists
> Every other install action is `if not dest.exists()`, so **an existing vault's `Maps/Dashboards/*.base`, `Templates/*.md` and `CLAUDE.md` are left exactly as they are** — no matter how far behind the skill they have fallen. Only the server and launcher are replaced.
>
> This matters whenever a skill release changes the *vocabulary* rather than the code. A vault upgrading to a release that added a task status keeps a `Tasks.base` with no filter for it, so the skill starts writing that status while the vault's own dashboard still counts those tasks as open — and the bundled browser dashboard, which *is* replaced, hides them. Two dashboards, permanently disagreeing.
>
> **So on any upgrade that changed the controlled vocabulary, diff the vault's copies against the skill's assets and patch them by hand** (`assets/bases/`, `assets/templates/`), then say what changed. `CHANGELOG.md` names the release's touched files. Don't assume re-running the bootstrap did it.

It won't add the link to an existing `Maps/Home.md` (that's the owner's note) — it prints the line to paste. **A copy the owner edited is never lost:** before replacing either file the old one is kept beside it as `<name>.bak`, and the run says so. `--dashboard-dir "<relative/path>"` installs somewhere other than `Maps/Dashboards` (relative to the vault; absolute and `..` paths are refused) — the vault path is then baked into the launcher as a relative path, since the server only infers its vault from `<vault>/Maps/Dashboards`.

**Two things worth telling the owner.** The installed server is the skill's program living inside their vault, so (a) it rides along on Obsidian Sync / iCloud / Dropbox like any other file, and (b) if they keep git history, exclude it — `references/version-history.md` has the `.gitignore` lines **and the one-time untrack step for repos that already track it** (ignore lines alone don't untrack), or every upgrade commits another ~100 KB copy.

The equivalent by hand, where running the script is awkward (macOS pair shown — substitute your platform's launcher from the table):

```bash
cp "<skill-path>/scripts/dashboard_server.py" \
   "<skill-path>/scripts/Start Dashboard.command" "/path/to/vault/Maps/Dashboards/"
chmod +x "/path/to/vault/Maps/Dashboards/Start Dashboard.command"
```

Each launcher is a few lines (`cd` to its own folder, run `dashboard_server.py --open`) — recreate one by hand where copying is awkward. Only run it from inside the vault: it serves the folder it lives in.

Like the CLI, the server is for a machine the user is sitting at (Claude Code / Desktop). In Cowork or Chat, hand the user the copy-into-vault setup above so *they* can double-click it locally.

### Daily recap (evening)
Prompt the scheduled task runs:
> "Open today's daily note (if the vault keeps dailies). Read today's meetings (`Work/Meetings/`), captures in `Inbox/`, and any notes modified today. Append a concise recap under `## 📝 Log`: what happened, decisions, and open task notes due today/overdue (from `Tasks.base`). File easy `Inbox/` items via the triage rules. Leave anything ambiguous and list it for me."

### Weekly review (Friday)
> "Read this week's `Work/Meetings/` plus `Daily/` notes and `Personal/Journal/` where those exist. Produce a weekly note: wins, misses, a focus score vs. my stated priorities, lingering inbox items, and top 3 for next week. Don't change project statuses without asking."

### People prep (before a 1:1)
> "Summarize my last 3 interactions with [[Sarah Chen]] from her people note and linked meetings. List open commitments on both sides."

### Inbox triage (e.g., twice weekly)
> "Process `Inbox/`: for each item set type + domain, file per the triage tree, upgrade frontmatter, link it. Batch by destination and show me the plan before moving."

## Setting up a scheduled task

- **Claude Desktop:** create a scheduled task with the prompt (e.g., daily 18:00, weekly Fri 16:00). It runs Claude against your local vault using this skill + the CLI.
- **Cron + Claude Code:** `0 18 * * * cd /path/to/vault && claude -p "run my daily recap skill"` (adjust to your setup).
- Keep prompts short; they should *invoke this skill* and name the inputs/outputs. Store reusable recap formats as templates in `Templates/`.

## Vault validation (bundled script)

The skill ships `scripts/validate_vault.py` — **execute it** (don't read it into context) after bulk edits, migrations, or as part of a weekly review:

**The validator reads the vault's own vocabulary.** `type` and `status` are checked against a fixed
list plus the `extra-types:` and `extra-statuses:` lines of the vault's `CLAUDE.md`, so a type the owner
registered there is accepted without anyone passing it in. The flags still work, and add to those lines.

```bash
python3 "<skill-path>/scripts/validate_vault.py" "/path/to/vault" [--extra-types a,b] [--extra-statuses x,y]
```

Checks: frontmatter parses (`Templates/` skipped; python3 required, PyYAML optional for stricter parsing), required `type`/`domain`/`created`, controlled `type`/`status`/`contact` values (checked against the union of all status sets, not per-type), transaction sanity (positive numeric amount, valid direction, fund link), chapter notes carry `book:`, unresolved wikilinks, orphaned knowledge notes (tasks/MOCs/dailies/transactions/funds/chapters exempt), stray `- [ ]` checkboxes outside task Steps, leftover `- [[ ]]` placeholders, and overdue tasks. Exit 1 = errors (fix before finishing); warnings are judgment calls — report them. Vault-specific vocabulary is read from the vault `CLAUDE.md`; the flags add to it. Two warnings on findings: a `base_n` of 1 or less, and a `measure` that starts with *why* or *how* (unless a quantity follows, as in *how many*); each usually means a fact about a source or a lesson filed as a figure.

## Deriving `last-contact` (bundled script)

`last-contact:` is the one person field nothing maintains — the rule is "update it when you file an interaction," and every missed update degrades the review sweep that reads it. But meetings already carry a date and a `people:` roster, so the answer is computable:

```bash
python3 "<skill-path>/scripts/sync_last_contact.py" "/path/to/vault"            # dry run (default)
python3 "<skill-path>/scripts/sync_last_contact.py" "/path/to/vault" --apply
        [--since YYYY-MM-DD] [--exclude "Vault Owner"]
```

Every `type: meeting` note (any folder) contributes its date to each linked attendee; each person gets their most recent. Guarantees: **never moves a date backwards** (a manually-set newer value wins, so WhatsApp/email/in-person contact you recorded by hand is safe), touches only the `last-contact:` line — inserted at its Person-template position when absent — atomic per-file write, and idempotent. Skips `contact: none` (authors and historical figures have no contact date) and reports anyone marked `contact: dormant` who turns out to have attended a meeting. **Always show the dry run before `--apply`** (Golden Rule 10). Pass `--exclude` for the vault owner, who attends their own meetings and would otherwise always read as freshly contacted.

**Know its ceiling.** It can only see interactions the vault records. Relationships conducted over chat, email, or in person produce no meeting note, so those people keep an empty `last-contact` — that is a habit gap, not a bug, and no script closes it. Read a blank as "no recorded interaction," never as "neglected."

## Staying current — receiving an update, and applying one

**This skill is a folder of files on somebody's machine, so a fix reaches them only if something
carries it there.** *When it is installed by hand, nothing does.* ⛔ **A machine nobody tells is a
machine running last month's rules while everyone else has moved on, and the person on it has no way of
knowing.**

> ### If an organisation layer beside the vault `CLAUDE.md` defines a release channel, that is the
> ### authority for where a release comes from and what the commands are. Follow it, and prefer it over
> ### anything remembered.

**What is true regardless of the channel**, and worth understanding rather than copying:

### A release is identified by a version, never by a date

⛔ **A modification date answers the wrong question.** It says *something changed*, not ***what I have is
older than what is there***, and it moves when the same bytes are uploaded again. **Compare version
numbers**, and keep the installed one written down somewhere the check can read cheaply.

### An unverified copy is never installed

**A release carries a hash of itself.** *A file that is still syncing, truncated, or half downloaded is
a real and ordinary event*, and it must be reported as **not ready** rather than installed as though it
were whole. ⛔ **One wrong hash and nothing at all is touched** - a half-applied update is worse than an
old one, because it looks finished.

### Checking is cheap and silent; installing is asked for

| | |
|---|---|
| **The check** | runs on a schedule, reads one small file, and **says nothing at all when nothing changed.** *That silence is the feature* |
| **The notification** | one message: the two version numbers, two or three lines of what changed, and how to take it |
| **The install** | happens when the owner says so ⛔ **and never by itself** |

> 🔴 **The reason is mechanical, not polite: a skill replaced while a conversation is open is not
> re-read by that conversation.** *So an update applied behind somebody's back leaves the session they
> are in running the old copy while everything reports success.* **It takes seconds, nothing is
> unavailable meanwhile, and it takes effect in the next conversation** - say exactly that, so nobody
> waits for a quiet moment that is not needed.

### What an update may and may not overwrite

| | |
|---|---|
| **The skill folder** | **replaced whole, and files the release retired are deleted.** *A copy-only update leaves a withdrawn file in place, looking valid* |
| **An organisation layer** | replaced whole, with the previous copy kept beside it |
| **The vault's own `CLAUDE.md`, and every note** | ⛔ **never touched.** They are the owner's |
| **The scaffold** - templates, dashboards, property types | **added to, never overwritten.** An edited template and a disagreeing property type are decisions somebody made |

### After it lands

**Verify file by file, then run the install check and read it aloud in one line.** *A copy that reports
success while silently skipping files is a thing that happens*, and the only defence is checking rather
than trusting the copy.

## ⛔ Checking your own work is not a check

**The model that produced something is the worst available judge of it.** *It already believes the
output is right; that belief is what produced it.* **So "I reviewed it and it looks correct" is not
evidence, and reporting it as though it were is how a defect ships with a clean bill of health.**

> ### Where the answer is a fact on disk, do not judge at all: measure.
> **Did the file move, or was it copied? Does the frontmatter say `shared`? Does the number in the
> reply match the number in the note?** *A question with a mechanical answer should never be settled by
> reading one's own prose about it.*

### Where judgement is genuinely needed, hand it to something that did not write it

**Send the artefact and the criteria to a subagent, and give it nothing else** - not the reasoning, not
the intention, not what was meant. **A fresh reader with the criteria in front of it is a different
observer**, and that difference is the whole value.

⚠️ **It is still a model, so it is evidence rather than proof.** *When the cost of being wrong is a
client, a colleague or a number that leaves the vault, the last reader is a person.*

### When this applies

| | |
|---|---|
| **After changing the skill, an instruction file or a rule** | *A change that reads well to whoever wrote it is the normal case, not the exception* |
| **After a bulk import or a long crawl** | check the notes against the source, do not re-read the summary you just wrote |
| **Before anything leaves the vault** | ⛔ the point where a mistake stops being private |

**And say which kind of checking was done.** *"Verified by reading the files"* and *"it looked right to
me"* are different claims, and only one of them is worth anything to whoever asks later.

## Mode reminder

Operating Modes are defined once in SKILL.md → *Operating Modes*. The CLI-specific delta: the `obsidian` CLI and scheduled local runs exist **only** in Claude Code / Desktop; Cowork is file-tools-only; Chat gets copy-paste commands. Run `obsidian help` rather than guessing flags — the command set evolves.

**"Claude Code" is two states, and you must know which one you are in.** The CLI needs Obsidian *installed*, *enabled* (both steps at the top of this file) **and running** — none of which follows from having a shell. Probe once with `obsidian help` before relying on it, and **degrade explicitly**: if it is unavailable, work as Cowork-with-a-shell — file reads, and reason from a `.base` definition rather than its computed rows — and tell the owner that is what you did, so a thinner answer is never mistaken for the live one. Never leave a scheduled job depending on the CLI: it will run at an hour when the app is closed and fail. Anything unattended uses the file tools.

## Editing safely while Obsidian is open

Claude and the Obsidian app can both write the same files, which risks lost edits. Keep them in sync:

- **Prefer the CLI when the app is running** (Claude Code/Desktop): `obsidian create/append/property:set` go *through* the app, so the UI and index update immediately — no stale cache.
- **`property:set` alone never satisfies Golden Rule 8.** Changing a task's `status` obliges you to log the dated line in the note body as well, and to advance `due` instead of closing a recurring task. The CLI has no single command for that, so pair them — and on a recurring task, do not set `done` at all:
  ```bash
  obsidian property:set name="status" value="done" file="Send Acme proposal"
  obsidian append file="Send Acme proposal" content="- **Done 2026-08-22**"
  ```
  A bare `property:set` leaves exactly the half-updated task the rule exists to prevent. The bundled dashboard server does both on one click; the CLI does not.
- **When editing files directly** (Cowork or scripts): Obsidian usually picks up external changes within a second, but **don't edit a note the user has open with unsaved changes** — your write and their save can clobber each other. Ask them to save/close it first, or target a different note.
- **Never run two writers on one file at once** (e.g. a script loop and the app). Finish one operation before starting the next.
- **After bulk changes**, tell the user Obsidian may need a moment to re-index. A **Git snapshot** makes anything unexpected reversible — if the vault has version history enabled, a bulk edit is a good moment to commit first; if it doesn't, `references/version-history.md` sets it up in a few minutes.
- **Schedule vault-writing tasks** for when you're not actively editing (e.g. an evening recap), to avoid collisions.

## Searching in one call, and the two hooks that save a search

**Every separate search, list and read is a round trip that re-sends the whole conversation**, and on a
usage-limited plan those trips are most of what a notes skill costs. Three pieces cut them:

```bash
python3 "<skill-path>/scripts/find.py" "Erbil" "income factor" "دخل"     # terms are OR'd
python3 "<skill-path>/scripts/find.py" --type finding "piped water"
```

- **`find.py`** searches titles, `aliases`, fields and text together, ranks the notes, shows the best
  few with their fields and matching lines, **every finding whole or not at all**, then names the rest
  and says how many. A term that matched nothing is named, so *"there is nothing in the vault"* can say
  which words were searched. ⛔ **It never reads `Judgements/` or a `type: judgement` note**, and it
  does not translate: the English words of an Arabic question are passed in, as step 0 of the retrieval
  ladder says.
- **`prompt_context.py`**, the `UserPromptSubmit` hook, prints the standing reminder and, when the
  message names notes by their title or an alias, lists them. It is a head start, never the search: a
  nickname the note does not carry, or a name in the other script, is not in the list.
- **`identity_card.py`**, a `SessionStart` hook, builds a short card from the owner's person note, read
  live at the start of each session, so a signature or a form does not open the note every time.

All three find the vault through `~/.claude/second-brain-release.json`, which the updater writes, or the
path in `~/.claude/CLAUDE.md`. **The hooks are silent or fall back to the plain reminder on any
failure**: a hook must never be the thing that breaks a conversation.

