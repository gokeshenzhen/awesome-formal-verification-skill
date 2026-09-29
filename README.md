# Awesome Formal Verification Skill

<p align="right">
  <strong>English</strong> · <a href="README.zh.md">简体中文</a>
</p>

**Teach your AI coding assistant to actually drive JasperGold formal verification.**

A formal-verification skill for Claude Code, Codex, and other AI agents. When a proof stalls, it tells the AI *which technique* to use, *when* to use it, and *the exact JasperGold command*. It also checks, against auditable acceptance criteria, whether a proof is really complete.

> 🎯 **Supported today**: JasperGold Formal Property Verification (FPV)
> 🗺️ **Planned**: VC Formal, CDC/RDC, Superlint, Coverage

## What Problem Does This Solve?

**If you are new to formal verification**: chip designs (RTL) are usually verified by simulation, which means running many test cases and checking for failures. Formal verification works differently. It mathematically proves that a property (an assertion) holds for *every possible input and state*. It finds deep bugs that simulation rarely reaches, but the computation can explode, and proofs often fail to finish. Getting a proof to converge takes a lot of tool experience.

**If you are a verification engineer**, you know the pain: properties stuck at `undetermined`, state-space explosion, and engine choices made by gut feel. A general-purpose AI assistant knows the methodology ("try abstraction or a helper lemma"), but it often:

- doesn't know the exact commands and flags, such as `abstract -counter`, `assert -helper`, `prove -with_helpers`, or `proof_structure -init`;
- doesn't know *which symptom* should trigger *which technique*, so it keeps adding time or switching engines on the raw proof;
- can't tell "proven" from "proven under extra assumptions", and reports a conditional result as signoff.

This skill fills exactly those three gaps: **tool-specific commands, symptom-to-technique trigger timing, and proof-acceptance discipline**.

## Results

We run manual blind A/B tests: same model, same task, with and without the skill. The difference is clearest on a weaker model (`gpt-5.4-mini` via Codex). Without the skill, both cases failed to reach a proof. With the skill, both closed in seconds.

| Case | Without skill | With skill |
|---|---|---|
| Wide counter (`cnt_abs`) | ❌ Still no signoff after 16m46s: 4 proven / 2 CEX; never found counter abstraction | ✅ 10.8 s: 7 proven / 6 covered, via `abstract -counter` |
| Twin-counter equivalence (`helper_counters`) | ❌ 0 proven / 2 undetermined; never thought of a helper lemma | ✅ 7 s: proved helper `counter1==counter2`, then proved the target `-with_helpers` |

The full report, with the raw source of every number, is in [`test/weak_model_ab/COMPARISON.md`](test/weak_model_ab/COMPARISON.md).

**Caveats**: each arm ran once (N=1), and the knowledge base contains a similar worked example for `cnt_abs`. On frontier models, most cases tie, because a strong model can re-derive the methodology on its own. The skill's value is concentrated in what a model *cannot* derive: exact tool commands and trigger timing. The weaker the model, or the more obscure the tool detail, the bigger the gain.

## What It Helps With

| Your situation | What the skill provides |
|---|---|
| Writing SVA assertions, assumptions, covers | Property patterns and anti-patterns; avoiding vacuous proofs |
| Proof stuck at `undetermined` / state explosion | Technique by symptom: counter/memory abstraction, cutpoints, case splitting, helper lemmas, assume-guarantee, `proof_structure` |
| Helpers added but still not converging | Use JasperGold SST traces to find the missing relation, strengthen the helper, and close the original target |
| Unsure which engine or how deep to run | Engine selection and tuning; Deep Bug Hunting (`hunt`, swarm modes) for deep bugs |
| Writing JasperGold Tcl scripts | Command reference and idioms, such as `-silent`, design/COI queries, and property enumeration |
| Setting up FPV from scratch | End-to-end flow (analyze → elaborate → clock/reset → prove → report) plus result-acceptance criteria |

## Quick Start

```bash
git clone https://github.com/gokeshenzhen/awesome-formal-verification-skill.git
cd awesome-formal-verification-skill
bash scripts/install.sh
```

The installer detects the AI agents on your machine and registers the skill with each one. Restart the agent, then ask questions in your RTL project; the skill triggers automatically. For example:

> The data-integrity assertion on this FIFO stays undetermined. Find out why and get it proven.

