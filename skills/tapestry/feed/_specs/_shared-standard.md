# Shared Feed Standard

This document defines the baseline rules for every structured feed built by `tapestry-feed`.

## Core objective

The final feed should make downstream reading easy without flattening all sources into the same voice.

Every feed must:

- preserve the source identity
- surface the most decision-relevant content early
- separate factual extraction from interpretation
- remain faithful to the crawler output

## Required top-level sections

Unless a source-specific file explicitly changes this, every feed should contain these sections in order:

1. `Source`
2. `Snapshot`
3. `Primary Content`
4. `Discussion / Response Signals`
5. `Media / Attachments`
6. `Structured Metadata`
7. `Gaps / Uncertainties`

## Source section

Always include:

- original URL
- canonical URL when available
- crawler id
- source type / page type
- author or account name if available
- publication time if available

## Snapshot section

This section is the fast-read layer.

It should contain:

- one concise overview sentence
- 3 to 7 bullet points with the most important extracted facts

Do not put speculative interpretation here.

## Primary content section

This is where the main text is organized.

Rules:

- preserve the original logical order when possible
- do light cleanup only
- remove obvious UI chrome and navigation residue if it leaked into the crawl
- keep direct quotations only when they are essential

## Discussion / response signals

Only include this section when the source has meaningful discussion or audience response data.

Examples:

- comments
- reply trees
- top answers
- engagement counts

This section should distinguish:

- what the original author said
- what the audience or respondents added

## Media / attachments

If the crawler captured media metadata, include it.

Examples:

- image count
- image URLs or references
- linked media URL
- video presence

If there is no media, say so briefly.

## Structured metadata

List the source-specific extracted fields that matter later.

Examples:

- counts
- tags
- user/profile attributes
- answer counts
- vote counts
- follower counts

## Gaps / uncertainties

Always end with a short honesty section.

Examples:

- profile page returned a generic shell instead of rich profile data
- engagement counts were unavailable
- comments were not fetched
- crawler output includes partial UI text

## Anti-error rules

- Never infer author intent unless the source spec explicitly asks for interpretation.
- Never merge audience commentary into the source author’s claims.
- Never hide missing fields.
- Never silently drop major media or count signals when the crawler captured them.
