# Vault Structure & Routing

How the vault is laid out, the exact rules for deciding where anything goes, and how to bootstrap a new vault. The goal is a structure that makes **work vs. personal** unambiguous and keeps everything retrievable.

## The default structure

```
Inbox/                  # fast capture, unsorted (status: needs-triage)
Daily/                  # daily notes (YYYY-MM-DD.md)
Tasks/                  # task notes (type: task) — one per actionable to-do
Work/
  Projects/             # active work with an outcome + deadline
  Areas/                # ongoing work responsibilities (a role, a team, a function)
  Business/             # clients, sales, partnerships, business development
  Meetings/             # work meeting notes
Personal/
  Projects/             # personal projects & goals with an end state
  Areas/                # health, finance, home, relationships, etc.
  Journal/              # reflections, personal thoughts, private logs
  Ideas/                # personal sparks and half-ideas
Resources/              # SHARED knowledge used by work AND personal
  Research/             # research topics / deep dives (hub each with a MOC)
  Sources/              # source notes — articles, papers, videos, web clips, internal briefs/reports
  Books/                # one folder per book: the book note + its chapter notes
  Notes/                # atomic / permanent concept notes (one idea each)
People/                 # one note per person (domain: work | personal) + type: group rosters
Money/                  # OPTIONAL: fund notes (type: fund) + Transactions/ (type: transaction)
Maps/                   # MOCs — Maps of Content (navigation hubs)
Archive/                # inactive items moved here from anywhere
Templates/              # note templates
Attachments/            # images, PDFs, media
```

**Why this shape.** The top level splits cleanly into `Work/`, `Personal/`, and the **shared** containers (`Resources/`, `People/`, `Maps/`). Work and personal each get a PARA-style breakdown (Projects/Areas + their specifics). Knowledge that serves both lives once in `Resources/` and is tagged by `domain`, so you never duplicate it. `Inbox/` absorbs anything you can't classify in the moment.

**Optional ordering.** If the user likes a fixed sidebar order, prefix folders with numbers (`00-Inbox`, `10-Work`, `20-Personal`, `30-Resources`, `40-People`, `50-Maps`, `90-Archive`). Keep it consistent if used.

## Adapt, don't impose

If the vault already has a structure, **read it first** (list the top-level folders) and map the routing logic onto the existing folders instead of forcing this layout. Only propose the default when starting fresh or when the user asks for a redesign. Never mass-reorganize an existing vault without explicit confirmation.

## Routing — where things go

**The routing tree lives once, in SKILL.md → *Triage & Routing*; it is not repeated here.** Walk it top-down, stop at the first match. Branch-specific notes the tree doesn't spell out:

- **Inbox (branch 1):** better to capture fast than to misfile — `Inbox/` + `status: needs-triage` is always a legitimate destination.
- **Tasks (branch 2):** filename is a Short Imperative Title; link `projects:`/`people:` and `source:` (Golden Rule 7); `assignee:` defaults to the vault owner.
- **Money (branch 3):** transactions go in `Money/Transactions/`, one note per event; funds in `Money/`; always restate balances after capture (`money.md`).
- **People (branch 4):** people are shared containers — someone who matters in both work and personal life gets `domain: shared`. Groups (`type: group`) live here too: roster in `members:`, mirrored by each member's `groups:`.
- **Sources (branch 5):** capture source metadata (`author`, `url`) in frontmatter at filing time; it's painful to recover later. A **book** gets its own folder — `Resources/Books/<Title>/<Title>.md` plus chapter notes (`type: chapter`, `book: "[[Title]]"`); the reading ideas it sparks are `type: concept` notes in `Resources/Notes/` with `source: "[[Title]]"`, never files inside the book folder (`note-types.md` → *Book*).
- **Concepts (branch 6):** link every atomic note into a relevant MOC in `Maps/` as you file it.
- **Research (branch 9):** create or update a `Maps/` MOC to hub the topic.

### Work vs. personal — the tie-breaker

