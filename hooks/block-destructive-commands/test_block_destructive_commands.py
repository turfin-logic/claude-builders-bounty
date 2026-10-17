#!/usr/bin/env python3
"""
Unit tests for block_destructive_commands.py
Verifies that all specified destructive patterns are blocked, safe commands are allowed,
and DELETE FROM with WHERE is permitted while DELETE FROM without WHERE is blocked.
"""

import unittest
import os
import shutil
import tempfile
from block_destructive_commands import inspect_command, log_blocked_attempt

class TestBlockDestructiveCommands(unittest.TestCase):

    def test_blocks_rm_rf(self):
        commands = [
            "rm -rf /",
            "rm -rf node_modules",
            "rm -fr build",
            "rm -r -f dist",
            "rm --recursive --force .git",
            "rm -rf /var/log/*"
        ]
        for cmd in commands:
            is_blocked, name = inspect_command(cmd, "/project")
            self.assertTrue(is_blocked, f"Should block '{cmd}'")

    def test_blocks_git_push_force(self):
        commands = [
            "git push origin main --force",
            "git push -f",
            "git push --force-with-lease origin branch",
            "git push origin head -f"
        ]
        for cmd in commands:
            is_blocked, name = inspect_command(cmd, "/project")
            self.assertTrue(is_blocked, f"Should block '{cmd}'")

    def test_blocks_drop_table(self):
        commands = [
            "psql -c 'DROP TABLE users;'",
            "mysql -e 'drop table accounts;'",
            "sqlite3 app.db 'DROP TABLE sessions'"
        ]
        for cmd in commands:
            is_blocked, name = inspect_command(cmd, "/project")
            self.assertTrue(is_blocked, f"Should block '{cmd}'")

    def test_blocks_truncate(self):
        commands = [
            "psql -c 'TRUNCATE TABLE logs;'",
            "TRUNCATE orders;",
            "sqlite3 db 'truncate users'"
        ]
        for cmd in commands:
            is_blocked, name = inspect_command(cmd, "/project")
            self.assertTrue(is_blocked, f"Should block '{cmd}'")

    def test_delete_from_without_where(self):
        destructive = [
            "DELETE FROM users;",
            "delete from accounts",
            "psql -c 'DELETE FROM logs;'"
        ]
        for cmd in destructive:
            is_blocked, name = inspect_command(cmd, "/project")
            self.assertTrue(is_blocked, f"Should block '{cmd}' without WHERE")

    def test_allows_delete_from_with_where(self):
        safe_sql = [
            "DELETE FROM users WHERE id = 123;",
            "delete from sessions where expired_at < NOW()",
            "DELETE FROM cache WHERE key = 'test'"
        ]
        for cmd in safe_sql:
            is_blocked, name = inspect_command(cmd, "/project")
            self.assertFalse(is_blocked, f"Should allow '{cmd}' with WHERE clause")

    def test_allows_normal_commands(self):
        normal_commands = [
            "git status",
            "git push origin feature-branch",
            "npm run test",
            "python -m pytest",
            "cat README.md",
            "mkdir -p src/components",
            "ls -la"
        ]
        for cmd in normal_commands:
            is_blocked, name = inspect_command(cmd, "/project")
            self.assertFalse(is_blocked, f"Should allow normal command: '{cmd}'")

    def test_logging(self):
        hooks_dir = os.path.expanduser("~/.claude/hooks")
        log_file = os.path.join(hooks_dir, "blocked.log")
        log_blocked_attempt("rm -rf test_dir", "Recursive forced deletion", "/test/project")
        self.assertTrue(os.path.exists(log_file), "Log file should exist")
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("rm -rf test_dir", content)
            self.assertIn("/test/project", content)

if __name__ == "__main__":
    unittest.main()
