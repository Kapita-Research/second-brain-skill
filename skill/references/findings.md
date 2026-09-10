# Findings — numbers that carry their own conditions (optional module)

**For anyone who quotes figures from their own or others' research** — a researcher, an analyst, a
journalist, a student. **Off unless the owner asks for it.**

> ### What is not a finding, even with a number in it
> **A finding is a quantity of some population that someone could quote to a reader.** *The number is
> the claim.* **If the note would still say something with the number removed, or its subject is a
> document, a dataset, a tool, a site or your own pipeline and says how it behaves, it is not a finding**:
> a fact about a source
> goes in that source's note, a lesson is a concept, and whatever is still undone is a task. *"12 of 12
> pages loaded from Windows and 0 of 12 from Ubuntu" is a diagnosis; "41% of 812 households have no
> piped water" is a finding, and so is *"the model scored 0.91 on 522 held-out images"*: a score on a
> set of cases is a quantity of that set. ⚠️ **Filling the required fields does not make a note a finding.** A
> `base_n` of 1, or a `measure` that starts with *why* or *how*, is the form being filled for a note
> that belongs somewhere else.

> **A number without its conditions is not reusable. It is a rumour with a decimal point.**

A `62%` sitting in a report is a fact **only while you remember what it was 62% *of*, who it described,
when it was measured, and what the person who produced it warned you about. That memory lasts weeks.
The figure gets quoted for years.**

---

## The whole-number rule — this module's Golden Rule

> ## **A finding is quoted whole, or not at all.**

**Every time a finding is returned — in an answer, a draft, an export, a chat reply — it goes out as one
statement carrying its value, its base, its dates and its caveat.** However short the question was.

| | |
|---|---|
| ⛔ | *"62%."* |
| ⛔ | *"62% of car owners prefer Toyota."* |
| ✅ | *"62% of Baghdad car owners aged 18+ preferred Toyota (base 340; fieldwork March 2025, describing 2024). Not to be reported below governorate level; 62% response rate."* |

**The reason it is a rule and not a preference:** the short form is *correct* and still causes the
damage. Someone reads *"62% prefer Toyota"*, uses it for a national figure, and nothing in the sentence
told them they could not.

---

## The two traps that actually happen

> 🔴 **`base_n` is not `sample_n`.** A figure computed on the 340 people who owned a car, inside a study
> with an achieved sample of 1,200, has a base of **340**. **Quoting the study's sample as the base
> overstates the precision of every number drawn from it** — and it is the single commonest way a
> research number is misused.

> 🔴 **`collected` is not `describes`.** Fieldwork run in March 2025 asking about the previous year
> produces a **2024** figure, not a 2025 one. Two dates, two different questions, and conflating them
> silently ages or freshens the number by a year.

---

## Comparability — when two findings may be combined

**Only when *what* was measured, *who* it describes, and the *unit* all match.**

**Otherwise, do not average, do not sum, and do not present them as a trend.** List them side by side
and **show the difference that stops them combining:**

> *"Baghdad 2024 (base 340) and Basra 2022 (base 210) are not comparable — different governorates, two
> years apart, and the 2022 study covered all adults rather than car owners."*

**This is a refusal that helps.** The alternative — a quiet average of two incomparable numbers — is
wrong in a way nobody can see afterwards.

---

## Incomplete findings are drafts

**A finding missing any required field is `status: draft` and is never quoted.** The note still exists,
still searches, still links — **only the quoting stops.**

> **Nobody is blocked from writing anything.** What is blocked is a number leaving without its
> conditions, which is the only failure this module exists to prevent.

**Write the finding when the numbers are in front of you** — at tabulation, at the moment of reading the
source. **Base, exclusions and dates are certain then and take a minute. Three weeks later the same
record costs fifteen and some of it is a guess.**

---

## Superseding — never overwrite a number

**A finding that has been cited somewhere must not change under the citation.** When a figure is
revised:

1. The old note stays, with `status: superseded` and `superseded_by: "[[New Finding]]"`.
2. The new note is written fresh, with its own base and dates.

> **Deleting or editing the old number in place breaks every reference to it silently** — the reader
> sees a different figure and has no way to know it moved.

---

## Where findings live

**`Findings/`** — one note per figure, filename a short human label (*"Toyota preference — Baghdad
owners"*), **the full statement as the first line of the body.**

**The number lives inside a sentence, never alone in a field.** That is deliberate: a value in its own
property invites being read out on its own, and **the whole point is that it cannot travel without its
conditions.**

**`source:` links the study, project or document it came from** — so the finding is always one click
from its method.

**Schema and template:** `note-types.md` → *Finding*. **Dashboard:** `Findings.base`.
