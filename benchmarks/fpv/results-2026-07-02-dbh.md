# DBH Task-Eval Results — 2026-07-02

## Scope

Run the three new Deep Bug Hunting control scenarios with the installed
formal-verification skill and Codex `gpt-5.5`. This is a skill-loaded task eval,
not a manual blind no-skill/skill A/B.

Command shape:

```bash
env RUNTIME=codex MODEL=gpt-5.5 OUT=<output-dir> \
  bash benchmarks/run_scenarios.sh <scenario-id>
```

Committed raw answers and run metadata live in
`benchmarks/fpv/results-2026-07-02-dbh/`. The original full stderr logs remain
under `/tmp/fpv-eval/`; their hashes are preserved in `run-metadata.txt`.

## Results

| Scenario | CONCEPT | EXACT | Raw answer | Runtime evidence |
|---|---:|---:|---|---|
| `dbh-stalled-bound` | 4/4 | 4/4 | `results-2026-07-02-dbh/dbh-stalled-bound.txt` | `results-2026-07-02-dbh/run-metadata.txt` |
| `dbh-known-bug-reproduction` | 4/4 | 5/5 | `results-2026-07-02-dbh/dbh-known-bug-reproduction.txt` | `results-2026-07-02-dbh/run-metadata.txt` |
| `dbh-regression-coverage` | 5/5 | 3/3 | `results-2026-07-02-dbh/dbh-regression-coverage.txt` | `results-2026-07-02-dbh/run-metadata.txt` |

## Grader Calibration

The first successful run exposed two grader-shape issues rather than knowledge
misses:

- Accept Jasper mode identifiers with underscores (`cycle_swarm`,
  `bound_swarm`) as equivalent to prose names.
- Accept both word orders for the exhaustive-unreachability boundary.

The regression prompt was also made explicit that exact Tcl commands are
required. The final scores above were recomputed from the recorded answers using
the checked-in regexes in `benchmarks/fpv/scenarios.json`; no answer text was
edited.

## Conclusion

All three DBH controls hit every expected CONCEPT and EXACT token. Keep the
module at 🔬 **from-docs**: this task eval validates retrieval and routing, not
production correctness or no-skill/skill uplift.
