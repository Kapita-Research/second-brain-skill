#!/usr/bin/env python3
"""Search the vault in one call: names, aliases, fields and text, ranked, with the lines that matched.

    python3 find.py "Erbil" "income factor" "دخل"          # terms are OR'd; quote a phrase
    python3 find.py --type finding "piped water"
    python3 find.py --vault "<path>" --limit 12 "Essam"

**Why it exists.** Searching by hand is a grep, a look at the list, then a file opened, then another:
each of those is a round trip that re-sends the whole conversation. This returns the few notes that
matter, with enough of each to decide whether to open it, in one.

**What it will not do.**
- ⛔ **It never reads `Judgements/` or a `type: judgement` note.** Those are pruned before a file is
  opened, because a script that walks the vault would otherwise pass the judgement guard unseen.
- ⛔ **It never shortens a finding.** A figure is shown whole, with its base, both dates and its
  caveat, or it is listed by name for you to open: a finding is quoted whole or not at all. A
  superseded one ranks below what replaced it.
- **It never hides that it stopped.** Past the budget it lists what else matched, by name, and says
  how many. Past the limit it says so. A term that matched nothing is named, so "there is nothing in
  the vault" can say which words were searched.

Names are compared the way the skill compares them across scripts (`vault_text.norm`). **It does not
translate:** an Arabic question still needs its English words passed in, because the vault's
filenames are English by rule.
"""
import argparse
import os
import sys

sys.dont_write_bytecode = True           # a hook runs from the installed skill; leave no cache there
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vault_text import as_list, frontmatter, is_private, iter_notes, norm, read, split_note, vault_path  # noqa: E402

SHOWN_FIELDS = ("status", "due", "people", "projects", "client", "org", "source", "domain")
FINDING_FIELDS = ("measure", "population", "base_n", "sample_n", "collected", "describes", "basis", "caveat")


def statement(body):
    """The sentence a finding is quoted by: its first block quote, else its first paragraph."""
    lines = [l for l in body.splitlines() if l.strip() and not l.startswith("#")]
    quote = [l.lstrip("> ").strip() for l in lines if l.startswith(">")]
    if quote:
        out = []
        for l in body.splitlines():
            if l.startswith(">"):
                out.append(l.lstrip("> ").strip())
            elif out:
                break
        return " ".join(x for x in out if x)
    return lines[0].strip() if lines else ""


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("terms", nargs="+")
    ap.add_argument("--vault")
    ap.add_argument("--type", help="only notes of this type")
    ap.add_argument("--limit", type=int, default=8, help="notes shown in detail (default 8)")
    ap.add_argument("--budget", type=int, default=3000, help="characters of detail (default 3000)")
    a = ap.parse_args()

    vault = a.vault or vault_path()
    if not vault or not os.path.isdir(vault):
        print("No vault found. Pass --vault \"<path>\".")
        return 1
    terms = [(t, norm(t)) for t in a.terms if norm(t)]
    matched_by = {t: 0 for t, _ in terms}
    hits = []

    for p, rel, title in iter_notes(vault):
        text = read(p)
        fm_text, body = split_note(text)
        fm = frontmatter(fm_text)
        if is_private(rel, fm):
            continue
        if a.type and str(fm.get("type", "")).lower() != a.type.lower():
            continue
        n_title = " %s " % norm(title)
        n_alias = " %s " % " | ".join(norm(x) for x in as_list(fm.get("aliases")))
        n_fm = " %s " % norm(" ".join(" ".join(as_list(v)) for k, v in fm.items() if k != "aliases"))
        body_lines = body.splitlines()
        n_body = [norm(l) for l in body_lines]
        score, lines, which = 0, [], set()
        for raw, t in terms:
            got = False
            if t in n_title:
                score += 10; got = True
            if t in n_alias:
                score += 8; got = True
            if t in n_fm:
                score += 3; got = True
            count = 0
            for i, nl in enumerate(n_body):
                if t in nl:
                    count += 1
                    if len(lines) < 3 and i not in which:
                        which.add(i)
                        lines.append(body_lines[i].strip())
            if count:
                score += min(count, 5); got = True
            lines[:] = [l for l in lines if not l.startswith("# ")]
            if got:
                matched_by[raw] += 1
        if score:
            if str(fm.get("status", "")).lower() in ("superseded", "archived", "cancelled", "done"):
                score = score / 2.0          # still found, but what is current comes first
            hits.append((score, os.path.getmtime(p), title, rel, fm, body, lines))

    hits.sort(key=lambda h: (-h[0], -h[1]))
    out, used, shown = [], 0, 0
    for score, _, title, rel, fm, body, lines in hits:
        if shown >= a.limit:
            break
        typ = str(fm.get("type", "")) or "?"
        head = "[[%s]]  %s%s  (%s)" % (title, typ, (", " + str(fm.get("status"))) if fm.get("status") else "",
                                       rel.replace("\\", "/"))
        block = [head]
        if typ == "finding":
            # whole or not at all: the conditions travel with the number
            block.append("  " + statement(body))
            for k in FINDING_FIELDS:
                if fm.get(k) not in (None, "", []):
                    block.append("  %s: %s" % (k, " ".join(as_list(fm.get(k)))))
        else:
            fields = ["%s: %s" % (k, ", ".join(as_list(fm.get(k))[:5])[:120]) for k in SHOWN_FIELDS
                      if fm.get(k) not in (None, "", [])]
            if fields:
                block.append("  " + " | ".join(fields))
            for l in lines:
                block.append("  > " + (l[:220] + ("..." if len(l) > 220 else "")))
        size = sum(len(b) + 1 for b in block)
        if shown and used + size > a.budget:
            break
        out.extend(block)
        used += size
        shown += 1

    rest = hits[shown:]
    print("\n".join(out) if out else "No note matched.")
    if rest:
        names = ", ".join("[[%s]]" % h[2] for h in rest[:25])
        print("\n%d more matched, best first: %s%s" % (len(rest), names, " ..." if len(rest) > 25 else ""))
    print("\nSearched: " + "; ".join("'%s' %s" % (t, ("%d note(s)" % n) if n else "NOTHING")
                                     for t, n in matched_by.items()))
    print("Judgements/ and type: judgement are never searched by this script.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
