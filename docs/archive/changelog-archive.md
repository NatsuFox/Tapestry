# Implementation Changelog Archive

This document archives detailed implementation notes from the development process. For current project status, see [CHANGELOG.md](../CHANGELOG.md).

---

## Data Directory Consolidation (2026-03-16)

### Summary
Consolidated all generated content under a single `data/` directory for better organization.

### Changes

**Before**:
```
project/
├── data/
│   ├── captures/
│   └── feeds/
└── knowledge-base/
    ├── catalog.jsonl
    ├── notes/
    └── {topics}/  (book structure)
```

**After**:
```
project/
└── data/
    ├── captures/      # Raw HTML captures
    ├── feeds/         # Normalized feed JSON
    ├── notes/         # Phase 1: date-organized notes
    ├── books/         # Phase 2: book-like knowledge base
    └── catalog.jsonl  # Index of all ingested content
```

### Benefits
1. Single directory for all generated content
2. Cleaner project root structure
3. Easier gitignore configuration
4. Logical grouping of data artifacts
5. Clear separation between source and generated content

### Modified Files
- `skills/tapestry/_src/store.py` - Updated all path references
- `.gitignore` - Simplified to `/data/`
- All documentation updated to reflect new structure

---

## Knowledge Base Template System (2026-03-16)

### Summary
Replaced fixed blueprint with flexible template system for knowledge base initialization.

### Templates

**default** (minimal, agent-adaptable):
- Starts with just `index.md`
- Agent creates topics and chapters as needed
- Most flexible for diverse content

**comprehensive** (predefined taxonomy):
- Pre-created topics: AI & Research, Markets & Trading, People & Profiles, etc.
- Structured chapters within each topic
- Good for specific use cases

### Configuration
Users can set their preferred default template in `skills/tapestry/config/tapestry.config.json`:
```json
{
  "synthesis": {
    "kb_template": "default"  // or "comprehensive"
  }
}
```

Priority: CLI flag > config file > default ("default")

### Implementation
- Created `skills/tapestry/synthesis/_kb_templates/` directory
- Modified `bootstrap_kb.py` to support template selection
- Added `kb_template` field to `TapestryConfig`
- Updated documentation

---

## Auto-Synthesis Configuration (2026-03-16)

### Summary
Implemented configurable synthesis modes to control when AI synthesis runs.

### Modes

**auto** (default):
- Synthesis runs automatically after each ingest
- Best for immediate knowledge base updates
- Agent receives notification to run synthesis

**manual**:
- Synthesis only when explicitly requested
- Best for batch processing or manual control
- No automatic triggers

**batch**:
- Ingest multiple URLs first
- Synthesize all at once
- Best for efficiency with many URLs

### Configuration
Set in `skills/tapestry/config/tapestry.config.json`:
```json
{
  "synthesis": {
    "mode": "auto"  // "auto", "manual", or "batch"
  }
}
```

### Implementation
- Created `skills/tapestry/_src/config.py` with Pydantic models
- Modified `skills/tapestry/_src/crawlers/run.py` to check config
- Updated ingest workflow to notify agent when auto mode enabled
- Added comprehensive documentation

---

## Text Parsing Improvements (2026-03-16)

### Problem
Text extraction was producing "messy body contents" without proper paragraph breaks, making notes hard to read.

### Solution
Added `_extract_text_with_structure()` function that:
- Identifies block-level HTML elements (p, div, section, article, etc.)
- Adds paragraph breaks after block elements
- Preserves text structure and readability
- Ensures proper spacing after punctuation

### Implementation
Modified `skills/tapestry/_src/parse.py`:
```python
def _extract_text_with_structure(node) -> str:
    """Extract text while preserving paragraph structure."""
    block_elements = {'p', 'div', 'section', 'article', 'h1', 'h2', 'h3', ...}
    # Traverses DOM and adds paragraph breaks after block elements
    # Ensures proper spacing after punctuation
```

Enhanced `_select_text()` with `preserve_structure` parameter for better control.

---

## Directory Reorganization (2026-03-16)

### Summary
Reorganized project structure for better user-friendliness and standard Python conventions.

### Changes

**Tests moved to project root**:
- Before: `skills/tapestry/_tests/`
- After: `tests/`
- Benefits: Standard layout, easier discovery, follows pytest conventions

**Config moved into skills directory**:
- Before: `tapestry.config.json` at project root
- After: `skills/tapestry/config/tapestry.config.json`
- Benefits: Cleaner root, config with skill code, users can override at root

