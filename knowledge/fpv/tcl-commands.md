# FPV: TCL Commands

> 🔬 **from-docs** — Generated from Cadence JasperGold documentation, 2026-06-14. Needs field validation. Content is [JG-specific] unless tagged [General Tcl].

## Overview

Writing Tcl for JasperGold/Jasper Apps: the Tcl language essentials that trip up new users (especially the HDL-vs-Tcl character conflicts), and the Jasper-specific scripting idioms (`-silent`, design/COI queries). For the end-to-end command *sequence* of an FPV run file, see `workflow.md`. Consult this module when a script mis-references a signal, mangles a bit-range, swallows an error, or you need a scripted design query.

## Quick Decision Tree

```
Writing Tcl for Jasper?
├─ String contains HDL refs / spaces / special chars?
│   ├─ want it VERBATIM (no substitution) ......... brace it: {sig[0:7]}
│   └─ want substitution but protect some chars ... quote + escape: "...\$func...\[0:7\]..."
├─ Referencing a Verilog bit-range in Tcl? ......... escape brackets: sig\[0:7\]  (or brace)
├─ Referencing a Verilog $system function? ......... escape dollar: \$func
├─ Command argument might be invalid (signal/file)? . wrap in catch {cmd} var  (status 0=ok,1=fail)
├─ Writing a script (not interactive)? ............. add -silent to every Jasper cmd that supports it
└─ Need design/COI facts in a variable? ............ get_design_info / get_signal_info  ... -silent
```

## Core Rules

1. **The three Tcl axioms**: everything is a string; every string is a list; every list is whitespace-separated words. [General Tcl]
2. **`{}` = literal (no substitution); `""` = variable/command/character substitution.** Pick braces to pass HDL references through untouched.
3. **The HDL-vs-Tcl conflict is the #1 pitfall.** `$` triggers variable substitution and `[ ]` triggers command substitution — both collide with Verilog. Escape (`\$`, `\[`) or brace them.
4. **Escapes/braces are stripped after ONE evaluation level.** `"abc\[0:7\]"` and `{abc[0:7]}` both evaluate to `abc[0:7]`.
5. **Every command returns a value AND a status** (value may be NULL; status 0=success, 1=failure). Printed output (`puts`) is not the return value.
6. **Check status with `catch` whenever an argument could be invalid** (signal names, file opens). An unchecked failing command aborts the running script.
7. **Always `return` an explicit value from a proc** — otherwise it returns whatever its last command returned.
8. **In scripts, add `-silent` to Jasper commands** so results come back as clean Tcl values instead of printing.
9. **Brace a variable name (`${var}`) when not followed by whitespace**; array access requires an element (`$arr(elt)` — bare `$arr` is an error).
10. **Know the Jasper Tcl differences**: standard `clock` → `tcl_clock`; `pid` returns the analysis-session PID; some standard packages (Thread, tdbc*) are unavailable.

## Pattern Catalog

### Verbatim vs substituted strings
**When to use**: deciding how to pass an HDL reference into a Jasper command.
**Template**:
```tcl
set v1 "abc\[0:7\]"   ;# quotes + escapes  → abc[0:7]
set v2 {abc[0:7]}     ;# braces, verbatim  → abc[0:7]
```
**Gotchas**: inside `""`, escape every `$` and `[` you don't want substituted; inside `{}`, nothing is substituted at all (including real `$var` you *do* want).

### Graceful error handling with `catch`
**When to use**: any command whose argument might be invalid.
**Template**:
```tcl
if { [catch {some_command args} msg] } {
  puts "Warning: $msg"      ;# msg = error message (status was 1)
} else {
  set result $msg           ;# msg = return value (status was 0)
}
```
**Example**:
```tcl
set myFile "my_file_name"
if { [catch {open $myFile w} msg] } {
  puts "Warning, unable to open ${myFile}: $msg"
} else {
  set fileID $msg
}
```
**Gotchas**: `catch` returns the *status*; the second arg captures the *value* (dual-purpose: error text or result).

### Procs with optional / variadic args
**When to use**: reusable helper procedures.
**Template**:
```tcl
proc p {arg1 {arg2 default_value}} { ...; return $result }  ;# optional w/ default
proc p {args} { ...; return $result }                       ;# args = one list of all args
proc p {} { ...; return $result }                           ;# no args: list present but null
```
**Gotchas**: `args` collects all arguments into one list and allows no defaults; always `return` explicitly.

### Capture a command's value
**Template**:
```tcl
set var [expr 3 * 8]   ;# command substitution → var = 24
```
**Gotchas**: an invalid `expr` returns error status, leaves `var` unset, and aborts the script unless wrapped in `catch`.

### Scripted design & COI queries
**When to use**: introspect the elaborated design inside a script.
**Template**:
```tcl
set modList  [get_design_info -list module -silent]
set instList [get_design_info -module Mod_B2 -list instance -silent]
set width    [get_signal_info -width  wdata0 -silent]     ;# 32
set idx      [get_signal_info -indexes wdata0 -silent]    ;# 1D_Array 31 0
set coiMods  [get_design_info -property myTask::addr_conn0 -list module -silent]
# modules NOT in COI:
set notCOI ""
foreach m [get_design_info -silent -list module] {
  if { [lsearch -exact $coiMods $m] < 0 } { lappend notCOI $m }
}
```
**Gotchas**: without `-silent` these print and return verbose values — unusable in a pipeline.

