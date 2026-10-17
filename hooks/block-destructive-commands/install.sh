#!/usr/bin/env bash
set -e

HOOKS_DIR="$HOME/.claude/hooks"
mkdir -p "$HOOKS_DIR"

SCRIPT_URL="https://raw.githubusercontent.com/claude-builders-bounty/claude-builders-bounty/main/hooks/block-destructive-commands/block_destructive_commands.py"
TARGET_FILE="$HOOKS_DIR/block_destructive_commands.py"

echo "Downloading block_destructive_commands hook..."
curl -fsSL "$SCRIPT_URL" -o "$TARGET_FILE"
chmod +x "$TARGET_FILE"

echo "✅ Hook installed to $TARGET_FILE"
echo "Add to your ~/.claude/settings.json under hooks.PreToolUse:"
echo '  "command": "python3 ~/.claude/hooks/block_destructive_commands.py"'
