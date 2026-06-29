# JasperGold Run Report

## Result

I could not complete a raw-RTL proof of the embedded assertion. The license issue was resolved, but the property did not close in the raw proof run, and the non-vacuity witness remained undetermined at the explored bound.

## Exact Commands

1. Created a timestamped project directory under `no_skill/`.
2. Ran:

```bash
jg -batch -proj no_skill/proj_20260629_120646 -tcl no_skill/run.tcl
```

3. Retried fail-fast with:

```bash
jg -batch -no_wait -proj no_skill/proj_20260629_120754 -tcl no_skill/run.tcl
```

3. Reran the same flow after updating the EDA environment troubleshooting skill:

```bash
jg -batch -no_wait -proj no_skill/proj_20260629_121600 -tcl no_skill/run.tcl
```

4. Split the run into a raw-proof flow and a bounded witness flow:

```bash
jg -batch -no_wait -proj no_skill/proj_proof_20260629_130046 -tcl no_skill/prove_only.tcl
jg -batch -no_wait -proj no_skill/proj_cover_20260629_131439 -tcl no_skill/cover_only.tcl
```

## Added Properties / Assumptions

For the final split run:

- `cover -name antecedent_reachable { @(posedge clk) &counter1 }`
- `set_max_trace_length 40` in the witness-only flow

I did not add any modeling assumption. The cover witness was a bounded search aid, not a proven assumption.

I did not add any bind checker, assumption, or auxiliary property. Nothing was proven under assumptions.

## Final Counts

Final raw-proof counts were not reached before I stopped the long-running proof session.

Completed witness-flow counts:

- Proven: 0
- CEX: 0
- Undetermined: 2

- Proven: N/A
- CEX: N/A
- Undetermined: N/A

## Raw-RTL Proof Status

No. The raw proof did not complete, so this is not an unqualified raw-RTL proof.

## Non-Vacuity

Not demonstrated in JasperGold. The bounded witness on `@(posedge clk) &counter1` finished as `undetermined` at bound 41, which is consistent with the antecedent being a deep 32-bit reachability problem.

## Wall-Clock Time

Time from start to first full proof: not reached.

## Logs

- [Batch project 1 console log](/home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/helper_counters/no_skill/proj_20260629_120646/jg_console.log)
- [Batch project 1 stdout](/home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/helper_counters/no_skill/proj_20260629_120646/jg_stdout.log)
- [Batch project 2 console log](/home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/helper_counters/no_skill/proj_20260629_120754/jg_console.log)
- [Batch project 2 stdout](/home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/helper_counters/no_skill/proj_20260629_120754/jg_stdout.log)
- [Batch project 3 console log](/home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/helper_counters/no_skill/proj_20260629_121600/jg_console.log)
- [Batch project 3 stdout](/home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/helper_counters/no_skill/proj_20260629_121600/jg_stdout.log)
- [Raw proof console log](/home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/helper_counters/no_skill/proj_proof_20260629_130046/jg_console.log)
- [Raw proof stdout](/home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/helper_counters/no_skill/proj_proof_20260629_130046/jg_stdout.log)
- [Witness console log](/home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/helper_counters/no_skill/proj_cover_20260629_131439/jg_console.log)
- [Witness stdout](/home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/helper_counters/no_skill/proj_cover_20260629_131439/jg_stdout.log)

## Failure Detail

The earlier problem was license checkout, but that was resolved by using the correct JasperGold batch invocation under the current environment.

The remaining blocker is algorithmic:

- The design is a 32-bit incrementing counter pair.
- The antecedent `&counter1` is a 2^32-state reachability condition from the reset-initialized start state.
- The raw proof did not complete in the time available.
- The bounded witness search also did not reach the antecedent within the explored bound.
