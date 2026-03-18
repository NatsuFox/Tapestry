# Visual Card Generation - Agent-Driven Approach

## Overview

This document describes the **Agent-driven** approach to generating visual cards, where the Agent intelligently analyzes content and makes decisions about what to include, rather than relying on rigid extraction rules.

## Two Approaches

### 1. Agent-Driven (Recommended for Quality)

**When to use**: When you want high-quality, thoughtfully curated cards

**Process**:
1. Prepare context from the chapter
2. Agent analyzes the content
3. Agent decides framework, insights, and narrative structure
4. Agent generates the final card

**Advantages**:
- Intelligent content selection
- Context-aware synthesis
- Better narrative flow
- Adapts to different content types

### 2. Automatic Extraction (Fast)

**When to use**: When you need quick batch generation

**Process**:
- Script automatically extracts patterns from markdown
- Uses heuristics to find frameworks and insights
- Generates cards immediately

**Advantages**:
- Fast batch processing
- No manual intervention
- Consistent output format

## Agent-Driven Workflow

### Step 1: Prepare Context

```bash
python skills/tapestry/visual-card/_scripts/generate_card_agent.py \
  --chapter "ai-and-development-tools/ai-agent-architecture.md" \
  --prepare-only
```

This creates a context JSON file with:
- Full chapter content
- Template requirements
- Design guidelines

### Step 2: Agent Synthesis

The Agent should analyze the context and decide:

**Framework (2-6 components)**:
- What are the core structural elements?
- What acronym would be memorable?
- How to describe each component concisely?

**Insights (3-4 items)**:
- What are the key takeaways?
- What would surprise or enlighten readers?
- What's actionable or thought-provoking?

**Key Points (Dark Panel)**:
- Block 1: What's the main conceptual foundation?
- Block 2: What's the practical application or implication?
- Conclusion: What's the memorable closing insight?

**Metadata**:
- Bilingual title (if applicable)
- Provocative thesis statement (2-3 lines)
- Topic and source labels

### Step 3: Generate Card

Once the Agent has synthesized the content, use the template to generate:

```bash
# Agent provides the synthesized content as JSON
python skills/tapestry/visual-card/_scripts/generate_card_from_synthesis.py \
  --synthesis-file "synthesis.json" \
  --output "data/cards"
```

## Template Structure

The visual card has these sections that need Agent decisions:

### 1. Top Bar
- **Topic Label**: Short category (e.g., "AI AGENT ARCHITECTURE")
- **Source Label**: Origin (e.g., "TAPESTRY")

### 2. Title Area
- **English Title**: Main title in English
- **Chinese Title**: Main title in Chinese (colored)
- **Thesis**: 2-3 line provocative statement with key phrase in `<strong>`

### 3. Framework Row (2-6 cards)
Each card needs:
- **Letter**: First character (for badge)
- **Name**: Short name (e.g., "模型")
- **Description**: 1-2 lines with `<strong>` keyword

### 4. Dark Panel (Left)
- **Section Title**: Main theme (e.g., "核心要点")
- **Block 1**: Title + 4 bullet points
- **Block 2**: Title + 4-5 bullet points
- **Conclusion**: Label + text with `<strong>` highlight

### 5. Light Panel (Right)
- **Section Title**: (e.g., "关键洞察")
- **3-4 Insights**: Each with title + description

### 6. Bottom Highlight Bar
- **Formula**: Framework acronym equation (e.g., "M × P × D × G = 完整理解")
- **Closing Thought**: Memorable final statement

### 7. Footer
- **Left**: Framework label
- **Right**: Brand name + framework + year

## Agent Decision Guidelines

### Content Selection Principles

1. **Prioritize Insight Over Information**
   - Choose surprising or counterintuitive points
   - Highlight what's actionable or transformative
   - Skip obvious or generic statements

2. **Create Narrative Flow**
   - Dark panel: Tell a story (problem → solution, before → after)
   - Light panel: Provide concrete takeaways
   - Conclusion: Tie it together with a memorable insight

3. **Match Source Language**
   - If source is Chinese, generate Chinese content
   - If source is English, generate English content
   - Always include bilingual titles

4. **Use Strong Formatting**
   - Bold key terms with `<strong>`
   - Keep descriptions concise (1-2 lines max)
   - Use active voice

### Framework Synthesis

**Good frameworks**:
- Capture the core structure of the content
- Have memorable acronyms (3-6 letters)
- Are mutually exclusive and collectively exhaustive
- Can be explained in 1-2 lines each

**Examples**:
- **D-T-O-E**: Data, Training, Optimization, Evaluation
- **M-P-D-G**: Model, Process, Data, Governance
- **L-I-T-S-M-C**: LLM, Identity, Tools, Sub-agents, Memory, Context

### Insight Extraction

**Good insights**:
- Challenge conventional thinking
- Provide actionable guidance
- Reveal hidden connections
- Are specific, not generic

**Bad insights**:
- "It's important to understand X" (too generic)
- "There are many approaches" (not actionable)
- "This is a complex topic" (obvious)

## Example: Agent Analysis Process

Given a chapter about "AI Agent Architecture":

**Agent thinks**:
1. "The core structure is: LLM foundation → Identity layer → Tool execution → Sub-agents → Memory → Context management"
2. "That's 6 components, acronym: LITSMC"
3. "Key insight: Agents have no innate identity - it's all injected via markdown files"
4. "Another insight: Every turn replays full history - agents aren't stateful processes"
5. "Dark panel block 1: Core mechanisms (LLM, identity, tools)"
6. "Dark panel block 2: Advanced features (sub-agents, memory, context)"
7. "Conclusion: Understanding the non-AI infrastructure is key to building effective agents"

**Agent outputs**:
```json
{
  "framework": [
    {"letter": "L", "name": "LLM Foundation", "description": "Token prediction..."},
    {"letter": "I", "name": "Identity Layer", "description": "Markdown files..."},
    ...
  ],
  "insights": [
    {"title": "Identity is Injected", "description": "Agents have no..."},
    ...
  ],
  ...
}
```

## Benefits of Agent-Driven Approach

1. **Quality**: Thoughtful content selection vs mechanical extraction
2. **Flexibility**: Adapts to different content types and structures
3. **Intelligence**: Understands context and makes smart decisions
4. **Creativity**: Can synthesize frameworks that don't exist in source

## When to Use Each Approach

**Use Agent-Driven when**:
- Creating showcase cards for important content
- Content has complex or non-standard structure
- You want maximum quality and insight
- You have time for Agent synthesis

**Use Automatic when**:
- Batch processing many cards
- Content follows standard patterns
- Speed is more important than perfection
- You want consistent formatting

## Next Steps

1. Try the Agent-driven approach on one chapter
2. Compare quality with automatic extraction
3. Decide which approach fits your workflow
4. Consider hybrid: automatic for bulk, Agent for highlights
