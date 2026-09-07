#!/usr/bin/env python3
"""Say, at the start of a conversation, that an update has been waiting - and nothing else.

Wired as a second `SessionStart` hook. **It touches no network and reads two small files.** The daily
check writes what it found; this only compares two numbers already on disk.

    installed  ~/.claude/second-brain-release.json   written by tools/update.py
    available  ~/.claude/second-brain-update.json    written by tools/update.py --check

**Silent when they match, which is almost always.** It speaks after the update has been available for
three days, on the assumption that the notification was seen and nothing happened - a person who has
just been told does not need telling again in the next hour.
"""
import io
import json
import os
import sys
import time

CLAUDE = os.path.join(os.path.expanduser("~"), ".claude")
GRACE_DAYS = 3


def load(name):
    p = os.path.join(CLAUDE, name)
    try:
        with io.open(p, encoding="utf-8") as fh:
            return json.load(fh), os.path.getmtime(p)
    except (OSError, ValueError):
        return None, 0


def main():
    have, _ = load("second-brain-release.json")
    avail, seen = load("second-brain-update.json")
    if not have or not avail:
        return 0
    a, b = str(avail.get("release", "")), str(have.get("release", ""))
    if not a or a == b:
        return 0
    if (time.time() - seen) < GRACE_DAYS * 86400:
        return 0
    msg = ("Second brain: release %s has been available for more than %d days and this machine is "
           "still on %s. Mention it once, briefly, and say that \"update the second brain\" installs "
           "it in seconds. Do not run it without being asked, and do not raise it again this session."
           % (a, GRACE_DAYS, b))
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart",
                                             "additionalContext": msg}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
