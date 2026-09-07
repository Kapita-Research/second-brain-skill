# KAPITA Research — vault conventions

> ## ⛔ The firm is `KAPITA Research`, in full. It is never shortened.
>
> **`KAPITA` on its own names the older parent company** — *a different entity, still trading as KAPITA
> Business Hub, with 11,187 followers to this firm's 1,270.* **It is not an abbreviation of this name;
> it is somebody else's.**
>
> ⛔ **Never on a cover, a title, a report header, a deck, a signature, a proposal, or anything a client
> sees** — **and never in a sentence that means this firm.**
>
> ✅ **Legitimately bare:** `KAPITA Business` and `KAPITA Business Hub` (the parent) · `KAPITA Tech`
> (the dissolved division) · `KAPITA.md` (this file) · `kapita.iq` · **and a span of years crossing
> November 2025** — *anyone who was here before then was at the parent, and their tenure is correct as
> written.*

> ## ⛔ This file is the firm's. Do not edit it.
>
> **It goes at your vault root as `KAPITA.md`, and it is replaced whole on every update** — anything you
> add here is lost the next time, silently. **That is the point: fifteen vaults read the same words.**
>
> **Your own conventions go in `CLAUDE.md`, beside it.** How you like things worded, your own folders,
> your languages, what you are working on. **Nobody replaces that file, ever.**
>
> **Where the two disagree:** this file governs shared vocabulary and sharing rules; **`CLAUDE.md`
> governs everything about how you work.**


> **This file sits at the root of your vault. The skill reads it on every run and it overrides the
> skill's own defaults** — which is why everything KAPITA-specific lives here, in one file, and nothing
> about the company is in the skill itself.

> ⚠️ **Because it overrides, a word here that disagrees with the skill wins — silently.** Every type
> name, folder name and field name below is checked against the skill by
> `tools/check-kapita-layer.py` before this file is distributed. **If you edit it, run that.**

---

## 1. Who you are

Set this once, at the top of your daily note or in a file called `Me.md`:

```yaml
---
type: person
domain: work
created: 2026-08-31
email: your.name@kapita.iq
---
```

**Your email is your identity everywhere in this system.** Not your name — names are spelled several
ways and change; the address does not. **When the company system reads your shared folder later, the
email is what joins your notes to you.**

> **Nothing here is a security check, and it is not meant to be one.** It is configuration. Real
> identity comes from Google when a file reaches the shared Drive, and from OAuth when the company
> system exists. **Neither can be edited away in a text file, and this can.**

---

## 2. ⛔ Nothing this firm publishes may read as machine-written

**The rule everyone forgets, so it sits before everything else.**

⛔ **No em-dash `—`, no en-dash `–`.** A comma, a full stop, a colon or brackets instead.
⛔ **No arrows `→`, no middle dots `·`, no decorative bullets, no emoji marking sections, no
checkmarks in tables.** None of the furniture that now signals a machine wrote the page.

> **KAPITA Research sells credibility.** A client who reads a paragraph and thinks *"this was
> generated"* stops weighing the finding and starts weighing whether anybody checked it.
> **The punctuation costs nothing to fix. The doubt costs the engagement.**

**Everything a person outside your vault reads:** a report, a brief, a deck, a dashboard label, a post,
an email, a proposal, a methodology note, an article. **Arabic and English alike.**

⚠️ **Not these notes.** *Your vault is a working record and its markers earn their place.*
⛔ **The line is the vault's edge ─ the moment text leaves, the furniture comes off.**

### And it has to be readable where the writing actually happens

⛔ **This file is only read when the vault is.** *A deck built in another folder, a post drafted
through somebody's own writing skill, an email written in a code project — none of them open it*, which
is exactly where the rule was being lost.

**So the short form below is installed into `~/.claude/CLAUDE.md`**, which is read at the start of every
conversation in every folder, and **refreshed from here on every update**. ⛔ **Edit it here and nowhere
else** — the copy is generated, and anything written into the copy is overwritten without a message.

```markdown
## Nothing KAPITA Research publishes may read as machine-written

No em-dash or en-dash: a comma, a full stop, a colon or brackets instead. No arrows, no middle dots, no
decorative bullets, no emoji marking sections, no checkmarks in tables. None of the furniture that now
signals a machine wrote the page. Arabic and English alike.

This covers everything a person outside my vault reads: a report, a brief, a deck, a dashboard label, a
post, an email, a proposal, an article. It does not cover my own notes, which are a working record.

The firm sells credibility, and a client who reads a paragraph and thinks "this was generated" stops
weighing the finding and starts weighing whether anybody checked it.
```

