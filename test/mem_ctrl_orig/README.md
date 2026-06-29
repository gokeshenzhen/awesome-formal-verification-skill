# Memory Controller Original-RTL Blind Test

This is a neutral JasperGold formal benchmark.

Task objective:

- Prove the embedded assertions for `mem_ctrl_top`.
- Use the benchmark RTL files in this directory as the design under test:
  - `simple_mem_design.sv`
  - `mem_ctrl_top.sv`
- Do not edit or replace these benchmark RTL files.
- Create proof scripts, logs, and summaries only under your assigned
  `blind/<agent>/` workspace.

Signoff rule:

- A full raw-RTL proof must analyze the benchmark RTL files from this directory
  and prove the target assertions on `mem_ctrl_top`.
- If you use additional bind/helper assertions, prove them before relying on
  them and report them separately.
- If your final result depends on any modeling assumption beyond the benchmark
  RTL itself, clearly disclose that assumption and do not label the result as an
  unqualified raw-RTL signoff result.

Do not read other testcase directories, prior blind reports, `raw-docs`,
`extractions`, or solution material while solving this benchmark.
