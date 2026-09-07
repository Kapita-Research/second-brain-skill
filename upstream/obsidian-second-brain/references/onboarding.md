# Onboarding — first run in a new vault

Use this when First Contact finds **no `CLAUDE.md` and no meaningful structure**. Goal: a vault shaped around *this* person's work, a `CLAUDE.md` that records the choices, and real value on day one. Never scaffold before the interview.

## The interview — one message, five questions

Ask conversationally (adapt wording, keep it one message):

1. **What do you do?** One or several hats — a role in a company, your own business, freelance, community work.
2. **What should this vault track?** Projects & deadlines · clients & deals · a team you manage · volunteers/community · properties/assets · money (donations, funds, debts) · research & learning · personal life alongside work.
3. **Who do you deal with?** Colleagues, clients, donors, tenants, volunteers, suppliers — and are there named teams/cohorts?
4. **What language(s) will you capture in?** (Dictation and mixed-language input are supported — names get resolved via aliases.)
5. **What should it answer in week one?** e.g. "what's on my plate?", "who owes me what?", "where does deal X stand?", "when did I last talk to Y?"

## Mapping answers → structure (the skill's types flex; don't invent new ones)

| They say… | Model as |
|---|---|
| clients, customers, donors, suppliers, agencies | `type: business` org notes in `Work/Business/` (`relationship:` distinguishes them) |
| deals, listings, grants, sponsorships, campaigns for a client | `type: engagement` (org:, value:, owner:, stage in `status:`) |
| my team, volunteers, committee, crew | `type: group` roster in `People/` + `groups:` on each person |
| properties, assets, fleets | an `Area` per asset class; each purchase/sale/lease in motion = an `engagement` (`org:` links the counterparty — an org note, or a person note for private sellers); the asset's paperwork lives in the engagement/area note |
| donations, funds we hold, who owes us, petty debts | `money` module — `type: fund` + `type: transaction` notes (`money.md`); balances restated at every capture |
| studying, reading, research | `resources` module (`Research/Sources/Books/Notes`); heavy book readers get the per-book folder + chapter system (`note-types.md` → *Book*) |
| ministries, regulators, state bodies | `type: government` org notes in `Work/Business/` (same schema as `business`) |
| journaling, life admin | `personal` module — mark it sensitive by default |

Multiple hats (e.g. agency + real estate + NGO) = **one vault**, one `Work/` tree: hats become **Areas**, their counterparties orgs, their deals engagements, their people/volunteers People + groups. Only split vaults when worlds must never mix.

## Scaffold (after answers, after a one-line confirmation of the plan)

1. Run the deterministic scaffold — **execute**:
   `python3 "<skill-path>/scripts/bootstrap_vault.py" "<vault>" --modules core,work[,personal,resources,daily,money]`
   (`<skill-path>` = the skill's install root — see *Running bundled scripts* in SKILL.md's Operating Modes.)
   It creates folders, installs `assets/templates/` into `Templates/` and `assets/bases/` into `Maps/Dashboards/`, and writes a starter `Maps/Home.md`. It refuses to touch a vault that already has a `CLAUDE.md`. (No shell? Create the same by hand from `vault-structure.md`.)
2. **Write the vault `CLAUDE.md`** — the interview's lasting output: their structure, domains, vocabulary extensions, naming, languages, sensitivities. Keep it short; it overrides skill defaults forever after.
3. **Seed the entities they named:** their own person note, their org(s), their group(s) with members they listed — and, if the money module was chosen, their first **fund** (`owner:` whose money, `custodian:` who holds it).
4. **First real capture, immediately:** ask for today's top 2–3 tasks and the last meeting they had; file them properly (Golden Rule 7, `source:` links). Then show "what's on my plate" — the vault answers something real in minute ten.
5. Close with day-1 habits: capture anything by telling Claude; ask "what's on my plate" tomorrow; weekly review when a week of notes exists. Don't mention advanced machinery until they need it.

## Don'ts

- Don't create folders their answers didn't justify (empty structure kills adoption — "Day 1 minimal start" in `vault-structure.md`).
- Don't write personal/journal scaffolding unless asked (question 2).
- Don't overwrite an existing `CLAUDE.md` — that vault isn't yours to reshape (First Contact rule).