### Modified Files
- Moved all test files from `skills/tapestry/_tests/` to `tests/`
- Created `tests/README.md` with documentation
- Created `skills/tapestry/config/` directory
- Updated `.gitignore` to ignore user config overrides

---

## Synthesis Script Path Fix (2026-03-16)

### Problem
Synthesis scripts were creating directories in wrong locations and reporting "No stored catalog entry matched" errors.

### Root Cause
1. Scripts ran from Claude's skill cache instead of project root
2. Incorrect path calculations using `Path(__file__).resolve().parents[2]`
3. Default to `Path.cwd()` which was the skill cache directory

### Solution

**Fixed `load_context.py`**:
```python
# Before
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # Wrong!

# After
TAPESTRY_ROOT = Path(__file__).resolve().parents[2]  # For imports only
if args.project_root:
    target_root = Path(args.project_root).expanduser().resolve()
else:
    target_root = Path.cwd().resolve()  # Expects to be run from project root
```

**Updated SKILL.md**:
- Added explicit `cd` instructions
- Documented `--project-root` flag usage
- Clarified working directory requirements

### Result
Scripts now correctly create directories at project root and find catalog entries.

---

## Path Display Enhancement (2026-03-16)

### Problem
Ingestion output showed relative paths, making it unclear where files were actually located.

### Solution
Modified `_src/crawlers/run.py` to display absolute paths while keeping internal storage as relative paths:

```python
# Convert relative paths to absolute paths for display
feed_abs = (target_root / result.feed_path).resolve()
note_abs = (target_root / result.note_path).resolve()
```

### Benefits
- Clear file locations in output
- Easy to copy-paste paths
- No ambiguity about file locations
- Maintains portability with relative internal paths

---

## Install Skill Implementation (2026-03-16)

### Summary
Implemented comprehensive installation skill with environment detection and user confirmation.

### Features

**Environment Detection**:
- Detects Python version and executable path
- Identifies environment type: conda, venv, or system Python
- Determines best package manager: conda, uv, poetry, or pip
- Lists currently installed packages

**Dependency Analysis**:
- Parses `pyproject.toml` or `requirements.txt`
- Categorizes dependencies: core, optional, dev, docs
- Identifies post-install commands (e.g., `playwright install chromium`)
- Detects missing dependencies

**Installation Planning**:
- Generates environment-specific commands
- Provides clear descriptions for each step
- Supports multiple modes: all, core-only, custom
- Warns about risky scenarios (system Python)

**User Confirmation**:
- Presents installation plan before execution
- Uses `AskUserQuestion` for approval
- Allows customization of installation scope
- Never installs without explicit consent

**Verification**:
- Checks that packages are importable
- Verifies system tools (e.g., Playwright browsers)
- Reports detailed status for each dependency
- Provides actionable feedback on failures

### Implementation Structure
```
skills/install/
├── SKILL.md                    # Main skill documentation
├── README.md                   # Developer documentation
└── _scripts/
    ├── detect_env.py          # Environment detection
    ├── parse_deps.py          # Dependency parsing
    ├── install_deps.py        # Installation orchestrator
    └── verify_install.py      # Post-install verification
```

---

## Two-Phase Architecture

### Overview
Tapestry uses a two-phase architecture to separate deterministic extraction from AI-driven synthesis.

**Phase 1: Deterministic Extraction (Python)**
- Fast, reliable content extraction
- CSS selectors + readability + browser rendering
- Basic text cleaning
- Stores raw content in date-organized notes

**Phase 2: AI-Driven Synthesis (Agent)**
- Reads raw content
- Applies universal quality standards
- Formats and organizes properly
- Integrates into book-like knowledge base

### Benefits
- Consistent quality across all sources
- Single place to update standards
- Easy to add new crawlers
- Clear separation of concerns

### Implementation
- Phase 1: `skills/tapestry/ingest/`
- Phase 2: `skills/tapestry/synthesis/`
- Quality standards: `skills/tapestry/synthesis/SKILL.md`

---

## Centralized Quality Standards

### Before
Formatting instructions scattered across every crawler, leading to:
- Inconsistent quality
- Duplication of standards
- Hard to maintain
- Difficult to add new crawlers

### After
All quality standards centralized in `skills/tapestry/synthesis/SKILL.md`:
- Consistent quality across all sources
- Single source of truth
- Easy to update
- Crawlers focus only on extraction

### Standards Include
- Markdown formatting rules
- Citation and attribution requirements
- Content organization guidelines
- Metadata handling
- Quality checks

---

*For current development status and version history, see [CHANGELOG.md](../CHANGELOG.md)*
