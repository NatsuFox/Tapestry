# Tapestry Configuration

Configuration for Tapestry. Users can customize by creating their own `tapestry.config.json`.

## Configuration Files

- `tapestry.config.example.json` - Example configuration template (tracked in git)
- `tapestry.config.json` - User configuration (ignored by git)

## Customization

To customize configuration:

1. Copy the example file:
   ```bash
   cp skills/tapestry/config/tapestry.config.example.json skills/tapestry/config/tapestry.config.json
   ```

2. Edit `tapestry.config.json` with your preferences

3. Your config is automatically ignored by git (won't be committed)

## Configuration Options

See [Configuration Reference](../../docs/reference/configuration.md) for detailed documentation.

### Quick Reference

**Synthesis Modes**:
- `"auto"` (default): Agent evaluates and decides when to merge
- `"manual"`: Synthesis only when explicitly requested
- `"batch"`: Ingest multiple, synthesize all at once
- `"deterministic"`: Force merge after every ingest (high overhead)

**Example**:
```json
{
  "synthesis": {
    "mode": "manual"
  }
}
```
