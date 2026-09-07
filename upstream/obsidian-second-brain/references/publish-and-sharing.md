# Publish & Sharing (OPTIONAL)

Your vault is private and local by default. Use this when the user wants to publish notes to the web or share them with a team/other tools.

## Obsidian Publish

Paid Obsidian service that hosts selected notes as a website.

**Setup:** Settings → Obsidian Publish → Connect → sign in → create/select a site → choose notes in the Publish panel.

**Control per note via frontmatter:**
```yaml
---
publish: true            # publish this note
publish: false           # keep private even if selected
title: "Custom Page Title"
description: "Meta description for SEO (≤150 chars)"
permalink: /custom-url
image: "https://example.com/og.jpg"
nav_order: 2
nav_exclude: false
---
```

**Notes:**
- Custom CSS via `publish.css` in the vault root; custom domain via a CNAME to `publish-main.obsidian.md`.
- Password protection and per-site analytics (Google/Plausible) available in site settings.
- **Limits:** community plugins and Dataview/Bases interactivity **do not run** on Publish — only static content renders. Supported files: `.md`, images, `.pdf`. 100MB/file.
- Because of this, write notes you intend to publish in **plain Markdown** (and keep `publish: false` as the default on private folders like `Personal/Journal/`).

**Safety:** never set `publish: true` on personal/journal/people notes — or money notes (funds/transactions) and engagements (they carry amounts and deal terms) — without explicit confirmation. When publishing, double-check the selected set excludes private domains.

## Sharing without Publish

- **Export a single note** to another format (Word/PDF/HTML): hand the Markdown to the `docx`/`pdf` skills if they're installed, or share the `.md` directly (it's portable plain text).
- **Team knowledge base** (Slite, Confluence, Notion, Google Docs): draft and refine in Obsidian (where Claude can help), then push the finished note out. Community sync plugins exist for some targets; otherwise export the Markdown and paste/import.
- **Selective sharing:** copy the specific note(s) rather than the vault. Strip private frontmatter/properties first if sharing externally.
- **Versioning/backup:** the Obsidian Git community plugin (or plain `git` in Claude Code) gives history and rollback — useful before any bulk change.

## Quick decision

| Want | Use |
|---|---|
| Public website of selected notes | Obsidian Publish |
| Send one note to someone | Export `.md` / convert to docx/pdf |
| Team wiki | Draft in Obsidian → push/export to the team tool |
| Backup & history | Git (plugin or CLI) |
