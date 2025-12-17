#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

# Use a separate dune build dir to avoid locking conflicts with editor tooling.
export DUNE_BUILD_DIR="${DUNE_BUILD_DIR:-_build_ci}"

mkdir -p build

TOPS=()
while IFS= read -r t; do
	[[ -z "${t}" ]] && continue
	TOPS+=("${t}")
done < <(opam exec -- dune exec -- ./bin/main.exe --list-verilog)

echo "== Build Hardcaml =="
opam exec -- dune build ./bin/main.exe ./bin/bench.exe

echo "== Export Verilog =="
./scripts/export_verilog.sh "${TOPS[@]}"

echo "== Yosys synth + stat =="
./scripts/yosys_synth.sh "${TOPS[@]}"

echo "== Cyclesim microbenchmarks =="

# Per-design wall-clock timeout for the Cyclesim benchmark executable.
# Default: 3 minutes.
BENCH_TIMEOUT_SECS="${AOC_BENCH_TIMEOUT_SECS:-180}"

out_cycles="build/bench_cycles.csv"
rm -f "${out_cycles}"

echo "design,day,variant,work_units,cycles,ok" > "${out_cycles}"

for t in "${TOPS[@]}"; do
	out_one="build/bench_cycles_${t}.csv"

	if [[ -s "${out_one}" ]]; then
		echo "Skip (exists): ${out_one}"
		tail -n +2 "${out_one}" >> "${out_cycles}" || true
		continue
	fi

	rm -f "${out_one}"

	set +e
	python3 scripts/run_with_timeout.py --timeout-secs "${BENCH_TIMEOUT_SECS}" -- \
		opam exec -- dune exec -- ./bin/bench.exe --out "${out_one}" --target "${t}"
	rc=$?
	set -e

	if [[ $rc -eq 124 ]]; then
		echo "Timeout (skipping): bench ${t} (${BENCH_TIMEOUT_SECS}s)" >&2
		rm -f "${out_one}"
		continue
	elif [[ $rc -ne 0 ]]; then
		echo "Bench failed (skipping): ${t} (exit ${rc})" >&2
		rm -f "${out_one}"
		continue
	fi

	if [[ -s "${out_one}" ]]; then
		tail -n +2 "${out_one}" >> "${out_cycles}" || true
	fi
done

echo "== Combine results =="
python3 scripts/combine_results.py --cycles build/bench_cycles.csv --yosys-dir build --out build/bench_results.csv

echo "Wrote: build/bench_cycles.csv build/bench_results.csv"
