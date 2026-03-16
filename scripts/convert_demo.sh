#!/bin/bash
# Convert asciinema cast file to animated GIF
# Usage: ./scripts/convert_demo.sh [input.cast] [output.gif]

set -e

INPUT="${1:-demo.cast}"
OUTPUT="${2:-assets/demo.gif}"

if [ ! -f "$INPUT" ]; then
    echo "Error: Input file '$INPUT' not found"
    echo "Usage: $0 [input.cast] [output.gif]"
    exit 1
fi

# Check if agg is installed
if ! command -v agg &> /dev/null; then
    echo "Installing agg (asciinema gif generator)..."
    cargo install --git https://github.com/asciinema/agg
fi

echo "Converting $INPUT to $OUTPUT..."
agg --theme monokai "$INPUT" "$OUTPUT"

echo "✓ Conversion complete: $OUTPUT"
echo ""
echo "To use in README:"
echo "  <img src=\"$OUTPUT\" width=\"90%\" alt=\"Tapestry Demo\" />"
