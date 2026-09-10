# Evals (development-only — excluded from the packaged .skill)

Thirteen scenario evals in `evals.json` (skill-creator schema) + `trigger-queries.json` (20 should/shouldn't-fire queries). Fixtures in `files/`: `mini-vault/` (standard layout), `money-vault/` (fund + pre-existing transactions, for the money regression evals), `custom-vault/` (owner conventions that differ from skill defaults — tests First Contact/CLAUDE.md deference), `meeting-transcript.txt` (dictated, names deliberately mangled).

**How to run:** use Anthropic's `skill-creator` skill (Claude Code / Cowork with the `claude` CLI available): baseline runs without the skill, then with it; grade expectations per run; compare pass rates. The Cowork sandbox itself cannot spawn eval runs — run from a normal Claude Code checkout.

**Acceptance status:** evals 3 and 4 test the Phase-1 features (contact fields; group/roster notes). Expected to fail at v1.5.0; **from v1.6.0 they are expected to pass** and serve as the regression tests for the people/groups module.

Scenario→friction mapping (from the 2026-07-02 audit): 1 = dictated meeting → task notes (the original checkbox bug + name mangling); 2 = "what's on my plate" table (v1.3.2 format); 3 = contact capture (Phase 1); 4 = team roster (Phase 1); 5 = new-user bootstrap interview; 6 = CLAUDE.md deference over skill defaults; 7 = lifecycle status updates; 8 = recurrence convention (7–8 are Phase 2, expected to pass from v1.7.0); 9 = org/engagement pipeline filing; 10 = context-grounded email drafting with the privacy rule (9–10 are Phase 3, expected to pass from v1.8.0); 11 = recipient cold start (Phase 4, expected to pass from v2.2.0); 12 = money module — donations/expense/transfer with balance restatement (v2.3.0); 13 = partial repayment split rule + pledge write-off (regression for the v2.3.0 diagnosis criticals, expected to pass from v2.3.1). Note: eval fixtures use dates around 2026-06/07 — run with a comparable 'today' or expect date-relative expectations (eval 1's Monday) to shift.

**Fork evals (19–22)** cover the behaviours this fork adds, which upstream's suite does not touch:
**19** = `Outbox/` — the two refusals and the move · **20** = a finding quoted whole under a short
question · **21** = a new type written without negotiation · **22** = an ambiguous name surfaced rather
than silently picked. **All four share one fixture, `files/fork-vault`.** **23** = typing: one message mixing a survey
figure, a scraper diagnosis, an API's behaviour, a model comparison and a leftover action, on
`files/typing-vault`. It exists because anything with a number in it used to become a finding; **its
control is the model comparison, which must stay one.** They are **regression tests for
the diff**: if a newer upstream is ever adopted and the changes re-applied, these are what say whether
the behaviours survived.
