#!/usr/bin/env python3
"""
Claude Code PreToolUse Hook: Block Destructive Bash Commands
Intercepts dangerous bash commands (rm -rf, DROP TABLE, git push --force, TRUNCATE, DELETE FROM without WHERE)
before execution, logs attempts to ~/.claude/hooks/blocked.log, and exits with code 2 to halt tool execution.
"""

import sys
import json
import re
import os
from datetime import datetime

# Blocked command patterns with explanations
BLOCKED_PATTERNS = [
    {
        "pattern": r"\brm\b(?:(?=.*\s-[a-zA-Z]*r)(?=.*\s-[a-zA-Z]*f)|(?=.*\s--recursive)(?=.*\s--force)|\s+-[a-zA-Z]*rf[a-zA-Z]*|\s+-[a-zA-Z]*fr[a-zA-Z]*)",
        "name": "Recursive forced deletion (rm -rf)",
        "reason": "Destructive file deletion can permanently destroy files or entire projects."
    },
    {
        "pattern": r"\bgit\s+push\b.*(--force|-f\b|--force-with-lease)",
        "name": "Forced git push (git push --force)",
        "reason": "Force pushing can overwrite remote repository history and erase colleagues' commits."
    },
    {
        "pattern": r"\bDROP\s+TABLE\b",
        "name": "Database DROP TABLE",
        "reason": "Dropping a database table permanently deletes schemas and all stored data."
    },
    {
        "pattern": r"\bTRUNCATE\b(\s+TABLE)?",
        "name": "Database TRUNCATE",
        "reason": "Truncating a table irrevocably wipes all rows from the database."
    },
    {
        "pattern": r"\bDELETE\s+FROM\b",
        "name": "Database DELETE FROM without WHERE clause",
        "reason": "Executing DELETE FROM without a WHERE clause wipes every record in the table.",
        "validator": lambda cmd: not bool(re.search(r"\bWHERE\b", cmd, re.IGNORECASE))
    }
]

def log_blocked_attempt(command, reason, project_path):
    """Logs the blocked command attempt to ~/.claude/hooks/blocked.log"""
    hooks_dir = os.path.expanduser("~/.claude/hooks")
    os.makedirs(hooks_dir, exist_ok=True)
    log_file = os.path.join(hooks_dir, "blocked.log")
    
    timestamp = datetime.now().isoformat()
    log_entry = (
        f"[{timestamp}] BLOCKED: {reason}\n"
        f"  Command: {command}\n"
        f"  Project: {project_path}\n"
        f"--------------------------------------------------\n"
    )
    
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"[Warning] Failed to write to blocked.log: {e}", file=sys.stderr)

def inspect_command(command, project_path):
    """
    Checks if a command contains any destructive patterns.
    Returns (is_blocked: bool, reason: str)
    """
    if not command or not isinstance(command, str):
        return False, ""

    for item in BLOCKED_PATTERNS:
        match = re.search(item["pattern"], command, re.IGNORECASE)
        if match:
            # Check custom validator if present (e.g. for DELETE FROM without WHERE)
            validator = item.get("validator")
            if validator and not validator(command):
                continue
                
            return True, item["name"]

    return False, ""

def main():
    # 1. Read JSON payload from stdin passed by Claude Code
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            sys.exit(0)
        data = json.loads(raw_input)
    except Exception:
        # If payload cannot be parsed as JSON, fail open to avoid breaking workflow
        sys.exit(0)

    # 2. Extract tool name and command
    tool_name = data.get("tool_name") or data.get("tool")
    tool_input = data.get("tool_input") or data.get("input") or {}
    project_path = data.get("cwd") or os.getcwd()

    # Only inspect Bash commands
    if tool_name not in ("Bash", "bash", "execute_command"):
        sys.exit(0)

    command = tool_input.get("command") or tool_input.get("CommandLine") or ""

    # 3. Check for destructive patterns
    is_blocked, blocked_name = inspect_command(command, project_path)

    if is_blocked:
        # Log blocked attempt
        log_blocked_attempt(command, blocked_name, project_path)

        # Output clear explanation to Claude on stderr
        error_msg = (
            f"\n[SECURITY HOOK BLOCKED COMMAND]\n"
            f"Action: Blocked '{blocked_name}'\n"
            f"Command: {command}\n"
            f"Reason: This command matches a destructive pattern and was stopped to protect your project.\n"
            f"Logged to: ~/.claude/hooks/blocked.log\n"
        )
        print(error_msg, file=sys.stderr)

        # In Claude Code, exit code 2 immediately halts tool execution!
        sys.exit(2)

    # Allow command to proceed
    sys.exit(0)

if __name__ == "__main__":
    main()
