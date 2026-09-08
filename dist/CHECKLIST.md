# Installing the second brain

> # Say this to Claude, and nothing else:
>
> ## *"Do the full checklist of installation of KAPITA second brain skill"*
>
> **It does the whole thing.** You are not asked to choose a folder, copy a file, edit a setting or run
> a command. **Everything below is written for Claude, not for you** — read it only if you want to know
> what happened.

**When it is finished you will simply be talking to it, and it will be writing notes.** ⚠️ **Open a new
conversation once it is done** — a skill installed mid-conversation is not picked up by the one already
running.

---

# For Claude — the runbook

**Follow this in order, and do not ask the person anything it can answer for itself.** *Someone who has
not used this yet has no basis for choosing a folder layout, and being asked makes an install feel like
a form.* **The one thing that is genuinely theirs is who they are and what they work on, and that comes
out of the first conversation rather than an interview.**

## 1 · Run the installer

```bash
python "<the shared KAPITA Second Brain folder>/install.py"
```

**Where to look for that folder**, in order:

| | |
|---|---|
| **Google Drive for desktop** | `G:\My Drive\KAPITA Second Brain`, or the same name under another drive letter, under `Shared drives`, or in the home folder |
| **A clone of the repository** | then `python tools/install.py` from it |
| **Neither** | see *If there is no shared folder* below |

**It does all of this by itself** and prints a line per step:

1. **Checks Python 3.8+**
2. **Finds the newest release and verifies the archive by hash before unpacking it**
3. **Creates the notes folder** — `~/OneDrive/Documents/Second Brain`, or `~/Documents/Second Brain`;
   somewhere synced, because a lost laptop should not take somebody's notes with it
4. **Scaffolds it** — folders, templates, dashboards, property types, with the findings module on
5. **Installs the skill and the two root files**, verifying every file by hash after it lands
6. **Merges three hooks** into `~/.claude/settings.json` and **appends the standing block** to
   `~/.claude/CLAUDE.md`
7. **Runs the install check** and prints it

⛔ **It overwrites nothing that belongs to the person.** Settings are merged and backed up, the standing
block is appended only if absent, and an existing vault is added to rather than replaced.

## 2 · Then do the five things a script cannot

**The installer ends by listing these. Do them without being asked again.**

### a · The one thing the owner pastes themselves  🔴

**Their notes folder is almost never the folder a conversation is open in**, so without this ⛔ **every
note asks their permission before it is written**, and the rule that says *do not ask permission to
write a note* loses to a dialog box every time.

**Tell them to open `~/.claude/settings.json`** (on Windows `C:\Users\<them>\.claude\settings.json`)
**and merge this into whatever `permissions` block is there**, with their real folder path:

```json
"permissions": {
  "additionalDirectories": ["<their notes folder>"],
  "allow": [
    "Read(<their notes folder>\**)",
    "Write(<their notes folder>\**)",
    "Edit(<their notes folder>\**)"
  ]
}
```

⛔ **Claude cannot do this one**, whichever way it is asked: **a model is not permitted to widen its own
permissions.** *That refusal is correct and is not a bug to route around.* **It is one paste, once per
machine, and it takes a minute.**

⚠️ **Do not let them click through the prompts instead.** *Somebody who approves twenty prompts a day
stops reading them*, and then the one that matters, the guard on their private judgements, **looks
exactly like the other nineteen.**

### b · The daily update routine  🔴

**Create a scheduled task**, once a day, whose whole job is:

```bash
python "<the shared folder>/install.py" --check
```

*(or `tools/update.py --check` from a clone)*

**What it does with the result matters more than the schedule:**

| it printed | the task does |
|---|---|
| `Up to date` | **replies with one word and nothing else.** This is the normal outcome and it must cost no attention at all |
| `still syncing` | the same. It resolves itself |
| `A newer release is available` | **one short message**: the two version numbers, two or three lines from the top of the skill's `CHANGELOG.md`, and *"say **update the second brain** whenever it suits you"* |
| `the shared folder is not on this machine` | **one short message, and every time it happens**: either install Google Drive for desktop, or download the archive from the folder in a browser and hand over the path |

⛔ **The routine never installs anything. It reports.** **A skill replaced under an open conversation is
not re-read by it**, so the moment belongs to the person.

### c · The index of installed skills  ⚪

**List `~/.claude/skills/`, read only each `SKILL.md`'s `description:` line, and write one note** — what
each skill is for and where it lives, grouped by purpose.

⛔ **Pointers, never content.** *No colour token, no template, no threshold copied out.* The skill is
maintained; a copy of it is not, and the copy is what gets read six months later when it is wrong.

### d · Their own note  🔴

**`People/Me.md`** — their name and its spellings, title, employer, and the links out to their work.

⛔ **Never invent any of it, and never ask for it as a form.** **Talk to them** — what they do, who they
deal with, what is on this week — **and write real notes as they answer**, this one among them.

> **Without it, anything written on their behalf has nothing to look up, and falls back to
> `[your name]` in a finished draft.**

### e · Obsidian  ⚪

**obsidian.md, then Open folder as vault.** Nothing breaks without it; several things become *asking*
instead of *seeing*. **If they install it: Settings → General → Command line interface → Register**,
which puts a live index behind search instead of plain text matching.

## 3 · Confirm, say one sentence, and start working

```bash
python "<clone or unpacked release>/tools/check-install.py"
```

> *"Done. From now on, in any conversation, if you mention something worth keeping it gets written
> down, and I look there before answering. You never have to name it."*

**Then stop explaining and start using it.**

---

## If there is no shared folder on this machine

**Both paths end in the same install, byte for byte.**

1. **Better, once:** install Google Drive for desktop and let it sync `KAPITA Second Brain`. Every
   future update then costs a file read, and works with the internet down.
2. **Or now, by hand:** open
   [the folder](https://drive.google.com/drive/folders/1D79209rP34Gay9C7LOicFbbpVYcOxOdz) in a browser,
   download the newest `second-brain-<version>.zip`, unpack it, and run:

```bash
python tools/install.py
```

---

## What is being installed

| | Where it goes |
|---|---|
| **The skill** | `~/.claude/skills/obsidian-second-brain/` — the instructions Claude follows |
| **The notes** | a folder of plain Markdown files, theirs, readable in any editor |
| **`KAPITA.md`** | the notes folder — **the firm's conventions.** Replaced whole on every update |
| **`CLAUDE.md`** | the notes folder — **theirs.** Nothing ever replaces it |
| **Three hooks** | `~/.claude/settings.json` — what makes the rule hold in the two-hundredth message |
| **The standing block** | `~/.claude/CLAUDE.md` — read at the start of every conversation, in every folder |

> ⛔ **Never write anything personal into `KAPITA.md`.** It is replaced on the next update and whatever
> was added disappears without a message. **Personal conventions go in `CLAUDE.md`, beside it.**

---

# When something is not working

**Open a new conversation and say: *"run the second brain install check"*.**

Every failing line prints the one thing to do about it. **Required failures are marked `!` and listed
first; optional ones never fail the run and print what you give up.**

**Run it after any update, and before asking anyone for help** — it turns *"it isn't working"* into a
line number.
