# Capture & Web

Getting things **into** the vault quickly, processing them, and pulling in web content cleanly. Capture should be near-frictionless; structure happens later at triage.

## The capture principle

Speed beats structure at capture time. A thought half-captured is lost. So:
- Write to `Inbox/` immediately with minimal frontmatter (`type: fleeting`, `domain: shared`, `created`, `status: needs-triage`).
- Don't stop to pick the perfect folder or links — that's the triage step's job.
- One *item* = one note (a compound capture — meeting + tasks + a payment — yields several; see *Compound captures* in SKILL.md) (keeps them atomic and movable).

Minimum capture note:
```markdown
---
type: fleeting
domain: shared
created: 2026-06-16
status: needs-triage
---
{{raw thought / link / quote}}
```

## Recording a session — filter, do not summarise

**A quick capture is a thought. A session is an hour of them** — a meeting, a long conversation, a
working stretch. For those, the capture principle above still holds, but **how you write the note
changes.**

> **Summarising re-reads and rewrites in other words, so it loses.**
> **Filtering removes the scaffolding and keeps the content as it was said.**

| | |
|---|---|
| **Scaffolding — drop it** | *"let me check"* · *"yes exactly"* · restated explanations · anything read back · false starts |
| **Content — keep it** | what was **decided** · what was **rejected and why** · any figure · any name · doubts · open questions — **in the owner's own words, verbatim wherever the wording carries the meaning** |

**Write it during the session, not after.** An interrupted session then loses nothing, and nothing has
to be reconstructed from memory.

> 🔴 **This is not a style preference. The session does not happen twice** — once it is summarised, the
> wording is gone and cannot be recovered. A summary of *"we can't promise below governorate level"*
> becomes *"discussed geographic limits"*, and the reason the constraint exists is lost with it.

**When to summarise instead:** when you are **producing** something — distilling a book into an atomic
note, drafting a status update, writing a memo. **Summarise what you produce; filter what you record.**

## Quick-capture patterns

- **Plain thought:** drop it in `Inbox/` as above. Give it a short descriptive filename.
- **Into today's note:** if it's a log-type item, append to `Daily/YYYY-MM-DD.md` under `## 💭 Notes & captures`.
- **A task:** if it's a tracked to-do, make a **task note** in `Tasks/` (`type: task`, `status: not-started`, link `source:`/`people:`/`projects:`); a trivial sub-step can stay an inline `- [ ]` in the relevant note. See `note-types.md` → *Task*.
- **A link:** capture the URL now; fetch/clean the content at processing time (below).
- **Claude Code:** `obsidian daily:append content="- captured idea"` or `obsidian create name="Idea — X" content="..."` (see `cli-and-automation.md`).

## Processing the inbox (triage in action)

Run when the user says "process my inbox" or during daily/weekly review. For each item:

1. Read it. Decide its **type** and **domain** (work/personal/shared).
2. Apply the **triage tree** (SKILL.md / `vault-structure.md`) to pick the folder.
3. **Search before you create.** Check whether a target note already exists (the person, project, or topic). If it does, append/merge into it; only create a new note when none exists. This prevents duplicate entities that fragment the vault.
4. Upgrade frontmatter to the full schema for that type (`note-types.md`); set the real `type` and remove `status: needs-triage`.
5. **Link it** — to a MOC and/or related notes. If a source spawned a durable idea, split that idea into an atomic note in `Resources/Notes/`.
6. Rename to a clear, human-readable title (match existing naming; reuse aliases so mentions resolve). **Rename through the app or `obsidian rename`** — a rename via the file tools breaks every inbound link (`vault-structure.md`). With the app closed, either keep the captured name and rename later, or update the inbound links yourself and say so.
7. If genuinely ambiguous, leave in `Inbox/` and ask one targeted question.

Batch tip: group inbox items by likely destination, confirm the plan with the user, then file them together.

## Web content → clean Markdown

LLM-friendly notes need clean text, not page clutter. Two routes depending on environment:

### Defuddle (CLI — when a shell + network are available)

Defuddle extracts the readable article as Markdown, stripping nav/ads (saves tokens vs. a raw fetch). It needs a shell **and** network access, so it's primarily a Claude Code / Desktop tool — it only works in Cowork if the sandbox can reach the URL.

