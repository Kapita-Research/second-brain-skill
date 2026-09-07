# Community Plugins (OPTIONAL)

> **This vault is core-first.** Everything works with native Obsidian (Bases + core plugins). The plugins below are **optional power-ups** — only use them if the user confirms they're installed. Always **label outputs that depend on a community plugin**, and prefer a Bases-native solution when one exists (`bases.md`). Install from Settings → Community Plugins.

When to reach for these:
- **Bases (native)** covers most structured table/list dashboards → prefer it.
- **Dataview** — inline queries, more flexible querying, `TASK`/`CALENDAR` outputs Bases doesn't do yet.
- **Templater** — dynamic templates (dates, prompts, scripting) beyond core Templates.
- **Tasks** — *optional* inline-checkbox tasks (due dates, recurrence, priorities). Default is task **notes** (Golden Rule 7); reach for this only if the user prefers `- [ ]` tasks.

---

## Dataview

Query notes like a database from inside a note.

```dataview
TABLE status, due, file.mtime AS "Modified"
FROM "Work/Projects"
WHERE type = "project" AND status = "active"
SORT due ASC
```

Query types: `TABLE`, `LIST`, `TASK`, `CALENDAR`. `FROM` sources: `#tag`, `"Folder"`, `[[Note]]`, `outgoing([[Note]])`, combine with `AND`/`OR`, exclude with `-`. Common `WHERE`: `status != "done"`, `contains(tags, "topic/ai")`, `due <= date(today) + dur(7 days)`, `!completed`. Implicit fields: `file.name/.path/.folder/.ctime/.mtime/.tags/.inlinks/.outlinks/.tasks/.day`.

Inline: `` `= this.status` ``, `` `= date(today)` ``.

Vault-matched examples:
```dataview
LIST FROM "Inbox" WHERE status = "needs-triage"
```
```dataview
TABLE author, status FROM "Resources/Books" WHERE status != "done"
```
```dataview
TASK FROM "Work" WHERE !completed AND due <= date(today) + dur(7 days) GROUP BY file.link
```

> Note: Dataview queries don't render outside Obsidian at all. Bases and plain Markdown are more portable.

## Templater

Dynamic templates (core Templates only does `{{title}}`/`{{date}}`/`{{time}}`).

```javascript
<%= tp.date.now("YYYY-MM-DD") %>            today
<%= tp.date.now("YYYY-MM-DD", -1) %>        yesterday
<%= tp.file.title %>                        note title
<%= tp.system.prompt("Project name") %>     ask the user
<%= tp.system.suggester(["Work","Personal"], ["work","personal"]) %>   pick a value
```
Use it to make the `note-types.md` templates self-filling. Example daily-note header:
```javascript
---
type: daily
domain: shared
created: <%= tp.date.now("YYYY-MM-DD") %>
---
# <%= tp.date.now("dddd, MMMM D, YYYY") %>
- Yesterday: [[<%= tp.date.now("YYYY-MM-DD", -1) %>]]
```
Set a Templates folder + (optionally) folder-template mappings so new notes in `Work/Projects/` auto-apply the project template.

## Tasks

> **Default is task *notes*, not this plugin** (Golden Rule 7; templates in `note-types.md`, dashboard in `bases.md`). The Tasks plugin below is an **optional** alternative for users who prefer inline `- [ ]` tasks. Its dates are **date-only** (no time-of-day) — one reason task notes use a separate `due_time`.

Richer inline checkboxes than core.

```markdown
- [ ] Ship landing page 📅 2026-07-01 🔁 every week ⏫
- [x] Sent contract ✅ 2026-06-16
```
Emojis: 📅 due · 🛫 start · ⏳ scheduled · ✅ done · 🔁 recurrence · priority 🔺⏫🔼🔽⏬.

Query block:
````markdown
```tasks
not done
due before next week
path includes Work
sort by due
group by path
```
````

## Other plugins users often pair (mention if relevant)
- **Notebook Navigator** — better file explorer.
- **Omnisearch** — stronger full-text search at scale.
- **Obsidian Git** — version/backup the vault.
- **Claudian** — embeds Claude Code in the Obsidian sidebar (desktop).
- **Importer (core, not a community plugin)** — bring in Apple Notes, Evernote, Notion, Roam, etc. Migration workflow is in `vault-structure.md` → *Migrating in*.

Keep dependencies minimal: if a native Base does the job, use the Base.
