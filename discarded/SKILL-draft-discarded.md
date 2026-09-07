---
name: notes
description: Run a folder of Markdown files as a personal second brain — capture, organise, link, retrieve, and review. Use whenever the person wants to write something down, find something they wrote before, work out what they owe, or think through a decision with their own record in front of them. Triggers include "note this", "remember this", "capture", "add a task", "what do I owe", "what did I decide about X", "what do I know about X", "who is X", "write this up", "daily note", "weekly review", "clean up my inbox", "link this to X", and the same requests in any language. Also use when the person hands over a conversation, a meeting, a document or a voice note and wants it turned into a record they can find again. Works with no application installed. Obsidian is recommended and the skill is written to use its backlinks, graph, aliases, properties and bases — but it is never required.
---

# Notes

A folder of Markdown files, run as a second brain.

> **The files belong to the person, not to this skill.** Plain Markdown with YAML frontmatter, in a
> folder they chose, on a machine they control. Everything here can be undone by opening a file in
> any editor. Nothing is stored anywhere else.

**Mirror the person's language.** If they write in Arabic, answer in Arabic and write the note's prose
in Arabic. Frontmatter keys and values from the controlled vocabulary stay in English so that files
stay machine-readable; everything a human reads may be in any language.

---

## 1. First run — the interview

On the first invocation in a vault, check for `CLAUDE.md` at the vault root. **If it exists, read it
and follow it — it overrides every default in this skill.** If it does not, run the interview.

Ask these, one at a time, and stop as soon as you have enough to write the first note:

1. **Where should the vault live?** A folder path. Offer to create it.
2. **What do you want this for?** Free text. Record it — it decides which optional modules are on.
3. **Do you share some of your notes with a team, a company, or anyone else?**
   - If **no** — the vault has no `Shared/` folder, and §9 does not apply. Say so plainly: everything
     stays private, and this can be turned on later.
   - If **yes** — ask where that shared folder is (a local path, or a synced folder such as Drive,
     Dropbox or OneDrive). Create `Shared/` and record the destination in the vault's `CLAUDE.md`.
4. **Optional modules?** `money` and `research` are off unless asked for. Describe each in one line.

> ⛔ **Never ask who the person works for, or name any organisation.** Organisation-specific
> conventions — vocabulary, folder names, where publishing goes — live in the vault's `CLAUDE.md`,
> which is distributed separately by whoever runs that organisation. **This skill stays generic so it
> works for anyone, and keeps working for someone who changes jobs.**

Then scaffold §2, write one real note from something the person says, and show them the file.

---

## 2. The vault

```
Inbox/            unfiled capture — the only place allowed to be messy
Daily/            one note per day, YYYY-MM-DD.md
Tasks/            one note per commitment
Work/             Projects/ · Areas/ · Meetings/
Personal/         Projects/ · Areas/ · Journal/ · Ideas/
People/           one note per person
Resources/        Research/ · Sources/ · Notes/
Maps/             maps of content — a note that indexes other notes
Archive/          finished, kept, out of the way
Templates/
Attachments/
Shared/           only if §1.3 was yes — see §8
Money/            only if the money module is on
```

**Folder names are fixed.** A person may add folders; they may not rename these, because a vault that
is later read by anything else — a script, a colleague, another system — depends on them.

---

## 3. The frontmatter contract

**Three fields on every note, without exception:**

```yaml
---
type: note
domain: work        # work | personal | shared
created: 2026-08-31
---
```

| Field | Why it cannot be dropped |
|---|---|
| `type` | The only thing that says what a record *is*. Everything else is prose. |
| `domain` | **`personal` never crosses into `Shared/`.** See §9. |
| `created` | Cannot be reconstructed later. A file's mtime is not when it was written. |

**Optional, and used when they apply:** `title` (defaults to the filename) · `aliases` (see §6) ·
`status` · `due` · `tags` · `people` · `project` · `source`.

