# CLI & Automation

The official **Obsidian CLI** lets an agent operate a *running* Obsidian instance from the shell, and scheduled tasks turn the vault into something that updates itself (daily/weekly recaps). This applies in **Claude Code / Claude Desktop**, where Claude has a real shell and Obsidian is running. The Cowork sandbox can't reach the local Obsidian app — there, use the file tools directly instead.

> Enable the CLI in Obsidian: Settings → General → Command line interface. Docs: https://help.obsidian.md/cli

## Obsidian CLI basics

```bash
obsidian help                         # all commands (authoritative, always current)
```

Syntax: parameters take `=` values (quote spaces); flags are bare switches.
```bash
obsidian create name="My Note" content="# Hello\n\nBody" silent
obsidian create name="Note" template="Daily" silent overwrite
```

File targeting: `file=<name>` resolves like a wikilink; `path=folder/note.md` is exact; omit both to act on the active file. Target a vault with `vault="My Vault"` as the first parameter. `--copy` copies output to clipboard; `silent` prevents files opening; `total` returns a count.

Common operations:
```bash
obsidian read file="Q3 Launch"
obsidian append file="Q3 Launch" content="- new note"
obsidian search query="status: needs-triage" limit=20
obsidian daily:read
obsidian daily:append content="- [ ] follow up with Sarah"
obsidian property:set name="status" value="done" file="Q3 Launch"
obsidian tasks daily todo
obsidian backlinks file="Sarah Chen"
obsidian tags sort=count counts
```

These respect Obsidian's live index, so prefer them over raw `grep` when the app is running.

> **Task notes vs. `obsidian tasks`.** Tracked tasks are notes (Golden Rule 7): create them with `obsidian create name="…" template="Task"` (or the file tools) and query them via `Tasks.base`. The `obsidian tasks` command and `daily:append "- [ ]"` touch *inline* checkboxes only — in-note steps, not tracked tasks.

## Second-brain automations

Pair the CLI with **scheduled tasks** (Claude Desktop scheduled tasks, or cron calling Claude Code) for hands-off upkeep. The machine must be awake when they run.

### Live dashboard server (interactive)

The skill ships `scripts/dashboard_server.py` — a single, fully self-contained script — **execute** it (python3, stdlib-only); don't read it into context:

```bash
python3 "<skill-path>/scripts/dashboard_server.py" "/path/to/vault" --open
```

It serves `http://127.0.0.1:8787` (`--port` to change) with a **tabbed UI** (tab bar sticks on scroll; ◐/☀/☾ button cycles the auto/light/dark theme — dark is a warm charcoal palette): **All Tasks** · one tab per `company:` value found in tasks (e.g. Swibit) · **Personal** (tasks whose company is none of the named companies) · **Overview** (pipeline, projects, organizations, funds, meetings, people). Each task tab has a hideable **view bar** switching between **Table · By Project · By Status · By Assignee · By Due date** (plus **By Company** on All Tasks), remembered per tab. The All Tasks tab shows every task attribute as a column (status, priority, due date, due time, company, projects, people, assignee, recurrence, blocked-by, …); columns can be shown/hidden, each header has a filter button (value checklists, due-date presets like Overdue/Today/This week, text search on the title) plus sorting, and filter/column state persists in the browser. The By Project view groups tasks under each project plus a "No project" group (a task linked to multiple projects appears under each).

Editing happens in the browser: **status pills** on tasks, engagements, and projects; **due-date** and **due-time** editing on tasks; single-select menus for a task's **`priority:`** and **`company:`**; and multi-select pickers for a task's **`projects:`** and **`assignee:`** (people + organizations for assignee). Clicking a pill writes the new `status:` into the note's frontmatter, appends a dated log bullet to the body (Golden Rule 8's close-the-loop, one click), and — for a recurring task marked done — advances `due` to the next occurrence instead, per the recurrence convention. Due edits set, move, or clear `due:` (clearing also blanks `due_time:`, and is refused on a recurring task — clear `recurrence:` first); the due-time editor mirrors it with a 24-hour `HH:mm` picker and refuses a time on a task that has no due date. Priority accepts `high | normal | low` or empty; company is written as a single quoted wikilink that must resolve to an existing note, and clearing it moves the task to the **Personal** tab. Every one of these edits appends the same dated log bullet, and any key the note is missing is inserted at its position in the task template.