```bash
# install once
npm install -g defuddle
# extract to markdown
defuddle parse <url> --md
# save straight to a source note
defuddle parse <url> --md -o "Resources/Sources/Title.md"
# just metadata
defuddle parse <url> -p title    # or description, author, domain
```
Then add source-note frontmatter (`type: source`, `source`, `url`, `author`, `status: to-read`), write a **summary in your own words**, and link it. Don't paste the entire article as the note — summarize and quote selectively (retrieval + copyright friendliness).

**If Defuddle isn't available** (plain chat, no network, or it errors), have Claude fetch and clean the page directly and produce the same summarized source note. Defuddle is an optimization, not a requirement — never block web capture on it.

> If a URL already ends in `.md`, just fetch it directly — it's already Markdown.

### Obsidian Web Clipper (browser extension)

A browser extension that saves pages straight into the vault using templates. Good for the user's own day-to-day clipping outside Claude. Clip modes: **Article**, **Full page**, **Selection**, **Highlight**.

Template variables: `{{title}} {{url}} {{author}} {{date}} {{content}} {{description}} {{image}} {{published}} {{domain}} {{highlights}}`. Filters pipe together: `{{date|date:"YYYY-MM-DD"}}`, `{{title|safe_name:mac}}`, `{{author|split:", "|join}}`, `{{content|callout:("quote","Clipped article",true)}}`.

> **There is no `default`/fallback filter.** Verified against the official filter list — `date · date_modify · duration · camel · capitalize · decode_uri · kebab · lower · pascal · replace · safe_name · snake · title · trim · uncamel · upper · blockquote · callout · footnote · fragment_link · image · link · list · table · wikilink · calc · length · round · markdown · remove_attr · remove_html · remove_tags · replace_tags · strip_attr · strip_md · strip_tags · first · join · last · map · merge · nth · object · slice · split · template · unique`. An unknown filter name makes the extension reject the whole template with `Unknown filter "…"`, so never invent one; design templates so an empty variable degrades gracefully instead.

Configure the template in the extension (all of this lives on the template, not in General):

| Setting | Value |
|---|---|
| Behavior | Create new note |
| Note name | `{{title\|safe_name:mac}}` — article titles routinely contain `:` `/` `#` `^` `[` `]` `\|`, which break filenames or wikilinks |
| Note location | `Resources/Sources` — vault-relative, no leading slash |

Properties (the **type** column is the Obsidian property type — see `properties-and-tags.md` → *Property types*):

| Type | Name | Value |
|---|---|---|
| Text | `type` | `source` |
| Text | `domain` | `shared` |
| Text | `status` | `to-read` |
| Date | `created` | `{{date\|date:"YYYY-MM-DD"}}` |
| Text | `source` | `{{domain}}` — the publication; **not** the title, and not the URL |
| Text | `url` | `{{url}}` |
| List | `author` | `{{author\|split:", "\|join}}` — add `\|wikilink` only if these authors will get `People/` notes, else every clip leaves unresolved links |
| List | `tags` | `clippings` — a real provenance tag; **never** the `topic/` placeholder, which only works where a human fills it in |

Note content:
```markdown
> Source: [{{domain}}]({{url}})

## Summary (my words)


## Key points / quotes
{{highlights}}


## How it connects
- Related: 
- Ideas spawned: 


---

## Full text
{{content|callout:("quote", "Clipped article", true)}}
```
`{{highlights}}` is what the reader marked; `{{content}}` is the whole article. Prefer highlights alone (retrieval + copyright); when the owner wants the full text too, put it **last**, behind a heading, and fold it with the `callout` filter's `true` — the note then reads as the owner's thinking with the source tucked underneath. Hand-writing `> {{content}}` does **not** work: only the first line gets quoted. Repeating `{{author}}` in the body is redundant with the property.

## A link is an entry point, never a destination

**A URL arrives — a profile, a company page, a paper, a repository, an article. ⛔ Do not open it, skim
it, summarise it and stop.** *That is the shallowest possible use of the single most connected thing
anyone can hand you.*

**Read it properly, then follow what comes out of it.** A link the author wrote inside a post. The
company they work at. The certificate they cite. The paper they reference. The repository behind the
screenshot. **Each of those is another entry point, and it works the same way.**

⛔ **Nobody has to ask for this.** A link handed over is a request to find out, not a request to read
one page.

### Depth is a decision, not a setting

**How far you go is set by what the subject is to the owner — and you decide it yourself, without
asking.**