## Anti-Pattern Reference

| Anti-Pattern | Why It Fails | Correct Alternative |
|-------------|-------------|-------------------|
| Unescaped Verilog bit-range `sig[0:7]` in a quoted string | `[...]` triggers command substitution | `sig\[0:7\]` or brace `{sig[0:7]}` |
| Unescaped `$` referencing a Verilog system function | `$` triggers variable substitution | `\$func` |
| Bracing a string that contains a `$var` you want expanded | `{}` suppresses ALL substitution | use `""` and escape only what must stay literal |
| Ignoring return status on a fallible command | A failure aborts the whole script | wrap in `catch {cmd} var` |
| Relying on a proc's implicit return | Returns last command's value — fragile | explicit `return` at every exit |
| Omitting `-silent` in scripts | Command prints instead of returning a value | add `-silent` |
| Bare array name `$myArray` | Error in Tcl | `$myArray(elt)` |
| Assuming `clock`/`pid` behave as standard Tcl | Jasper renames `clock`→`tcl_clock`; `pid`=analysis-session PID | use `tcl_clock`; know `pid` semantics |

## Tcl Commands by Function (standard Tcl in Jasper)

| Function | Commands |
|---|---|
| Math / increment | `expr`, `incr` |
| File I/O | `open`, `close`, `puts` |
| Regex test / substitute | `regexp`, `regsub` |
| Build a list | `list`, `lappend`, `linsert`, or `{ }` braces |
| Extract from a list | `lindex`, `lrange`, `foreach` |
| Count / search a list | `llength`, `lsearch` |
| Replace / sort a list | `lreplace`, `lsort` |
| String ops | `string` |
| Substitute without executing | `subst` |
| Run Linux commands | `exec` (e.g., `exec date {+%Y%m%d %H:%M:%S}`) |

> 📝 GAP — Jasper Tcl is far larger than this app note covers. Tcl 8.6.10 reference: https://www.tcl.tk/man/tcl/TclCmd/contents.htm

## Package Installation

```tcl
package require <pkg>        ;# import; returns version or errors
lappend auto_path <dir>      ;# add a dir to the running instance (repeat each launch)
# OR set TCLLIBPATH env var  ;# Tcl appends it to auto_path at startup (every instance)
```
Unavailable standard packages in Jasper: `Thread`, `tdbc`, `tdbc::mysql`, `tdbc::odbc`, `tdbc::postgres`.

## Tool-Specific Notes

### JasperGold
- `-silent` is the key scripting switch — returns results as Tcl values instead of printing. Use it on every command that supports it.
- `get_design_info` / `get_signal_info` are the workhorse introspection commands (modules, instances, flops, registers, COI membership, bit width/indexes).
- Jasper Tcl deviates from standard: `clock`→`tcl_clock`; `pid`=analysis-session PID.

### VC Formal
> 📝 GAP — No VC Formal Tcl content in the current sources. To be added.

## Command Reference
| Command | Purpose | Tool |
|---|---|---|
| `set`, `expr`, `incr`, `puts`, `open`, `close` | core Tcl | General Tcl |
| `proc name {args} {body}`, `return` | define procedure / return value | General Tcl |
| `catch {cmd} var` | run cmd; capture status + value | General Tcl |
| `regexp`, `regsub`, `subst`, `string` | regex / substitution / string ops | General Tcl |
| `list`/`lappend`/`linsert`/`lindex`/`lrange`/`foreach`/`llength`/`lsearch`/`lreplace`/`lsort` | list ops | General Tcl |
| `exec` | run Linux commands | General Tcl |
| `package require` / `lappend auto_path` / `TCLLIBPATH` | package import | General Tcl |
| `<cmd> -silent` | return results instead of printing | JG |
| `get_design_info [-list module\|instance\|input\|flop\|register] [-module M] [-property P] -silent` | design / COI queries | JG |
| `get_signal_info -indexes\|-width <sig> -silent` | signal bit range / width | JG |
| `tcl_clock` (vs std `clock`); `pid` | Jasper Tcl differences | JG |

For the full FPV run-file command sequence (`clear`, `analyze`, `elaborate`, `clock`, `reset`, `assume`, `assert`, `cover`, `prove`, `report`, …) see **Command Reference** in `workflow.md`.

## Further Reading
- For the end-to-end FPV run-file order and its commands: see `workflow.md`
- For property declaration syntax (`assert`/`assume`/`cover` bodies): see `property-writing.md`
- For proof/engine settings (`set_proofgrid_*`, `set_proofmaster_*`): see `engine-tuning.md`
- For complexity levers used in setup (`stopat`, `-bbox_*`): see `complexity-management.md`
- Standard Tcl 8.6.10 reference: https://www.tcl.tk/man/tcl/TclCmd/contents.htm
