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

## Project Introduction

- [微信公众号文章：Awesome Formal Verification Skill 项目介绍](https://mp.weixin.qq.com/s/utIrVrACSNOdHx_XbMbazQ)

## Quick Start

Clone the repo, then run the installer once:

```bash
git clone <this-repo-url>
cd awesome-formal-verification-skill
bash scripts/install.sh
```

That's it. The installer auto-detects the AI agents on your machine and registers
the skill for each:

- **Claude Code** and **Codex** — both use global skills directories. The
  installer points them at this repo's canonical skill directory
  (`adapters/claude-code/`) via directory symlinks:
  `~/.claude/skills/`, `~/.agents/skills/` for current Codex, and
  `~/.codex/skills/` for legacy Codex installs.
  Restart the agent and the skill auto-triggers on any FPV task
  (formal / property / assertion / prove / CEX / JasperGold / VC Formal / FPV).
- **Cursor** and **Gemini CLI** — these use *project-level* rule/context files,
  not a global skills directory. If detected, the installer prints exactly how to
  wire them into a project.

Because each agent's skill entry is a directory symlink to this checkout,
updating the repo (`git pull`) updates every agent instantly — no reinstall.
`SKILL.md` itself stays a normal tracked file inside the repo, which avoids
scanner issues with file-level `SKILL.md` symlinks. Re-run the installer after
moving the repo; use `bash scripts/install.sh --uninstall` to remove the links.

> The per-agent wrapper files under `adapters/` are the source-of-truth manifests
> the installer wires up — you normally don't touch them directly.

## Project Structure

```
awesome-formal-verification-skill/
├── knowledge/                  # Core knowledge (agent-agnostic)
│   ├── fpv/                    # Formal Property Verification
│   │   ├── property-writing.md
│   │   ├── engine-tuning.md
│   │   ├── complexity-management.md     # index (progressive disclosure)
│   │   ├── complexity-management/       # sub-topic leaves
│   │   ├── tcl-commands.md
│   │   └── workflow.md
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
- [x] FPV property writing module
- [x] FPV engine tuning module
- [x] FPV complexity management module
- [x] FPV TCL commands module
- [x] FPV end-to-end workflow module
- [x] Benchmark test cases for FPV
- [ ] CDC/RDC verification modules
- [ ] Superlint automation modules
- [ ] VC Formal tool-specific layer
- [ ] Coverage-driven verification modules

## License

[MIT](LICENSE)

## Acknowledgments

Built with insights from the chip verification community. Powered by AI, validated by engineers.
