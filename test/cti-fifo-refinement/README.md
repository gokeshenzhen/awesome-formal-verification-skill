<p align="right">
  <strong>English</strong> · <a href="README.zh.md">简体中文</a>
</p>

**Feeding a CTI back into helper refinement: making a FIFO data proof converge**

This is a rerunnable convergence case. The direct data-correctness proof does not
finish within the given budget; the initial data helper does not close either. An
SST trace exposes a missing capacity relation. Prove that relation first, use it to
support the data helper, and the unmodified original target closes.

It demonstrates **what refinement does**. To go further and claim "the model
without the skill fails, the model with the skill reads the CTI on its own and
succeeds", two independent sessions are required; there is no such new blind-test
result yet. [BLIND_AB.md](BLIND_AB.md) provides the isolated materials and
acceptance conditions. Running the prepared scripts is not evidence that a model
discovered the helper by itself.

**Design and goal**

Think of the FIFO as a ring warehouse with only 32 slots. The write pointer marks
the next slot to fill, the read pointer marks the next slot to drain, and `o_fill`
is the book inventory. Pointers are 6 bits wide: the low 5 bits select the physical
slot, and the extra bit distinguishes wrap-around laps. For example, indices 20 and
52 point to the same physical slot.

The DUT is a [pinned version of the ZipCPU sfifo](https://github.com/ZipCPU/zipcpu/blob/42606d2d6ef55df313772232977621b2d72f0159/rtl/ex/sfifo.v),
configured in [neutral/tb.sv](neutral/tb.sv): 32-bit data, 32 entries, registered
read output, with the write-when-full and read-when-empty options disabled. Only
the upstream `FORMAL` conditional block is removed; the rest of the source and the
public-domain notice are kept. Provenance and hashes are in
[SOURCE.json](SOURCE.json). Rerunning needs no upstream download.

The verification observer picks an arbitrary fixed extended address
`watched_address` and remembers the data of the most recent accepted write to that
location. The original target `testbench.P0`: when that location is the head of a
non-empty FIFO, the output equals the recorded data. The only input assumption is
that the watched address stays stable; read/write requests and data are arbitrary.
This proves the data correspondence only; it does not include a liveness guarantee
that every request is eventually served.

**What refinement adds**

The initial helper `H_mem_watch_live` states:

> While the watched location is still inside the FIFO's valid range, the data in the
> corresponding physical slot equals what the observer recorded.

```tcl
assert -name H_mem_watch_live {
  ((watched_address - dut.rd_addr) < dut.o_fill)
  |-> dut.mem[watched_address[4:0]] == watched_data
}
```

The existing control relations include `fill == wr_addr - rd_addr`,
`empty == (fill == 0)`, and `full == (fill == 32)`. Subtraction wraps as 6-bit
unsigned. These relations allow the following diagnostic state:

| Signal / relation | Current state | After one accepted write |
|---|---:|---:|
| `rd_addr` | 22 | 22 |
| `wr_addr` | 20 | 21 |
| `o_fill` | 62 | 63 |
| `watched_address` | 52 | 52 |
| `mem[20]` | 0 | 4096 |
| `watched_data` | 0 | 0 |

These values are for hand calculation; the tool does not guarantee the same choice
every time. Here reset is released, a write is accepted, nothing is read, and the
input data is 4096. `(20 - 22) mod 64 = 62`, so the pointer relation holds;
`52 - 22 = 30 < 62`, so the data helper's antecedent holds too. Write pointer 20
overwrites `mem[20]`, but the watched address is 52, so the observer does not
update. On the next cycle the data differ and the helper is broken. The problem:
**a 32-slot FIFO whose arbitrary initial state permits an inventory of 62.**

The SST points to a capacity upper bound as the missing relation, rather than
forbidding this one particular index:

```tcl
assert -name H_fill_range {dut.o_fill <= 6'd32}
```

First prove `H_fill_range` on the original reset, RTL, and input environment; only
after it is proven is it added to the support set of later obligations. This case
keeps the formula, engine, and budget of `H_mem_watch_live` unchanged and only adds
and proves the capacity relation. What gets strengthened is the **helper set**:
`H_controls ∧ H_mem` becomes `H_controls ∧ H_fill_range ∧ H_mem`. The
register-read-path relation is then proven, and finally the original `P0`. The full
dependency order is in [prove_refined.tcl](prove_refined.tcl).

The tool's official name for the export is **SST trace**; the scripts check
`get_trace_info` for `tag SST`. It is used here to observe the induction
strengthening gap; it is not a reset-reachable design counterexample, nor does it
mean the IC3/PDR engine's internal CTI data structure was exported. Only once the
capacity bound is proven is the unreachability of the over-capacity state above
supported by an independent proof.

**Rerun from a clean clone**

Requires an installed, working JasperGold (`jg` on PATH, license available);
collecting results needs Python 3.9+ with the standard library only. Commands were
verified against JasperGold `2025.12p002`.
[TraceWeave](https://github.com/gokeshenzhen/TraceWeave) is an optional waveform
reading tool, not a dependency for running the Tcl.

Run from the repository root; each Jasper run uses its own project:

```bash
cd test/cti-fifo-refinement/neutral
jg -no_gui -proj runs/baseline -tcl baseline.tcl
cd ..
jg -no_gui -proj runs/initial_helpers -tcl initial_helpers.tcl
jg -no_gui -proj runs/helper_sst -tcl diagnose_helper.tcl
jg -no_gui -proj runs/refined -tcl prove_refined.tcl
python3 collect_evidence.py
```

| Stage | Fixed configuration | Expected observation |
|---|---|---|
| baseline | Original target, `H AM N`, 120 s proof budget | `P0` is `undetermined` |
| initial_helpers | Prove the control relations first, then the data helper with `H AM N`, 20 s | Data helper is `undetermined`; stop here, do not reuse the unproven relation |
| helper_sst | Same control relations; `-sst 2 -engine_mode B`, 10 s | Data helper still `undetermined`; a `tag SST` trace is exported |
| refined | Add the capacity bound and prove it first; data helper still `H AM N`, 20 s | All helpers and `P0` are `proven`, validity is `proven`, the proof is unbounded; the read cover is `covered` |

The time limits are proof-command budgets, not the run time of the whole Jasper
process. Different versions, machines, and solver choices can change run time, the
trace, and even the baseline result; `undetermined` only means no conclusion within
this budget. If your baseline proves the target directly, record that result and do
not edit the report to claim it did not converge.

`proof_utils.tcl` checks status, validity, and unbounded results before reusing each
relation; the new capacity relation is an assertion, not an environment assume. The
scripts do not modify the DUT, do not black-box or cut points, and do not use
`marked_proven`. The read cover is solved separately. The warning that Jasper
ignores `initial` blocks is visible in the log; the proof uses the explicit reset
configured by `setup.tcl`.

All results are generated locally:

- `neutral/evidence/baseline.txt` and `neutral/runs/baseline/`: baseline report and full log.
- `evidence/initial_helpers.txt`, `helper_sst.txt`, `refined.txt`: per-stage reports.
- `evidence/helper_sst.vcd`: diagnostic waveform of the current run; target-related signals only.
- `runs/<stage>/sessionLogs/session_*/jg_session_*.log`: raw logs.
- `evidence/results.json`: statuses, log line numbers, hashes, and check results extracted by the Python script.

`collect_evidence.py` does not run proofs and does not generate preset results; it
reads the latest session log of each project. Only when all checks are `true` does
the current rerun show the comparison in the table. If a run is missing or the
results differ, it keeps the actual results and returns non-zero. The property
`time` field in the logs must not be taken as the total time of all helpers plus the
original target.

**Reading the current SST**

With TraceWeave, use `get_formal_paths`, `get_waveform_summary`, `search_signals`,
`get_signals_around_time` in order. Confirm the trace kind from the log first, then
confirm the time scale from the waveform summary; read `o_fill`, `wr_addr`,
`rd_addr`, `watched_address`, `watched_data`, the corresponding `mem` slot of the
adjacent states, and the pre-transition `w_wr`, `w_rd`, `i_data`, `i_reset`. Without
TraceWeave, a VCD viewer can read the same signals. First explain how the old
relations allow that state, then derive the missing relation from the RTL, and
finally return to an ordinary proof to verify.

These scripts reproduce an already-determined fix; they are not a program that
synthesizes helpers automatically from arbitrary traces. The repository commits
only source, provenance, and rerun/blind-test notes; run results, the WeChat
article draft, and figures are not committed.
