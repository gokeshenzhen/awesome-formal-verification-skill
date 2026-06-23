#!/usr/bin/env bash
# install.sh — register this formal-verification knowledge base as a skill for
# every supported AI coding agent found on this machine.
#
# After cloning the repo, run:
#     bash scripts/install.sh
#
# What it does (idempotent — safe to re-run):
#   • Builds ONE canonical skill directory (real dir of symlinks back into this
#     repo: SKILL.md + knowledge/ + tool-specific/), preferring ~/.claude.
#   • Points every other skills-dir agent (Codex) at that canonical dir via a
#     single symlink — mirroring how eda-environment is shared across agents.
#   • Detects project-scoped agents (Cursor, Gemini CLI) and prints how to wire
#     them, since they use project-level rule/context files, not a global skills
#     directory.
#
# Re-run anytime after moving the repo. Use `--uninstall` to remove the links.
set -euo pipefail

NAME="formal-verification"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="$REPO/adapters/claude-code/SKILL.md"   # the SKILL.md (frontmatter + routing table)

# --- sanity: must run from inside the repo, content must be present ---
[ -f "$MANIFEST" ]        || { echo "ERROR: $MANIFEST not found — run from a full checkout."; exit 1; }
[ -d "$REPO/knowledge" ]  || { echo "ERROR: $REPO/knowledge not found."; exit 1; }

link() { ln -sfn "$1" "$2"; }   # force, no-deref → idempotent symlink

# skills-dir agents that share the SKILL.md model (homedir name → label)
SKILLS_AGENTS=(claude codex)

if [ "${1:-}" = "--uninstall" ]; then
  for a in "${SKILLS_AGENTS[@]}"; do
    rm -rf "$HOME/.$a/skills/$NAME" 2>/dev/null || true
    [ -d "$HOME/.$a/skills" ] && echo "  removed ~/.$a/skills/$NAME"
  done
  echo "Uninstalled '$NAME'."
  exit 0
fi

# --- 1. choose the canonical (real) skill dir: prefer ~/.claude, else ~/.codex ---
CANON=""
for a in "${SKILLS_AGENTS[@]}"; do
  if [ -d "$HOME/.$a" ]; then CANON="$HOME/.$a/skills/$NAME"; break; fi
done

if [ -z "$CANON" ]; then
  echo "No ~/.claude or ~/.codex directory found."
  echo "Install Claude Code or Codex first, then re-run — or wire Cursor/Gemini manually (see below)."
else
  mkdir -p "$CANON"
  link "$MANIFEST"            "$CANON/SKILL.md"
  link "$REPO/knowledge"      "$CANON/knowledge"
  link "$REPO/tool-specific"  "$CANON/tool-specific"
  echo "✅ canonical skill dir: $CANON"
  echo "     SKILL.md → adapters/claude-code/SKILL.md ; knowledge/ ; tool-specific/  (all → repo)"

  # --- 2. point every present skills-dir agent at the canonical dir ---
  for a in "${SKILLS_AGENTS[@]}"; do
    [ -d "$HOME/.$a" ] || continue
    mkdir -p "$HOME/.$a/skills"
    target="$HOME/.$a/skills/$NAME"
    if [ "$target" = "$CANON" ]; then
      echo "  ✅ $a  → $target  (canonical)"
    else
      link "$CANON" "$target"
      echo "  ✅ $a  → $target  ⇒  $CANON"
    fi
  done
fi

# --- 3. project-scoped agents (NOT a global skills dir) ---
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