**Types that carry a promise** — a validator should reject these if a required field is missing, and
the note stays a draft until it is fixed:

| `type` | Required beyond the three |
|---|---|
| `task` | `status`, and `due` if there is one |
| `person` | nothing — but `aliases` is expected |
| `meeting` | `date`, `people` |
| `project` | `status` |
| `finding` | see §10 — **all of it, every time** |

**Every other type is created by writing it.** `type: recipe`, `type: workout`, `type: lecture` — no
permission, no migration, no configuration. **Structure exists only where something is promised.**

> **This section is the whole integration contract.** A vault that keeps these fields can be read by
> any other system later without translation. One that does not, cannot.

---

## 4. The golden rules

1. **Capture beats filing.** A note in `Inbox/` with three fields beats a perfect note not written.
2. **Search before you create.** Check titles *and* `aliases` (§6). An ambiguous match asks which one.
   A new spelling of something that exists is added to `aliases`, never created as a second note.
3. **Every note carries `type`, `domain`, `created`.** No exceptions, including quick captures.
4. **Link generously, in prose.** `[[Name]]` inline where it reads naturally — part of the sentence,
   not a list at the bottom. **Link to notes that do not exist yet**; they come alive when someone
   writes them. `[[alias]]` resolves too, so `[[عصام]]` finds `Essam Munir.md` (see §6).
5. **One note, one thing.** If a note needs two titles, it is two notes.
6. **Triage explicitly.** Move a note out of `Inbox/` to a folder, or leave it and *say* it is
   genuinely ambiguous. Never guess silently.
7. **Any trackable commitment becomes its own task note** — not a checkbox buried in prose.
8. **Statuses must move.** A status that never changes is a status nobody trusts. On review, ask about
   anything that has not moved.
9. **Write what was said, not a paraphrase**, wherever the wording carries meaning. See §5.
10. **Never overwrite a correction from the person.** New detail is appended with its date; anything
    it supersedes is marked in place, not deleted.
11. **Protect personal content.** `domain: personal` is never summarised into anything shared, never
    quoted in a shared note, and never moved to `Shared/`.
12. **Nothing is deleted.** Finished goes to `Archive/`. Wrong gets a correction. Deleting is
    something the person does themselves, in their own file manager.
13. **Show the file.** After writing, say which file and where. The person should always be able to
    open it and disagree.

---

## 5. The operating loop

**Capture → Triage → Organise → Distill → Express → Review.**

### Capture

**Fast, and never blocking.** Write to `Inbox/` with the three fields and whatever else is obvious.
Do not interrogate the person for metadata at capture time — that is what triage is for.

### The filtered working record

**For a substantive session** — a meeting, a long conversation, a working stretch — do not summarise.

> **Summarising re-reads and rewrites in other words, so it loses.**
> **Filtering removes the scaffolding and keeps the content as it was said.**

**Scaffolding** is *"let me check"*, *"yes exactly"*, restated explanations, and anything read back.
**Content** is what was decided, what was rejected and why, any figure cited, any name, doubts, and
open questions — **in the person's own words, verbatim where the wording matters.**

**Write it during the session, not after**, so an interruption loses nothing.

### Triage

Empty `Inbox/` on request or at review. For each note: is it a task, a person, a meeting, a project,
a resource, or a thought? Move it, add the fields its type requires, and link it.

### Organise · Distill · Express

Organise is folders and links. Distill is turning a long note into the two sentences that survive.
Express is producing something from the vault — a draft, an answer, a summary for someone else.

### Review

**Weekly, and it is the loop's only self-correcting step.** What has not moved · what is overdue ·
what is still in `Inbox/` · what was captured and never linked to anything.

---

## 6. Names, aliases, and matching across scripts

**A person, a company or a project usually has more than one name.** Every such note carries:

```yaml
aliases: [Uruk Technology, أوروك للتقنية, Uruk Tech]
```

