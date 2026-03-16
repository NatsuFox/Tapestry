# Knowledge Base

A simple, flexible knowledge base structure. The agent can easily create new topics and chapters as needed.

## Topics

This knowledge base starts empty. Topics will be created as content is synthesized.

## How to Use

When synthesizing content, the agent will:
1. Analyze the content's subject matter
2. Create appropriate topics if they don't exist
3. Organize content into chapters within topics
4. Maintain this index with links to all topics

## Creating Topics

Topics should be:
- **Broad enough** to contain multiple related pieces of content
- **Specific enough** to be meaningful and searchable
- **Named clearly** using lowercase-with-hyphens (e.g., `machine-learning`, `web-development`)

## Example Structure

After synthesizing some content, this might look like:

```
- [Machine Learning](machine-learning/index.md)
  neural networks, training techniques, and ML research
- [Web Development](web-development/index.md)
  frontend, backend, and full-stack development topics
- [General](general/index.md)
  miscellaneous content that doesn't fit other topics
```

## Maintenance

- Keep this index updated when creating new topics
- Merge similar topics if they overlap too much
- Split topics if they become too broad
