You are the no_skill_weak_model arm of a manual blind JasperGold experiment.

Work only in:
/home/robin/Projects/awesome-formal-verification-skill/test/phase_stride_orig

Write every artifact only under:
/home/robin/Projects/awesome-formal-verification-skill/test/phase_stride_orig/blind/no_skill_weak_model

First read only `README.md`, `CHECKSUMS.sha256`, `phase_stride_orig.sv`, and
`baseline.tcl` from the case root. Before running JasperGold, execute
`sha256sum -c CHECKSUMS.sha256` from the case root and preserve its complete
output in `blind/no_skill_weak_model/integrity_before.txt`. Then perform the
investigation described in `README.md` with JasperGold.

Isolation rules:
- Do not consult the installed formal-verification skill, repository
  `knowledge/`, `adapters/`, `tool-specific/`, `raw-docs/`, or `extractions/`.
- Do not read another testcase, prior reports, solution archives, or
  `blind/skill_weak_model`.
- You may use JasperGold's installed command help and the EDA environment
  instructions needed to launch the authorized local tool.
- Do not edit the shared RTL or shared baseline Tcl.
- Do not add assertions, covers, assumptions, constraints, helper properties,
  or guidepoints.
- Keep every Jasper project, log, trace, script, and report under
  `blind/no_skill_weak_model`.

Run `./run_baseline.sh` first and preserve its log. Explore independently until
the completion conditions in `README.md` are met, or until the stated Jasper
wall-time budget has been consumed.

Before finishing, provide:
- `run.tcl`: the final self-contained Jasper flow;
- keep `run_baseline.sh` as the common baseline replay;
- `reproduce.sh`: a non-interactive timestamped replay script;
- `RESULT.md`: exact commands, tool version, files read and created, baseline
  and final status, bounds, witness information, wall time, aggregate
  slot-seconds, citations to exact artifacts and log lines, and the reasoning
  behind the selected investigation strategy.

Run the checksum command again and preserve its complete output in
`blind/no_skill_weak_model/integrity_after.txt`. Do not turn an inconclusive
result into a proof or a falsification claim.
