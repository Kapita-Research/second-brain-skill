# Version History (Git)

**OPTIONAL module.** A vault records when a note was *created* (`created:`) but nothing records when it was *revised*. Git closes that gap: a complete, dated, permanent history of every change, for free, entirely on the owner's machine.

Set this up when the owner asks "what did I work on?", wants to recover deleted content, worries about losing work, or is about to run a review that depends on knowing what changed. `retrieval-and-review.md` → *Activity reporting* explains how to **use** the history; this file is how to **install** it.

## What the vault can't tell you without it

| Question | Without git | With git |
|---|---|---|
| When was this note created? | `created:` frontmatter — reliable | same |
| When was it last edited? | filesystem mtime — lossy (see below) | exact, per revision |
| How many times was it revised? | unanswerable | exact |
| What did it say last month? | unanswerable | exact |
| I deleted a paragraph — get it back | unanswerable | trivial |
| What changed across the vault this quarter? | guesswork | one command |

**Why mtime is not a substitute.** It stores only the *latest* touch, so a note revised eight times is indistinguishable from one touched once; it is bumped by things that aren't the owner thinking (Obsidian rewriting properties, a dashboard write, an agent's bulk edit); and it is destroyed by any copy, move, or restore. A block of files sharing one timestamp to the minute is **one bulk operation, not N work sessions** — never present it as activity.

## Explaining it to a non-technical owner

Most vault owners are not developers. Lead with the mental model, not the vocabulary:

> Saving a file **overwrites** the old version — it's gone. A **commit** is a photo of the whole vault at one moment, added to an album that never deletes anything. Keep taking photos and you can walk back to any point: read what a note said three weeks ago, recover a deleted paragraph, or list everything that changed in a month.

Four things a commit carries: an ID (fingerprint), an author, a date, and a message the owner writes. Answer the three questions they always ask:

- *"Does each photo copy the whole vault?"* No. Git identifies files by content — unchanged files are referenced, not re-stored — then compresses, and later repacks versions as differences. **Measured on a real 288-note vault: 11 full snapshots occupied 1.9 MB, less than a single unpacked one.** Storage fear is the usual objection and it is unfounded for text.
- *"Is anything uploaded?"* No. Git is local by default. Nothing leaves the machine unless a remote is deliberately added.
- *"Can I undo it?"* Yes — deleting the `.git` folder restores exactly the prior state. Notes are never modified by git itself.

## Setup

```bash
cd "/path/to/vault"
git init -b main
git config user.name "Owner Name"          # repo-local, not --global
git config user.email "owner@example.com"
git config core.quotepath false            # show non-ASCII filenames readably (Arabic, CJK, accents)
```

`core.quotepath false` matters in any multilingual vault — without it git prints `\330\250...` escapes instead of the actual filename.

**`.gitignore` — write it before the first commit:**

```gitignore
# Attachments — images/PDFs. Large, don't compress, no useful diffs.
Attachments/

# macOS clutter
.DS_Store

# Obsidian: keep real config, ignore the noisy and the bulky.
.obsidian/workspace.json
.obsidian/graph.json.bak
.obsidian/plugins/
.obsidian/themes/

# The dashboard program installed by the skill's bootstrap (~100 KB, rewritten
# on every skill upgrade) and any .bak the upgrade leaves behind.
Maps/Dashboards/dashboard_server.py
Maps/Dashboards/Start Dashboard.command
Maps/Dashboards/Start Dashboard.bat
Maps/Dashboards/start-dashboard.sh
Maps/Dashboards/*.bak
```

The reasoning, which the owner should hear: **`Attachments/`** is binary — it inflates the repository and produces no readable diff. **`workspace.json`** records pane layout and changes every time a panel is dragged, so tracking it means constant meaningless commits. **`plugins/`/`themes/`** is third-party code that churns on update — and **`Maps/Dashboards/dashboard_server.py`** is the same story from a different direction: it lives inside the vault so the owner can double-click it, but it is the skill's program, not their notes, and every skill upgrade would otherwise commit another ~100 KB copy of it. But **keep `types.json`, `app.json`, `appearance.json`, `core-plugins.json`, `community-plugins.json`** — property types and the enabled-plugin list are real configuration worth versioning.

