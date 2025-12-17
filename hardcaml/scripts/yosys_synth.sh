#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

# Use a separate dune build dir to avoid locking conflicts with editor tooling.
export DUNE_BUILD_DIR="${DUNE_BUILD_DIR:-_build_ci}"

if ! command -v yosys >/dev/null 2>&1; then
  echo "yosys not found. Install yosys (e.g. brew install yosys) or use a containerized flow." >&2
  exit 1
fi

mkdir -p build

# Per-design wall-clock timeout for synthesis (seconds).
# Default: 3 minutes.
YOSYS_TIMEOUT_SECS="${AOC_YOSYS_TIMEOUT_SECS:-180}"

# Tapeout flow selection:
# - fast (default): quick netlist + stat (no ABC), intended for preliminary numbers.
# - cmos: full synth + CMOS tech stat (slower, more comparable).
YOSYS_FLOW="${AOC_YOSYS_FLOW:-fast}"

tops=("$@")
if [[ ${#tops[@]} -eq 0 ]]; then
  while IFS= read -r t; do
    [[ -z "${t}" ]] && continue
    tops+=("${t}")
  done < <(opam exec -- dune exec -- ./bin/main.exe --list-verilog)
fi

for top in "${tops[@]}"; do
  in_v="build/${top}.v"
  out_stat_json="build/${top}_yosys_stat.json"
  out_rpt="build/${top}_yosys.rpt"

  echo "== Yosys: ${top} =="

  if [[ -s "${out_stat_json}" ]]; then
    echo "Skip (exists): ${out_stat_json}"
    continue
  fi

  if [[ ! -f "${in_v}" ]]; then
    echo "Missing verilog (skipping): ${in_v}" >&2
    continue
  fi

  yosys_script_fast="read_verilog -sv ${in_v}; hierarchy -top ${top}; proc; opt -fast; memory; opt -fast; techmap; opt -fast; stat -json"
  yosys_script_cmos="read_verilog -sv ${in_v}; synth -top ${top}; stat -tech cmos -json"

  if [[ "${YOSYS_FLOW}" == "cmos" ]]; then
    yosys_script="${yosys_script_cmos}"
  else
    yosys_script="${yosys_script_fast}"
  fi

  echo "Run yosys (${YOSYS_FLOW}, timeout=${YOSYS_TIMEOUT_SECS}s): ${top}"

  # Note: `stat -json` prints JSON to stdout.
  # Some designs can take a long time; enforce a per-top timeout and skip on timeout/failure.
  set +e
  python3 scripts/run_with_timeout.py --timeout-secs "${YOSYS_TIMEOUT_SECS}" -- \
    yosys -p "${yosys_script}" 2>"${out_rpt}" | tee "${out_stat_json}" >/dev/null
  rc=$?
  set -e

  if [[ $rc -eq 124 ]]; then
    echo "Timeout (skipping): ${top} (${YOSYS_TIMEOUT_SECS}s)" >&2
    rm -f "${out_stat_json}"
    continue
  elif [[ $rc -ne 0 ]]; then
    echo "Yosys failed (skipping): ${top} (exit ${rc})" >&2
    rm -f "${out_stat_json}"
    continue
  fi

  echo "Wrote: ${out_stat_json} ${out_rpt}"
done
