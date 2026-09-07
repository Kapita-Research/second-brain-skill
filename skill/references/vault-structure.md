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
                        #   authors/historical figures live here too — mark them contact: none
Money/                  # OPTIONAL: fund notes (type: fund) + Transactions/ (type: transaction)
Outbox/                 # OPTIONAL: finished notes handed to an organisation — the only exit
Findings/               # OPTIONAL: one note per research figure (type: finding)
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
| "Notes on the author of the book I'm reading" | `People/Fadhil Hussain.md` (`contact: none`) | person | shared |
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
- Filenames in one script (ours: Latin). Every other spelling goes in `aliases`.
```

## Naming across scripts — one filename, many aliases

**A vault whose owners write in more than one script needs one rule, and it is not about language.**

📐 **Pick a single script for filenames — and put every other spelling in `aliases`.**

```yaml
# Uruk Technology.md
aliases: [أوروك, أوروك للتقنية, Uruk, اوروك]
```

**People still write however they like.** `[[أوروك]]` resolves through the alias; the convention decides
what the **file** is called, not what anyone types.

### 🔴 An alias must be unique, or it must not exist

**An alias that could fit more than one note is worse than no alias at all.**

> **Golden Rule 2 catches ambiguity by *finding two candidates and asking*. A shared name registered on
> **one** person produces exactly one candidate — so there is nothing to detect. It resolves cleanly,
> silently, to the wrong note.**

**Where several people share a given name, that name goes on nobody's list.** Only the forms that
identify one person do: a surname, a compound given name, a father's name, an initial-plus-surname.

### ✅ What an alias is actually for

**An alias is not there to teach Claude that two spellings are the same name — it already knows that,
and generates variants better than a list can.**

📐 **Write an alias when something *mechanical* has to resolve the name:**

| | |
|---|---|
| **Obsidian's link resolver** | `[[آيه]]` opens the note **only** if that exact string is in `aliases`. **This is the main reason the list exists** |
| **A base or a filter** | matches a literal value |
| **Any index built over the vault later** | compares characters |

**So the test is not *"could someone spell it this way?"* — it is *"will someone type this as a link?"*
A couple of real forms per entity covers that. **An exhaustive permutation list is wasted effort**, and
it is never complete anyway.

**What genuinely belongs written down is what cannot be worked out from the name itself** — that two
people here are called Yousif, that this person is also the one who signs as *M. Mustafa Imran*, that a
former name still appears in old notes. **Facts about the world, not spelling mechanics.**

**Compound and patronymic names make this ordinary rather than rare.** Someone whose full name is three
parts may be called by any two of them — **register each combination that is unique, and leave out every
part that is not.**

> 📐 **Transliterate, never translate.** An entity whose name has no official form in the filename script
> gets it **written in those letters, not rendered into that language** — a translated name is one **you
> invented**: it appears on no contract, no invoice and no email, so nobody else will ever search for
> it. **Every transliteration people actually use goes into `aliases`**, because transliteration varies
> where translation only misleads.

### Why a filename is not a free choice

**A note title is a technical identifier that travels** — through sync, `git`, links, the terminal, and
whatever reads the vault later. **A filename in a script some of those handle badly causes small,
scattered problems that are tedious to unpick.** Latin is the usual safe choice simply because
everything handles it.

### 🔴 Why this cannot be left to preference

**Golden Rule 2 — *search before you create* — is what prevents duplicate entities. It works inside one
script and breaks across two.**

> Someone searching `Uruk` does not find `أوروك.md` when that note carries no Latin alias. **They follow
> the rule correctly and create the second note anyway** — and now one company has two records, each
> holding half its history, with nothing saying they are the same thing.

**`aliases` cannot repair this. They let one note answer to many names; they do not merge two notes.**

### Seed the entities rather than relying on the convention

**People create entity notes before they read any convention.** So for a shared or organisational
vault, **ship the entity notes already written** — the colleagues, the clients, the recurring
organisations, each with its aliases in both scripts.

> **Nobody creates what already exists.** The convention then only has to govern genuinely new names.

> ⚠️ **A seed list is a starting set, never a closed one.** **New entities are normal** — say so
> explicitly wherever the list is written, or someone will read it as the set of entities they are
> allowed to create, and hesitate at exactly the moment capture should be frictionless.

## Renaming — an action, not a file operation

**Renaming a note in a file manager silently breaks every `[[link]]` pointing at it.** Obsidian rewrites
those links when *it* performs the rename — but the primary operating mode is **Cowork, where Obsidian
is not running**, so that safety net is absent exactly where this skill does most of its work.

📐 **A rename is three steps, and all three are yours:**

1. **Rename the file.**
2. **Rewrite every link that points to it** — search the vault for the old title, including
   `[[Old Name|shown text]]` and `[[Old Name#Heading]]` forms.
3. **Add the old name to the note's `aliases`.**

> **Step 3 is the one Obsidian does not do, and it is the most valuable.** An old name that survives as
> an alias means **a link missed anywhere still resolves**, a search on the old name still works, and
> **anything reading this vault later can tell that both names are one thing.**

**Run `scripts/validate_vault.py` after any batch of renames** — broken links then surface in days
rather than years.

**Renaming a person or an organisation is the common case**, and it is exactly where the surviving
alias pays: transcripts, old meeting notes and other people's spellings all keep resolving.

## Bootstrapping a new vault

**Interview first** — `references/onboarding.md` (ask about the owner's work before creating anything). Then the deterministic scaffold: **execute** `scripts/bootstrap_vault.py <vault> --modules core,work[,personal,resources,daily,money]` — it creates the module folders, installs `assets/templates/` and `assets/bases/`, drops the live dashboard server (plus this platform's launcher) into `Maps/Dashboards/`, and writes a starter Home MOC (it refuses vaults that already have a `CLAUDE.md`). Manual fallbacks:

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
- **Tasks:** mark a finished task `status: done` (or `cancelled`) and leave it in `Tasks/` — the `Tasks.base` "Done & cancelled" view keeps it out of the open lists. A task handed to someone else *along with its supervision* gets `delegated-out` and the "Delegated out" view; it is **not** "finished" and **not** archive fodder — the work may still be live in their hands. Per Golden Rule 8, an `Archive/` sweep of long-done tasks may be **offered** (monthly review) with explicit confirmation — never automatic, never deletion (the `source`/`projects` links are useful history).
- **Moving a note doesn't break `[[wikilinks]]`; renaming one does.** Archiving is safe — a wikilink carries no folder, and Obsidian resolves it by **basename**, treating any path inside the link as a hint only. Verified by moving a note with a plain filesystem `mv`: inbound links kept resolving, and the referring notes were **not modified** — nothing was rewritten, so this holds whether the move went through the app, the CLI, or the file tools.
  - **The scope of that guarantee, stated honestly.** It was tested on a vault using Obsidian's defaults — wikilinks, *shortest* link format. A vault set to **Markdown links** (`useMarkdownLinks: true`) or to **absolute/relative** link paths (`newLinkFormat`) stores the folder *inside* the link, so there a move plausibly **does** break references and only an in-app or `obsidian move` move is safe. **This was not tested.** Check `.obsidian/app.json` before promising a vault its moves are safe, and if those settings are non-default, route moves through the app too.
- **A rename is the dangerous one, and only Obsidian can make it safe.** Basename resolution has nothing to fall back on when the basename changes, so an external rename silently orphans every inbound link (verified: `unresolved` rose by one per link form, and the renamed note had zero backlinks). The *Automatically update internal links* setting does **not** save you — it fires when the app performs the rename, not when the app merely notices one. So: rename through Obsidian, or with `obsidian rename file="Old" name="New"` while it is running (`cli-and-automation.md`). In Cowork or with the app closed, either defer the rename or **find and update every inbound link yourself** — search the old name first, and tell the owner you did it by hand.
- **Basename resolution has a collision edge.** Two notes sharing a basename make `[[That Name]]` ambiguous, so moving a note into a folder beside a same-named one can silently re-point existing links at the wrong file. Check for a name clash before moving, not after.
- Archive is for *inactive but worth keeping*. Truly useless notes can be deleted (with confirmation). Reference knowledge you still consult stays in `Resources/`, not `Archive/`.
