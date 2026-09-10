#!/usr/bin/env python3
"""Vault hygiene validator for the obsidian-second-brain skill.

Usage:
    python3 validate_vault.py /path/to/vault [--extra-types a,b] [--extra-statuses x,y]

Checks (stdlib only; uses PyYAML for full parsing when available):
  ERRORS   - frontmatter missing/unparseable, missing type/domain/created,
             off-vocabulary type/domain/status/contact values
  WARNINGS - unresolved wikilinks, orphaned knowledge notes, stray '- [ ]'
             checkboxes outside task notes, leftover '- [[ ]]' placeholders
  INFO     - overdue open tasks

Exit code: 1 if any ERRORS, else 0. Templates/ and .obsidian/ are skipped.
"""
import argparse, datetime, pathlib, re, sys

TYPES = {"fleeting","daily","weekly","journal","project","area","business","government","meeting",
         "person","group","engagement","fund","transaction","source","book","chapter","research","concept","moc","task","finding","judgement"}
# Task statuses that take a task off the owner's plate: no overdue chasing, hidden
# from open views. `delegated-out` = someone else owns the work AND its supervision.
CLOSED_TASK_STATUS = ("done", "cancelled", "delegated-out")
STATUSES = {"idea","planning","active","on-hold","done","archived",
            "to-read","reading","not-started","in-progress","in-review","cancelled","needs-triage",
            "delegated-out",
            "lead","talking","proposal","lost","settled","outstanding",
            "current","superseded","draft"}
DOMAINS = {"work","personal","shared"}
# person `contact:` — omitted means active, so the empty case is never an error
CONTACTS = {"active","dormant","none"}
# Orphan check exempts entity/dashboard-first and periodic types
# (chapter: reached via the book's `book == this` base view + the book backlink;
#  judgement: deliberately unlinked - an inbound link is a signpost to a note that must
#  not be found while writing for anyone else, so being an orphan is its correct state):
ORPHAN_EXEMPT = {"task","moc","daily","weekly","fleeting","group","transaction","fund","chapter",
                 "judgement"}

