#!/usr/bin/env python3
"""Live dashboard server for an obsidian-second-brain vault (stdlib only).

Usage:
    python3 dashboard_server.py [vault] [--port 8787] [--vault-name NAME] [--open]

Serves the interactive dashboard at http://127.0.0.1:<port>/ :
  GET  /            the dashboard app — tabbed UI (All Tasks · one tab per
                    company · Personal · Overview) with a hideable in-tab view
                    bar (Table / By Project / By Status / By Assignee / By Due,
                    + By Company on All Tasks), a sticky tab bar, a light/dark/
                    auto theme toggle (dark = warm charcoal palette), per-column
                    header filters, column show/hide, and sorting
  GET  /api/health  identity probe (used for idempotent relaunch)
  GET  /api/data    live JSON snapshot of the vault (re-scanned per request)
  POST /api/status  update a note's frontmatter status (task / engagement /
                    project), append a dated log line to the body, and — for
                    recurring tasks marked done — advance `due` instead.
  POST /api/due     set, change, or clear a task/project `due:` date
                    (clearing a due date also blanks a filled `due_time:`)
  POST /api/field   set or clear a task's scalar `priority:`, `company:`, or
                    `due_time:` (a due time needs a due date to hang off)
  POST /api/assign  rewrite a task's `projects:` or `assignee:` wikilink list

Safety: writes are atomic (same-dir temp file + os.replace), confined to the
edited key's lines in the first frontmatter block plus one inserted log
bullet, guarded by an mtime conflict check (HTTP 409) and a global write
lock. List writes only accept link targets that resolve to existing notes
(targets already present on the note are tolerated, so a pre-existing broken
link never blocks an edit). Binds to 127.0.0.1 only. Fully self-contained —
no companion scripts.
"""
import argparse, calendar, datetime, json, os, pathlib, re, sys, tempfile, threading, urllib.parse, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = pathlib.Path(__file__).resolve().parent

APP_ID = "sb-dashboard"
VERSION = "2.8.0"

VOCAB = {
    # order is the lifecycle order — status pills, menus, and sorting all read it
    "task": ["not-started", "in-progress", "in-review", "done", "on-hold", "cancelled"],
    "engagement": ["lead", "talking", "proposal", "active", "on-hold", "done", "lost"],
    "project": ["idea", "planning", "active", "on-hold", "done", "archived"],
}
TASK_LOG_LABEL = {"done": "Done", "cancelled": "Cancelled", "in-progress": "Started",
                  "in-review": "Submitted for review", "on-hold": "On hold",
                  "not-started": "Reopened"}
DUE_TYPES = ("task", "project")  # note types whose `due:` the dashboard may edit
# task list keys the dashboard may rewrite, with their body-log labels
LIST_KEYS = {"projects": {"set": "Projects set", "clear": "Projects cleared"},
             "assignee": {"set": "Assigned", "clear": "Unassigned"}}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")  # 24-hour HH:mm

# Scalar task fields the dashboard may set, in one line each:
#   values  allowed literals, or None when `apply_scalar_change` validates them
#   link    the value is a note title, written as a quoted "[[…]]" wikilink
#   quote   wrap the written value in double quotes (YAML 1.1 reads a bare
#           15:00 as sexagesimal, and the vault templates quote it anyway)
#   anchors where to insert the key line on a note that lacks it — first match
#           wins, mirroring the frontmatter order in Templates/Task Template.md
#   log     (set, clear) labels for the dated body bullet
SCALAR_KEYS = {
    "priority": {"values": ("high", "normal", "low"), "link": False, "quote": False,
                 "anchors": [("before", "due"), ("after", "company"),
                             ("after", "domain"), ("after", "status")],
                 "log": ("Priority set", "Priority cleared")},
    "company":  {"values": None, "link": True, "quote": True,
                 "anchors": [("before", "priority"), ("before", "due"),
                             ("after", "domain"), ("after", "status")],
                 "log": ("Company set", "Company cleared")},
    "due_time": {"values": None, "link": False, "quote": True,
                 "anchors": [("after", "due"), ("after", "priority"),
                             ("after", "status")],
                 "log": ("Due time set", "Due time cleared")},
}

WRITE_LOCK = threading.Lock()


# ---------------------------------------------------------------- frontmatter
# Line-level parser (not a YAML library): flat `key: value` plus simple `- `
# block lists, one layer of surrounding quotes stripped. Shared convention
# with the vault templates; nested YAML is out of scope.

def fm(text):
    # exact fences only (trailing blanks tolerated) — keep in sync with _split_note,
    # which must agree on where the frontmatter ends before any rewrite
    m = re.match(r"^---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(\r?\n|$)", text, re.S)
    if not m: return {}
    d, key = {}, None
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if km:
            key, v = km.group(1), km.group(2).strip().strip('"').strip("'")
            d[key] = v if v not in ("", "[]") else ([] if v == "[]" else v)
            if isinstance(d[key], str) and not d[key]: d[key] = ""
        elif key and re.match(r"^\s*- ", line) and (isinstance(d.get(key), list) or d.get(key) in ("", None)):
            if not isinstance(d.get(key), list): d[key] = []
            d[key].append(line.strip()[2:].strip().strip('"').strip("'"))
    return d


def links_of(v):
    out = []
    for s in (v if isinstance(v, list) else [v] if isinstance(v, str) else []):
        out += re.findall(r"\[\[([^\]|#]+)", s or "")
    return [x.strip() for x in out if x.strip()]


class ChangeError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code, self.message = code, message


# ---------------------------------------------------------------- write engine

def advance_due(due, recurrence, today):
    """Next occurrence strictly after `today`. Month-based steps keep the
    original day-of-month anchor (Jan 31 monthly → Feb 28 → Mar 31, not Mar 28)."""
    anchor = due.day
    def add_months(d, n):
        y, m = divmod(d.month - 1 + n, 12)
        y, m = d.year + y, m + 1
        return datetime.date(y, m, min(anchor, calendar.monthrange(y, m)[1]))
    step = {"daily": lambda d: d + datetime.timedelta(days=1),
            "weekly": lambda d: d + datetime.timedelta(days=7),
            "monthly": lambda d: add_months(d, 1),
            "quarterly": lambda d: add_months(d, 3),
            "yearly": lambda d: add_months(d, 12)}.get(recurrence)
    if not step:
        return None
    nxt = step(due)
    while nxt <= today:
        nxt = step(nxt)
    return nxt


def _find_key_line(lines, end, key):
    """Index of the first `key:` line inside the frontmatter block, else None."""
    pat = re.compile(r"^" + re.escape(key) + r":")
    for i in range(1, end):
        if pat.match(lines[i]):
            return i
    return None


def _require_single_key(lines, end, key):
    """Refuse to edit a note whose frontmatter repeats `key:` — the parser
    honors the LAST occurrence while the rewriter edits the FIRST, so an
    edit would report success without taking effect."""
    pat = re.compile(r"^" + re.escape(key) + r":")
    if sum(1 for i in range(1, end) if pat.match(lines[i])) > 1:
        raise ChangeError(422, f"duplicate '{key}:' in frontmatter — fix the note "
                          "in Obsidian first")


def _block_span_end(lines, ki, end):
    """Index just past lines[ki]'s key line plus its `- ` continuation lines.
    Blank lines are part of the block only when another bullet follows —
    mirroring fm(), which ignores blanks between bullets."""
    j = ki + 1
    while j < end:
        if re.match(r"^\s*- ", lines[j]):
            j += 1
            continue
        if not lines[j].strip():
            k = j
            while k < end and not lines[k].strip():
                k += 1
            if k < end and re.match(r"^\s*- ", lines[k]):
                j = k + 1
                continue
        break
    return j


def _set_key_line(lines, idx, value):
    """Replace the value on a `key: value` line, preserving key, spacing, EOL."""
    m = re.match(r"^([A-Za-z_][\w-]*:)([ \t]*)(.*?)(\r?\n)?$", lines[idx])
    head, pad, eol = m.group(1), m.group(2) or " ", m.group(4) or ""
    lines[idx] = head + pad + value + eol


def _insert_log_line(lines, end, log_line, eol):
    """Insert as the first bullet under `## Steps` (vault convention),
    falling back to `## Notes`, then to appending at EOF."""
    for heading in ("Steps", "Notes"):
        pat = re.compile(r"^##\s+" + heading + r"\b")
        for i in range(end + 1, len(lines)):
            if pat.match(lines[i]):
                j = i + 1
                if j < len(lines) and lines[j].strip() == "":
                    j += 1
                if not lines[j - 1].endswith("\n"):  # heading/blank is last line, no EOL
                    lines[j - 1] += eol
                lines.insert(j, log_line + eol)
                return
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += eol
    lines.append(log_line + eol)


def _split_note(text):
    """(frontmatter dict, keepends lines, closing-fence index, eol) or ChangeError."""
    d = fm(text)
    if not d:
        raise ChangeError(422, "note has no frontmatter")
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip() != "---":
        raise ChangeError(422, "no frontmatter block")
    end = next((i for i in range(1, len(lines)) if lines[i].rstrip() == "---"), None)
    if end is None:
        raise ChangeError(422, "unterminated frontmatter block")
    eol = "\r\n" if "\r\n" in lines[0] else "\n"
    return d, lines, end, eol


def apply_status_change(text, new_status, today=None, log=True):
    """Pure function: (note text, new status) -> (new text, result meta).

    Only ever touches the `status:` (or, for recurring completions, `due:`)
    line of the first frontmatter block, plus one inserted body bullet.
    Raises ChangeError for anything it can't do faithfully.
    """
    d, lines, end, eol = _split_note(text)
    ntype = str(d.get("type") or "")
    vocab = VOCAB.get(ntype)
    if not vocab:
        raise ChangeError(422, f"status editing is not supported for type '{ntype or '?'}'")
    if new_status not in vocab:
        raise ChangeError(422, f"'{new_status}' is not a valid {ntype} status")
    today = today or datetime.date.today()
    tstr = today.isoformat()

    meta = {"recurred": False, "status": new_status, "due": str(d.get("due") or "")}
    recurred = False
    # Recurring task marked done: advance `due`, leave `status` (vault CLAUDE.md rule).
    # If the recurrence can't be advanced faithfully, refuse rather than silently
    # marking the task done and killing the recurrence.
    if ntype == "task" and new_status == "done" and str(d.get("recurrence") or "").strip():
        rec_word = str(d["recurrence"]).strip().lower()
        due_s = str(d.get("due") or "")
        nxt = (advance_due(datetime.date.fromisoformat(due_s), rec_word, today)
               if DATE_RE.match(due_s) else None)
        _require_single_key(lines, end, "due")
        idx = _find_key_line(lines, end, "due")
        if nxt is None or idx is None:
            raise ChangeError(422, "recurring task can't advance: it needs due 'YYYY-MM-DD' "
                              "and recurrence daily|weekly|monthly|quarterly|yearly "
                              f"(found due='{due_s}', recurrence='{rec_word}') — fix the "
                              "note in Obsidian first")
        _set_key_line(lines, idx, nxt.isoformat())
        recurred = True
        meta.update(recurred=True, status=str(d.get("status") or ""), due=nxt.isoformat())
    if not recurred:
        if isinstance(d.get("status"), list):  # same orphaned-continuation hazard
            raise ChangeError(422, "status is a YAML list in this note — fix it in "
                              "Obsidian first")
        _require_single_key(lines, end, "status")
        idx = _find_key_line(lines, end, "status")
        if idx is None:
            raise ChangeError(422, "no 'status:' line in frontmatter")
        _set_key_line(lines, idx, new_status)

    if log:
        if ntype == "task":
            log_line = (f"- **Done {tstr} → next due {meta['due']}.**" if recurred
                        else f"- **{TASK_LOG_LABEL[new_status]} {tstr}.**")
        else:
            log_line = f"- **Moved to {new_status} {tstr}.**"
        _insert_log_line(lines, end, log_line, eol)
        meta["log_line"] = log_line
    return "".join(lines), meta


