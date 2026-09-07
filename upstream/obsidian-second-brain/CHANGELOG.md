# Changelog — obsidian-second-brain

Version lives in `SKILL.md` frontmatter (`metadata.version`). Install/upgrade: open the `.skill` file in Claude → **Save skill** (replaces the same-named skill) → start a **new chat**.

## 2.9.2 — 2026-08-08
Fixes the Web Clipper guidance — it documented a filter that does not exist.

- **Removed `{{author|default:"Unknown"}}`.** Web Clipper has **no `default`/fallback filter**; pasting that template made the extension reject it outright with `Unknown filter "default"`. The full official filter list is now quoted inline in `capture-and-web.md` so the next template is written against reality, with the rule that an unknown name kills the whole template — design for graceful degradation instead of inventing a filter. The body no longer repeats `{{author}}` at all (it is already a property).
- **Corrected the property mapping.** `source` was `{{title}}` (an article's title is not its source) and there was no `url` property — now `source: {{domain}}` + `url: {{url}}`, matching how the vault's own source notes record origin. `tags` was the `topic/` placeholder, which only works where a human fills it in; an unattended clipper would stamp a literal `topic/` on every note, so it is now `clippings` (a real provenance tag for finding un-triaged clips, and consistent with existing flat tags like `people`/`company`).
- **The guidance is now a full, verified configuration** — Behavior/Note name/Note location table plus a properties table carrying each property's **Obsidian type**, so clips satisfy `types.json` on arrival. Note name gains `{{title|safe_name:mac}}`: article titles routinely contain `:` `/` `#` `^` `[` `]` `|`, which break macOS filenames or Obsidian wikilinks.
- **Full-text clipping documented.** `{{highlights}}` (what the reader marked) stays the default for retrieval and copyright reasons, but when the owner wants the whole article too it goes **last**, behind a `## Full text` heading, folded via `{{content|callout:("quote","Clipped article",true)}}`. Hand-writing `> {{content}}` silently quotes only the first line — the `callout`/`blockquote` filters exist precisely because multi-line prefixing can't be done by hand.
- Docs only — no schema, script, template, or base changes.

## 2.9.1 — 2026-08-08
Property **types** get pinned down — `author` becomes a list, and the vault gains an explicit type registry.

- **`author` is now `multitext` (List)** in `assets/types.json`, the Book template, and the Source template. 2.9.0 shipped a Book template with a list `author:` while the Source template kept a scalar — since Obsidian keys property types by **name across the whole vault**, those two cannot coexist. List wins: multi-author books and papers are normal, and every other link-bearing property here (`people`, `projects`, `assignee`, `groups`, `members`) is already a list. **Migration:** rewrite any scalar `author: "[[X]]"` as a one-item list. Bases consequence — query authors with `author.contains(this)`, not `author == this`.
- **New `assets/types.json`** — the full property→type map for the vocabulary, installed by `bootstrap_vault.py` into `.obsidian/types.json` (a new copy step; it creates `.obsidian/` if missing and never overwrites an existing file). New **Property types** section in `properties-and-tags.md` documents the id mapping (`text` · `multitext` · `number` · `checkbox` · `date` · `datetime`, plus the `aliases`/`tags` specials) and the four rules that bite: list-anywhere means list-everywhere; `due_time` must stay `text` (no time-only type exists — a date type corrupts `HH:mm`); `pages` is `text` because it holds ranges; and a property is best left **undeclared** when a tool writes scalars but some notes need lists (`company` — declaring it would either break the dashboard server’s list-refusing field writer or flag the dual-role people notes).
- `Reading.base` now installs only with the `resources` module, matching how `Pipeline.base`/`Ledger.base` are gated.

## 2.9.0 — 2026-08-08
`literature` becomes **`source`**, books become a three-layer system (book → chapters → ideas), and `government` joins the stock vocabulary.

- **Vocabulary — `literature` → `source`** (`Resources/Literature/` → `Resources/Sources/`). The old name never matched what the folder holds: in real vaults it fills with internal project briefs and reports as much as external papers, and none of it is "literature." `type: source` is defined as *notes on any material you're consuming or annotating — external article/paper/video/clip or an internal brief you didn't author as a note*, which legitimizes existing filing instead of fighting it. The reading lifecycle (`to-read → reading → done`), schema, and body template carry over unchanged; the property `source:` (origin of a material/task, and now the note or book an idea sprang from) coexists with the type — the type names the note, the property names the origin. Renamed across the triage tree, all references, `validate_vault.py` `TYPES`, and `bootstrap_vault.py`. **Migration:** rename the folder, rewrite `type: literature` → `type: source` in its notes, update the vault `CLAUDE.md`, and repoint the Web Clipper's default folder (manual — browser extension settings). Zettelkasten's "literature notes" keep their historical name in `methodologies.md`, mapped to the new type.
- **Book system — one folder per book.** `Resources/Books/<Title>/<Title>.md` (`type: book`) is a deliberately thin shelf entry: wikilinked `author:` **list** (authors get person notes, so books surface on their backlinks), `year`/`rating`, a dated reading log, and two inline `base` views that assemble the content live. Chapter notes sit beside it; reading ideas do **not** — they're `type: concept` notes in `Resources/Notes/` with `source: "[[Title]]"`, kept outside the book folder so an idea sparked by a book can belong to any project and still roll up in the book's *Ideas sparked* view. Actionable ideas additionally become task notes (Golden Rule 7).
- **New type `chapter`** — `Resources/Books/<Title>/`, one note per chapter or reading session (`<Title> — Ch01 <Name>.md`; the `NN` prefix keeps name-sort correct since Bases documents no per-view row-sort key). Carries **required `book:`** (validator errors without it — new chapter-sanity check), `chapter:` number, `pages:`, and `aliases:` for dictation. Faithful-to-the-author content only (summary, quotes + pages, questions); no per-chapter `status`. Added to `ORPHAN_EXEMPT` — a chapter's inbound path is the book's live view, not static links.
- **Bases — `Embedding & this`** (new section in `bases.md`, verified against the official Bases docs): `![[X.base]]` embeds and inline ` base ` code blocks both resolve the keyword `this` to the **embedding note**, and link properties compare directly to files — `book == this`, `source == this` — which is what makes the book note self-assembling. The ready-made **Reading list** base is rewritten for `source`/`book` (chapters are naturally excluded — they carry no `status`) and now **ships as `assets/bases/Reading.base`** (→ `Maps/Dashboards/`) with *Reading now · To read · Finished* views.
- **New templates in `assets/templates/`: Book, Chapter, Source.** Neither Book nor Literature had a shipped template before — vaults improvised their own copies, which is exactly how template drift happens (plain-text authors, wrong default status). `bootstrap_vault.py` installs all three with the rest.
- **Vocabulary — `government` absorbed as a stock type.** A ministry/commission/regulator is an org in `Work/Business/` with the `business` schema but `type: government` (documented in `note-types.md` → *Organization*, the triage tree, and onboarding). Promoted from a vault-level `--extra-types` extension — vaults using it can drop the flag from validator runs.
- No dashboard-server changes; server stays at `VERSION` 2.8.0 (the dashboard is tasks-only and untouched by any of this).

## 2.8.0 — 2026-08-06
New task status **`in-review`** — the handoff state between "I've done it" and "it's accepted".

- **Vocabulary:** the task lifecycle is now `not-started → in-progress → in-review → done` (plus `on-hold`, `cancelled`). `in-review` means the assignee has delivered and is waiting on someone else's review or feedback; it goes **back to `in-progress`** if changes are requested, **forward to `done`** when approved. Deliberately distinct from `on-hold` (nobody working, nobody owes an answer). Added to `validate_vault.py`'s `STATUSES`, the task template, and every status list in the references.
- **Dashboard:** picks it up automatically in the status-pill menu, the By Status view, and the status column filter; it counts as **open** in tab totals and is **not** exempt from the overdue flag (the work isn't accepted yet). New `.s-in-review` pill styling on a dedicated violet `--stat-review-bg/fg` token pair, defined for both themes.
- **Body log:** setting it writes `- **Submitted for review YYYY-MM-DD.**`.
- **Review rituals** (`retrieval-and-review.md`): `in-review` items sitting over a week now lead the weekly sweep, ahead of stale `in-progress` — someone owes a reply, so they're the cheapest thing to unblock. Name the reviewer and how long it's been sitting.
- **Bases:** the ready-made Open tasks dashboard gains an **In review** view.
- **Saved-state migrations (fixes a silent-hide bug).** A browser's saved status filter lists the values to *show*, so a filter written before `in-review` existed would have hidden every in-review task with no indication why — the same trap 2.7.0's default-visible Due Time column walked into. Saved state now carries a `v` number and runs one-time migrations on load: v1 adds `due_time` to a saved column set, v2 adds `in-review` to a saved status filter. Only ever grants consent for a value the saved state had no opinion about; anything the user deselects afterwards stays deselected.
- Server `VERSION` = 2.8.0. Supersedes 2.7.0 — installing this gets both releases.

## 2.7.0 — 2026-08-06
Three more task fields become editable from the dashboard, and the two due columns say what they are.

- **Priority editing:** the Priority cell is now a menu — `high · normal · low`, plus **Clear priority**. `high` renders in the error colour, `low` muted.
- **Company editing:** the Company cell opens a single-select menu, **In use** (companies already on tasks) above **Organizations** (the remaining `type: business` notes), with a filter box once the list passes eight entries and **Clear company (→ Personal)** at the foot. The value is written as one quoted wikilink and must resolve to an existing note; clearing it drops the task into the **Personal** tab.
- **Due-time editing:** `due_time:` gets the same treatment `due:` already had — a native 24-hour `HH:mm` picker with a **Set** button (no auto-commit on intermediate values), `09:00 / 12:00 / 14:00 / 17:00` shortcuts, and **Clear due time**. Setting a time on a task with no due date is refused on both sides of the wire, matching the existing rule that clearing a due date blanks the time.
- **Column labels:** *Due* → **Due date**, *Time* → **Due Time**. The Due Time column is now visible by default, and the due cell stops appending the time when that column is showing (it would read twice on one row). Sorting by Due Time puts blanks last.
- **New endpoint** `POST /api/field` (`key` ∈ `priority | company | due_time`, `value`) backed by `apply_scalar_change()` — same guarantees as the existing writers: atomic write, one frontmatter line touched, one dated body bullet (`Priority set` / `Company set` / `Due time set`, and their `… cleared` forms), duplicate-key and YAML-list refusals, 409 on an mtime conflict. A missing key is inserted at its position in `Templates/Task Template.md`; `company:` and `due_time:` are written quoted.
- No schema changes; server `VERSION` = 2.7.0.

## 2.6.0 — 2026-07-23
In-tab views + theme control: the dashboard's grouping views move into every tab, the tab bar sticks on scroll, and light/dark becomes a user choice — with a new warm-charcoal dark palette.

- **In-tab view bar** (replaces the *By Project* tab): every task tab now has a second bar under the tabs switching between **Table · By Project · By Status · By Assignee · By Due date** (plus **By Company** on All Tasks). The choice is remembered per tab; a ⌃/⌄ button on the tab bar hides/shows the bar. Grouped views inherit the tab's base set and all active column filters; multi-value groupings (projects, assignees, companies) show a task under each of its groups, with a "none" bucket. Saved pre-2.6 state that had the old By Project tab selected migrates to All Tasks + the By Project view.
- **Theme toggle:** a ◐/☀/☾ button on the tab bar cycles **auto → light → dark** (persisted; auto follows the OS and reacts live to OS changes; resolved before first paint to avoid a flash).
- **New dark palette:** warm charcoal + ivory + terracotta (surfaces `#1F1E1D`–`#45443F`, text `#F0EEE6`, accent `#D97757`) replacing 2.5.1's purple-black M3 dark; status chips re-tuned to match. Light mode unchanged.
- **Sticky tab bar:** the tabs (and view bar) stay pinned to the top while scrolling.
- No endpoint, write-engine, or schema changes; server `VERSION` = 2.6.0.

## 2.5.1 — 2026-07-23
Material 3 visual refresh of the live dashboard — presentation only, no behavioral, schema, or API changes.

- **Material Design 3 UI** (`dashboard_server.py`): the embedded app now uses the M3 baseline token system (seed `#6750A4`) — full **light and dark color schemes** (follows the OS `prefers-color-scheme`, form controls included via `color-scheme`), Roboto-first type scale, and M3 shape/elevation. Components restyled to their M3 equivalents: filled/outlined/text buttons, a pill search field, primary tabs with badge counts, **outlined-card data tables** (row dividers + hover state layers instead of full gridlines), tonal status chips (harmonized green/blue/amber/error containers), M3 menus with elevation, snackbar-style toasts, an error-container offline banner, and visible focus rings. Server `VERSION` bumped to 2.5.1 in lockstep.
- Everything else — endpoints, write engine, validator, references, templates, bases — is byte-identical to 2.5.0.

## 2.5.0 — 2026-07-23
Task accountability + dashboard rework: the `assignee` property lands, the live server becomes the only dashboard — tabbed, filterable, and more editable — and the static HTML dashboard is retired.

- **New canonical task property `assignee`** — who is *responsible* for doing the task (accountability). A quoted-wikilink block list; each entry is a person (`People/`) or organization (`Work/Business/`) note; multiple assignees allowed. Every new task defaults to the vault owner. Canonical position: after `recurrence:`, before `projects:`. Distinct from `people:` (everyone involved/mentioned) and from `owner:` (engagements = deal driver; funds = whose money) — those keep their names and meanings, nothing merged or renamed.
- **Tabbed live dashboard** (`dashboard_server.py`): **All Tasks** · **By Project** · one tab per `company:` value found in tasks (e.g. Swibit, Kapita Research) · **Personal** (tasks whose company is none of the named companies) · **Overview** (the former pipeline / projects / organizations / funds / meetings / people sections). *All Tasks* shows every task attribute as a column (status, priority, due, due_time, days-left, company, projects, people, assignee, recurrence, parent-task, blocked-by, related, source, created, domain) with column show/hide, per-column header filters (value checklists, due-date presets like Overdue/Today/This week/No date, text search on the title) and sorting; filter/column state persists in the browser. *By Project* groups tasks under each project plus a "No project" group — a task linked to multiple projects appears under each.
- **Editing from the dashboard grows:** besides the existing status pills and due-date editor, a task's `projects:` and `assignee:` are now editable via multi-select pickers (people + organizations for assignee) — new **`POST /api/assign`** endpoint. Writes go to note frontmatter as quoted-wikilink block lists, append a dated log bullet in the body, and use the same mtime-conflict detection (HTTP 409) as status/due edits. `GET /api/data` now includes company/assignee and all task attributes.
- **Static dashboard retired:** `scripts/generate_dashboard.py` removed, `Dashboard.html` no longer generated, and the server's post-edit snapshot-rebuild machinery deleted. The `fm`/`links_of` parser is inlined into `dashboard_server.py`, which is now fully self-contained — deploying into a vault means copying just **two files** (`dashboard_server.py` + `Start Dashboard.command`) into `<vault>/Maps/Dashboards/`; the old "must travel as a pair with `generate_dashboard.py`" caveat is obsolete. SKILL.md (cheat-sheet + script notes) and README updated to match.
- **Write safety & hardening (adversarial review):** a 20-agent adversarial review confirmed and fixed 16 defects before packaging — including a write-corruption blocker: inserting a new list key after a block-list anchor could split the anchor's items into the new list (inserts are now block-aware, mirroring the delete path). Also from the review: `/api/assign` targets must resolve to existing notes (values already on the note are tolerated, so a pre-existing broken link never blocks editing the rest of the list); `"` `[` `]` `\` refused in link targets; duplicate frontmatter keys refuse with 422 (the parser honors the *last* occurrence while the rewriter edits the *first* — editing would silently not stick); parser and rewriter now agree on frontmatter fence detection; non-object JSON bodies and malformed `expected_mtime_ns` return clean 400s instead of dropped connections; Host-header pinning blocks DNS-rebinding reads of the vault snapshot; `X-Frame-Options: DENY` + `X-Content-Type-Options: nosniff` on every response. UI hardening: sort controls re-anchor after re-render, stale persisted filter values surface as clearable "· gone" entries, hiding a column retires its filter/sort, auto-refresh defers while an editor is open, and pickers grey out names the server would refuse.
- **Notes:** `validate_vault.py` intentionally unchanged — `assignee` is not validator-enforced this release. Evals untouched.

## 2.4.0 — 2026-07-06
Live dashboard server — owner-requested promotion from vault tooling (same route as 2.3.0's money module): built and battle-tested in the origin vault first, then generalized into the bundle.

- **New `scripts/dashboard_server.py`** (stdlib-only): serves an interactive dashboard at `http://127.0.0.1:8787` — refresh, filters, status pills for tasks / engagements / projects, and due-date editing for tasks / projects. A pill click rewrites `status:` in the note's frontmatter and appends a dated log bullet (Golden Rule 8's close-the-loop, one click); a recurring task marked done advances `due` instead, per the recurrence convention. Due edits set, move, or clear `due:` (clearing blanks a filled `due_time:` and is refused on recurring tasks). Every write triggers a background rebuild of the static `Dashboard.html` via `generate_dashboard.py`, whose `fm`/`links_of` parser it also imports — one parser, both dashboards.
- **Write safety:** atomic writes (same-dir temp + `os.replace`) confined to the `status:`/`due:`/`due_time:` frontmatter lines plus one log bullet, mtime conflict check (HTTP 409), global write lock, 127.0.0.1 bind only, idempotent relaunch via `/api/health` (same vault → reopen browser; different vault → suggests the next port). Adversarially reviewed and tested (unit suite + a browser round-trip) in the origin vault before promotion.
- **New `scripts/Start Dashboard.command`** — four-line macOS double-click launcher for the copy-into-vault deployment (server + generator + launcher into `<vault>/Maps/Dashboards/`, `chmod +x`); runs the server with `--open`, no terminal needed.
- **Docs:** `cli-and-automation.md` gains *Live dashboard server (interactive)* — usage from the skill install, safety properties, the `.command` deploy pattern, upgrade note (vault copies don't self-update), and the Cowork/Chat fallback (hand the user the local setup). SKILL.md's *Running bundled scripts* note and Reference Router row updated; README layout updated. No parser or schema changes — `generate_dashboard.py`, the validator, and all references are byte-identical to 2.3.1.

## 2.3.1 — 2026-07-02
Corrective release — fixes everything found by the four-agent v2.3.0 diagnosis (see the diagnosis report in the dev folder).

- **Money math fixed (was Critical):** partial repayment now uses the **split rule** (repaid portion becomes its own `out+settled` note; the original keeps only the outstanding remainder) — the old "shrink the original" procedure overstated cash by the repaid amount on every engine. Write-offs defined precisely: forgiven receivable → `settled` (cash stays down); dead pledge → **`cancelled`**, a new transaction status meaning *void, excluded from all balance math* (vocabulary, validator, Ledger formula, and dashboard all aligned). Pledge fulfillment = flip in place, never a second note. Amounts declared immutable history.
- **Ledger.base rebuilt:** cancelled-aware signed formula; *Outstanding* split into **Receivables** and **Pledges** views (their old combined Sum was meaningless); group views exclude cancelled; *All transactions* keeps them for audit.
- **Scripts:** dashboard skips cancelled transactions, parses flush-left YAML lists, gains `--no-money`, documents its Funds section, and warns when defaulting to cwd; validator stops false-flagging transactions/funds as orphans and CLAUDE.md as a note, and now errors on non-numeric/negative amounts and invalid directions (warns on missing fund); bootstrap documents the `money` module and links the Ledger from Home.
- **Docs unblocked:** `money` added to every `--modules` string; *Running bundled scripts* note (skill root discovery per mode, read-only-cache reality, python3/PyYAML needs); **compound-capture rule** in the triage section ("decompose first — the tree routes items, not messages") + capture-and-web's "one capture = one note" corrected; zero-fund path + fund seeding in onboarding; **money-vs-engagement seam** defined (transactions record movement; engagements track the deal; `initiative:` may link an engagement).
- **Consistency sweep:** Day-1 no longer imposes daily notes; weekly template unified (lifecycle sweep + focus score) in both copies; journal template added; org/fund/research statuses documented; publish-safety list covers money/engagements; archive wording re-aligned to offer-only; `org`/`company` naming reconciled; "Waiting on…" convention surfaced; README/evals counts corrected; Project template default aligned.
- **Regression protection:** eval 13 (partial repayment + write-off on a live fixture ledger) + `money-vault` fixture; eval 1 de-date-fragilized.

## 2.3.0 — 2026-07-02
Money module (owner-requested promotion from vault-extension design).

- **Two new types:** `fund` (wallet/pot — `owner:` whose money it is vs `custodian:` who holds it) and `transaction` (one money event — `amount`, `currency`, `direction`, `txn`, `fund`, `initiative` earmark, `counterparty`, `settled|outstanding`).
- **Four-way semantics** (`references/money.md`): cash in · cash out · receivable (out+outstanding — owed to the fund's *owner*, not the custodian) · pledge (in+outstanding). Repayments link and settle originals; partials logged, never deleted.
- **Balance verification rule:** after every money capture, recompute cash/receivables/pledges from the transaction notes and restate them; discrepancies are flagged, never silently fixed.
- **Ledger base** (`bases.md` + `assets/bases/Ledger.base`): signed-amount formula, All transactions · Outstanding · By fund · By initiative views with sums; per-counterparty view pattern.
- Money is an optional bootstrap module (`--modules …,money`); triage tree gains the money branch (branches renumbered); dashboard script gains a Funds section (cash/receivables/pledges per fund); templates + assets; validator vocabulary; eval 12 (the 10-donations scenario).
- Deliberately not accounting software: no double-entry, no bank sync, one currency per transaction, sensitive-by-default.

## 2.2.0 — 2026-07-02
Onboarding & shareability (Phase 4 of the development plan) — the edition built to hand to other people.

- **Onboarding interview** (`references/onboarding.md`): five questions about the owner's work, an answers→structure mapping (clients→orgs, deals→engagements, volunteers→groups, properties→areas+engagements, multiple hats = one vault), then scaffold → `CLAUDE.md` from the answers → first real capture in minute ten. First Contact now routes empty vaults here; never scaffold before the interview.
- **`scripts/bootstrap_vault.py`**: deterministic scaffold — module folders (core/work/personal/resources/daily), installs bundled templates + bases, starter Home MOC; refuses vaults that already have a `CLAUDE.md`.
- **`assets/`**: 10 ready-made note templates + 4 `.base` dashboards (Tasks, People, Pipeline, Overview) the bootstrap installs.
- **`scripts/generate_dashboard.py`**: generalized, schema-native standalone HTML dashboard (overdue/open tasks, pipeline by stage, projects, orgs, meetings, people with last-contact) — stdlib-only, schedulable, works on any vault built with this skill.
- **README rewritten recipient-first**: what this is, 3-step start, example phrases, multi-profession framing.
- Eval 11 (cold-start "what can this do?") added.

## 2.1.0 — 2026-07-02
Renumbering release — identical content to 1.8.0. The development plan labeled its milestones **v2.0** (Phases 0–2), **v2.1** (Phase 3), **v2.2** (Phases 4–5), while the skill artifact was versioned incrementally (1.5.0–1.8.0) — two numbering systems, one confusion. From here the skill version tracks the plan milestones: Phases 0–3 complete = **2.1.0**; the shareable edition (Phases 4–5) ships as **2.2.0**. The 1.x series is retired.

## 1.8.0 — 2026-07-02
Organizations, engagements & communication (Phase 3 of the v2 development plan).

- **Org / deal split.** `type: business` now means the **organization entity** (relationship, sector, hq, parent, key people); new **`type: engagement`** models one deal/opportunity — `org:`, `value:`, `owner:`, and the stage in `status:` (`lead → talking → proposal → active → done` + `lost`, `on-hold`). Deliberately CRM-lite. Triage tree, vocabulary, templates, and a ready-made **Engagement pipeline** base added.
- **New `references/communication.md`.** Drafting emails, status updates, minutes, memos, and talking points from vault context: mandatory context pull (person's considerations, commitments both ways, org + engagement state, open tasks); the privacy rule — *considerations shape tone, never appear in the text*; per-type output shapes; after-send loop (log to History, update last-contact, promises become task notes).
- Validator vocabulary extended (engagement type + stage statuses); evals 9 (pipeline filing) and 10 (context-grounded email with privacy) added.

## 1.7.0 — 2026-07-02
Task lifecycle & reviews (Phase 2 of the v2 development plan).

- **New Golden Rule 8 — close the loop on tasks:** statuses move on evidence, in-session; overdue leads every task display; tasks are **never deleted or auto-archived** (archive sweeps offered, confirmation-only). Former rules 8–12 renumbered 9–13.
- **Task lifecycle section** (retrieval-and-review.md): update-on-evidence, overdue-is-a-decision, stale checks, archive policy, and the **recurrence convention** — `recurrence: daily|weekly|monthly|quarterly|yearly`; completion logs the date and advances `due` (default) or spawns a dated instance.
- "What's on my plate" ends with a close-the-loop sweep; weekly review gains a lifecycle sweep.
- **`scripts/validate_vault.py`** bundled (execute, don't read): frontmatter/vocabulary/link/orphan/checkbox/placeholder/overdue checks; wired into Before Finishing, reviews, and cli-and-automation.md.
- **Reviews degrade gracefully** and unused machinery is demoted: daily notes, journaling, and book notes are explicitly optional habits (web clipping stays first-class, per owner decision). MOC rule: dynamic listings are Base embeds, never manual lists.
- `priority` + `recurrence` in the cheat-sheet task block; `recurrence` in the controlled vocabulary; evals 7 (lifecycle) & 8 (recurrence) added.

## 1.6.0 — 2026-07-02
People, groups & relationships (Phase 1 of the v2 development plan).

- **Person schema v2:** optional contact & org fields join the controlled vocabulary — `company`, `job_title`, `department`, `manager`, `email`, `phone`, `location`, `last-contact`, `groups`. Person template rebuilt: About / Working style / **Relationship & considerations** (favors in both directions, sensitivities, open issues — with privacy guidance) / Conversations / Commitments (now both directions: owed and waiting-on).
- **New `group` note type** in `People/`: roster notes for teams, committees, volunteer cohorts, client circles. `members:` on the group, mirrored by `groups:` on each person — queryable both ways.
- **Entity resolution:** Golden Rule 2 extended to aliases + canonical linking; new *Dictated & multilingual capture* section (normalize transcripts, resolve names via aliases, ask on ambiguity, record new variants); triage tree gains the group branch.
- **`last-contact` upkeep:** filing a meeting updates each attendee's `last-contact`.
- **People directory Base v2** in `bases.md`: contact-column directory, by-department, groups view, per-group roster pattern (`file.hasLink`).

## 1.5.0 — 2026-07-02
Infrastructure & hygiene release (Phase 0 of the v2 development plan).

- Version recorded in SKILL.md frontmatter; this changelog now ships inside the skill, with a README.
- New **First Contact** sequence in SKILL.md: find the vault → read its `CLAUDE.md` (owner's source of truth, overrides skill defaults) → else adapt to the existing structure or offer the bootstrap. Vault-specific config explicitly belongs in the vault `CLAUDE.md`, keeping the skill generic and shareable.
- Skill description gains a negative scope (won't fire for coding, non-vault file management, or standalone document work).
- **De-duplicated:** the task-note rule is now stated once as Golden Rule 7 (canonical) and pointed to from everywhere else — previously ~7 near-copies across 6 files. The routing tree and the operating-modes table each live once in SKILL.md; `vault-structure.md` and `cli-and-automation.md` keep only their local specifics.
- Genericized a real-client example filename (`Send Acme MoU draft.md`).
- Documented the `- [[ ]]` template-placeholder gotcha (note-types intro + a new Before-Finishing check).
- Resolved the tag-taxonomy contradiction: the bare type tag is the documented default; `#type/…` nesting is an explicit optional alternative (one style per vault).
- Documented why weeklies live in `Daily/` (all periodic notes in one chronological folder) with a per-vault escape hatch.
- Hedged the docx/pdf skill assumption in publish-and-sharing.
- Added `evals/` (development-only; excluded from the packaged `.skill`): 6 scenario evals with two fixture vaults + a dictated-transcript fixture + 20 trigger queries, following the skill-creator harness format.

## 1.4.0 — 2026-06-30 *(retroactive)*
- Golden Rule 7 generalized: actionable to-dos become task notes **wherever they surface** (any source, not just meetings). Templates stopped modeling bare `- [ ]`; Before-Finishing gate widened to any note with action items.

## 1.3.2 — 2026-06 *(retroactive)*
- Standard "what's on my plate" output: Markdown table `# | Task | Priority | Due | Thread`, priority→due→alpha sort, one-line closing read.

*(Versions before 1.5.0 are reconstructed retroactively; the skill previously carried no version metadata.)*
