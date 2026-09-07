# Methodologies — PARA, Zettelkasten, LYT/MOCs, and the blend

Use this to explain the systems to a user, help them choose, or understand why this skill is structured the way it is. This vault uses a **PARA-based blend**: PARA for organization, MOCs for navigation, atomic notes for durable ideas, and the CODE workflow for processing.

## PARA (Tiago Forte, *Building a Second Brain*)

Organize by **actionability**, not by topic. Four buckets:

- **Projects** — short-term efforts with a goal and an end (a launch, a trip, a paper). Has a finish line.
- **Areas** — ongoing responsibilities to maintain over time with no end date (health, finances, a job role, a team).
- **Resources** — topics and interests for future reference (research, books, reusable knowledge).
- **Archive** — anything from the above three that's now inactive.

The test that separates Projects from Areas: a Project can be *completed*; an Area is *maintained*. PARA's strength is that it works for work and life together and is beginner-friendly. Its weakness is that pure PARA underuses linking — which is why we add MOCs.

**CODE** is PARA's companion workflow: **C**apture → **O**rganize → **D**istill → **E**xpress. It maps onto this skill's Operating Loop (with explicit Triage and Review added).

## Zettelkasten ("slip-box," Niklas Luhmann)

A method for *thinking and writing*, not just filing. Principles:

- **Atomic notes** — one idea per note, written in your own words.
- **Unique IDs** — each note gets a stable identifier (often a timestamp like `202606161045`) so links never break.
- **Dense linking** — notes connect to other notes; meaning emerges from the web, not from folders.
- **Three note kinds** — *fleeting* (quick captures), *literature* (notes from sources — this skill's `type: source` and `type: chapter` notes; we renamed the type because most vaults' sources aren't literature), *permanent* (refined atomic ideas in the slip-box).

Strength: unmatched for research, writing, and developing original ideas over years. Weakness: higher discipline, and pure Zettelkasten can feel heavy for everyday work/admin. We borrow its **atomic notes** (`Resources/Notes/`) and optional **timestamp IDs**, without forcing the full system.

## LYT / MOCs (Nick Milo, "Linking Your Thinking")

A lighter, linking-first philosophy. Don't over-plan folders; capture freely, link liberally, and when a cluster of notes grows around a theme, create a **Map of Content (MOC)** — an index note that links to related notes and imposes order *after* the fact rather than before.

- **MOC** = a hand-curated hub note. It holds links and light commentary, not primary content.
- Structure is **emergent**: you make a MOC when you feel the need, not upfront.

Strength: flexible, low friction, scales naturally. Weakness: with no folder discipline at all, retrieval can suffer. We use MOCs as the **navigation layer** on top of PARA folders — best of both.

## The blend this skill uses

| Layer | Borrowed from | How it's used here |
|---|---|---|
| Folder organization | PARA | `Work/`, `Personal/` (Projects + Areas), `Resources/`, `Archive/` |
| Processing workflow | CODE | Capture → Triage → Organize → Distill → Express → Review |
| Durable ideas | Zettelkasten | Atomic notes in `Resources/Notes/`; optional timestamp IDs |
| Navigation | LYT/MOCs | `Maps/` hubs; a cluster earns a MOC once it grows (~5+ related notes); `Maps/Home.md` is the front door |
| Actionable to-dos | (pragmatic add) | Tracked tasks as notes in `Tasks/` (`type: task`), surfaced via `Tasks.base` — outside pure PARA, but keeps "what's on my plate" queryable |

**Why a blend rather than one pure method:** the user wants work *and* personal in one vault with reliable work/personal separation. PARA gives that separation and is the easiest to start. MOCs prevent the vault from becoming a pile of disconnected folders. Atomic notes let knowledge compound. None of the three alone delivers all of that.

## Helping a user choose

- New to PKM, mixes work + life, wants low friction → **PARA blend (this default).**
- Academic/writer building original ideas over years → lean harder into **Zettelkasten** (more atomic notes, timestamp IDs, fewer folders).
- Dislikes rigid folders, thinks in connections → lean into **LYT/MOCs** (flatter folders, more maps).

You can shift the emphasis without changing the skill — e.g., put more weight on `Resources/Notes/` + `Maps/` for a Zettelkasten/LYT lean, or on `Work/Projects/` + `Personal/` for a PARA lean.

## A note on scope (managing expectations)

A second brain in Markdown is excellent for **capturing, connecting, drafting, and reviewing** knowledge. It is **not** a relational database. For thousands of highly structured records that need complex queries (e.g., a CRM with multi-field filters and joins), use **Bases** for in-vault structured views (`bases.md`), and for truly large/relational needs point the user to a real database rather than overloading Markdown. Keep notes consistently structured (controlled frontmatter) so they stay queryable as the vault grows.