def apply_due_change(text, new_due, today=None, log=True):
    """Pure function: set, change, or clear a task/project note's `due:` date.

    new_due is '' (clear) or 'YYYY-MM-DD'. Clearing also blanks a filled
    `due_time:` (a time without a date is meaningless). Touches only the
    `due:`/`due_time:` frontmatter lines plus one inserted body bullet.
    Returns the input text unchanged when there is nothing to do.
    """
    d, lines, end, eol = _split_note(text)
    ntype = str(d.get("type") or "")
    if ntype not in DUE_TYPES:
        raise ChangeError(422, f"due editing is not supported for type '{ntype or '?'}'")
    # a YAML list under due/due_time spans continuation lines this line-level
    # editor can't rewrite faithfully — orphaned items would corrupt the block
    if isinstance(d.get("due"), list) or isinstance(d.get("due_time"), list):
        raise ChangeError(422, "due/due_time is a YAML list in this note — fix it in "
                          "Obsidian first")
    new_due = str(new_due or "").strip()
    if new_due:
        if not DATE_RE.match(new_due):
            raise ChangeError(422, f"'{new_due}' is not a YYYY-MM-DD date")
        try:
            parsed = datetime.date.fromisoformat(new_due)
        except ValueError:
            raise ChangeError(422, f"'{new_due}' is not a real calendar date")
        if not (1970 <= parsed.year <= 2100):  # backstop against half-typed years
            raise ChangeError(422, f"'{new_due}' looks wrong — year must be 1970–2100")
    elif ntype == "task" and str(d.get("recurrence") or "").strip():
        raise ChangeError(422, "this task recurs — clearing its due date would break the "
                          "recurrence; clear 'recurrence:' in Obsidian first")
    today = today or datetime.date.today()
    tstr = today.isoformat()

    old_due = str(d.get("due") or "")
    due_time = str(d.get("due_time") or "")
    meta = {"due": new_due, "due_time": due_time}
    if old_due == new_due:
        meta["noop"] = True
        return text, meta

    _require_single_key(lines, end, "due")
    _require_single_key(lines, end, "due_time")
    idx = _find_key_line(lines, end, "due")
    if idx is not None:
        _set_key_line(lines, idx, new_due)
    elif new_due:
        # no `due:` line yet — insert one where the template puts it
        new_line = f"due: {new_due}{eol}"
        anchor = _find_key_line(lines, end, "due_time")
        if anchor is not None:
            lines.insert(anchor, new_line)
        else:
            for key in ("priority", "status", "type"):
                k = _find_key_line(lines, end, key)
                if k is not None:
                    # skip the anchor's continuation lines — same block-aware
                    # rule as apply_list_change's insert path
                    lines.insert(_block_span_end(lines, k, end), new_line)
                    break
            else:
                lines.insert(end, new_line)
    else:  # clearing, but there is no due line at all
        meta["noop"] = True
        return text, meta

    if not new_due and due_time:  # a time without a date is meaningless
        ti = _find_key_line(lines, end, "due_time")
        if ti is not None:
            _set_key_line(lines, ti, "")
            meta["due_time"] = ""

    if log:
        log_line = (f"- **Rescheduled {tstr}: due {old_due or '—'} → {new_due}.**" if new_due
                    else f"- **Due cleared {tstr}.**")
        _insert_log_line(lines, end, log_line, eol)
        meta["log_line"] = log_line
    return "".join(lines), meta


def apply_scalar_change(text, key, value, today=None, log=True, known=None):
    """Pure function: set or clear one of a task's scalar frontmatter fields
    (`priority:`, `company:`, `due_time:` — see SCALAR_KEYS).

    `value` is '' (clear) or the new value; for `company` it is a note title,
    with or without [[ ]]. Touches only that key's line — rewritten in place,
    or inserted at its template position when the note lacks it — plus one
    inserted body bullet. Returns the input text unchanged when nothing moves.
    """
    spec = SCALAR_KEYS.get(key)
    if spec is None:
        raise ChangeError(422, f"'{key}' is not an editable field")
    d, lines, end, eol = _split_note(text)
    ntype = str(d.get("type") or "")
    if ntype != "task":
        raise ChangeError(422, f"{key} editing is only supported for tasks "
                          f"(this note is type '{ntype or '?'}')")
    # a YAML list under the key spans continuation lines this line-level editor
    # can't rewrite faithfully — orphaned items would corrupt the block
    if isinstance(d.get(key), list):
        raise ChangeError(422, f"{key} is a YAML list in this note — fix it in "
                          "Obsidian first")

    value = str(value or "").strip()
    if spec["link"] and value.startswith("[[") and value.endswith("]]"):
        value = value[2:-2].strip()
    if value:
        if spec["values"] is not None and value not in spec["values"]:
            raise ChangeError(422, f"'{value}' is not a valid {key} "
                              f"({' | '.join(spec['values'])})")
        if key == "due_time":
            if not TIME_RE.match(value):
                raise ChangeError(422, f"'{value}' is not a 24-hour HH:mm time")
            if not str(d.get("due") or "").strip():
                raise ChangeError(422, "this task has no due date — set one before a "
                                  "due time (a time without a date is meaningless)")
        if spec["link"]:
            # any quote, bracket, or backslash breaks the quoted "[[...]]" form
            if re.search(r'["\\\[\]\r\n|#]', value):
                raise ChangeError(422, f"invalid link target: {value!r}")
            if known is not None and value not in known:
                raise ChangeError(422, f"no note named: {value} — create it in "
                                  "Obsidian first")
    today = today or datetime.date.today()
    tstr = today.isoformat()

    current = (links_of(d.get(key)) or [""])[0] if spec["link"] \
        else str(d.get(key) or "").strip()
    meta = {"key": key, "value": value}
    if current == value:
        meta["noop"] = True
        return text, meta

    _require_single_key(lines, end, key)
    written = ""
    if value:
        inner = f"[[{value}]]" if spec["link"] else value
        written = f'"{inner}"' if spec["quote"] else inner
    idx = _find_key_line(lines, end, key)
    if idx is not None:
        _set_key_line(lines, idx, written)
    elif value:
        pos = None
        for where, k in spec["anchors"]:
            ki = _find_key_line(lines, end, k)
            if ki is not None:
                # "after" must clear the anchor's own `- ` continuation lines,
                # or the insert would split the anchor's block list
                pos = ki if where == "before" else _block_span_end(lines, ki, end)
                break
        lines.insert(end if pos is None else pos, f"{key}: {written}{eol}")
        end += 1
    else:  # clearing, but there is no such line at all
        meta["noop"] = True
        return text, meta

    if log:
        set_lbl, clear_lbl = spec["log"]
        shown = f"[[{value}]]" if spec["link"] else value
        log_line = (f"- **{set_lbl} {tstr}: {shown}.**" if value
                    else f"- **{clear_lbl} {tstr}.**")
        _insert_log_line(lines, end, log_line, eol)
        meta["log_line"] = log_line
    return "".join(lines), meta


def apply_list_change(text, key, values, today=None, log=True, known=None):
    """Pure function: rewrite a task's `projects:` or `assignee:` wikilink list.

    `values` is a list of note titles (with or without [[ ]]). The whole key
    block (key line + its `- ` continuation lines) is replaced with a quoted
    block list, or `key: []` when cleared. When `known` (a set of existing
    note stems) is given, every target must resolve to it. Returns the input
    text unchanged when the list already matches.
    """
    if key not in LIST_KEYS:
        raise ChangeError(422, f"'{key}' is not an editable list field")
    d, lines, end, eol = _split_note(text)
    ntype = str(d.get("type") or "")
    if ntype != "task":
        raise ChangeError(422, f"{key} editing is only supported for tasks "
                          f"(this note is type '{ntype or '?'}')")

    clean = []
    for v in values:
        v = str(v or "").strip()
        if v.startswith("[[") and v.endswith("]]"):
            v = v[2:-2].strip()
        if not v:
            continue
        # any quote, bracket, or backslash breaks the quoted "[[...]]" form
        if re.search(r'["\\\[\]\r\n|#]', v):
            raise ChangeError(422, f"invalid link target: {v!r}")
        if v not in clean:
            clean.append(v)
    current = links_of(d.get(key))
    if known is not None:
        # tolerate values already on the note — a pre-existing broken link must
        # not block editing the rest of the list
        missing = [v for v in clean if v not in known and v not in current]
        if missing:
            raise ChangeError(422, "no note named: " + ", ".join(missing) +
                              " — create it in Obsidian first")

    today = today or datetime.date.today()
    tstr = today.isoformat()
    meta = {"key": key, "values": clean}
    if clean == current:
        meta["noop"] = True
        return text, meta

    _require_single_key(lines, end, key)
    idx = _find_key_line(lines, end, key)
    if idx is not None:
        # frontmatter `- ` lines always belong to the nearest preceding key,
        # so everything up to the next `key:` line is this key's block
        j = _block_span_end(lines, idx, end)
        del lines[idx:j]
        end -= j - idx
    else:
        # no such key yet — insert at the canonical spot near its siblings
        anchors = {"assignee": [("before", "projects"), ("after", "recurrence"),
                                ("after", "due_time"), ("after", "priority"),
                                ("after", "status")],
                   "projects": [("after", "assignee"), ("before", "people"),
                                ("after", "recurrence"), ("after", "status")]}
        idx = None
        for where, k in anchors.get(key, []):
            ki = _find_key_line(lines, end, k)
            if ki is not None:
                # "after" must clear the anchor's own `- ` continuation lines,
                # or the insert would split the anchor's block list
                idx = ki if where == "before" else _block_span_end(lines, ki, end)
                break
        if idx is None:
            idx = end
    block = ([f"{key}:{eol}"] + [f'  - "[[{v}]]"{eol}' for v in clean]) if clean \
        else [f"{key}: []{eol}"]
    lines[idx:idx] = block
    end += len(block)

    if log:
        labels = LIST_KEYS[key]
        names = ", ".join(f"[[{v}]]" for v in clean)
        log_line = (f"- **{labels['set']} {tstr}: {names}.**" if clean
                    else f"- **{labels['clear']} {tstr}.**")
        _insert_log_line(lines, end, log_line, eol)
        meta["log_line"] = log_line
    return "".join(lines), meta


def atomic_write(path, text):
    st = path.stat()
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".sbdash-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp, st.st_mode & 0o777)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


# ---------------------------------------------------------------- vault scan

def _skip(rel):
    return rel.parts[0] in (".obsidian", "Templates") or ".trash" in rel.parts


