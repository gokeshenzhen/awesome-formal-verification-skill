<p align="right">
  <strong>English</strong> · <a href="README.zh.md">简体中文</a>
</p>

**Feeding a CTI back into helper refinement: a parcel-relay teaching example**

To demonstrate "the original proof stalls, then converges after refinement", use
the [FIFO convergence case](../cti-fifo-refinement/README.md). This directory is
kept as an introductory example of the induction concept.

```text
input → A: intake desk → B: staging desk → C: dispatch desk
```

Each desk holds a parcel number `data_*`, and the verification reference `ref_*`
holds the expected number. `valid[0]`, `valid[1]`, `valid[2]` say whether A, B, C
hold a valid parcel. When `step=1` the whole pipeline advances one stage; when
`step=0` everything pauses together.

The original target `P`: when C holds a parcel, `data_c == ref_c`. If induction only
checks this condition, B in an arbitrary initial state may still hold inconsistent
data, which moves to C on the next cycle. So propose `H0`: when B holds a parcel,
`data_b == ref_b`. Checking one-step induction of H0 shows that an inconsistency at
A can still move into B; so the same helper is strengthened into `H1`: whenever A
and B each hold a parcel, their data match the reference.

```tcl
assert -helper -name h_ab {
  ((!valid[0]) || (data_a == ref_a)) &&
  ((!valid[1]) || (data_b == ref_b))
}
```

Reset establishes H1, and pause preserves H1. When advancing, the same input
establishes A's relation, and A's old relation preserves B's new one. After H1 is
proven, explicitly select it to support the original target P. H0 can be true in
reachable states but is not one-step inductive on its own; refinement adds the
upstream relation it depends on. On idle cycles data may keep an old value, so the
`valid` conditions cannot be dropped.

This is a hand-built teaching demo. Plain Jasper can also prove this small circuit
directly; the diagnosis is requested explicitly in a separate fresh session to
unfold the induction strengthening, not as a performance-speedup benchmark. The
tool's official name for the export is **SST trace**; check `tag SST`, and do not
treat it as a reset-reachable design counterexample or the internal CTI data
structure of the IC3/PDR engine.

| File | Purpose |
|---|---|
| [parcel_pipe.sv](parcel_pipe.sv) | Design, data reference, and original assertion |
| [setup.tcl](setup.tcl) | Common model setup, status output, and SST export |
| [baseline.tcl](baseline.tcl) | Ordinary proof without helpers, plus dispatch/idle covers |
| [diagnose_target.tcl](diagnose_target.tcl) | Round 1: SST of the original target |
| [diagnose_helper.tcl](diagnose_helper.tcl) | Round 2: SST of the initial helper |
| [prove_refined.tcl](prove_refined.tcl) | Prove the strengthened helper first, then support the original target |
| [induction_check.py](induction_check.py) | Exhaustive mathematical model separating reachability from one-step induction |
| [collect_evidence.py](collect_evidence.py) | Extract results, provenance, and hashes from this run's logs |

**Run from a clean clone**

The Python path needs only the Python 3 standard library; it needs no Jasper,
[TraceWeave](https://github.com/gokeshenzhen/TraceWeave), or pre-generated results.
Run from the repository root:

```bash
cd test/cti-helper-refinement
python3 induction_check.py
```

The script creates `evidence/induction.json` automatically. Expected: all relations
hold in reset-reachable states; `one_step_inductive` is `false` for `P`, `H0_B`,
`P_and_H0`, and `true` for `H1_AB`, `P_and_H1`. It enumerates all encoded states
and inputs and fully traverses the reachable states, with no random testing. It does
not parse the RTL and cannot replace the Jasper proof on the RTL.

To run the RTL proofs, make sure JasperGold is installed, `jg` is on `PATH`, and the
license is available. The scripts are verified against the command semantics of
JasperGold `2025.12p002`; on other versions, check `help prove` and `help sst`
first. Continue in the `test/cti-helper-refinement/` directory:

```bash
jg -no_gui -proj runs/baseline -tcl baseline.tcl
jg -no_gui -proj runs/target_sst -tcl diagnose_target.tcl
jg -no_gui -proj runs/helper_sst -tcl diagnose_helper.tcl
jg -no_gui -proj runs/refined -tcl prove_refined.tcl
python3 collect_evidence.py
```

The top-level Tcl locates `setup.tcl` relative to the current working directory, so
launch from the directory above. Each Jasper command uses its own project; the
scripts create the output directories and exit automatically. If Jasper was not
run, there is no need to run `collect_evidence.py`.

| Run | Expected result | Files generated after the run |
|---|---|---|
| `baseline` | Original target `proven`; both the dispatch and idle-data-mismatch covers `covered` | `evidence/baseline.txt` |
| `target_sst` | Original target `undetermined`; a trace with `tag SST` attached | `evidence/target_sst.txt`, `target_sst.vcd` |
| `helper_sst` | H0 `undetermined`; a trace with `tag SST` attached | `evidence/helper_sst.txt`, `helper_sst.vcd` |
| `refined` | H1 and the original target both `proven`, validity `proven`, bound `Infinite` | `evidence/refined.txt` |
| `collect_evidence.py` | Extracts the raw result lines and log locations of the runs above | `evidence/proof-results.txt` |

Full logs are in `runs/<run name>/sessionLogs/session_*/jg_session_*.log`.
`prove_refined.tcl` checks the status and validity of a helper before reusing it and
exits if it is unproven; merely marking `-helper` is not a proof or an unconditional
assumption. Even when a bound field of an SST shows `infinite`, it must not be used
to declare a complete proof.

**Optional waveform analysis**

Inspect the exported VCD with a waveform viewer. If TraceWeave is configured, call
`get_formal_paths`, `search_signals`, `get_signals_around_time` in order to read
`valid`, `data_*`, `ref_*`, `step`, and other signals of the current and next state.
Choose sample times from the VCD's actual time scale; it is not a chip performance
parameter. The specific counterexample numbering may vary with version or solver
choices; focus on the unequal relation and the branch that actually updates.

If you saved two TraceWeave samplings yourself, you can additionally replay their
state projection:

```bash
python3 induction_check.py --replay-samples /path/to/local/samples
```

The directory must contain `target_sst_samples.json` and `helper_sst_samples.json`.
The `samples` array of each file contains two time-ordered JSON result objects from
`get_signals_around_time(return_mode="values_only")`. Keep at least the full paths
of `parcel_pipe.rst_n`, `step`, `in_valid`, `in_data`, `valid`, `data_a`, `data_b`,
`ref_a`, `ref_b`; the original target's samples also include `data_c`, `ref_c`.
Choose samples where reset is released and there is an adjacent state transition.
The replay only checks the saved signal projection and cannot replace a proof.
Without this option, sample files are not read and the report explicitly marks
`sst_transition_replay: not requested`.

The repository contains only source and rerun notes. `runs/` and `evidence/` are
generated locally and ignored by Git; no historical results need to be downloaded.
The WeChat article draft and figures are not dependencies of this runnable example.

The scripts contain no input assumptions, cutpoints, or black boxes. `ref_*` is a
verification data reference, and `valid` is shared with the DUT; the proof scope is
the correspondence of valid data, and does not include independent verification of
no-drop, no-reorder, or backpressure protocols.
