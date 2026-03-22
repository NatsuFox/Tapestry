---
name: tapestry
description: AI-native web intelligence workflow for crawling, organizing, and synthesizing web content from multiple platforms (Zhihu, Reddit, HN, X/Twitter, Xiaohongshu, Weibo). Use when users share URLs, want to archive web content, build knowledge bases, or analyze online discussions.
argument-hint: [url-or-instruction]
---

# 🧵 Tapestry

**AI-Native Web Intelligence Workflow**

Tapestry is a complete workflow for turning scattered web content into organized, searchable knowledge. It handles everything from crawling to synthesis across multiple platforms.

## When to Use Tapestry

Use this skill when the user:
- Shares URLs to ingest (from Zhihu, Reddit, HN, X/Twitter, Xiaohongshu, Weibo, or any webpage)
- Wants to archive or capture web content
- Asks to organize content into a knowledge base
- Wants structured feeds or analysis of web content
- Needs to visualize their knowledge base

## Workflow Overview

Tapestry has six internal sub-skills that work together:

1. **Init Deps Install** (`init-deps-install/SKILL.md`) - Auto-triggered dependency installation (Phase 0: setup)
2. **Ingest** (`ingest/SKILL.md`) - Crawl and capture URLs (Phase 1: deterministic)
3. **Synthesis** (`synthesis/SKILL.md`) - Analyze and organize into knowledge base (Phase 2: AI-driven)
4. **Feed** (`feed/SKILL.md`) - Generate structured, source-aware feeds
5. **Display** (`display/SKILL.md`) - Visualize the knowledge base as a website
6. **Visual Card** (`visual-card/SKILL.md`) - Generate visual note cards from KB content

### Two-Phase Architecture

Tapestry uses a two-phase design with automatic dependency setup:

**Phase 0 (Init)**: Auto-triggered dependency installation when first launched or dependencies missing
**Phase 1 (Ingest)**: Deterministic extraction → `_data/notes/YYYY/MM/` (date-organized)
**Phase 2 (Synthesis)**: AI-driven analysis → `_data/books/{topic}/{chapter}/` (book-organized)

By default, synthesis runs automatically after each ingest (`synthesis.mode: "auto"` in `tapestry.config.json`). You can configure this to "manual" or "batch" mode.

## How to Use This Skill

### Step 1: Understand the User's Intent

Analyze what the user wants:
- **Just capture?** → Use ingest only (set synthesis mode to "manual" if needed)
- **Structured feed?** → Use ingest + feed
- **Analysis/organization?** → Use ingest + synthesis (default with "auto" mode)
- **Browse knowledge base?** → Use display
- **Visual summary?** → Use visual-card to generate infographic cards
- **Complete workflow?** → Ingest automatically triggers synthesis in "auto" mode

### Step 2: Execute the Appropriate Sub-Skill(s)

Read and follow the instructions in the relevant sub-skill SKILL.md files:

#### For Dependency Installation (Auto-Triggered)

Read the file `init-deps-install/SKILL.md` to understand the detection and installation workflow.
All installation steps require explicit user confirmation before execution.

#### For URL Ingestion

Read the file `ingest/SKILL.md`, then follow the workflow described there.

#### For Structured Feeds

Read the file `feed/SKILL.md`, then follow the workflow described there.

#### For Synthesis & Knowledge Base

Read the file `synthesis/SKILL.md`, then follow the workflow described there.

#### For Visualization

Read the file `display/SKILL.md`, then follow the workflow described there.

#### For Visual Cards

Read the file `visual-card/SKILL.md`, then follow the workflow described there.

### Step 3: Chain Sub-Skills When Needed

The sub-skills reference each other. When one sub-skill says to "route to" another, read that sub-skill's SKILL.md and follow its instructions.

## Supported Platforms

- 🇨🇳 **Zhihu**: Questions, answers, articles, profiles
- 🐦 **X/Twitter**: Posts, threads
- 📱 **Xiaohongshu**: Notes, profiles
- 🇨🇳 **Weibo**: Posts
- 🔶 **Hacker News**: Discussions with full comment trees
- 🤖 **Reddit**: Threads
- 🌐 **Generic HTML**: Any webpage (fallback)

## Key Principles

1. **Read sub-skill instructions first**: Each sub-skill's SKILL.md contains detailed workflow steps
2. **Follow the deterministic pipeline**: Ingest → Feed → Synthesis → Display
3. **Respect user intent**: Don't over-process if they just want capture
4. **Chain appropriately**: Let sub-skills hand off to each other as described in their instructions
5. **Report clearly**: Tell the user what was done and where artifacts are stored

## Directory Structure

```
tapestry/
├── SKILL.md (this file)          # Main orchestrator
├── init-deps-install/SKILL.md     # Dependency installation sub-skill
├── ingest/SKILL.md                # URL crawling sub-skill
├── feed/SKILL.md                  # Feed generation sub-skill
├── synthesis/SKILL.md             # Analysis & KB sub-skill
├── display/SKILL.md               # Visualization sub-skill
├── visual-card/SKILL.md           # Visual card generation sub-skill
├── _src/                          # Shared code (crawlers, parsers, storage)
└── _tests/                        # Unit tests
```

## Example Usage Patterns

### Pattern 1: Simple Capture
```
User: "Ingest this Zhihu answer: https://www.zhihu.com/question/123/answer/456"

Action:
1. Read ingest/SKILL.md
2. Follow its workflow to capture the URL
3. Report the created artifacts
```

### Pattern 2: Structured Feed
```
User: "Give me a structured feed of this Reddit thread"

Action:
1. Read ingest/SKILL.md and capture the URL
2. Read feed/SKILL.md and generate the structured feed
3. Present the feed to the user
```

### Pattern 3: Full Analysis (Default)
```
User: "Analyze this HN discussion and add it to my knowledge base"

Action:
1. Read ingest/SKILL.md and capture the URL
2. Synthesis runs automatically (default "auto" mode)
3. Report where the content was organized in the KB
```

### Pattern 4: Manual Synthesis
```
User: "Just capture these URLs for now, I'll organize them later"

Action:
1. Set synthesis mode to "manual" in tapestry.config.json
2. Read ingest/SKILL.md and capture the URLs
3. User can later run synthesis on selected URLs
```

### Pattern 4: Batch Processing
```
User: "Ingest these 5 URLs and organize them"

Action:
1. Read ingest/SKILL.md and batch process all URLs
2. With "auto" mode, synthesis runs for each URL automatically
3. Summarize the results
```

## Important Notes

- **Always read the sub-skill SKILL.md files**: They contain the actual implementation details
- **Don't invent workflows**: Follow what's written in the sub-skill instructions
- **Preserve artifacts**: The pipeline creates `_data/captures/`, `_data/feeds/`, `_data/notes/`, and `_data/books/`
- **Respect the architecture**: Ingest is deterministic, synthesis is interpretive
- **Check for errors**: Sub-skills may fail; handle gracefully and report to user

## Resources

- `_src/`: Shared Python code for crawlers, parsers, and storage
- `_tests/`: Unit tests for the shared code
- Each sub-skill has its own `_scripts/`, `_specs/`, or `_kb_rules/` directories

---

**Remember**: This main skill is an orchestrator. The real work happens in the sub-skills. Read their SKILL.md files and follow their instructions.