def scan(vault):
    """[(rel_path, frontmatter_dict, mtime_ns)]."""
    notes = []
    for p in sorted(vault.rglob("*.md")):
        rel = p.relative_to(vault)
        if _skip(rel):
            continue
        try:
            mt = p.stat().st_mtime_ns  # stat BEFORE read: a racing edit then 409s (safe side)
            d = fm(p.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        if d:
            notes.append((rel, d, mt))
    return notes


def note_stems(vault):
    """Existing note titles — the valid wikilink targets for list writes."""
    stems = set()
    for p in vault.rglob("*.md"):
        rel = p.relative_to(vault)
        if not _skip(rel):
            stems.add(p.stem)
    return stems


def build_data(vault, name):
    today = datetime.date.today().isoformat()
    notes = scan(vault)

    def obs(rel):
        return (f"obsidian://open?vault={urllib.parse.quote(name)}"
                f"&file={urllib.parse.quote(str(rel.with_suffix('')))}")

    def s(v):  # frontmatter scalar -> str
        return str(v).strip() if isinstance(v, (str, int, float)) else ""

    tasks, engagements, projects, orgs, txns, meetings, people = [], [], [], [], [], [], []
    for rel, d, mt in notes:
        t = d.get("type")
        if t == "task":
            due, status = s(d.get("due")), s(d.get("status"))
            src = links_of(d.get("source")) or ([s(d.get("source"))] if s(d.get("source")) else [])
            tasks.append({
                "vtype": "task", "path": str(rel), "title": rel.stem, "url": obs(rel),
                "status": status, "priority": s(d.get("priority")), "due": due,
                "due_time": s(d.get("due_time")), "domain": s(d.get("domain")),
                "recurrence": s(d.get("recurrence")), "created": s(d.get("created")),
                "company": links_of(d.get("company")),
                "assignee": links_of(d.get("assignee")),
                "projects": links_of(d.get("projects")), "people": links_of(d.get("people")),
                "parent": links_of(d.get("parent-task")),
                "blocked_by": links_of(d.get("blocked-by")),
                "related": links_of(d.get("related")), "source": src,
                "overdue": bool(DATE_RE.match(due)) and due < today
                           and status not in ("done", "cancelled"),
                # str, not int: 19-digit mtimes exceed JS's safe-integer range
                "mtime_ns": str(mt),
            })
        elif t == "engagement":
            engagements.append({
                "vtype": "engagement", "path": str(rel), "title": rel.stem, "url": obs(rel),
                "status": s(d.get("status")), "org": links_of(d.get("org")),
                "value": s(d.get("value")), "owner": links_of(d.get("owner")),
                "mtime_ns": str(mt),
            })
        elif t == "project":
            projects.append({
                "vtype": "project", "path": str(rel), "title": rel.stem, "url": obs(rel),
                "status": s(d.get("status")), "domain": s(d.get("domain")),
                "due": s(d.get("due")), "people": links_of(d.get("people")),
                "mtime_ns": str(mt),
            })
        elif t == "business":
            orgs.append({"title": rel.stem, "url": obs(rel),
                         "relationship": s(d.get("relationship")), "sector": s(d.get("sector"))})
        elif t == "transaction" and s(d.get("status")) != "cancelled":
            txns.append(d)
        elif t == "meeting":
            meetings.append({"title": rel.stem, "url": obs(rel), "created": s(d.get("created")),
                             "people": links_of(d.get("people"))})
        elif t == "person":
            people.append({"title": rel.stem, "url": obs(rel), "job_title": s(d.get("job_title")),
                           "groups": links_of(d.get("groups")),
                           "last_contact": s(d.get("last-contact"))})

    po = {"high": 0, "normal": 1, "medium": 1, "low": 2}
    tasks.sort(key=lambda t: (po.get(t["priority"].lower(), 3), t["due"] or "9999",
                              t["title"].lower()))
    so = {"lead": 0, "talking": 1, "proposal": 2, "active": 3, "on-hold": 4}
    engagements.sort(key=lambda e: (so.get(e["status"], 9), e["title"].lower()))
    projects.sort(key=lambda p: p["title"].lower())
    orgs.sort(key=lambda o: o["title"].lower())
    meetings.sort(key=lambda m: m["created"], reverse=True)
    people.sort(key=lambda p: p["title"].lower())

    funds = {}
    for d in txns:
        f = ", ".join(links_of(d.get("fund"))) or "(no fund)"
        cur = str(d.get("currency", "") or "?")
        try:
            amt = float(str(d.get("amount", "0")).replace(",", "") or 0)
        except ValueError:
            amt = 0.0
        cash, recv, pledge = funds.setdefault((f, cur), [0.0, 0.0, 0.0])
        dr, st = d.get("direction"), d.get("status")
        if dr == "in" and st == "outstanding":
            pledge += amt
        elif dr == "in":
            cash += amt
        elif dr == "out":
            cash -= amt
            if st == "outstanding":
                recv += amt
        funds[(f, cur)] = [cash, recv, pledge]

    return {
        "app": APP_ID, "vault": name, "today": today,
        "generated": datetime.datetime.now().isoformat(timespec="seconds"),
        "notes_scanned": len(notes), "vocab": VOCAB,
        "tasks": tasks, "engagements": engagements, "projects": projects, "orgs": orgs,
        "funds": [{"fund": f, "currency": cur, "cash": v[0], "receivables": v[1],
                   "pledges": v[2]} for (f, cur), v in sorted(funds.items())],
        "meetings": meetings[:10], "people": people,
    }


# ---------------------------------------------------------------- HTTP server

class Handler(BaseHTTPRequestHandler):
    # class attrs set in main(): VAULT, NAME, PORT
    server_version = APP_ID
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        pass  # keep the terminal quiet

    def _send(self, code, body, ctype):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def _json(self, code, obj):
        self._send(code, json.dumps(obj), "application/json")

    def _host_ok(self):
        # DNS-rebinding guard: a hostile page can point its own hostname at
        # 127.0.0.1 and read the vault snapshot unless we pin the Host header.
        host = (self.headers.get("Host") or "").strip().lower()
        return host in {f"127.0.0.1:{self.PORT}", f"localhost:{self.PORT}",
                        "127.0.0.1", "localhost"}

    def do_GET(self):
        if not self._host_ok():
            return self._json(403, {"error": "forbidden-host",
                                    "message": self.headers.get("Host") or ""})
        path = urllib.parse.urlparse(self.path).path
        if path == "/":
            page = APP_HTML.replace("__BOOT__", json.dumps({"vault": self.NAME}))
            self._send(200, page, "text/html")
        elif path == "/api/health":
            self._json(200, {"app": APP_ID, "vault": self.NAME, "pid": os.getpid(),
                             "version": VERSION})
        elif path == "/api/data":
            try:
                self._json(200, build_data(self.VAULT, self.NAME))
            except Exception as e:
                self._json(500, {"error": "scan-failed", "message": str(e)})
        else:
            self._json(404, {"error": "not-found", "message": path})

    def do_POST(self):
        # Drain the request body FIRST, whatever happens next — leaving it unread
        # desyncs HTTP/1.1 keep-alive (leftover bytes get parsed as the next request).
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length > 1_000_000:
            self.close_connection = True
            return self._json(413, {"error": "too-large", "message": "body over 1 MB"})
        raw = self.rfile.read(length) if length > 0 else b""

        if not self._host_ok():
            return self._json(403, {"error": "forbidden-host",
                                    "message": self.headers.get("Host") or ""})
        path = urllib.parse.urlparse(self.path).path
        if path not in ("/api/status", "/api/due", "/api/field", "/api/assign"):
            return self._json(404, {"error": "not-found", "message": path})
        # CSRF guards: JSON-only, and no foreign Origin (we send no CORS headers).
        origin = self.headers.get("Origin")
        allowed = {f"http://127.0.0.1:{self.PORT}", f"http://localhost:{self.PORT}"}
        if origin and origin not in allowed:
            return self._json(403, {"error": "forbidden-origin", "message": origin})
        if not (self.headers.get("Content-Type") or "").startswith("application/json"):
            return self._json(415, {"error": "json-only",
                                    "message": "Content-Type must be application/json"})
        try:
            body = json.loads(raw)
        except (ValueError, TypeError):
            return self._json(400, {"error": "bad-json", "message": "unparseable body"})
        if not isinstance(body, dict):
            return self._json(400, {"error": "bad-json", "message": "body must be a JSON object"})

        rel = str(body.get("path") or "")
        expected = body.get("expected_mtime_ns")
        do_log = bool(body.get("log", True))
        try:
            if expected is not None:
                try:
                    expected = int(expected)
                except (TypeError, ValueError):
                    raise ChangeError(400, "expected_mtime_ns must be an integer")
            if path == "/api/status":
                new_status = str(body.get("new_status") or "")
                apply_fn = lambda text: apply_status_change(text, new_status, log=do_log)
            elif path == "/api/due":
                new_due = str(body.get("new_due") or "")
                apply_fn = lambda text: apply_due_change(text, new_due, log=do_log)
            elif path == "/api/field":
                key = str(body.get("key") or "")
                value = str(body.get("value") or "")
                # only link-valued fields need the (relatively costly) stem scan
                known = note_stems(self.VAULT) \
                    if SCALAR_KEYS.get(key, {}).get("link") else None
                apply_fn = lambda text: apply_scalar_change(text, key, value,
                                                            log=do_log, known=known)
            else:  # /api/assign
                key = str(body.get("key") or "")
                values = body.get("values")
                if not isinstance(values, list):
                    raise ChangeError(400, "'values' must be a list of note titles")
                values = [str(v) for v in values]
                known = note_stems(self.VAULT)
                apply_fn = lambda text: apply_list_change(text, key, values, log=do_log,
                                                          known=known)
            note = self._resolve(rel)
            with WRITE_LOCK:
                st = note.stat()
                if expected is not None and expected != st.st_mtime_ns:
                    raise ChangeError(409, "note changed on disk since the dashboard loaded it")
                try:
                    # read_bytes + decode: no universal-newline translation, so a
                    # CRLF note round-trips byte-exactly instead of being LF-ified
                    text = note.read_bytes().decode("utf-8")
                except UnicodeDecodeError:
                    raise ChangeError(422, "note is not valid UTF-8; refusing to rewrite it")
                new_text, meta = apply_fn(text)
                changed = new_text != text
                if changed:
                    atomic_write(note, new_text)
                meta["new_mtime_ns"] = str(note.stat().st_mtime_ns)
            meta.update(ok=True, path=rel)
            self._json(200, meta)
        except ChangeError as e:
            label = {409: "conflict", 403: "forbidden", 400: "bad-request"}.get(e.code, "unprocessable")
            self._json(e.code, {"error": label, "message": e.message})
        except FileNotFoundError:
            self._json(404, {"error": "not-found", "message": rel})
        except Exception as e:  # always answer — a dead connection reads as "offline"
            self._json(500, {"error": "internal", "message": f"{type(e).__name__}: {e}"})

    def _resolve(self, rel):
        if not rel or not rel.lower().endswith(".md"):
            raise ChangeError(403, "path must be a .md note inside the vault")
        parts = pathlib.PurePosixPath(rel).parts
        if pathlib.PurePosixPath(rel).is_absolute() or ".." in parts:
            raise ChangeError(403, "path escapes the vault")
        # lower(): APFS is case-insensitive, 'templates/x.md' is the same folder
        if parts and parts[0].lower() in (".obsidian", "templates"):
            raise ChangeError(403, "refusing to edit config/template files")
        p = (self.VAULT / rel).resolve()
        if not str(p).startswith(str(self.VAULT) + os.sep):
            raise ChangeError(403, "path escapes the vault")
        if not p.is_file():
            raise FileNotFoundError(rel)
        return p


# ---------------------------------------------------------------- embedded app

APP_HTML = r"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>🧠 Second Brain — Dashboard</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🧠</text></svg>">
<script>/* resolve the theme before first paint to avoid a flash */
try{var t=localStorage.getItem("sbdash.theme")||"auto",
    d=t==="dark"||(t==="auto"&&matchMedia("(prefers-color-scheme: dark)").matches);
document.documentElement.dataset.theme=d?"dark":"light"}catch(e){}</script>
<style>
/* Material Design 3 (baseline scheme, seed #6750A4) — light + dark via tokens. */
:root{
  color-scheme:light;
  --primary:#6750A4;--on-primary:#FFFFFF;--primary-container:#EADDFF;--on-primary-container:#21005D;
  --secondary-container:#E8DEF8;--on-secondary-container:#1D192B;
  --error:#B3261E;--on-error:#FFFFFF;--error-container:#F9DEDC;--on-error-container:#410E0B;
  --surface:#FEF7FF;--sc-lowest:#FFFFFF;--sc-low:#F7F2FA;--sc:#F3EDF7;--sc-high:#ECE6F0;--sc-highest:#E6E0E9;
  --on-surface:#1D1B20;--on-surface-var:#49454F;--outline:#79747E;--outline-var:#CAC4D0;
  --inverse-surface:#322F35;--inverse-on-surface:#F5EFF7;
  --hover:rgba(29,27,32,.05);--hover-strong:rgba(29,27,32,.09);
  --stat-todo-bg:#E6E0E9;--stat-todo-fg:#49454F;
  --stat-doing-bg:#D3E3FD;--stat-doing-fg:#041E49;
  --stat-review-bg:#DCC7F5;--stat-review-fg:#2B0E52;
  --stat-done-bg:#C4EED0;--stat-done-fg:#072711;
  --stat-hold-bg:#FCE8B3;--stat-hold-fg:#564500;
  --elev1:0 1px 2px rgba(0,0,0,.3),0 1px 3px 1px rgba(0,0,0,.15);
  --elev2:0 1px 2px rgba(0,0,0,.3),0 2px 6px 2px rgba(0,0,0,.15);
  --elev3:0 1px 3px rgba(0,0,0,.3),0 4px 8px 3px rgba(0,0,0,.15);
}
/* Dark scheme: warm charcoal + ivory + terracotta (Anthropic-style), applied
   via data-theme — JS resolves auto/light/dark and stamps the root element. */
:root[data-theme=dark]{
  color-scheme:dark;
  --primary:#D97757;--on-primary:#2A1810;--primary-container:#553226;--on-primary-container:#F8DED2;
  --secondary-container:#3E3D3A;--on-secondary-container:#F0EEE6;
  --error:#F2A296;--on-error:#45120C;--error-container:#69251C;--on-error-container:#FADFD9;
  --surface:#1F1E1D;--sc-lowest:#262624;--sc-low:#2B2A28;--sc:#30302E;--sc-high:#3A3937;--sc-highest:#45443F;
  --on-surface:#F0EEE6;--on-surface-var:#B3AFA4;--outline:#8A8678;--outline-var:#3E3D3A;
  --inverse-surface:#F0EEE6;--inverse-on-surface:#30302E;
  --hover:rgba(240,238,230,.05);--hover-strong:rgba(240,238,230,.1);
  --stat-todo-bg:#3E3D3A;--stat-todo-fg:#DAD7CE;
  --stat-doing-bg:#2C4763;--stat-doing-fg:#D2E3F8;
  --stat-review-bg:#4A3568;--stat-review-fg:#DCC7F5;
  --stat-done-bg:#2C4A33;--stat-done-fg:#C2E5C8;
  --stat-hold-bg:#54430F;--stat-hold-fg:#F2DFA0;
}
*{box-sizing:border-box}
body{font-family:Roboto,'Google Sans',-apple-system,'SF Pro Text','Segoe UI',system-ui,sans-serif;
  max-width:1240px;margin:1.25rem auto 4rem;padding:0 1.25rem;
  color:var(--on-surface);background:var(--surface);font-size:14px;line-height:1.45}
h1{font-size:24px;font-weight:400;letter-spacing:0;margin:.4rem 0 .8rem;display:flex;align-items:center;gap:10px}
h2{margin:1.5rem 0 .4rem;font-size:16px;font-weight:500;color:var(--on-surface);display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.badge{font-size:11px;font-weight:500;background:var(--primary-container);color:var(--on-primary-container);border-radius:999px;padding:4px 12px;letter-spacing:.08em}
.meta{color:var(--on-surface-var);font-size:12.5px}
.toolbar{display:flex;align-items:center;gap:.65rem;flex-wrap:wrap;margin:.4rem 0 .7rem}
button,select,input[type=search]{font:inherit}
button:focus-visible,select:focus-visible,input:focus-visible,a:focus-visible{outline:2px solid var(--primary);outline-offset:2px;border-radius:8px}
.btn{background:var(--primary);color:var(--on-primary);border:0;border-radius:999px;padding:9px 22px;cursor:pointer;font-size:14px;font-weight:500;letter-spacing:.01em}
.btn:hover{box-shadow:var(--elev1);background-image:linear-gradient(rgba(255,255,255,.08),rgba(255,255,255,.08))}
.btn:active{transform:translateY(1px);box-shadow:none}
.btn.spin{opacity:.6;pointer-events:none}
.btn.ghost{background:transparent;color:var(--primary);border:1px solid var(--outline);box-shadow:none}
.btn.ghost:hover{background:var(--hover);background-image:none}
select{border:1px solid var(--outline-var);border-radius:8px;padding:6px 8px;background:var(--sc-lowest);color:var(--on-surface);font-size:13px}
.banner{background:var(--error-container);color:var(--on-error-container);border:0;border-radius:12px;padding:12px 16px;margin:.6rem 0;font-size:14px;display:flex;gap:.8rem;align-items:center;box-shadow:var(--elev1)}
.banner .btn{background:var(--error);color:var(--on-error);padding:6px 16px;font-size:13px}
input[type=search]{border:0;border-radius:999px;padding:9px 18px;font-size:14px;min-width:210px;background:var(--sc-high);color:var(--on-surface)}
input[type=search]::placeholder{color:var(--on-surface-var)}
.link{background:none;border:0;color:var(--primary);cursor:pointer;font-size:13px;font-weight:500;text-decoration:none;padding:6px 10px;border-radius:999px}
.link:hover{background:var(--hover)}
.stickybar{position:sticky;top:0;z-index:20;background:var(--surface)}
.tabs{display:flex;gap:2px;flex-wrap:wrap;align-items:center;border-bottom:1px solid var(--outline-var);margin:.7rem 0 0;padding-top:2px}
.tabctl{margin-left:auto;display:flex;gap:2px;align-items:center}
.iconbtn{background:none;border:0;border-radius:999px;padding:5px 10px;cursor:pointer;color:var(--on-surface-var);font-size:15px;line-height:1.2}
.iconbtn:hover{background:var(--hover-strong);color:var(--on-surface)}
.viewbar{display:flex;gap:6px;flex-wrap:wrap;align-items:center;padding:8px 2px 9px;border-bottom:1px solid var(--outline-var);background:var(--surface)}
.vchip{background:transparent;border:1px solid var(--outline-var);border-radius:8px;padding:5px 14px;font-size:13px;font-weight:500;cursor:pointer;color:var(--on-surface-var)}
.vchip:hover{background:var(--hover)}
.vchip.on{background:var(--secondary-container);color:var(--on-secondary-container);border-color:transparent}
.tab{background:none;border:0;border-bottom:3px solid transparent;padding:11px 16px 10px;font-size:14px;font-weight:500;cursor:pointer;color:var(--on-surface-var);border-radius:10px 10px 0 0;display:flex;gap:7px;align-items:center}
.tab:hover{background:var(--hover);color:var(--on-surface)}
.tab.on{color:var(--primary);border-bottom-color:var(--primary)}
.tab .n{color:var(--on-surface-var);font-size:12px;font-weight:400}
.tab .od{background:var(--error);color:var(--on-error);border-radius:999px;font-size:10.5px;padding:2px 7px;font-weight:600}
.tablewrap{overflow-x:auto;background:var(--sc-lowest);border:1px solid var(--outline-var);border-radius:12px;margin:.45rem 0 1.3rem}
table{border-collapse:collapse;width:100%}
th,td{border:0;border-bottom:1px solid var(--outline-var);padding:10px 14px;text-align:left;font-size:14px;background:transparent}
tr:last-child td{border-bottom:0}
tbody tr:hover td,tr:hover td{background:var(--hover)}
th{background:var(--sc-low);white-space:nowrap;font-size:12.5px;font-weight:500;color:var(--on-surface-var);letter-spacing:.03em}
tr:hover th{background:var(--sc-low)}
.fbtn{background:none;border:0;cursor:pointer;color:var(--on-surface-var);font-size:10px;padding:2px 6px;border-radius:999px;vertical-align:middle}
.fbtn:hover{background:var(--hover-strong);color:var(--primary)}
.fbtn.on{color:var(--on-primary);background:var(--primary)}
a{color:var(--primary);text-decoration:none;font-weight:500}a:hover{text-decoration:underline}
.pill{border:0;border-radius:8px;padding:5px 12px;font-size:12.5px;font-weight:500;cursor:pointer;white-space:nowrap;color:var(--stat-todo-fg);background:var(--stat-todo-bg)}
.pill:hover{box-shadow:var(--elev1);filter:brightness(1.03)}
.pill:after{content:" ▾";font-size:9px;opacity:.6}
.offline .pill{opacity:.5;pointer-events:none}
.cellbtn{background:none;border:0;border-radius:8px;padding:4px 9px;font:inherit;font-size:13.5px;cursor:pointer;color:var(--on-surface);text-align:left}
.cellbtn:hover{background:var(--hover-strong)}
.cellbtn:after{content:" ▾";font-size:9px;opacity:.6}
.cellbtn.due-over{color:var(--error);font-weight:600}
.cellbtn.empty{color:var(--on-surface-var);opacity:.7}
.cellbtn.p-high{color:var(--error);font-weight:600}
.cellbtn.p-low{color:var(--on-surface-var)}
.menu button.dim{opacity:.45;cursor:not-allowed}
.offline .cellbtn{opacity:.5;pointer-events:none}
.pstat{border-radius:8px;padding:3px 10px;font-size:11.5px;font-weight:500;margin-left:4px;vertical-align:middle}
.menu-date{padding:8px 10px 10px;border-bottom:1px solid var(--outline-var);margin-bottom:4px;display:flex;gap:8px;align-items:center}
.menu-date input{border:1px solid var(--outline-var);border-radius:8px;padding:6px 8px;font:inherit;font-size:13px;flex:1;min-width:0;background:var(--sc-lowest);color:var(--on-surface)}
.menu .setbtn{width:auto;background:var(--primary);color:var(--on-primary);border-radius:999px;padding:7px 16px;font-size:13px;font-weight:500}
.menu .setbtn:hover{box-shadow:var(--elev1);background:var(--primary)}
.menu button.danger{color:var(--error)}
.pending{opacity:.45}
.s-in-progress,.s-talking{background:var(--stat-doing-bg);color:var(--stat-doing-fg)}
.s-in-review{background:var(--stat-review-bg);color:var(--stat-review-fg)}
.s-done,.s-active{background:var(--stat-done-bg);color:var(--stat-done-fg)}
.s-on-hold{background:var(--stat-hold-bg);color:var(--stat-hold-fg)}
.s-cancelled,.s-lost{background:var(--error-container);color:var(--on-error-container)}
.s-proposal,.s-planning{background:var(--primary-container);color:var(--on-primary-container)}
.s-not-started,.s-lead,.s-idea,.s-archived{background:var(--stat-todo-bg);color:var(--stat-todo-fg)}
.due-over{color:var(--error);font-weight:600}
.menu{position:absolute;z-index:30;background:var(--sc);border:0;border-radius:8px;box-shadow:var(--elev2);padding:6px;min-width:180px;max-width:340px;max-height:400px;overflow-y:auto}
.menu button{display:block;width:100%;text-align:left;background:none;border:0;border-radius:8px;padding:9px 12px;font-size:13.5px;cursor:pointer;color:var(--on-surface)}
.menu button:hover{background:var(--hover-strong)}
.menu button.current{font-weight:700;color:var(--primary)}
.mbar{display:flex;gap:5px;padding:4px 6px 8px;border-bottom:1px solid var(--outline-var);margin-bottom:4px;flex-wrap:wrap}
.mbar button{width:auto;padding:5px 12px;font-size:12.5px;font-weight:500;border:1px solid var(--outline-var);border-radius:8px;color:var(--on-surface)}
.mbar button.on{background:var(--secondary-container);color:var(--on-secondary-container);border-color:transparent}
.mrow{display:flex;align-items:center;gap:10px;padding:7px 12px;font-size:13.5px;cursor:pointer;border-radius:8px;color:var(--on-surface)}
.mrow:hover{background:var(--hover-strong)}
.mrow.dim{opacity:.45;cursor:not-allowed}
.mrow input{margin:0;accent-color:var(--primary)}
input[type=checkbox]{accent-color:var(--primary)}
.mrow .cnt{color:var(--on-surface-var);font-size:11.5px;margin-left:auto}
.msec{font-size:11px;letter-spacing:.09em;color:var(--on-surface-var);text-transform:uppercase;font-weight:500;padding:9px 12px 3px}
.msearch{padding:5px 6px 8px;border-bottom:1px solid var(--outline-var);margin-bottom:4px}
.msearch input{width:100%;border:0;border-radius:999px;padding:7px 12px;font-size:13px;background:var(--sc-highest);color:var(--on-surface)}
.mfoot{display:flex;gap:8px;padding:8px 6px 4px;border-top:1px solid var(--outline-var);margin-top:4px;position:sticky;bottom:-6px;background:var(--sc)}
.mfoot button{width:auto;flex:1;text-align:center;border:1px solid var(--outline);border-radius:999px;padding:7px;font-weight:500;color:var(--primary)}
.mfoot .apply{background:var(--primary);color:var(--on-primary);border-color:transparent;font-weight:600}
.toast{position:fixed;left:50%;bottom:26px;transform:translateX(-50%);background:var(--inverse-surface);color:var(--inverse-on-surface);border-radius:8px;padding:12px 20px;font-size:13.5px;z-index:40;box-shadow:var(--elev3);max-width:85vw}
.hidden{display:none}
.count{color:var(--on-surface-var);font-weight:400;font-size:12px}
</style></head><body>
<h1>🧠 <span id="vname"></span> — Dashboard <span class="badge">LIVE</span></h1>
<div class="toolbar">
  <button id="refresh" class="btn">↻ Refresh</button>
  <label class="meta">auto
    <select id="auto"><option value="0">off</option><option value="30">30s</option><option value="60">60s</option></select>
  </label>
  <button id="colsbtn" class="btn ghost">⚙ Columns</button>
  <input type="search" id="f-q" placeholder="Search tasks, projects, people…">
  <button id="f-clear" class="link">clear filters</button>
  <span id="meta" class="meta">loading…</span>
</div>
<div id="offline" class="banner hidden">
  <span>⚠️ Dashboard server unreachable — showing the last loaded data.</span>
  <button id="retry" class="btn">Retry</button>
</div>
<div class="stickybar">
<nav id="tabs" class="tabs"></nav>
<div id="viewbar" class="viewbar hidden"></div>
</div>
<main id="main"><p class="meta">Connecting to the vault…</p></main>
<div id="menu" class="menu hidden"></div>
<div id="toast" class="toast hidden"></div>
<script>
"use strict";
const BOOT = __BOOT__;
document.getElementById("vname").textContent = BOOT.vault;
let data = null, offline = false, menuKind = null, autoTimer = null, toastTimer = null;
let pendingWrites = 0, refreshQueued = false, lastWriteAt = 0;
const $ = (id) => document.getElementById(id);
const SKEY = "sbdash2.state", AKEY = "sbdash.auto";
const NONE = "__none__";
const ISO = /^\d{4}-\d{2}-\d{2}$/;
const TIME = /^([01]\d|2[0-3]):[0-5]\d$/;
const UNWRITABLE = /["\\\[\]]/;  // characters the server refuses in a link target

/* Column registry — `get` returns the value(s) used for filtering/sorting
   ("" stands for empty and renders as the (none) bucket). */
const COLS = [
  {id:"title",     label:"Task",        type:"text", get:t=>[t.title]},
  {id:"status",    label:"Status",      type:"vals", get:t=>[t.status||""]},
  {id:"priority",  label:"Priority",    type:"vals", get:t=>[t.priority||""]},
  {id:"due",       label:"Due date",    type:"due",  get:t=>[t.due||""]},
  {id:"due_time",  label:"Due Time",    type:"vals", get:t=>[t.due_time||""]},
  {id:"days_left", label:"Days left",   type:"due",  get:t=>[t.due||""], hide:true},
  {id:"company",   label:"Company",     type:"vals", get:t=>t.company.length?t.company:[""]},
  {id:"projects",  label:"Projects",    type:"vals", get:t=>t.projects.length?t.projects:[""], edit:"projects"},
  {id:"assignee",  label:"Assignee",    type:"vals", get:t=>t.assignee.length?t.assignee:[""], edit:"assignee"},
  {id:"people",    label:"People",      type:"vals", get:t=>t.people.length?t.people:[""]},
  {id:"recurrence",label:"Repeats",     type:"vals", get:t=>[t.recurrence||""], hide:true},
  {id:"parent",    label:"Parent task", type:"vals", get:t=>t.parent.length?t.parent:[""], hide:true},
  {id:"blocked_by",label:"Blocked by",  type:"vals", get:t=>t.blocked_by.length?t.blocked_by:[""], hide:true},
  {id:"related",   label:"Related",     type:"vals", get:t=>t.related.length?t.related:[""], hide:true},
  {id:"source",    label:"Source",      type:"vals", get:t=>t.source.length?t.source:[""], hide:true},
  {id:"created",   label:"Created",     type:"vals", get:t=>[t.created||""], hide:true},
  {id:"domain",    label:"Domain",      type:"vals", get:t=>[t.domain||""], hide:true},
];
const DEFAULT_VISIBLE = COLS.filter(c=>!c.hide).map(c=>c.id);
const DUE_BUCKETS = [["past","Past due"],["today","Due today"],["week","Next 7 days"],["later","Later"],["none","No date"]];

let state = {tab:"all", cols:null, colf:{}, sort:null, q:"", view:{}, viewbar:true, v:0, _init:false};

/* Saved state outlives the version that wrote it. Whenever a release adds a
   status or turns a column on by default, a *pre-existing* saved filter has
   no opinion about it — and the default (a filter lists what to SHOW) is to
   hide it, so the new thing silently goes missing. Each migration below
   grants that consent once; anything the user later deselects stays gone. */
const STATE_VERSION = 2;
function migrateState(){
  const from = state.v || 0;
  if (from < 1 && Array.isArray(state.cols) && !state.cols.includes("due_time"))
    state.cols.push("due_time");            // 2.7: Due Time became default-visible
  if (from < 2 && Array.isArray(state.colf.status) && !state.colf.status.includes("in-review"))
    state.colf.status.push("in-review");    // 2.8: `in-review` joined the task vocabulary
  if (from < STATE_VERSION){ state.v = STATE_VERSION; saveState(); }
}

function loadState(){
  try{ const s = JSON.parse(localStorage.getItem(SKEY)||"null"); if (s) state = {...state, ...s}; }catch(e){}
  if (!Array.isArray(state.cols)) state.cols = null;
  if (!state.colf || typeof state.colf !== "object") state.colf = {};
  if (!state.view || typeof state.view !== "object") state.view = {};
  if (state.tab === "project"){ state.tab = "all"; state.view.all = "project"; }  // pre-2.6 saved tab
  migrateState();
  $("f-q").value = state.q || "";
}

/* ---------------- theme: auto → light → dark, persisted separately -------- */
let themePref = "auto";
try { themePref = localStorage.getItem("sbdash.theme") || "auto"; } catch(e){}
function applyTheme(){
  const dark = themePref === "dark" ||
    (themePref === "auto" && window.matchMedia("(prefers-color-scheme: dark)").matches);
  document.documentElement.dataset.theme = dark ? "dark" : "light";
}
function cycleTheme(){
  themePref = themePref === "auto" ? "light" : themePref === "light" ? "dark" : "auto";
  try { localStorage.setItem("sbdash.theme", themePref); } catch(e){}
  applyTheme(); if (data) renderTabs();
  toast("Theme: " + themePref);
}
try { window.matchMedia("(prefers-color-scheme: dark)")
        .addEventListener("change", () => { if (themePref === "auto") applyTheme(); }); } catch(e){}
applyTheme();
function saveState(){ localStorage.setItem(SKEY, JSON.stringify(state)); }
function visibleCols(){
  const ids = state.cols || DEFAULT_VISIBLE;
  return COLS.filter(c => c.id === "title" || ids.includes(c.id));
}

function el(tag, attrs, ...kids){
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})){
    if (k === "class") n.className = v;
    else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
    else n.setAttribute(k, v);
  }
  for (const kid of kids.flat(9)) if (kid !== null && kid !== undefined)
    n.append(kid.nodeType ? kid : document.createTextNode(kid));
  return n;
}
const noteLink = (it) => el("a", {href: it.url, title: "open in Obsidian"}, it.title);
const dash = (v) => v || "—";

