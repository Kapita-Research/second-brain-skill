# Install checklist — the second brain

**Eleven steps, then one command that checks all of them.**

> 🔴 **Five of these are outside the skill — in your own files — and the skill does not work properly
> without them.** They are the ones people skip, because nothing forces them: **the two files at your
> notes folder's root (4)** · **the Obsidian CLI registration (6)** · **your own person note (7)** ·
> **automatic capture (8)** · **and the two hooks (8, second half)**. The check at the bottom marks each of them **REQUIRED**.

> ## If something is not working, you do not need to read this file.
>
> **Open a new conversation with Claude and say: *"run the second brain install check"*.** It runs the
> command at the bottom and tells you which line failed and what to do about it.

---

## What you are installing

| | Where it goes |
|---|---|
| **The skill** | `~/.claude/skills/obsidian-second-brain/` — the instructions Claude follows |
| **Your notes** | any folder you choose — plain Markdown files, yours, readable in any editor |
| **`KAPITA.md`** | the notes folder — **the firm's conventions.** Replaced whole on every update |
| **`CLAUDE.md`** | the notes folder — **yours.** Nothing ever replaces it |
| **Obsidian** | optional and free — turns the notes into something you can see |

---

## 1 · Python

**Needed by the scaffold, the health check and this checklist.** `python --version` should print 3.8
or higher. If not: **python.org**, and tick *Add python.exe to PATH* during install.

## 2 · The skill

