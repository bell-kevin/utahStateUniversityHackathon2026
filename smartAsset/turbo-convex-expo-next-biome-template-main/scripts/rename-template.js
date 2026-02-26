#!/usr/bin/env node
/**
 * Global search/replace to re-scope the template.
 *
 * Usage:
 *   pnpm rename <scope> "My App Name"
 *
 * - Replaces all "@template/" with "@<scope>/" across the repo.
 * - Replaces "monorepo-template" with "<scope>".
 * - Replaces Expo display/slug/scheme defaults:
 *     "Template Expo App" / "template-expo-app" / "template-app"
 *     => provided app name + slug.
 *
 * Ignores node_modules, .git, build outputs, and lockfiles already handled.
 */
const fs = require("node:fs");
const path = require("node:path");

const rawScope = process.argv[2];
const displayName = process.argv[3] || "My App";
if (!rawScope) {
  console.error("Usage: pnpm rename <scope> [Expo App Name]");
  process.exit(1);
}
const scope = rawScope.replace(/^@/, "");
const slug =
  displayName
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "") || "app";

const ignoreDirs = new Set([
  "node_modules",
  ".git",
  ".turbo",
  ".next",
  ".expo",
  "dist",
  "build",
  ".cache",
  ".pnpm",
  "convex/_generated",
]);

const ignoreFiles = new Set([
  path.resolve(__filename),
  path.resolve("README.md"),
  path.resolve("pnpm-lock.yaml"),
  path.resolve("package-lock.json"),
  path.resolve("yarn.lock"),
  path.resolve("bun.lockb"),
]);

function shouldSkip(filePath) {
  if (ignoreFiles.has(path.resolve(filePath))) return true;
  const parts = filePath.split(path.sep);
  return parts.some((p) => ignoreDirs.has(p));
}

function replaceInFile(filePath) {
  if (shouldSkip(filePath)) return;
  const stat = fs.statSync(filePath);
  if (!stat.isFile()) return;
  // skip very large files
  if (stat.size > 2 * 1024 * 1024) return;

  const content = fs.readFileSync(filePath, "utf8");
  const replaced = content
    .replace(/@template\//g, `@${scope}/`)
    .replace(/monorepo-template/g, `${scope}`)
    .replace(/Template Expo App/g, displayName)
    .replace(/template-expo-app/g, slug)
    .replace(/template-app/g, slug);

  if (replaced !== content) {
    fs.writeFileSync(filePath, replaced);
    console.log(`updated ${filePath}`);
  }
}

function walk(dir) {
  if (shouldSkip(dir)) return;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(full);
    } else {
      replaceInFile(full);
    }
  }
}

walk(process.cwd());

console.log(
  `Done. Scope set to @${scope}/, app name "${displayName}", slug "${slug}". Run pnpm install to refresh the lockfile.`,
);