function toast(msg){
  const t = $("toast"); t.textContent = msg; t.classList.remove("hidden");
  clearTimeout(toastTimer); toastTimer = setTimeout(() => t.classList.add("hidden"), 3200);
}
function setOffline(on){
  offline = on;
  $("offline").classList.toggle("hidden", !on);
  document.body.classList.toggle("offline", on);
}

/* ------------------------------------------------ filtering + sorting */
function addDaysISO(iso, days){
  const d = new Date(iso + "T12:00:00"); d.setDate(d.getDate() + days);
  return d.getFullYear() + "-" + String(d.getMonth()+1).padStart(2,"0") + "-" + String(d.getDate()).padStart(2,"0");
}
function dueBucket(t){
  if (!ISO.test(t.due)) return "none";
  if (t.due < data.today) return "past";
  if (t.due === data.today) return "today";
  return t.due <= addDaysISO(data.today, 7) ? "week" : "later";
}
function daysLeft(t){
  if (!ISO.test(t.due)) return "";
  return Math.round((new Date(t.due+"T12:00:00") - new Date(data.today+"T12:00:00")) / 864e5);
}
function passCol(t, c){
  const f = state.colf[c.id];
  if (f === undefined) return true;
  if (c.type === "text"){
    const q = String(f).toLowerCase();
    return !q || t.title.toLowerCase().includes(q);
  }
  const sel = Array.isArray(f) ? f : [];
  if (c.type === "due") return sel.includes(dueBucket(t));
  return c.get(t).map(v => v === "" ? NONE : v).some(v => sel.includes(v));
}
function passQ(t){
  if (!state.q) return true;
  const hay = [t.title, ...t.projects, ...t.people, ...t.assignee, ...t.company].join(" ").toLowerCase();
  return hay.includes(state.q.toLowerCase());
}
function sortKey(c, t){
  switch (c.id){
    case "status":   return data.vocab.task.indexOf(t.status);
    case "priority": return {high:0, normal:1, medium:1, low:2}[t.priority] ?? 3;
    case "due": case "days_left": return t.due && ISO.test(t.due) ? t.due : "9999-99-99";
    case "due_time": return t.due_time || "99:99";  // blanks sort last, not first
    case "created":  return t.created || "9999-99-99";
    default:         return c.get(t).filter(v=>v!=="").join(", ").toLowerCase();
  }
}
function applyFilters(tasks){
  let out = tasks.filter(t => passQ(t) && COLS.every(c => passCol(t, c)));
  if (state.sort){
    const c = COLS.find(x => x.id === state.sort.col);
    if (c){
      const dir = state.sort.dir;
      out = out.slice().sort((a, b) => {
        const ka = sortKey(c, a), kb = sortKey(c, b);
        return (ka < kb ? -1 : ka > kb ? 1 : 0) * dir;
      });
    }
  }
  return out;
}
function anyFilterActive(){
  return state.q || state.sort || Object.keys(state.colf).length > 0;
}

