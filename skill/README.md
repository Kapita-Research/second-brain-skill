# obsidian-second-brain

Run an Obsidian vault as a **second brain** through Claude: capture anything by saying it, and get back an organized, linked, queryable memory — tasks that surface when due, people notes that remember every favor and commitment, deals with stages, meetings whose action items never get lost.

## New here? Start in 3 steps

1. **Install:** open the `.skill` file in Claude → **Save skill** → start a **new chat**.
2. Say: **"Set up my second brain — my vault folder is empty."** Claude interviews you about your work (5 questions), scaffolds a vault shaped around it, and files your first real tasks on the spot.
3. Use it by talking:
   - *"I just had a meeting with the ops team, here are the action points…"*
   - *"What's on my plate?"* · *"What's overdue?"*
   - *"Who is Sarah, when did we last talk, what do we owe each other?"*
   - *"We're pitching Acme a retainer, ~30k, I own it — file it."*
   - *"Draft a follow-up email to Omar about the proposal."*
   - *"Log 10 donations for the two initiatives; then I spent 3,000 on the first one — what's our balance?"*

Works for any kind of working life: a company role, an agency with clients, real estate, an NGO with donors and volunteer cohorts — the setup interview shapes the same system to each.

## How it stays yours
The skill is generic; everything about *your* vault lives in your vault's own `CLAUDE.md`, which Claude reads first and treats as overriding truth. **Customize by editing that file** — that is where a company's vocabulary, its people, and where publishing goes all belong.

> **This copy is version `3.0`, built on upstream v2.17.0.** It adds an `Outbox/` as the only way anything leaves the vault, a `type: finding` record for research figures, cross-script name matching, a first session that takes notes rather than configuring a tool, and an organisation layer read beside `CLAUDE.md`. **Every difference from 2.17.0 is the 3.0 entry in `CHANGELOG.md`.** ⛔ **Nothing in the skill itself names a company.**

## Layout (for maintainers)
- `SKILL.md` — loaded on trigger: First Contact, operating loop, golden rules, triage tree.
  **Hard limit: `description` must be ≤ 1024 characters** or the skill is rejected at install. It runs close to the cap, so adding trigger terms means removing others — check before packaging:
  `python3 -c "import yaml,sys;d=yaml.safe_load(open('SKILL.md').read().split('---')[1]);print(len(d['description']))"`
- `references/` — 16 on-demand files (see the Reference Router in SKILL.md).
- `scripts/` — `bootstrap_vault.py` (scaffold) · `validate_vault.py` (hygiene checks) · `sync_last_contact.py` (derive `last-contact:` from meeting notes; dry run by default) · `dashboard_server.py` + a launcher per platform (`Start Dashboard.command` macOS · `Start Dashboard.bat` Windows · `start-dashboard.sh` elsewhere) — live local tabbed dashboard with filtering and in-browser task editing; self-contained, and installed into the vault by the bootstrap.
- `assets/` — templates and `.base` dashboards the bootstrap installs (it installs the live dashboard server into `Maps/Dashboards/` as well).
- `evals/` — development-only tests; excluded from the packaged `.skill`. **22 of them: 18 from upstream, plus 4 covering this fork's own behaviours** (`evals/README.md`).

**Version:** `SKILL.md` frontmatter → `metadata.version` · **History:** `CHANGELOG.md`
