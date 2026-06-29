# cnt_abs formal-verification report

Files:

- [Main checker](</home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/cnt_abs/no_skill/cnt_abstract_eg_checker.sv:1>)
- [A reachability helper](</home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/cnt_abs/no_skill/reach_checker.sv:1>)
- [A bind file](</home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/cnt_abs/no_skill/bind_reach_a.sv:1>)
- [B bind file](</home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/cnt_abs/no_skill/bind_reach_b.sv:1>)

What I wrote:

- For the main proof, I encoded the RTL intent as:
  - `!C` and `!D` remain true after reset.
  - `cntr == 32'd8369262 |=> A`
  - `A |=> A`
  - `cntr == 32'd268407145 |=> B`
  - `B |=> B`
- For non-vacuity, I used separate helper witnesses:
  - `cover property (@(posedge clk) sig);` with `sig=A` and `cntr=THR_A-1`
  - `cover property (@(posedge clk) sig);` with `sig=B` and `cntr=THR_B-1`

Exact JasperGold commands run:

- Main raw-RTL attempt:
  - `jg -batch -proj no_skill/proj_20260629_121257 -tcl no_skill/run_jg.tcl`
  - `jg -batch -proj no_skill/proj_20260629_121345 -tcl no_skill/run_jg.tcl`
  - `jg -batch -proj no_skill/proj_main_init_20260629_122958 -tcl no_skill/run_main_init.tcl`
- Helper non-vacuity witnesses:
  - `jg -batch -proj no_skill/proj_reach_a_20260629_122524 -tcl no_skill/run_reach_a.tcl`
  - `jg -batch -proj no_skill/proj_reach_b_20260629_122545 -tcl no_skill/run_reach_b.tcl`

Status:

- I did not obtain an unqualified raw-RTL signoff.
- The raw-proof run with formal reset did not converge to a final summary before I stopped it.
- The non-vacuity witnesses completed under explicit `reset -init_state` abstractions, so they are valid reachability demonstrations but not raw-RTL signoff.

Completed counts:

- Raw abstraction run `no_skill/proj_20260629_121345`:
  - assertions: 4 proven, 2 cex, 0 undetermined
  - covers: 6 covered, 0 unreachable, 0 undetermined
  - This was not a signoff-quality run.
- Helper A witness `no_skill/proj_reach_a_20260629_122524`:
  - assertions: 0
  - covers: 1 covered, 0 unreachable
- Helper B witness `no_skill/proj_reach_b_20260629_122545`:
  - assertions: 0
  - covers: 1 covered, 0 unreachable

Interpretation:

- `A` and `B` are sticky-set bits driven by the internal counter thresholds.
- `C` and `D` are reset-only outputs and are intended to stay low.
- The helper runs show the A/B trigger states are reachable under a disclosed init-state abstraction.

Wall-clock timing:

- Start of the first Jasper run: 2026-06-29 12:08:11 CST
- First completed proof result in this session: 2026-06-29 12:24:57 CST
- Elapsed time to that first completed proof result: about 16m 46s

Logs:

- Main raw attempt logs:
  - [no_skill/proj_20260629_121257/jg_console.log](</home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/cnt_abs/no_skill/proj_20260629_121257/jg_console.log>)
  - [no_skill/proj_20260629_121345/jg_console.log](</home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/cnt_abs/no_skill/proj_20260629_121345/jg_console.log>)
  - [no_skill/proj_main_init_20260629_122958/jg_console.log](</home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/cnt_abs/no_skill/proj_main_init_20260629_122958/jg_console.log>)
- Helper witnesses:
  - [no_skill/proj_reach_a_20260629_122524/jg_console.log](</home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/cnt_abs/no_skill/proj_reach_a_20260629_122524/jg_console.log>)
  - [no_skill/proj_reach_b_20260629_122545/jg_console.log](</home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/cnt_abs/no_skill/proj_reach_b_20260629_122545/jg_console.log>)

Notes:

- The helper witnesses rely on explicit `reset -init_state` files:
  - [no_skill/init_a.txt](</home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/cnt_abs/no_skill/init_a.txt>)
  - [no_skill/init_b.txt](</home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/cnt_abs/no_skill/init_b.txt>)
  - [no_skill/init_reset.txt](</home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/cnt_abs/no_skill/init_reset.txt>)
- Because the non-vacuity proof was satisfied with an init-state abstraction, I am not calling the result raw-RTL signoff.
