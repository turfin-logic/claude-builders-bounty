# 🛡️ Claude Code PreToolUse Hook: Block Destructive Bash Commands

A production-ready security hook for [Claude Code](https://docs.anthropic.com/claude-code) that intercepts dangerous commands before execution, preventing accidental data loss and catastrophic overwrites.

## 🛑 Protected Patterns

This hook intercepts and blocks:
- **`rm -rf`** / `rm -fr` / `rm -r -f` (recursive forced deletion)
- **`git push --force`** / `git push -f` / `git push --force-with-lease`
- **`DROP TABLE`** (database table drops)
- **`TRUNCATE`** / `TRUNCATE TABLE` (database truncation)
- **`DELETE FROM`** without a `WHERE` clause (unfiltered table wipes; `DELETE FROM ... WHERE ...` is safely allowed)

Every blocked attempt is immediately logged to `~/.claude/hooks/blocked.log` with timestamp, command, and project directory. Claude receives a clear explanation on `stderr`, and tool execution is halted with exit code `2`.

---

## ⚡ Quick Install (2 Commands or Fewer)

Run in your terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/claude-builders-bounty/claude-builders-bounty/main/hooks/block-destructive-commands/install.sh | bash
```

Or manually:

```bash
mkdir -p ~/.claude/hooks
curl -fsSL -o ~/.claude/hooks/block_destructive_commands.py https://raw.githubusercontent.com/claude-builders-bounty/claude-builders-bounty/main/hooks/block-destructive-commands/block_destructive_commands.py
chmod +x ~/.claude/hooks/block_destructive_commands.py
```

Then add to your `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/block_destructive_commands.py",
            "timeout": 15
          }
        ]
      }
    ]
  }
}
```

---

## 🧪 Testing & Verification

Run the comprehensive unit test suite:

```bash
python3 test_block_destructive_commands.py
```

### Manual Test

You can pipe mock Claude Code payload into the script:

```bash
# Test blocked command (exits with code 2)
echo '{"tool_name": "Bash", "tool_input": {"command": "rm -rf /tmp/test"}, "cwd": "/home/user"}' | python3 block_destructive_commands.py
echo "Exit code: $?"

# Test safe command (exits with code 0)
echo '{"tool_name": "Bash", "tool_input": {"command": "git status"}, "cwd": "/home/user"}' | python3 block_destructive_commands.py
echo "Exit code: $?"
```

---

## 📜 Log Format (`~/.claude/hooks/blocked.log`)

```text
[2026-10-17T11:52:05.123456] BLOCKED: Recursive forced deletion (rm -rf)
  Command: rm -rf node_modules
  Project: /Users/dev/my-project
--------------------------------------------------
```

## 📄 License
MIT
