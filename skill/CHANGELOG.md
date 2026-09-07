# Changelog — obsidian-second-brain

Version lives in `SKILL.md` frontmatter (`metadata.version`). Install/upgrade: open the `.skill` file in Claude → **Save skill** (replaces the same-named skill) → start a **new chat**.

## 3.1 — 2026-09-07

**One sentence installs the whole thing, and the skill now knows how it is kept current.**

**The install was eleven steps, five of them outside the skill, and every one of them a place to stop.**
*Most of the people receiving this are not developers* — and a checklist written for a person is a
checklist that gets half done, on the machines least able to tell that it did. **So the checklist is now
addressed to Claude**, and the person says one sentence and answers nothing.

**`install.py` does everything a script defensibly can**, in one run: finds the release and **verifies
its archive by hash before unpacking it**, creates the notes folder somewhere synced, scaffolds it,
installs the skill and both root files with a hash check on every file that lands, merges the three
hooks into `settings.json` and appends the standing block to the global `CLAUDE.md`, then runs the
install check and prints it. ⛔ **It overwrites nothing that belongs to the person** — settings are
merged and backed up, the block is appended only when absent, an existing vault is added to.

> ### And it refuses to ask questions it can answer.
> *Somebody who has not used this yet has no basis for choosing a folder layout*, and being asked turns
> an install into a form. **The one genuinely personal thing — who they are and what they work on — is
> deliberately left to the first conversation**, where it arrives as real notes rather than as answers.

**Four things stay with Claude because a script cannot do them**: the daily update routine, the index of
installed skills, the owner's own person note, and Obsidian. **The installer ends by naming them**, so
they are not forgotten by whoever is driving.

**The skill also learns what an update is** — `cli-and-automation.md` → *Staying current*. **Generic, and
it names no company**: a release is identified by a **version and never by a modification date** (*a date
says something changed, not that what you have is older, and it moves when the same bytes are uploaded
again*); an **unverified or half-synced copy is reported as not ready rather than installed**; the check
is cheap and **silent when nothing changed**, while the install is asked for. 🔴 **That last one is
mechanical rather than polite: a skill replaced while a conversation is open is not re-read by it**, so an
update applied behind somebody's back leaves them on the old copy while everything reports success.

**And the layer carries the specifics**, which is what a layer is for: the folder, the link, the three
commands, and what an update may touch — **the skill folder whole, the layer whole with a `.bak`, the
scaffold additively, and ⛔ never a note or the vault's own `CLAUDE.md`.**

**Touched:** `SKILL.md` (version, router) · `references/cli-and-automation.md` · the fork's
`dist/CHECKLIST.md` (rewritten as a runbook addressed to Claude), `kapita-vault-KAPITA.md` (§9, *Updates*)
and `tools/release.py` (publishes `install.py` unzipped — *somebody with nothing installed cannot run a
script inside an archive they have not unpacked*). **Added:** `tools/install.py`. **Gate:** nine tests,
the ninth running the whole install against a temporary HOME.

**Tested:** a complete install into an empty machine — 96 skill files, a 25-file vault validating 0
errors, four hooks, the standing block — and a second run over the top adding nothing. ⚠️ **The
idempotence was not free:** the first version compared its hooks against `json.dumps()`, which escapes
every quote the command contains, so it matched nothing and would have appended the same four hooks on
every run.

---

## 3.0 — 2026-09-06
**A major number, and the reason is identity rather than size.** This is `obsidian-second-brain`
2.17.0 with a fork's design on top of it: a **one-way exit** from the vault, a **`type: finding`** record
for research figures, a **`type: judgement`** that never leaves under any condition, an **organisation
layer** beside `CLAUDE.md`, **crawling** as the default treatment of any link, **four scripts** that make
importing a project or a past conversation affordable, and a first session that reads as someone taking
notes rather than configuring a tool.

⚠️ **Upstream's own major bump is the reason this one is not `2.18`.** Its `2.1.0` was, in its own
words, *"a renumbering release — identical content to 1.8.0"*, aligning the artifact with a plan's
milestone labels; there is no `2.0.0`, and everything before `1.5.0` is reconstructed retroactively
because the skill carried no version at all. **So the major number there never meant magnitude — and
`2.18` here would have collided with a real upstream release while claiming to be one.** 🔴 **The
frontmatter's `upstream_base` is what actually says where this sits**, and it reads
`obsidian-second-brain 2.17.0`.

**`Outbox/` — the only way anything leaves.** A note is *moved* there, never copied, so one copy stays
authoritative and an exported file cannot silently drift from the note it came from. ⛔ **`domain:
personal` never enters it** — refused by the path rather than by judgement, so the rule holds without a
model deciding anything. **Nothing is moved there on the agent's initiative**; the owner says so, each
time. *"Publish this"* now asks which was meant and offers the folder. **Obsidian Publish is gone from
the skill entirely** — `publish-and-sharing.md` is replaced by `sharing-and-export.md`, and the retired
`publish:` key is swept on upgrade: with nobody subscribed it does nothing at all, **until someone
subscribes and every note carrying it goes live at once**, from a decision no one remembers making.

**`type: finding` — a figure is quoted whole or not at all.** Nine properties: `measure` · `population`
· `base_n` · `sample_n` · `collected` · `describes` · `basis` · `caveat` · `superseded_by`. **`caveat`
is required**; a finding missing any required field is `status: draft` and is never quoted. **`base_n`
is the base of *this* number, not the study's `sample_n`** — the most common way a research figure is
misreported. **`collected` is when fieldwork ran; `describes` is the period the figure is about** — they
differ, and conflating them dates a number wrongly. ⛔ **There is no `value` property:** the number
lives in a sentence with its unit and its subject, because a bare `62` in a column is exactly what gets
pasted into a deck without its base. Ships `Findings.base` (four views, `Templates/` excluded on all of
them), `Finding Template.md`, `references/findings.md`, and a `findings` module in the bootstrap.

**Golden Rule 3 now states the boundary: you may add, you may not redefine.** A new type or a new field
is **free** — `type: lecture`, `died: 1998-04-02` — written with no permission, no migration, and no
argument that the idea is really a project. ⛔ **What is forbidden is taking a word that already means
something**: `status: buried` on a person, or coining `death_date` when `died` is already in use. *A new
name costs nothing; a reused name with a new meaning breaks every view built on the old one, silently.*
**One follow-through:** a new `type:` or `status:` value also goes on the vault `CLAUDE.md`'s
`extra-types:` / `extra-statuses:` line — those two are checked against a fixed list, so an unrecorded
one is reported as an **error** on notes that were written correctly. Ordinary fields need no entry.

**Rule 2a — an organisation layer, read but never written.** A vault belonging to someone in an
organisation carries a second root file (`KAPITA.md`, `ACME.md`, `TEAM.md`) holding the shared rules
everyone there follows, distributed to every member and **replaced wholesale on update**. `CLAUDE.md`
stays the owner's alone, and nothing replaces it. **The organisation's file governs shared vocabulary
and sharing rules; `CLAUDE.md` governs how that person works.** The split is what makes the shared half
updatable: a single file mixing the two cannot be replaced without risking someone's own conventions, so
in practice it never is, and every vault drifts. **`validate_vault.py` exempts every root-level `.md`**
rather than the name `CLAUDE.md` — no note belongs at a vault root, and a convention file's prose
carries illustrative `[[wikilinks]]` that are examples, not references.

**The first session takes their notes; it does not configure a tool.** Four questions, in the owner's
words rather than the system's — *"What do you do?"* · *"Who do you deal with most weeks?"* · *"Walk me
through your week — what happened, what's coming?"* · *"What's the one thing you'd most want this to do
for you?"* — each buying exactly what *"what should this vault track?"* would have bought, from someone
who does not yet know what this is. **Notes are written as they talk**, routed by the triage tree, so
the structure is the residue of what was said rather than something designed in the session. **What
else is available is offered at the end, as a summary to confirm — not at the start, as a question.**
⛔ **A fifth is never asked: what language they write in.** *They are writing in it.* Ahead of all of
it, a step 0 — **ask what material they already have** and seed from it, producing a small real set and
showing it before writing the rest. **Obsidian is raised once, with what skipping it costs**, rather
than as "it's optional", which leaves someone turning down something they cannot see.

**Cross-script capture.** Name matching across scripts runs **`NFKC` first**: text extracted from a PDF
carries the *presentation form* of an Arabic letter and shares no trigram with the same word typed, so
every later step fails without it. Then diacritics, alef and yaa/taa-marbuta variants, tatweel, and
digits. ⛔ **`چ گ پ ڤ` are never folded** — they are distinct letters in Kurdish and Persian, not
variants. **And normalisation cannot fix Latin transliteration** — `Najem` / `Najim` / `Najam` share no
normal form. That is what `aliases` is for, which is also why **an alias must be unique across the
vault**: a shared name registered on one person creates an ambiguity nothing can catch. **Filenames stay
English and every other spelling goes in `aliases`, transliterated rather than translated** — a
translated name is a different name.

