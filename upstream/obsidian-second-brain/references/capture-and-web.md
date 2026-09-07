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

## Quick-capture patterns

- **Plain thought:** drop it in `Inbox/` as above. Give it a short descriptive filename.
- **Into today's note:** if it's a log-type item, append to `Daily/YYYY-MM-DD.md` under `## 💭 Notes & captures`.
- **A task:** if it's a tracked to-do, make a **task note** in `Tasks/` (`type: task`, `status: not-started`, link `source:`/`people:`/`projects:`); a trivial sub-step can stay an inline `- [ ]` in the relevant note. See `note-types.md` → *Task*.
- **A link:** capture the URL now; fetch/clean the content at processing time (below).
- **Claude Code:** `obsidian daily:append content="- captured idea"` or `obsidian create name="Idea — X" content="..." silent` (see `cli-and-automation.md`).

## Processing the inbox (triage in action)

Run when the user says "process my inbox" or during daily/weekly review. For each item:

1. Read it. Decide its **type** and **domain** (work/personal/shared).
2. Apply the **triage tree** (SKILL.md / `vault-structure.md`) to pick the folder.
3. **Search before you create.** Check whether a target note already exists (the person, project, or topic). If it does, append/merge into it; only create a new note when none exists. This prevents duplicate entities that fragment the vault.
4. Upgrade frontmatter to the full schema for that type (`note-types.md`); set the real `type` and remove `status: needs-triage`.
5. **Link it** — to a MOC and/or related notes. If a source spawned a durable idea, split that idea into an atomic note in `Resources/Notes/`.
6. Rename to a clear, human-readable title (match existing naming; reuse aliases so mentions resolve).
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

## After any capture

- It's in a known place (folder or explicitly `Inbox/`).
- Frontmatter is consistent (or flagged `needs-triage`).
- For sources: summarized in your words + linked, not dumped wholesale.

## Dictated & multilingual capture

Voice-dictated and machine-transcribed input (meeting recaps, voice notes — any language) is a first-class capture source, and it arrives *dirty*: names mangled, fillers everywhere, sometimes mixed languages. Normalize before writing anything to the vault:

1. **Extract, don't transcribe.** Pull the entities and facts (who, what, decisions, action items); drop fillers and false starts. Keep meaningful original-language phrases as quotes where nuance matters.
2. **Resolve every name against the vault** (Golden Rule 2): search People note names *and* `aliases` before writing any name. Transcripts misspell — "sara chen" is probably `[[Sarah Chen]]`. Always link the canonical note name.
3. **Ambiguous match → ask, never guess.** Two plausible people ("which Hussain?") means one quick question to the user, or an explicit flag in the note — not a silent pick.
4. **New variant → record it.** When a transcript teaches you a new spelling of an existing person, add it to that note's `aliases` so the next transcript resolves automatically.
5. **Then capture normally** — triage tree, frontmatter, Golden Rule 7 for action items, `last-contact` for attendees.
