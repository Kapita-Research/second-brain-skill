# Onboarding — first run in a new vault

Use this when First Contact finds **no `CLAUDE.md` and no meaningful structure**. Goal: a vault shaped around *this* person's work, a `CLAUDE.md` that records the choices, and real value on day one. Never scaffold before the interview.

## Step 0 — ask for what they already have, before any question

**Open with this, not with the interview:**

> *"Before anything else — point me at something you already have. A folder of documents, old notes, a
> chat log, a report you wrote. I'll read it and tell you what's in it."*

**Why this comes first.** The interview ends by asking for today's top two or three tasks and then
showing them back — which demonstrates the *mechanism* but not the *value*, because the owner already
knew those tasks. **Reading forty files they already own tells them something they had forgotten.**
Value should come from **their material**, before they have written a line.

**And it builds the corpus.** A vault seeded from what already exists is not empty on day one — which
matters enormously when several people are starting at once and nobody wants to be told to "fill
something in."

### Do it in this order, and stop at step 3

**This is a bulk import, and its three rules apply** — a single source note everything points at, the set proposed before it is written, and the source note kept current so an interruption can be resumed (`capture-and-web.md` → *Bulk import*).

1. **Read a sample, not everything.** Enough to see what kind of material it is.
2. **Produce a small, real set** — a few people, a project or two, two or three sources. **Not forty
   notes.**
3. **Show it and ask before writing the rest.** ⛔ **Forty mediocre notes are worse than an empty
   vault**, and the owner is the only one who can tell which is which.
4. **Say what you could not read** — scanned PDFs, images, unsupported formats. **That list is useful
   in itself**: it is the first honest measure of how much of their archive is actually text.

**If they have nothing to point at, or decline, go straight to the interview.** Nothing below depends
on this step.

## The first session — you are taking their notes, not configuring a tool

> ## **You ask four plain questions. You never announce a setup.**
>
> **The owner should experience the first session as someone sitting down and taking their notes** —
> asking about their week, their work, the people in it — **while the structure gets built underneath,
> unmentioned.**
>
> **Asking is normal; a person taking your notes asks things.** What breaks the session is asking them
> to **describe a system** — and then narrating the one you built.

⛔ **Do not say — at all, in the first session:** *module · type · frontmatter · folder · domain ·
schema · vault structure · "how would you like this organised".*

**Those are your words for your problem.** The owner has a different problem: **they have a week's worth
of things in their head and nowhere good to put them.**

### The four you actually ask

**There are four things you need, and asking for them plainly is fine.** What is not fine is asking
for them **in your words instead of theirs.**

| Ask this | Never this |
|---|---|
| **1 · "What do you do?"** | *"What domains should this vault have?"* |
| **2 · "Who do you deal with most weeks?"** | *"Which people, orgs and groups should I seed?"* |
| **3 · "Walk me through your week — what happened, what's coming?"** | *"What should this vault track?"* |
| **4 · "What's the one thing you'd most want this to do for you?"** | *"What should it answer in week one?"* |

**Both columns buy exactly the same information.** The left one can be answered by anyone; the right
one can only be answered by someone who already knows what this is — **which, on the first day, is
nobody.**

⛔ **And a fifth is never asked at all: what language they write in.** *They are writing in it.*

**Question 3 is the session.** The other three take a minute between them; that one runs as long as they
have things to say, and **it is where the notes get written.** Follow it conversationally — a few
prompts at a time, not a list:

- *"Who did you talk to this week — and about what?"*
- *"What are you supposed to get back to someone about?"*
- *"What's the thing you keep meaning to do and haven't?"*
- *"Did you decide anything recently you'd hate to forget the reason for?"*
- *"What do you usually go looking for and can't find?"*

**Then follow up like a person would** — *"who's that?"*, *"when's that due?"*, *"is that the same
client as the other one?"*

### 🔴 Write as they talk

**Do not collect answers and then build.** As each thing comes up, **it becomes a note** — the project
they named, the person they mentioned, the thing they owe someone, the decision and its reason.

**Route each by the triage tree, exactly as you would on any other day.** The structure that results is
not designed in this session; **it is the residue of what they actually said.**

> **Which is why it fits: it was never chosen, only recorded.**

### Then show them their week, not your architecture