**Also**
- **Recording a session: filter, do not summarise.** Scaffolding is dropped; what was decided,
  rejected, doubted or quoted survives **in the speaker's words**. A summary loses the sentence that
  mattered.
- **Bulk import, in eight ordered steps** — entities before records before links, so nothing is written
  twice under two names — with the instruction to ask when a name is ambiguous rather than pick one.
- **Retrieval gains a step 0, query expansion**, and three sub-rungs under step 1 (ask · topical → MOC ·
  time-scoped): one failed literal search is not evidence that nothing is there.
- **Renaming is a three-step action** — rename, rewrite the inbound links, **and keep the old name as an
  alias.**

**The skill could not be reached by the people it was written for.** Every trigger term in the previous
`description` was the tool's own vocabulary — *Obsidian · vault · PKM · MOC · wikilink · frontmatter ·
Dataview · Templater* — so it fired only for someone who already knew what to call it. **The owners this
was designed for say *"he asked me for a report"* and *"I finished a meeting"*, and none of that matched
anything.** The description now leads with what a person actually says, in any language, and states
explicitly that it applies **even when they never say note, vault, or the skill's name**. The vault
vocabulary is kept, second. **Removed to make room:** the money module's terms, `Dataview`, `Templater`
and `Canvas` — the first because a vault without the module never uses them, the rest because they buy
nothing a semantic match does not already cover. **990 characters against the 1024 cap.**

**And the first session now offers to make the skill reachable at all.** A description matches what
someone said; **the person this was built for is the least likely to name it.** At the very end, after
they have seen real notes, the owner is offered a few lines in their own `~/.claude/CLAUDE.md` — read at
the start of every session in every directory — saying that they will talk about their day rather than
ask for a note, and that such things should be recorded without being announced. ⛔ **Only on a yes,
appended and never overwriting, offered once and never raised again.** The block also carries what is
*not* worth recording, and an instruction not to interrupt work in progress to file something.

🔴 **And the findings module was never taught to the validator.** `type: finding` ships with a
template, a view and a reference file — and `finding`, `current`, `superseded` and `draft` were in none
of `validate_vault.py`'s vocabulary sets, so **every finding in a real vault was reported as two errors
on a note that was written exactly as instructed.** It went unseen because the vault it was developed
against had no findings in it; **it surfaced the first time an install check ran against a vault
somebody had actually used** — 94 errors across 47 findings. Added to `TYPES` and `STATUSES`.

⛔ **Anything about the owner is looked up, never guessed and never left as a placeholder.**
`[your name]`, `[your title]`, `[your email]` — in an email, a bio, a form, a README — *a placeholder in
a finished draft is a defect, not a courtesy.* **The owner has a person note in `People/`: it carries
their name and its spellings, title, employer and addresses, and it links out to their projects, the
people they deal with and what was decided.** Read it, follow the links that bear on what is being
written, **and search the vault for the rest — reading one note is not looking.** If a fact genuinely is
not there, **ask one question, and never infer it from an org chart, a table or a filename.**

⚠️ **And the block offered for `~/.claude/CLAUDE.md` deliberately carries no personal details** — not a
name, not a title, not an address. **Anything written there would be a frozen subset that goes stale
while the vault stays live**, so the block teaches the search instead of holding the answer. **It also
means the rule holds in conversations where this skill is never loaded** — which is where the failure
was observed: a draft email signed `[your name]`, in a session that had no reason to reach for a notes
skill.

**And the standing rule now covers reading, not only writing.** *Every conversation is one of two
things: it has prior context in the vault, or it produces context for it — there is no third kind.*
**Before answering anything involving a person, a project, a client, a decision, a commitment, a figure
or a date, the vault is searched first** — not answered from the conversation alone — **and it is
searched again as the conversation turns to something new, not only at its start.**

🟢 **Enforced rather than requested.** The block in `~/.claude/CLAUDE.md` is an instruction, and an
instruction can be drifted past two hundred messages into a session. **So the first session also offers
two hooks in `~/.claude/settings.json`** — `SessionStart` for the rule once, `UserPromptSubmit` for one
short line **on every message** — each a `command` hook that echoes a single JSON object into context.
**The harness runs them, so they cannot decay.** ⛔ **Merged into `settings.json`, never written over
it**, and parsed afterwards, because a malformed settings file silently disables every setting in it.

🔴 **Query expansion covered names and missed languages, and the vault's own naming rule guaranteed
the failure.** Filenames here are English by rule, so a question asked in Arabic searches for something
that by construction is not there. Asked in Arabic for a scraper for Baghdad private-school fees, a real
session searched, found one file, and answered *"there is nothing in the vault about a schools project"*
— while the vault held **fourteen**: the project itself, five findings including *schools almost never
publish fees* on a base of 1,425, and **a task recording the decision to telephone them instead.**

**Step 0 of the retrieval ladder now translates before it expands** — every content word, not only names:
*أقساط* → `fees`/`tuition`, *مدارس أهلية* → `private schools`. **Search the broadest single English word
before the exact phrase.**

⛔ **And "there is nothing in the vault" is now a claim held to the same standard as an answer.** It may
not be said without a search in English, and it must name the words searched. **A wrong "we do not have
this" is the most expensive failure this skill has, because it does not look like one** — the owner does
not go and check, they act on it, and building a scraper for data a recorded finding says is not
published looks like helpfulness the entire time.

**A person is always `domain: personal`, and a person note holds facts rather than a verdict.**
*However you met them — once you know someone they are someone you know, and that does not stop being
true outside the building or after either of you leaves the job.* **`domain` on a person records whose
relationship it is, not which context introduced you**, and it is what keeps a colleague's private
number, a read on their health and the reason they left out of an `Outbox/`. **Filing people as `work`
puts a directory of real people one folder-move away from leaving the vault.** The test for the note
itself: *could you show it to the person it is about?*

**New type — `judgement`, in `Judgements/`.** The owner's own opinion of a person, a tool, a vendor, a
piece of work. **It exists so the person note can stay checkable**: the read goes somewhere rather than
colouring a note meant to be factual. Subjects are not only people.

> ## 🔴 **And a judgement never leaves the vault, in any form, under any condition.**

⛔ **Not quoted, not paraphrased, not softened into a work note, and not as the reason a sentence was
worded the way it was.** ⛔ **No confirmation unlocks it** — asking does not make it allowed, which is
true of nothing else in this skill. **The owner says it in their own voice, or it is not said.**

🟢 **So the protection is at retrieval, not at output.** Whenever what is being written will be read by
anyone but the owner, **`Judgements/` and `type: judgement` are excluded from the search — not read and
set aside, *not read*.** *A judgement you have read has already changed what you would write, and no
rule can un-read it; restraint after reading is not a mechanism, exclusion before reading is.* **Three
independent markers carry it** — the folder, the type, and `domain: personal`, which already bars it
from `Outbox/` under Golden Rule 11 — **so missing one still holds.** The one shipped view without a
type filter now excludes the folder as well, because **a title is a leak too.**

🟢 **And one of the three markers is not an instruction.** `scripts/guard_judgements.py`, wired as a
`PreToolUse` hook on `Read|Grep|Glob|Bash`, **turns any tool call whose path, pattern or command reaches
a judgement into a permission prompt the owner answers.** The harness runs it before the tool does, so
**a model cannot approve its own way past it** — *the only rule in this skill that is enforced rather
than followed.* **Asking for a judgement deliberately costs one click; reaching for one while writing
for somebody else produces a prompt nobody expected, and that surprise is the alarm.** ⛔ **It emits a
decision only on a match**, so it can never widen a permission for any other call, and it exits quietly
on malformed input rather than blocking work.

⚠️ **Its limit is stated where it is installed:** once a judgement is in context — approved, or pasted
— nothing un-reads it. **Do not open one in the same conversation that is writing for someone else.**
*That rule belongs to the person, and no hook replaces it.*

⚠️ **And a judgement ages faster than any fact in the vault** — a read on how someone approaches
problems is true of a person at a moment, so it is dated and read as of that date.

**A link handed over is a request to find out, not a request to read one page.** New section: a URL is
an **entry point, never a destination** — read it properly, then follow what comes out of it: the link
the author wrote inside a post, the employer, the cited certificate, the repository behind the
screenshot. **Each of those works the same way, and nobody has to ask for it.**

