#!/usr/bin/env python3
"""Crawl from a seed URL, clean every page to disk, and print a manifest instead of the pages.

**The point is token economy.** A naive crawl pulls each page into the context window as raw HTML -
nav, cookie banner, footer, scripts - and pays for all of it whether the page turned out to matter or
not. Twenty pages can cost a hundred thousand tokens to learn that three were relevant.

This fetches, strips each page to readable text, **writes it to a file**, and prints one line per page:

    #  depth  words  links  title                              first words of the text
    1  0       1840     37  Sarah Chen - LinkedIn              Head of Research at Uruk Technology...

**Read the manifest, decide, then open only the files worth opening.** Thirty pages cost roughly five
hundred tokens to triage instead of tens of thousands to read.

    python scripts/crawl.py <url> [more urls] --depth 2 --max 40 --out <dir>

    --depth N     how many hops from the seeds (default 2; 0 = the seeds only)
    --max N       hard ceiling on pages fetched (default 40)
    --same-host   do not leave the seed hosts at all
    --out DIR     where the cleaned files and crawl.json go (default: ./crawl-<host>)

**Re-running is cheap and safe:** every fetched URL is recorded in `crawl.json`, so a second run with a
bigger `--depth` continues rather than starting over.

## What it does not do, and says so rather than hiding

⛔ **Stdlib only, so it fetches HTML - it does not run JavaScript.** A page whose content is rendered
client-side (most social platforms) comes back nearly empty; those are marked **`js`** in the manifest
and in `crawl.json`. **Open them another way, or record that you could not.**

⛔ **`robots.txt` is honoured.** A path it disallows is marked **`robots`** and not fetched - a boundary
someone set is a fact about the source, not an obstacle.

⚠️ **It sends no cookies, so anything behind a login comes back empty** - as `js` or a short error line.
**That is a capability limit, not a permission one:** a page the owner is logged into is theirs to read,
and the way to get it is a browser session, an export, or a paste - not this script. ⛔ **What must not
happen is a page you could not fetch reading as a page with nothing on it.**

**Cleaning:** uses `defuddle parse <url> --md` when it is on PATH (better output), otherwise a stdlib
tag-strip. Either way the result lands on disk, never in the conversation.
"""
import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser

UA = "Mozilla/5.0 (compatible; second-brain-crawl/1.0)"
DROP = re.compile(r"<(script|style|nav|footer|header|noscript|svg|form)[^>]*>.*?</\1>", re.S | re.I)
TAG = re.compile(r"<[^>]+>")
WS = re.compile(r"\n{3,}")
SKIP_EXT = (".pdf", ".zip", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".mp4", ".mp3", ".css", ".js")


def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        ctype = r.headers.get("Content-Type", "")
        if "html" not in ctype and "text" not in ctype:
            raise ValueError("not text: " + ctype.split(";")[0])
        return r.read(3_000_000).decode(r.headers.get_content_charset() or "utf-8", "replace")


def links_of(page, base):
    out = []
    for m in re.finditer(r'href\s*=\s*["\']([^"\'#]+)', page, re.I):
        u = urllib.parse.urljoin(base, html.unescape(m.group(1)).strip())
        p = urllib.parse.urlparse(u)
        if p.scheme in ("http", "https") and not p.path.lower().endswith(SKIP_EXT):
            out.append(urllib.parse.urldefrag(u)[0])
    seen, uniq = set(), []
    for u in out:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
    return uniq


def title_of(page):
    m = re.search(r"<title[^>]*>(.*?)</title>", page, re.S | re.I)
    return WS.sub(" ", html.unescape(m.group(1))).strip()[:90] if m else ""


