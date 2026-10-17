# Next.js 15 + SQLite SaaS `CLAUDE.md` Template

A production-ready, opinionated `CLAUDE.md` guide tailored specifically for building modern SaaS products using **Next.js 15 (App Router, React 19)** and **SQLite (better-sqlite3 / Turso @libsql)** with **Drizzle ORM**.

## Why this template?

Most generic AI instructions fail on Next.js 15 by mixing Server and Client Components, using outdated Pages Router conventions, or proposing slow ORMs that cause serverless cold-start latency. 

This guide enforces:
1. **Explicit SQLite Configuration**: Mandatory `WAL` mode, busy timeouts, and foreign key pragma enforcement.
2. **Server-First Mindset**: RSC for data fetching, leaf `'use client'` components, and type-safe Server Actions.
3. **No-Nonsense Architectural Guardrails**: Clear, justified rules on what *not* to do.

## How to Use

Copy `CLAUDE.md` into the root of your Next.js project:

```bash
curl -fsSL https://raw.githubusercontent.com/claude-builders-bounty/claude-builders-bounty/main/templates/nextjs-sqlite-saas/CLAUDE.md -o CLAUDE.md
```

Claude Code will instantly recognize your stack and structure all proposed code according to these rules.