⛔ **Not** *"I've set up Work/Projects, People and Tasks."*
✅ **This instead:**

> *"So — I've written down the Uruk rollout and the two things you owe Sarah on it, a note for Sarah,
> the pricing decision and why you went that way, and three things you said you keep meaning to do.
> That last one — 'find where we said no to the Basra scope' — is the kind of thing you'll be able to
> ask for from now on. Did I get any of it wrong?"*

**The question at the end is about *what they said*, not about *how it is stored*.** They correct a
sentence far more readily than they review a design.

### And only then, the menu — as a summary, never as the opening question

**After they have seen real notes, name what you are now tracking and offer what you are not.** This is
the one moment a list of options helps, because **it is read as "did I understand you?" rather than as
"configure this."**

> *"So I'll keep track of your projects and deadlines, the clients, and your team. I'm not tracking
> money or anything you read — say the word if either of those matters."*

**They can answer that. They could not have answered it before seeing anything.**

⛔ **One offer, one line each, and drop it.** If they say no, it does not get built and it does not get
raised again — **a type is one line the day it is needed.**

### What to do about the things they did not mention

**Whatever did not come up does not get built.** No money folder because they might one day hold money;
no research module because they might one day quote a figure. **A type is one line the day it is
needed** — so an unused branch costs more now than it saves later.

**And the pain point — the answer to *"what do you go looking for and can't find?"* — is the single most
useful thing they will say.** It names what this has to be good at, in their words, **and it belongs in
the vault's `CLAUDE.md` verbatim.**

## Mapping what you heard → structure (map to an existing type where one fits; invent a new one where none does)

| They say… | Model as |
|---|---|
| clients, customers, donors, suppliers, agencies | `type: business` org notes in `Work/Business/` (`relationship:` distinguishes them) |
| deals, listings, grants, sponsorships, campaigns for a client | `type: engagement` (org:, value:, owner:, stage in `status:`) |
| my team, volunteers, committee, crew | `type: group` roster in `People/` + `groups:` on each person |
| properties, assets, fleets | an `Area` per asset class; each purchase/sale/lease in motion = an `engagement` (`org:` links the counterparty — an org note, or a person note for private sellers); the asset's paperwork lives in the engagement/area note |
| donations, funds we hold, who owes us, petty debts | `money` module — `type: fund` + `type: transaction` notes (`money.md`); balances restated at every capture |
| quoting numbers from research — surveys, studies, reports | `findings` module — `type: finding` notes (`findings.md`); a figure is quoted whole or not at all |
| studying, reading, research | `resources` module (`Research/Sources/Books/Notes`); heavy book readers get the per-book folder + chapter system (`note-types.md` → *Book*) |
| ministries, regulators, state bodies | `type: government` org notes in `Work/Business/` (same schema as `business`) |
| journaling, life admin | `personal` module — mark it sensitive by default |

Multiple hats (e.g. agency + real estate + NGO) = **one vault**, one `Work/` tree: hats become **Areas**, their counterparties orgs, their deals engagements, their people/volunteers People + groups. Only split vaults when worlds must never mix.

## Obsidian — raise it once, and say what it costs to skip

**Ask whether they use it. If they do not, tell them what it is and what they would gain — once, in a
few lines, and then never again.**

> ⛔ **"It's optional, everything works without it" is true and useless on its own.** A person who is
> told only that installs nothing, and never finds out what they turned down.

**Say it this way instead: nothing is blocked without it — several things become *asking* instead of
*seeing*.**

| With it | Without it |
|---|---|
| Open a client and **see every note that mentions them**, in a panel, maintained by nobody | Ask Claude, each time |
| **Your tasks as a board**, built from the notes themselves — no second place to update | Ask for the list |
| **Click a link and be there** | Ask for the note |
| **Edit a note's fields** without touching YAML | Edit the text |
| *"This note mentions Uruk and doesn't link it"* — **one click** | Never surfaced |
| A visual map of a corner of the vault | — |

**And what it does not cost them:** it is **free**, it opens the folder **as it is**, it **changes
nothing about the files**, and **they can stop using it any day** — the notes are plain Markdown either
way. **There is no lock-in to weigh.**

**If they install it:** tell them to turn on **Settings → General → Command line interface** — it is off
by default, and it lets search use the live index instead of matching text.

