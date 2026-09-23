**Synchronous FIFO verification task**

The DUT is a public-domain synchronous FIFO. It is instantiated with 32-bit data,
32 entries, registered reads, and both optional full-write/empty-read modes off.
The observer records the last accepted write at an arbitrary fixed extended
pointer value. `testbench.P0` checks the output when this position is the nonempty
head. `testbench.C_read` witnesses a read from that position.

Work only on the files in this workspace and artifacts you generate here.
Do not inspect other experiments, solutions, reference proofs, or upstream formal
instrumentation. Attribution in the source is not permission to fetch solutions.
Use only the reference material explicitly made available for this session.

First run the supplied baseline unchanged, from this directory:

```bash
jg -no_gui -proj runs/baseline -tcl baseline.tcl
```

Prove the original `testbench.P0`, or report an evidence-backed unresolved result.
Keep `sfifo.v`, `tb.sv`, the clock/reset setup, and the input environment unchanged.
The watched address is arbitrary but stable. Read/write requests and data remain
unrestricted; the DUT decides which operations are accepted.

The session budget is 15 minutes. All Jasper invocations combined have a
300-second wall-clock budget, including the baseline. Run Jasper jobs serially.
Use the same installed Jasper version and machine throughout. Stop when either
budget is exhausted; do not convert an unfinished proof into a success claim.

Deliver `final.tcl`, runnable from a new Jasper project, and `FINAL_REPORT.md`.
Record every Jasper invocation, elapsed time, source changes, the final status,
validity status, and bounds of the original target and any supporting obligations.
Point each result to its raw log and line. Preserve the raw logs and any diagnostic
artifacts locally. A reachable read cover is required alongside a proof claim.
