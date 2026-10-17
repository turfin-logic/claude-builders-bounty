#!/usr/bin/env python3
"""
Structured CHANGELOG.md Generator from Git History
Fetches commits since the latest git tag (or from root commit if untagged),
categorizes them into Added, Fixed, Changed, Removed, and writes or updates CHANGELOG.md.
"""

import subprocess
import sys
import re
import os
from datetime import datetime

def run_git_command(args):
    """Runs a git command and returns its trimmed stdout."""
    try:
        res = subprocess.run(['git'] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return res.stdout.strip()
    except subprocess.CalledProcessError:
        return ""

def get_latest_tag():
    """Returns the latest git tag, or None if no tags exist."""
    tag = run_git_command(['describe', '--tags', '--abbrev=0'])
    return tag if tag else None

def get_commits_since(tag=None):
    """Fetches commit hashes and subjects since tag (or all if tag is None)."""
    rev_range = f"{tag}..HEAD" if tag else "HEAD"
    output = run_git_command(['log', rev_range, '--pretty=format:%h|%s'])
    if not output:
        return []
    commits = []
    for line in output.splitlines():
        if '|' in line:
            h, msg = line.split('|', 1)
            commits.append({'hash': h.strip(), 'msg': msg.strip()})
    return commits

def categorize_commits(commits):
    """Categorizes commits into Added, Fixed, Changed, Removed."""
    categories = {
        'Added': [],
        'Fixed': [],
        'Changed': [],
        'Removed': []
    }
    
    for c in commits:
        msg = c['msg']
        h = c['hash']
        entry = f"- {msg} (`{h}`)"
        
        # Categorization heuristics
        if re.match(r'^(feat|add|feature)(\(.*?\))?:\s*', msg, re.I):
            categories['Added'].append(entry)
        elif re.match(r'^(fix|bug|patch)(\(.*?\))?:\s*', msg, re.I):
            categories['Fixed'].append(entry)
        elif re.match(r'^(remove|deprecate|revert)(\(.*?\))?:\s*', msg, re.I):
            categories['Removed'].append(entry)
        elif re.match(r'^(refactor|perf|chore|style|docs|build|ci|test|update)(\(.*?\))?:\s*', msg, re.I):
            categories['Changed'].append(entry)
        else:
            # Fallback based on content keywords
            if any(w in msg.lower() for w in ['fix', 'bug', 'patch']):
                categories['Fixed'].append(entry)
            elif any(w in msg.lower() for w in ['add', 'new', 'create']):
                categories['Added'].append(entry)
            elif any(w in msg.lower() for w in ['remove', 'delete', 'deprecat']):
                categories['Removed'].append(entry)
            else:
                categories['Changed'].append(entry)
                
    return categories

def build_changelog_markdown(categories, version="Unreleased"):
    """Formats categorized commits into markdown format."""
    today = datetime.now().strftime("%Y-%m-%d")
    md = [f"## [{version}] - {today}\n"]
    
    has_content = False
    for cat in ['Added', 'Fixed', 'Changed', 'Removed']:
        items = categories.get(cat, [])
        if items:
            has_content = True
            md.append(f"### {cat}")
            md.extend(items)
            md.append("")
            
    if not has_content:
        md.append("_No user-facing changes documented._\n")
        
    return "\n".join(md)

def main():
    tag = get_latest_tag()
    commits = get_commits_since(tag)
    print(f"Inspecting git commits (Since tag: {tag or 'initial commit'})... Found {len(commits)} commits.")
    
    categories = categorize_commits(commits)
    content = build_changelog_markdown(categories, version="Unreleased" if not tag else f"vNext (after {tag})")
    
    changelog_path = "CHANGELOG.md"
    existing = ""
    if os.path.exists(changelog_path):
        with open(changelog_path, "r", encoding="utf-8") as f:
            existing = f.read()
            
    # Prepend new section if existing, otherwise write header
    if existing.strip():
        if "# Changelog" in existing:
            new_changelog = existing.replace("# Changelog\n", f"# Changelog\n\n{content}\n")
        else:
            new_changelog = f"# Changelog\n\n{content}\n\n{existing}"
    else:
        new_changelog = f"# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n{content}\n"
        
    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write(new_changelog)
        
    print(f"✅ Generated and updated {changelog_path}")
    print("\n--- Preview ---\n" + content)

if __name__ == "__main__":
    main()
