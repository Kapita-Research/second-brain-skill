#!/usr/bin/env python3
"""Derive each person's `last-contact:` from the meetings they attended.

Usage:
    python3 sync_last_contact.py /path/to/vault            # dry run (default)
    python3 sync_last_contact.py /path/to/vault --apply    # write the changes
    python3 sync_last_contact.py /path/to/vault --since 2026-01-01

`last-contact` is the one person field nothing maintains: the rule says "update it
when you file an interaction", and in practice it rots — which quietly breaks the
review sweep that depends on it. But the vault already knows the answer: every
`type: meeting` note carries a date and a `people:` roster. This reads those and
writes each attendee's most recent meeting date back to their person note.

Guarantees (same contract as the dashboard server's writers):
  - **Never moves a date backwards.** A manually-set newer value always wins, so
    contact made over WhatsApp/email//in person — which no note records — is safe.
  - Touches only the `last-contact:` line; inserted at its Person-template
    position when the note lacks the key. No reformatting, no key reordering.
  - Atomic per-file write (temp + os.replace).
  - Idempotent: a second run reports zero changes.
  - Skips `contact: none` (authors, historical figures — they have no contact date)
    and reports `contact: dormant` people who turn out to have a meeting.

Stdlib only; uses PyYAML for frontmatter when available.
Exit code: 0 normally, 1 on a vault/IO error.
"""
import argparse, datetime, os, pathlib, re, sys, tempfile

FM_RE = re.compile(r"^---\r?\n(.*?)\r?\n---(\r?\n|$)", re.S)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")
# meeting date: an explicit `date:` wins, else `created:` (the stock meeting schema)
DATE_KEYS = ("date", "created")


def parse_frontmatter(text):
    """Return the frontmatter dict, or None. Mirrors validate_vault.py."""
    m = FM_RE.match(text)
    if not m:
        return None
    raw = m.group(1)
    try:
        import yaml
        try:
            d = yaml.safe_load(raw)
            return d if isinstance(d, dict) else None
        except Exception:
            return None
    except ImportError:
        pass
    d, key = {}, None
    for line in raw.splitlines():                      # minimal list-aware fallback
        km = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if km:
            key, v = km.group(1), km.group(2).strip()
            d[key] = v.strip('"').strip("'") if v else []
        elif key and re.match(r"^\s+-\s+", line):
            item = re.sub(r"^\s+-\s+", "", line).strip().strip('"').strip("'")
            if isinstance(d.get(key), list):
                d[key].append(item)
    return d


def as_date(v):
    if isinstance(v, datetime.date) and not isinstance(v, datetime.datetime):
        return v
    if isinstance(v, datetime.datetime):
        return v.date()
    s = str(v or "").strip().strip('"').strip("'")
    return datetime.date.fromisoformat(s[:10]) if DATE_RE.match(s) else None


def link_names(v):
    """['[[A]]', 'B|shown'] -> {'A', 'B'} — bare names, no brackets or aliases."""
    if not v:
        return set()
    if not isinstance(v, list):
        v = [v]
    out = set()
    for x in v:
        n = re.sub(r"^\[\[|\]\]$", "", str(x).strip().strip('"').strip("'"))
        n = n.split("|")[0].split("#")[0].strip()
        if n:
            out.add(n)
    return out


def template_order(vault):
    """Ordered frontmatter keys from Templates/Person Template.md (may be absent)."""
    p = vault / "Templates" / "Person Template.md"
    if not p.is_file():
        return []
    m = FM_RE.match(p.read_text(encoding="utf-8", errors="replace"))
    if not m:
        return []
    return [km.group(1) for km in
            (re.match(r"^([A-Za-z_][\w-]*):", ln) for ln in m.group(1).splitlines()) if km]


