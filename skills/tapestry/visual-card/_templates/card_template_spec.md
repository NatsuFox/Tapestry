# Visual Card Template Specification

This document describes how to map knowledge base content to the visual card template blocks. The Agent should read this specification and autonomously decide how to fill each template block based on the source content.

## Template Structure

The visual card has **7 fixed display blocks** arranged in a poster layout (1200px wide):

```
┌──────────────────────────────────────────┐
│ [1] TOP BAR                              │
├────────────────────┬─────────────────────┤
│ [2] TITLE AREA     │ [2] THESIS          │
├─────┬─────┬─────┬──┴──────────────────────┤
│ [3] FRAMEWORK ROW (2-6 cards)            │
├─────────────────────┬───────────────────┤
│ [4] DARK PANEL     │ [5] LIGHT PANEL    │
├──────────────────────────────────────────┤
│ [6] BOTTOM HIGHLIGHT BAR                 │
├──────────────────────────────────────────┤
│ [7] FOOTER                               │
└──────────────────────────────────────────┘
```

## Block 1: Top Bar

**Purpose**: Provide context labels for the card

**What to fill**:
- **Left label**: Topic category in uppercase (e.g., "AI AGENT ARCHITECTURE", "MARKET ANALYSIS")
  - Extract from: Directory name or main topic
  - Format: ALL CAPS, use spaces not hyphens

- **Right label**: Source attribution (e.g., "TAPESTRY", "RESEARCH PAPER", "BLOG POST")
  - Extract from: Frontmatter `source` field or use "TAPESTRY" as default
  - Format: ALL CAPS, short (1-3 words)

**Agent decision**: Choose labels that provide immediate context about what this card covers and where it came from.

## Block 2: Title Area

**Purpose**: Bilingual title and provocative thesis statement

**What to fill**:
- **English Title**: Main title in English (38px Playfair Display)
  - Extract from: First `#` heading if English, or translate if Chinese
  - Style: Title case, concise (3-8 words)

- **Chinese Title**: Main title in Chinese (40px Noto Sans SC, colored teal)
  - Extract from: First `#` heading if Chinese, or translate if English
  - Style: Concise (4-12 characters)

- **Thesis Statement**: 2-3 line provocative claim (right side, 14.5px)
  - Create from: Article's core argument or main insight
  - Style: Strong, opinionated, with one `<strong>` keyword
  - Example: "Agent 的智能上限完全由底层 LLM 决定，而基础设施负责<strong>将被动响应转化为主动执行</strong>"

**Agent decision**:
- Detect the primary language of the content
- Write thesis that captures the **most provocative or counterintuitive** insight
- Choose a keyword to emphasize that challenges conventional thinking

## Block 3: Framework Row

**Purpose**: Visual framework showing 2-6 core components

**What to fill**: 2-6 component cards, each with:
- **Letter badge**: First character of component name (colored square)
- **Name**: Short component name (2-4 characters Chinese, 1-2 words English)
- **Description**: 1-2 line explanation with `<strong>` keyword

**How to extract**:
1. **Look for explicit frameworks**: Numbered lists with bold headers like:
   ```
   1. **Component Name**: Description...
   2. **Component Name**: Description...
   ```

2. **Synthesize from structure**: If no explicit framework, analyze the content structure:
   - What are the main sections/themes?
   - Can they be organized into 2-6 logical components?
   - Create a memorable acronym from the first letters

3. **Framework quality criteria**:
   - Components should be mutually exclusive and collectively exhaustive
   - Acronym should be memorable (e.g., LITSMC, DOTE, MPFG)
   - Each description should highlight one key aspect with `<strong>`

**Agent decision**:
- Choose between 2-6 components based on content complexity
- Prefer extracting existing frameworks over synthesizing new ones
- If synthesizing, ensure the framework genuinely captures the content structure
- Create an acronym that's easy to remember

## Block 4: Dark Panel (Left Column)

**Purpose**: Narrative content with structured bullet points

**What to fill**:
- **Section Title**: Main theme (e.g., "核心要点", "架构基础", "Core Mechanisms")
- **Icon**: Emoji that represents the theme (⚡, 🔥, 🛠, 💡, 🎯)
- **Block 1**: Title + 4 bullet points
- **Block 2**: Title + 4-5 bullet points
- **Conclusion**: Label + text with `<strong>` highlight

**How to extract**:
1. **Block 1 - Foundation/Concepts**:
   - Use the first major section or theme
   - Extract 4 key points that establish the foundation
   - Focus on "what it is" and "why it matters"

2. **Block 2 - Application/Advanced**:
   - Use the second major section or theme
   - Extract 4-5 key points about application or advanced concepts
   - Focus on "how it works" and "what to watch out for"

3. **Conclusion**:
   - Extract or synthesize a memorable closing insight
   - Highlight the most important takeaway with `<strong>`

