# Sharing & Export (OPTIONAL)

Your vault is **private and local by default**. Nothing in it reaches anyone until the owner moves it.


## ⛔ One thing has no exit at all

**`type: judgement` — the owner's opinion of a person or a thing — never leaves, in any form, under any
condition.** Everything else on this page is a question of *how* something leaves. **This is the one
thing for which the answer is: it does not.**

⛔ **Not in a file, not quoted, not paraphrased, not softened into a work note, and not as the reason a
sentence was worded the way it was.** ⛔ **And no confirmation unlocks it** — asking does not make it
allowed, which is true of nothing else here. **The owner says it in their own voice, or it is not said.**

**It is already barred from `Outbox/` by `domain: personal`. That is the second line of defence; the
first is that it is never read while writing for anyone else.** See `references/note-types.md` →
*Judgement*.

## The word "publish" — route it, never guess

⛔ **When someone says *"publish this"*, they almost always mean *"share it with my team."*** Treat it
as that, and confirm which they meant before doing anything.

| They mean | Do this |
|---|---|
| Share with their organisation | **Move it to `Outbox/`** — see `SKILL.md` → *`Outbox/` — the only way anything leaves* |
| Send it to one person | Export the note — below |
| Put it on the open internet | **Not something this skill does.** See the bottom of this file |

## Sharing with an organisation

**`Outbox/` is the whole mechanism.** A finished note the owner has decided belongs to their
organisation **moves** there; nothing else about it changes. It is the vault's only exit, and every
rule around it lives in `SKILL.md`, not here.

## Sending one note to a person

- **Export to another format** (Word/PDF/HTML): hand the Markdown to the `docx`/`pdf` skills if they
  are installed, or share the `.md` directly — it is portable plain text.
- **Copy the note, not the vault.** Strip private frontmatter before sharing externally.

## Pushing into a team tool

**Slite, Confluence, Notion, Google Docs:** draft and refine in the vault — where Claude can help —
then push the finished note out. Community sync plugins exist for some targets; otherwise export the
Markdown and paste or import it.

## Versioning & backup

The Obsidian Git community plugin, or plain `git` in Claude Code, gives history and rollback. **Useful
before any bulk change.**

## Quick decision

| Want | Use |
|---|---|
| Hand it to my organisation | **`Outbox/`** |
| Send one note to someone | Export `.md`, or convert to docx/pdf |
| Team wiki | Draft in the vault → export or push to the team tool |
| Backup & history | Git (plugin or CLI) |

---

## ⛔ What this skill does not do: publish to the open web

**Obsidian Publish — the paid service that turns selected notes into a public, search-indexed website —
is deliberately not supported here, and the `publish:` frontmatter key is retired.**

**Two reasons, and the second is the one that decided it:**

**1 · The mistake cannot be taken back.** A note that reaches the open internet is cached, indexed and
possibly archived within hours. Removing it later removes the page, not the copies.

**2 · The word collides with what people actually mean.** *"Publish this"* means *"share it with my
team"* far more often than it means *"put it on the internet"* — and a skill that resolves that
ambiguity toward the public web is one confused sentence away from an unrecoverable disclosure.

> 🔴 **And a `publish: true` written today is dormant, not harmless.** It does nothing until someone
> subscribes to the service — and then every note carrying it goes live at once, from a decision nobody
> remembers making.

**If an owner genuinely wants a public site, that is a deliberate act they set up themselves, outside
this skill.**
