# CLAUDE.md — Next.js 15 + SQLite SaaS Guidelines

This is an opinionated, production-grade guide for developing SaaS applications with **Next.js 15 (App Router)** and **SQLite (better-sqlite3 / Turso @libsql)** using **Drizzle ORM**. Follow these conventions strictly.

---

## 1. Stack & Versions

- **Framework**: Next.js 15.x (App Router, Turbopack, React 19)
- **Database**: SQLite (Local: `better-sqlite3` | Production/Edge: `@libsql/client` / Turso)
- **ORM**: Drizzle ORM + Drizzle Kit
- **Language**: TypeScript 5.x (Strict mode enabled)
- **Styling**: Tailwind CSS v4 + Radix UI primitives
- **Validation**: Zod (all inputs, environment variables, server actions)
- **Icons**: Lucide React

---

## 2. Project & Folder Structure

```text
├── app/
│   ├── (auth)/             # Route group: login, signup, reset-password
│   ├── (dashboard)/        # Route group: authenticated SaaS dashboard
│   │   ├── layout.tsx      # Dashboard shell, navigation & user session check
│   │   └── page.tsx        # Dashboard home (Server Component)
│   ├── api/webhooks/       # Only external webhooks (e.g. Stripe, Polar)
│   ├── layout.tsx          # Root layout with fonts, theme provider
│   └── error.tsx           # Global error boundary
├── components/
│   ├── ui/                 # Reusable atomic UI (Button, Input, Modal, etc.)
│   └── dashboard/          # Dashboard feature-specific components
├── db/
│   ├── schema/             # Drizzle table schemas (users.ts, subscriptions.ts, etc.)
│   ├── index.ts            # Database client connection with WAL & foreign keys
│   └── migrations/         # Generated SQL migrations (managed via drizzle-kit)
├── server/
│   ├── actions/            # Type-safe Server Actions for mutations
│   └── queries/            # Reusable server-side DB query functions
├── lib/
│   ├── auth/               # Session cookies, password hashing (argon2/scrypt)
│   ├── env.ts              # Zod-validated process.env variables
│   └── utils.ts            # Helper functions (cn, formatting)
└── drizzle.config.ts       # Drizzle Kit configuration
```

---

## 3. SQL & Migration Conventions

### SQLite PRAGMAs (Mandatory on Connection)
Every SQLite connection **must** execute these two PRAGMAs immediately:
```typescript
db.run(sql`PRAGMA journal_mode = WAL;`);      // Enables non-blocking concurrent reads
db.run(sql`PRAGMA busy_timeout = 5000;`);     // Prevents SQLITE_BUSY under concurrent write spikes
db.run(sql`PRAGMA foreign_keys = ON;`);       // Enforces relational integrity
```

### Schema Rules
- Use `text` primary keys with `cuid2` or `nanoid` (random, sortable, URL-friendly; avoids sequential integer ID enumeration).
- Always define explicit `createdAt` and `updatedAt` integer timestamps (Unix seconds) or ISO text.
- Every foreign key reference **must have an explicit index**; SQLite does not auto-index foreign keys, which causes full table scans during CASCADE operations.
- Avoid JSON columns for data that needs filtering or joining; use normalized child tables.

### Migrations
- Never edit existing migration files in `db/migrations/` once merged.
- Always run `npm run db:generate` to produce declarative `.sql` files, followed by `npm run db:migrate`.
- For zero-downtime column renames: add new column -> copy data -> drop old column in separate steps.

---

## 4. Component & State Architecture

### Server Components by Default
- All `page.tsx` and layout files are **React Server Components (RSC)**.
- Fetch data directly in Server Components using async functions from `server/queries/`.
- Never wrap a Server Component with `'use client'` just to handle navigation or simple CSS classes.

### Leaf `'use client'` Directives
- Apply `'use client'` **only at the lowest interactive leaf component** (e.g. `UserDropdown.tsx`, `DeleteProjectModal.tsx`).
- Pass server-fetched data down as props or pass Server Components as `children` into Client Components.

### Server Actions for Mutations
- All mutations (creating records, updating profiles, billing actions) must be **Server Actions** placed in `server/actions/`.
- Validate all incoming parameters with **Zod** before touching the database.
- Return structured result types: `{ success: true, data: T } | { success: false, error: string }`.
- Use React 19's `useActionState` and `useTransition` for optimistic UI updates and loading spinners.

Example Action Pattern:
```typescript
'use server';

import { z } from 'zod';
import { db } from '@/db';
import { projects } from '@/db/schema';
import { requireAuth } from '@/lib/auth';
import { revalidatePath } from 'next/cache';

const CreateProjectSchema = z.object({
  name: z.string().min(1).max(50),
});

export async function createProjectAction(prevState: any, formData: FormData) {
  const session = await requireAuth();
  const parsed = CreateProjectSchema.safeParse({
    name: formData.get('name'),
  });

  if (!parsed.success) {
    return { success: false, error: parsed.error.issues[0].message };
  }

  await db.insert(projects).values({
    userId: session.userId,
    name: parsed.data.name,
  });

  revalidatePath('/dashboard');
  return { success: true };
}
```

---

## 5. What We DON'T Do (and Why)

| Anti-Pattern | Why We Avoid It | What We Do Instead |
| :--- | :--- | :--- |
| **No Prisma ORM** | Prisma includes a heavy query engine binary that inflates cold starts in serverless/edge environments. | Use **Drizzle ORM** (zero-overhead, lightweight SQL builder). |
| **No API Routes for internal mutations** | Route handlers (`app/api/...`) require manual serializing, fetch calls, and boilerplate. | Use **Server Actions** with automatic TypeScript typing and CSRF protection. |
| **No `useEffect` for data fetching** | Causes layout shift, waterfall requests, and increases client JavaScript payload. | Fetch data directly inside **React Server Components**. |
| **No raw string SQL concatenation** | High risk of SQL injection vulnerabilities. | Always use parameterized queries via `sql` tagged template literals or Drizzle query builders. |
| **No heavy global client stores (Redux)** | Most state in Next.js 15 is server state; global client stores cause cache desync. | Rely on Next.js `revalidatePath` / `revalidateTag` and React URL search params. |
| **No synchronous blocking loops on SQLite** | SQLite is single-writer; long transactions lock the entire database. | Keep write transactions short, use WAL mode, and offload heavy batch processing. |

---

## 6. Development Commands

```bash
# Development
npm run dev              # Starts Next.js development server with Turbopack

# Production Build
npm run build            # Type-checks and creates optimized production bundle
npm run start            # Starts production standalone server

# Database Operations
npm run db:generate      # Generates SQL migration files from Drizzle schema
npm run db:migrate       # Applies pending migrations to SQLite database
npm run db:studio        # Opens Drizzle Studio GUI for visual database management
npm run db:seed          # Populates local database with development mock data

# Code Quality
npm run lint             # Runs ESLint with Next.js rules
npm run typecheck        # Runs tsc --noEmit to verify TypeScript types
```