Ask: **"Who is this for, and who benefits?"**
- **Work** = your job, employer, clients, revenue, professional reputation/growth.
- **Personal** = you, family, friends, health, hobbies, private reflection.
- Mixed (e.g., "learning Python" that helps both) → file by the **primary** motive; if truly 50/50, put it in `Resources/` with `domain: shared` and tag both `#work` and `#personal`.

Set `domain` on **every** note so even shared folders stay filterable. When you can't decide in one pass, leave it in `Inbox/` and ask the user a single clarifying question.

### Worked examples

| Incoming | Folder | type | domain |
|---|---|---|---|
| "Note: follow up with Acme on the renewal" | `Work/Business/Acme.md` (or a task in the project) | business | work |
| "Thoughts after therapy today" | `Personal/Journal/2026-06-16.md` | journal | personal |
| "Great article on attention in transformers" | `Resources/Sources/` | source | shared |
| "Idea: a triage step that tags work vs personal" | `Resources/Notes/` + link to a MOC | concept | shared |
| "Kickoff notes for the Q3 launch" | `Work/Projects/Q3 Launch.md` | project | work |
| "Sarah mentioned she's moving to design" | `People/Sarah Chen.md` | person | work |
| "Want to run a half-marathon this year" | `Personal/Projects/Half Marathon.md` | project | personal |
| "Book notes: Building a Second Brain" | `Resources/Books/Building a Second Brain/` | book (+ chapters) | shared |

## The vault `CLAUDE.md`

Drop a `CLAUDE.md` in the vault root so any agent (Claude Code especially) understands the vault instantly. Keep it short — it is **instructions**, not stored knowledge. This file is the home for everything vault-specific — the owner's folders, vocabulary extensions, entities, and workflows — so the skill itself stays generic and shareable. **Always check for an existing `CLAUDE.md` first (First Contact in SKILL.md) and never overwrite one without explicit confirmation** — extend it additively. Template:

```markdown
# Vault Guide for Claude

This is my Obsidian second brain. Use the `obsidian-second-brain` skill.

## Structure
- `Inbox/` capture; `Daily/` daily notes; `Tasks/` task notes (`type: task`)
- `Work/` Projects, Areas, Business, Meetings
- `Personal/` Projects, Areas, Journal, Ideas
- `Resources/` Research, Sources, Books, Notes (shared knowledge)
- `People/` one note per person; `Maps/` MOCs; `Archive/` inactive

## Rules
- Every note has frontmatter: `type`, `domain` (work|personal|shared), `created`.
- Use controlled values only (see the skill's properties-and-tags reference).
- Triage work vs personal before filing; link every note to a MOC or related note.
- Search before reading; never load the whole vault.
- Confirm before deleting, overwriting, or mass-moving notes.

## Naming
- Notes: Title Case, human-readable (`Q3 Launch.md`).
- Daily: `YYYY-MM-DD.md`. People: `Full Name.md`.
```

## Bootstrapping a new vault