> Write handshake protocol assertions for this AXI slave and generate a JasperGold run script.

**Prerequisite**: JasperGold is installed locally with a working license. The skill provides knowledge only and does not ship EDA tools.

<details>
<summary>Install details (supported agents, updating, uninstalling)</summary>

- **Claude Code** and **Codex**: the installer symlinks this repo's `adapters/claude-code/` into the global skills directories (`~/.claude/skills/`, `~/.agents/skills/`, and `~/.codex/skills/` for legacy Codex).
- **Cursor** and **Gemini CLI**: these use project-level rule files. If they are detected, the installer prints how to wire them into a project.
- **Updating**: the entries are symlinks to this checkout, so `git pull` takes effect immediately; no reinstall is needed.
- **Uninstalling**: `bash scripts/install.sh --uninstall`. Re-run the installer after moving the repo.

</details>

## Scope and Limitations

- Validated only for **JasperGold FPV** so far. VC Formal and other tools are not covered yet.
- The knowledge is distilled mainly from official documentation and application notes, backed by a small number of blind tests. Most modules still need real-project feedback (see Module Maturity below).
- The skill requires the AI to disclose what a result depends on. A proof under abstraction, black-boxing, or extra assumptions is **not** raw-RTL signoff, and neither is a `hunt`/DBH run that finds no counterexample.

## Reproducible Cases

The repo ships JasperGold cases you can rerun directly to see what the skill teaches:

- [`test/cti-fifo-refinement/`](test/cti-fifo-refinement/README.md): FIFO data-correctness proof. The direct proof doesn't converge and neither does the initial helper. An SST trace exposes the missing occupancy relation; adding it closes the original target.
- [`test/cti-helper-refinement/`](test/cti-helper-refinement/README.md): introductory helper-strengthening example on a three-stage pipeline, with a Jasper-free exhaustive Python check.
- [`test/weak_model_ab/`](test/weak_model_ab/): raw blind-test material behind the Results section.

## How It Works

Knowledge is decoupled from agents in three layers:

```
knowledge/        Single source of truth: plain Markdown any agent can read
  fpv/            Five FPV modules; large modules split into index + sub-topics, loaded on demand
  shared/         Common references (SVA, Tcl)
adapters/         Thin per-agent routers (Claude Code / Codex / Gemini CLI / Cursor); no knowledge inside
tool-specific/    EDA tool differences (JasperGold today; VC Formal planned)
benchmarks/       Scenario evals and manual A/B experiment tooling
```

The agent loads only the modules relevant to the current task, never the whole knowledge base at once.

## Module Maturity

| Module | Status | Covers |
|--------|--------|--------|
| `fpv/complexity-management` | ⚠️ needs-validation | Abstraction, cutpoints, case splitting, helper lemmas and SST-guided refinement, assume-guarantee |
| `fpv/engine-tuning` | 🔬 from-docs | Engine selection and tuning, Deep Bug Hunting |
| `fpv/property-writing` | 🔬 from-docs | SVA property patterns and best practices |
| `fpv/tcl-commands` | 🔬 from-docs | JasperGold Tcl commands and scripting idioms |
| `fpv/workflow` | 🔬 from-docs | End-to-end flow, proof records, and acceptance criteria |

- ✅ `battle-tested`: validated in real production projects
- ⚠️ `needs-validation`: backed by blind-test evidence, awaiting real-project feedback
- 🔬 `from-docs`: distilled from official documentation, not yet field-tested

**Feedback wanted**: if you've used it on a real project, good or bad, please open an issue. That is the only way a module moves up in maturity.

## Roadmap

- [x] Five JasperGold FPV modules
- [x] SST-guided helper refinement and proof-acceptance criteria
- [x] Scenario evals and weak-model blind tests
- [ ] VC Formal tool layer
- [ ] CDC/RDC verification modules
- [ ] Superlint automation modules
- [ ] Coverage-driven verification modules

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add knowledge modules, report inaccuracies found in real use, and add support for new AI agents or EDA tools.

## Further Reading

- [WeChat article (Chinese): Awesome Formal Verification Skill introduction](https://mp.weixin.qq.com/s/utIrVrACSNOdHx_XbMbazQ)
- How the skill is built: [liandan](https://github.com/gokeshenzhen/liandan), which distills dense formal-verification material into a traceable, portable, verifiable agent skill

## License

[MIT](LICENSE)
