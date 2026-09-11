#!/usr/bin/env python3
"""Shared by find.py and the two hooks: where the vault is, what a note is called, how two strings compare.

Three things the scripts must agree on, so they live in one place:

- **Where the vault is.** The installer records it in `~/.claude/second-brain-release.json`; failing
  that, the path written in `~/.claude/CLAUDE.md`. A hook that cannot find the vault stays quiet.
- **What is never read.** `Judgements/` and `type: judgement` are skipped before a file is opened for
  its body. A script that walks the whole vault would otherwise walk straight past the judgement guard,
  which only sees paths in tool calls.
- **How names compare across scripts.** NFKC first, because text extracted from a PDF carries the drawn
  shape of an Arabic letter; then case, diacritics, alef and yaa/taa-marbuta variants, tatweel and
  digits. The letters that are distinct in Kurdish and Persian are left alone.
"""
import io
import json
import os
import re
import unicodedata

CLAUDE = os.path.join(os.path.expanduser("~"), ".claude")
SKIP_DIRS = {".obsidian", ".trash", ".git", "Templates", "Judgements"}

_MARKS = re.compile("[ؐ-ًؚ-ٰٟۖ-ۭ]")
_FOLD = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا",
                       "ى": "ي", "ة": "ه", "ـ": ""})
_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩"
                        "۰۱۲۳۴۵۶۷۸۹",
                        "01234567890123456789")
_NONWORD = re.compile(r"[^\w]+", re.U)


def norm(s):
    """One comparable form for a name or a query, in any script."""
    s = unicodedata.normalize("NFKC", str(s or "")).casefold()
    s = _MARKS.sub("", s).translate(_FOLD).translate(_DIGITS)
    return _NONWORD.sub(" ", s).strip()


def vault_path():
    """The vault, or None. Never guesses beyond what the installer or the owner wrote down."""
    env = os.environ.get("SECOND_BRAIN_VAULT")
    if env and os.path.isdir(env):
        return env
    try:
        with io.open(os.path.join(CLAUDE, "second-brain-release.json"), encoding="utf-8") as fh:
            v = json.load(fh).get("vault")
        if v and os.path.isdir(v):
            return v
    except (OSError, ValueError, AttributeError):
        pass
    try:
        with io.open(os.path.join(CLAUDE, "CLAUDE.md"), encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        return None
    for cand in re.findall(r"`([A-Za-z]:[\\/][^`\n]+|/[^`\n]+)`", text):
        cand = cand.strip()
        if os.path.isdir(cand) and os.path.isdir(os.path.join(cand, "People")):
            return cand
    return None


def split_note(text):
    """(frontmatter text, body). A note without frontmatter has an empty first part."""
    if text.startswith("---"):
        parts = text.split("\n---", 1)
        if len(parts) == 2:
            fm = parts[0][3:]
            body = parts[1].split("\n", 1)[1] if "\n" in parts[1] else ""
            return fm, body
    return "", text


def _scalar(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1]
    return v


def frontmatter(fm_text):
    """A small, forgiving reader: scalars, [inline, lists] and block lists. Enough for names and fields."""
    out, key = {}, None
    for line in fm_text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z0-9_\-]+):\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if val.startswith("[") and val.endswith("]"):
                items = re.findall(r"\"[^\"]*\"|'[^']*'|[^,]+", val[1:-1])
                out[key] = [_scalar(i) for i in items if i.strip()]
            elif val in ("", ">-", ">", "|", "|-"):
                out[key] = [] if val == "" else ""
            else:
                out[key] = _scalar(val)
            continue
        m = re.match(r"^\s+-\s+(.*)$", line)
        if m and key is not None:
            if not isinstance(out.get(key), list):
                out[key] = []
            out[key].append(_scalar(m.group(1)))
            continue
        if key is not None and isinstance(out.get(key), str) and line.startswith((" ", "\t")):
            out[key] = (out[key] + " " + line.strip()).strip()
    return out


def as_list(v):
    if isinstance(v, list):
        return [str(x) for x in v if str(x).strip()]
    return [str(v)] if v not in (None, "") else []


def is_private(rel, fm):
    """A judgement is never read by a script, whichever of its markers is present."""
    first = rel.replace("\\", "/").split("/", 1)[0]
    return first == "Judgements" or str(fm.get("type", "")).strip().lower() == "judgement"


def iter_notes(vault):
    """(path, rel, title) for every note, with the folders nobody searches already pruned."""
    for root, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        rel_root = os.path.relpath(root, vault)
        for f in files:
            if not f.endswith(".md") or f == "README.md":
                continue
            if rel_root == ".":
                continue                      # convention files live at the root; no note does
            p = os.path.join(root, f)
            yield p, os.path.relpath(p, vault), f[:-3]


def read(p, limit=None):
    try:
        with io.open(p, encoding="utf-8", errors="replace") as fh:
            return fh.read(limit) if limit else fh.read()
    except OSError:
        return ""