def clean(url, page):
    """Defuddle if present - much better - else strip tags. Never returns HTML."""
    if shutil.which("defuddle"):
        try:
            r = subprocess.run(["defuddle", "parse", url, "--md"],
                               capture_output=True, text=True, timeout=60)
            if r.returncode == 0 and len(r.stdout.strip()) > 200:
                return r.stdout.strip()
        except (OSError, subprocess.SubprocessError):
            pass
    t = TAG.sub("\n", DROP.sub(" ", page))
    t = html.unescape(t)
    return WS.sub("\n\n", "\n".join(l.strip() for l in t.splitlines() if l.strip()))


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("urls", nargs="+")
    ap.add_argument("--depth", type=int, default=2)
    ap.add_argument("--max", type=int, default=40)
    ap.add_argument("--same-host", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--delay", type=float, default=0.7)
    a = ap.parse_args()

    seeds = [urllib.parse.urldefrag(u if "://" in u else "https://" + u)[0] for u in a.urls]
    hosts = {urllib.parse.urlparse(u).netloc for u in seeds}
    out = a.out or ("crawl-" + sorted(hosts)[0].replace(":", "_"))
    os.makedirs(out, exist_ok=True)

    ledger = os.path.join(out, "crawl.json")
    state = json.load(open(ledger, encoding="utf-8")) if os.path.exists(ledger) else {"pages": {}}
    pages = state["pages"]

    robots = {}

    def allowed(u):
        h = urllib.parse.urlparse(u).netloc
        if h not in robots:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(urllib.parse.urlunparse((urllib.parse.urlparse(u).scheme, h, "/robots.txt", "", "", "")))
            try:
                rp.read()
            except Exception:
                rp = None
            robots[h] = rp
        rp = robots[h]
        return True if rp is None else rp.can_fetch(UA, u)

    frontier = [(u, 0) for u in seeds]
    rows, n = [], 0

    while frontier and n < a.max:
        url, d = frontier.pop(0)
        if url in pages:
            continue
        if a.same_host and urllib.parse.urlparse(url).netloc not in hosts:
            continue
        if not allowed(url):
            pages[url] = {"depth": d, "status": "robots"}
            rows.append((d, 0, 0, "", url, "robots.txt disallows this path"))
            continue

        n += 1
        try:
            page = fetch(url)
        except Exception as e:                                   # noqa: BLE001 - report, never crash
            pages[url] = {"depth": d, "status": "error", "error": str(e)[:120]}
            rows.append((d, 0, 0, "", url, "could not fetch: " + str(e)[:60]))
            time.sleep(a.delay)
            continue

        text = clean(url, page)
        outs = links_of(page, url)
        words = len(text.split())
        # A JavaScript shell is a LARGE page that yields almost no text. A page that is simply
        # short is not the same thing, and calling it "gated" sends the reader looking for a
        # wall that is not there.
        status = "js" if (words < 120 and len(page) > 20000) else "ok"

        name = re.sub(r"[^A-Za-z0-9._-]+", "-", urllib.parse.urlparse(url).netloc +
                      urllib.parse.urlparse(url).path)[:80].strip("-") or "index"
        fp = os.path.join(out, "%03d-%s.md" % (n, name))
        with open(fp, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("<!-- %s -->\n\n" % url + text + "\n")

        pages[url] = {"depth": d, "status": status, "file": os.path.basename(fp),
                      "title": title_of(page), "words": words, "links": outs[:200]}
        rows.append((d, words, len(outs), title_of(page), url,
                     " ".join(text.split())[:110] if status == "ok"
                     else "%d KB of HTML, almost no text - rendered by JavaScript, or gated"
                          % (len(page) // 1024)))

        if d < a.depth:
            for u in outs:
                if u not in pages:
                    frontier.append((u, d + 1))
        time.sleep(a.delay)

    with open(ledger, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(state, fh, indent=1, ensure_ascii=False)

    print("crawled %d page(s) into %s/  -  read the files you want, not this output\n" % (n, out))
    print("%-3s %-5s %-6s %-5s %s" % ("#", "depth", "words", "links", "title / url / first words"))
    for i, (d, w, l, t, u, snip) in enumerate(rows, 1):
        print("%-3d %-5d %-6d %-5d %s" % (i, d, w, l, t or u))
        print("%23s %s" % ("", snip))
    gated = [u for u, p in pages.items() if p.get("status") in ("js", "robots", "error")]
    if gated:
        print("\n%d page(s) could not be read here (js / robots / error) - listed in crawl.json."
              % len(gated))
        print("Absence of text from these is not evidence that nothing is there.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