/* ------------------------------------------------ tabs */
function tabDefs(){
  const companies = [...new Set(data.tasks.flatMap(t => t.company))].sort((a,b)=>a.localeCompare(b));
  return [{id:"all", label:"All Tasks"},
          ...companies.map(c => ({id:"co:"+c, label:c})),
          {id:"personal", label:"Personal"}, {id:"overview", label:"Overview"}];
}
function tabBase(tabId){
  if (tabId === "all") return data.tasks;
  if (tabId === "personal") return data.tasks.filter(t => !t.company.length);
  if (tabId.startsWith("co:")){ const c = tabId.slice(3); return data.tasks.filter(t => t.company.includes(c)); }
  return [];
}
/* in-tab views — remembered per tab; "By Company" only makes sense on All */
const VIEWS = [
  {id:"table",    label:"Table"},
  {id:"project",  label:"By Project"},
  {id:"status",   label:"By Status"},
  {id:"assignee", label:"By Assignee"},
  {id:"company",  label:"By Company", allOnly:true},
  {id:"due",      label:"By Due date"},
];
function currentView(){
  const v = state.view[state.tab] || "table";
  const def = VIEWS.find(x => x.id === v);
  return (!def || (def.allOnly && state.tab !== "all")) ? "table" : v;
}
function renderTabs(){
  const nav = $("tabs"); nav.innerHTML = "";
  const defs = tabDefs();
  if (!defs.some(d => d.id === state.tab)) state.tab = "all";
  for (const d of defs){
    const kids = [d.label];
    if (d.id !== "overview"){
      const base = tabBase(d.id);
      const open = base.filter(t => t.status !== "done" && t.status !== "cancelled").length;
      const od = base.filter(t => t.overdue).length;
      kids.push(el("span", {class:"n"}, String(open)));
      if (od) kids.push(el("span", {class:"od", title: od + " overdue"}, String(od)));
    }
    nav.append(el("button", {class: "tab" + (state.tab === d.id ? " on" : ""),
      onclick: () => { state.tab = d.id; saveState(); render(); }}, kids));
  }
  nav.append(el("div", {class:"tabctl"},
    el("button", {class:"iconbtn", title:"Theme: " + themePref + " — click to cycle auto → light → dark",
      onclick: cycleTheme}, themePref === "auto" ? "◐" : themePref === "light" ? "☀" : "☾"),
    state.tab === "overview" ? null :
      el("button", {class:"iconbtn", title:(state.viewbar !== false ? "Hide" : "Show") + " the views bar",
        onclick: () => { state.viewbar = state.viewbar === false; saveState(); render(); }},
        state.viewbar !== false ? "⌃" : "⌄")));
}
function renderViewbar(){
  const bar = $("viewbar"); bar.innerHTML = "";
  const show = state.viewbar !== false && state.tab !== "overview";
  bar.classList.toggle("hidden", !show);
  if (!show) return;
  const cur = currentView();
  for (const v of VIEWS){
    if (v.allOnly && state.tab !== "all") continue;
    bar.append(el("button", {class:"vchip" + (cur === v.id ? " on" : ""),
      onclick: () => { state.view[state.tab] = v.id; saveState(); render(); }}, v.label));
  }
}

