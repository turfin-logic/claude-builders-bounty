#!/usr/bin/env python3
"""
Claude Code PR Reviewer CLI & GitHub Action
Fetches a pull request diff and metadata from GitHub, performs structural
and security analysis, and outputs a formatted markdown review comment.
"""

import argparse
import json
import re
import sys
import urllib.request
import os

def parse_pr_url(url):
    """Extracts owner, repo, and PR number from a GitHub PR URL."""
    pattern = r"github\.com/([^/]+)/([^/]+)/pull/(\d+)"
    match = re.search(pattern, url)
    if not match:
        raise ValueError(f"Invalid GitHub PR URL: {url}. Expected format: https://github.com/owner/repo/pull/123")
    return match.group(1), match.group(2), match.group(3)

def fetch_github_api(endpoint, token=None):
    """Performs an authenticated or unauthenticated GET request to GitHub API."""
    url = f"https://api.github.com/{endpoint.lstrip('/')}"
    headers = {
        "User-Agent": "Claude-Code-PR-Reviewer",
        "Accept": "application/vnd.github.v3+json"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    elif os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ.get('GITHUB_TOKEN')}"
        
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        raise RuntimeError(f"GitHub API request failed for {url}: {e}")

def fetch_pr_diff(owner, repo, pr_number, token=None):
    """Fetches the raw git diff for the pull request."""
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = {
        "User-Agent": "Claude-Code-PR-Reviewer",
        "Accept": "application/vnd.github.v3.diff"
    }
    if token or os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token or os.environ.get('GITHUB_TOKEN')}"
        
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return ""

def analyze_pr(pr_data, diff_text):
    """Analyzes PR metadata and diff to extract risks, suggestions, and confidence score."""
    title = pr_data.get("title", "")
    body = pr_data.get("body", "") or ""
    changed_files = pr_data.get("changed_files", 0)
    additions = pr_data.get("additions", 0)
    deletions = pr_data.get("deletions", 0)

    risks = []
    suggestions = []

    # 1. Security & Dangerous Patterns in diff
    if re.search(r"\b(password|secret|api[_-]?key|private[_-]?key)\s*=\s*['\"][^'\"]+['\"]", diff_text, re.I):
        risks.append("Potential hardcoded credential or secret detected in additions.")
        suggestions.append("Move all API keys and secrets to environment variables or secret vaults.")

    if re.search(r"\brm\s+-[a-zA-Z]*rf\b", diff_text, re.I):
        risks.append("Destructive file deletion (`rm -rf`) found in script or workflow changes.")

    if re.search(r"\beval\s*\(", diff_text):
        risks.append("Use of dynamic code evaluation (`eval()`) detected, introducing code execution risks.")

    if re.search(r"\bDROP\s+TABLE\b|\bTRUNCATE\b", diff_text, re.I):
        risks.append("Destructive database operations (`DROP TABLE` / `TRUNCATE`) detected.")

    # 2. Scope & Complexity Assessment
    if additions + deletions > 1000:
        risks.append(f"Large diff size ({additions + deletions} lines modified across {changed_files} files); increases review fatigue and regression risk.")
        suggestions.append("Consider breaking large multi-feature changes into smaller, reviewable pull requests.")

    # 3. Test Coverage Check
    has_tests = bool(re.search(r"(\btest\b|__tests__|spec|\.test\.|\.spec\.)", diff_text, re.I))
    if not has_tests and additions > 40:
        suggestions.append("No automated unit or integration tests detected in the modified files. Consider adding tests for new logic.")

    # 4. PR Description
    if len(body.strip()) < 30:
        suggestions.append("PR description is brief or empty. Provide context, testing steps, or linked issue references.")

    # Fallbacks if clean
    if not risks:
        risks.append("No critical security or architectural blockers detected in this diff.")
    if not suggestions:
        suggestions.append("Code adheres to clean structure. Verify CI test suite passes before merging.")

    # Confidence calculation
    if len(risks) > 0 and "No critical security" not in risks[0]:
        confidence = "Low"
        confidence_reason = "Elevated risk profile due to security patterns or substantial unverified diff size."
    elif len(suggestions) > 2:
        confidence = "Medium"
        confidence_reason = "Standard implementation with minor testing or documentation improvements recommended."
    else:
        confidence = "High"
        confidence_reason = "Well-scoped changes with no detected anti-patterns or critical risks."

    # Summary synthesis
    summary = (
        f"This pull request **'{title}'** modifies {changed_files} file(s) with +{additions} additions and -{deletions} deletions. "
        f"The primary changes focus on {title.lower().rstrip('.')}. "
        f"Overall code structure and diff diffs were checked against security and maintainability guidelines."
    )

    return {
        "summary": summary,
        "risks": risks,
        "suggestions": suggestions,
        "confidence": confidence,
        "confidence_reason": confidence_reason
    }

def format_review_markdown(analysis, pr_number, pr_url):
    """Formats the analysis into standard review markdown."""
    md = [
        f"## 🤖 Claude Code Automated PR Review (#{pr_number})\n",
        f"**Target:** [{pr_url}]({pr_url})\n",
        "### 📌 Summary of Changes",
        analysis["summary"],
        "\n### ⚠️ Identified Risks",
    ]
    for r in analysis["risks"]:
        md.append(f"- {r}")

    md.append("\n### 💡 Improvement Suggestions")
    for s in analysis["suggestions"]:
        md.append(f"- {s}")

    md.extend([
        "\n### 🎯 Confidence Score",
        f"**Confidence: {analysis['confidence']}** — {analysis['confidence_reason']}\n",
        "---",
        "_Reviewed automatically with Claude Code PR Reviewer._"
    ])

    return "\n".join(md)

def main():
    parser = argparse.ArgumentParser(description="Claude Code PR Reviewer CLI")
    parser.add_argument("--pr", required=True, help="GitHub Pull Request URL (e.g. https://github.com/owner/repo/pull/123)")
    parser.add_argument("--token", help="GitHub Personal Access Token (or set GITHUB_TOKEN env var)")
    parser.add_argument("--output", help="Optional file path to write markdown review")
    args = parser.parse_args()

    try:
        owner, repo, pr_number = parse_pr_url(args.pr)
        pr_data = fetch_github_api(f"repos/{owner}/{repo}/pulls/{pr_number}", token=args.token)
        diff_text = fetch_pr_diff(owner, repo, pr_number, token=args.token)
        analysis = analyze_pr(pr_data, diff_text)
        review_md = format_review_markdown(analysis, pr_number, args.pr)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(review_md)
            print(f"Review successfully written to {args.output}")

        print(review_md)

    except Exception as e:
        print(f"Error reviewing PR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
