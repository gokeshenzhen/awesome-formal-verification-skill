#!/usr/bin/env bash
# run_scenarios.sh — run the FPV benchmark scenarios through a headless agent and
# grade each against its expected tokens.
#
# Requires: the formal-verification skill installed (bash scripts/install.sh) and
# the `claude` CLI on PATH. Runs every scenario in benchmarks/fpv/scenarios.json
# with the skill available, then reports — separately — how many CONCEPT tokens
# (general methodology) and EXACT tokens (tool-specific JG commands) appear.
#
# The split is the point: distillation loss shows up as missing EXACT tokens while
# CONCEPT tokens are often recovered by the model itself. A control scenario should
# hit both; a loss-probe scenario typically hits concept but misses exact.
#
# Usage:
#   bash benchmarks/run_scenarios.sh                 # all scenarios
#   bash benchmarks/run_scenarios.sh config-logic-cutpoint   # one by id
#   OUT=/tmp/fpv-eval bash benchmarks/run_scenarios.sh       # custom output dir
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JSON="$HERE/fpv/scenarios.json"
OUT="${OUT:-/tmp/fpv-eval/$(date +%Y%m%d-%H%M%S)}"
ONLY="${1:-}"
TIMEOUT="${TIMEOUT:-220}"
command -v claude >/dev/null || { echo "ERROR: 'claude' CLI not on PATH."; exit 1; }
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

echo "FPV scenario benchmark — output in $OUT"
printf "%-30s %-11s %-10s %-10s\n" "scenario" "type" "concept" "exact(JG)"
printf "%-30s %-11s %-10s %-10s\n" "------------------------------" "-----------" "--------" "---------"
while IFS=$'\t' read -r id type prompt concept exact; do
  f="$OUT/$id.txt"
  timeout "$TIMEOUT" claude -p "$prompt Be concise." > "$f" 2>/dev/null || true
  c=$(grade "$f" "$concept")
  e=$(grade "$f" "$exact")
  flag=""
  [ -n "$exact" ] && [ "${e%/*}" = "0" ] && flag="  ← EXACT JG command missing (distillation loss)"
  printf "%-30s %-11s %-10s %-10s%s\n" "$id" "$type" "$c" "$e" "$flag"
done < <(read_scenarios)

echo
echo "Interpretation: control scenarios should hit concept AND exact. A loss-probe that"
echo "hits concept but misses exact = the dropped JG command/flag is a real, model-unrecoverable loss."