---

## 3. Sharing

**`Outbox/` is the staging folder, and it syncs to KAPITA Research's Drive.**

**A note in `Outbox/` is a note you have decided belongs to the firm.** Nothing else about it changes —
same Markdown, same frontmatter. When the firm-wide system is built, **it reads `Outbox/` and nothing
else**, so no one ever has to go back through months of notes and sort them.

**Do the sorting once, when you write the note and already know the answer.**

| | |
|---|---|
| ⛔ **`domain: personal` never enters `Outbox/`** | Refuse it in the path, not by judgement |
| ⛔ **Nothing moves there on Claude's initiative** | Even when it is obviously work. **You decide what colleagues see, every time** |
| ✅ **What moves** | Meeting notes · decisions · findings · anything about a client, a project, or the firm's own work |

---

## 4. The people

⛔ **Do not copy these in.** A vault that opens with fifteen people nobody has mentioned yet is
fifteen files in the way.

📐 **This table is a lookup, not a list to install.** **The first time a colleague comes up in
conversation, their note gets written then** — one note in `People/`, using the name and aliases below,
so it is written the same way here as in everyone else's vault.

> **That is where the duplicate is actually prevented: at the moment of creation, whether that is today
> or in three months.** Copying them in on day one adds nothing but clutter.

**People join and leave.** This is who is on record today, **not who is allowed to be in the vault.**
Anyone else — a client contact, a supplier, a candidate — gets a note the same way, and the same
conventions apply.

```yaml
---
type: person
domain: personal          # ⛔ always — a person is someone you know, whatever context introduced you
created: 2026-08-31
email: essam@kapita.iq
job_title: Senior Market Researcher
company: "[[KAPITA Research]]"
aliases: [Essam Munir, Essam, عصام منير, عصام]
---
```

### The roster — facts only

⛔ **Nothing here is an assessment of anybody.** Name, the Arabic spelling, address, and role — **what the skill needs to write to somebody and to spell them right.** **Judgements
about colleagues are a different type in a different folder and never go in this file.**

> ⚠️ **Degrees are deliberately not here.** *Nothing the skill does needs them*, and a single file
> listing everybody's university and years, copied to fifteen machines, is a compiled record nobody
> agreed to. **What you know about a colleague belongs in their note in your own vault**, which is
> where it already is. **The one exception is below**, because it prevents a wrong name rather than
> describing a person.

| Name · العربية | Email | Role |
|---|---|---|
| **Mohammed Jamal** · محمد جمال | `m.jamal@kapita.iq` | **CEO** — from the parent company before the split, and **the approver for access to closed projects** |
| **Essam Munir** · عصام منير | `essam@kapita.iq` | Senior Market Researcher |
| **Moamin Al-Kakaei** · مؤمن الككائي | `moamin@kapita.iq` | Senior Market Researcher |
| **Yousif Ahmed** · يوسف أحمد | `yousif.ahmed@kapita.iq` | Market Researcher — **called "Dr. Yousif"** |
| **Yousif Al-Shaikhli** · يوسف الشيخلي | `yousif.alshaikhali@kapita.iq` | Data Analyst & Technology Officer |
| **Murtadha Najem** · مرتضى نجم | `murtadha.najem@kapita.iq` | Data Engineer & Market Researcher |
| **Mohammed Mustafa** · محمد مصطفى عمران | `m.mustafa@kapita.iq` | Internal Development Consultant |
| **Mohammed Hayder** · محمد حيدر | `m.hayder@kapita.iq` | Field Researcher |
| **Ammar Jalel** · عمار جليل | `ammar.jalel@kapita.iq` | **Creative Lead** — has designed the firm's reports and magazines since 2023 |
| **Aya Salam** · آية سلام | `aya.salam@kapita.iq` | Business Development Lead — **from the parent company, before the split** |
| **Athar Hakeem** · آثار حكيم | `athar.hakeem@kapita.iq` | Project Coordinator — **began in aviation as an Airworthiness Planning Engineer** |
| **Fatima Suhail** · فاطمة سهيل | `fatima.suhail@kapita.iq` | Marketing Executive — **an urban-planning engineer** |
| **Ameer Loay** · أمير لؤي | `ameer.loay@kapita.iq` | **Field Operations Supervisor** — promoted through the field ladder here: Junior Research Analyst → Field Researcher → Supervisor |
| **Assim Anas** · عاصم أنس | `assim.anas@kapita.iq` | Market Researcher |
| **Fatimah Oday** · فاطمة عدي | `fatimah.oday@kapita.iq` | Junior Market Researcher |
| **Mafaz Al-Kubaisi** · مفاز الكبيسي | — | **Research Intern** |
| **Payam Sherzad** · بيام شيرزاد | — | **Political Analyst & Field Researcher** — Iraq, the KRI and Iran · multilingual |
| **Ali Al-Saedi** · علي الساعدي | — | not published |

