#!/usr/bin/env bash
# blind_ab.sh — enforceable double-blind skill A/B runner (Claude & Codex).
#
# Implements test/BLIND_TEST_PROTOCOL.md Part II as MECHANICS, so blind-test
# compliance does not depend on an agent "remembering" the rules:
#   - per-arm skill isolation via an agent-home sandbox
#   - pre-launch leak scan of what the agents can read
#   - auditable manifest (RTL sha256, jg version, skill commit)
#   - post-run leak cross-check of the no_skill transcript
#   - Option-A cold replay of each arm's FINAL script -> fair engine-time
#
# DRY-RUN BY DEFAULT for the agent-launch step: it PRINTS the exact
# env-isolated `claude`/`codex` command for you to review the flags, and only
# runs it if you pass --execute (after you have confirmed the flags). Every
# other step (scaffold, sha256, leak scan, replay, metric extraction) actually
# runs — they are deterministic and side-effect-safe.
#
# Usage:
#   benchmarks/blind_ab.sh init      <case_dir> <top_module>
#   benchmarks/blind_ab.sh prompts   <case_dir> <top_module>
#   benchmarks/blind_ab.sh launch    <case_dir> <top_module> <ns|sk> <claude|codex> [--execute]
#   benchmarks/blind_ab.sh leakcheck <case_dir>
#   benchmarks/blind_ab.sh replay    <case_dir>
#   benchmarks/blind_ab.sh install-skill
#
# <case_dir> SHOULD live OUTSIDE this repo (Axis A: no relative path to knowledge/).
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_DIR="$REPO/adapters/claude-code"                 # canonical formal-verification skill
PROTOCOL="$REPO/test/BLIND_TEST_PROTOCOL.md"
JG="$(command -v jg || echo /tools/cadence/jasper_2025.12p002/bin/jg)"

# Forbidden technique tokens — the neutral benchmark must NOT contain these,
# and the no_skill transcript must NOT have read skill paths.
LEAK_TOKENS='CAG|cag|proof_structure|compositional|assume.guarantee|memory abstraction|symbolic slot|counter abstraction|helper assertion|invariant|stopat|black.?box|raw-docs|solution'
SKILL_PATH_TOKENS='knowledge/fpv|adapters/claude-code|tool-specific/jaspergold|formal-verification|proof_structure|compositional'

die(){ echo "ERROR: $*" >&2; exit 1; }
have(){ command -v "$1" >/dev/null 2>&1; }
RG(){ if have rg; then rg "$@"; else grep -rEn "$@"; fi; }

# Claude writes transcripts to <CONFIG_DIR>/projects/<encoded-cwd>/<uuid>.jsonl
# where encoded-cwd = the absolute cwd with every '/' and '_' replaced by '-'.
encode_cwd(){ echo "$1" | sed 's#[/_]#-#g'; }

