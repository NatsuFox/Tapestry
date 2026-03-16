# Synthesis Quality Standards Architecture

## Design Decision

All formatting and quality standards are now **centralized in the synthesis skill** (`synthesis/SKILL.md`), not scattered across individual crawlers.

## Why This Approach?

### 1. Consistency Across All Sources

**Before** (distributed):
```python
# generic_html crawler
instructions="Format with headers and lists..."

# zhihu crawler
instructions="Format with headers and lists..."

# reddit crawler
instructions="Format with headers and lists..."
```
❌ Duplicated instructions across every crawler
❌ Inconsistent quality if one crawler is updated
❌ Hard to maintain and improve

**After** (centralized):
```python
# synthesis/SKILL.md
## Synthesis Quality Standards
All content must:
- Use clear hierarchical headers
- Add paragraph breaks
- Apply markdown formatting
...

# Crawlers just specify content-specific focus
generic_html: "Focus on thesis and key arguments"
zhihu: "Preserve question-answer structure"
reddit: "Highlight discussion insights"
```
✓ Single source of truth for quality standards
✓ Consistent quality across all sources
✓ Easy to update and improve

### 2. Separation of Concerns

**Crawlers** (content-specific):
- What to focus on for this content type
- What structure to preserve
- What context is important

**Synthesis Skill** (universal):
- How to format text properly
- How to organize content
- How to clean up noise
- How to integrate into KB

### 3. Easier Maintenance

To improve formatting quality:
- **Before**: Update 7+ crawler definitions
- **After**: Update 1 synthesis skill

### 4. Better for New Crawlers

Adding a new crawler:
- **Before**: Copy-paste formatting instructions, hope they're up to date
- **After**: Just specify content-specific focus, formatting is automatic

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Synthesis Skill                    │
│                                                     │
│  ┌───────────────────────────────────────────┐    │
│  │   Universal Quality Standards             │    │
│  │   - Text formatting and cleanup           │    │
│  │   - Content organization                  │    │
│  │   - Factual accuracy                      │    │
│  │   - Markdown formatting                   │    │
│  │   - Noise removal                         │    │
│  │   - KB integration                        │    │
│  └───────────────────────────────────────────┘    │
│                      ↑                              │
│                      │ Applied to all content      │
└──────────────────────┼──────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
   ┌────▼────┐    ┌───▼────┐    ┌───▼────┐
   │ Generic │    │ Zhihu  │    │ Reddit │
   │  HTML   │    │Crawler │    │Crawler │
   └─────────┘    └────────┘    └────────┘
   Content-specific instructions only:
   "Focus on      "Preserve     "Highlight
    thesis"        Q&A format"   insights"
```

## Implementation

### Synthesis Skill (synthesis/SKILL.md)

Contains comprehensive quality standards:

```markdown
## Synthesis Quality Standards

**IMPORTANT**: All synthesized content must go through this refinement
process, regardless of the source crawler or content type.

### 1. Text Formatting and Cleanup
- Use clear hierarchical headers
- Add paragraph breaks
- Apply markdown formatting
- Remove noise and artifacts

### 2. Content Organization
- Identify main topic
- Create clear hierarchy
- Preserve important elements

### 3. Factual Accuracy
- Ground in source material
- Maintain technical accuracy
- Preserve context

### 4. Content-Specific Guidance
- For articles: preserve thesis
- For discussions: preserve Q&A structure
- For reference: organize for lookup

### 5. Knowledge Base Integration
- Determine placement
- Update hierarchy
```

### Crawler Definitions

Keep instructions minimal and content-specific:

```python
# generic_html
analysis=AnalysisHandoff(
    skill="tapestry-synthesis",
    deliverable="Create a well-organized synthesis note from the article.",
    instructions="Focus on the article's main thesis, key arguments, and concrete claims."
)

# zhihu (hypothetical)
analysis=AnalysisHandoff(
    skill="tapestry-synthesis",
    deliverable="Create a Q&A synthesis preserving the question-answer structure.",
    instructions="Preserve the question, answer, and key discussion points."
)

# reddit (hypothetical)
analysis=AnalysisHandoff(
    skill="tapestry-synthesis",
    deliverable="Create a discussion synthesis highlighting key insights.",
    instructions="Focus on consensus points, disagreements, and valuable insights from comments."
)
```

## Benefits

### For Users
- ✓ Consistent quality across all content sources
- ✓ Better formatted output
- ✓ Easier to read and reference

### For Developers
- ✓ Single place to update quality standards
- ✓ Easier to add new crawlers
- ✓ Clear separation of concerns
- ✓ Less code duplication

### For the System
- ✓ Maintainable architecture
- ✓ Scalable to many content sources
- ✓ Quality improvements benefit all sources
- ✓ Consistent user experience

## Migration Path

When adding new crawlers:

1. **Don't** copy formatting instructions from other crawlers
2. **Do** specify only content-specific focus
3. **Trust** the synthesis skill to handle formatting

When updating quality standards:

1. **Don't** update individual crawlers
2. **Do** update `synthesis/SKILL.md`
3. **Benefit** from improvements across all sources

## Example: Adding a New Crawler

```python
# Bad (old approach)
analysis=AnalysisHandoff(
    instructions=(
        "Format with headers and lists.\n"
        "Add paragraph breaks.\n"
        "Remove navigation text.\n"
        "Focus on API documentation.\n"  # Only this is content-specific!
        "..."
    )
)

# Good (new approach)
analysis=AnalysisHandoff(
    instructions="Focus on API endpoints, parameters, and code examples."
)
# Formatting is handled by synthesis skill automatically
```

## Conclusion

By centralizing quality standards in the synthesis skill, we achieve:
- **Consistency**: All content gets the same quality treatment
- **Maintainability**: One place to update standards
- **Scalability**: Easy to add new content sources
- **Clarity**: Clear separation between content-specific and universal concerns

The synthesis skill becomes the **quality gate** that all content passes through, ensuring a consistent, high-quality knowledge base regardless of the source.