/* ------------------------------------------------ menus (shared container) */
function placeMenu(target){
  const m = $("menu");
  m.classList.remove("hidden");
  const r = target.getBoundingClientRect();
  const left = Math.min(r.left + window.scrollX,
                        window.scrollX + document.documentElement.clientWidth - m.offsetWidth - 12);
  m.style.left = Math.max(window.scrollX + 6, left) + "px";
  m.style.top = (r.bottom + window.scrollY + 4) + "px";
}
function closeMenu(){
  const wasItem = menuKind === "item";
  $("menu").classList.add("hidden"); menuKind = null;
  // a refresh deferred while an editor was open runs once the editor closes
  if (wasItem && refreshQueued && !pendingWrites){ refreshQueued = false; setTimeout(refresh, 0); }
}
document.addEventListener("click", (ev) => { if (!$("menu").contains(ev.target)) closeMenu(); });
document.addEventListener("keydown", (ev) => { if (ev.key === "Escape") closeMenu(); });

/* ------------------------------------------------ status + due editing */
function pill(item){
  return el("button", {class: "pill s-" + (item.status || "none") + (item.pending ? " pending" : ""),
    onclick: (e) => openStatusMenu(e, item)}, item.status || "—");
}
function openStatusMenu(e, item){
  e.stopPropagation();
  menuKind = "item";
  const m = $("menu"); m.innerHTML = "";
  for (const s of (data.vocab[item.vtype] || [])){
    m.append(el("button", {class: s === item.status ? "current" : "",
      onclick: () => { closeMenu(); if (s !== item.status) changeStatus(item, s); }}, s));
  }
  placeMenu(e.currentTarget);
}
function localISO(offsetDays){
  const d = new Date(); d.setDate(d.getDate() + (offsetDays || 0));
  return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") +
         "-" + String(d.getDate()).padStart(2, "0");
}
function dueCell(item){
  // the time rides along only when its own column is hidden — otherwise it
  // would read twice on the same row
  const solo = !visibleCols().some(c => c.id === "due_time");
  const label = (item.due || "—") + (solo && item.due_time ? " " + item.due_time : "");
  return el("td", {}, el("button", {class: "cellbtn" + (item.overdue ? " due-over" : "") + (item.due ? "" : " empty"),
    title: "change due date", onclick: (e) => openDueEditor(e, item)}, label));
}
function openDueEditor(e, item){
  e.stopPropagation();
  menuKind = "item";
  const m = $("menu"); m.innerHTML = "";
  // No auto-commit on 'change': Chrome fires it on every intermediate valid
  // value while typing (first year digit → "0002-…"). Commit only on the
  // explicit Set button or Enter; Escape/outside-click abandons the edit.
  const input = el("input", {type: "date", min: "1970-01-01", max: "2100-12-31"});
  input.value = ISO.test(item.due) ? item.due : "";
  input.addEventListener("click", () => { try { input.showPicker(); } catch (err){} });
  const commit = () => {
    const v = input.value;
    if (!v || v === item.due) return;
    if (v.slice(0, 4) < "1970" || v.slice(0, 4) > "2100") { toast("That year looks wrong — not saved"); return; }
    closeMenu(); changeDue(item, v);
  };
  input.addEventListener("keydown", (ev) => { if (ev.key === "Enter"){ ev.preventDefault(); commit(); } });
  const setBtn = el("button", {class: "setbtn", onclick: commit}, "Set");
  m.append(el("div", {class: "menu-date"}, input, setBtn));
  for (const [lbl, days] of [["Today", 0], ["Tomorrow", 1], ["Next week", 7]]){
    const iso = localISO(days);
    m.append(el("button", {onclick: () => { closeMenu(); if (iso !== item.due) changeDue(item, iso); }},
      lbl + " · " + iso));
  }
  if (item.due) m.append(el("button", {class: "danger",
    onclick: () => { closeMenu(); changeDue(item, ""); }}, "Clear due date"));
  placeMenu(e.currentTarget);
}

/* ------------------------------------------------ due-time editing */
function dueTimeCell(item){
  const settable = item.due || item.due_time;
  return el("td", {}, el("button", {class: "cellbtn" + (item.due_time ? "" : " empty") + (item.pending ? " pending" : ""),
    title: settable ? "change due time" : "set a due date first",
    onclick: (e) => openTimeEditor(e, item)}, item.due_time || "—"));
}
function openTimeEditor(e, item){
  e.stopPropagation();
  menuKind = "item";
  const m = $("menu"); m.innerHTML = "";
  if (!item.due && !item.due_time){
    // mirrors the server rule: a time with no date is meaningless
    m.append(el("div", {class: "msec"}, "set a due date first"));
    placeMenu(e.currentTarget); return;
  }
  // same no-auto-commit rule as the date editor — 'change' fires on every
  // intermediate value while typing, so commit only on Set or Enter
  const input = el("input", {type: "time"});
  input.value = TIME.test(item.due_time) ? item.due_time : "";
  input.addEventListener("click", () => { try { input.showPicker(); } catch (err){} });
  const commit = () => {
    const v = input.value;
    if (!v || v === item.due_time) return;
    if (!TIME.test(v)) { toast("That time looks wrong — not saved"); return; }
    closeMenu(); changeScalar(item, "due_time", v);
  };
  input.addEventListener("keydown", (ev) => { if (ev.key === "Enter"){ ev.preventDefault(); commit(); } });
  m.append(el("div", {class: "menu-date"}, input, el("button", {class: "setbtn", onclick: commit}, "Set")));
  for (const t of ["09:00", "12:00", "14:00", "17:00"])
    m.append(el("button", {class: t === item.due_time ? "current" : "",
      onclick: () => { closeMenu(); if (t !== item.due_time) changeScalar(item, "due_time", t); }}, t));
  if (item.due_time) m.append(el("button", {class: "danger",
    onclick: () => { closeMenu(); changeScalar(item, "due_time", ""); }}, "Clear due time"));
  placeMenu(e.currentTarget);
}

/* ------------------------------------------------ priority + company editing */
function priorityCell(item){
  const v = item.priority || "";
  return el("td", {}, el("button", {class: "cellbtn" + (v ? " p-" + v : " empty") + (item.pending ? " pending" : ""),
    title: "change priority", onclick: (e) => openPriorityMenu(e, item)}, v || "—"));
}
function openPriorityMenu(e, item){
  e.stopPropagation();
  menuKind = "item";
  const m = $("menu"); m.innerHTML = "";
  for (const v of ["high", "normal", "low"])
    m.append(el("button", {class: v === item.priority ? "current" : "",
      onclick: () => { closeMenu(); if (v !== item.priority) changeScalar(item, "priority", v); }}, v));
  if (item.priority) m.append(el("button", {class: "danger",
    onclick: () => { closeMenu(); changeScalar(item, "priority", ""); }}, "Clear priority"));
  placeMenu(e.currentTarget);
}
function companyCell(item){
  const v = item.company[0] || "";
  return el("td", {}, el("button", {class: "cellbtn" + (v ? "" : " empty") + (item.pending ? " pending" : ""),
    title: "change company", onclick: (e) => openCompanyMenu(e, item)}, v || "—"));
}
function openCompanyMenu(e, item){
  e.stopPropagation();
  menuKind = "item";
  const cur = item.company[0] || "";
  // employers already on tasks lead — the long tail of org notes sits below
  const inUse = [...new Set(data.tasks.flatMap(t => t.company))].sort((a,b)=>a.localeCompare(b));
  const rest = data.orgs.map(o => o.title).filter(n => !inUse.includes(n)).sort((a,b)=>a.localeCompare(b));
  const sections = [{label: "In use", items: inUse},
                    {label: "Organizations", items: rest}];
  const m = $("menu"); m.innerHTML = "";
  const rows = [];
  const search = el("input", {type: "search", placeholder: "Filter…",
    oninput: () => { const q = search.value.toLowerCase();
      for (const r of rows) r.node.style.display = r.name.toLowerCase().includes(q) ? "" : "none"; }});
  if (inUse.length + rest.length > 8) m.append(el("div", {class: "msearch"}, search));
  for (const sec of sections){
    if (!sec.items.length) continue;
    m.append(el("div", {class: "msec"}, sec.label));
    for (const name of sec.items){
      const invalid = UNWRITABLE.test(name);
      const btn = el("button", {class: name === cur ? "current" : (invalid ? "dim" : ""),
        title: invalid ? 'title contains " [ ] or \\ — rename or edit in Obsidian' : "",
        onclick: () => { if (invalid) return;
          closeMenu(); if (name !== cur) changeScalar(item, "company", name); }}, name);
      rows.push({name, node: btn});
      m.append(btn);
    }
  }
  if (!rows.length) m.append(el("div", {class: "msec"}, "no organization notes yet"));
  if (cur) m.append(el("button", {class: "danger",
    onclick: () => { closeMenu(); changeScalar(item, "company", ""); }}, "Clear company (→ Personal)"));
  placeMenu(e.currentTarget);
}

function refreshOverdueFlag(t){
  if (t.vtype !== "task") return;
  t.overdue = ISO.test(t.due) && t.due < data.today
              && t.status !== "done" && t.status !== "cancelled";
}
async function changeStatus(item, newStatus){
  const prev = item.status;
  item.status = newStatus; item.pending = true;
  refreshOverdueFlag(item); render();
  pendingWrites++;
  try {
    const res = await fetch("/api/status", {method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({path: item.path, new_status: newStatus,
                            expected_mtime_ns: item.mtime_ns})});
    const out = await res.json().catch(() => ({}));
    lastWriteAt = Date.now();
    if (res.status === 409){
      item.status = prev; item.pending = false;
      toast("Note changed on disk — refreshing…");
      refreshQueued = true; return;
    }
    if (!res.ok){
      item.status = prev; item.pending = false; refreshOverdueFlag(item); render();
      toast("Update failed: " + (out.message || res.status)); return;
    }
    item.mtime_ns = out.new_mtime_ns; item.pending = false;
    if (out.recurred){
      item.status = out.status; item.due = out.due;
      toast("Recurring task — due advanced to " + out.due);
    } else {
      toast(item.title + " → " + newStatus);
    }
    refreshOverdueFlag(item); render();
  } catch (err){
    item.status = prev; item.pending = false; refreshOverdueFlag(item);
    setOffline(true); render();
  } finally {
    pendingWrites--;
    if (!pendingWrites && refreshQueued){ refreshQueued = false; refresh(); }
  }
}
async function changeDue(item, newDue){
  const prevDue = item.due, prevTime = item.due_time;
  item.due = newDue; if (!newDue) item.due_time = "";
  item.pending = true; refreshOverdueFlag(item); render();
  pendingWrites++;
  try {
    const res = await fetch("/api/due", {method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({path: item.path, new_due: newDue,
                            expected_mtime_ns: item.mtime_ns})});
    const out = await res.json().catch(() => ({}));
    lastWriteAt = Date.now();
    if (res.status === 409){
      item.due = prevDue; item.due_time = prevTime; item.pending = false;
      toast("Note changed on disk — refreshing…");
      refreshQueued = true; return;
    }
    if (!res.ok){
      item.due = prevDue; item.due_time = prevTime; item.pending = false;
      refreshOverdueFlag(item); render();
      toast("Update failed: " + (out.message || res.status)); return;
    }
    item.mtime_ns = out.new_mtime_ns; item.pending = false;
    if (out.due !== undefined) item.due = out.due;
    if (out.due_time !== undefined) item.due_time = out.due_time;
    toast(item.title + (item.due ? " → due " + item.due : " — due date cleared"));
    refreshOverdueFlag(item); render();
  } catch (err){
    item.due = prevDue; item.due_time = prevTime; item.pending = false;
    refreshOverdueFlag(item); setOffline(true); render();
  } finally {
    pendingWrites--;
    if (!pendingWrites && refreshQueued){ refreshQueued = false; refresh(); }
  }
}

