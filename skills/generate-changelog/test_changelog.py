#!/usr/bin/env python3
"""
Unit tests for the changelog generator categorizer
"""

import unittest
from generate_changelog import categorize_commits, build_changelog_markdown

class TestChangelogGenerator(unittest.TestCase):

    def test_categorization(self):
        sample_commits = [
            {'hash': 'a1b2c3d', 'msg': 'feat(auth): add OAuth login via GitHub'},
            {'hash': 'e4f5g6h', 'msg': 'fix: handle null token in session store'},
            {'hash': 'i7j8k9l', 'msg': 'refactor: streamline DB queries with Drizzle'},
            {'hash': 'm1n2o3p', 'msg': 'deprecate: remove legacy v1 REST endpoint'},
            {'hash': 'q4r5s6t', 'msg': 'chore: bump dependencies'}
        ]
        
        categories = categorize_commits(sample_commits)
        
        self.assertEqual(len(categories['Added']), 1)
        self.assertIn("OAuth login", categories['Added'][0])
        
        self.assertEqual(len(categories['Fixed']), 1)
        self.assertIn("null token", categories['Fixed'][0])
        
        self.assertEqual(len(categories['Removed']), 1)
        self.assertIn("legacy v1", categories['Removed'][0])
        
        self.assertEqual(len(categories['Changed']), 2)
        
    def test_markdown_formatting(self):
        categories = {
            'Added': ['- New feature (`1234567`)'],
            'Fixed': ['- Bug fix (`890abcd`)'],
            'Changed': [],
            'Removed': []
        }
        md = build_changelog_markdown(categories, version="v1.0.0")
        self.assertIn("## [v1.0.0]", md)
        self.assertIn("### Added", md)
        self.assertIn("- New feature (`1234567`)", md)
        self.assertIn("### Fixed", md)

if __name__ == '__main__':
    unittest.main()
