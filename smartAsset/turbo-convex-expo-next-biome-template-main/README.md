# Expo + Next + Convex Turborepo Template

## Stack
- pnpm + Turborepo
- Expo (Expo Router) mobile app
- Next.js web app
- Convex backend
- Biome formatter/linter
- TypeScript everywhere

## Prerequisites
- Node.js 18+ (corepack recommended)
- VS Code (Biome extension) or your preferred editor

## Getting Started
1. Rename the template (see section below)
2. Copy envs
   ```bash
   cp .env.example .env.local
   ```
   A postinstall script symlinks `.env.local` into each app/package.
3. Enable corepack and install dependencies
   ```bash
   corepack enable
   pnpm install
   ```
4. Set up convex
   ```
   pnpm dev:convex
   ```
5. Run dev servers
   ```bash
   pnpm dev
   ```

## Rename the template
Update the package scope and Expo app name in one command (works on Windows/macOS/Linux):
```bash
pnpm rename myscope "My App Name"
pnpm install # refresh lockfile after renaming
```
This replaces all `@template/*` packages with `@myscope/*` and updates `apps/expo/app.json` name/slug/scheme.

## Convex note
The Convex backend ships with stubbed generated files so typecheck passes out of the box. When you’re ready to use Convex, run:
```bash
pnpm --filter @template/convex convex codegen
```
then start the Convex dev server with `pnpm dev:convex`.

## Useful scripts
- `pnpm dev:expo`
- `pnpm dev:web`
- `pnpm dev:convex`
- `pnpm lint` | `pnpm format` | `pnpm typecheck` | `pnpm build` | `pnpm test`
