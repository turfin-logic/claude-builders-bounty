---
name: generate-changelog
description: Automatically inspects git commits since the last tag and generates a structured CHANGELOG.md categorized by Added, Fixed, Changed, and Removed.
---

# Generate Changelog Skill

Use this skill when the user asks to generate, update, or preview release notes or `CHANGELOG.md` from recent git commits.

## Usage
Run directly:
```bash
python3 skills/generate-changelog/generate_changelog.py
```
Or via shell:
```bash
bash skills/generate-changelog/changelog.sh
```

## Categorization Logic
- **Added**: Commits starting with `feat:`, `feat(...)`, `add`, `new`
- **Fixed**: Commits starting with `fix:`, `fix(...)`, `bug`, `patch`
- **Changed**: Commits starting with `refactor:`, `perf:`, `style:`, `chore:`, `update`
- **Removed**: Commits starting with `revert:`, `deprecate:`, `remove`, `drop`