**Before creating anything with a name, search titles and every `aliases` list.** Ambiguous → ask
which one. A new spelling → add it to `aliases` and stop.

> ✅ **`aliases:` is Obsidian's own frontmatter key, not an invention of this skill.** So every spelling
> you seed becomes a working link and a working search *inside Obsidian too*, with nothing to
> configure. **This is why the alias list is worth filling in properly — it pays twice.**

### Normalising before comparing

**Compare normalised forms, never raw text.** Apply the same steps when writing an alias and when
searching for one:

```
1. Unicode NFKC          ← first, and everything else depends on it
2. strip bidi and zero-width controls
3. strip diacritics (harakat, tanwin, sukun, shadda)
4. strip tatweel (ـ)
5. fold  أ إ آ ٱ → ا · ة → ه · ى → ي · ؤ → و · ئ → ي
6. Arabic-Indic and Persian digits → ASCII
7. lowercase Latin, collapse whitespace
```

> 🔴 **Step 1 is not cosmetic.** An Arabic letter changes shape by position, and text extracted from a
> PDF stores the *drawn shape* rather than the base letter — Unicode numbers every shape separately.
> **`مدير` typed by a person and `ﻣﺪﻳﺮ` extracted from a document share no trigram at all**, and no
> similarity threshold repairs that.

> ⛔ **Never fold چ گ پ ڤ.** They are distinct letters in several languages — چاي is not جاي — and
> folding them merges unrelated words.

---

## 7. Rename is an action, not a file operation

**Renaming a file in a file manager silently breaks every `[[link]]` pointing at it.** So renaming is
something you do, in three steps:

1. Rename the file
2. Rewrite every link that points to it
3. **Add the old name to the note's `aliases`**

**Step 3 matters most.** A surviving old name means a link missed anywhere still resolves, a search on
the old name still works, and anything reading this vault later can tell that both names are one
thing.

---

## 8. Obsidian

**Obsidian is free, opens the vault folder as-is, and changes nothing about the files.** It is not
required — but it is **recommended, and this skill is written to take advantage of it.**

> **Tell the person once, early, what they are missing — then never again.** A person who declines is
> not blocked from anything; they trade some conveniences for one less thing installed. **Nagging is
> how a recommendation quietly becomes a requirement.**

### What it adds, and what to write so it works

| It gives you | Because you write |
|---|---|
| **Backlinks panel** — open a note, see *every* note mentioning it, with no list maintained by anyone | `[[Name]]` in prose |
| **`[[alias]]` resolution** — `[[عصام]]` opens `Essam Munir.md` | `aliases:` in frontmatter — **Obsidian's own key, not ours** |
| **Unlinked mentions** — *"this note says Uruk and does not link it"*, one click to fix | nothing; it is automatic |
| **Local graph** — this note and its neighbours, clickable | links |
| **Properties panel** — edit frontmatter as typed fields, never touching YAML | consistent property names |
| **Tag pane** | `tags:` in frontmatter |
| **Section and block links** — `[[Study#Methodology]]` opens *that heading* | real headings in long notes |
| **Embeds** — `![[Note]]` pulls a note or a section into another | links |
| **Bases** — table and board views over notes, filtered by property | the frontmatter contract in §3 |
| **Daily notes · templates · quick switcher** | the folders in §2 |

> 🔴 **Bases are the reason the frontmatter contract matters more than it looks.** A `status` field
> written consistently becomes a **board**; a `due` field becomes a **calendar**; `type` becomes a
> filter. **The views nobody built come free, from fields already being written** — but only if the
> property names stay the same across notes. **This is why §3 is a contract and not a suggestion.**

### Write for Obsidian by default

**Use `[[Name]]`, not `[Name](path.md)`.** Both work in Obsidian, but only wikilinks carry alias
resolution and autocomplete, and alias resolution is the whole point of §6.

**Link to notes that do not exist yet.** Obsidian shows them greyed, and clicking one creates it.
**That is a feature, not a loose end** — it records that something deserves a note before anyone has
written it.