| The subject is… | How far |
|---|---|
| **The owner themselves** | **Exhaustively.** There is no such thing as too much about the person whose vault this is. Every profile, every post, every repository, every thing they built or wrote. **Stop only when new pages stop producing new facts** |
| **Something they work with closely** — a client, a key colleague, a tool the work depends on | **Until the picture stops changing.** Enough that a question about it next month is already answered |
| **Something mentioned in passing** | **Enough to identify it and place it.** Who they are, where they sit, why they came up. **Then stop** |

**The judgement is yours, made from what the material is worth, not from a number anyone gave you.**

### 🔴 When to stop — and "I have read a lot" is not one of the signals

**Returns stopped.** The last several pages produced nothing you did not already have. **This is the
real signal and it is observable** — count new facts, not pages read.

**Drift.** You are now reading about someone mentioned by someone mentioned by the subject. **Each hop
away costs relevance, and two hops is usually already somewhere else.**

**And the line is the owner's own access — not whether something was published.**

**Anything they can legitimately reach is theirs to read, follow and record.** *A public profile, yes
— and equally their own feed, their own inbox, a client portal they hold credentials for, a paid
subscription they pay for.* **A login is not a wall when you are the one with the account**, and a
vault that refuses to look at what its owner can plainly see is worse at its job for no gain to
anybody.

⛔ **What is not theirs to reach is not reached.** Do not guess or reuse a credential, do not defeat a
control, do not go around a paywall. **That is a rule against breaking in, not against reading** — and
it is the only thing on this page that limits what may be recorded.

⚠️ **And separately from any of that, there is what the tools can physically do.** `crawl.py` sends no
cookies, so an authenticated page comes back empty — **a capability limit, not a permission one.**
**Get it another way:** a browser session, an export, the site's own download, or the owner pasting it.
⛔ **What you must not do is let a page you could not fetch read as a page with nothing on it.**

### 🟢 The cheap way to run one — `scripts/crawl.py`

**A naive crawl pulls every page into the conversation as raw HTML** — nav, cookie banner, footer,
scripts — **and pays for all of it whether the page mattered or not.** *Twenty pages can cost a hundred
thousand tokens to discover that three were relevant.*

```bash
python "<skill-path>/scripts/crawl.py" <url> --depth 2 --max 40 --out <scratch dir>
```

**It fetches, strips each page to readable text, writes it to a file, and prints one line per page** —
depth, word count, how many links it found, the title, and the first hundred characters:

```
#   depth words  links title / url / first words
1   0     1840   37    Murtadha Najem - LinkedIn
                       Data Engineer and Market Researcher at KAPITA Research...
```

> ## **Read the manifest, decide, then open only the files worth opening.**
>
> **Thirty pages cost a few hundred tokens to triage instead of tens of thousands to read** — and the
> ones you never open cost nothing at all. **The pages are on disk either way, so changing your mind
> later is free.**

**Use `defuddle` if it is installed** — the script picks it up automatically and its output is much
cleaner. **Re-running with a bigger `--depth` continues** rather than starting over: every URL is in
`crawl.json`.

⛔ **It fetches HTML and does not run JavaScript**, so a client-rendered page (most social platforms)
comes back nearly empty and is marked **`js`**. **`robots.txt` is honoured**, and a disallowed path is
marked **`robots`** and not fetched. **Both are listed at the end of the run** — *and neither is
evidence that nothing is there.* **Open those another way, or record that you could not.**

### What a crawl has to produce, or it was not worth doing

⛔ **Not a wall of prose.** A crawl that ends in one long summary has thrown away everything that made
it worth running.

1. **Entities become notes** — the person, their employer, each project, each thing they built. Routed
   by the triage tree exactly as anything else is, and **searched for first** so you extend rather than
   duplicate (Golden Rule 2).
2. **Every claim carries where it came from.** A `source:` link on the note, or the URL beside the line.
   **A fact with no source is an assertion, and in six months nobody can tell which was which.**
3. **Facts and inference stay separate.** *"His GitHub shows twelve public repositories"* is a fact.
   *"He is primarily a backend engineer"* is your reading of it — mark it as yours, or leave it out.
   ⛔ **And an opinion about a person is not a crawl result at all** — see *Judgement* in
   `references/note-types.md`.
