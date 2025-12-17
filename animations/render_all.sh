#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Config:
# - Set MANIM to an explicit manim binary path if desired.
# - Set MANIM_FLAGS to change quality (default: -ql).
#   Examples:
#     MANIM_FLAGS='-pqh' ./render_all.sh
#     MANIM_FLAGS='-pql --disable_caching' ./render_all.sh

if [[ -n "${MANIM:-}" ]]; then
	MANIM_CMD="$MANIM"
elif [[ -x "$SCRIPT_DIR/../.venv/bin/manim" ]]; then
	MANIM_CMD="$SCRIPT_DIR/../.venv/bin/manim"
elif command -v manim >/dev/null 2>&1; then
	MANIM_CMD="$(command -v manim)"
else
	echo "Error: manim not found. Set MANIM or create ../.venv with manim installed." >&2
	exit 1
fi

MANIM_FLAGS="${MANIM_FLAGS:--ql}"
read -r -a MANIM_FLAGS_ARR <<< "$MANIM_FLAGS"

render() {
	local file="$1"
	local scene="$2"

	echo "Rendering ${scene} (${file})..."
	if ! "$MANIM_CMD" "${MANIM_FLAGS_ARR[@]}" "$file" "$scene"; then
		FAILURES+=("${scene} (${file})")
		echo "WARNING: Failed to render ${scene} (${file}); continuing..." >&2
		return 0
	fi
}

FAILURES=()

render day1.py Day1
render day2.py Day2
render day3.py Day3
render day4.py Day4
render day5.py Day5
render day6.py Day6
render day7.py Day7
render day8.py Day8
render day9.py Day9
render day10.py Day10
render day11.py Day11
render day12.py Day12

if [[ -f "bonus_series.py" ]]; then
	render bonus_series.py BonusReel
fi

if (( ${#FAILURES[@]} > 0 )); then
	echo "" >&2
	echo "Finished with failures:" >&2
	for item in "${FAILURES[@]}"; do
		echo "- ${item}" >&2
	done
	exit 1
fi

echo "All animations rendered."
