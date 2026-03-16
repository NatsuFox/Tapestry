# Tapestry Configuration

Default configuration for Tapestry. Users can override this by creating `tapestry.config.json` at the project root.

## Configuration File

`tapestry.config.json` - Default configuration with sensible defaults

## Customization

To customize configuration:

1. Copy this file to your project root:
   ```bash
   cp skills/tapestry/config/tapestry.config.json ./tapestry.config.json
   ```

2. Edit the copied file with your preferences

3. The project root config takes precedence over this default

## Configuration Options

See [Configuration Reference](../../docs/reference/configuration.md) for detailed documentation.

### Quick Reference

**Synthesis Modes**:
- `"auto"` (default): Synthesis runs after each ingest
- `"manual"`: Synthesis only when explicitly requested
- `"batch"`: Ingest multiple, synthesize all at once

**Example**:
```json
{
  "synthesis": {
    "mode": "manual"
  }
}
```