def parse_frontmatter(text):
    """Return (dict, error). Minimal line parser; PyYAML pass adds strictness."""
    m = re.match(r"^---\r?\n(.*?)\r?\n---(\r?\n|$)", text, re.S)
    if not m:
        return None, "no frontmatter block"
    raw = m.group(1)
    err = None
    try:
        import yaml
        try:
            data = yaml.safe_load(raw)
            if not isinstance(data, dict):
                return None, "frontmatter is not a mapping"
            return data, None
        except Exception as e:
            return None, f"YAML parse error: {str(e).splitlines()[0]}"
    except ImportError:
        pass  # fall back to the minimal parser below
    data = {}
    for line in raw.splitlines():
        km = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if km:
            v = km.group(2).strip().strip('"').strip("'")
            data[km.group(1)] = v
    return data, err

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vault")
    ap.add_argument("--extra-types", default="")
    ap.add_argument("--extra-statuses", default="")
    a = ap.parse_args()
    V = pathlib.Path(a.vault)
    if not V.is_dir():
        print(f"ERROR: not a directory: {V}"); sys.exit(1)
    # the vault registers its own words on two lines of its CLAUDE.md; read them, so a note written
    # correctly with a registered type is not reported as an error unless someone passes a flag
    extra = {"extra-types": a.extra_types, "extra-statuses": a.extra_statuses}
    cm = V / "CLAUDE.md"
    if cm.is_file():
        ct = cm.read_text(encoding="utf-8", errors="replace")
        for key in extra:
            m = re.search(r"^%s:[ 	]*(.*)$" % key, ct, re.M)
            if m and m.group(1).strip():
                extra[key] = extra[key] + "," + m.group(1).strip()
    types = TYPES | {t.strip() for t in extra["extra-types"].split(",") if t.strip()}
    statuses = STATUSES | {s.strip() for s in extra["extra-statuses"].split(",") if s.strip()}

    notes = {}           # path -> (fm, text)
    errors, warns, info = [], [], []
    for p in sorted(V.rglob("*.md")):
        rel = p.relative_to(V)
        if rel.parts[0] in (".obsidian", "Templates") or ".trash" in rel.parts:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        # Convention files live at the vault root and are not notes: CLAUDE.md (the owner's)
        # and any organisation layer beside it (ACME.md, TEAM.md - see SKILL.md rule 2a).
        # No note belongs at the root, so depth is the test rather than a list of names.
        # They are documentation, and their prose carries illustrative `[[wikilinks]]` that
        # are examples rather than references - so they are skipped entirely, not stored.
        if len(rel.parts) == 1:
            continue
        # A README explains a folder to a person. It is documentation sitting inside the
        # vault, not a note, and requiring frontmatter on it only teaches people to fake one.
        if p.name == "README.md":
            continue
        fm, err = parse_frontmatter(text)
        if err or fm is None:
            errors.append(f"{rel}: {err}"); notes[p] = ({}, text); continue
        notes[p] = (fm, text)
        for req in ("type","domain","created"):
            if req not in fm or fm.get(req) in (None,""):
                errors.append(f"{rel}: missing required `{req}`")
        t = fm.get("type")
        if isinstance(t,str) and t and t not in types:
            errors.append(f"{rel}: off-vocabulary type `{t}`")
        d = fm.get("domain")
        if isinstance(d,str) and d and d not in DOMAINS:
            errors.append(f"{rel}: off-vocabulary domain `{d}`")
        s = fm.get("status")
        if isinstance(s,str) and s and s not in statuses:
            errors.append(f"{rel}: off-vocabulary status `{s}`")
        # a finding is a quantity of some population. These two signals were measured on a
        # 70-finding vault before being added: each hit mostly notes that belonged elsewhere
        # (a fact about a source, a lesson). Warnings, because a small base can be real.
        if t == "finding":
            b = str(fm.get("base_n", "")).replace(",", "").strip()
            try: small = float(b) <= 1
            except ValueError: small = True
            if small:
                warns.append(f"{rel}: finding with base_n `{fm.get('base_n')}` - a figure about a population needs a base; a fact about a source or a lesson?")
            # "why" is an explanation; "how" is one too unless a quantity follows it
            # ("how much", "how often" are measures). "whether" was tried and dropped:
            # on a real vault it hit a correct significance test.
            m = str(fm.get("measure", "")).strip().lower()
            if m.startswith("why ") or (m.startswith("how ") and
                    m.split()[1:2] not in (["much"], ["many"], ["often"], ["far"], ["large"], ["long"], ["big"])):
                warns.append(f"{rel}: finding measure starts with '{m.split()[0]}' - an explanation, not a quantity; a source note or a lesson?")
        c = fm.get("contact")
        if isinstance(c,str) and c and c not in CONTACTS:
            errors.append(f"{rel}: off-vocabulary contact `{c}` (use active | dormant | none, or omit)")

    # link resolution: targets = ALL md basenames in the vault (incl. Templates/,
    # which are skipped from validation but are still legitimate link targets)
    md_names = {q.stem for q in V.rglob("*.md")
                if ".obsidian" not in q.parts and ".trash" not in q.parts}
    all_files = {q.name for q in V.rglob("*") if q.is_file()}
    inbound = {p: 0 for p in notes}
    stem_to_path = {p.stem: p for p in notes}
    unresolved = {}
    for p,(fm,text) in notes.items():
        rel = p.relative_to(V)
        body = re.sub(r"```.*?```", "", text, flags=re.S)  # ignore code blocks
        for target in re.findall(r"!?\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]", body):
            target = target.strip()
            if not target: continue
            if "." in target and target in all_files:      # embed with extension
                continue
            if target in md_names:
                tp = stem_to_path.get(target)
                if tp is not None and tp != p: inbound[tp] += 1
            elif p.name != "CLAUDE.md":
                unresolved.setdefault(target, []).append(str(rel))
        # transaction sanity (money module)
        if fm.get("type") == "transaction":
            amt = str(fm.get("amount","")).replace(",","").strip()
            try:
                if float(amt) <= 0: errors.append(f"{rel}: transaction amount must be a positive number (got `{fm.get('amount')}`)")
            except (TypeError, ValueError):
                errors.append(f"{rel}: transaction amount must be a positive number (got `{fm.get('amount')}`)")
            if str(fm.get("direction")) not in ("in","out"):
                errors.append(f"{rel}: transaction direction must be `in` or `out` (got `{fm.get('direction')}`)")
            if not fm.get("fund"):
                warns.append(f"{rel}: transaction has no `fund:` link")
        # chapter sanity (book system): a chapter is meaningless without its book
        if fm.get("type") == "chapter" and not fm.get("book"):
            errors.append(f"{rel}: chapter note missing required `book:` link")
        # stray checkboxes (non-task notes; CLAUDE.md is config, not a note)
        if fm.get("type") != "task" and p.name != "CLAUDE.md":
            n_cb = len(re.findall(r"(?m)^\s*- \[ \] ", body))
            if n_cb: warns.append(f"{rel}: {n_cb} stray `- [ ]` checkbox(es) — promote to task notes?")
        # placeholders
        if p.name != "CLAUDE.md":
            n_ph = len(re.findall(r"(?m)^\s*- \[\[ ?\]\]\s*$", body))
            if n_ph: warns.append(f"{rel}: {n_ph} unfilled `- [[ ]]` placeholder(s)")
        # delegated-out integrity: the status hides the task from every open view and
        # from overdue chasing, so the record itself has to hold up. These are checks on
        # the note, NOT a prompt to chase the delegate — nothing here asks the owner to
        # follow up (that is the whole point of the status).
        if fm.get("type") == "task" and str(fm.get("status")) == "delegated-out":
            who = fm.get("assignee")
            if not (who if isinstance(who, list) else [who] if who else []):
                warns.append(f"{rel}: delegated-out with no `assignee:` — nobody is recorded as owning it")
            if str(fm.get("recurrence") or "").strip():
                warns.append(f"{rel}: delegated-out but `recurrence:` is still set — the repeat is dead, hand it over or clear it")
        # overdue
        if fm.get("type") == "task" and str(fm.get("status")) not in CLOSED_TASK_STATUS:
            due = str(fm.get("due") or "").strip()
            if re.match(r"^\d{4}-\d{2}-\d{2}$", due) and due < datetime.date.today().isoformat():
                info.append(f"{rel}: overdue since {due}")
    for target, srcs in sorted(unresolved.items()):
        warns.append(f"unresolved link [[{target}]] in: {', '.join(sorted(set(srcs))[:4])}{'…' if len(set(srcs))>4 else ''}")
    for p,(fm,_) in notes.items():
        if p.name == "CLAUDE.md" or fm.get("type") in ORPHAN_EXEMPT: continue
        if inbound.get(p,0) == 0:
            warns.append(f"{p.relative_to(V)}: orphan (no inbound links)")

    print(f"Scanned {len(notes)} notes in {V.name}/")
    for label, items in (("ERRORS",errors),("WARNINGS",warns),("INFO (overdue)",info)):
        print(f"\n{label}: {len(items)}")
        for x in items: print(f"  - {x}")
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