**Interview first** — `references/onboarding.md` (ask about the owner's work before creating anything). Then the deterministic scaffold: **execute** `scripts/bootstrap_vault.py <vault> --modules core,work[,personal,resources,daily,money]` — it creates the module folders, installs `assets/templates/` and `assets/bases/`, and writes a starter Home MOC (it refuses vaults that already have a `CLAUDE.md`). Manual fallbacks:

**Cowork (file tools):** create the folders and `Templates/` files directly, add `CLAUDE.md`, and create starter MOCs (`Maps/Home.md`). 

**Claude Code (shell):**
```bash
mkdir -p Inbox Daily Tasks \
  Work/{Projects,Areas,Business,Meetings} \
  Personal/{Projects,Areas,Journal,Ideas} \
  Resources/{Research,Sources,Books,Notes} \
  People Maps Maps/Dashboards Archive Templates Attachments
# optional money module: mkdir -p Money/Transactions
```
Then create `CLAUDE.md` and a `Maps/Home.md` top-level MOC that links to the main areas.

**Chat:** give the user the tree + the `mkdir` command + the `CLAUDE.md` to paste.

Always finish setup by creating a **Home MOC** (`Maps/Home.md`) that links to `Maps/Work.md`, `Maps/Personal.md`, and key area notes — this becomes the front door to the vault.

## Day 1 — minimal start

Don't build the whole structure on day one — a beautiful empty vault you never use is the classic failure. Start with a few things and let the rest grow as real notes arrive:

```bash
mkdir -p Inbox Tasks Templates Attachments
```
- **Capture** everything to `Inbox/` (`type: fleeting`) — or straight to task notes when it's clearly a to-do.
- A **`Daily/`** note each day is optional — add the folder only if the habit appeals.
- Create a folder only when you actually have notes that need it — when `Inbox/` keeps filling with the same kind of thing, give it a home (e.g. `Work/Projects/`).
- Add `CLAUDE.md` and `Maps/Home.md` once you have a handful of notes worth linking.

This grows into the full structure above without upfront overwhelm.

## Sync & multi-device

The vault is just a folder, so sync it however you like — but pick **one** method to avoid conflicts:

- **Obsidian Sync** — official, end-to-end encrypted, syncs `.obsidian/` settings and resolves conflicts cleanly. Easiest for multiple devices.
- **iCloud / Dropbox / OneDrive / Google Drive** — free, but can create "conflicted copies" if two devices edit while offline; let one device finish syncing before editing on another.
- **Git** — version history and rollback (especially valuable when an agent edits the vault). Add a `.gitignore` for `.obsidian/workspace*` and large attachments; pairs with the Obsidian Git plugin.

Don't stack two sync engines on one folder. When Claude (CLI/Cowork) and the Obsidian app both touch the vault, follow the concurrent-edit note in `cli-and-automation.md`.

## Attachments

- Keep media in `Attachments/` (or a per-folder `attachments/` subfolder in large vaults).
- Set Obsidian's default location: Settings → Files & Links → *Default location for new attachments* → a fixed `Attachments/` folder (or a subfolder under the current note).
- Embed with `![[image.png|400]]` (see `markdown-syntax.md`). Link large files rather than pasting big base64 blobs into notes.
- If syncing via Git, consider Git LFS or excluding large binaries to keep the repo light.

## Migrating in (existing notes)

Bringing notes from another app is often the first real task. Use the **core Importer plugin** (Settings → core/community plugins → "Importer", depending on version):

- Supports **Apple Notes** (export HTML), **Evernote** (`.enex`), **Notion** (Markdown+CSV zip), **Roam** (JSON), **Google Keep** (Takeout), **Bear**, plain Markdown/HTML, and CSV (one note per row).
- After import, notes land in a folder. **Don't reorganize by hand** — drop them in `Inbox/` (or an `Import/` staging folder) and run inbox **triage** in batches: set `type`/`domain`, file per the routing tree, link, and dedupe (search-before-create) as you go.
- Expect imperfect conversions (complex tables, nested links). Fix opportunistically; don't block on perfection.
- Import in **chunks** and triage each chunk before the next — never stare at 2,000 unsorted notes.

## Archiving

- Move a note to `Archive/` when its project is `done`/abandoned or an area is no longer maintained; for types that carry `status` (projects, orgs, funds, research), set it to `archived` (or `done`). Areas have no status field — the move itself is the record.
- **Tasks:** mark a finished task `status: done` (or `cancelled`) and leave it in `Tasks/` — the `Tasks.base` "Done & cancelled" view keeps it out of the open lists. Per Golden Rule 8, an `Archive/` sweep of long-done tasks may be **offered** (monthly review) with explicit confirmation — never automatic, never deletion (the `source`/`projects` links are useful history).
- **Links survive moves** — Obsidian auto-updates `[[wikilinks]]` and backlinks, so archiving never breaks references.
- Archive is for *inactive but worth keeping*. Truly useless notes can be deleted (with confirmation). Reference knowledge you still consult stays in `Resources/`, not `Archive/`.
