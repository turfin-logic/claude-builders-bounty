#!/usr/bin/env python3
"""
Unit tests for Claude Code PR Reviewer
"""

import unittest
from claude_review import parse_pr_url, analyze_pr, format_review_markdown

class TestPRReviewer(unittest.TestCase):

    def test_parse_pr_url(self):
        owner, repo, pr = parse_pr_url("https://github.com/facebook/react/pull/12345")
        self.assertEqual(owner, "facebook")
        self.assertEqual(repo, "react")
        self.assertEqual(pr, "12345")

    def test_risk_detection(self):
        pr_data = {
            "title": "fix: update database config",
            "body": "Updates config settings",
            "changed_files": 2,
            "additions": 15,
            "deletions": 2
        }
        diff_with_secret = "+ const apiKey = 'sk_live_1234567890abcdef';"
        analysis = analyze_pr(pr_data, diff_with_secret)
        self.assertTrue(any("credential or secret" in r for r in analysis["risks"]))
        self.assertEqual(analysis["confidence"], "Low")

    def test_clean_pr_analysis(self):
        pr_data = {
            "title": "feat: add user settings page",
            "body": "Implements clean settings screen with comprehensive tests.",
            "changed_files": 3,
            "additions": 45,
            "deletions": 5
        }
        diff_clean = "+ import { render } from '@testing-library/react';\n+ describe('Settings', () => {});"
        analysis = analyze_pr(pr_data, diff_clean)
        self.assertEqual(analysis["confidence"], "High")

    def test_markdown_structure(self):
        analysis = {
            "summary": "This is a summary of changes.",
            "risks": ["Risk 1"],
            "suggestions": ["Suggestion 1"],
            "confidence": "High",
            "confidence_reason": "Clean code"
        }
        md = format_review_markdown(analysis, "10", "https://github.com/owner/repo/pull/10")
        self.assertIn("### 📌 Summary of Changes", md)
        self.assertIn("### ⚠️ Identified Risks", md)
        self.assertIn("### 💡 Improvement Suggestions", md)
        self.assertIn("### 🎯 Confidence Score", md)

if __name__ == '__main__':
    unittest.main()