**Depth is a decision, not a setting.** The owner themselves is crawled **exhaustively** — there is no
such thing as too much about the person whose vault this is. Something they work with closely, **until
the picture stops changing**. Something mentioned in passing, **enough to identify it and place it**.
*The judgement is made from what the material is worth, not from a number.*

🔴 **Three stopping signals, and "I have read a lot" is not one of them.** **Returns stopped** — count
new facts, not pages. **Drift** — two hops from the subject is usually somewhere else.

**And the line is the owner's own access, not whether something was published.** Anything they can
legitimately reach is theirs to read, follow and record — *a public profile, and equally their own
feed, their own inbox, a portal they hold credentials for.* **A login is not a wall when you are the
one with the account**, and a vault that refuses to look at what its owner can plainly see is worse at
its job for no gain to anybody. ⛔ **What is not theirs to reach is not reached** — no guessed or
reused credential, no defeated control. *That is a rule against breaking in, not against reading.*
⚠️ **Separate from either: what the tools can physically do.** `crawl.py` sends no cookies, so an
authenticated page comes back empty — **a capability limit, not a permission one** — and the answer is
a browser session, an export or a paste. ⛔ **A page that could not be fetched must never read as a page
with nothing on it.**

**And a crawl that ends in one long summary threw away the reason to run it.** Entities become notes,
searched for first so they extend rather than duplicate; **every claim carries where it came from**;
facts and inference stay separate; and 🔴 **what could not be reached is stated** — dead links, login
walls, paths not followed — **because without that list absence reads as non-existence, and the owner
acts on it.**

**Bulk import gains the case it never had — a folder or a repository rather than a conversation — and
a script for it, `scripts/survey.py`.** *"Record everything you know about this project" is the most
expensive request in this skill*; read naively it pulls vendored libraries, lock files and build output
into the conversation for nothing. **The survey prints one line per file** — size, kind, and the
cheapest strong signal available: a heading, a docstring, a CSV header, a commit subject — **and puts
first the files where a project explains itself.** 🔴 **Where it is a git repository the commit subjects
are read**, because *they are the cheapest record of decisions that exists and usually the only one
written at the time rather than remembered later.* ⛔ **What it skipped is listed with the rule that
skipped it**, so a directory nobody saw is never mistaken for a directory with nothing in it.

🟢 **And the case that could not be done at all before — *"record that whole conversation"* — now runs
as one sentence, on `scripts/session.py`.** A past Claude Code session is a file on disk, often twenty
megabytes, and **ninety-five percent of it is assistant output and tool results that are re-derivable
from the files they produced.** **The owner's own messages are not re-derivable**, and they are where
every decision, correction and reason lives. The script prints what the session was, 🔴 **the files it
*wrote*, ranked — which is what the project actually is** — the files it only read, and every owner
message numbered and clipped; **the full text goes to a file beside the transcript.** `--list` finds a
session by a fragment of its folder name and shows dates and opening lines, **because a UUID identifies
nothing to a person.** It also prints the working directory, **which hands `survey.py` its argument** —
so the conversation and the project files come in one chain rather than two requests.

⛔ **And the sentence never means "save the transcript."** It means **record the subject**: the project
the conversation was about, its files, the people in it, the decisions and why, the numbers with their
conditions, what was learned, what is still owed. *A session that ends with one note saying "long
conversation about the dashboards" has recorded nothing — everything that made it worth an hour is
still only in the transcript, which is exactly where it already was.* 🔴 **Nor is it only what is inside
the conversation:** the conversation **names** a folder, a repository, a URL, a person — and **each of
those is followed**, surveyed, crawled or searched for in the vault. **The transcript is the seed; the
import is everything it reaches.**

**With no argument it digests the session you are in**, resolved from the working directory, so *"record
this conversation" needs no name and no UUID.* ⚠️ The last turns may not be flushed to disk yet — they
are in context instead — and 🔴 **it is worth running even mid-conversation, because a long session has
been compacted and the transcript still holds what the context window dropped.**

🔴 **And an import ends by changing the session's posture, not by reporting a count.** *"Done, 32 notes
written"* reads as a task closing — **and the session then carries on deciding things, producing numbers
and naming people, none of which reaches the vault, in the very conversation that just proved how much
was there.** So the last step says it once and then behaves that way: decisions onto the project note
with their reasons **as they are made**, settled numbers as findings, new people as notes, commitments
as tasks. **And questions about the project answered from the vault first** — because ten minutes
earlier it knew nothing and now it is the better of the two sources: *organised, permanent, and not
about to be summarised away.* ⚠️ **The owner said it once, about this project, in this session. They
will not say it again, and they should not have to.**

**Measured on a real 24 MB session: the digest costs about five thousand tokens** and the full owner
messages another seven on disk. *Reading the transcript itself would have cost several million.*

**And the interrogation is now separate sweeps rather than one read** — *a single pass looking for
everything finds the obvious and misses the rest, and each question scans for a different shape.*
🔴 **A sweep was missing entirely: what was learned.** **A lesson is a `type: concept` note whose title
is a claim that could be wrong** — *"Internal consistency is not correctness"*, not *"Data quality"* —
**and it is the thing most often lost, because nobody says "we learned that" at the time; they say it by
changing what they do.** The topic-titled note is the one that never gets read again: it answers
nothing, so nothing brings anyone back to it.

**Searching the vault first is now part of the first step, not an afterthought** — in the vault's own
language, since **a bulk import run against a subject the vault already knows produces a second copy of
everything.**

**Golden Rule 4 gains the other half of linking: a value more than one note could carry is a link, not
a string.** *A university written into five person notes as plain words is five dead strings; written
as `[[University of Baghdad]]` it is one note with five backlinks — and* ***"who else studied there?" is
answered by opening it***, *with no search, no keyword guessing, and nothing missed because one note
spelled it in English and another in Arabic.* **The test is whether you would ever want the list:** a
university, a field of study, an employer, a client, a tool, a certification — yes; a phone number, a
date, a street — no.

🔴 **And a hub note may be empty.** *"I have nothing to write about that university" is not a reason to
skip it* — **a title, a `type` and an `aliases` line are the whole job, because its value is what points
at it rather than what is in it.** ⛔ **No new type is invented for this:** an institution is a
`business` or a `government`, **a discipline or a method is a `concept`**, and the `aliases` line is what
makes the link survive three notes spelling the same thing three ways.

**Why it beats searching, which is the whole point:** *search finds what you thought to ask for, spelled
the way you happened to spell it.* **A link is exact, bidirectional and complete, and it still works when
whoever is asking has forgotten which words were used.**

**The vault now knows what else is installed on the machine, and knows it as pointers.** *A second
brain that records every project and every person, and does not record that its owner already has a
deck builder, a chart builder and a transcription pipeline, is missing the cheapest context there is.*
**Half the value of a capability is remembering it exists on the day it is needed.** The index is one
note, one line per skill, grouped by what they are for, built from each skill's own `description` line
rather than from its contents.

⛔ **And nothing is copied out.** *Not a colour token, not a template, not a threshold* — **C15, one
writer of truth.** The skill is maintained; the copy is not, and the copy is what gets read six months
later when it is wrong. **The note's job is to say which file to open, and then get out of the way.**
⚠️ **Dated on sight, with the refresh procedure written into it**, because an index that does not admit
it is a snapshot will be trusted past its expiry.

**And the release now has a way of arriving.** *Fifteen vaults reading the same words is only true if
the words can reach them*, and until now nothing delivered them: the install check could tell you your
copy of the firm's layer was stale, and then leave you to fix it by hand. **The repository is the
distribution.**

**`MANIFEST.json` is the only file that knows a destination.** Every path maps to one of four rules -
mirrored whole, replaced with a `.bak`, written only if absent, or shipped and installed nowhere - and
`update.py` does exactly what it says and nothing else. ⛔ **An unclaimed file fails the gate**, because
a reference file added in a release and never given a destination is one that quietly reaches nobody.

**The order the installer works in is the point of it.** *Verify the clone against the manifest before
touching anything*, so a half-downloaded release never reaches the skill folder; **mirror the tree,
deleting what the release retired**, because a copy-only update leaves a withdrawn file in place
looking valid; **then verify what landed, file by file.** *A copy that reported success while silently
skipping files has happened on this project before.*

🔴 **Nothing installs by itself.** A daily routine asks for the newest tag, says nothing at all when
there is none, and sends one notification when there is. **The person installs when it suits them** -
and a second `SessionStart` hook mentions a release only after it has sat unclaimed for three days,
comparing two numbers already on disk and never touching the network.