**If they decline, that is a real choice, not a wrong one.** Record it in the vault's `CLAUDE.md` so no
later session asks again, and **make the local dashboard their view instead**
(`cli-and-automation.md`).

## Scaffold — quietly, while they are talking

**The folders are not a step the owner attends. Run the scaffold as soon as the conversation shows what
is needed** — the moment they mention client work, `Work/` exists; the moment they mention money passing
through their hands, it can be offered.

1. **Execute the deterministic scaffold:**
   `python3 "<skill-path>/scripts/bootstrap_vault.py" "<vault>" --modules core,work[,personal,resources,daily,money,findings]`
   (`<skill-path>` = the skill's install root — see *Running bundled scripts* in SKILL.md's Operating Modes.)
   It creates folders, installs `assets/templates/` into `Templates/` and `assets/bases/` into `Maps/Dashboards/`, installs the **live dashboard** (`dashboard_server.py` + this platform's launcher — `Start Dashboard.command` on macOS, `Start Dashboard.bat` on Windows, `start-dashboard.sh` elsewhere) into `Maps/Dashboards/` too, and writes a starter `Maps/Home.md` that links it. It refuses to touch a vault that already has a `CLAUDE.md`. (No shell? Create the same by hand from `vault-structure.md`.)
2. **The notes they produced while talking go where the triage tree sends them** — not into a holding area to be filed later.
3. **Seed the entities they named:** their own person note, their org(s), their group(s) — and, if money came up, their first **fund** (`owner:` whose money, `custodian:` who holds it).
4. **Write the vault `CLAUDE.md`.** Their conventions, languages, sensitivities, **and its two vocabulary lines (`extra-types:` / `extra-statuses:`, empty until something is invented)** — and 🔴 **the pain point in their own words**, because it is the sharpest statement of what this has to be good at.
5. **Then show them their week** (above), and close with one habit only: **tell me things as they happen.** ⛔ **Do not teach the weekly review, the bases, or anything else on day one.** They come up when they are needed.

**Raise Obsidian at the end of this session, not in the middle** — the conversation is about their work,
and a tooling recommendation dropped into it changes the subject.

> **The one exception worth a single sentence: version history.** `git init` is nearly free at scaffold time and **cannot be applied retroactively** — every week without it is a week that can never be reconstructed. Mention it once, in one line, and move on if they aren't interested; the natural moment to revisit is the first "what did I work on?" or the first lost paragraph (`references/version-history.md`).

## Last — offer to make this automatic, once

**Everything so far only works when this skill gets picked up.** It is chosen by matching what the
owner said, and someone who says *"he asked me for the report by Thursday"* — which is exactly how
people talk — **may not reach it at all.** ⛔ **The person this was built for is the least likely to
name it.**

**A few lines in their own `~/.claude/CLAUDE.md` fix that**, because that file is read at the start of
every session in every directory. **It turns a guess into an instruction.**

### Offer it at the very end, after they have seen real notes

> *"One more thing and I'll stop. Right now I only pick this up when it's obvious. I can add a few
> lines to your Claude settings so I'm listening in every conversation, not just this one — you
> mention something about your work, it gets written down without you asking. It's one small file,
> you can read it, and deleting it turns this off. Want me to?"*

⛔ **Only on a yes.** This writes outside their vault and changes every future session — **it is not
yours to assume.**

### What to write

**Append to `~/.claude/CLAUDE.md`. ⛔ Never overwrite it** — other things live there. **If a section
like this already exists, say so and change nothing.**

```markdown
## Every conversation is one of two things

It has prior context in my second brain — or it produces context for it. There is no third kind.
My vault is at `<their vault path>`, read and written through the `obsidian-second-brain` skill.

**Before answering** anything involving a person, a project, a client, a decision, a commitment, a
figure or a date: search the vault first. Do not answer from this conversation alone. Reading one note
is not searching — follow the links, and search for what the notes do not link to.

**Keep doing it as the conversation runs**, not only at the start. A turn to a new client, a new
decision, a new number needs the same look before you answer, and the same record after.

**And record, without being asked.** I will almost never say "note this", and I will not name the
skill. I will just talk about my day: who I dealt with, what someone asked me for, what I decided and
why, what I owe and by when.

**When something like that comes up, load the skill and record it — without announcing that you did.**
Do not ask permission to write a note. Do ask before anything leaves the vault.

Worth recording: a person I dealt with · something I owe or am owed, and by when · a decision and its
reason · a meeting and what came out of it · a client or project named for the first time.

Not worth recording: this conversation's own mechanics, my questions to you, or anything I am only
thinking out loud about.

If I am deep in a task — writing code, debugging, editing a document — do not interrupt it to file a
note. Record it and carry on.

⛔ Anything about me — look it up. Never write `[your name]`, `[your title]`, `[your email]` or any
placeholder, in an email, a bio, a form, anywhere. `People/Me.md` in that folder is my own record and
links out to my projects, the people I deal with and what was decided. Read it, follow the links that
matter, and search the vault for the rest — reading one note is not looking. If it genuinely is not
there, ask me one question. Do not infer it.
```

⛔ **Do not copy the owner's name, title or address into this file.** Whatever you wrote would be a
frozen subset that goes stale, and the vault is the live record — **so the block teaches the search
rather than carrying the answer.**

**Fill in their real vault path.** Everything else is written as *they* would say it, because that file
is theirs and they will read it.

### Then offer the hooks — the half that is enforced rather than asked

**A file of instructions is read and can be drifted past over a long conversation. A hook is run by the
harness**, so it cannot be. **Two of them, in `~/.claude/settings.json`:**

| | |
|---|---|
| **`SessionStart`** | the standing rule, once per conversation |
| **`UserPromptSubmit`** | one short line **on every message**, so it does not decay as the session grows |

**Each is a `command` hook whose entire job is to echo one JSON object:**

```json
{"hooks": {"UserPromptSubmit": [{"hooks": [{"type": "command", "timeout": 5,
  "command": "echo '{\"hookSpecificOutput\": {\"hookEventName\": \"UserPromptSubmit\", \"additionalContext\": \"<the reminder>\"}}'"}]}]}}
```

⛔ **Read `settings.json` and merge** — other settings live there, and replacing the file loses them.
⛔ **A malformed `settings.json` silently disables every setting in it**, so parse it after writing.
⚠️ **A single-quoted `echo` works in both bash and PowerShell**, which matters on Windows.

**Say what it costs:** the per-message line is about forty tokens. **Say what it buys:** the rule holds
in the two-hundredth message of a long session exactly as it did in the first.

### And a third hook, if the vault will hold judgements

**`PreToolUse` on `Read|Grep|Glob|Bash`, running `scripts/guard_judgements.py` from the installed
skill.** Any tool call whose path, pattern or command reaches a judgement note **becomes a permission
prompt the owner answers.**

> 🔴 **This is the only rule in the skill with a mechanism behind it rather than an instruction.**
> **Everything else about judgements is text a model reads and follows. This runs in the harness, and a
> model cannot approve its own way past it.**

**Asking for a judgement deliberately costs one click. Reaching for one while writing something for
somebody else produces a prompt nobody expected — and that surprise is the alarm.**

⛔ **The guard emits a decision only on a match**, so it can never widen a permission for any other call.
⚠️ **And say what it cannot do:** once a judgement is in context — approved, or pasted — nothing un-reads
it. **Do not open one in the same conversation that is writing for someone else.** *That rule belongs to
the person.*

### Then say what it does in one sentence, and stop

> *"Done — from now on, in any conversation, if you mention something worth keeping it gets written
> down. That file is at `~/.claude/CLAUDE.md` if you ever want to change or delete it."*

⛔ **Offer this once.** If they say no, it does not come up again — **a recommendation repeated is a
requirement in disguise.**

## Don'ts

- ⛔ **Don't narrate the machinery.** No `type`, no `frontmatter`, no `module`, no *"how would you like this organised"*. **Those are your words for your problem, not theirs.**
- Don't create folders the conversation didn't justify (empty structure kills adoption — "Day 1 minimal start" in `vault-structure.md`).
- Don't write personal/journal scaffolding unless they brought up personal life themselves.
- Don't overwrite an existing `CLAUDE.md` — that vault isn't yours to reshape (First Contact rule).
- ⛔ **Don't write to `~/.claude/CLAUDE.md` without being told to, and don't overwrite it when you are.** It is outside the vault, it affects every future session, and other things live in it.
