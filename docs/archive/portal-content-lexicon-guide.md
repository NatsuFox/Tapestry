# Portal Content and Lexicon Guide

This document records the **content model, copy strategy, lexicon system, and editing preferences** for the Tapestry launch portal.

## Content Positioning

The landing page must promote **Tapestry** itself:

- a multi-source crawler layer
- a unified feed-normalization layer
- a synthesis system for converting sources into structured knowledge
- a display layer for turning that knowledge into a shareable output

The page should not position the portal as the product being sold. The portal is the **public launch surface and final presentation layer** for the Tapestry project.

## Copy Principles

### Tone

- premium
- launch-ready
- professional
- product-specific
- high-signal, not fluffy

### Scope

Copy should explain:

- what Tapestry is
- what problem it solves
- how the pipeline works
- why the output matters
- how source coverage differentiates it

Copy should avoid:

- talking too much about the landing page itself
- placeholder demo-page wording
- generic website-builder phrasing
- overly abstract “AI magic” claims

## Section Intent

### Introduction

Use a concise one-line project definition as the lead statement.

Current lead:

- `Tapestry - 基于 Agent Skill Bundle 的轻量级书签知识库`

The more detailed product explanation belongs in the secondary subtitle line beneath it.

### Overview

This section explains Tapestry as a reusable content-intelligence pipeline. It should describe:

- source-aware routing
- deterministic capture
- unified feed normalization
- synthesis into structured knowledge
- display/publishing as a project output

### Terminal Operations

This section proves that Tapestry is operational, not hypothetical. The copy should emphasize:

- real execution
- skill-driven workflow
- ingest pipeline entry from a single source URL
- observable system behavior

### Knowledge Base

This section should describe the Knowledge Base as a **direct product output** of Tapestry’s pipeline. It is not “the website preview”; it is evidence of what Tapestry produces after synthesis.

### Knowledge Sources

This section should explain support coverage in product terms:

- platform-aware crawling
- source-specific handling
- normalization into a common model
- unified output despite heterogeneous input

Avoid demo-oriented phrasing here. The copy should present Tapestry’s support model as a product capability.

## Lexicon System

All replaceable portal text is now centralized in:

- `src/ui/lexicon.json`

The portal hydrates:

- visible text
- alt text
- meta description
- aria labels
- preview button labels
- structure-detail content
- slide titles and captions
- small icon glyph text where applicable

### Why This Matters

This allows future refinement without searching through layout markup. The lexicon is the editing surface for:

- wording tweaks
- bilingual adjustments
- terminology changes
- section-title refinement
- CTA changes

## Editing Guidance

### When Adjusting Copy

- update `src/ui/lexicon.json` first
- avoid editing HTML for text-only changes
- keep Chinese as the primary information layer
- keep English supportive and concise

### When Adding New Sections

- decide whether the text belongs in lexicon before writing the HTML
- preserve the existing section heading pattern
- ensure generated labels and accessibility strings also come from the lexicon

### When Adding New Slides or Source Types

- extend the relevant arrays in `lexicon.json`
- keep slide titles and captions product-oriented
- keep source descriptions focused on what Tapestry enables

## Durable Preferences Captured

- Chinese-first, English-supported presentation
- high-end launch-page tone
- Tapestry-focused messaging, not portal-focused messaging
- no unrelated project branding
- all replaceable text should be centralized
- even accessibility labels should be included in the lexicon

## Maintenance Recommendation

Treat `src/ui/lexicon.json` as the portal’s copy contract. If the content and layout ever drift, the layout should remain stable while the lexicon evolves.