**And the release does not arrive through the repository, because most of the people receiving it are
not developers and have no account there.** *A distribution channel that assumes GitHub assumes wrong
about thirteen of fifteen machines.* **The repository is where the work happens; a shared Drive folder
is where the release lands** - one small file naming the current version, and the archive it names.

**Compared by version, never by modification date.** *A date changes when the same bytes are uploaded
again and does not change when it matters*, and it answers the wrong question: not *"did something
change"* but ⛔ ***"is what I have older than what is there"***. **The archive's hash sits in the same
file**, which makes an unverified copy impossible to install - **including one that is only half
synced**, reported as still syncing rather than installed as if it were whole.

⚪ **And a machine with no Drive app is not stuck.** It is told, *each time a release comes out*, to
either install the app once or download the archive in a browser and hand it over. **The install that
follows is byte-identical** - same manifest, same verification. *The fallback costs the same work every
time instead of once, and that is the only difference.*

**Machines install a tag, not the branch.** *That is what makes a bad release recoverable and a
half-finished commit harmless*, and it is why the six-test gate exists: **two of the six are written
from the receiving end**, which is the only place the interesting failures live.

⚠️ **One of them found its own bug immediately.** Git rewrites `LF` as `CRLF` on checkout on Windows by
default, and the manifest hashes the working tree, **so a perfectly good clone failed verification on
all 178 files.** `.gitattributes` turns the conversion off; verified by cloning with `autocrlf=true`
and re-running the gate inside the clone.

**Touched:** `SKILL.md` (`description` rewritten; **Golden Rules 3, 4 and 11 extended in place — never renumbered**; rules 2a and 2b added) · `references/{capture-and-web,cli-and-automation,community-plugins,note-types,onboarding,properties-and-tags,retrieval-and-review,vault-structure}.md` · `assets/types.json` (50 → 59 properties) · `assets/bases/Overview.base` (its one type-less view now excludes `Judgements/` — a title is a leak too) · `scripts/{bootstrap_vault,validate_vault}.py` · `README.md` (the fork's `tools/check-install.py` gained a twenty-fourth line and `dist/CHECKLIST.md` a tenth step, both for the skills index). **Added:** `references/{findings,sharing-and-export}.md` · `assets/bases/Findings.base` · `assets/templates/Finding Template.md` · `scripts/{guard_judgements,crawl,survey,session}.py`. **Removed:** `references/publish-and-sharing.md`. **Evals 19–22** cover the fork's own behaviours on one shared fixture (`files/fork-vault`); 22 in total.

**Tested — by running, on real material rather than fixtures:**

**The retrieval fix, against the case that exposed it.** The same Arabic request for a Baghdad
private-school fee scraper, in a fresh session, now searches `مدارس|school|أقساط|Education`, opens the
project and three findings, and leads with the recorded number and its base (7 of 1,425 schools, 0.5%,
across the three sources checked) plus the recorded decision that a telephone survey is the only route
to price — while identifying the one source earlier work did not sweep, and saying not to expect it to
change the ratio. **Before the fix the same request answered *"there is nothing in the vault about a
schools project"* while the vault held fourteen notes.**

🔴 **A first install, from the archive, into an empty folder — and it failed.** `bootstrap_vault.py`
wrote `Maps/Home.md` through `pathlib.write_text` with no encoding, **so on Windows it used the ANSI code
page and crashed on the file's own characters**, leaving a half-built vault at the step where somebody
says *"set up my vault"*. **Every read and write in that script is now explicit UTF-8**, and the run was
repeated with the UTF-8 mode forced off: **37 actions, 25 files, and the vault validates 0 errors and 0
warnings.** *It had never failed here because this vault was built by an earlier version, and a scaffold
only runs once.*

**The three new tools, each on live input.** `crawl.py` two hops from a real site, cleaning to disk and
manifesting. `survey.py` over a 171-file project, surfacing the six narrative files. `session.py` over a
**24 MB, 13,000-line transcript — a ~5,000-token digest** naming 54 written files and 140 owner messages,
and separately resolving **the running session from its own working directory** with no name given.

**And the rest of the package.** A 151-note vault with 47 findings validates at 0 errors, 0 warnings;
every `.base` parses and all 27 views across the seven shipped bases carry the `Templates/` exclusion;
`types.json` and `evals.json` parse; all six scripts compile; the validator accepts a root-level
organisation file and still runs clean on a vault that has only `CLAUDE.md`; an off-vocabulary `type`
errors bare and passes with `--extra-types`; the judgement guard was piped six shapes of tool input and
asked on three, stayed silent on two, and exited quietly on malformed input; `description` is 991
characters against the 1024 cap.

🟢 **And the bulk import itself, end to end, on a real project.** One sentence in a working session
took a vault from 164 notes to 196: **two findings, two lessons, four tasks, five new person notes and
thirteen existing ones extended, two organisations, a project and a crawl source** — validator clean at
0 errors, 0 warnings. The parts that had never been checked all held:

* **`base_n` and `sample_n` came out different and correct** — 195 months against 4,603 daily quotes —
  which is the single distinction the findings module exists for. **No `value` field on either.**
* **A caveat did real work rather than hedging:** *"the denominator is 1,320, not 1,300 — since Feb 2023
  Iraq has three official rates."* **That sentence is what stops the figure being misused.**
* **The lessons are claim-titled and cased**, not topics: *"A published number can be an artefact of how
  it was measured"*, with a table of the six that actually happened.
* **Every new person came out `domain: personal`**, and the crawl source records that it read the pages
  **through the owner's own logged-in session** — the access rule applied and stated rather than assumed.
* 🟢 **And the crawl is what found them.** None of the five was named in the conversation: the link led
  to the team pages, and each note carries `source:` back to the crawl and `contact: none` — **so they
  are searchable without entering the follow-up sweeps.** *A link was treated as an entry point, and
  five colleagues who were not in the vault now are.*

**Not tested:** the four fork evals ship as specifications and have not been run; and the `Outbox/` move
has not been exercised on a note with inbound links.
## 2.17.0 — 2026-08-24
Adds one task status — **`delegated-out`**, for a task handed to someone else along with its supervision — and the guard rails a three-reviewer adversarial pass showed it needed. First feature release since 2.16.0.

**The status.** Terminal for the vault owner: excluded from open views and the open count, never flagged overdue, hidden by default in the bundled dashboard. The note stays in `Tasks/` with the new owner in `assignee:` and a dated handover line; a *Delegated out* view holds the record. The gap it fills is real — `done` claims an outcome that hasn't happened and `in-review` says a reply is owed to the owner, so both misreport a completed handover.

**The distinction that keeps it safe: supervision, not who does the work.** Delegating the doing while keeping the follow-up stays `in-progress`/`in-review` with the other person as `assignee:`. `SKILL.md`'s Golden Rule 8 — the always-loaded file — now carries this as a **question to ask** ("do you still need to know whether that lands?") rather than a description to interpret, because the phrasings owners actually use ("I handed it to X", "X is taking it from here") say who does the work and nothing about who reports the outcome.

**Reviewed adversarially before release; three of the findings changed the design.**
- **The overdue exemption was challenged on its own precedent** — 2.8.0 gave `in-review` no overdue exemption because "the work isn't accepted yet", which applies verbatim here. Kept the exemption (it is the point of the status) but the silence is no longer unguarded: `validate_vault.py` now warns when a `delegated-out` task has **no `assignee:`** or still carries a **live `recurrence:`**. Neither warning asks anyone to chase the delegate. A reviewer demonstrated the un-guarded case — no assignee, 236 days past due, zero output from any tool.
- **"Audit trail" was write-only, and now says so.** No ritual raises delegated-out tasks; that is deliberate and stated, rather than implied by a view nothing opens. The integrity warnings are what stands in for a cadence.
- **The lossless alternative was missing and is now documented first.** Reassigning (`assignee:` → them, status unchanged) keeps a task live — it holds its due date, still flags overdue, still surfaces in reviews — and merely drops off an **On my plate** view filtered by `assignee`. `bases.md` ships that view as a copy-paste block. Prefer it whenever the owner still wants to know how the work ends; `delegated-out` is for when they genuinely don't.
- **Recurrence, `due`, reversal and dependents were all undefined** and are now specified: clear `recurrence:` (a repeat cannot advance on a terminal status, so leaving it set silently ends the series), leave `due` in place as the delegate's date, reverse via `in-progress` + `assignee:` back + a second dated line + a fresh `due`, and check `blocked-by:`/`parent-task:` dependents before closing.

**Also fixed, all found by the same pass**
- **`delegated-out` had no colour.** It was added to the vocabulary, the closed lists and the log labels but never to the palette, so its pill rendered pixel-identical to `not-started` — the one status meant to look distinct was the only one without a rule. New `--stat-handed-*` tokens (light + dark) and a `.s-delegated-out` rule; all 15 statuses across the three vocabularies now have one.
- **The documented activity-report grep didn't match `Delegated out`**, so every handover dropped out of "what did I work on" — from the evidence source that same file ranks first. The alternation now covers all seven labels and carries a note to keep it in step with `TASK_LOG_LABEL`.
- **The stray-checkbox sweep would re-import handed-over work.** It offered to promote every unticked `- [ ]`, including the steps inside a `delegated-out` note. Now skips terminal tasks.
- **`vault-structure.md` called a delegated task "finished"** and filed it under the archive sweep — the exact misreport this release exists to prevent. Delegated-out is now explicitly neither finished nor archive fodder.
- **`bases.md` had the divergence backwards**, claiming the teaching listing is "deliberately smaller" than the shipped asset when it carries one view the asset doesn't. Corrected — this is the reconciliation sentence 2.16.3 added, gone stale in the file it was added to.
- **A first-person comment and a private-vault citation were shipping in `dashboard_server.py`** ("off my plate", "vault CLAUDE.md → Tasks") — the class of leak 2.16.3 swept out. Rewritten.
- **Server `VERSION` bumped 2.8.0 → 2.9.0**: the UI gained a status pill and the vocabulary changed, so `/api/health` was misreporting.
- **The bootstrap's upgrade limit is now documented where it bites.** `--dashboard-only` replaces the server and launcher; every other install action is `if not dest.exists()`, so an existing vault's `Tasks.base` and templates are left stale — a vocabulary release therefore needs them hand-patched, or the vault's own dashboard keeps counting the new status as open while the bundled dashboard hides it. Two dashboards, permanently disagreeing. `cli-and-automation.md` carries the warning and the instruction to diff.
- **Three evals added** (16–18): a clean handover routes to `delegated-out` with an assignee and stops being overdue; a handover where the owner still reports on Friday must **not** route there; and "what's on my plate" must not surface delegated tasks. The negative case is the one that matters — past releases added evals alongside new lifecycle states and this one initially didn't.

**Corrections to this release's own earlier notes:** the refactor replaced **five** hard-coded task-pair comparisons in the dashboard (plus one in the validator), not "six sites". And the claim that the live vault "no longer lists the delegated task as overdue" was vacuous — that task has no due date and could never have been flagged; the real evidence is the fresh-vault case, where a task due 2026-01-01 stopped being reported the moment it was delegated out.

**Touched:** `SKILL.md` · `references/{properties-and-tags,retrieval-and-review,note-types,bases,vault-structure,cli-and-automation}.md` · `assets/bases/Tasks.base` · `assets/templates/Task Template.md` · `scripts/{validate_vault.py,dashboard_server.py}` · `evals/evals.json` (source only).

**Tested:** both integrity warnings fire on the exact cases a reviewer showed were silent, and stay quiet on a well-formed handover; overdue suppression still holds; the validator accepts the status with no flags and still rejects `delgated-out`; all 15 statuses have a CSS rule; both `Tasks.base` files parse with the exclusion on every open view; all 23 views across the six bundled dashboards keep the `Templates/` exclusion; `evals.json` parses; fresh-vault bootstrap gives 0 errors / 0 warnings and an overdue task goes quiet on delegation. **Not tested:** the pill's rendered colour in a browser (the CSS rule's existence is verified in the served page, its appearance is not), and the three new evals have not been *run* — they ship as specifications.