const SCALAR_LABEL = {priority: "priority", company: "company", due_time: "due time"};
async function changeScalar(item, key, value){
  // `company` is a single link the snapshot carries as an array of one
  const arr = key === "company";
  const prev = arr ? item.company : item[key];
  if (arr) item.company = value ? [value] : [];
  else item[key] = value;
  const revert = () => { if (arr) item.company = prev; else item[key] = prev; };
  item.pending = true; render();
  pendingWrites++;
  try {
    const res = await fetch("/api/field", {method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({path: item.path, key: key, value: value,
                            expected_mtime_ns: item.mtime_ns})});
    const out = await res.json().catch(() => ({}));
    lastWriteAt = Date.now();
    if (res.status === 409){
      revert(); item.pending = false;
      toast("Note changed on disk — refreshing…");
      refreshQueued = true; return;
    }
    if (!res.ok){
      revert(); item.pending = false; render();
      toast("Update failed: " + (out.message || res.status)); return;
    }
    item.mtime_ns = out.new_mtime_ns; item.pending = false;
    toast(item.title + (value ? " → " + SCALAR_LABEL[key] + " " + value
                              : " — " + SCALAR_LABEL[key] + " cleared"));
    render();
  } catch (err){
    revert(); item.pending = false; setOffline(true); render();
  } finally {
    pendingWrites--;
    if (!pendingWrites && refreshQueued){ refreshQueued = false; refresh(); }
  }
}

/* ------------------------------------------------ projects / assignee editing */
function listEditBtn(item, key){
  const vals = item[key];
  return el("button", {class: "cellbtn" + (vals.length ? "" : " empty") + (item.pending ? " pending" : ""),
    title: "edit " + key, onclick: (e) => openListEditor(e, item, key)},
    vals.length ? vals.join(", ") : "—");
}
function openListEditor(e, item, key){
  e.stopPropagation();
  menuKind = "item";
  const m = $("menu"); m.innerHTML = "";
  let sections;
  if (key === "projects"){
    const names = new Set(data.projects.map(p => p.title));
    for (const t of data.tasks) for (const n of t.projects) names.add(n);
    sections = [{label: null, items: [...names].sort((a,b)=>a.localeCompare(b))}];
  } else {
    const known = new Set([...data.people.map(p => p.title), ...data.orgs.map(o => o.title)]);
    sections = [{label: "People", items: data.people.map(p => p.title)},
                {label: "Organizations", items: data.orgs.map(o => o.title)}];
    const extra = item[key].filter(v => !known.has(v));
    if (extra.length) sections.push({label: "Other", items: extra});
  }
  const sel = new Set(item[key]);
  const rows = [];
  const search = el("input", {type: "search", placeholder: "Filter…",
    oninput: () => { const q = search.value.toLowerCase();
      for (const r of rows) r.node.style.display = r.name.toLowerCase().includes(q) ? "" : "none"; }});
  m.append(el("div", {class: "msearch"}, search));
  for (const sec of sections){
    if (sec.label && sec.items.length) m.append(el("div", {class: "msec"}, sec.label));
    for (const name of sec.items){
      const cb = el("input", {type: "checkbox"});
      cb.checked = sel.has(name);
      const invalid = UNWRITABLE.test(name);
      if (invalid) cb.disabled = true;
      else cb.addEventListener("change", () => { cb.checked ? sel.add(name) : sel.delete(name); });
      const row = el("label", {class: "mrow" + (invalid ? " dim" : ""),
        title: invalid ? 'title contains " [ ] or \\ — rename or edit in Obsidian' : ""}, cb, name);
      rows.push({name, node: row});
      m.append(row);
    }
  }
  if (!rows.length) m.append(el("div", {class: "msec"}, "nothing to pick from"));
  m.append(el("div", {class: "mfoot"},
    el("button", {onclick: closeMenu}, "Cancel"),
    el("button", {class: "apply", onclick: () => { closeMenu(); changeList(item, key, [...sel]); }}, "Apply")));
  placeMenu(e.currentTarget);
}
async function changeList(item, key, values){
  const prev = item[key];
  if (JSON.stringify(prev) === JSON.stringify(values)) return;
  item[key] = values; item.pending = true; render();
  pendingWrites++;
  try {
    const res = await fetch("/api/assign", {method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({path: item.path, key: key, values: values,
                            expected_mtime_ns: item.mtime_ns})});
    const out = await res.json().catch(() => ({}));
    lastWriteAt = Date.now();
    if (res.status === 409){
      item[key] = prev; item.pending = false;
      toast("Note changed on disk — refreshing…");
      refreshQueued = true; return;
    }
    if (!res.ok){
      item[key] = prev; item.pending = false; render();
      toast("Update failed: " + (out.message || res.status)); return;
    }
    item.mtime_ns = out.new_mtime_ns; item.pending = false;
    if (Array.isArray(out.values)) item[key] = out.values;
    toast(item.title + " — " + (key === "assignee" ? "assignee" : "projects") + " updated");
    render();
  } catch (err){
    item[key] = prev; item.pending = false; setOffline(true); render();
  } finally {
    pendingWrites--;
    if (!pendingWrites && refreshQueued){ refreshQueued = false; refresh(); }
  }
}

/* ------------------------------------------------ column filter / sort menus */
function orderedVals(c, counts){
  let vals = [...counts.keys()];
  if (c.id === "status") vals.sort((a,b) => data.vocab.task.indexOf(a) - data.vocab.task.indexOf(b));
  else if (c.id === "priority"){
    const po = {high:0, normal:1, low:2};
    vals.sort((a,b) => (po[a] ?? 8) - (po[b] ?? 8));
  } else vals.sort((a,b) => a.localeCompare(b));
  if (vals.includes(NONE)) vals = vals.filter(v => v !== NONE).concat([NONE]);
  return vals;
}
function reopenColMenu(c){
  // after renderAll() the old header cell is gone — re-anchor on the fresh one
  const btn = document.querySelector('.fbtn[data-col="' + CSS.escape(c.id) + '"]');
  if (btn) openColMenu(btn, c); else closeMenu();
}
function openColMenu(anchor, c){
  menuKind = "filter";
  const m = $("menu"); m.innerHTML = "";
  const sortRow = el("div", {class: "mbar"});
  for (const [lbl, dir] of [["Sort ↑", 1], ["Sort ↓", -1]]){
    const on = state.sort && state.sort.col === c.id && state.sort.dir === dir;
    sortRow.append(el("button", {class: on ? "on" : "",
      onclick: () => { state.sort = on ? null : {col: c.id, dir}; saveState(); renderAll(); reopenColMenu(c); }}, lbl));
  }
  sortRow.append(el("button", {onclick: () => {
    delete state.colf[c.id];
    if (state.sort && state.sort.col === c.id) state.sort = null;
    saveState(); renderAll(); closeMenu(); }}, "Clear"));
  m.append(sortRow);

  if (c.type === "text"){
    const input = el("input", {type: "search", placeholder: "Title contains…", value: String(state.colf[c.id] || "")});
    let timer = null;
    input.addEventListener("input", () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        const v = input.value.trim();
        if (v) state.colf[c.id] = v; else delete state.colf[c.id];
        saveState(); renderAll();
      }, 150);
    });
    m.append(el("div", {class: "msearch"}, input));
  } else {
    let entries;  // [value, label, count]
    if (c.type === "due"){
      const counts = new Map();
      for (const t of data.tasks){ const b = dueBucket(t); counts.set(b, (counts.get(b) || 0) + 1); }
      entries = DUE_BUCKETS.filter(([v]) => counts.has(v)).map(([v, lbl]) => [v, lbl, counts.get(v)]);
    } else {
      const counts = new Map();
      for (const t of data.tasks) for (let v of c.get(t)){
        v = v === "" ? NONE : v;
        counts.set(v, (counts.get(v) || 0) + 1);
      }
      entries = orderedVals(c, counts).map(v => [v, v === NONE ? "(none)" : v, counts.get(v)]);
    }
    const allVals = entries.map(en => en[0]);
    // a saved filter may reference values that no longer exist — surface them
    // (count 0) so they can still be unchecked instead of silently hiding rows
    if (Array.isArray(state.colf[c.id]))
      for (const v of state.colf[c.id]) if (!allVals.includes(v))
        entries.push([v, (v === NONE ? "(none)" : v) + " · gone", 0]);
    const bar = el("div", {class: "mbar"},
      el("button", {onclick: () => { delete state.colf[c.id]; saveState(); renderAll(); syncBoxes(); }}, "All"),
      el("button", {onclick: () => { state.colf[c.id] = []; saveState(); renderAll(); syncBoxes(); }}, "None"));
    m.append(bar);
    const boxes = [];
    const isSel = (v) => state.colf[c.id] === undefined || state.colf[c.id].includes(v);
    function syncBoxes(){ for (const b of boxes) b.cb.checked = isSel(b.v); }
    for (const [v, lbl, cnt] of entries){
      const cb = el("input", {type: "checkbox"});
      cb.checked = isSel(v);
      cb.addEventListener("change", () => {
        let sel = Array.isArray(state.colf[c.id]) ? state.colf[c.id].slice() : allVals.slice();
        sel = cb.checked ? sel.concat(sel.includes(v) ? [] : [v]) : sel.filter(x => x !== v);
        if (allVals.every(x => sel.includes(x))) delete state.colf[c.id];
        else state.colf[c.id] = sel;
        saveState(); renderAll();
      });
      boxes.push({cb, v});
      m.append(el("label", {class: "mrow"}, cb, lbl, el("span", {class: "cnt"}, String(cnt))));
    }
  }
  placeMenu(anchor);
}
function openColsMenu(e){
  e.stopPropagation();
  menuKind = "cols";
  const m = $("menu"); m.innerHTML = "";
  m.append(el("div", {class: "msec"}, "Show columns"));
  for (const c of COLS){
    if (c.id === "title") continue;
    const cb = el("input", {type: "checkbox"});
    cb.checked = (state.cols || DEFAULT_VISIBLE).includes(c.id);
    cb.addEventListener("change", () => {
      let ids = (state.cols || DEFAULT_VISIBLE).slice();
      ids = cb.checked ? ids.concat(ids.includes(c.id) ? [] : [c.id]) : ids.filter(x => x !== c.id);
      if (!cb.checked){
        // hiding a column also retires its (now invisible) filter and sort
        delete state.colf[c.id];
        if (state.sort && state.sort.col === c.id) state.sort = null;
      }
      state.cols = ids; saveState(); renderAll();
    });
    m.append(el("label", {class: "mrow"}, cb, c.label));
  }
  m.append(el("div", {class: "mfoot"},
    el("button", {onclick: () => { state.cols = null; saveState(); renderAll(); closeMenu(); }}, "Reset"),
    el("button", {class: "apply", onclick: closeMenu}, "Done")));
  placeMenu(e.currentTarget);
}

