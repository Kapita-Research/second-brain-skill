# Money — funds, transactions & debts (optional module)

A **relationship-aware ledger**, not accounting software: donations, project spending, informal debts, custody of other people's money. No double-entry, no bank sync — for audit-grade books use an ERP/spreadsheet (transaction notes export cleanly to xlsx on request).

## The model — two note types

**Fund** (`type: fund`, lives in `Money/`) — a wallet, account, or pot of money.
`owner:` (the org/person whose money it *is*), `custodian:` (who holds it), `currency:`, `status: active|archived`. The fund note is the landing page for its balances.

**Transaction** (`type: transaction`, lives in `Money/Transactions/`) — one money event.
`fund:`, `amount:` (positive number — never negative), `currency:`, `direction: in|out`, `txn: donation|expense|transfer|repayment|pledge|other`, `counterparty:` (`"[[Person/Org]]"` — omit for anonymous, note it in the body), `initiative:` (`"[[Project/Area/Engagement]]"` or `general`), `status: settled|outstanding|cancelled`, `related:`.
Filename: `YYYY-MM-DD <What> — <Counterparty>.md` (e.g. `2026-07-02 Donation — Sarah Chen.md`).

**No fund yet?** Create one on the spot: ask two things — whose money is it (`owner:`) and who holds it (`custodian:`) — take the currency from the amounts, then proceed with the capture.

## Semantics (memorize — everything follows from these five)

| direction + status | Meaning | Cash | Other effect |
|---|---|---|---|
| `in` + `settled` | money received | +amount | — |
| `out` + `settled` | spent/disbursed, closed | −amount | — |
| `out` + `outstanding` | disbursed, owed back | −amount | **receivable**: the counterparty owes the fund's **`owner`** (not the custodian) |
| `in` + `outstanding` | **pledge** — promised, not received | none | expected income |
| any + `cancelled` | **void** — never materialized (a written-off pledge, or an entry logged in error) | none | **excluded from ALL balance math** |

**Amounts are immutable history** — a transaction's `amount` is only ever changed by the split rule below; corrections that void an entry use `cancelled`, never deletion.

## Lifecycle procedures (follow exactly — the math depends on it)

- **Full repayment** of a receivable: new `in + settled` transaction, `txn: repayment`, `related:` the original; **flip the original to `settled`** (its amount unchanged). Cash rises by the repayment; the receivable disappears.
- **Partial repayment — the split rule.** William owes 5,000 and repays 3,000: (1) new `in + settled` repayment note for 3,000, `related:` the original; (2) **split the original** — reduce it to the outstanding remainder (2,000, still `out + outstanding`) **and** add an `out + settled` note for the repaid portion (3,000, `txn` matching the original, `related:` both ways, body: "settled portion of [[original]]"). Total outflow history stays 5,000; cash and receivable both compute correctly. Log the split in both bodies. *(Never just shrink the original — that silently overstates cash by the repaid amount.)*
- **Repayment field inheritance:** a repayment/split note inherits `fund`, `currency`, and `counterparty` from the original; date it the day the money moved.
- **Write-off, receivable** (debt forgiven — the money is still gone): flip the original to **`settled`** with a dated body note "written off"; cash stays down, receivable clears. Do **not** use `cancelled` (the disbursement really happened).
- **Write-off, pledge** (promised money isn't coming): set the pledge to **`cancelled`** with a dated body note; it leaves the pledge column and never touches cash.
- **Pledge fulfilled:** flip the pledge itself to `in + settled` (it becomes cash). Do **not** create a second note — that would double-count.
- **Entry logged in error:** `cancelled` + body note. Never delete — the audit trail stays.

## The balance verification rule (this module's Golden Rule)

After **every** money capture or edit: recompute and state the affected fund's position — **cash, receivables, pledges** (per the table; `cancelled` excluded), plus the earmarked initiative's net if relevant. Compute from the transaction notes' frontmatter (grep them, or the Ledger views' per-fund/initiative sums) — **never from memory or the previous chat turn**. If the user's stated number disagrees with the computed one, flag the discrepancy and ask — never silently adjust either side. **Balance questions follow the same rule:** compute fresh; several funds → report each fund, one line per currency, unless one fund is named.

## Capture patterns

- *"10 donations came in: 3 from X, Y, Z for initiative A; 5 for project B, one of them anonymous; 2 general purpose"* → 10 `in/settled/donation` transactions, earmarks set, counterparties resolved via aliases (Golden Rule 2), anonymous one gets no `counterparty` + a body note → restate fund position.
- *"Spent 3,000 on initiative A"* → `out/settled/expense`, `initiative:` linked → restate.
- *"Sent 5,000 to William"* → `out/outstanding/transfer`, counterparty `[[William]]` → William now owes the fund's `owner`; restate cash **and** receivables. Offer a follow-up task (`Collect repayment — William`, `due:` if known) per Golden Rule 7.
- Money inside a compound capture (a meeting recap that mentions a payment): the transaction note is created **in addition to** the meeting/task notes — see *Compound captures* in SKILL.md's triage section.
- Earmark unclear → ask one question, or file as `general` and flag. Which fund? One fund → assume it; several → ask once, remember for the session; none → create one (above).

## Money vs engagements (the seam)

An **engagement** tracks a *relationship/deal state*; a **transaction** records *money moving*. "The client paid the invoice" = a transaction (triage branch 3) — optionally also a dated line in the engagement's *History*. Deal income earmarks to the engagement via `initiative: "[[Engagement]]"`; a promised grant is an engagement (the deal) plus an `in + outstanding` pledge (the money). In a vault without the money module, log money events in the org/engagement note's History and offer to add the module.

## Discipline & privacy

- **One currency per transaction; balances reported per currency; never auto-convert.** Multi-currency funds get one balance line per currency.
- **Recurring money events** (rent, salaries): there is no transaction recurrence — capture each occurrence when it happens; a recurring *task* (`recurrence:`) works as the reminder.
- `domain:` follows whose life the money belongs to (`work`/`personal`); money notes are **sensitive by default regardless of domain** — amounts never appear in work outputs, emails, or shared notes unless the user explicitly includes them (communication.md ground rules apply).
- The live dashboard server's **Overview** tab shows fund balances (cash · receivables · pledges) in the browser. It binds to `127.0.0.1` only and writes no shareable file — but an unattended open dashboard tab is still a sensitive view; close it on shared screens.
- **Reviews:** the weekly sweep covers `outstanding` items like overdue tasks — each receivable/pledge gets a decision (chase, reschedule, or write off per the procedures above).
- Receipts/photos: attach to the transaction note (`Attachments/`).

## Queries this supports

"How much is in <fund>?" · "Who owes us?" / "what am I owed?" · "How much did initiative A raise / spend?" · "All transactions with William" (his backlinks or a counterparty-filtered view) · "What did we promise and not receive yet?" (pledges). Ready-made views: `bases.md` → **Ledger** (per-fund/per-initiative **net** sums; cash vs receivables vs pledges come from the table above — state them explicitly when reporting).