4. 🔴 **Say what you could not reach.** Dead links, login walls, pages you chose not to follow, a
   profile that turned out to be someone else. **Without that list, absence reads as non-existence** —
   and the owner will act on it.

### The habit, stated once

> **Every link you are given, and every link inside it, is a door.** **Open the ones that lead toward
> what the owner actually needs to know, keep opening them while they are still paying, and stop for a
> reason you can name.**

## After any capture

- It's in a known place (folder or explicitly `Inbox/`).
- Frontmatter is consistent (or flagged `needs-triage`).
- For sources: summarized in your words + linked, not dumped wholesale.

## Bulk import — a whole conversation, transcript or archive at once

**A three-hour working session, an exported chat, a folder of old material.** Everything above still
applies. **What changes is that volume turns small mistakes into a mess nobody can unpick** — so the
order of operations matters as much as the rules.

---

### 🟢 "Record this conversation" — the one sentence, and what it means

> ## ⛔ It does not mean "save the transcript".
>
> **It means: record the *subject*.** The project the conversation was about, its files, the people in
> it, the decisions and why, the numbers with their conditions, the links it followed, what was learned,
> what is still owed. **The transcript is the *index* to all of that — it is not the thing being filed.**

**A session that ends with one note saying *"long conversation about the climate dashboards"* has
recorded nothing.** *Everything that made it worth an hour is still only in the transcript, which is
exactly where it was already.*

🔴 **And it is not only what is inside the conversation.** The conversation **names** things — a
folder, a repository, a URL, a person, a client. **Each of those is followed:** the folder is surveyed,
the repository's commits are read, the link is crawled (*a link is an entry point, never a
destination*), the person is searched for in the vault and extended. **The conversation is the seed;
the import is everything it reaches.**

#### What it runs

**An old Claude Code session is a file.** It is on disk at `~/.claude/projects/<project>/<id>.jsonl`,
often twenty megabytes, and **almost none of it is worth reading** — assistant output and tool results
are ninety-five percent of it and are re-derivable from the files they produced. **The owner's own
messages are not re-derivable, and they are where every decision, correction and reason lives.**

**So the request runs as a chain, and each step hands the next one its input:**

**Inside the conversation itself, nothing needs naming at all:**

```bash
python "<skill-path>/scripts/session.py"          # this session, found from the working directory
```

⚠️ **The last few messages may not be flushed yet**, so the turn that asked for the import is usually
not in the file — **it is in your context instead, so nothing is lost.** 🔴 **And do this even though the
conversation is already in context: a long session has been compacted, and the transcript on disk still
holds what the context window dropped.**

**For a session you are not in:**

```bash
python "<skill-path>/scripts/session.py" --list <part of the folder name>   # 1 · find it
python "<skill-path>/scripts/session.py" "<the .jsonl>"                     # 2 · digest it
python "<skill-path>/scripts/survey.py"  "<the cwd it just printed>"        # 3 · the project's files
```

**Step 2 is the one that pays.** It prints, in this order:

| | |
|---|---|
| **What the session was** | dates, working directories, branch, how many messages |
| 🔴 **The files it *wrote*, ranked by how often** | ***this is what the project is.*** A session's written files are its output; everything else is context it consulted. **The top three usually name the project better than the owner would** |
| **The files it only read** | what it depended on |
| **Every owner message, numbered and clipped** | skim for the turns that mattered |

**And it writes the full text of those messages to a file beside the transcript**, so the expensive
half is on disk rather than in the conversation.

> ## **Measured on a real 24 MB session: the digest costs about five thousand tokens.**
> **The full owner messages are another seven, on disk, read only when you are actually extracting.**
> *Reading the transcript itself would have cost several million.*

⛔ **Do not ask which conversation.** Run `--list` with whatever the owner called it, show the three
that match with their dates and opening lines, and let them point. **A folder name and a first message
identify a session far better than a UUID.**

**Then continue from Step 1 below** — the survey and the digest between them have already answered
*"what kind of material is this"* and *"who and what is named in it"*.

### Step 0 · If it is on disk, survey it — do not read it

**"Record everything you know about this project" is the most expensive request in this skill.** A
folder or a repository read naively pulls vendored libraries, lock files, build output and every
notebook cell into the conversation, **and most of it holds nothing worth a note.**

```bash
python "<skill-path>/scripts/survey.py" "<folder>"
```

