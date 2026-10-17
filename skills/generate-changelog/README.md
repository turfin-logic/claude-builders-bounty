# 📝 Structured Git Changelog Generator (Claude Code Skill)

A fast, automated changelog generator that inspects git history since the latest tag, categorizes commits into standard sections (**Added**, **Fixed**, **Changed**, **Removed**), and outputs a clean `CHANGELOG.md`.

## ⚡ Setup in 3 Steps or Fewer

1. **Clone or Copy** the `skills/generate-changelog` folder into your project or Claude Code skills directory (`~/.claude/skills/generate-changelog`).
2. **Make executable**:
   ```bash
   chmod +x skills/generate-changelog/generate_changelog.py skills/generate-changelog/changelog.sh
   ```
3. **Run in any git repository**:
   ```bash
   bash skills/generate-changelog/changelog.sh
   # Or directly with Python:
   python3 skills/generate-changelog/generate_changelog.py
   ```

---

## 🧪 Testing

Run the automated test suite:
```bash
python3 skills/generate-changelog/test_changelog.py
```

---

## 📄 Real Sample Output (`CHANGELOG.md`)

```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [v1.2.0] - 2026-10-17

### Added
- feat(auth): add OAuth login via GitHub (`a1b2c3d`)
- feat(billing): integrate Stripe webhook idempotency keys (`f2e4d6a`)

### Fixed
- fix: handle null token in session store (`e4f5g6h`)
- fix(ui): prevent button overflow on mobile viewport (`b7c8d9e`)

### Changed
- refactor: streamline DB queries with Drizzle ORM (`i7j8k9l`)
- chore: bump dependencies to React 19 (`q4r5s6t`)

### Removed
- deprecate: remove legacy v1 REST endpoint (`m1n2o3p`)
```