**If the repo already tracks the dashboard** (any vault whose git predates these lines): a `.gitignore` entry never untracks a file that is already committed, so for that vault the exclusions silently do nothing. Untrack it once —

```bash
git rm --cached --ignore-unmatch "Maps/Dashboards/dashboard_server.py" \
  "Maps/Dashboards/Start Dashboard.command" "Maps/Dashboards/Start Dashboard.bat" \
  "Maps/Dashboards/start-dashboard.sh"
git commit -m "stop tracking the dashboard program"
```

The files stay on disk and past copies stay in history (harmless); future upgrades just stop adding new ones. Installed elsewhere via `--dashboard-dir`? Point the ignore lines and this command at that folder instead.

Then the first commit:

```bash
git add -A && git commit -m "Initial snapshot of the vault"
```

**Verify before declaring success:** `git status --short` must be empty (everything captured), and `git ls-files | wc -l` should roughly match the note count. Confirm the exclusions actually applied — `git ls-files | grep -c Attachments/` must be `0`.

## Automating the snapshots

**This is the part that decides whether the module works.** A repository with one commit is no better than no repository. Manual commits do not survive contact with a real week — automate, or don't bother.

### Scheduled job (preferred — runs regardless of Obsidian)

Ship a script that commits **only when something changed**, so history has no empty noise:

```bash
#!/bin/bash
VAULT="/path/to/vault"; GIT=/usr/bin/git
LOG="$HOME/Library/Logs/vault-snapshot.log"
cd "$VAULT" || { echo "$(date '+%F %T')  ERROR: vault unreachable" >> "$LOG"; exit 1; }
[ -d .git ] || { echo "$(date '+%F %T')  ERROR: no .git in vault" >> "$LOG"; exit 1; }
STATUS=$("$GIT" status --porcelain) || {               # git FAILED — that is not "clean"
  echo "$(date '+%F %T')  ERROR: git status failed — see the error log" >> "$LOG"; exit 1; }
if [ -n "$STATUS" ]; then                              # nothing changed → no commit…
  COUNT=$(printf '%s\n' "$STATUS" | wc -l | tr -d ' ')
  "$GIT" add -A
  "$GIT" commit -q -m "Auto snapshot $(date '+%Y-%m-%d %H:%M') — $COUNT file(s) changed" \
    && echo "$(date '+%F %T')  committed $COUNT file(s)" >> "$LOG"
fi                                                     # …but keep going: the push must still run

# >>> If a remote is configured, the push block from "Pushing off-machine
# >>> automatically" (below) goes HERE — after this point, never inside the if.

if [ "$(date +%u)" = "7" ]; then "$GIT" gc --quiet --auto; fi   # weekly compaction
exit 0
```

**Two things in that script are deliberate.** The commit is wrapped in `if … fi` rather than exiting early when nothing changed, so the push below is always reached — see *Pushing off-machine automatically*. And the weekly `gc` is a full `if`, not `[ … ] && …`: as the last line of a script, the `&&` form makes every non-Sunday run exit **1**, which turns the exit status into noise exactly where you want it meaningful.

**Why the status check is written that way.** Capture `git status` once and **check its exit code** — do not inline it in a test. When git cannot read the vault at all it exits non-zero with *empty* output, so the obvious form (`[ -z "$(git status --porcelain)" ] && exit 0`) reads a hard failure as "nothing changed" and exits 0. That single line is what turns a broken job into a silent one; see *Full Disk Access* below for the failure it hides.

**macOS (launchd)** — `~/Library/LaunchAgents/com.<owner>.vault-snapshot.plist`, key `StartInterval` in seconds (`3600` = hourly), `ProgramArguments` = `/bin/bash` + the script path. Load it with `launchctl bootstrap gui/$(id -u) <plist>`; confirm with `launchctl list | grep vault-snapshot`. Use absolute paths throughout — launchd runs with a minimal `PATH`, so call `/usr/bin/git`, never bare `git`. If the Mac is asleep when a run is due, it runs shortly after waking.

**Linux (cron)** — `0 * * * * /path/to/vault-snapshot.sh`.

### macOS: Full Disk Access, or every run fails silently

**Check this before declaring the job working.** macOS restricts `~/Desktop`, `~/Documents`, `~/Downloads` and iCloud Drive under TCC. A launchd job runs the script through `/bin/bash`, which has **no** access to those folders by default — so if the vault lives in one of them, every run fails:

```
fatal: Unable to read current working directory: Operation not permitted
```

**Why nobody notices.** That message goes to the plist's `StandardErrorPath`. The snapshot log itself stays *empty* — no error line, no commit line, just nothing — and with the naive status check above, git's failure looks like "nothing changed", so the script exits **0**. Every health check then reports fine: the job is loaded, `launchctl list` shows last exit status `0`, and the log's most recent entry is a successful commit from before the break. Observed in the field: **six days** of no snapshots with nothing anywhere saying so, on a vault under `~/Desktop`.

**Grant it:** System Settings → Privacy & Security → **Full Disk Access** → `+` → in the file picker press **⌘⇧G** and enter `/bin/bash` (it is hidden) → enable it. Then `launchctl kickstart -k gui/$(id -u)/com.<owner>.vault-snapshot` and confirm a real commit appears in the log.

**Two things to set up so this is diagnosable next time:**
- Always give the plist a `StandardErrorPath`. Without it git's stderr is discarded and the only evidence of the failure is gone.
- Prefer a vault path outside the protected folders. Where the owner wants it on the Desktop, grant Full Disk Access **during setup** and verify with one real run — not at the first restore attempt.

### Obsidian Git plugin (alternative)

Community plugin, configured in the UI: set *Vault backup interval* to the desired minutes and turn **"Push on backup" OFF** when there is no remote, or it throws an error notification on every run.

**Its one real limitation, which decides the interval:** the plugin's timer runs **only while Obsidian is open**. It starts when the app launches and stops when it quits. So a 6-hour interval only ever fires if the owner leaves Obsidian running 6 continuous hours — with typical two-hour sessions it may fire rarely or never, and they will believe they have history when they don't. At 10–60 minutes the problem is invisible. **If the owner wants a long interval, use the scheduled job instead** — it runs on the clock regardless of the app.

### Choosing an interval

Frame the trade-off honestly, then let the owner choose:

- **Shorter (10–30 min)** — less unrecoverable work; more commits to read through.
- **Longer (1–6 h)** — cleaner history with fewer half-finished intermediate states; a whole session's rewriting can be lost.
- **The real cost is not "temporary files."** It is *finished work sitting unrecorded*. Cut three paragraphs from a memo with no snapshot since morning and they are gone. Say this plainly — owners often reason about the interval as if it only affected scratch work.
- Storage does not depend on the interval in any meaningful way. Don't let it drive the decision.

**Default recommendation: hourly, via the scheduled job.** Enough granularity for any review question, few enough commits to read, no dependence on the app being open.

## Privacy — the hard rule

**Never add a public remote.** A second-brain vault typically contains client NDAs, salary and grading data, contact details for dozens of real people, private journals, and financial records. Golden Rule 11 applies to the repository exactly as it applies to the notes.

- Local-only is the default and is sufficient for version history. Say so explicitly — owners hear "git" and think "GitHub".
- If the owner wants off-machine backup, it must be a **private** repository, and the exclusion list gets reviewed against `domain: personal`, `Money/`, and `Personal/Journal/` **before** the first push. Confirm explicitly (Golden Rule 10) — pushing publishes, and a deleted public repo can still be cached or indexed.
- A repository that has ever been pushed cannot be un-published by deleting it.

### Pushing off-machine automatically

Only once the owner has confirmed a **private** remote and the exclusions have been reviewed. The decision is above; this is what makes it reliable unattended:

```bash
export GIT_TERMINAL_PROMPT=0     # fail and log; never hang on a prompt no one can see

# Runs even when nothing was committed this hour, so a push that failed earlier
# (offline, asleep, GitHub down) is retried instead of leaving the remote behind.
if ! "$GIT" rev-parse --abbrev-ref '@{u}' >/dev/null 2>&1; then
  echo "$(date '+%F %T')  WARNING: no upstream branch — nothing is being pushed" >> "$LOG"
else
  AHEAD=$("$GIT" rev-list --count '@{u}..HEAD' 2>/dev/null || echo 0)
  if [ "${AHEAD:-0}" -gt 0 ]; then
    if PUSH_OUT=$("$GIT" push origin HEAD 2>&1); then
      echo "$(date '+%F %T')  pushed $AHEAD commit(s) to origin" >> "$LOG"
    else
      echo "$(date '+%F %T')  ERROR: push failed — $AHEAD commit(s) still local only — $(echo "$PUSH_OUT" | tr '\n' ' ' | cut -c1-300)" >> "$LOG"
    fi
  fi
fi
```