---

## 2.16.3 — 2026-08-22
Sweep release. A three-lens review (gaps, inconsistencies, contradictions, run in parallel) found **both** of this package's established failure modes recurring in 2.16.2 — and all three lenses independently landed on the same file. No new features.

- **The claim 2.16.2 existed to kill was still shipping, in the file the router points at.** `markdown-syntax.md` read: *"Use `[[wikilinks]]` for internal vault links (Obsidian auto-updates them on rename)."* That is the exact false mechanism 2.16.2 corrected in `vault-structure.md` and `cli-and-automation.md` — left standing in the one file `SKILL.md`'s Reference Router sends every wikilink question to. A session could legitimately load only the copy saying renames are safe, then rename with the file tools and orphan every inbound link. Corrected, with the rule and a pointer to the evidence. Failure mode #2 — fixed here, not there — landing on the release's own flagship rule.
- **The inbox flow still ordered an unqualified rename.** `capture-and-web.md`'s *Processing the inbox* step 6 says "rename to a clear, human-readable title" — the skill's most-run workflow, commanding the one operation 2.16.2 identified as unsafe outside the app, with no pointer to the rule. It now carries it, including what to do with the app closed.
- **The move-safety guarantee was stated universally and is only known for one configuration.** `vault-structure.md` said moving "never" breaks links with **zero** qualification, and 2.16.2's changelog then claimed those rules were "written to be safe" in untested configurations — they were not; no caveat existed anywhere in the normative text. A vault set to `useMarkdownLinks: true` or a non-default `newLinkFormat` stores the folder *inside* the link, so "the folder was never part of the link" is false there and a move plausibly does break references. The scope is now stated where an agent reads it, with the instruction to check `.obsidian/app.json` first. Failure mode #1 — verified on one instance, stated universally — inside the release whose notes apologised for it three times.
- **`property:set` now carries Golden Rule 8.** The CLI page presented `property:set name="status" value="done"` as the preferred write route with no mention of the mandated dated body bullet or the recurring-task rule, so following the page as written produced exactly the half-updated task the rule forbids — and 2.15.0–2.16.2 raised that route's prominence. The page now pairs the two commands and says a bare `property:set` is insufficient.
- **The shipped `types.json` was leaking one vault's vocabulary into every vault.** It pinned `grading` (an employer-specific grade scale), `office` and `role` — none of which appear anywhere in this skill's documentation — contradicting the rule that vault-specific vocabulary never ships. Removed; 50 properties remain.
- **Two more instances of fix-here-not-there, closed:** the inline base blocks in `assets/templates/Book Template.md` and `note-types.md` lacked the `Templates/` exclusion that `bases.md` calls mandatory, so copying the shipped template produced a non-compliant base. And `bases.md` now names `assets/bases/Tasks.base` as the authoritative copy, since the package shipped two divergent definitions of the same dashboard and changelog claims about "the base this skill ships" were each false against one of them.
- **Verified:** all patched YAML parses; every shell fence still passes `bash -n`; all six shipped bases and all 26 `bases.md` examples retain the exclusion; package extracted and re-checked after building. **Not verified:** vaults using Markdown-style or path-style links (the case this release documents rather than tests — it needs a differently-configured vault); `obsidian rename`'s link rewriting was not exercised, only its syntax confirmed against `obsidian help`.

## 2.16.2 — 2026-08-22
Closes the last open item from the v2.15.0 review: whether the skill's core archive operation quietly breaks links. **It does not — but the reason the docs gave was wrong, and the operation that *does* break links was undocumented.** Settled by controlled test, not inference.

- **The old claim** (`vault-structure.md`): *"Links survive moves — Obsidian auto-updates `[[wikilinks]]` and backlinks, so archiving never breaks references."* The conclusion is right; the mechanism is not. Moving a note with a plain filesystem `mv` left every inbound link resolving (backlinks 2 → 2, unresolved 8 → 8) **and left the referring notes unmodified** — same bytes, same mtime. Nothing was auto-updated. Links survive because a `[[wikilink]]` never encoded the folder: resolution is by **basename**, with any path inside the link treated as a hint. Even a deliberately path-qualified `[[folder/sub/Note]]` kept resolving after the file moved out of that folder.
- **Renaming is the unguarded case.** Basename resolution has nothing to fall back on when the basename changes: an external rename took `unresolved` from 8 to 10 (one entry per link form) and left the renamed note with zero backlinks. The *Automatically update internal links* setting does not help — it fires when the app performs the rename, not when it notices one. Documented as a rule: rename through Obsidian or `obsidian rename`; with the app closed, defer it or update every inbound link by hand and say so. This matters because the skill's own naming conventions make renames routine — retitling a note, correcting a person's name, fixing a task title.
- **`obsidian move` and `obsidian rename` were absent from every document** while `obsidian help` has offered both all along. Now in the CLI basics, with the asymmetry stated on the spot: rename needs the app, move never did.
- **Basename resolution has a collision edge**, previously unmentioned: two notes sharing a basename make a short link ambiguous, so moving a note in beside a same-named one can silently re-point existing links at the wrong file. Check for a clash before moving.
- **Also:** `obsidian unresolved total` was observed disagreeing with `obsidian unresolved`'s own list (9 vs 10) for a few seconds after an external change. Noted, with the advice to read twice before reporting a link-health number.
- **Verified** in the live vault with disposable notes covering both link forms, then removed; link health returned to its 8-unresolved baseline and nothing was committed. Settings confirmed for that vault: wikilinks, shortest-form links, `alwaysUpdateLinks: true`. **Not verified:** behaviour under a non-default `newLinkFormat` (absolute/relative paths) or `useMarkdownLinks: true`, where a move plausibly *would* break links — **those rules carried no such caveat — corrected in 2.16.3**, which puts the configuration limit into the normative text where an agent will actually read it.