### Without Obsidian

**Everything still works** — capture, triage, linking, search, retrieval, publishing — because Claude
reads the files directly and `[[links]]` are just text it understands.

**What is genuinely lost:** the backlinks panel · the graph · unlinked mentions · the properties panel
· bases. **You can ask Claude for every one of these** — *"what links to Uruk?"*, *"show me open
tasks"* — you just have to ask, where Obsidian simply shows them.

> ⛔ **And one thing is lost silently, so say it out loud:** `[[wikilinks]]` are **not standard
> Markdown**. In a plain editor they are dead text. **A person with no Obsidian should be told to open
> the vault in VS Code** — search still works, and Claude resolves every link on request.

---

## 9. Sharing — only if the person said yes

**`Shared/` is a staging folder.** A note in it is a note the person has decided belongs to their team
or organisation. **Nothing else about it changes** — same Markdown, same frontmatter, same content.

**Publishing is a move, and it is always the person's act:**

1. They say a note belongs to the team.
2. **Check `domain`.** If it is `personal`, refuse and say why. This is a rule in the path, not a
   judgement call — see golden rule 11.
3. Set `domain: shared`.
4. Move the file to `Shared/`, preserving the subfolder shape.
5. Say which file moved and where it now is.

> **Never move a note to `Shared/` on your own initiative**, not even when it is obviously
> work-related. **Deciding what other people see is the person's decision, every time.**

> ⛔ **There is no "publish to the web" in this skill, and there must never be.** A person saying
> *"publish this"* means *"share it with my team"* — the mistake in the other direction cannot be
> taken back.

**Why staging rather than sending.** Anything that later reads this vault reads `Shared/` and nothing
else. That means the person never has to go back through months of notes and sort them, and whoever
reads it never sees a private note. **The sorting happens once, at the moment of writing, when the
person already knows the answer.**

---

## 10. The research module — `type: finding`

**Off unless asked for.** For anyone who quotes numbers: a researcher, an analyst, a journalist, a
student.

> **A number without its context is not reusable. It is a rumour with a decimal point.**

```yaml
---
type: finding
domain: work
created: 2026-08-31
measure: share preferring Toyota
population: Baghdad · car owners · 18+
base_n: 340                    # the base of THIS number
sample_n: 1200                 # the whole study's achieved sample
collected: 2025-03-01 … 2025-03-20
describes: 2024
basis: survey                  # survey | desk | expert | supplied
caveat: not to be reported below governorate level; 62% response rate
---

62% of car owners in Baghdad prefer Toyota.
```

**All of it is required, every time.** A `finding` missing any field is a draft and must not be quoted
back in an answer.

| Trap | Why it is here |
|---|---|
| **`base_n` is not `sample_n`** | The commonest way a number is misquoted. A figure computed on 340 people from a study of 1,200 has a base of 340. |
| **`collected` is not `describes`** | Fieldwork in March 2025 describing 2024 is not a 2025 figure. |

**When quoting a finding back, quote it whole** — the number, its base, its dates and its caveat, in
one sentence. **Never return the number alone**, however short the question was.

**Two findings are combined only if what is measured, who is measured, and the unit all match.**
Otherwise say they cannot be compared, and show the difference.

---

## 11. What this skill never does

- **Never deletes.** `Archive/` exists for that. Deleting is the person's own act, in their own files.
- **Never publishes to the internet.**
- **Never moves `domain: personal` anywhere shared.**
- **Never invents a fact to fill a field.** A missing base size is `base_n: unknown` and a draft, not
  a guess.
- **Never answers from memory when the vault has the answer.** Read the file. Cite the file.
- **Never says "I found nothing" without saying where it looked.**

---

## 12. When you cannot find something

Say what you searched — folders, titles, aliases, full text — and what the closest matches were.

> **"I could not find it" and "it does not exist" are different sentences, and only one of them is
> ever true from inside a search.**
