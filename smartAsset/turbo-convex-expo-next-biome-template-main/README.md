# Smart Asset Intelligence (Hack USU Startup Track MVP)

This folder now contains a full hackathon-ready prototype for an **AI-enhanced CMMS layer** focused on NFC-tagged assets.

## What it demonstrates
- NFC-style asset selection (simulated in web UI)
- Role-based action menu (`student`, `maintenance`, `supervisor`)
- AI inspection scoring from notes (keywords -> findings -> priority/actions)
- Structured AI payload in the format requested
- Convex-ready backend schema for assets, scans, inspections, users, and work orders
- Risk updates and work-order generation via backend mutations

## Project structure
- `apps/web`: Next.js dashboard/prototype and API route for AI inspection evaluation
- `backend/convex`: Convex schema + mutations/queries for asset operations
- `apps/expo`: Existing Expo shell retained for mobile expansion

## Key workflow
1. User scans NFC tag (simulated by selecting an asset).
2. User chooses an action from role-based options.
3. User submits notes (and optionally photo URL in backend flow).
4. AI layer evaluates notes and returns:
   - `summary`
   - `overall_priority`
   - `findings[]`
   - `actions[]`
5. Backend mutation can merge new risk into asset score and auto-create work orders.

## Run locally
```bash
corepack enable
pnpm install
pnpm dev:web
```

Then open `http://localhost:3000`.

## Validation commands
```bash
pnpm --filter @template/web test
pnpm --filter @template/web typecheck
pnpm --filter @template/web lint
pnpm --filter @template/backend typecheck
pnpm --filter @template/web build
```

## Notes
- The AI module currently uses deterministic heuristics for fast hackathon prototyping.
- Swap in an LLM or vision model by replacing `evaluateInspection` and/or Convex action logic.