**Two things a newcomer gets wrong, so they are stated:**

⛔ **"The doctor" identifies nobody here.** **Five people hold a medical degree** — Mohammed Jamal,
Essam Munir, Yousif Ahmed, Mohammed Hayder, Ammar Jalel — **and only Essam Munir still practises.**

⛔ **"Yousif" is two people**, and they do different jobs: **Yousif Ahmed** (Market Researcher, *"Dr.
Yousif"*) and **Yousif Al-Shaikhli** (Data Analyst & Technology Officer). **Never resolve a bare
"Yousif" without asking which.**

⚠️ **Where a line says *not published*, that is what it means — the person has one, it is simply not on
record here.** ⛔ **Do not fill a gap with a guess.**

### Aliases — a short list, for Obsidian's benefit

**Claude does not need these.** It knows `عصام` is Essam, `آيه` is `آية`, `Najim` is `Najem` — and it
generates variants better than any list. **These exist because `[[آيه]]` opens the right note in
Obsidian only if that exact string is written down.**

**So: two or three real forms per person, and stop.** The list is **not a spelling authority** and does
not need to be complete.

```yaml
Mohammed Jamal:     [محمد جمال, جمال, MJ]
Essam Munir:        [عصام منير, عصام]
Moamin Al-Kakaei:   [مؤمن الككائي, مؤمن]
Yousif Ahmed:       [يوسف أحمد, د. يوسف, Dr. Yousif]
Yousif Al-Shaikhli: [يوسف الشيخلي, الشيخلي]
Murtadha Najem:     [مرتضى نجم, مرتضى]
Mohammed Mustafa:   [محمد مصطفى, محمد عمران, مصطفى, عمران, M. Mustafa Imran]
Mohammed Hayder:    [محمد حيدر]
Fatima Suhail:      [فاطمة سهيل]
Fatimah Oday:       [فاطمة عدي]
Aya Salam:          [آية سلام, آية]
Ameer Loay:         [أمير لؤي, أمير]
Athar Hakeem:       [آثار حكيم, آثار]
Assim Anas:         [عاصم أنس, عاصم]
Ammar Jalel:        [عمار جليل, عمار]
```

### 🔴 What actually needs writing down — because it cannot be worked out from a name

**Two people are called Yousif.** `Yousif Ahmed` is **"Dr. Yousif"** — a market researcher with an MD.
`Yousif Al-Shaikhli` is the **Data Analyst & Technology Officer**. **When a note says only "Yousif",
ask.**

**Three people are called Mohammed** — Jamal, Mustafa and Hayder. **So `محمد` and `Mohammed` are on
nobody's alias list**: a shared name registered on one person creates no ambiguity anyone can catch —
**it resolves cleanly and silently to the wrong one.**

**Mohammed Mustafa's full name is محمد مصطفى عمران** — `محمد مصطفى` a compound given name, `عمران` his
father's. He is called any of `مصطفى`, `محمد عمران`, `عمران`, and signs as **M. Mustafa Imran**.

**And the sources you already hold disagree with themselves:** the website writes *Najim* where the
email says *najem*, and *Al-Shaikhli* where his address says *alshaikhali*. **Worth knowing; not worth
cataloguing.**

### Naming — English filenames, every other spelling in `aliases`

**The file is named in English. You write in whatever language you like.**

```yaml
# Uruk Technology.md
aliases: [أوروك, أوروك للتقنية, Uruk, اوروك]
```

`[[أوروك]]` resolves through the alias. **The convention decides what the *file* is called, nothing
else** — a filename travels through sync, links and whatever reads the vault later, so it stays in one
script.

> 🔴 **This is not a preference.** *Search before you create* — the rule that prevents duplicates —
> works inside one script and breaks across two. Someone searching `Uruk` does not find `أوروك.md`, and
> **creates a second note while following the rule correctly.** One client, two records, half the
> history in each.

---

## 5. Clients — twelve to start with, and the list is open

⛔ **Do not copy these in either.** **Same rule as the people above: a lookup, not an installation.**

**When a client first comes up, write the note then** — a `type: business` note in `Work/Business/`,
with the name and aliases below. **Twelve empty client notes on day one help nobody**; one written
correctly the moment it is needed prevents the duplicate that matters.

> ⚠️ **A starting set, not a closed list.** **New clients are the normal course of business here.**
> **Nothing on this list restricts anyone**, and no capture should ever be refused, delayed or
> questioned because a client is not on it. A new client gets a note the same way — English filename,
> every spelling in `aliases`, transliterated rather than translated.

| Client | A couple of forms for Obsidian |
|---|---|
| **UN-Habitat** | `[UN-Habitat, الأمم المتحدة - الموئل]` |
| **Uruk** | `[Uruk, أوروك]` |
| **JICA** | `[JICA, جايكا]` |
| **IREX** | `[IREX, ايركس]` |
| **GIZ** | `[GIZ, جي آي زد]` |
| **IDB** | `[IDB, Iraq Development Bank, مصرف العراق للتنمية]` |
| **Zain Iraq** | `[Zain Iraq, زين]` |
| **Tahoonat Al-Rabee** | `[Tahoonat Al-Rabee, طاحونة الربيع]` — **transliterated, not translated** |
| **Ridah Alwan** | `[Ridah Alwan, رضا علوان]` |
| **Fastlink** | `[Fastlink, فاست لينك]` |
| **Power China Glass** | `[Power China Glass, باور تشاينا]` |
| **Sardar** | `[Sardar, سردار]` |

> **Two forms each is enough.** Claude resolves the rest; these exist so `[[أوروك]]` opens the right
> note in Obsidian.

**Transliterate, never translate.** An entity with no official English name gets its Arabic name written
in Latin letters — **طاحونة الربيع becomes `Tahoonat Al-Rabee`, not "Rabee Mill".** A translated name is
one **you invented**: it appears on no contract, no invoice and no email, so nobody else searching will
ever type it. **Put every transliteration people actually use into `aliases`.**

> 🔴 **Notion's `Client Name` field mixes three different things**, and the owner had to strip three
> entries from it by hand: **`FMCG`** (a sector), **`Paper Bags`** and **`New Frontiers`** (not clients).
> **Three more carry a project name welded to the client** — `IREX - Monitoring & Evaluation`,
> `GIZ - ICCA Anbar`, `HR - Sardar`. **Here the client is the client and the project is a separate
> note**, which is the distinction that field never made.

---

## 6. What KAPITA Research writes down

**The types that carry a promise here, beyond the skill's defaults:**

| `type` | Use it for |
|---|---|
| `meeting` | Any client or internal meeting. `people` and `date` required |
| `project` | A client engagement. Carries `client` and `status` |
| `business` | A client, a partner, a competitor. *(A ministry or state body is `government`.)* |
| `finding` | **A number from our own research.** All fields required — see `references/findings.md` |

**Everything else is free.** `type: lecture`, `type: training`, `type: instrument`, `type: proposal` —
write it and it exists.

**`type: nda` is one of those free types, with a convention rather than a promise:** carry `client`,
`signed` and `expires` on it. ⚠️ **Nothing in your vault acts on `expires`** — the clock that reopens a
closed project belongs to the firm-wide system, not here. **Write it so the information exists when
that system does.**

### ⛔ Task statuses are the skill's, not Notion's

**Read the current values from `references/properties-and-tags.md` in the skill — they are not listed
here, deliberately.**

> 🔴 **This file overrides the skill.** A list written here is right on the day it is written and
> becomes a **cap** the day the skill gains a value — which is then **rejected silently, by a file we
> wrote.** *Four times now the layer has quietly out-voted the skill; a frozen vocabulary is the easiest
> way to make it a fifth.*

**Notion's eight "categories" are not statuses at all.** *Instrument Design*, *Data Collection*,
*Reporting* describe **where a project has got to**, not whether a task is being worked on. **Two
different axes, and Notion keeps them in one field** — which is part of why it stopped being trusted.

**If project phases are wanted here, they are a *new field* on the project note** — `phase:`, with its
own values. **An addition, which is free. Not a redefinition of `status`, which is not.**

⚠️ **And there is no single vocabulary to copy even if we wanted one:** Notion holds **two** phase
lists — a five-value `Current Phase` and an eight-value set on its buttons and task categories — and
*"Phase 3"* means something different in each. **The words that end up mattering here will come from a
month of use, not from a system being replaced.**

---

### The vocabulary this vault has invented

**Not here — in your own `CLAUDE.md`**, on its `extra-types:` / `extra-statuses:` lines. **What one
vault invents is that vault's, and this file is everyone's.**

---

## 7. Findings — the one thing KAPITA Research cannot be loose about

**We sell numbers.** A figure quoted without its base size or its caveat is the product being wrong,
and it is the only failure this firm treats as fatal.

**So `type: finding` is not optional here, and every field is required.** The traps, restated because
they are the two that actually happen:

> **`base_n` is not `sample_n`.** A figure computed on 340 people inside a study of 1,200 has a base of
> **340**. Quoting the study's sample as the base overstates the precision of every number in it.

> **`collected` is not `describes`.** Fieldwork in March 2025 describing 2024 is **not a 2025 figure**.

**Write the finding at tabulation, not at review.** The base, the exclusions, the weighting and the
fieldwork dates are on screen and certain — about ninety seconds. Three weeks later the same record
costs fifteen minutes of recall, and some of it is a guess.

🔴 **So a vault set up at this firm includes the findings module from the first day** — the scaffold
leaves it out by default, and a folder that does not exist is a habit that never starts. **Say so when
you set one up:** *"set up my vault, with findings"*.

**And when you quote one back, quote it whole** — the number, its base, its dates and its caveat, in
one sentence. **Never the number alone, however short the question was.**

---

## 8. What this file does not do

**It does not check who you are, and it cannot.** Anyone can edit it. **Nothing in this file is a
permission, and nothing here decides what you may see** — that is Drive's job today, and the company
system's job later.

**It is a set of conventions, agreed once, so that fifteen vaults can be read as one archive when the
time comes.**

---

## 9. Updates — where a release comes from, and how to take one

**The skill keeps changing.** Fixes, new rules, a corrected figure in this file. **This section is the
authority for how that reaches your machine** (`cli-and-automation.md` → *Staying current* explains why
it works this way).

### The channel

| | |
|---|---|
| **The shared Drive folder** | **`KAPITA Second Brain`.** It holds `latest.json` (which release is current, and the archive's hash) and the archive itself |
| **With Google Drive for desktop** | it is a local path, usually `G:\My Drive\KAPITA Second Brain`. **A check costs one file read, needs no network, and works offline** |
| **Without it** | open <https://drive.google.com/drive/folders/1D79209rP34Gay9C7LOicFbbpVYcOxOdz>, download the newest `second-brain-<version>.zip`, unpack it, and install from there. ✅ **Byte-identical result** |
| **The repository** | `github.com/Kapita-Research/second-brain-skill`, **private and for whoever maintains the skill.** ⛔ Nobody else needs an account, and the update path never touches it |

### The three commands, and nothing else

```bash
python "<the shared folder>/install.py" --check   # is there a newer one? Silent when there is not
python "<the shared folder>/install.py"           # a machine with nothing: the whole install
python "<unpacked release>/tools/update.py"       # a machine that already has it: just the update
```

### How it behaves here

**A scheduled routine runs the check once a day.** ⛔ **When nothing changed it says nothing at all.**
When something did, it sends one message: the two version numbers, two or three lines from the top of
the skill's `CHANGELOG.md`, and *"say **update the second brain** whenever it suits you."*

🔴 **Nothing installs by itself, and that is mechanical rather than polite.** *A skill replaced while a
conversation is open is not re-read by that conversation.* **The update takes seconds, nothing is
unavailable meanwhile, and it takes effect in the next conversation.**

### What it does to your vault

| | |
|---|---|
| `KAPITA.md` | **replaced whole**, with your previous copy kept as `KAPITA.md.bak` |
| **Templates, dashboards, property types** | **added to, never overwritten** |
| ✅ **Your `CLAUDE.md` and every note you have written** | **never touched** |

⛔ **So nothing personal goes in this file** — it is replaced on the next update and whatever was added
disappears without a message.

### When it does not work

**Say *"run the second brain install check"* in a new conversation.** Every failing line prints the one
thing to do about it. ⚠️ **Run it after an update too**, not only when something feels wrong.

---

## 10. Obsidian

**Install it.** It is free, it opens your vault folder without changing anything, and at KAPITA Research it pays
for itself on one feature: **open a client and see every note that mentions them, with nobody
maintaining that list.**

**Three things are worth setting up on day one:**

| | |
|---|---|
| **Fill `aliases` from §3** | then `[[عصام]]` and `[[Essam]]` and a misspelling all open the same note |
| **A base over `type: task`, grouped by `status`** | that is your board — **and unlike Notion it is built from fields you already write, so it cannot go stale separately** |
| **A base over `type: finding`** | every number the firm holds, with its base size and caveat visible in the table |

> **And the thing Notion got wrong that this gets right:** there is no second place to update. **The
> board *is* the notes.** A task is done when its note says so — there is no checkbox somewhere else
> that also has to be ticked.

**If you do not install it, nothing breaks** — ask Claude instead. You lose the panels, not the data.
