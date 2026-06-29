#!/usr/bin/env bash
# install.sh — register this formal-verification knowledge base as a skill for
# every supported AI coding agent found on this machine.
#
# After cloning the repo, run:
#     bash scripts/install.sh
#
# What it does (idempotent — safe to re-run):
#   • Uses adapters/claude-code as the canonical skill directory inside this repo.
#     SKILL.md is a normal tracked file there; knowledge/ and tool-specific/ are
#     relative symlinks back to the repo content.
#   • Points every skills-dir agent at that repo skill directory via a directory
#     symlink. This keeps git-pull hot updates while avoiding a symlinked SKILL.md,
#     which some skill scanners do not discover.
#   • Detects project-scoped agents (Cursor, Gemini CLI) and prints how to wire
#     them, since they use project-level rule/context files, not a global skills
#     directory.
#
# Re-run anytime after moving the repo. Use `--uninstall` to remove the links.
set -euo pipefail

NAME="formal-verification"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_DIR="$REPO/adapters/claude-code"
MANIFEST="$SKILL_DIR/SKILL.md"   # the SKILL.md (frontmatter + routing table)

# --- sanity: must run from inside the repo, content must be present ---
[ -f "$MANIFEST" ]        || { echo "ERROR: $MANIFEST not found — run from a full checkout."; exit 1; }
[ -d "$REPO/knowledge" ]  || { echo "ERROR: $REPO/knowledge not found."; exit 1; }
[ -L "$SKILL_DIR/knowledge" ] || { echo "ERROR: $SKILL_DIR/knowledge symlink missing."; exit 1; }
[ -L "$SKILL_DIR/tool-specific" ] || { echo "ERROR: $SKILL_DIR/tool-specific symlink missing."; exit 1; }

link() { ln -sfn "$1" "$2"; }   # force, no-deref → idempotent symlink

install_skill_link() {
  label="$1"
  skills_root="$2"
  mkdir -p "$skills_root"
  rm -rf "$skills_root/$NAME"
  link "$SKILL_DIR" "$skills_root/$NAME"
  echo "  ✅ $label  → $skills_root/$NAME  ⇒  $SKILL_DIR"
}

if [ "${1:-}" = "--uninstall" ]; then
  for skills_root in "$HOME/.claude/skills" "$HOME/.codex/skills" "$HOME/.agents/skills"; do
    rm -rf "$skills_root/$NAME" 2>/dev/null || true
    [ -d "$skills_root" ] && echo "  removed $skills_root/$NAME"
  done
  echo "Uninstalled '$NAME'."
  exit 0
fi

# --- 1. point skills-dir agents at the repo skill dir ---
echo "✅ canonical skill dir: $SKILL_DIR"
echo "     SKILL.md is a regular repo file; knowledge/ and tool-specific/ are repo-relative symlinks"

INSTALLED=0
if [ -d "$HOME/.claude" ]; then
  install_skill_link "claude" "$HOME/.claude/skills"
  INSTALLED=1
fi
if [ -d "$HOME/.codex" ]; then
  install_skill_link "codex" "$HOME/.agents/skills"
  install_skill_link "codex-legacy" "$HOME/.codex/skills"
  INSTALLED=1
elif [ -d "$HOME/.agents" ]; then
  install_skill_link "codex" "$HOME/.agents/skills"
  INSTALLED=1
fi
if [ "$INSTALLED" -eq 0 ]; then
  echo "No ~/.claude, ~/.codex, or ~/.agents directory found."
  echo "Install Claude Code or Codex first, then re-run — or wire Cursor/Gemini manually (see below)."
fi

# --- 2. project-scoped agents (NOT a global skills dir) ---
if [ -d "$HOME/.cursor" ]; then
  echo "  ℹ cursor detected — Cursor rules are PROJECT-scoped (no global skills dir)."
  echo "     In a project where you want FPV help, copy this into that project root:"
  echo "       cp '$REPO/adapters/cursor/.cursorrules' <your-project>/.cursorrules"
  echo "     (it references this repo's knowledge/, so keep this checkout in place)."
fi
if [ -d "$HOME/.gemini" ]; then
  echo "  ℹ gemini detected — Gemini CLI uses GEMINI.md (project or ~/.gemini), not a skills dir."
  echo "     Point Gemini at: $REPO/adapters/gemini-cli/GEMINI.md"
  echo "     or add a pointer in ~/.gemini/GEMINI.md using the ABSOLUTE path $REPO/knowledge/."
fi

echo
echo "Done. Restart your agent so it rescans skills."
echo "The skill triggers on: formal / property / assertion / prove / CEX / JasperGold / VC Formal / FPV."
