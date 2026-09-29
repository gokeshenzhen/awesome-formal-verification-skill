<p align="right">
  <strong>English</strong> · <a href="BLIND_AB.zh.md">简体中文</a>
</p>

**Manual skill / no-skill comparison: protocol pending execution**

The rerun scripts here verify "missing invariant → diagnosis → strengthening →
convergence". They already contain the answer, so their execution results cannot
serve as evidence that an independent model discovered the answer. The repository
convention is that the skill A/B is run by the user in two independent sessions;
this document provides the materials and acceptance conditions and does not start
an automatic double-blind harness.

The participants' base materials are the five files in `neutral/`: `sfifo.v`,
`tb.sv`, `setup.tcl`, `baseline.tcl`, `TASK.md`. Identical run configuration and a
plain tool-environment description may be attached for both sides, but they must
not contain a solution route or the case answer. Copy them into two new directories
outside the repository, for example:

```bash
mkdir -p /tmp/fifo-arm-a /tmp/fifo-arm-b
cp neutral/sfifo.v neutral/tb.sv neutral/setup.tcl neutral/baseline.tcl neutral/TASK.md /tmp/fifo-arm-a/
cp neutral/sfifo.v neutral/tb.sv neutral/setup.tcl neutral/baseline.tcl neutral/TASK.md /tmp/fifo-arm-b/
```

The directories must be freshly created; if a previous run exists, use new paths.
Do not copy this directory's README, helpers, diagnosis/convergence scripts, or
historical reports. The participants' workspaces must not be inside this repository,
so they do not inherit its routing and answers. Copying files is not operating-system
isolation; also restrict what the sessions can read, and check the actual tool
records for out-of-bounds access.

Both sides use the same model version, reasoning setting, session budget,
Jasper/license environment, and TraceWeave. Keep the EDA environment configuration
notes common to both; the only knowledge difference is that B can read the
`formal-verification` skill and the knowledge files it routes to, while A cannot.
The actual tool read records must be checked; it is not enough to prompt "do not use
the skill" while the skill is still auto-injected into A's context. Start with a
weaker model, but fix the model and budget before seeing any result.

Take the configuration confirmed for this run as the source of the budget, and
synchronize the participants' TASK and startup notes with it; the existing budget in
`neutral/TASK.md` is this template's setting, not a quota every experiment must
reuse. Define how the baseline, launch failures, and retries are accounted for, and
fix the number of independent attempts per side, the stopping rule, and the
environment-failure rerun rule before running. Keep all attempts, not only the
successful ones; if conditions change, record a new experiment. A single comparison
supports only a case observation under that condition.

Fix the skill content B can actually read: dereference the knowledge symlinks in the
install directory and record hashes, so it does not follow changes in the
development worktree during the run. Statically checking files and configuration is
not the same as verified run isolation; at launch the user must also verify the
skills actually injected, parent-directory/global instructions, historical context,
and the access scope of every file-reading tool. If isolation cannot be shown, do
not treat the result as a valid comparison.

Open a brand-new session for each side and give both exactly the same prompt:

> Please complete the verification task in TASK.md in the current working directory, following its budget, file scope, and deliverable requirements.

Do not add solution hints such as "CTI", "SST", "helper", or "capacity bound" to the
prompt. Neither side should see the other's process or results. Keep the complete
event record, and also record the model version, settings, skill content hashes,
tool versions, workspace source hashes, budget, and every Jasper invocation with its
duration.

**What results support the statement the user wants to make**

- A does not close the original target within the pre-fixed budget; this must not be
  written as "without the skill it can never be proven".
- B independently locates the unclosed obligation, generates or obtains a diagnostic
  trace, actually reads signal values, explains the missing relation, and modifies
  the helper accordingly; the order of these steps can be found in the event record.
- B obtains a valid unbounded proof of the unmodified original target and of the
  final required support, and the read cover is reachable. Valid sequential reuse or
  tool-managed joint closure is allowed; keep the actual obligations and selection
  evidence. Abandoned candidates that left the final obligations and on which the
  result does not depend are kept as history only. When proof_structure is used, the
  propagated ROOT must also be accepted. Extra assumptions, black boxes, cutpoints,
  `marked_proven`, or a weaker target cannot pass as a complete proof of the
  original design.
- After receiving the two reports, independently rerun each side's `final.tcl` in
  fresh Jasper projects that share no cache, and check the source, environment,
  dependencies, and results. If both sides prove it, or B did not use trace
  feedback, report that as it is; do not call it "the CTI skill caused the win".

Behavioral correctness, proof closure, resource consumption/comparison, and the
strict demonstration above are reported separately. A direct proof or a first-
candidate success is still a valid success; correctly reporting non-completion can
pass the corresponding behavior checks, but there is no proof closure. The
no-skill / current-skill difference measures the effect of the whole body of
knowledge; attributing it to a specific change would additionally require old- vs.
new-version evidence under fixed conditions, and this is not expanded into three
groups by default.

Until the two reports exist, the evidence conclusion of this directory is only a
**refinement convergence case**.