Four properties worth keeping, each of them load-bearing:

- **The push is not conditional on this run having committed.** The obvious design exits early when nothing changed — which means one failed push leaves the remote permanently behind while the log goes on looking healthy. Gating on *"is the branch ahead of its upstream"* instead makes every run a retry, so the backlog clears itself as soon as the network returns.
- **`GIT_TERMINAL_PROMPT=0`.** Unattended, a credential prompt is an invisible hang, not an error. Fail loudly instead.
- **Credentials from the OS keychain.** git's `osxkeychain` helper lives under `/usr/bin`, so it works inside launchd's minimal `PATH` with no dependency on Homebrew. Do not put a token in the script.
- **Log the failure with the count still local.** *"push failed — 3 commit(s) still local only"* tells the owner what is at risk; a bare "push failed" does not.

Tell the owner plainly what changes: **every edit now leaves the machine within the hour, automatically.** That is the point of it, and it is also the reason the exclusion review happens before the first push and not after.

## It is not retroactive

Git starts recording the day it is enabled. It cannot reconstruct history that was never captured. Say this out loud when setting it up, especially if the owner's motivating question was about the past — the honest answer is that the current question gets reconstructed from `created:` dates and task-body logs (see `retrieval-and-review.md` → *Activity reporting*), and the *next* one gets a real answer.

## Using the history

```bash
git log --oneline                                  # every snapshot
git log --since="3 weeks ago" --name-only          # what changed, by file
git log --since="3 weeks ago" --pretty=format:'%ad %s' --date=short
git log --follow -p -- "Tasks/Some Task.md"        # one note's full revision history
git show <id>:"path/to/note.md"                    # that note as it was at that snapshot
git diff <id> HEAD --stat                          # everything since a point in time
git restore "path/to/note.md"                      # undo uncommitted changes to a note
```

To recover deleted content: find the snapshot with `git log`, read the old version with `git show`, and **copy the wanted passage into the current note** rather than reverting the whole file — the rest of the note has usually moved on.

## Verifying and removing

```bash
launchctl list | grep vault-snapshot               # registered? (2nd column = last exit status)
tail ~/Library/Logs/vault-snapshot.log             # did it run, what did it commit
tail ~/Library/Logs/vault-snapshot.error.log       # THE one that shows a failing run
git status -sb                                     # is the remote behind? (ahead/behind)
git log -1 --date=relative --pretty='%ad  %s'      # when was the last snapshot
```

**If the last snapshot is old, do not conclude the job isn't running** — the more common case is a job that runs on schedule and fails every time. A loaded job and an exit status of `0` both prove nothing. Read the **error log** first: `Operation not permitted` means Full Disk Access (above), not a broken schedule. To remove entirely: `launchctl bootout gui/$(id -u)/com.<owner>.vault-snapshot`, delete the plist, and (if wanted) delete `.git`.

## The `modified:` alternative

A `modified:` frontmatter property is the low-tech option: visible inside Obsidian, queryable in a Base, no tooling. It is strictly weaker — it records *that* a note changed and when, not *what* changed, keeps only the most recent time, and depends on discipline nothing enforces. Offer it when the owner won't run a background job, or alongside git when they want the date visible in dashboards. It is not a substitute.

## Know its ceiling

- **It records files, not thinking.** A commit shows a note changed; it can't say whether that was an hour of work or a typo. Task-body status logs remain the better evidence of what was actually accomplished.
- **It cannot see work done outside the vault** — a deck built on disk, an email sent, a meeting held. Those enter the history only when a note about them does.
- **It is not a backup.** The repository sits on the same disk as the vault; a drive failure takes both. It protects against *editing* mistakes, not hardware loss. Say so if the owner starts treating it as one.
- **Rule 12 still applies.** The snapshot job writes nothing to notes — it only reads and commits — so it is safe alongside an open Obsidian, unlike the dashboard's write path.