Safety properties: binds to **127.0.0.1 only**; writes are atomic (same-dir temp + `os.replace`) and confined to the edited frontmatter properties (`status:`, `due:`/`due_time:`, `priority:`, `company:`, `projects:`, `assignee:`) plus the one log bullet; an mtime conflict check rejects a write if the note changed underneath (HTTP 409). Rule 12 still applies — the server writes files directly, so don't have the same note mid-edit in Obsidian when you click; the app re-indexes within a second. Relaunching is idempotent: if the same vault's dashboard already holds the port, it just reopens the browser; a *different* vault on the port gets told to use `--port <n+1>`.

**Double-click launcher — the `.command` pattern (macOS).** So the user can start it without a terminal: copy `dashboard_server.py` into `<vault>/Maps/Dashboards/` (run from there, the server finds the vault two levels up, no argument needed), then install the bundled launcher beside it and mark it executable:

```bash
cp "<skill-path>/scripts/dashboard_server.py" \
   "<skill-path>/scripts/Start Dashboard.command" "/path/to/vault/Maps/Dashboards/"
chmod +x "/path/to/vault/Maps/Dashboards/Start Dashboard.command"
```

The launcher is four lines (`cd` to its own folder, `exec python3 dashboard_server.py --open`) — recreate it by hand where copying is awkward. Only run it from inside the vault: it serves the folder it lives in. Vault copies don't self-update — re-copy `dashboard_server.py` after a skill upgrade.

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

```bash
python3 "<skill-path>/scripts/validate_vault.py" "/path/to/vault" [--extra-types a,b] [--extra-statuses x,y]
```

Checks: frontmatter parses (`Templates/` skipped; python3 required, PyYAML optional for stricter parsing), required `type`/`domain`/`created`, controlled `type`/`status` values (checked against the union of all status sets, not per-type), transaction sanity (positive numeric amount, valid direction, fund link), unresolved wikilinks, orphaned knowledge notes (tasks/MOCs/dailies/transactions/funds exempt), stray `- [ ]` checkboxes outside task Steps, leftover `- [[ ]]` placeholders, and overdue tasks. Exit 1 = errors (fix before finishing); warnings are judgment calls — report them. Feed vault-specific vocabulary extensions from the vault `CLAUDE.md` via the flags.

## Mode reminder

Operating Modes are defined once in SKILL.md → *Operating Modes*. The CLI-specific delta: the `obsidian` CLI and scheduled local runs exist **only** in Claude Code / Desktop; Cowork is file-tools-only; Chat gets copy-paste commands. Run `obsidian help` rather than guessing flags — the command set evolves.

## Editing safely while Obsidian is open

Claude and the Obsidian app can both write the same files, which risks lost edits. Keep them in sync:

- **Prefer the CLI when the app is running** (Claude Code/Desktop): `obsidian create/append/property:set` go *through* the app, so the UI and index update immediately — no stale cache.
- **When editing files directly** (Cowork or scripts): Obsidian usually picks up external changes within a second, but **don't edit a note the user has open with unsaved changes** — your write and their save can clobber each other. Ask them to save/close it first, or target a different note.
- **Never run two writers on one file at once** (e.g. a script loop and the app). Finish one operation before starting the next.
- **After bulk changes**, tell the user Obsidian may need a moment to re-index, and keep a **Git snapshot** so anything unexpected is reversible.
- **Schedule vault-writing tasks** for when you're not actively editing (e.g. an evening recap), to avoid collisions.
