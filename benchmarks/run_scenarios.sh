#!/usr/bin/env bash
# run_scenarios.sh — run the FPV benchmark scenarios through a headless agent and
# grade each against its expected tokens.
#
# Requires: the formal-verification skill installed for the chosen runtime, and
# that runtime's CLI on PATH. Runs every scenario in benchmarks/fpv/scenarios.json
# with the skill available, then reports — separately — how many CONCEPT tokens
# (general methodology) and EXACT tokens (tool-specific JG commands) appear.
#
# The split is the point: distillation loss shows up as missing EXACT tokens while
# CONCEPT tokens are often recovered by the model itself. A control scenario should
# hit both; a loss-probe scenario typically hits concept but misses exact.
#
# The runtime that answers each prompt is AUTO-DETECTED from the agent you launch
# this script from — no manual flag needed:
#   • inside Claude Code  → `claude -p`
#   • inside Codex        → `codex exec`
# Both get the SAME skill via `bash scripts/install.sh`, which symlinks the one
# canonical skill dir (adapters/claude-code) into each agent's skills directory
# (~/.claude/skills for claude, ~/.codex/skills for codex). So: update the skill
# with whichever agent you use, then just run this script there — it picks the
# matching CLI automatically. Override with RUNTIME=claude|codex if ever needed.
#
# Usage:
#   bash benchmarks/run_scenarios.sh                          # all scenarios (auto runtime)
#   bash benchmarks/run_scenarios.sh config-logic-cutpoint    # one by id
#   RUNTIME=codex bash benchmarks/run_scenarios.sh            # force Codex CLI
#   MODEL=gpt-5.5 bash benchmarks/run_scenarios.sh <scenario> # pin Codex model
#   OUT=/tmp/fpv-eval bash benchmarks/run_scenarios.sh        # custom output dir
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JSON="$HERE/fpv/scenarios.json"
OUT="${OUT:-/tmp/fpv-eval/$(date +%Y%m%d-%H%M%S)}"
ONLY="${1:-}"
TIMEOUT="${TIMEOUT:-220}"
MODEL="${MODEL:-}"

# Auto-detect the calling agent runtime (override with RUNTIME=claude|codex).
detect_runtime() {
  case "${AI_AGENT:-}" in
    claude*) echo claude; return ;;
    codex*)  echo codex;  return ;;
  esac
  [ -n "${CLAUDECODE:-}${CLAUDE_CODE_SESSION_ID:-}" ] && { echo claude; return; }
  [ -n "${CODEX_SANDBOX:-}${CODEX_SESSION_ID:-}${CODEX_INTERNAL_ORIGINATOR_OVERRIDE:-}" ] && { echo codex; return; }
  # Not inside a known agent → fall back to whichever CLI is installed.
  command -v claude >/dev/null && { echo claude; return; }
  command -v codex  >/dev/null && { echo codex;  return; }
  echo none
}
RUNTIME="${RUNTIME:-$(detect_runtime)}"

# Invoke the detected runtime headlessly; print the agent's answer to stdout.
run_agent() { # prompt
  case "$RUNTIME" in
    claude) timeout "$TIMEOUT" claude -p "$1 Answer in English. Be concise." </dev/null ;;
    codex)
      local args=(exec --ephemeral -s read-only)
      [ -n "$MODEL" ] && args+=(-m "$MODEL")
      timeout "$TIMEOUT" codex "${args[@]}" "$1 Answer in English. Be concise." </dev/null
      ;;
    *) echo "ERROR: no supported agent runtime (claude/codex) detected." >&2; return 1 ;;
  esac
}

case "$RUNTIME" in
  claude) command -v claude >/dev/null || { echo "ERROR: runtime=claude but 'claude' CLI not on PATH."; exit 1; } ;;
  codex)  command -v codex  >/dev/null || { echo "ERROR: runtime=codex but 'codex' CLI not on PATH.";  exit 1; } ;;
  *) echo "ERROR: could not detect a supported agent runtime; set RUNTIME=claude or RUNTIME=codex."; exit 1 ;;
esac
command -v python3 >/dev/null || { echo "ERROR: python3 required to read scenarios.json."; exit 1; }
mkdir -p "$OUT"

# emit "id<TAB>type<TAB>prompt<TAB>concept|csv<TAB>exact|csv" per scenario
read_scenarios() {
  python3 - "$JSON" "$ONLY" <<'PY'
import json, sys
data = json.load(open(sys.argv[1]))
only = sys.argv[2]
for s in data["scenarios"]:
    if only and s["id"] != only:
        continue
    print("\t".join([s["id"], s["type"], s["prompt"],
                     ",".join(s.get("expect_concept", [])),
                     ",".join(s.get("expect_exact", []))]))
PY
}

grade() { # file, csv-of-regexes  → prints "hit/total"
  local f="$1" csv="$2" hit=0 tot=0
  [ -z "$csv" ] && { echo "0/0"; return; }
  IFS=',' read -ra pats <<< "$csv"
  for p in "${pats[@]}"; do
    tot=$((tot+1))
    grep -qiE "$p" "$f" && hit=$((hit+1))
  done
  echo "$hit/$tot"
}

echo "FPV scenario benchmark — runtime=$RUNTIME — output in $OUT"
printf "%-30s %-11s %-10s %-10s\n" "scenario" "type" "concept" "exact(JG)"
printf "%-30s %-11s %-10s %-10s\n" "------------------------------" "-----------" "--------" "---------"
while IFS=$'\t' read -r id type prompt concept exact; do
  f="$OUT/$id.txt"
  err="$OUT/$id.stderr"
  rc=0
  run_agent "$prompt" > "$f" 2>"$err" || rc=$?
  if [ "$rc" -ne 0 ] || [ ! -s "$f" ]; then
    printf "%-30s %-11s %-10s %-10s  \u2190 agent ERROR (rc=%s; see %s)\n" \
      "$id" "$type" "ERROR" "ERROR" "$rc" "$err"
    continue
  fi
  c=$(grade "$f" "$concept")
  e=$(grade "$f" "$exact")
  flag=""
  [ -n "$exact" ] && [ "${e%/*}" = "0" ] && flag="  ← EXACT JG command missing (distillation loss)"
  printf "%-30s %-11s %-10s %-10s%s\n" "$id" "$type" "$c" "$e" "$flag"
done < <(read_scenarios)

echo
echo "Interpretation: control scenarios should hit concept AND exact. A loss-probe that"
echo "hits concept but misses exact = the dropped JG command/flag is a real, model-unrecoverable loss."
