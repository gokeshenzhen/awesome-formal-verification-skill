#!/usr/bin/env bash
set -euo pipefail

arm_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
case_dir=$(cd "$arm_dir/../.." && pwd)
stamp=$(date +%Y%m%d_%H%M%S)
run_dir="$arm_dir/baseline_runs/$stamp"

mkdir -p "$run_dir"
export CASE_DIR="$case_dir"
cd "$run_dir"

echo "RUN_DIR=$run_dir"
echo "COMMAND=/usr/bin/time -p -o $run_dir/wall_time.txt jg -no_gui -proj $run_dir/jgproject -tcl $case_dir/baseline.tcl"
/usr/bin/time -p -o "$run_dir/wall_time.txt" \
  jg -no_gui -proj "$run_dir/jgproject" -tcl "$case_dir/baseline.tcl"
cp "$run_dir/jgproject/jg_console.log" "$run_dir/jg.log"