**Copy the `obsidian-second-brain` folder from this package into `~/.claude/skills/`.**
On Windows that is `C:\Users\<you>\.claude\skills\`.

**Then start a new conversation** — a skill added mid-conversation is not picked up by the one already
running.

## 3 · The notes folder

**Any empty folder.** Somewhere synced is a good idea — OneDrive, Drive — because these are your notes
and a lost laptop should not take them.

⛔ **Do not put it inside a git repository or a code project.**

## 4 · The two files at its root  🔴 required

| From this package | Rename to | Whose it is |
|---|---|---|
| `kapita-vault-KAPITA.md` | **`KAPITA.md`** | **the firm's** — replaced whole on every update |
| `dist/CLAUDE.md` | **`CLAUDE.md`** | **yours** — nothing ever replaces it |

⛔ **Never write anything personal into `KAPITA.md`.** It is overwritten on the next update and what
you added disappears without a message. **Your own conventions go in `CLAUDE.md`.**

## 5 · Obsidian  ⚪ optional

**Optional, free, and changes nothing about the files** — it opens the folder exactly as it is, and you
can stop using it any day.

**What you give up by skipping it:** every note that mentions a client, visible in a panel · **your
tasks as a board built from the notes themselves** · clicking a link to follow it · editing a note's
fields without touching YAML. **Nothing is blocked without it. Several things become *asking* instead
of *seeing*.**

**obsidian.md** → install → **Open folder as vault** → pick your notes folder.

## 6 · The Obsidian command line interface  ⚪ optional, but pointless to skip if you installed Obsidian

**Settings → General → Command line interface**, then **Set up CLI to work in the terminal → Register.**

**Off by default.** With it on, search uses Obsidian's live index — backlinks, alias resolution,
property search — instead of matching text. **The toggle alone is not enough; Register is what puts
`obsidian` on your PATH.**

## 7 · The scaffold — and your own note  🔴 required

**Tell Claude: *"set up my vault"*.** It creates the folders, installs the templates and the dashboard
views, and writes the property types Obsidian needs so a date behaves like a date.

**Already have a vault from an older version?** `python tools/sync-vault.py "<your vault>" --fix` —
additive only; it overwrites nothing.

**Then: *"write my own note"*.** 🔴 **Do not skip this.** It writes `People/Me.md` — your name and its
spellings, your title, your employer, your addresses. **Anything Claude ever writes on your behalf —
an email, a bio, a form — looks there first.** Without it you get `[your name]` in a finished draft.

## 8 · Automatic capture  🔴 required

**Tell Claude: *"set up automatic capture"*.**

**It appends a short block to `~/.claude/CLAUDE.md`** — read at the start of every conversation, in
every folder — saying that you will talk about your work rather than ask for a note, and that such
things should be written down without being announced.

> **Without this, the skill only starts when you say something that obviously sounds like note-taking.**
> **You will not talk that way.** You will say *"he asked me for the report by Thursday"* — and nothing
> will happen.

**It is one small file. You can read it, edit it, or delete it to turn this off.**

**Then: *"enforce the second brain with hooks"*.** 🔴 **The second half of the same step.**

**Two hooks go into `~/.claude/settings.json`** — one fires at the start of every conversation, one on
**every message**.

> **The file above is an instruction. Over a long conversation an instruction can be drifted past.**
> **A hook is run by the program itself, so it cannot be.**

**Cost: about forty tokens a message. What it buys: the rule holds in the two-hundredth message exactly
as it did in the first.**

**And if you will keep private opinions in the vault: *"arm the judgement guard"*.** ⚪ Optional — but it
is **the only protection here that is a mechanism rather than an instruction.** Any read of a
`Judgements/` note becomes a prompt you answer. **Asking for one costs a click. Claude reaching for one
while writing something for somebody else produces a prompt you did not expect — and that is the point.**

## 9 · What else is on this machine  ⚪ optional

**Tell Claude: *"index my installed skills in the vault"*.**

**It lists `~/.claude/skills/`, reads one line from each, and writes a single note** — what each skill
is for and where it lives, grouped by what they are *for*.

> **Half the value of a capability is remembering it exists on the day it is needed.** *A skill nobody
> remembers is a skill nobody uses* — and the ones you install and forget are usually the ones that
> would have saved the afternoon.

⛔ **Pointers, never content.** *Nothing is copied out of a skill into the note* — not a colour, not a
template, not a threshold. **The skill is maintained; a copy of it is not, and the copy is what gets
read six months later when it is wrong.**

**Re-run it whenever you add or remove a skill.** It is one note and it is cheap to rewrite.

## 10 · The daily update check  🔴 required

**Tell Claude: *"set up the daily second brain update check"*.**

**It creates one scheduled routine.** Once a day it asks the repository whether a newer release exists.
**If it does not, it says nothing at all.** If it does, you get one notification naming the release and
what changed, and you install it by saying *"update the second brain"* whenever it suits you.

> ### Why this is required rather than optional
> **The skill will keep changing.** Fixes, new rules, a corrected number in the firm's layer. **A
> machine that never hears about a release is a machine running last month's rules while everyone else
> moved on** — and the person on it has no way of knowing.

**The update takes seconds and nothing is unavailable while it runs.** The conversation you are in keeps
the copy it started with; the next one gets the new one. **So you never have to pick a quiet moment.**

⛔ **Nothing installs by itself.** The routine only tells you.

**Two things it needs**, and Claude sets both up:

| | |
|---|---|
| **A clone of the repository** | `git clone <repo>` somewhere you will not delete, then `git config core.hooksPath .githooks` inside it |
| **A second `SessionStart` hook** | mentions a release that has been waiting more than three days. No network, it compares two numbers already on disk |

## 11 · The first session

**Just talk.** Claude will ask what you do, who you deal with, and walk you through your week — and
write real notes while you answer. **You do not have to prepare anything.**

---

# The check

```bash
python tools/check-install.py
```

**Two dozen checks, nothing changed — it only looks.**

**Required failures are marked `!` and listed first** — the skill will not work properly until they are
done. **Optional ones are marked `-` and never fail the run**; they print what you give up.

**Or say to Claude: *"run the second brain install check"*.**

**Run it now, run it after any update, and run it before asking anyone for help** — it turns *"it isn't
working"* into a line number.

---

## The four that fail most often, and what they look like

| The line | What it means |
|---|---|
| **`Obsidian CLI enabled`** | You turned on the toggle but did not press **Register**. Search still works; it just matches text instead of using the index |
| **`KAPITA.md is current`** | Your copy still says `Shared/` — a folder that no longer exists. **Replace the file** |
| **`Views exclude Templates/`** | Your dashboards are counting the blank templates as real notes, so every total is off by one |
| **`Automatic capture configured`** | 🔴 Step 8 was skipped. The skill only starts when you name it — **and you will not name it** |
| **`Your own person note`** | 🔴 Step 7's second half was skipped. Anything written on your behalf has nothing to look up |
| **`Standing reminder enforced by hooks`** | 🔴 Step 8's second half was skipped. The rule holds early in a conversation and fades as it grows |

---

**When it prints `All N checks pass. Nothing to do.` — you are done, and nothing else on this page
matters.**
