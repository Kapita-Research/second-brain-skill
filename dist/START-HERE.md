# Second brain — install or update

**Version `3.0`** · built on upstream `obsidian-second-brain` v2.17.0

**A folder of your notes, run through Claude. You talk; it writes files on your machine and finds them
again later.** The files are plain text in a folder you choose — **nothing is stored anywhere else, and
you can open, edit or delete any of it in any editor.**

---

> ## Send this folder to Claude and say one of two things
>
> **Never used it before** → *"Install this skill."*
> **Used it before** → *"Update my skill with this."*
>
> **Everything below is what Claude then does. You do not have to read it.**
>
> ---
>
> **And whenever anything seems not to work, in any conversation:** *"run the second brain install
> check"* — twenty checks, and each failure says the one thing to do. `CHECKLIST.md` has the steps
> written out.

---

# A · For Claude — a first install

**1 · Install the skill**

Copy the `obsidian-second-brain/` folder into the user's skills directory
(`~/.claude/skills/` — on Windows, `C:\Users\<them>\.claude\skills\`).

**2 · Ask where their notes should live**, and create that folder if it does not exist.

**3 · Copy **two** files into that folder — and keep them separate on purpose**

| From here | To the vault root | Whose it is |
|---|---|---|
| `kapita-vault-KAPITA.md` | **`KAPITA.md`** | **the firm's** — replaced whole on every update |
| `dist/CLAUDE.md` | **`CLAUDE.md`** | **theirs** — nothing ever replaces it |

> **`KAPITA.md` is the only file that names the company** — the team, the clients, how a figure is
> recorded. **Removed, the skill still works as a personal system with nothing of KAPITA in it.**
>
> ⛔ **Never write anything personal into `KAPITA.md`** — it is overwritten on the next update and the
> addition is lost silently. **Their own conventions go in `CLAUDE.md`.**

**4 · Raise Obsidian once — and say what skipping it costs.**

⛔ **Do not just say "it's optional".** That is true, and it leaves them turning something down without
knowing what. **Nothing is blocked without it; several things become *asking* instead of *seeing*:**
every note that mentions a client, visible in a panel · **your tasks as a board built from the notes
themselves** · clicking a link · editing a note's fields without touching YAML.

**It is free, opens the folder as it is, changes nothing about the files, and can be abandoned any
day** — the notes are plain Markdown either way.

**If they install it: turn on Settings → General → Command line interface.** Off by default, and it
lets search use the live index instead of matching text.

**5 · Then start the skill normally** — it will ask them to point it at material they already have
before asking them for anything.

---

# B · For Claude — updating an existing install

> ## **Say this first, before anything else: their notes are not touched.**
>
> **The skill lives in the skills directory. Their vault lives wherever they put it. Replacing one
> cannot affect the other.** This is an update to the instructions you follow — **not to anything they
> wrote.** No migration, no re-filing, no re-tagging.

**1 · Read `obsidian-second-brain/CHANGELOG.md`** — the 3.0 entry says what changed — and check the version already installed
(`SKILL.md` frontmatter → `metadata.version`).

**2 · Replace the whole skill folder** with `obsidian-second-brain/` from here. **Nothing in it holds
state.** Confirm afterwards that the installed `metadata.version` reads `3.0`.

**3 · Replace `KAPITA.md`, and do not touch `CLAUDE.md`**

**Copy `kapita-vault-KAPITA.md` over the vault's `KAPITA.md`.** ⛔ **Leave `CLAUDE.md` exactly as it
is** — it is theirs, and it is the one file nothing here has the right to change.

> **Updating an older install?** If the vault has a `CLAUDE.md` that *is* the firm's file — it names
> KAPITA, the clients, the team — **rename it to `KAPITA.md`, replace it, and put a fresh `CLAUDE.md`
> from `dist/` beside it.** ⚠️ **Read it first and carry anything the owner added into the new
> `CLAUDE.md`** — before the split there was nowhere else for it to go.

```bash
python tools/check-kapita-layer.py "<vault>/KAPITA.md"
```

**Run that after** — it reports any word in the vault's copy that disagrees with the skill.

**4 · Their vault's scaffold is behind — one command brings it up**

```bash
python tools/sync-vault.py "<their vault>" --fix
```

**The skill is replaced whole. A vault is not.** Property types, templates and views were copied in
once at creation and **never update themselves** — so a view filtering on a property their vault has
never heard of **returns nothing, with no error.**

**`--fix` is additive only:** it merges new property types and copies missing templates. **It
overwrites nothing** — a property type that disagrees, a template they have edited, a `.base` they
chose not to have, and every `publish:` line are **reported for a person to settle, never changed.**

**Run it without `--fix` first and read what it says.** Then act on anything in the second list.

> ⛔ **`publish:` will appear there if any note carries it.** **Dormant, not harmless:** with nobody
> subscribed to Obsidian Publish the key does **nothing at all** — **until someone subscribes, and
> then every note carrying it goes live at once**, from a decision no one remembers making. **Delete
> those lines with the file open.**

**5 · Offer to make it automatic — they never got this offer**

**This skill is picked up by matching what someone said. A person who says *"he asked me for the report
by Thursday"* — which is how people actually talk — may not reach it at all.** A few lines in their own
`~/.claude/CLAUDE.md` turn that guess into an instruction, because that file is read at the start of
every session, in every directory.

**Offer it in one line and act only on a yes** — the wording and the exact block to append are in
`references/onboarding.md` → *Last — offer to make this automatic*.

⛔ **Append, never overwrite** — other things live in that file. **If a section like it is already
there, say so and change nothing.**

**6 · Tell them what will feel different** — from the changelog, in a few lines. **Four they would
otherwise meet by surprise:**

| | |
|---|---|
| **"Publish this"** | **Asks what they meant** and offers the firm's folder. **It will not put anything on the open internet — that was removed** |
| **Writing up a meeting** | **Filtered, not summarised.** Scaffolding dropped; what was decided, rejected, doubted or quoted stays **in their words** |
| **Asking for a new record type** | **It just writes it.** No argument that the idea is really a project or a source |
| **Renaming a note** | **Three steps** — rename, rewrite the links, **and keep the old name as an alias** |

**And two additions they will only meet if they ask:** an **`Outbox/`** — the single way anything leaves,
which `domain: personal` never enters — and **`Findings/`**, where a research number is quoted whole,
with its base and caveat, or not at all.

---

## What it will never do

**Delete anything** · **put anything on the internet** · **move a private note to the firm's folder** ·
**move anything to the firm at all unless told to.**

---

## Trying it out

Say these the way you would say them to a person — **do not phrase them carefully:**

- *"Note this: the client wants the results before Thursday."*
- *"Write up the meeting I just had — [paste it]"*
- *"What's on my plate?"* · *"What's overdue?"*
- *"What did we decide about \<a client\>?"*
- *"I want to track the training sessions I run — set that up."*
- *"Record this finding: 62% of X prefer Y"* — **and see what it asks for**
- *"This note belongs to the firm."* · *"Publish this."*

**Anything that feels wrong, or that it does unexpectedly — write it down and send it back.**

---

## When it does not work

```bash
python tools/check-install.py
```

**Twenty checks, nothing changed.** Skill installed and matching · vault found · both root files, and
whether `KAPITA.md` is current · property types · templates · every dashboard view and whether it
excludes `Templates/` · Obsidian, its CLI, and whether the vault was ever opened in it · automatic
capture · and whether the vault validates.

**Each failure prints the one thing to do.** Full steps in `CHECKLIST.md`.
