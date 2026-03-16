# Tapestry Skills

This directory contains all skills for the Tapestry project.

## Available Skills

### 1. tapestry (Main Orchestrator)
**Path**: `skills/tapestry/SKILL.md`

AI-native web intelligence workflow for crawling, organizing, and synthesizing web content from multiple platforms (Zhihu, Reddit, HN, X/Twitter, Xiaohongshu, Weibo).

**Sub-skills**:
- `ingest/` - URL crawling and capture
- `feed/` - Structured feed generation
- `synthesis/` - AI-driven knowledge base organization
- `display/` - Knowledge base visualization

### 2. tapestry-install
**Path**: `skills/tapestry-install/SKILL.md`

Intelligent dependency installation with environment detection. Handles virtual environments, conda, package managers, and system-level dependencies.

**Features**:
- Environment detection (conda, venv, system Python)
- Dependency analysis (pyproject.toml, requirements.txt)
- Installation planning with user confirmation
- Post-install verification
- System tool installation (e.g., playwright browsers)

**Usage**: `/tapestry-install`

## Skill Development

When creating new skills:

1. Create a directory under `skills/`
2. Add a `SKILL.md` file with frontmatter:
   ```yaml
   ---
   name: skill-name
   description: Brief description
   argument-hint: [optional-args]
   ---
   ```
3. Include implementation in `_scripts/` or `_src/`
4. Add tests in `tests/`
5. Document in README.md

## Testing Skills

```bash
# Test individual skill scripts
python skills/tapestry-install/_scripts/detect_env.py

# Run integration tests
python tests/test_tapestry_install_skill.py
```

## Skill Naming Convention

- Use lowercase with hyphens: `skill-name`
- Prefix with project name for project-specific skills: `tapestry-install`
- Keep names concise and descriptive
