#!/usr/bin/env python3
"""Check the KAPITA layer against the skill.

`kapita-vault-CLAUDE.md` sits in the vault and **overrides the skill**. So a word in it that
disagrees with the skill wins — silently, with no error anywhere. This is the only thing that
notices.

Two real divergences had already accumulated before this existed:

    `Shared/`  where the skill says `Outbox/`   — the firm's importer reads an empty folder
    `company`  where the skill says `business`  — every base filtering `business` misses the note

Run before distributing, and after any edit to the layer:

    python tools/check-kapita-layer.py

**And point it at a vault's own copy**, which is where this actually bites. `CLAUDE.md` is copied
into a vault once at install and **nothing updates it** — so a vault can still be reading the version
that said `Shared/`, months after the source said `Outbox/`:

    python tools/check-kapita-layer.py "<vault>/KAPITA.md"

Exit 0 = clean. Exit 1 = something to look at.

**What it does not catch:** meaning. Two files can use the same word for different things, and this
sees only that the word exists on both sides.
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYER = os.path.join(ROOT, "kapita-vault-KAPITA.md")
SKILL = os.path.join(ROOT, "skill")

ALLOWED_EXTRA_TYPES = {"type"}  # `type: type` — the vocabulary registry note

# Not frontmatter keys: the two vocabulary lists the vault declares for validate_vault.py.
VOCAB_KEYS = {"extra-types", "extra-statuses"}


def read(path):
    with io.open(path, encoding="utf-8") as fh:
        return fh.read()


def skill_text():
    """Every .md, .json and .base in the skill, minus evals."""
    out = []
    for base, dirs, files in os.walk(SKILL):
        dirs[:] = [d for d in dirs if d not in ("evals", "__pycache__")]
        for f in files:
            if f.endswith((".md", ".json", ".base")):
                out.append(read(os.path.join(base, f)))
    return "\n".join(out)


def main(argv=None):
    target = argv[1] if argv and len(argv) > 1 else LAYER
    if not os.path.exists(target):
        print("cannot find " + target)
        return 1
    if target != LAYER:
        print("checking a vault's own copy: " + target)
        print("")

    layer = read(target)
    skill = skill_text()
    types_json = read(os.path.join(SKILL, "assets", "types.json"))
    problems = []

    # 1 · type names the layer DECLARES — a table row, not prose.
    #     Inline `type: x` in prose is nearly always an example of a free type
    #     ("write `type: lecture` and it exists"), so it is deliberately not checked.
    types = set(re.findall(r"^\|\s*`([a-z][a-z0-9_-]+)`\s*\|", layer, re.M))
    for t in sorted(types - ALLOWED_EXTRA_TYPES):
        if not re.search(r"type:\s*" + re.escape(t) + r"\b", skill):
            problems.append(("type", t, "declared in a table; the skill never defines type: " + t))

    # 2 · folder names — a capitalised word followed by a slash, in backticks
    folders = set(re.findall(r"`([A-Z][A-Za-z]+)/`", layer))
    for f in sorted(folders):
        if ("`" + f + "/`") not in skill and (f + "/") not in skill:
            problems.append(("folder", f + "/", "the skill never mentions this folder"))

    # 3 · frontmatter field names used in the layer's yaml blocks
    fields = set()
    for block in re.findall(r"```yaml\n(.*?)```", layer, re.S):
        for line in block.splitlines():
            m = re.match(r"([a-z][a-z0-9_-]*):", line.strip())
            if m and m.group(1) not in VOCAB_KEYS:
                fields.add(m.group(1))
    # An invented field is legal - Golden Rule 3 says so, and a vault's own vocabulary is exactly
    # what this layer is for. But a field the skill has never typed renders as plain text in
    # Obsidian, so it is worth saying. A note, not a divergence.
    unknown = [f for f in sorted(fields)
               if ('"' + f + '"') not in types_json
               and not re.search(r"" + re.escape(f) + r":", skill)]

    # 4 · pointers to skill files that must exist
    for ref in sorted(set(re.findall(r"`(references/[a-z-]+\.md)`", layer))):
        if not os.path.exists(os.path.join(SKILL, ref)):
            problems.append(("path", ref, "referenced by the layer, missing from the skill"))

    # 5 · a frozen copy of a vocabulary the skill owns.
    #     Right the day it is written; a silent CAP the day the skill adds a value — and the
    #     layer wins. This has been the recurring failure of this file, so it is checked by
    #     reading the skill's own sets rather than by hard-coding them here.
    validator = read(os.path.join(SKILL, "scripts", "validate_vault.py"))
    for setname in ("TYPES", "STATUSES", "DOMAINS"):
        m = re.search(setname + r"\s*=\s*\{(.*?)\}", validator, re.S)
        if not m:
            continue
        vocab = set(re.findall(r'"([a-z][a-z0-9-]*)"', m.group(1)))
        for i, line in enumerate(layer.splitlines(), 1):
            hits = {v for v in re.findall(r"`([a-z][a-z0-9-]*)`", line) if v in vocab}
            if len(hits) >= 3:
                problems.append(("vocab", setname.lower() + " line %d" % i,
                                 "enumerates %d values the skill owns (%s ...) - point at the "
                                 "skill instead; a list here caps it"
                                 % (len(hits), ", ".join(sorted(hits)[:3]))))

    # 6 · unfilled placeholders — a different kind of problem, reported apart
    placeholders = sorted(set(re.findall(r"^([a-z_]+):\s*\[\s*(?:…|\.\.\.)\s*\]", layer, re.M)))
    problems = [p for p in problems if p[1] not in placeholders]

    if unknown:
        print("field(s) only this layer uses: " + ", ".join(unknown))
        print("  legal - an invented field is free. But the skill never types them, so Obsidian")
        print("  shows them as plain text. Add to the vault's .obsidian/types.json to fix that.")
        print("")

    if placeholders:
        print("unfilled placeholder(s): " + ", ".join(placeholders))
        print("  not a divergence - a value never decided. Fill it, or delete the line.")
        print("")

    if not problems:
        print("clean - %d declared types, %d folders, %d fields (%d layer-only)"
              % (len(types), len(folders), len(fields), len(unknown)))
        return 1 if placeholders else 0

    print("%d divergence(s) - the layer overrides the skill, so each of these wins silently:"
          % len(problems))
    print("")
    for kind, name, why in problems:
        print("  %-7s %-22s %s" % (kind, name, why))
    print("")
    print("Fix the layer, or add the term to the skill deliberately.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
