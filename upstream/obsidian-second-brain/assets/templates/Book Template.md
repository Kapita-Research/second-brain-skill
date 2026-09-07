---
type: book
domain: shared
status: to-read     # to-read | reading | done
created: {{date:YYYY-MM-DD}}
author:
  - "[[ ]]"
year: 
rating:             # 1–5, set when finished
source:             # edition / file / store link, if any
aliases: []
tags:
  - topic/
---
# {{title}}

> One-line takeaway — fill it when it crystallizes.

<!-- One folder per book: this note lives at Resources/Books/<Title>/<Title>.md, chapter notes beside it
     (type: chapter, book: "[[<Title>]]", filenames "<Title> — Ch01 <Name>.md" so they sort).
     Your own ideas go to Resources/Notes/ as type: concept with source: "[[<Title>]]" — the views below pick both up live. -->

## Reading log
- {{date:YYYY-MM-DD}} — added to the shelf.

## Chapters
```base
filters:
  and:
    - 'type == "chapter"'
    - 'book == this'
views:
  - type: table
    name: "Chapters"
    order:
      - file.name
      - chapter
```

## Ideas sparked
```base
filters:
  and:
    - 'type == "concept"'
    - 'source == this'
views:
  - type: table
    name: "Ideas"
    order:
      - file.name
      - created
```

## Related
- [[ ]]
