# mem_ctrl_orig Blind JasperGold Result

## Scope

Allowed benchmark files analyzed as DUT:

- `test/mem_ctrl_orig/simple_mem_design.sv`
- `test/mem_ctrl_orig/mem_ctrl_top.sv`

No benchmark RTL files were edited or replaced. All generated artifacts are under `test/mem_ctrl_orig/blind/no_skill`.

## Scripts

- `run.sh` creates `runs/<timestamp>/`, changes into that directory, and invokes `jg -no_gui -proj <run>/jgproject -tcl <script>`.
- `prove_top_targets.tcl` analyzes the raw benchmark RTL, elaborates `mem_ctrl_top`, declares `clk`/`rst`, proves `mem_ctrl_top.ctrl_readback_ok`, covers `mem_ctrl_top.ctrl_transaction_seen`, and reports the summary.
- `prove_raw.tcl` analyzes the same raw benchmark RTL and runs `prove -all`.

## Commands Run

Focused completed top-target run:

```sh
cd /home/robin/Projects/awesome-formal-verification-skill/test/mem_ctrl_orig/blind/no_skill
./run.sh
```

Clean completed run directory:

```text
runs/20260624_165725
```

Raw all-property attempt:

```sh
cd /home/robin/Projects/awesome-formal-verification-skill/test/mem_ctrl_orig/blind/no_skill
./run.sh prove_raw.tcl
```

The preserved raw all-property attempt is in:

```text
runs/20260624_165306
```

That attempt was manually interrupted after the top assertion had proven and JasperGold continued spending time on `mem_ctrl_top.u_mem.mem_works_ndc`.

## Completed Top-Target Result

From `runs/20260624_165725/jg_console.log`:

- `mem_ctrl_top.ctrl_readback_ok`: proven in 85.96 s.
- `mem_ctrl_top.ctrl_transaction_seen`: covered in 4 cycles.
- JasperGold exited with status 0.

Summary from the completed focused run:

```text
Total Properties      : 7
  assumptions         : 2 temporary
  assertions          : 2 total, 1 proven, 1 unprocessed
  covers              : 3 total, 1 covered, 2 unprocessed
```

The unprocessed assertion/cover items are from properties not targeted by `prove_top_targets.tcl`, including the instantiated memory-wrapper assertion.

## Raw All-Property Attempt

From `runs/20260624_165306/jg_console.log`:

- `mem_ctrl_top.ctrl_readback_ok`: proven in 17.24 s during the raw `prove -all` attempt.
- `mem_ctrl_top.ctrl_transaction_seen`: covered in 4 cycles.
- `mem_ctrl_top.u_mem.mem_works_ndc:precondition1`: covered in 4 cycles.
- `mem_ctrl_top.u_mem.mem_works_ndc`: not discharged before interruption; engines hit 1 s, 10 s, and 100 s per-property scans and continued retrying.

## Signoff Statement

Raw RTL proof of the top-level `mem_ctrl_top` assertion `ctrl_readback_ok` was achieved on the benchmark RTL.

An unqualified full raw-RTL proof of every embedded assertion below `mem_ctrl_top` was not achieved, because the instantiated `simple_mem` assertion `u_mem.mem_works_ndc` remained unresolved in the all-property attempt.

No additional bind files, helper assertions, constraints, abstractions, or modeling assumptions were added by these scripts. The only assumptions reported by JasperGold are the two temporary assumptions already embedded in the benchmark RTL: `stable_addr` and `stable_data` in `simple_mem`.
