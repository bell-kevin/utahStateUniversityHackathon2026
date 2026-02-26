#!/usr/bin/env node
/**
 * Cross-platform script to symlink .env.local from root to app/package directory
 * Falls back to copying if symlink creation fails (e.g., Windows without admin)
 */

const fs = require("node:fs");
const path = require("node:path");

const rootDir = path.resolve(__dirname, "..");
const targetDir = process.cwd();
const sourceFile = path.join(rootDir, ".env.local");
const targetFile = path.join(targetDir, ".env.local");

// Don't create symlink if we're already in the root directory
if (rootDir === targetDir) {
  console.log("Skipping .env.local symlink (already in root directory)");
  process.exit(0);
}

// Check if source file exists
if (!fs.existsSync(sourceFile)) {
  console.log("No .env.local file found in root - skipping symlink creation");
  process.exit(0);
}

// Remove existing symlink or file if it exists
if (fs.existsSync(targetFile)) {
  const stats = fs.lstatSync(targetFile);
  if (stats.isSymbolicLink()) {
    fs.unlinkSync(targetFile);
    console.log("Removed existing .env.local symlink");
  } else {
    console.log(".env.local already exists (not a symlink) - skipping");
    process.exit(0);
  }
}

// Try to create symlink
try {
  fs.symlinkSync(sourceFile, targetFile, "file");
  console.log(
    `✓ Created symlink: .env.local -> ${path.relative(targetDir, sourceFile)}`,
  );
} catch (error) {
  // Symlink failed (possibly Windows without admin), try copying instead
  console.log("⚠ Symlink creation failed, copying .env.local instead");
  try {
    fs.copyFileSync(sourceFile, targetFile);
    console.log("✓ Copied .env.local from root");
  } catch (copyError) {
    console.error(`✗ Failed to copy .env.local: ${copyError.message}`);
    process.exit(1);
  }
}