## 2.16.1 — 2026-08-22
Verification patch on 2.16.0, which was built but never installed. A five-agent adversarial pass over the built package — empirical claims, collateral regression, and the packaging/delivery lens the previous review had omitted entirely — found that **2.16.0's headline fix never reached this file's own examples**, and that two of its three "we corrected a false claim" sentences were themselves false. No feature changes.

- **`bases.md` broke its own new rule, 26 blocks to 1.** 2.16.0 added the `Templates/` exclusion to the six shipped `assets/bases/*.base` and wrote the rule into that file's prose and pre-delivery checklist — while the **26 ready-made base definitions in the same file**, the ones anyone actually copies, carried none of it. Including the Ledger example: verbatim the block whose real-world equivalent was reporting the transaction template *as a transaction*. Every deliverable example now carries the clause (the *Needs Triage* view restructured so the exclusion sits in an outer `and:` beside its `or:`, not inside it); the and/or/not syntax demo is deliberately left bare, and the checklist now says so.
- **"Every format returns the view's columns only, plus `path`" — wrong about `path`.** Only `json` emits it; `csv`, `tsv` and `md` return the configured columns and nothing else. And the example asserting a named view "carries no `status` and no `priority`" was true of one vault's live base and **false of the base this skill ships**, whose `Overdue` view does list `priority`. Both replaced with the rule that actually holds — read the view's `order:`, because views differ between vaults. The same over-generalisation was removed from `retrieval-and-review.md`.
- **The snapshot script made its own push unreachable.** The script printed under *Scheduled job* ended `[ -z "$STATUS" ] && exit 0` on a quiet hour — so the push block from *Pushing off-machine automatically*, which is meant to be appended to it, could never run. That is precisely the design the surrounding prose criticises ("the push is not conditional on this run having committed"). The commit is now wrapped in `if … fi` with a marked insertion point for the push. Also: the weekly `gc` was `[ … ] && …` as the final line, making every non-Sunday run exit `1` — noise in the exit status this release had just told readers to interpret.
- **Residues 2.16.0 claimed to have cleared:** `template="Task"` survived in the task-notes callout (no such template ships — all are `<Type> Template.md`) and `silent` survived in `capture-and-web.md`. Both fixed; the 2.16.0 entry now admits its sweep was incomplete.
- **Verified:** all 26 patched examples parse; **31 views across the owner's 7 live dashboards return zero `Templates/` rows** — 2.16.0 checked default views only and therefore under-reported its own effect, having missed a view that was returning two template rows; `csv`/`tsv`/`md`/`json` column sets observed directly; the corrected script passes `bash -n` with its exit status checked on a non-Sunday. **Not verified:** `base:create`, `delete permanent`, and `template=` name resolution (all write); the Full Disk Access grant itself (needs a system permission change); the assembled script under a live permission revocation.

## 2.16.0 — 2026-08-22
**Supersedes 2.15.0, which was built but never installed.** A 12-agent adversarial review of that build (five independent lenses, per-lens refutation, orchestrated synthesis, completeness critic) found three defects in its own new text and two pre-existing faults that matter more than anything it fixed. This release carries 2.15.0's `base:` documentation forward with those corrections, plus two hard-won operational findings from a live vault. **Not docs-only** — the six shipped bases change.

- **`Templates/` was being counted as real data, in every shipped base.** A template is a note with real frontmatter, so Obsidian aggregates it: the ledger reported the transaction template *as a transaction*, the pipeline showed the engagement template as a live deal, the task dashboard was off by one. No shipped base excluded it. All 22 filter blocks across the six `assets/bases/*.base` now carry `not: [file.inFolder("Templates")]`, and `bases.md` documents the rule with the reason it hides: a view filtered on `due` or `status` excludes the undated, statusless template *by accident*, so the leak appears on the broad views while the narrow ones look clean — which is exactly why it survived this long. The pre-delivery checklist now says to count filter blocks against exclusions.
- **macOS: the snapshot job fails silently without Full Disk Access.** `~/Desktop`, `~/Documents`, `~/Downloads` and iCloud Drive are TCC-restricted, and launchd runs the script through `/bin/bash`, which has no access by default — so a vault in any of them fails every run with `Operation not permitted`. Nothing looks wrong: the error goes to the plist's `StandardErrorPath`, the snapshot log stays *empty*, and — because the shipped script inlined `[ -z "$(git status --porcelain)" ] && exit 0` — git's failure read as "nothing changed" and the script exited **0**. Loaded job, exit status 0, last log line a successful commit from before the break. Observed in the field: **six days** with nothing anywhere saying so. `version-history.md` now documents the grant, hardens the shipped script to check git's exit code rather than inlining it, and **corrects its own troubleshooting line**, which said an old snapshot means the job isn't running — the likelier case is a job that runs on schedule and fails every time.
- **Automatic off-machine push, documented properly.** The privacy rule already gated the decision; the mechanics that make it reliable unattended were missing. Added: the push gates on *"is the branch ahead of upstream"* rather than on this run having committed, so every run retries a failed push instead of leaving the remote permanently behind while the log looks healthy; `GIT_TERMINAL_PROMPT=0` so an unattended credential prompt fails loudly instead of hanging invisibly; keychain credentials via the `osxkeychain` helper in `/usr/bin`, which works inside launchd's minimal `PATH` and keeps tokens out of the script; and failure logged *with the count still local*.
- **Corrected in 2.15.0's own new text.** (a) It claimed a `base:query`/dashboard-server disagreement "means one of the two has drifted" — false, and guaranteed to fire: the server skips `Templates/` and `.trash` and never reads the `.base` files at all, so the two differ by construction. Now states both differences and tells you to discount them. (b) It said `format=json` returns "full property objects" — every format returns **the view's configured columns only**, the properties named in the view's `order:`, with lists comma-joined and unsafe to write back. The headline example was moved to `Open — by status`, which carries the full set a task table needs. *(Corrected again in 2.16.1: only `json` adds a `path` key, and which columns a given view carries varies per vault — 2.16.0 asserted both too generally.)* (c) The bracket property search it introduced fails *silently* — a wrong separator or a typo'd property both return a clean `0`. Trading a loud failure for a silent one is worse; the doc now requires calibrating the syntax on a value known to exist before reporting "none".
- **Reachability.** `retrieval-and-review.md` was the file routed to for task retrieval and still said the answer was to "read `Tasks.base`" — which yields the filter definition, not the rows. It now distinguishes the two and names the CLI path, with the reverse pointer where the mandated table is defined.
- **Also:** the enablement instruction needed a second step (`Set up CLI to work in the terminal → Register` puts `obsidian` on `PATH`; the toggle alone leaves `command not found`). Errors print `Error:` on **stdout** and still exit `0`, and unknown parameters are dropped in silence — so branch on output text, never `$?`. `base:query` discards `groupBy`, which matters when the grouping key isn't also a column. `base:create` has no `template=`, so governed types must go through `create … template="<Type> Template"` or their required frontmatter is simply absent. Whole-vault queries need scoping where a vault separates streams by `company:`/`domain:` — and the view *named* for the split often omits the key from `order:`. Removed `--copy` and `silent`, which do not exist, and corrected template names to match `assets/templates/` (**incompletely — finished in 2.16.1**); documented `delete permanent`, `obsidian vault`/`vaults`, and the dashboard server's `/api/health` and `/api/data`. SKILL.md's Claude Code row now states the two capability states and the degradation rule. Note count corrected to 343.

## 2.15.0 — 2026-08-22
Teaches the CLI reference the **`base:` commands** — the read path for a vault whose whole dashboard layer is Bases — and fixes a property-search example that never worked.

