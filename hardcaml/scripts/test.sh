#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

# Default: 10 minutes. Override via env var.
: "${AOC_DUNE_TEST_TIMEOUT_SECS:=600}"

echo "== dune test (verbose, no-buffer) =="
echo "timeout: ${AOC_DUNE_TEST_TIMEOUT_SECS}s"

# Notes:
# - --no-buffer makes test output stream immediately (helps diagnose stalls).
# - --display verbose makes dune print what it's doing.
python3 scripts/run_with_timeout.py \
  --timeout-secs "${AOC_DUNE_TEST_TIMEOUT_SECS}" \
  -- \
  opam exec -- dune test --display verbose --no-buffer "$@"