def set_last_contact(text, value, order):
    """Rewrite or insert `last-contact:`. Returns new text, or None if impossible."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip() != "---":
        return None
    end = next((i for i in range(1, len(lines)) if lines[i].rstrip() == "---"), None)
    if end is None:
        return None
    eol = "\r\n" if lines[0].endswith("\r\n") else "\n"
    new = f"last-contact: {value}{eol}"

    for i in range(1, end):
        if re.match(r"^last-contact:", lines[i]):
            # a list under the key spans continuation lines this editor can't rewrite
            if i + 1 < end and re.match(r"^\s+-\s+", lines[i + 1]):
                return None
            lines[i] = new
            return "".join(lines)

    present = {}
    for i in range(1, end):
        km = re.match(r"^([A-Za-z_][\w-]*):", lines[i])
        if km:
            present[km.group(1)] = i
    at = end                                            # default: end of frontmatter
    if "last-contact" in order:
        for k in reversed(order[:order.index("last-contact")]):
            if k in present:                            # after the nearest preceding
                at = present[k] + 1                     # template key this note has
                while at < end and re.match(r"^\s+[-\w]", lines[at]):
                    at += 1                             # step over its list items
                break
    lines.insert(at, new)
    return "".join(lines)


def write_atomic(path, text):
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".sync-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vault")
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    ap.add_argument("--since", default="", help="ignore meetings before YYYY-MM-DD")
    ap.add_argument("--exclude", default="", help="comma-separated person notes to leave "
                    "alone — normally the vault owner, who attends their own meetings "
                    "and so would always read as freshly contacted")
    a = ap.parse_args()
    V = pathlib.Path(a.vault)
    if not V.is_dir():
        print(f"ERROR: not a directory: {V}"); sys.exit(1)
    since = as_date(a.since) if a.since else None
    if a.since and since is None:
        print(f"ERROR: --since must be YYYY-MM-DD (got {a.since!r})"); sys.exit(1)

    people, meetings = {}, []
    for p in sorted(V.rglob("*.md")):
        rel = p.relative_to(V)
        if rel.parts[0] in (".obsidian", "Templates", "Archive") or ".trash" in rel.parts:
            continue
        fm = parse_frontmatter(p.read_text(encoding="utf-8", errors="replace"))
        if not fm:
            continue
        t = fm.get("type")
        if t == "person":
            people[p.stem] = (p, fm)
        elif t == "meeting":
            d = next((as_date(fm.get(k)) for k in DATE_KEYS if fm.get(k)), None)
            if d and (since is None or d >= since):
                meetings.append((p, d, link_names(fm.get("people"))))

    latest = {}                                          # person stem -> newest date
    for _, d, names in meetings:
        for n in names:
            if latest.get(n) is None or d > latest[n]:
                latest[n] = d

    excluded = {n.strip() for n in a.exclude.split(",") if n.strip()}
    order = template_order(V)
    updates, unchanged, skipped, unknown, dormant = [], 0, [], [], []
    for name, d in sorted(latest.items()):
        if name in excluded:
            continue
        if name not in people:
            unknown.append(name); continue
        path, fm = people[name]
        standing = str(fm.get("contact") or "").strip()
        if standing == "none":
            skipped.append(name); continue
        if standing == "dormant":
            dormant.append((name, d))
        cur = as_date(fm.get("last-contact"))
        if cur is not None and cur >= d:
            unchanged += 1; continue
        updates.append((name, path, cur, d))

    print(f"{len(meetings)} meetings · {len(people)} people"
          f"{f' · since {since}' if since else ''}\n")
    if updates:
        print(f"{'PERSON':<26} {'CURRENT':<12} -> NEW")
        for name, _, cur, d in updates:
            print(f"  {name:<24} {str(cur or '—'):<12} -> {d}")
    print(f"\n  to update: {len(updates)}   already current: {unchanged}"
          f"   contact:none skipped: {len(skipped)}")
    if dormant:
        print("\n  NOTE — marked `contact: dormant` but attended a meeting "
              "(review the standing):")
        for name, d in dormant:
            print(f"    {name} — {d}")
    if unknown:
        print(f"\n  WARNING — linked in a meeting but no person note exists "
              f"({len(unknown)}): {', '.join(sorted(unknown))}")

    if not a.apply:
        print("\nDry run — nothing written. Re-run with --apply to write.")
        return
    written, failed = 0, []
    for name, path, _, d in updates:
        text = path.read_text(encoding="utf-8", errors="replace")
        new = set_last_contact(text, d.isoformat(), order)
        if new is None or new == text:
            failed.append(name); continue
        write_atomic(path, new); written += 1
    print(f"\nWrote {written} note(s).")
    if failed:
        print(f"  SKIPPED (unparseable or `last-contact` is a YAML list): "
              f"{', '.join(failed)}")


if __name__ == "__main__":
    main()
