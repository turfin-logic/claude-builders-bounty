# ⚡ Automated Weekly GitHub Dev Summary with Claude 3.5 Sonnet (n8n Workflow)

A production-ready [n8n](https://n8n.io) workflow that triggers weekly, inspects commits and closed PRs from your GitHub repository, sends the activity context to Anthropic's Claude 3.5 Sonnet API, and broadcasts an executive developer summary to your team's Discord or Slack webhook.

## 📦 What's Included

- `github_weekly_summary.json` — Importable n8n workflow file (v1 execution order).

---

## 🚀 Setup Instructions in 3 Steps

### 1. Import Workflow into n8n
1. Open your n8n instance.
2. In the top-right menu, select **Workflows** > **Import from File...**
3. Select `github_weekly_summary.json`.

### 2. Configure Environment Variables / Parameters
Set the following variables in your n8n environment or directly in the node parameters:

| Variable | Description | Example |
| :--- | :--- | :--- |
| `GITHUB_OWNER` | GitHub organization or username | `facebook` |
| `GITHUB_REPO` | Repository name | `react` |
| `ANTHROPIC_API_KEY` | Your Anthropic Claude API Key | `sk-ant-api03-...` |
| `DISCORD_WEBHOOK_URL` | Discord or Slack webhook URL | `https://discord.com/api/webhooks/...` |

### 3. Test & Activate
- Click **Test step** on the `Schedule Trigger` node to run a manual execution.
- Toggle the workflow from **Inactive** to **Active** to run automatically every Friday at 17:00 UTC.

---

## 📋 Sample Summary Delivered to Discord

```markdown
🚀 **Weekly Development Pulse — turfin-logic/CubeRun**

### 🌟 Executive Overview
This week the team focused on mobile responsiveness, ad-blocker resilience, and offline crash prevention, closing 12 pull requests across the stack.

### ✨ Key Deliverables
- **Ad-blocker Resilience**: Isolated main-frame navigation failures from third-party tracker blocks to guarantee seamless gameplay.
- **ASO & Store Metadata**: Optimized title, taglines, and feature graphics for Google Play store launch.

### 🐛 Fixes & Polish
- Fixed APK crash on startup under strict private DNS filters.
- Removed dead RewardedInterstitialAd legacy listeners.

### 👥 Top Contributors
Shoutout to `@turfin-logic` for landing the core engine resilience updates!
```