**It prints one line per file** — size, kind, and the cheapest strong signal: a heading, a docstring, a
CSV header. **And it puts first the files where a project explains itself** — `README`, `CHANGELOG`,
architecture and methodology docs. **Those are usually the six worth opening out of four hundred.**

> 🔴 **If it is a git repository, read the commit subjects.** *They are the cheapest record of
> decisions that exists, and usually the only one written at the time rather than remembered later.*

⛔ **And it lists what it skipped, with the rule that skipped it** — so a directory you never saw is
never mistaken for a directory with nothing in it.

**Then come back to Step 1 with six files instead of four hundred.**

---

### Step 1 · Read it whole before writing anything

**Do not start at the top and file as you go.** Read enough to answer four questions first:

**What kind of material is this?** *(a decision session · a client meeting · a research discussion · a
handover)* — it decides where things go.
**Who and what is named in it?** People, organisations, projects.
🔴 **What does the vault already hold about any of them?** **Search before extracting, not after** —
a bulk import run against a subject the vault already knows produces a second copy of everything.
⛔ **And search in the vault's own language:** filenames here are English, so an Arabic subject finds
nothing until the words are translated. *`school` finds fourteen notes that `أقساط المدارس` finds none of.*
**And what is the natural unit here** — one meeting, or six weeks of them?

> **Filing as you read produces notes that link to nothing, because the things they should link to have
> not been written yet.**

---

### Step 2 · Interrogate it — the transcript will not hand you structure

**Material records what happened. What you want is what came out of it.** 🔴 **Ask these as separate
sweeps, not as one read** — a single pass looking for everything finds the obvious and misses the rest,
and each question below scans for something with a different shape. *A sweep for numbers finds figures
a general read walks straight past.*

| | |
|---|---|
| **What was decided?** | Not *what was discussed*. A decision has a shape: this, not that |
| 🔴 **What was rejected, and why?** | **The most valuable thing in any long session and the first thing lost.** The reasons a path was closed are what stop it being reopened next year |
| **What changed mid-way?** | Long sessions reverse themselves. **Record the final position *and* what it superseded** — the reasoning lives in the reversal, not the conclusion |
| **What was left open?** | Questions nobody answered. These become notes or tasks, never silence |
| **What figures appeared?** | And **with what conditions** — a number without them is a draft, not a finding. → `type: finding` |
| 🔴 **What was learned?** | **Not what was decided — what turned out to be true.** *"Internal consistency is not correctness."* *"Attribute a figure at the level it was measured."* **A lesson is a `type: concept` note whose title is a claim that could be wrong**, not a topic. **It is the thing most often lost**, because nobody says *"we learned that"* at the time — they say it by changing what they do |
| **Who was named, and in what role?** | |
| **What did the owner commit to?** | Every one becomes a task note — Golden Rule 7 does not relax for volume |

**Keep the owner's words** where the wording carries the meaning. **Filter, do not summarise** — the
section above governs this one.

---

### Step 3 · Write in dependency order — entities, then records, then links

📐 **Entities first.** People, organisations, projects — **resolve each against the vault (Golden Rule 2)
before creating anything.** An entity named forty times is **one** note.

📐 **Then the records** — meetings, decisions, findings — **which can now link correctly on the first
pass** instead of pointing at notes that do not exist yet.

📐 **Then the tasks**, linking `source:` and the projects and people they belong to.

> **Written in this order, nothing has to be revisited. Written in any other order, everything does.**

---

### Step 4 · Place each item by the triage tree — never by the import

⛔ **There is no `Imported/` folder, and the import does not get a home of its own.** Each item goes
where the triage tree in `SKILL.md` sends it, **exactly as if it had been captured on the day.**

> **A batch filed as a batch is a batch nobody ever reads again.** The whole point is that a decision
> from an old conversation surfaces next to today's work — **which only happens if it sits where a
> decision sits.**

**Genuinely unclassifiable items stay in `Inbox/` with `status: needs-triage`** — that is the tree's own
answer, and it is a small residue, not a destination for the bulk of it.

---

### Step 5 · Link three ways, and read the vault before you write

**Every note the import produces gets:**

1. **`source:` → the import's own note** (step 6) — where it came from.
2. **Links to the entities it mentions** — resolved, not invented.
3. 🔴 **Links to what the vault already holds on the same subject.**

