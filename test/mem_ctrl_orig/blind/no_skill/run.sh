#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
bench_dir=$(cd "$script_dir/../.." && pwd)
tcl_name=${1:-prove_top_targets.tcl}
run_id=$(date +%Y%m%d_%H%M%S)
run_dir="$script_dir/runs/$run_id"
proj_dir="$run_dir/jgproject"

case "$tcl_name" in
  /*) tcl_path="$tcl_name" ;;
  *) tcl_path="$script_dir/$tcl_name" ;;
esac

if [[ ! -f "$tcl_path" ]]; then
  echo "Tcl script not found: $tcl_path" >&2
  exit 2
fi

mkdir -p "$run_dir"

export BENCH_DIR="$bench_dir"
export RUN_DIR="$run_dir"
export PROJ_DIR="$proj_dir"
export TCL_PATH="$tcl_path"

cd "$run_dir"

#jg -no_gui -proj "$proj_dir" -tcl "$tcl_path" 2>&1 | tee "$run_dir/jg_console.log"
jg -proj "$proj_dir" -tcl "$tcl_path" 2>&1 | tee "$run_dir/jg_console.log"
