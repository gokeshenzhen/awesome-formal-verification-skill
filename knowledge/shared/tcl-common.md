# Common TCL Patterns

> 🔬 **from-docs** — Generated from Cadence JasperGold documentation, 2026-06-14. Needs field validation.

Tool-agnostic Tcl language reference for EDA scripting — the language essentials and the HDL-vs-Tcl character conflicts that trip up new users on any formal/simulation tool. For **JasperGold-specific** scripting (`-silent`, `get_design_info`/COI queries, Jasper Tcl differences) see `knowledge/fpv/tcl-commands.md`.

## Core Tcl Rules

1. **Three axioms**: everything is a string; every string is a list; every list is whitespace-separated words.
2. **`{}` = literal (no substitution); `""` = variable/command/character substitution.** Brace anything you want passed through untouched.
3. **Escapes/braces are stripped after ONE evaluation level.** `"abc\[0:7\]"` and `{abc[0:7]}` both evaluate to `abc[0:7]`.
4. **Every command returns a value AND a status** (value may be NULL; status 0=success, 1=failure). Printed output (`puts`) is not the return value.
5. **`$name` substitutes a variable; brace it (`${name}`) when not followed by whitespace.** Array access needs an element: `$arr(elt)` — bare `$arr` is an error.
6. **Always `return` an explicit value from a proc** — otherwise it returns whatever its last command returned.

## The HDL-vs-Tcl Escaping Pitfall

The #1 gotcha when a Tcl script references Verilog/VHDL objects: characters meaningful in HDL collide with Tcl.

- `$` triggers **variable substitution** → escape as `\$` to reference a Verilog system function literally.
- `[ ]` triggers **command substitution** → escape as `\[ \]` to include a Verilog bit-range, or brace the whole string.
- `\\` inserts a literal backslash.

```tcl
set v1 "abc\[0:7\]"   ;# quotes + escapes  → abc[0:7]
set v2 {abc[0:7]}     ;# braces, verbatim  → abc[0:7]
```
Inside `""` escape every `$`/`[` you don't want substituted; inside `{}` nothing is substituted at all (including a real `$var` you *do* want).

## Patterns

### Graceful error handling with `catch`
```tcl
if { [catch {some_command args} msg] } {
  puts "Warning: $msg"      ;# status was 1 → msg = error message
} else {
  set result $msg           ;# status was 0 → msg = return value
}
```
`catch` returns the *status*; the second arg captures the *value* (dual-purpose: error text or result). Use it whenever an argument could be invalid (signal names, file opens) — an unchecked failing command aborts the running script.

### Procs with optional / variadic args
```tcl
proc p {arg1 {arg2 default_value}} { ...; return $result }  ;# optional w/ default
proc p {args} { ...; return $result }                       ;# args = one list of all args
proc p {} { ...; return $result }                           ;# no args: list present but null
```
`args` collects all arguments into one list and allows no defaults.

### Capture a command's value
```tcl
set var [expr 3 * 8]   ;# command substitution → var = 24
```
An invalid `expr` returns error status, leaves `var` unset, and aborts the script unless wrapped in `catch`.

## Tcl Commands by Function

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
| Run shell commands | `exec` (e.g., `exec date {+%Y%m%d %H:%M:%S}`) |

## Package Installation

```tcl
package require <pkg>        ;# import; returns version or errors
lappend auto_path <dir>      ;# add a dir to the running instance (repeat each launch)
# OR set TCLLIBPATH env var  ;# Tcl appends it to auto_path at startup (every instance)
```

## Anti-Pattern Reference

| Anti-Pattern | Why It Fails | Correct Alternative |
|-------------|-------------|-------------------|
| Unescaped Verilog bit-range `sig[0:7]` in a quoted string | `[...]` triggers command substitution | `sig\[0:7\]` or brace `{sig[0:7]}` |
| Unescaped `$` referencing a Verilog system function | `$` triggers variable substitution | `\$func` |
| Bracing a string that contains a `$var` you want expanded | `{}` suppresses ALL substitution | use `""` and escape only what must stay literal |
| Ignoring return status on a fallible command | A failure aborts the whole script | wrap in `catch {cmd} var` |
| Relying on a proc's implicit return | Returns last command's value — fragile | explicit `return` at every exit |
| Bare array name `$myArray` | Error in Tcl | `$myArray(elt)` |

## Further Reading
- For JasperGold-specific Tcl (`-silent`, `get_design_info`/COI queries, `tcl_clock`/`pid` differences, package availability): see `knowledge/fpv/tcl-commands.md`
- For the SVA driven by these scripts: see `knowledge/shared/sva-reference.md`
- Authoritative spec: Tcl 8.6.10 reference — https://www.tcl.tk/man/tcl/TclCmd/contents.htm