/* ------------------------------------------------ rendering */
function section(title, count, node){
  return el("section", {}, el("h2", {}, title, count === null ? "" : " ",
    count === null ? null : el("span", {class: "count"}, count)), node);
}
function thFor(c){
  const active = state.colf[c.id] !== undefined || (state.sort && state.sort.col === c.id);
  return el("th", {}, c.label, " ",
    el("button", {class: "fbtn" + (active ? " on" : ""), title: "filter / sort " + c.label,
      "data-col": c.id,
      onclick: (e) => { e.stopPropagation(); openColMenu(e.currentTarget, c); }}, "▾"));
}
function cellFor(c, t){
  switch (c.id){
    case "title":    return el("td", {}, noteLink(t));
    case "status":   return el("td", {}, pill(t));
    case "priority": return priorityCell(t);
    case "company":  return companyCell(t);
    case "due":      return dueCell(t);
    case "due_time": return dueTimeCell(t);
    case "days_left": {
      const n = daysLeft(t);
      return el("td", {class: n !== "" && n < 0 && t.status !== "done" && t.status !== "cancelled" ? "due-over" : ""},
                n === "" ? "—" : String(n));
    }
    case "projects": case "assignee": return el("td", {}, listEditBtn(t, c.id));
    default: {
      const v = c.get(t).filter(x => x !== "");
      return el("td", {}, v.length ? v.join(", ") : "—");
    }
  }
}
function taskTable(tasks){
  const cols = visibleCols();
  const tbl = el("table", {}, el("tr", {}, cols.map(thFor)));
  for (const t of tasks)
    tbl.append(el("tr", {class: t.pending ? "pending" : ""}, cols.map(c => cellFor(c, t))));
  return el("div", {class: "tablewrap"}, tbl);
}
function renderByProject(main, tasks){
  const known = new Map(data.projects.map(p => [p.title, p]));
  const groups = new Map();
  for (const p of data.projects)
    if (!["done", "archived", "cancelled"].includes(p.status)) groups.set(p.title, []);
  for (const t of tasks) for (const name of t.projects){
    if (!groups.has(name)) groups.set(name, []);
    groups.get(name).push(t);
  }
  const names = [...groups.keys()].sort((a, b) => a.localeCompare(b));
  for (const name of names){
    const rows = groups.get(name), p = known.get(name);
    if (!rows.length && !p) continue;
    const head = el("h2", {}, p ? noteLink(p) : name,
      p ? el("span", {class: "pstat s-" + p.status}, p.status) : null,
      " ", el("span", {class: "count"}, "(" + rows.length + ")"));
    main.append(el("section", {}, head,
      rows.length ? taskTable(rows) : el("p", {class: "meta"}, "No matching tasks.")));
  }
  const noproj = tasks.filter(t => !t.projects.length);
  main.append(section("— No project —", "(" + noproj.length + ")",
    noproj.length ? taskTable(noproj) : el("p", {class: "meta"}, "Every task is attached to a project.")));
}
function renderGrouped(main, tasks, viewId){
  if (viewId === "project") return renderByProject(main, tasks);
  const bucket = new Map(); const noneRows = [];
  const push = (k, t) => { if (!bucket.has(k)) bucket.set(k, []); bucket.get(k).push(t); };
  let entries = [], noneLabel = "";
  if (viewId === "status"){
    for (const t of tasks) push(t.status || "—", t);
    entries = data.vocab.task.filter(s => bucket.has(s)).map(s => [s, bucket.get(s)]);
    for (const [k, v] of bucket) if (!data.vocab.task.includes(k)) entries.push([k, v]);
  } else if (viewId === "assignee"){
    for (const t of tasks){ if (!t.assignee.length) noneRows.push(t); for (const a of t.assignee) push(a, t); }
    entries = [...bucket.entries()].sort((a, b) => a[0].localeCompare(b[0]));
    noneLabel = "— Unassigned —";
  } else if (viewId === "company"){
    for (const t of tasks){ if (!t.company.length) noneRows.push(t); for (const c of t.company) push(c, t); }
    entries = [...bucket.entries()].sort((a, b) => a[0].localeCompare(b[0]));
    noneLabel = "— No company —";
  } else {  // due
    for (const t of tasks) push(dueBucket(t), t);
    entries = DUE_BUCKETS.filter(([v]) => bucket.has(v)).map(([v, lbl]) => [lbl, bucket.get(v)]);
  }
  if (!entries.length && !noneRows.length)
    return main.append(el("p", {class: "meta"}, "No tasks match the current filters."));
  for (const [name, rows] of entries){
    const head = el("h2", {},
      viewId === "status" ? el("span", {class: "pstat s-" + name}, name) : name,
      " ", el("span", {class: "count"}, "(" + rows.length + ")"));
    main.append(el("section", {}, head, taskTable(rows)));
  }
  if (noneLabel && noneRows.length)
    main.append(section(noneLabel, "(" + noneRows.length + ")", taskTable(noneRows)));
}
function renderOverview(main){
  const rowCls = (it) => it.pending ? "pending" : "";
  function plainTable(headers, rows){
    const t = el("table", {}, el("tr", {}, headers.map(h => el("th", {}, h))));
    for (const r of rows) t.append(r);
    return el("div", {class: "tablewrap"}, t);
  }
  const eng = data.engagements.filter(x => x.status !== "done" && x.status !== "lost");
  if (eng.length){
    main.append(section("📈 Pipeline", "(" + eng.length + ")",
      plainTable(["Engagement", "Stage", "Org", "Value", "Owner"], eng.map(x =>
        el("tr", {class: rowCls(x)}, el("td", {}, noteLink(x)), el("td", {}, pill(x)),
           el("td", {}, x.org.join(", ")), el("td", {}, dash(x.value)),
           el("td", {}, dash(x.owner.join(", "))))))));
  }
  const proj = data.projects.filter(p => !["done", "archived", "cancelled"].includes(p.status));
  if (proj.length){
    main.append(section("🚀 Projects", "(" + proj.length + ")",
      plainTable(["Project", "Status", "Domain", "Due", "People"], proj.map(p =>
        el("tr", {class: rowCls(p)}, el("td", {}, noteLink(p)), el("td", {}, pill(p)),
           el("td", {}, dash(p.domain)), dueCell(p),
           el("td", {}, p.people.join(", ")))))));
  }
  if (data.orgs.length){
    main.append(section("🏢 Organizations", "(" + data.orgs.length + ")",
      plainTable(["Org", "Relationship", "Sector"], data.orgs.map(o =>
        el("tr", {}, el("td", {}, noteLink(o)), el("td", {}, dash(o.relationship)),
           el("td", {}, dash(o.sector)))))));
  }
  if (data.funds.length){
    const n = (x) => Number.isInteger(x) ? x.toLocaleString() :
                     x.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
    main.append(section("💰 Funds", null,
      plainTable(["Fund", "Currency", "Cash", "Receivables", "Pledges"], data.funds.map(f =>
        el("tr", {}, el("td", {}, f.fund), el("td", {}, f.currency), el("td", {}, n(f.cash)),
           el("td", {}, n(f.receivables)), el("td", {}, n(f.pledges)))))));
  }
  if (data.meetings.length){
    main.append(section("🗣️ Recent meetings", null,
      plainTable(["Meeting", "Date", "People"], data.meetings.map(m =>
        el("tr", {}, el("td", {}, noteLink(m)), el("td", {}, dash(m.created)),
           el("td", {}, m.people.join(", ")))))));
  }
  if (data.people.length){
    main.append(section("👥 People", "(" + data.people.length + ")",
      plainTable(["Person", "Title", "Groups", "Last contact"], data.people.map(p =>
        el("tr", {}, el("td", {}, noteLink(p)), el("td", {}, dash(p.job_title)),
           el("td", {}, dash(p.groups.join(", "))), el("td", {}, dash(p.last_contact)))))));
  }
}
function render(){
  if (!data) return;
  if (menuKind === "item") closeMenu();  // rows may shift under an open item menu
  renderTabs();
  renderViewbar();
  const main = $("main"); main.innerHTML = "";
  $("f-clear").style.visibility = anyFilterActive() ? "visible" : "hidden";
  if (state.tab === "overview") return renderOverview(main);
  const base = tabBase(state.tab);
  const filtered = applyFilters(base);
  const viewId = currentView();
  if (viewId !== "table") return renderGrouped(main, filtered, viewId);
  const od = filtered.filter(t => t.overdue).length;
  const label = state.tab === "all" ? "✅ All tasks"
              : state.tab === "personal" ? "👤 Personal / other tasks"
              : "🏢 " + state.tab.slice(3) + " tasks";
  main.append(section(label,
    "(showing " + filtered.length + " of " + base.length + (od ? " · " + od + " overdue" : "") + ")",
    filtered.length ? taskTable(filtered)
                    : el("p", {class: "meta"}, "No tasks match the current filters.")));
}
function renderAll(){ render(); }

/* ------------------------------------------------ data + boot */
async function refresh(){
  // Never swap `data` under an in-flight write: the scan may predate the write,
  // which would revert the pill and leave a stale mtime (spurious 409 next click).
  // Likewise never yank an open editor out from under the user mid-edit.
  if (pendingWrites || menuKind === "item"){ refreshQueued = true; return; }
  const btn = $("refresh"); btn.classList.add("spin");
  const started = Date.now();
  try {
    const r = await fetch("/api/data", {cache: "no-store"});
    if (!r.ok) throw new Error(r.status);
    const fresh = await r.json();
    if (pendingWrites){ refreshQueued = true; return; }
    if (started < lastWriteAt){ return refresh(); }  // scan predates a completed write
    data = fresh;
    for (const t of data.tasks) t.vtype = "task";
    for (const e of data.engagements) e.vtype = "engagement";
    for (const p of data.projects) p.vtype = "project";
    setOffline(false);
    if (!state._init){
      state._init = true;
      // first run: hide done/cancelled by default (clearable like any filter)
      if (state.colf.status === undefined)
        state.colf.status = data.vocab.task.filter(s => s !== "done" && s !== "cancelled");
      saveState();
    }
    $("meta").textContent = "refreshed " + new Date().toLocaleTimeString() +
      " · " + data.notes_scanned + " notes · links open in Obsidian";
    render();
  } catch (err){
    setOffline(true);
    if (!data) $("main").innerHTML =
      "<p class='meta'>Could not reach the vault. Is the dashboard server running? " +
      "Double-click <b>Start Dashboard.command</b> in Maps/Dashboards.</p>";
  } finally {
    btn.classList.remove("spin");
  }
}
function setAuto(secs){
  clearInterval(autoTimer); autoTimer = null;
  if (secs > 0) autoTimer = setInterval(refresh, secs * 1000);
  localStorage.setItem(AKEY, String(secs));
}
$("refresh").addEventListener("click", refresh);
$("retry").addEventListener("click", refresh);
$("auto").addEventListener("change", (e) => setAuto(+e.target.value));
$("colsbtn").addEventListener("click", openColsMenu);
document.addEventListener("visibilitychange", () => { if (!document.hidden && data) refresh(); });
let qTimer = null;
$("f-q").addEventListener("input", (e) => {
  clearTimeout(qTimer);
  qTimer = setTimeout(() => { state.q = e.target.value.trim(); saveState(); render(); }, 130);
});
$("f-clear").addEventListener("click", () => {
  if (!data) return;
  state.colf = {}; state.sort = null; state.q = ""; $("f-q").value = "";
  saveState(); render();
});

loadState();
const autoSaved = +(localStorage.getItem(AKEY) || 0);
$("auto").value = String(autoSaved); setAuto(autoSaved);
refresh();
</script></body></html>
"""


# ---------------------------------------------------------------- entry point

def probe_existing(port):
    import urllib.request
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health", timeout=2) as r:
            return json.load(r)
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("vault", nargs="?", default=None)
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--vault-name", default=None)
    ap.add_argument("--open", action="store_true", help="open the dashboard in the browser")
    a = ap.parse_args()

    if a.vault is None:
        if HERE.name == "Dashboards" and HERE.parent.name == "Maps":
            a.vault = str(HERE.parent.parent)
        else:
            a.vault = "."
            print("Note: no vault argument and not inside <vault>/Maps/Dashboards — "
                  "using the current directory as the vault.")
    vault = pathlib.Path(a.vault).resolve()
    name = a.vault_name or vault.name
    url = f"http://127.0.0.1:{a.port}/"

    Handler.VAULT, Handler.NAME, Handler.PORT = vault, name, a.port
    global APP_HTML
    APP_HTML = APP_HTML.replace("🧠 Second Brain — Dashboard", f"🧠 {name} — Dashboard")

    try:
        srv = ThreadingHTTPServer(("127.0.0.1", a.port), Handler)
    except OSError as e:
        if e.errno in (48, 98):  # EADDRINUSE (mac, linux)
            info = probe_existing(a.port)
            if info and info.get("app") == APP_ID and info.get("vault") == name:
                print(f"Dashboard already running at {url} (pid {info.get('pid')}).")
                if a.open:
                    webbrowser.open(url)
                return 0
            if info and info.get("app") == APP_ID:
                print(f"Port {a.port} serves the dashboard for vault "
                      f"'{info.get('vault')}' — try --port {a.port + 1} for '{name}'.")
                return 1
            print(f"Port {a.port} is in use by another program — try --port {a.port + 1}.")
            return 1
        raise
    srv.daemon_threads = True

    print(f"🧠 {name} dashboard → {url}   (vault: {vault})")
    print("Press Ctrl-C to stop.")
    if a.open:
        threading.Timer(0.4, webbrowser.open, args=(url,)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