**The third is what makes an import join the vault rather than sit beside it** — and it is the one that
requires **searching before writing.** A decision about a project that already has a note **belongs in
that note's orbit**, not in a parallel island of imported material.

**Where the import contradicts something already recorded, do not overwrite.** Add the new detail with
its date and **mark what it supersedes in place** — the same rule that governs any late information.

---

### Step 6 · One source note, and everything points at it

📐 **Create a single `type: source` note for the import itself**, named for the session and recording
what it was, when, and where it came from.

> **This is what makes a bulk import reversible.** Thirty notes with nothing in common cannot be
> reviewed, found or removed as a set — **and an import nobody can undo is one nobody dares run twice.**

**Keep it updated as you go** — what is written, what is left. **A long import gets interrupted, and a
second attempt should continue rather than produce a parallel set of near-identical notes.**

---

### Step 7 · Ask — but collect the questions and ask them once

**Bulk work raises questions. Asking them one at a time makes an import unusable.**

📐 **Gather them during the read, and put them all at the proposal in step 8.**

**What is worth asking:**

- **A routing decision affecting a whole class of items** — *"the client conversations: work notes, or meetings?"* Not each item; the pattern.
- **Two entities that may be one** — *"is 'the Uruk team' the same as `[[Uruk Technology]]`?"*
- 🔴 **Anything that looks personal inside a work session** — **`domain` is decided per note, never inherited from the batch.** When in doubt it does not go in, and you say so.
- **A figure without its conditions** — ask, or write it as a draft that will not be quoted. **Never infer a base size.**

**What is not worth asking:** a spelling, a title, a folder you can pick sensibly. **Choose, say what you
chose, and let them correct it.**

---

### Step 8 · Propose the whole set, then write

⛔ **Show the full list of notes you intend to create — with where each one goes — and wait.** Not the
first three and then the rest.

**Say what you are *not* capturing.** A long session contains a great deal not worth a note; **naming
what you dropped is how a wrong call gets caught while it is still cheap.**

**Then ask the batched questions from step 7, and write only after both are answered.**

> **Forty mediocre notes are worse than none, and the owner is the only one who can tell which is
> which.**

### 🔴 Step 9 · The import is not the deliverable — the mode is

⛔ **Do not end with *"done, 32 notes written."*** That reads as a task closing, and the session then
carries on discussing the project, deciding things, producing numbers, naming people — **and none of it
reaches the vault, in the very conversation that just proved how much was there.**

> ## **An import is not a job you finish. It is the moment this conversation starts writing things down.**

**Say so once, plainly, and then behave that way for the rest of the session:**

> *"That's in the vault now — the project, four tasks, two findings, the people. From here I'll keep
> it current as we go: anything we decide, any number we land on, anyone new. And I'll check there
> before answering rather than scrolling back."*

**What changes from that point, concretely:**

| From now on | |
|---|---|
| **A decision** | goes on the project note **with its reason**, when it is made — not at the end |
| **A number** | becomes a `finding` **with its base and caveat**, the moment it is settled |
| **A new person, client or tool** | gets its note and is linked |
| **Something learned** | becomes a claim-titled `concept` |
| **A commitment** | becomes a task — Golden Rule 7 does not relax after an import |
| 🔴 **A question about this project** | **search the vault first.** It now holds the structured answer, and *this conversation is the thing that will be compacted* |

**That last row is the one that matters most.** *Ten minutes ago the vault knew nothing about this
project; now it is the better source of the two — organised, permanent, and not about to be summarised
away.* **Continuing to answer from the transcript after importing it is strictly worse than reading
what you just wrote.**

⚠️ **And it does not need re-asking.** The owner said it once, about this project, in this session.
**They will not say it again, and they should not have to.**

## The tools already installed are context too, and they are recorded as pointers

**The machine this runs on has other skills on it** - a deck builder, a chart builder, a
transcription pipeline, one per colleague. **Each is a capability the owner already has, and half the
value of a capability is remembering it exists on the day it is needed.** A skill nobody remembers is
a skill nobody uses.

> ### So the vault carries an index of them: what each one is for, and where it lives.

⛔ **Pointers, never content.** *Do not copy a colour token, a template, a threshold or a procedure out
of a skill and into a note.* **C15 - one writer of truth.** The skill is maintained; the copy is not,
and the copy is what gets read six months later when it is wrong.

