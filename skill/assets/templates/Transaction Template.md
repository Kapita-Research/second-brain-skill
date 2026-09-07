---
type: transaction
domain: work
status: settled     # settled | outstanding | cancelled (cancelled = void, excluded from balances)
created: {{date:YYYY-MM-DD}}
fund:               # "[[Fund]]"
amount:             # positive number
currency: USD
direction: in       # in | out
txn: donation       # donation | expense | transfer | repayment | pledge | other
counterparty:       # "[[Person/Org]]" — omit for anonymous (note it below)
initiative:         # "[[Project/Area/Engagement]]" earmark, or general
related: []
tags:
  - transaction
---
# {{title}}

> One line: what happened.

## Notes
<!-- Context, receipt link, anonymous-donor note, partial-payment log. -->
