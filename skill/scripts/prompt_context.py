#!/usr/bin/env python3
"""The per-message hook: the standing reminder, plus the notes this message names.

Wired as the `UserPromptSubmit` hook. The harness passes the message on stdin; whatever this prints
as `additionalContext` is placed beside it before the model reads it.

**Why.** The reminder alone says *search the vault*, and the search that follows is several round
trips. When the message names something the vault already has a note for, the note's name is known
before the model starts, and the first of those trips is not needed.

**A head start, never the search.** It matches only names spelled the way a note spells them (its
title and its `aliases`, compared after normalisation). A person called by a nickname the note does
not carry, or a question asked in one language about a note titled in another, is not in the list, so
the message says the list is not the whole search, every time.

**It cannot break a conversation.** Any failure prints the plain reminder and exits 0. It reads note
headers only, never a body, and never a judgement. The name index is cached against the vault's file
count and newest modification time, so an unchanged vault costs one directory walk.
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vault_text import CLAUDE, as_list, frontmatter, is_private, iter_notes, norm, read, split_note, vault_path  # noqa: E402

RULE = ("Second brain: if this turn touches a person, project, client, decision, commitment, figure or "
        "date - search the vault before answering. If it produces one - record it. Neither is announced.")
CACHE = os.path.join(CLAUDE, "second-brain-names.json")
MAX_SHOWN = 8
MIN_LEN = 4


def build(vault):
    """[(normalised name, title, type, status)] for every title, alias and distinctive first name."""
    rows, first_names = [], {}
    for p, rel, title in iter_notes(vault):
        fm = frontmatter(split_note(read(p, 4096))[0])
        if is_private(rel, fm):
            continue
        # the owner is on the session card already; listing them on every message is noise
        if rel.replace("\\", "/") == "People/Me.md" or str(fm.get("owner", "")).lower() == "true":
            continue
        typ, status = str(fm.get("type", "")), str(fm.get("status", ""))
        for i, name in enumerate([title] + as_list(fm.get("aliases"))):
            n = norm(name)
            # an alias that is one ordinary lower-case word ("phone", "devices") matches half of all
            # messages and names nothing; a title, a proper noun or another script is kept
            if i and name.isascii() and name.islower() and " " not in name.strip():
                continue
            if len(n) >= MIN_LEN and len(n.split()) <= 8:
                rows.append((n, title, typ, status))
        if typ == "person" and " " in title.strip():
            f = norm(title.split()[0])
            if len(f) >= MIN_LEN:
                first_names.setdefault(f, []).append((title, typ, status))
    for f, owners in first_names.items():
        if len(owners) == 1:                       # a first name two people share names nobody
            rows.append((f,) + owners[0])
    return rows


def signature(vault):
    count, newest = 0, 0.0
    for p, _, _ in iter_notes(vault):
        count += 1
        try:
            newest = max(newest, os.path.getmtime(p))
        except OSError:
            pass
    return [vault, count, newest]


def index(vault):
    sig = signature(vault)
    try:
        with io.open(CACHE, encoding="utf-8") as fh:
            c = json.load(fh)
        if c.get("sig") == sig:
            return [tuple(r) for r in c["rows"]]
    except (OSError, ValueError, KeyError):
        pass
    rows = build(vault)
    try:
        with io.open(CACHE, "w", encoding="utf-8") as fh:
            json.dump({"sig": sig, "rows": rows}, fh, ensure_ascii=False)
    except OSError:
        pass
    return rows


def matches(prompt, rows):
    text = " %s " % norm(prompt)
    found = {}
    for n, title, typ, status in rows:
        if (" %s " % n) in text:
            if title not in found or len(n) > len(found[title][0]):
                found[title] = (n, typ, status)
    # "Acme" inside "Acme Research" names the longer thing, not both
    names = [v[0] for v in found.values()]
    keep = {t: v for t, v in found.items()
            if not any(o != v[0] and (" %s " % v[0]) in (" %s " % o) for o in names)}
    return sorted(((t, (len(v[0]), v[1], v[2])) for t, v in keep.items()), key=lambda kv: -kv[1][0])


def emit(text):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                                             "additionalContext": text}}, ensure_ascii=False))


def main():
    try:
        raw = sys.stdin.read() if not sys.stdin.isatty() else ""
        prompt = (json.loads(raw).get("prompt") or "") if raw.strip() else ""
        vault = vault_path()
        if not prompt or not vault:
            emit(RULE)
            return 0
        found = matches(prompt, index(vault))
        if not found:
            emit(RULE)
            return 0
        listed = " · ".join("[[%s]] (%s)" % (t, ", ".join(x for x in (typ, st) if x))
                            for t, (_, typ, st) in found[:MAX_SHOWN])
        more = " and %d more" % (len(found) - MAX_SHOWN) if len(found) > MAX_SHOWN else ""
        emit(RULE + " Notes this message names, matched by title or alias: " + listed + more + ". "
             "Read the ones the answer depends on first. This list only knows names spelled the way "
             "the notes spell them, so it is a head start on the search, never a reason to skip it.")
    except Exception:                                # a hook must never be the thing that fails
        emit(RULE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