**One line per skill: the name, what it owns, and the path.** *"`kapita-presentations` - decks, the
design system and the colour tokens - `~/.claude/skills/kapita-presentations/`"* is the whole entry.
**If a reader needs the actual token, the note has told them which file to open.**

### Running it

1. **List `~/.claude/skills/`.** Every folder is a skill.
2. **Read only the `description:` line of each `SKILL.md`** - one head per file, not the file. That is
   what the field is for.
3. **Write one index note**, grouped by what the skills are *for* rather than alphabetically.
4. **Link the entities they name** - a skill about a client links to that client's note; the
   organisation's own skills link to its note.
5. **Date it and say how to refresh it.** Skills change; an index that does not admit it is a snapshot
   will be trusted past its expiry.

**Where it goes:** a `concept` note in the resources folder, not a project. **It describes a standing
capability, not a piece of work.**

⚠️ **And note the gaps you find.** *A rule that lives in the vault's own layer, which the text-producing
skills do not carry, will not reach a draft written through one of them.* **That is worth a line in the
index, because it is the kind of thing that is only discovered twice: once here, and once in front of a
client.**

## Dictated & multilingual capture

Voice-dictated and machine-transcribed input (meeting recaps, voice notes — any language) is a first-class capture source, and it arrives *dirty*: names mangled, fillers everywhere, sometimes mixed languages. Normalize before writing anything to the vault:

1. **Extract, don't transcribe.** Pull the entities and facts (who, what, decisions, action items); drop fillers and false starts. Keep meaningful original-language phrases as quotes where nuance matters.
2. **Resolve every name against the vault** (Golden Rule 2): search People note names *and* `aliases` before writing any name. Transcripts misspell — "sara chen" is probably `[[Sarah Chen]]`. Always link the canonical note name.
3. **Ambiguous match → ask, never guess.** Two plausible people ("which Hussain?") means one quick question to the user, or an explicit flag in the note — not a silent pick.
4. **New variant → record it.** When a transcript teaches you a new spelling of an existing person, add it to that note's `aliases` so the next transcript resolves automatically. ⛔ **Only if it identifies that person alone** — a given name several people share must go on nobody's list, or it will resolve cleanly and silently to the wrong one (`vault-structure.md` → *An alias must be unique*).
5. **Then capture normally** — triage tree, frontmatter, Golden Rule 7 for action items, `last-contact` for attendees.

### Matching names across scripts

**You do not need a rule to see that `آية` and `آيه` are the same name, or that `Najem` and `Najim` are
one person. Read the question and you know.** ⛔ **So do not ask the owner which spelling is "right",
and do not treat a variant as an obstacle.**

**What follows is for the parts of the system that are not you:** `grep`, Obsidian's link resolver, and
any index built over the vault later. **They compare characters, and they are what actually fail.**

**Where a comparison is mechanical, compare normalised forms — and normalise both sides identically.**
A mismatch between the two is invisible: nothing errors, matches just quietly stop happening.

```
1. Unicode NFKC                     ← first, and everything below depends on it
2. strip bidi and zero-width controls
3. strip diacritics (harakat, tanwin, sukun, shadda)
4. strip tatweel (ـ)
5. fold  أ إ آ ٱ → ا · ة → ه · ى → ي · ؤ → و · ئ → ي
6. Arabic-Indic and Persian digits → ASCII
7. lowercase Latin, collapse whitespace
```

> 🔴 **Step 1 is not cosmetic.** An Arabic letter changes shape by position, and text extracted from a
> PDF stores the **drawn shape** rather than the base letter — Unicode numbers every shape separately.
> **`مدير` typed by a person and `ﻣﺪﻳﺮ` extracted from a document share no trigram at all**, and no
> similarity threshold repairs that. People type base letters; documents carry presentation forms.

> ⛔ **Never fold `چ گ پ ڤ`.** They are distinct letters in Iraqi, Persian and Urdu — چاي is not جاي —
> and folding them merges unrelated words.

> ⚠️ **Normalisation does not fix Latin transliteration.** *Najem*, *Najim* and *Najam* stay three
> different strings, because they differ in a vowel letter rather than in a form of the same letter.
> **Only `aliases` solves that** — which is why step 4 matters more than it looks: **seed every spelling
> anyone actually uses.**

**The steps generalise.** The principle is *normalise both sides identically before comparing*; the
specific folds above are Arabic. Add the equivalent for any other script the owner captures in.