- **`base:query` was missing entirely.** The CLI section documented `read`, `append`, `search`, `daily:*`, `property:set`, `tasks`, `backlinks` and `tags`, but none of the three `base:` commands the CLI actually ships. That was the wrong gap to have: this skill pushes Bases as the dashboard layer (`Tasks.base`, `Pipeline.base`, `Ledger.base`, `Reading.base`, `People.base`, `Overview.base`), and reading a `.base` off disk yields the *filter definition* only — so an agent had to re-implement the owner's filters and hope it matched what they see on screen. `cli-and-automation.md` gains a *Querying bases* subsection: `base:query` with all five formats, `file=` vs `path=`, the default-view behaviour when `view=` is omitted, and `bases` for discovery. `bases.md` gains a short pointer so anyone arriving from the Bases side finds it, with the Cowork/Chat caveat that there is no CLI to call.
- **The shipped property-search example was broken.** `obsidian search query="status: needs-triage" limit=20` does not search a property — it exits with `Error: Operator "status" not recognized`. Anyone who copied the line got an error, and the one command an agent reaches for first (find the untriaged notes) was the one that failed. Corrected to Obsidian's bracket form, `query='["status":"needs-triage"]'`, and given its own *Property search syntax* subsection since the form isn't guessable. Also noted there: `search:context` prints a line once **per match**, so a line matching twice appears twice.
- **`base:views` is a trap, and now says so.** It reads only the *active* file and accepts **no parameters** — `file=`/`path=` are silently ignored, so non-interactively it always fails with `Active file is not a base file: <whatever the owner has open>`. The documented way to discover view names is a deliberate wrong `view=`, whose error lists every view in the file; grepping `name:` in the `.base` also works.
- **`base:query` as a cross-check on `dashboard_server.py`.** The bundled server re-implements Bases filtering in Python and must keep working with Obsidian closed, so it isn't replaceable — but where the app *is* open, the two can now be compared. *(This entry originally presented a disagreement as evidence of drift — wrong, and retracted in 2.16.0: the two differ by construction.)*
- **Verified against a live 343-note vault** (Obsidian 1.13.7, macOS): `base:query` in `md`/`json`/`paths` across `Tasks.base` and `Pipeline.base`, `file=` with the `.base` extension, omitted `view=`, the wrong-view error listing, `bases`, the corrected bracket search (106 hits on `["type":"task"]`), `search:context`, `backlinks`, `tags`, `aliases`. **`base:create` is documented from `obsidian help` and was not exercised** — it writes a note, and this was a live vault. Docs only: no schema, asset, script or note-type changes; server `VERSION` stays 2.8.0.

## 2.14.1 — 2026-08-18
Self-review patch on 2.14.0 (contradictions-and-gaps pass) — no new features, no schema or asset changes.

- **Untrack step for repos that already track the dashboard.** The 2.14.0 `.gitignore` lines only protect repos that adopt them before the dashboard is first committed — a `.gitignore` entry never untracks an already-committed file, so for every vault whose git predates them (including the vault this skill was built in) the exclusions silently did nothing. `version-history.md` now ships the one-time `git rm --cached --ignore-unmatch` step, and `cli-and-automation.md` points at it.
- **`--dashboard-dir` hardening.** An absolute path crashed with a raw traceback (the action-label `relative_to` call) and a `..` path installed files outside the vault without comment; both are now refused with a plain message. Trailing slashes are normalized, and if the vault path can't be baked into a launcher (unexpected launcher layout) the run fails loudly instead of installing a launcher that can't start.
- **Wording.** The scaffold's docstring no longer claims unqualified determinism (it's deterministic per platform + flags — the launcher installed matches the OS); the manual-copy block is labeled as the macOS pair with a pointer to the platform table; `vault-structure.md` stops calling the Linux launcher "double-click"; and 2.14.0's changelog line about `--dashboard-only` and Home.md is reworded — 2.13.0 never edited Home.md, the 2.14.0 change *added* the paste-hint.
- Known and accepted: the `.bak` keeps one generation (each upgrade overwrites it); dry-run doesn't preview the `.bak`; the `.bat` remains unverified on real Windows; some Linux file managers won't launch `.sh` on double-click (the docs already say "else `./start-dashboard.sh`"). Server `VERSION` stays 2.8.0.

## 2.14.0 — 2026-08-18
Hardens 2.13.0's scaffold-installed dashboard: a launcher on **every** platform, an edited copy is never silently lost, and the vault's git history stops swallowing a ~100 KB program.

