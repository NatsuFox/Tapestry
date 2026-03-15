# Synthesis Governance

This file defines how the synthesis skill should maintain the book-like knowledge base under `knowledge-base/books/`.

## Core objective

The knowledge base is not a flat pile of notes.

It should behave like a living reference book:

- top-level topics hold coarse semantic clusters
- child chapters hold coherent sub-domains
- each `index.md` explains the scope and organization of its level

## Allowed operations

For every incoming feed, the synthesis skill may:

1. create a new topic if the current top-level taxonomy cannot absorb the feed cleanly
2. create a new chapter inside an existing topic
3. extend an existing chapter
4. split a chapter when it becomes too mixed
5. revise parent `index.md` files to reflect structural changes

## Required behavior

- Always inspect the nearest relevant `index.md` files before editing chapter content.
- Prefer the narrowest valid placement that still fits the content honestly.
- Preserve topical coherence over convenience.
- If a feed contains multiple unrelated semantic threads, either:
  - place it in the dominant chapter and note the secondary themes, or
  - split the knowledge into more than one destination when that is clearly warranted.

## Index requirements

Every level must have an `index.md`.

Each `index.md` should include:

- purpose of the level
- scope boundary
- child nodes and what each child covers
- recent structural decisions when relevant

## Anti-chaos rules

- Do not create near-duplicate chapters just because wording differs slightly.
- Do not append unrelated content to a chapter that already has a clear semantic center.
- Do not leave newly created chapters unregistered in every parent `index.md` above them.
- If a topic becomes too broad, prefer a structural split over increasingly vague chapter titles.
