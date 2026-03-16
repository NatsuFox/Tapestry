# Tapestry Skill Architecture

## Design Philosophy

Tapestry uses a **single main skill with internal sub-skills** pattern. This provides:

- ✅ **Single entry point**: Users invoke `/tapestry`
- ✅ **Framework-agnostic**: Works with any Agent Skills-compatible framework
- ✅ **Internal orchestration**: The main skill reads sub-skill instructions and executes them
- ✅ **Clean organization**: Sub-skills are organized in subdirectories
- ✅ **No complex nesting**: Simple, flat structure that agents can understand

## Structure

```
skills/tapestry/
├── SKILL.md                    # Main orchestrator skill
├── ingest/SKILL.md             # Sub-skill: URL crawling
├── feed/SKILL.md               # Sub-skill: Structured feeds
├── synthesis/SKILL.md          # Sub-skill: AI analysis
├── display/SKILL.md            # Sub-skill: Visualization
├── _src/                       # Shared code library
└── _tests/                     # Unit tests
```

## How It Works

### 1. User Invokes Main Skill

```
User: "Ingest this Zhihu answer: https://..."
Agent: Loads /tapestry skill
```

### 2. Main Skill Analyzes Intent

The main `SKILL.md` contains logic to:
- Understand what the user wants
- Determine which sub-skill(s) to use
- Read the appropriate sub-skill SKILL.md files
- Execute the workflow described in those files

### 3. Sub-Skills Are Executed

The main skill reads sub-skill instructions:

```bash
# Main skill reads the sub-skill instructions
cat ingest/SKILL.md

# Then executes according to those instructions
python ingest/_scripts/run.py "$ARGUMENTS"
```

### 4. Sub-Skills Can Chain

Sub-skills reference each other:
- `ingest/SKILL.md` says "route to `$tapestry-feed`" or "`$tapestry-synthesis`"
- The main skill reads those referenced sub-skills and continues the workflow

## Key Principles

1. **Main skill is the orchestrator**: It doesn't do the work itself, it reads sub-skill instructions and follows them
2. **Sub-skills are documentation**: They describe workflows that the main skill executes
3. **Shared code is reusable**: All sub-skills use `_src/` for common functionality
4. **Progressive disclosure**: Main skill only loads sub-skill details when needed

## Benefits

### For Users
- Single command: `/tapestry <url>` handles everything
- Clear intent: The main skill figures out what to do
- Flexible: Can request specific sub-workflows if needed

### For Developers
- Modular: Each sub-skill is independently documented
- Maintainable: Changes to one sub-skill don't affect others
- Testable: Shared code has a single test suite

### For Frameworks
- Standards-compliant: Follows Agent Skills specification
- Portable: Works across all compatible frameworks
- Simple: No complex nesting or plugin systems required

## Comparison with Previous Approaches

### ❌ Flat Namespace (tapestry-ingest, tapestry-feed, etc.)
- Required users to know which sub-skill to invoke
- Agent had to discover and choose between multiple skills
- More complex for users

### ❌ Plugin System
- Framework-specific (Claude Code only)
- Not portable to other agent frameworks
- Added unnecessary complexity

### ✅ Main Skill with Internal Sub-Skills
- Single entry point for users
- Framework-agnostic
- Agent orchestrates internally
- Clean and simple

## Installation

Users install the entire bundle:

```bash
# Copy the entire tapestry directory
cp -r skills/tapestry ~/.claude/skills/

# Or symlink for development
ln -s "$(pwd)/skills/tapestry" ~/.claude/skills/tapestry
```

## Usage Examples

### Simple Invocation
```
/tapestry https://www.zhihu.com/question/123/answer/456
```

The main skill:
1. Recognizes this is a URL to ingest
2. Reads `ingest/SKILL.md`
3. Executes the ingest workflow
4. Reports results

### Complex Workflow
```
/tapestry Analyze these HN discussions and organize into my KB:
https://news.ycombinator.com/item?id=123
https://news.ycombinator.com/item?id=456
```

The main skill:
1. Recognizes multiple URLs + analysis request
2. Reads `ingest/SKILL.md` and processes all URLs
3. Reads `synthesis/SKILL.md` and organizes content
4. Reports where content was placed in the knowledge base

## Conclusion

This architecture achieves the best balance:
- **Simple for users**: One command does everything
- **Clear for agents**: Main skill provides orchestration logic
- **Portable**: Works across all frameworks
- **Maintainable**: Modular sub-skills with shared code

The main skill acts as an intelligent router that reads sub-skill documentation and executes the appropriate workflows based on user intent.
