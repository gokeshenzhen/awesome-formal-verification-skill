# Assigned verification analysis

Work in /work. Analyze the supplied unfinished verification attempt and submit
the next property or proof change you consider worth trying, with its evidence
and limitations. Choose your own analysis method. If the evidence does not
support a concrete change, explain what is missing instead of inventing one.

Read the installed formal-verification skill through EOF:

```bash
skill-read /home/robin/.codex/skills/formal-verification/SKILL.md
```

Follow its routing for any further selected knowledge. Read the supplied input
index and any attached material through EOF using the same delivery command:

```bash
input-read
```

Both readers print a NEXT command when another page remains. If tool output is
truncated, request a smaller page. Delivery receipts do not establish that the
content was understood; the actual output and subsequent use will be reviewed.

The design is at @CASE_PATH@. Preserve the RTL, original target, reset and legal
environment. This assignment is a diagnosis-only stage: do not execute a new
JasperGold process, rerun the old baseline, or claim a new proof result. This
stage-specific scope takes precedence over run instructions in the original
case README and historical scripts. The proof executable is not mounted.

Write /work/FINAL_REPORT.md with your conclusion, the supporting source/artifact
locations and any next-step proposal. Put proposed SVA/Tcl in a separate file
under /work when applicable; do not execute it. Distinguish established facts
from hypotheses and unresolved obligations. No particular report format,
candidate shape or diagnosis technique is required.