- **Launchers for Windows and Linux.** 2.13.0 shipped the dashboard everywhere but the double-click launcher only on macOS, which left everyone else with the thing the launcher exists to avoid — typing a path. New assets `scripts/Start Dashboard.bat` (Windows; `py -3`, falling back to `python`, and it pauses so an error stays readable) and `scripts/start-dashboard.sh` (Linux/BSD, mode 755). The bootstrap installs the launcher for the platform it runs on and words `Maps/Home.md` to match — *double-click* on macOS/Windows, *run* elsewhere. Launchers for other platforms coexist in the folder, so a synced vault collects them by running `--dashboard-only` once per machine.
- **A copy you edited is kept, not overwritten.** `dashboard_server.py` is a single hackable file, and 2.13.0 replaced it whenever the bytes differed — silently discarding a local change. Now the existing file is copied to `<name>.bak` first and the run prints `kept your copy as …`. Applies to the launcher too.
- **`.gitignore` for the vault's git module.** `version-history.md` already excluded `.obsidian/plugins/` as "third-party code that churns on update"; the dashboard is the same thing installed one folder over, and nothing excluded it — so every skill upgrade would commit another ~100 KB copy into a repository whose whole selling point is that 11 snapshots of a 288-note vault fit in 1.9 MB. The four launcher/server paths and `Maps/Dashboards/*.bak` are now in the documented ignore list, with the reasoning spelled out.
- **`--dashboard-dir REL`** — install the dashboard outside `Maps/Dashboards` (a vault whose structure doesn't use `Maps/`). The server can only infer its vault from `<vault>/Maps/Dashboards`, so the launcher gets the vault path baked in as a **relative** path — moving the vault doesn't break it.
- **`--dashboard-only` now prints the Home.md line to paste.** 2.13.0 installed silently, leaving upgraded vaults with no link to the dashboard; an existing `Maps/Home.md` is the owner's note, so the run prints the link line rather than editing it.
- Verified on macOS: fresh scaffold, no-op re-run, edited-copy preservation (both files), custom `--dashboard-dir` served the right vault through the baked path, `start-dashboard.sh` launched the server end-to-end; the Windows and Linux install paths were exercised with the platform faked, and the `.bat`'s baked path checked (`"..\.."`). **The `.bat` itself has not been run on Windows** — it is four lines of `cmd`, but it is unverified. Validator and `sync_last_contact.py` are unaffected (both walk `*.md` only). Server `VERSION` stays 2.8.0; no schema or note-type changes.

## 2.13.0 — 2026-08-18
The live dashboard is now **installed by the scaffold**, so a new vault has it from minute one instead of after a manual copy nobody knew to ask for.

- **The gap.** Since 2.5.0 the dashboard has been a two-file deploy — copy `dashboard_server.py` and `Start Dashboard.command` into `<vault>/Maps/Dashboards/`, `chmod +x` the launcher — documented in `cli-and-automation.md` and nowhere else in the flow. `bootstrap_vault.py` installed templates, bases and `types.json` but not those two, so every new owner ended up with a dashboard they'd never see unless the conversation happened to reach that reference. The whole point of the `.command` launcher is that a non-technical owner never types a path; requiring a manual install first defeats it.
- **`bootstrap_vault.py` installs it.** Both files are copied into `Maps/Dashboards/` (the launcher marked `0755`), and the starter `Maps/Home.md` gains a *Live dashboard* line pointing at it. The server already resolves its vault two levels up when it lives there, so the installed copy needs no argument.
- **Kept current, deliberately.** These two are program code, not user content — so they are the **one thing the scaffold replaces**, and only when the installed bytes differ from the skill's. Everything else keeps the never-overwrite rule. That makes a re-run the answer to "vault copies don't self-update".
- **`--dashboard-only`** — the upgrade path for a vault that already exists: installs/refreshes just those two files, scaffolds nothing, and doesn't trip the `CLAUDE.md` guard (no `--force` needed, so an established vault is never re-scaffolded to get a dashboard update). **`--no-dashboard`** opts out; the two flags together are refused.
- **Platform honesty.** The `.command` launcher is macOS-only and is only installed there; elsewhere the scaffold prints (and Home.md shows) the `python3 … --open` invocation instead. `cli-and-automation.md` now says this plainly rather than presenting the mac pattern as the pattern.
- Docs updated where the scaffold is described: `onboarding.md` (step 1), `vault-structure.md`, `README.md`. No schema, note-type, or dashboard-server changes (server `VERSION` stays 2.8.0); nothing to migrate, and evals are unchanged.

## 2.12.0 — 2026-08-16
New reference **`version-history.md`** (git) and a new **Activity reporting** capability — the vault can finally answer *"what did I work on?"* honestly.

- **The gap.** The vault records when a note was **created** and nothing about when it was **revised**. Asked to reconstruct three weeks of work, the only edit signal available was filesystem **mtime** — which keeps just the latest touch (a note revised eight times looks like one touched once), is bumped by Obsidian property rewrites, dashboard writes and the agent's own bulk edits, and is destroyed by any copy or move. Answering from it produces confident fiction. Found in real use: a block of 24 task notes sharing one timestamp was a property migration, and 33 person notes sharing another was a bulk rewrite — neither was a work session, and both would have been reported as activity.
- **`retrieval-and-review.md` → *Activity reporting*.** Ranks the four evidence sources: **dated status bullets in task bodies** first (they record accomplishment, deliberately written — this is what Golden Rule 8 exists to produce), then `created:` frontmatter, then git history where it exists, and mtime last with its traps named. Includes the shell recipes (whitespace-safe `created:` extraction, status-bullet counting, the git one-liner), the reminder to filter `Templates/` whose `created:` is a literal `{{date:…}}`, and the presentation rule: **group by initiative, never by folder** — "39 notes in People/" is not something anyone can say to a manager. Closes by requiring the gaps be stated: an empty `Daily/` means no narrative record, and work done outside the vault is invisible.
- **`version-history.md` — the optional git module.** Setup (`git init`, repo-local identity, `core.quotepath false` so non-ASCII filenames print readably), the `.gitignore` with the reasoning per entry (`Attachments/` is binary and diffs to nothing; `workspace.json` churns on every pane drag; keep `types.json` and the enabled-plugin list), and verification that the exclusions actually applied before declaring success.
- **Automation is the whole module.** A one-commit repository is worthless, and manual commits don't survive a real week. Ships the snapshot-script pattern (commits **only when something changed**, so no empty noise; weekly `gc`), launchd and cron wiring, and the launchd trap of a minimal `PATH` — call `/usr/bin/git`, never bare `git`. Documents the **Obsidian Git plugin's decisive limitation**: its timer runs only while Obsidian is open, so a long interval may fire rarely or never while the owner believes they have history. Long interval → use the scheduled job. Default recommendation: **hourly, scheduled**.
- **Framed for non-technical owners**, who are most vault owners. The commit-as-photograph model, and straight answers to the three questions they actually ask — does each snapshot copy everything (no: content-addressed, compressed, later repacked as deltas — **measured on a real 288-note vault, 11 snapshots = 1.9 MB, less than one unpacked**), is anything uploaded (no), can it be undone (yes). Also names the true cost of a long interval: not "temporary files" but **finished work sitting unrecorded**.
- **Privacy is a hard rule, not a caveat.** Never a public remote — these vaults hold NDAs, grading data, journals, and contact details for dozens of real people. Off-machine backup means a **private** repo with the exclusion list reviewed against `domain: personal`, `Money/` and `Personal/Journal/` **before** the first push, confirmed explicitly (Rules 10 + 11). A pushed repository cannot be un-published.
- **Honest about limits.** Git is **not retroactive** — say so when the motivating question was about the past; the current one gets reconstructed, the next one gets a real answer. It records files, not thinking. It cannot see work done outside the vault. And it is **not a backup** — same disk, so a drive failure takes both.
- **`modified:` documented as the weaker alternative** — visible in Obsidian and queryable in a Base, but records only that a note changed and only the latest time, and depends on discipline nothing enforces. Deliberately **not** added to the controlled vocabulary: it would touch the validator and `types.json` to buy a strictly worse version of what git already provides.
- SKILL.md: new **Account** row in the Operating Loop, router entry, version-history trigger terms in the description. `cli-and-automation.md` now points its long-standing "keep a Git snapshot" line at the real setup. `onboarding.md` mentions it in one sentence at scaffold time — cheapest then, and it can never be backdated — without violating the rule against day-1 machinery.
- No schema changes, no script changes, no dashboard-server changes (`VERSION` stays 2.8.0). Nothing to migrate.

## 2.11.0 — 2026-08-11
New script **`sync_last_contact.py`** — derives `last-contact:` from meeting notes instead of trusting anyone to type it.

- **Why.** `last-contact` is the one person field with no maintenance mechanism: the rule says "update it when you file an interaction," and every miss silently degrades the review sweep that reads it — a stale date is worse than none, because it looks authoritative. Meetings already carry a date and a `people:` roster, so the value is computable rather than remembered.
- **What it does.** Every `type: meeting` note in any folder contributes its date (`date:` if present, else `created:`) to each linked attendee; each person gets their most recent. `--apply` writes; **dry run is the default**, per Golden Rule 10.
- **Guarantees**, matching the dashboard server's writers: never moves a date **backwards** (a manually-set newer value wins, so chat/email/in-person contact recorded by hand survives); touches only the `last-contact:` line, inserted at its Person-template position when the note lacks the key; atomic per-file write (temp + `os.replace`); idempotent; refuses a note where `last-contact` is a YAML list rather than corrupting the block; `Templates/` and `Archive/` excluded (a template's `{{date:YYYY-MM-DD}}` is not valid YAML).
- **Ties into `contact:` (2.10.0).** Skips `contact: none` — an author has no contact date. Reports anyone marked `contact: dormant` who turns out to have attended a meeting, so the standing gets reviewed rather than silently contradicted. `--exclude` leaves named notes alone; use it for the vault owner, who attends their own meetings and would otherwise always read as freshly contacted.
- **Documented ceiling.** It only sees interactions the vault records. Relationships run over WhatsApp, email, or in person produce no meeting note, so those people keep an empty `last-contact` — a habit gap, not a bug. `retrieval-and-review.md` now says to chase **stale dates, not blanks**, so the People sweep doesn't drown in people who were never neglected.
- No schema changes; no dashboard-server changes (`VERSION` stays 2.8.0). Supersedes 2.10.0 — installing this gets both releases.

## 2.10.0 — 2026-08-11
New person property **`contact:`** — separates the people you deal with from the people you only read about.

- **The problem.** The triage tree sends *"colleague, client, friend, **author**"* to `People/`, but `People.base` filtered on `type == "person"` and nothing else — so the moment you followed the skill's own filing instruction for a book author, they landed in the working directory beside real contacts, with every CRM column (Email · Phone · Last contact) blank. Two parts of the same skill disagreed. Books make this immediate: a single history book can add a dozen historical figures.
- **`contact: active | dormant | none`, and *omitted* means active** — so adopting it costs zero edits to existing vaults; you mark only the exceptions. `dormant` = was a contact, isn't now (left the company, dead lead) — stays in the directory and searchable, but **drops out of `last-contact` follow-up sweeps**. `none` = never a contact (authors, historical figures, cited executives) — out of the working directory entirely.
- **Why a third state and not a boolean:** a former colleague is not a reference figure. They were a contact and may be again, so they belong in the directory — they just shouldn't appear in "who am I overdue with." Different treatment, different value.
- **Why not `status:`.** `status` is one shared vocabulary across every type, enforced by the validator; adding person-states would have loosened validation for projects, tasks, and deals simultaneously. And **not** `relationship: client|partner|vendor` on the person either — that fact belongs to the **organization** (`company:` → the org note's `relationship:`) and duplicating it onto people is denormalization that drifts. `contact` records the one thing nothing else does.
- **Bases — `not:` + equality, never `!=`.** Because the default is *omitted*, most person notes carry no `contact:` at all. `contact == "none"` against an absent property is reliably false, so `not: ['contact == "none"']` includes them correctly; `'contact != "none"'` depends on missing-value semantics the Bases docs don't specify, and if it evaluated false the Directory would render **empty**. Documented as a general rule for filtering any optional flag (`bases.md` → *People directory & groups*).
- **`assets/bases/People.base`** gains the exclusion on *Directory* and *By department* plus two new views, **Reference (never contacts)** and **Dormant**, and a `Standing` column. **`validate_vault.py`** errors on an off-vocabulary `contact` value (empty is always fine). `assets/types.json` declares `contact` as `text`. Person template and the `note-types.md` Person schema carry the field, with a new *People you only read or cite* subsection: same `type: person` note, `contact: none`, and the *Relationship & considerations*/*Conversations*/*Commitments* sections simply left off.
- **One person is always one note** — reinforced in the triage tree. A separate `type: figure` was considered and rejected: it would break `people:` links, alias resolution, group rosters, and meeting backlinks to avoid one property. Research personas are not people at all — they belong in the research note or as `type: concept`.
- **Migration:** none required. Optionally add `contact: none` to author/figure notes and `contact: dormant` to lapsed contacts. No dashboard-server changes; server stays at `VERSION` 2.8.0.

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
