# Scripts

Utility scripts for the Tapestry project.

## convert_demo.sh

Convert asciinema `.cast` terminal recordings to animated GIF for use in documentation.

### Prerequisites

- [agg](https://github.com/asciinema/agg) - Asciinema GIF generator (will be auto-installed if missing)

### Usage

```bash
# Convert demo.cast to assets/demo.gif (default)
./scripts/convert_demo.sh

# Convert specific files
./scripts/convert_demo.sh my-recording.cast output.gif
```

### Recording a Demo

1. Install asciinema:
   ```bash
   # macOS
   brew install asciinema

   # Ubuntu/Debian
   apt install asciinema

   # Or use pip
   pip install asciinema
   ```

2. Record your terminal session:
   ```bash
   asciinema rec demo.cast
   # Perform your demo
   # Press Ctrl+D to stop recording
   ```

3. Convert to GIF:
   ```bash
   ./scripts/convert_demo.sh demo.cast assets/demo.gif
   ```

4. The GIF is now ready to use in the README!

### Tips for Good Demos

- Keep recordings short (30-90 seconds)
- Use a clean terminal with good contrast
- Set terminal size to 80x24 or 100x30 for consistency
- Add pauses between commands with `sleep 1`
- Use `clear` to reset the screen between sections
- Test the recording before converting: `asciinema play demo.cast`
