# Contributing to Awesome Formal Verification Skill

Thank you for your interest in contributing! This project aims to build a comprehensive, community-validated knowledge base for formal verification that works across AI coding agents.

## How to Contribute

### 1. Report Real-World Feedback (Most Valuable!)

The biggest gap in this project is real-world validation. If you've used any module in an actual project:

- **Open an Issue** with the label `field-report`
- Include: which module you used, what worked, what didn't, and what was missing
- This directly moves modules from 🔬 `from-docs` → ⚠️ `needs-validation` → ✅ `battle-tested`

### 2. Improve Knowledge Modules

Each module in `knowledge/` follows a consistent structure:

```markdown
# Module Title

## Overview
Brief description of what this module covers.

## When to Use
Conditions that should trigger this knowledge.

## Key Concepts
Core knowledge organized by topic.

## Decision Trees
Flowcharts or if/then guidance for common decisions.

## Common Patterns
Reusable patterns with examples.

## Anti-Patterns
Common mistakes and how to avoid them.

## Tool-Specific Notes
Pointers to tool-specific details (link to tool-specific/ directory).
```

When editing or adding content:
- Write in imperative form ("Use X" not "You should use X")
- Include concrete examples with code snippets
- Explain *why*, not just *what*
- Keep modules under 500 lines; split into sub-modules if needed

### 3. Add Agent Adapters

To add support for a new AI agent:

1. Create a directory under `adapters/your-agent/`
2. Create the agent's config file (e.g., `.rules`, `INSTRUCTIONS.md`)
3. The adapter should:
   - Describe when to trigger the skill
   - Point to the appropriate `knowledge/` modules
   - Respect the agent's conventions and format
4. Update README.md's Quick Start section

### 4. Add Tool Support

To add support for a new EDA tool (e.g., VC Formal, OneSpin):

1. Create a directory under `tool-specific/your-tool/`
2. Document tool-specific quirks, commands, and version notes
3. Reference these from the relevant `knowledge/` modules

### 5. Add Benchmark Cases

Benchmark cases in `benchmarks/` help validate knowledge quality:

```markdown
## Scenario: [descriptive name]

### User Prompt
What a user might ask the AI agent.

### Expected Behavior
What the AI should do/recommend based on the skill.

### Key Points to Cover
- Point 1
- Point 2

### Anti-Patterns to Avoid
- Wrong approach 1
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/add-cdc-module`)
3. Make your changes
4. Update the maturity table in README.md if applicable
5. Submit a PR with a clear description

## Code of Conduct

Be respectful, constructive, and focused on making formal verification more accessible. We welcome engineers of all experience levels.

## Questions?

Open an issue with the `question` label.
