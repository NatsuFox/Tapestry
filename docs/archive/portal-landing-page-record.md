# Portal Landing Page Record

This document summarizes the full portal-landing-page rollout for Tapestry, including design direction, implementation decisions, verification steps, and working preferences captured during the iteration cycle.

## Related Documents

- [Portal Design and Implementation](portal-design-implementation.md)
- [Portal Content and Lexicon Guide](portal-content-lexicon-guide.md)

## Summary

The portal at `src/ui/` was built as a public-facing launch page for the **Tapestry project itself**, not as a showcase of the landing page as a product. The final direction presents Tapestry as an **agent-native, multi-source content intelligence library** that:

- captures web content from multiple platforms,
- normalizes heterogeneous sources into a unified feed layer,
- synthesizes content into structured knowledge,
- publishes a polished, shareable output surface.

The portal ended up as a **Chinese-first, English-supported** showcase with warm glassmorphism styling, restrained interactive motion, a real terminal workflow demo, and a lexicon-driven content system for future copy refinement.

## Final Scope

All portal work was intentionally kept inside `src/ui/` and its local assets/vendor files.

### Core Files

- `src/ui/index.html` - Portal structure and content slots
- `src/ui/styles.css` - Visual design, layout, hover states, and responsive behavior
- `src/ui/app.js` - Interaction logic, lexicon hydration, structure-diagram behavior, carousel timing, and local asciinema player initialization
- `src/ui/lexicon.json` - Centralized copy dictionary for replaceable text
- `src/ui/assets/tapestry-logo-transparent.png` - Transparent hero/header logo generated from project artwork
- `src/ui/assets/zhihu_fetch.cast` - Terminal recording embedded on the page
- `src/ui/vendor/asciinema-player.min.js` - Local asciinema player bundle
- `src/ui/vendor/asciinema-player.css` - Local asciinema player stylesheet

## Design Direction

### Visual Language

- Warm glassmorphism with soft amber highlights and an even top glow
- Large Tapestry brand mark at the top of the page
- Spacious layout with soft cards, layered surfaces, and restrained shadows
- Interactive polish without turning the page into a motion demo

### Structure

The final portal keeps the current high-level order:

1. Introduction
2. Overview
3. Terminal Operations
4. Knowledge Base
5. Knowledge Sources

Each section after the opening intro was normalized to a common structure:

- eyebrow
- main heading
- supporting English line

This keeps the page readable and consistent while still allowing different content modules underneath.

## Content Positioning

The copy was rewritten away from “look at this landing page” language and toward **Tapestry’s value proposition**:

- Tapestry is presented as a **skill library** and **content pipeline**
- The portal is framed as the **result** of Tapestry, not the main product
- The Knowledge Base is described as a **direct product output** of ingestion, feed normalization, synthesis, and display
- The terminal section is used as proof of real execution, not a decorative terminal shell
- The sources section emphasizes **source-aware ingestion**, **unified schemas**, and **consistent output**

## Implementation Notes

### 1. Transparent Tapestry Logo

The final main logo uses a transparent asset derived from the project’s own artwork:

- initial source: `assets/tapestry_logo.png`
- later replaced with a higher-resolution source from `assets/tapestry_logo_highres.jpg`
- output file: `src/ui/assets/tapestry-logo-transparent.png`

Important lesson:

- do not pull branding from sibling projects or archived unrelated repos
- use only Tapestry-owned assets for Tapestry’s public surface

### 2. Local Asciinema Embedding

The `zhihu_fetch.cast` recording is embedded locally using the official asciinema player approach rather than a custom parser.

Implementation choices:

- vendored local player bundle under `src/ui/vendor/`
- embedded player mounted in `app.js`
- local cast path used directly from `src/ui/assets/zhihu_fetch.cast`

Important lesson:

- for `.cast` playback, use the official asciinema player model instead of trying to reinterpret the cast stream manually

### 3. Knowledge Base Preview Carousel

The Knowledge Base section uses a timed image carousel with:

- automatic switching every few seconds,
- left/right controls pinned to the far right,
- a visible progress/timer bar,
- caption/title updates synced to the current slide.

Important lesson:

- the header layout of this section matters; keep the controls and timer aligned at the far right even when trimming nearby text

### 4. Structure Diagram

The Overview section contains a six-node diagram representing the pipeline:

- Match
- Capture
- Feed
- Synthesis
- Structure
- Display

The detail panel beneath the diagram updates when a node is hovered or clicked.

Important lesson:

- avoid transforming the full SVG node group on hover; highlight the node visually without shifting its geometry
- remove focus-ring-like selection artifacts from click behavior
- keep the diagram typography lighter and more elegant than the surrounding section headings

### 5. Lexicon-Driven Copy System

All replaceable portal text was centralized into:

- `src/ui/lexicon.json`

The page now hydrates:

- visible content text,
- alt text,
- meta description,
- aria labels,
- generated preview-dot labels,
- structure-diagram detail strings,
- Knowledge Base slide titles/captions,
- small text glyphs used as source-icon labels.

Important lesson:

- if the goal is future refinement speed, lexicon coverage must include accessibility strings and JS-generated labels, not only visible marketing copy

## Verification Performed

Portal verification was done repeatedly during implementation and refinement.

### Runtime Checks

- Local HTTP serving via `python3 -m http.server`
- Direct HTTP verification for:
  - `src/ui/index.html`
  - `src/ui/styles.css`
  - `src/ui/app.js`
  - local logo assets
  - local asciinema assets
  - `zhihu_fetch.cast`

### Browser Checks

Headless browser checks covered:

- desktop and mobile render
- nav expansion on mobile
- preview carousel switching and timer behavior
- asciinema player rendering
- structure-node detail swapping
- hover/focus interaction behavior
- console/request/page error checks

### Visual Checks

Repeated screenshot reviews were used to validate:

- spacing,
- typography scale,
- section hierarchy,
- hover intensity,
- icon visibility,
- source-tag contrast,
- terminal chrome styling,
- diagram emphasis.

## Preferences Captured For Future Portal Work

These preferences were expressed clearly during the rollout and should be treated as durable guidance for future edits.

### Branding and Assets

- Use only Tapestry assets on the Tapestry portal
- Do not reuse assets from sibling or unrelated projects
- Prefer project-owned high-resolution logo sources when available

### Layout and Style

- Preserve the current layout, typography direction, and overall style baseline unless explicitly changed
- Keep Chinese as the primary language and English as a secondary support layer
- Use warm glassmorphism, but avoid clutter and cramped layouts
- Favor spacious composition over dense marketing panels

### Content

- Promote Tapestry the library/workflow, not the landing page itself
- Write at a high-end launch-page standard
- Keep copy professional, product-oriented, and specific to Tapestry’s real capabilities

### Interaction

- Interactions should feel polished and subtle, not showy
- Terminal chrome should mimic macOS lightly without becoming a gimmick
- Source icons may float slightly on hover
- Source tags should highlight on hover without floating
- Structure nodes should reveal details without visually “jumping”

### Maintainability

- Put all replaceable text into `lexicon.json`
- Keep future content tuning copy-first by editing the lexicon, not the page structure
- Keep portal-specific work isolated under `src/ui/`

## Current Portal Role

The current portal should be understood as:

- a public entry point for the Tapestry project,
- a brand surface for explaining the library’s value,
- a proof surface for Tapestry’s execution model,
- a display output that demonstrates what the Tapestry pipeline can produce.

It should **not** be treated as the product being promoted in isolation.

## Suggested Session Name

`Tapestry Launch Portal`
