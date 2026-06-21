# Awesome Formal Verification Skill

An open-source, AI-agent-agnostic knowledge base for formal verification, designed to supercharge your EDA workflow with any AI coding assistant.

> 🎯 **Current Focus**: JasperGold Formal Property Verification (FPV)
> 🗺️ **Roadmap**: CDC/RDC, Superlint, Coverage, VC Formal support

## What Is This?

This project packages deep formal verification expertise into structured "skills" that AI coding agents can consume. Instead of repeatedly explaining FPV concepts, engine tuning tricks, or TCL scripting patterns to your AI assistant, you point it at this skill and it *knows*.

**Key design principles:**
- **Agent-agnostic**: Core knowledge lives in plain Markdown. Thin adapter layers make it work with Claude Code, Codex, Gemini CLI, Cursor, and more.
- **Tool-aware**: JasperGold and VC Formal have different quirks. Shared verification knowledge is separated from tool-specific details.
- **Community-driven**: Each module has a maturity badge. Battle-tested by real engineers, not just extracted from docs.

## Quick Start

### Claude Code
```bash
# Option 1: Install as a skill
cp -r adapters/claude-code/SKILL.md /path/to/your/project/.claude/skills/

# Option 2: Reference in CLAUDE.md
echo "Read and follow /path/to/awesome-formal-verification-skill/adapters/claude-code/SKILL.md" >> CLAUDE.md
```

### Codex (OpenAI)
```bash
cp adapters/codex/AGENTS.md /path/to/your/project/
```

### Gemini CLI
```bash
cp adapters/gemini-cli/GEMINI.md /path/to/your/project/
```

### Cursor
```bash
cp adapters/cursor/.cursorrules /path/to/your/project/
```

## Project Structure

```
awesome-formal-verification-skill/
├── knowledge/                  # Core knowledge (agent-agnostic)
│   ├── fpv/                    # Formal Property Verification
│   │   ├── property-writing.md
│   │   ├── engine-tuning.md
│   │   ├── complexity-management.md
│   │   ├── tcl-commands.md
│   │   ├── workflow.md
│   │   └── examples/
│   ├── shared/                 # Cross-app shared knowledge
│   │   ├── sva-reference.md
│   │   └── tcl-common.md
│   ├── cdc/                    # 🔜 CDC verification
│   └── lint/                   # 🔜 Superlint
│
├── adapters/                   # Agent-specific wrappers
│   ├── claude-code/SKILL.md
│   ├── codex/AGENTS.md
│   ├── gemini-cli/GEMINI.md
│   └── cursor/.cursorrules
│
├── tool-specific/              # EDA tool differences
│   ├── jaspergold/
│   └── vc-formal/              # 🔜
│
└── benchmarks/                 # Validation test cases
    └── fpv/
```

## Module Maturity

| Module | Status | Description |
|--------|--------|-------------|
| `fpv/property-writing` | 🔬 from-docs | SVA property patterns & best practices |
| `fpv/engine-tuning` | 🔬 from-docs | Proof engine selection & tuning |
| `fpv/complexity-management` | 🔬 from-docs | Complexity reduction techniques |
| `fpv/tcl-commands` | 🔬 from-docs | TCL command reference for FPV |
| `fpv/workflow` | 🔬 from-docs | End-to-end FPV workflow |

**Maturity levels:**
- ✅ `battle-tested` — Validated in real production projects
- ⚠️ `needs-validation` — Structured and reviewed, awaiting real-world feedback
- 🔬 `from-docs` — Extracted from official documentation, not yet field-tested

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Adding new knowledge modules
- Reporting inaccuracies from real-world usage
- Adding support for new AI agents
- Adding support for new EDA tools

## Roadmap

- [x] Project skeleton & adapter framework
- [ ] FPV property writing module
- [ ] FPV engine tuning module
- [ ] FPV complexity management module
- [ ] FPV TCL commands module
- [ ] FPV end-to-end workflow module
- [ ] Benchmark test cases for FPV
- [ ] CDC/RDC verification modules
- [ ] Superlint automation modules
- [ ] VC Formal tool-specific layer
- [ ] Coverage-driven verification modules

## License

[MIT](LICENSE)

## Acknowledgments

Built with insights from the chip verification community. Powered by AI, validated by engineers.
