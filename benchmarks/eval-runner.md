# Benchmark Evaluation Runner

## Overview

This document explains how to run benchmark evaluations across different AI agents to validate skill quality.

## For Claude Code

Use the skill-creator's built-in eval framework:

```bash
# 1. Copy the skill to your project
cp -r adapters/claude-code/SKILL.md /path/to/project/.claude/skills/formal-verification/

# 2. Run eval scenarios using skill-creator
# (requires skill-creator skill installed)
# See: https://github.com/anthropics/skill-creator
```

## For Other Agents (Manual Testing)

### Step 1: Pick a scenario from `fpv/scenarios.md`

### Step 2: Feed the prompt to the agent with the skill loaded

### Step 3: Evaluate the response against the checklist

Record results in this format:

```markdown
## Result: [scenario-name]
- Agent: Claude Code | Codex | Gemini CLI | Cursor
- Date: YYYY-MM-DD
- Modules consulted: (did the agent read the right modules?)
- Key points covered: X/Y
- Anti-patterns avoided: Yes/No
- Notes: [free-form observations]
```

### Step 4: Open an issue or PR with your results

Results from real-world testing are the most valuable contribution to this project. Even a single scenario tested in a real project helps move modules from 🔬 to ⚠️ to ✅.

## Interpreting Results

| Score | Interpretation |
|-------|---------------|
| All key points covered, no anti-patterns | Module is solid |
| Most points covered, minor gaps | Module needs refinement |
| Major gaps or anti-patterns triggered | Module needs rewrite |
| Agent didn't consult the right modules | Adapter/routing needs fix |
