# Knowledge Base Templates

## Summary

Replaced fixed blueprint with flexible template system:
- **default** template: Minimal, agent-adaptable (just index.md)
- **comprehensive** template: Predefined topics (AI, markets, etc.)

## Changes

### Before
```
_kb_blueprint/knowledge-base/
  ├── index.md
  ├── ai-and-research/
  ├── markets-and-trading/
  └── ... (always created)
```

### After
```
_kb_templates/
  ├── default/              # Minimal (NEW DEFAULT)
  │   └── index.md
  └── comprehensive/        # Full structure (OPTIONAL)
      ├── index.md
      ├── ai-and-research/
      └── ...
```

## Implementation

### Modified Files

**`skills/tapestry/synthesis/_scripts/bootstrap_kb.py`**:
```python
# Added --template flag
parser.add_argument(
    "--template",
    default="default",
    choices=["default", "comprehensive"],
    help="Template to use"
)

# Load from templates
template_root = Path(__file__).resolve().parent.parent / "_kb_templates" / args.template
```

### Created Files

- `skills/tapestry/synthesis/_kb_templates/default/index.md` - Minimal template
- `skills/tapestry/synthesis/_kb_templates/comprehensive/` - Full structure
- `skills/tapestry/synthesis/_kb_templates/README.md` - Documentation

## Usage

### Default (Minimal)
```bash
python skills/tapestry/synthesis/_scripts/bootstrap_kb.py
# Creates: data/books/index.md only
```

### Comprehensive (Full Structure)
```bash
python skills/tapestry/synthesis/_scripts/bootstrap_kb.py --template comprehensive
# Creates: data/books/ with all predefined topics
```

### Configuration
Set your preferred default template in `skills/tapestry/config/tapestry.config.json`:
```json
{
  "synthesis": {
    "kb_template": "default"  // or "comprehensive"
  }
}
```

Priority: CLI flag > config file > default ("default")

## Benefits

1. **Flexibility**: Agent can create topics as needed
2. **Simplicity**: Default starts with just one file
3. **Adaptability**: Easy for agent to modify structure
4. **Choice**: Users can still use comprehensive template if desired
5. **Cleaner**: No unused directories by default

## Default Template Content

```markdown
# Knowledge Base

A simple, flexible knowledge base structure. The agent can easily create
new topics and chapters as needed.

## Topics

This knowledge base starts empty. Topics will be created as content is
synthesized.

## How to Use

When synthesizing content, the agent will:
1. Analyze the content's subject matter
2. Create appropriate topics if they don't exist
3. Organize content into chapters within topics
4. Maintain this index with links to all topics
```

## Agent Workflow

With the default template, the agent will:

1. **First synthesis**: Create appropriate topic directory
   ```
   data/books/
   ├── index.md
   └── machine-learning/
       └── index.md
   ```

2. **Add content**: Create chapters within topics
   ```
   data/books/
   ├── index.md
   └── machine-learning/
       ├── index.md
       └── neural-networks/
           └── index.md
   ```

3. **Update index**: Keep top-level index current
   ```markdown
   ## Topics

   - [Machine Learning](machine-learning/index.md)
     neural networks, training techniques, and ML research
   ```

## Testing

```bash
# Test default template
$ rm -rf data/books && python skills/tapestry/synthesis/_scripts/bootstrap_kb.py
$ tree data/books
data/books
└── index.md
✓ PASS - Minimal structure created

# Test comprehensive template
$ rm -rf data/books && python skills/tapestry/synthesis/_scripts/bootstrap_kb.py --template comprehensive
$ tree data/books -L 1
data/books
├── ai-and-research/
├── markets-and-trading/
├── people-and-profiles/
├── community-qa-and-discussion/
├── general-reference/
└── index.md
✓ PASS - Full structure created
```

## Migration

Existing installations using the old blueprint will continue to work. The comprehensive template contains the same structure as the old blueprint.

## See Also

- [Two-Phase Organization](two-phase-organization.md)
- [Data Consolidation](data-consolidation.md)
- [Synthesis Quality Standards](synthesis-quality-standards.md)
