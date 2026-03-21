# Portal Design and Implementation

This document captures the **design system, interaction rules, structure, and frontend implementation** of the Tapestry launch portal.

## Purpose

The portal is a launch surface for the **Tapestry project**, not the product being promoted in isolation. Its role is to explain Tapestry’s value, show how the pipeline works, demonstrate real execution, and present the form of the resulting knowledge output.

## Layout Structure

The current portal keeps five major sections in order:

1. Introduction
2. Overview
3. Terminal Operations
4. Knowledge Base
5. Knowledge Sources

The first section acts as the brand-facing entry point. Every later section is normalized around:

- eyebrow
- headline
- supporting English line
- a section-specific content module

This structure is deliberate because it keeps the page visually coherent while letting different content systems live underneath.

## Visual Direction

### Core Style

- warm glassmorphism
- soft amber highlight accents
- even top illumination
- restrained shadows
- roomy composition rather than dense sales-page stacking

### Typography

- Chinese-first information hierarchy
- English as secondary support text
- headings are prominent but not oversized
- diagram typography is lighter than the main heading system

### Brand Treatment

- only Tapestry-owned visual assets should be used
- the current hero/header wordmark comes from the project’s own high-resolution logo source
- the logo animation is subtle and pointer-reactive, not decorative noise

## Interactive Rules

### Logo Motion

The main logo uses pointer-driven CSS variable transforms:

- mild rotateX / rotateY
- slight translate3d shift
- reset on pointer leave
- disabled under reduced-motion preference

The intent is to create a premium, responsive feel without turning the page into an animation demo.

### Structural Diagram

The Overview diagram represents the pipeline:

- Match
- Capture
- Feed
- Synthesis
- Structure
- Display

Interaction rules:

- hovering or clicking a node updates the detail card beneath the diagram
- node highlighting should stay visually anchored
- the node group itself should not jump or detach from the layout
- no visible focus-ring artifact should remain after click
- the final node should not remain highlighted by default

### Terminal Section

The terminal area is not a fake code block. It uses:

- local asciinema player assets
- a local `.cast` recording
- a macOS-inspired window chrome

Interaction rules:

- the terminal shell itself should not aggressively float on hover
- subtle shadow increase is enough
- the three traffic-light buttons may animate lightly to mimic a desktop window

### Knowledge Base Carousel

The Knowledge Base module should preserve this layout:

- section heading on the left
- timer and previous/next controls pinned on the far right
- timer always visible
- automatic slide progression every few seconds
- manual controls stay available

The carousel is meant to hold future real screenshots without redesigning the section.

### Source Cards

Source cards should feel alive but controlled:

- cards may rise slightly on hover
- source icons may float slightly on hover
- source tags should highlight on hover without floating
- tag contrast should remain readable against the glass card background

## Frontend Implementation

### Core Files

- `src/ui/index.html`
- `src/ui/styles.css`
- `src/ui/app.js`

### Supporting Assets

- `src/ui/assets/tapestry-logo-transparent.png`
- `src/ui/assets/zhihu_fetch.cast`
- `src/ui/vendor/asciinema-player.min.js`
- `src/ui/vendor/asciinema-player.css`

### Behavior Wiring

`app.js` currently initializes:

- nav expansion for mobile
- logo motion
- structure diagram detail switching
- asciinema player mounting
- timed Knowledge Base carousel
- lexicon-driven copy hydration

## Verification Pattern

Portal changes should continue to be verified with:

- local HTTP serving
- browser-level desktop check
- browser-level mobile check
- hover/interaction checks
- console/request/page error checks
- screenshot review for visual regressions

## Durable Preferences

- Keep edits isolated to `src/ui/` for portal work
- Preserve the current layout and visual baseline unless explicitly changed
- Keep interactions subtle, premium, and legible
- Prioritize Tapestry’s real architecture and workflow truth over generic marketing language