cmd_init(){
  local case="$1" top="${2:-}"
  [ -n "$top" ] || die "usage: init <case_dir> <top_module>"
  case="$(cd "$case" && pwd)"
  case "$case" in "$REPO"/*) echo "WARN: case_dir is inside the skill repo — Axis A (isolation) is weaker; prefer a path outside $REPO." ;; esac

  mkdir -p "$case/blind/no_skill" "$case/blind/skill"
  # Per-arm agent-home sandboxes (Axis B). Mirror the real home via symlinks so
  # auth/settings carry over, but override the skills dir per arm.
  for arm in ns sk; do
    local sb="$case/.blind_sbox/$arm"
    rm -rf "$sb"; mkdir -p "$sb/skills"
    # mirror ~/.claude entries except skills (so auth/config still resolve).
    # Include dotfiles (.credentials.json etc.) — auth lives there.
    if [ -d "$HOME/.claude" ]; then
      for e in "$HOME/.claude"/* "$HOME/.claude"/.[!.]*; do
        [ -e "$e" ] || continue
        local b; b="$(basename "$e")"
        # skip skills (controlled per-arm) and projects (per-arm transcripts, so
        # leakcheck can attribute them — never symlink projects to the shared dir)
        case "$b" in skills|projects) continue;; esac
        ln -sfn "$e" "$sb/$b"
      done
      mkdir -p "$sb/projects"
    fi
  done
  # sk arm gets the skill; ns arm deliberately does not.
  ln -sfn "$SKILL_DIR" "$case/.blind_sbox/sk/skills/formal-verification"
  echo "  sk sandbox skill: $(ls -l "$case/.blind_sbox/sk/skills/formal-verification" | sed 's/.* -> //')"
  echo "  ns sandbox skill: (none — $(ls -A "$case/.blind_sbox/ns/skills" | wc -l) entries)"

  # Manifest (auditable fixtures)
  local man="$case/blind/MANIFEST.txt"
  {
    echo "# blind A/B manifest — $(date -Iseconds)"
    echo "case_dir: $case"
    echo "top_module: $top"
    echo "jg: $("$JG" -version 2>/dev/null | head -1 || echo 'unknown')"
    echo "skill_commit: $(git -C "$REPO" rev-parse HEAD 2>/dev/null || echo 'n/a')"
    echo "rtl_sha256:"
    find "$case" -maxdepth 1 -name '*.sv' -o -maxdepth 1 -name '*.v' 2>/dev/null | sort | while read -r f; do
      [ -f "$f" ] && echo "  $(sha256sum "$f")"
    done
  } > "$man"
  echo "  manifest: $man"

  # Neutral benchmark README (no technique leak)
  cat > "$case/blind/README.md" <<EOF
# Neutral JasperGold FPV benchmark

Task: prove the embedded assertions for top module \`$top\`.
- Use the RTL files in the case root as the design under test; do NOT edit them.
- Write scripts/logs/reports only under your assigned blind/<arm>/ workspace.
- If your result depends on any modeling assumption/abstraction/bind helper,
  prove helpers before use and DISCLOSE the assumption; do not call an
  abstracted result an unqualified raw-RTL signoff.
- Do not read other testcase dirs, prior reports, or any solution material.
EOF

  echo "== leak scan of benchmark (must be clean) =="
  cmd_leakscan_files "$case"
  echo "init OK. Next: benchmarks/blind_ab.sh launch $case $top ns <claude|codex>"
}

cmd_leakscan_files(){
  local case="$1"
  # Scan ONLY the files an agent reads as the benchmark (RTL + READMEs), not the
  # whole tree — avoids false positives from archived runs and needs no rg globs.
  local files=()
  while IFS= read -r f; do files+=("$f"); done < <(find "$case" -maxdepth 1 \( -name '*.sv' -o -name '*.v' -o -name 'README.md' \) 2>/dev/null)
  [ -f "$case/blind/README.md" ] && files+=("$case/blind/README.md")
  if [ "${#files[@]}" -gt 0 ] && grep -nEi "$LEAK_TOKENS" "${files[@]}" 2>/dev/null \
       | grep -vi 'do not\|disclose\|modeling assumption'; then
    echo "  !! benchmark/README may leak a technique — review the hits above"
  else
    echo "  benchmark clean (no technique tokens; scanned ${#files[@]} files)"
  fi
}

cmd_prompts(){
  local case="$1" top="${2:-<top_module>}"
  case="$(cd "$case" && pwd)"
  cat <<EOF
================= NO_SKILL (ns) prompt =================
You are Agent NS for a blind JasperGold FPV experiment.
Work only under $case ; write artifacts only under $case/blind/no_skill .
Do NOT use any formal-verification skill, and do NOT read knowledge/adapters/
tool-specific/raw-docs/extractions or any other testcase or prior report.
Use only general JasperGold knowledge and the RTL + README in $case .
Do NOT edit the benchmark RTL. If your result needs a modeling assumption
beyond the RTL, disclose it and do not call it an unqualified raw-RTL proof.
Goal: full-prove the embedded assertions for top module $top using batch jg.
Leave run.sh + RESULT.md (commands, proven/cex/undet counts, covers, whether
raw-RTL full proof, any assumptions, log paths).

================= SKILL (sk) prompt =================
You are Agent SK for a blind JasperGold FPV experiment.
Work only under $case ; write artifacts only under $case/blind/skill .
The task is intentionally neutral. You MAY use the formal-verification skill.
Do NOT read other testcase dirs, prior reports, raw-docs, extractions, or
solution archives. Do NOT edit the benchmark RTL; disclose any modeling
assumption and do not call an abstracted result an unqualified raw-RTL proof.
Goal: full-prove the embedded assertions for top module $top using batch jg.
Leave run.sh + RESULT.md (commands, why you chose the method, proven/cex/undet
counts, covers, whether raw-RTL full proof, any assumptions, log paths).
EOF
}

cmd_launch(){
  local case="$1" top="$2" arm="$3" agent="$4" exec="${5:-}"
  case="$(cd "$case" && pwd)"
  [ "$arm" = ns ] || [ "$arm" = sk ] || die "arm must be ns|sk"
  local sb="$case/.blind_sbox/$arm"
  [ -d "$sb" ] || die "sandbox missing — run 'init' first"
  local prompt; prompt="$(cmd_prompts "$case" "$top" | awk -v a="$arm" '
     /NO_SKILL \(ns\)/{p=(a=="ns")} /SKILL \(sk\)/{p=(a=="sk")} p&&!/====/{print}')"

  echo "# ---- DRY-RUN: review these flags before running with --execute ----"
  case "$agent" in
    claude)
      # CLAUDE_CONFIG_DIR redirects ~/.claude so the skills dir (hence skill
      # availability) is the per-arm sandbox. VERIFY this env var for your version.
      cat <<EOF
cd "$case"
env CLAUDE_CONFIG_DIR="$sb" claude -p "$(echo "$prompt" | tr '\n' ' ')"
# transcript will land in: $sb/projects/$(encode_cwd "$case")/<uuid>.jsonl
EOF
      ;;
    codex)
      # CODEX_HOME redirects ~/.codex similarly. VERIFY for your version.
      cat <<EOF
cd "$case"
env CODEX_HOME="$sb" codex exec "$(echo "$prompt" | tr '\n' ' ')"
# transcript will land under: $sb/sessions/<YYYY>/<MM>/<DD>/rollout-*.jsonl
EOF
      ;;
    *) die "agent must be claude|codex" ;;
  esac
  echo "# ------------------------------------------------------------------"
  if [ "$exec" = "--execute" ]; then
    echo "(--execute requested: uncomment the runner below once flags are confirmed)"
    # cd "$case" && env CLAUDE_CONFIG_DIR="$sb" claude -p "$prompt"
    die "guarded: edit the script to enable --execute after verifying flags"
  fi
}

cmd_leakcheck(){
  set +e
  local case="$1"; case="$(cd "$case" && pwd)"
  local enc; enc="$(encode_cwd "$case")"
  # Real-leak signals only (NOT mere word mentions, which the prompt's own
  # prohibition text would false-positive on):
  #  - a `"name":"Skill"` tool invocation  (loading the formal-verification skill)
  #  - the CONTIGUOUS repo path awesome-formal-verification-skill/(knowledge|adapters|
  #    tool-specific) in a tool call — the prompt never writes that path contiguously.
  local repore='awesome-formal-verification-skill/(knowledge|adapters|tool-specific)'
  for arm in ns sk; do
    local key; key="$(armkey "$arm")"
    local pj="$case/.blind_sbox/$arm/projects/$enc"
    if [ ! -d "$pj" ]; then echo "  [$key] no per-arm transcript dir yet ($pj)"; continue; fi
    local skill_tool=0 repo_hits=0 t
    for t in "$pj"/*.jsonl; do
      [ -f "$t" ] || continue
      skill_tool=$(( skill_tool + $(grep -c '"name":"Skill"' "$t" 2>/dev/null) ))
      repo_hits=$(( repo_hits + $(grep -cE "$repore" "$t" 2>/dev/null) ))
    done
    if [ "$arm" = ns ]; then
      if [ "$skill_tool" -eq 0 ] && [ "$repo_hits" -eq 0 ]; then
        echo "  [no_skill] PASS — Skill-tool=0, skill-repo file hits=0 → valid blind arm"
      else
        echo "  [no_skill] FAIL — Skill-tool=$skill_tool, skill-repo hits=$repo_hits → arm INVALID"
      fi
    else
      echo "  [skill] Skill-tool=$skill_tool, skill-repo hits=$repo_hits (informational; sk may use the skill)"
    fi
  done
}

# Option-A cold replay: rerun each arm's FINAL script in a fresh proj (no cache),
# extract wall + max IPF057 engine-time + final counts. THIS is the auditable,
# cross-comparable engine-time number (the in-flight jgproject is contaminated by
# engine contention / ProofMaster cache hits, so replay even though it's kept).
cmd_replay(){
  local case="$1"; case="$(cd "$case" && pwd)"
  local ts; ts="$(date +%Y%m%d_%H%M%S)"
  printf '%-9s %-8s %-12s %s\n' ARM WALL MAX_ENGINE FINAL
  for arm in no_skill skill; do
    local d="$case/blind/$arm"
    [ -d "$d" ] || { echo "  (no $arm dir)"; continue; }
    local tcl; tcl="$(ls "$d"/prove_full.tcl 2>/dev/null || ls -t "$d"/*.tcl 2>/dev/null | head -1)"
    [ -n "$tcl" ] || { echo "  ($arm: no .tcl found)"; continue; }
    rm -rf "$d"/pm_cache 2>/dev/null || true          # force cold proof
    local proj="jgproject_replayA_$ts"
    local s e; s=$(date +%s)
    ( cd "$d" && "$JG" -batch -tcl "$(basename "$tcl")" -proj "$proj" > "replayA_${ts}.log" 2>&1 ) || true
    e=$(date +%s)
    local sl="$d/$proj/sessionLogs/session_0/jg_session_0.log"
    local maxe; maxe="$(grep -hoE 'proven (unreachable )?in [0-9.]+ s' "$sl" 2>/dev/null \
                        | grep -oE '[0-9.]+ s' | sort -rn | head -1)"
    local fin; fin="$(grep -hE 'NON-PROVEN ASSERTION COUNT|assert/proven' "$d/replayA_${ts}.log" 2>/dev/null | tail -1)"
    printf '%-9s %-8s %-12s %s\n' "$arm" "$((e-s))s" "${maxe:-?}" "${fin:-?}"
    echo "    log: $d/replayA_${ts}.log   sessionLog: $sl"
  done
}

cmd_install_skill(){
  local src="$REPO/benchmarks/blind_ab_skill"
  [ -f "$src/SKILL.md" ] || die "missing $src/SKILL.md"
  for root in "$HOME/.claude/skills" "$HOME/.codex/skills"; do
    [ -d "$(dirname "$root")" ] || continue
    mkdir -p "$root"; ln -sfn "$src" "$root/blind-ab"
    echo "  linked $root/blind-ab -> $src"
  done
}

armkey(){ [ "$1" = ns ] && echo no_skill || echo skill; }

# Real background launch of one arm: PID file + budget + wall + transcript capture.
# Prompt comes from <case>/.blind_sbox/<arm>_prompt.txt (falls back to generated).
cmd_run(){
  local case="$1" top="$2" arm="$3" agent="${4:-claude}" budget="${5:-1800}"
  case="$(cd "$case" && pwd)"
  [ "$arm" = ns ] || [ "$arm" = sk ] || die "arm must be ns|sk"
  local key; key="$(armkey "$arm")"
  local sb="$case/.blind_sbox/$arm"; [ -d "$sb" ] || die "run 'init' first"
  local pf="$case/.blind_sbox/${arm}_prompt.txt"
  if [ ! -f "$pf" ]; then
    cmd_prompts "$case" "$top" | awk -v a="$arm" '
      /NO_SKILL \(ns\)/{p=(a=="ns")} /SKILL \(sk\)/{p=(a=="sk")} p&&!/====/{print}' > "$pf"
  fi
  mkdir -p "$case/blind/$key"
  # transcripts land in the arm's OWN sandbox projects dir (init no longer
  # symlinks projects), so each arm's transcript is cleanly attributable.
  local projdir="$sb/projects/$(encode_cwd "$case")"
  ls "$projdir"/*.jsonl 2>/dev/null | sort > "$case/blind/$key/.before_jsonl"
  local extra=""; [ "$arm" = sk ] && extra="--add-dir $REPO"
  # generate a self-contained runner so we avoid inline-quoting hazards
  local rs="$case/.blind_sbox/run_${arm}.sh"
  cat > "$rs" <<RUN
#!/bin/bash
s=\$(date +%s)
cd "$case" || exit 1
timeout $budget env CLAUDE_CONFIG_DIR="$sb" claude -p "\$(cat "$pf")" \
    --permission-mode bypassPermissions $extra > "$case/blind/$key/agent_stdout.log" 2>&1
e=\$(date +%s); echo \$((e-s)) > "$case/blind/$key/wall_seconds.txt"
comm -13 "$case/blind/$key/.before_jsonl" <(ls "$projdir"/*.jsonl 2>/dev/null | sort) \
    > "$case/blind/$key/transcript_paths.txt"
RUN
  chmod +x "$rs"
  setsid bash "$rs" < /dev/null > "$case/blind/$key/run_nohup.log" 2>&1 &
  echo $! > "$case/blind/$key/agent.pid"
  echo "[$key] launched pid $(cat "$case/blind/$key/agent.pid")  budget=${budget}s"
  echo "  watch: $0 watch $case   |   stop: $0 stop $case $arm"
}

cmd_watch(){
  set +e   # read-only reporter: never let a no-match grep abort the watch
  local case="$1"; case="$(cd "$case" && pwd)"
  echo "== blind A/B watch: $case  ($(date +%T)) =="
  for arm in ns sk; do
    local key; key="$(armkey "$arm")"; local d="$case/blind/$key"; [ -d "$d" ] || continue
    local pid st; pid="$(cat "$d/agent.pid" 2>/dev/null || true)"; st="finished"
    { [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; } && st="RUNNING"
    local wall ntcl njg jg last verdict
    wall="$(cat "$d/wall_seconds.txt" 2>/dev/null || true)"
    ntcl="$(ls "$d"/*.tcl 2>/dev/null | wc -l)"; njg="$(ls -d "$d"/proj_* 2>/dev/null | wc -l)"
    jg="no"; pgrep -f "$key"/'proj' >/dev/null 2>&1 && jg="yes"
    last="$(ls -t "$d"/*.log 2>/dev/null | head -1)"
    verdict="$(grep -hiE 'proven +: *[0-9]+|covered +: *[0-9]+|NON-PROVEN ASSERTION COUNT|cex +: *[0-9]+' "$last" 2>/dev/null | tail -3 | tr -s ' ' | tr '\n' '|')"
    printf '  [%-8s] %-8s wall=%-5s tcl=%s jg_runs=%s jg_now=%s\n' "$key" "$st" "${wall:-…}s" "$ntcl" "$njg" "$jg"
    [ -n "$verdict" ] && echo "             last: $verdict"
    [ -f "$d/RESULT.md" ] && echo "             RESULT.md ✓"
  done
}

# Safe stop: kill the arm's setsid process-group via its PID file (no pkill -f
# self-match). Optional arm = ns|sk|both.
cmd_stop(){
  set +e   # cleanup path: best-effort kills, never abort on a missing pid/match
  local case="$1" which="${2:-both}"; case="$(cd "$case" && pwd)"; local me=$$
  for arm in ns sk; do
    case "$which" in both) ;; "$arm") ;; *) continue;; esac
    local key; key="$(armkey "$arm")"; local d="$case/blind/$key"
    local pid; pid="$(cat "$d/agent.pid" 2>/dev/null || true)"
    if [ -n "$pid" ]; then kill -- -"$pid" 2>/dev/null || true; kill "$pid" 2>/dev/null || true; echo "stopped $key (pgid $pid)"; fi
    local pat="$key"/'proj'                       # assembled so this script's own cmdline can't match
    for p in $(pgrep -f "$pat" 2>/dev/null); do [ "$p" = "$me" ] && continue; kill "$p" 2>/dev/null || true; done
  done
}

case "${1:-}" in
  init)         shift; cmd_init "$@";;
  prompts)      shift; cmd_prompts "$@";;
  launch)       shift; cmd_launch "$@";;
  run)          shift; cmd_run "$@";;
  watch)        shift; cmd_watch "$@";;
  stop)         shift; cmd_stop "$@";;
  leakcheck)    shift; cmd_leakcheck "$@";;
  replay)       shift; cmd_replay "$@";;
  install-skill) shift; cmd_install_skill "$@";;
  *) sed -n '2,40p' "$0"; exit 1;;
esac
