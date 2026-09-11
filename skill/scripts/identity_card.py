#!/usr/bin/env python3
"""Put the owner's name, spellings, title and addresses in front of the model at the start of a session.

Wired as a `SessionStart` hook. The owner's person note (`People/Me.md`, or a person note carrying
`owner: true`) is read **now, from the live note**, and its fields become a short card.

**Why.** Nothing about the owner may be guessed or left as a placeholder, so a conversation that
writes a signature, a bio or a form opens that note first, and a working session does it many times.
The card answers the common case, their name, how it is spelled, their title and their email, without
a read.

**What it is not.** It is not a copy that goes stale: it is rebuilt every session from the note. And
it is not the whole record: the card says so, and anything not on it, the projects, the people, what
was decided, is still read from the note and its links. Silent when there is no vault or no owner note.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vault_text import as_list, frontmatter, read, split_note, vault_path  # noqa: E402

SKIP = {"type", "domain", "created", "updated", "tags", "last-contact", "owner", "groups", "cssclasses"}
MAX_VALUE, MAX_CARD = 160, 1400


def owner_note(vault):
    people = os.path.join(vault, "People")
    me = os.path.join(people, "Me.md")
    if os.path.isfile(me):
        return me
    if os.path.isdir(people):
        for f in sorted(os.listdir(people)):
            if f.endswith(".md"):
                fm = frontmatter(split_note(read(os.path.join(people, f), 4096))[0])
                if str(fm.get("owner", "")).lower() == "true":
                    return os.path.join(people, f)
    return None


def main():
    try:
        vault = vault_path()
        note = owner_note(vault) if vault else None
        if not note:
            return 0
        fm = frontmatter(split_note(read(note, 8192))[0])
        rel = os.path.relpath(note, vault).replace("\\", "/")
        names = as_list(fm.get("aliases"))
        title = os.path.basename(note)[:-3]
        parts = []
        if title != "Me":
            names = [title] + names
        if names:
            parts.append("name and its spellings: " + ", ".join(names))
        for k, v in fm.items():
            if k in SKIP or k == "aliases":
                continue
            val = ", ".join(as_list(v)).strip()
            if val:
                parts.append("%s: %s" % (k, val[:MAX_VALUE]))
        if not parts:
            return 0
        card = "; ".join(parts)[:MAX_CARD]
        msg = ("Second brain, the owner, read from %s at the start of this session: %s. Use these rather "
               "than asking or guessing, and never write a placeholder for them. Anything not on this "
               "card - their projects, the people they deal with, what was decided - is in %s and its "
               "links: read it." % (rel, card, rel))
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart",
                                                 "additionalContext": msg}}, ensure_ascii=False))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
