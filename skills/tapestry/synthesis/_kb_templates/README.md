# Knowledge Base Templates

Templates for initializing the book-like knowledge base structure.

## Available Templates

### default (Recommended)
**Minimal, agent-adaptable structure**

- Starts with just an `index.md` file
- Agent creates topics and chapters as needed
- Most flexible for diverse content
- Easy to modify and adapt

**Use when:**
- You want maximum flexibility
- Content topics are not predetermined
- Agent should decide organization

**Usage:**
```bash
python _scripts/bootstrap_kb.py --template default
```

### comprehensive
**Predefined topic taxonomy**

- Pre-created topics: AI & Research, Markets & Trading, People & Profiles, etc.
- Structured chapters within each topic
- Good for specific use cases

**Use when:**
- You know your content domains in advance
- You want immediate structure
- Content fits predefined categories

**Usage:**
```bash
python _scripts/bootstrap_kb.py --template comprehensive
```

## Template Structure

### default/
```
index.md    # Simple starting point with instructions
```

### comprehensive/
```
index.md
ai-and-research/
  index.md
  agent-development-and-tooling/
  model-training-and-optimization/
  research-tracking-and-papers/
markets-and-trading/
  index.md
  market-structure-and-signals/
  trading-psychology-and-risk/
people-and-profiles/
  index.md
  researchers-and-creators/
community-qa-and-discussion/
  index.md
  platform-discussions/
  practical-identification-and-qa/
general-reference/
  index.md
  reference-and-articles/
```

## Creating Custom Templates

1. Create a new directory under `_kb_templates/`
2. Add an `index.md` file
3. Add any topic/chapter structure you want
4. Use with `--template your-template-name`

## Default Behavior

If no `--template` flag is specified, the template is loaded from the configuration file (`skills/tapestry/config/tapestry.config.json`). If no config is found, the **default** template is used.

**Priority**: CLI flag > config file > default ("default")

To set your preferred template, edit `skills/tapestry/config/tapestry.config.json`:
```json
{
  "synthesis": {
    "kb_template": "default"  // or "comprehensive"
  }
}
```

This provides a clean slate for the agent to organize content naturally.
