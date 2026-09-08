#!/usr/bin/env python3
"""PreToolUse guard: a judgement note is never opened without the owner saying so.

`type: judgement` holds the owner's private opinion of a person or a thing. The rule is that it
never leaves the vault in any form - see `references/note-types.md`. **Everything else enforcing
that rule is an instruction, read and followed by a model. This is not.** It runs in the harness,
before the tool does, and a model cannot approve its own way past it.

Wire it as a `PreToolUse` hook on `Read|Grep|Glob|Bash` in `~/.claude/settings.json`:

    {"hooks": {"PreToolUse": [{"matcher": "Read|Grep|Glob|Bash", "hooks": [{"type": "command",
      "command": "python \\"<skill>/scripts/guard_judgements.py\\"", "timeout": 5}]}]}}

**What it does:** any tool call that reaches the judgements folder - a `Judgements/` path segment, or a
`type: judgement` query - becomes a permission prompt the owner answers.

⚠️ **It matches a path, not the word.** *An earlier version matched the bare word and fired on any
command that merely mentioned judgements*, which taught the owner to click through without reading.
**A guard that cries wolf is worse than no guard**, because the one real prompt looks like the others.
⛔ **The cost of the narrowing, stated:** a vault-wide search for the word will no longer prompt. It
never covered that properly anyway - a search for any *other* word can return a line from a judgement
note and always could. **This is a tripwire on the obvious paths, not a net.** Asking for a judgement deliberately costs one click. Reaching
for one while writing something for somebody else produces a prompt nobody expected - **and that
surprise is the alarm.**

⛔ **It emits a decision ONLY on a match.** Anything else produces no output at all, so this can never
widen a permission for any other tool call.

⚠️ **What it cannot do:** once a judgement is in context - approved, or pasted by the owner - nothing
un-reads it. **Do not open one in the same conversation that is writing for someone else.** That rule
belongs to the person, not to this script.
"""
import json
import sys

# A path segment, or the frontmatter line. NOT the bare word: matching that fired on any command
# that merely mentioned judgements - editing the vocabulary, writing a changelog entry, grepping the
# skill's own source - and a guard that cries wolf gets clicked through. Habituation kills an alarm
# faster than deleting it does.
import re

SEP = r"[/\\]"                       # a path separator, either slash, on either platform
EDGE = r"[\s\"'`,;()]"               # what a path is wrapped in when it sits inside a command
REACHES = re.compile(
    r"(?:^|" + SEP + r"|" + EDGE + r")judgements(?:" + SEP + r"|" + EDGE + r"|$)"
    r"|type:\s*judgement", re.I)

# Every field across Read, Grep, Glob and Bash that could name or reach the folder.
FIELDS = ("file_path", "path", "notebook_path", "pattern", "glob", "command")


def main():
    try:
        data = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0                      # never block work because the guard could not parse

    ti = data.get("tool_input") or {}
    hay = " ".join(str(ti.get(f, "")) for f in FIELDS)

    if not REACHES.search(hay):
        return 0                      # no output = no opinion; every other call is untouched

    json.dump({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason":
            "This reaches a judgement note - your private opinion of a person or a thing. "
            "It must never appear in, or shape, anything written for someone else. "
            "Allow it only if you asked for it. If you did not, say no and ask what it was for.",
    }}, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