**Agent decision**:
- Choose sections that tell a story: foundation → application, or problem → solution
- Bullet points should be specific, not generic
- Conclusion should tie everything together with a memorable phrase

## Block 5: Light Panel (Right Column)

**Purpose**: Numbered insights or key takeaways

**What to fill**: 3-4 numbered insight items, each with:
- **Number**: Large serif number (1-4)
- **Title**: Bold statement (1 line, provocative)
- **Description**: 1-2 line explanation with `<strong>` keyword

**How to extract**:
1. **Look for explicit insights**: Sections titled "Key Insights", "Takeaways", "Important Points"

2. **Extract from content**: Find the most valuable/surprising points:
   - Counterintuitive findings
   - Practical warnings or tips
   - Hidden connections or patterns
   - Actionable recommendations

3. **Insight quality criteria**:
   - Should challenge assumptions or reveal non-obvious truths
   - Avoid generic statements like "It's important to understand X"
   - Prefer specific, memorable claims

**Agent decision**:
- Choose 3-4 insights that would surprise or enlighten readers
- Prioritize actionable or thought-provoking content
- Each insight should stand alone (not depend on others)

## Block 6: Bottom Highlight Bar

**Purpose**: Formula-style summary and closing thought

**What to fill**:
- **Formula** (left): Framework acronym as equation
  - Format: "ACRONYM Framework" or "Component × Component × ... = Outcome"
  - Example: "LITSMC = 完整 Agent 架构" or "M × P × D × G = 完整理解"

- **Closing Thought** (right): Final memorable statement
  - Extract from: Conclusion section or synthesize
  - Style: Concise (1 sentence), philosophical or practical

**Agent decision**:
- Create a formula that's visually appealing and meaningful
- Closing thought should leave a lasting impression

## Block 7: Footer

**Purpose**: Framework label and branding

**What to fill**:
- **Left**: Framework reference (e.g., "tapestry.knowledge-base")
- **Right**: Brand + Framework + Year (e.g., "TAPESTRY • LITSMC FRAMEWORK • 2026")

**Agent decision**: Use consistent branding, incorporate the framework acronym

---

## Content Analysis Workflow

When the Agent receives a knowledge base chapter, follow this process:

### Step 1: Initial Analysis
- Read the full content
- Identify the primary language (Chinese/English)
- Detect the content type (technical, conceptual, practical, theoretical)
- Identify explicit structures (numbered lists, sections, frameworks)

### Step 2: Block Mapping
For each template block (1-7):
- Read the block specification above
- Analyze what content best fits that block's purpose
- Make decisions based on the quality criteria
- Extract or synthesize content as needed

### Step 3: Quality Check
- Does the framework genuinely represent the content structure?
- Are the insights provocative and valuable (not generic)?
- Does the dark panel tell a coherent story?
- Is the thesis statement strong and opinionated?
- Are all `<strong>` tags used to highlight key terms?

### Step 4: Language Consistency
- Match the source content language
- Bilingual titles always (English + Chinese)
- Technical terms stay in original language
- Framework acronyms use original letters

---

## Examples of Good vs Bad Decisions

### Framework Extraction

**Good**:
- LITSMC (LLM, Identity, Tools, Sub-agents, Memory, Compression) - captures actual architecture layers
- DOTE (Data, Optimization, Training, Evaluation) - represents real workflow stages

**Bad**:
- ABCD (Aspect, Benefit, Challenge, Direction) - generic, doesn't reflect actual content
- Forcing 4 components when content naturally has 6 distinct parts

### Insights

**Good**:
- "身份是注入的，非天生的" - counterintuitive, challenges assumptions
- "'说了但没做'陷阱" - practical warning with memorable phrasing

**Bad**:
- "理解这个概念很重要" - generic, obvious
- "有很多不同的方法" - vague, not actionable

### Dark Panel Story

**Good**:
- Block 1: Foundation concepts (what/why)
- Block 2: Advanced applications (how/watch-out)
- Flows from basic to advanced

**Bad**:
- Block 1: Random collection of points
- Block 2: Unrelated points
- No narrative progression

---

## Agent Autonomy

The Agent should:
- **Make intelligent decisions** based on content analysis, not rigid rules
- **Adapt to different content types** (technical papers, blog posts, tutorials)
- **Prioritize quality over completeness** (better to have 3 great insights than 4 mediocre ones)
- **Synthesize when needed** (create frameworks if none exist, but only if they genuinely fit)
- **Maintain consistency** (same language, same style, same level of detail across blocks)

The Agent should NOT:
- Mechanically extract patterns without understanding context
- Force content into blocks where it doesn't fit
- Use generic placeholders when specific content is available
- Ignore the narrative flow between blocks
- Create frameworks that don't reflect actual content structure
