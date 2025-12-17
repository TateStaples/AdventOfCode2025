#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

# Use a separate dune build dir to avoid locking conflicts with editor tooling.
export DUNE_BUILD_DIR="${DUNE_BUILD_DIR:-_build_ci}"

mkdir -p build

# Per-design wall-clock timeout for verilog generation (seconds).
# Default: 3 minutes.
EXPORT_TIMEOUT_SECS="${AOC_EXPORT_TIMEOUT_SECS:-180}"

targets=("$@")
if [[ ${#targets[@]} -eq 0 ]]; then
	while IFS= read -r t; do
		[[ -z "${t}" ]] && continue
		targets+=("${t}")
	done < <(opam exec -- dune exec -- ./bin/main.exe --list-verilog)
fi

for t in "${targets[@]}"; do
	out="build/${t}.v"

	if [[ -s "${out}" ]]; then
		echo "Skip (exists): ${out}"
		continue
	fi

	tmp_out="${out}.tmp"
	rm -f "${tmp_out}"

	set +e
	python3 scripts/run_with_timeout.py --timeout-secs "${EXPORT_TIMEOUT_SECS}" -- \
		opam exec -- dune exec -- ./bin/main.exe --verilog "${t}" > "${tmp_out}"
	rc=$?
	set -e

	if [[ $rc -eq 124 ]]; then
		echo "Timeout (skipping): ${t} (${EXPORT_TIMEOUT_SECS}s)" >&2
		rm -f "${tmp_out}"
		continue
	elif [[ $rc -ne 0 ]]; then
		echo "Verilog export failed (skipping): ${t} (exit ${rc})" >&2
		rm -f "${tmp_out}"
		continue
	fi

	if [[ ! -s "${tmp_out}" ]]; then
		echo "Verilog export produced empty output (skipping): ${t}" >&2
		rm -f "${tmp_out}"
		continue
	fi

	mv -f "${tmp_out}" "${out}"
	echo "Wrote: ${out}"
done
