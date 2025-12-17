# Advent of Code 2025 (Days 1–6) — Efficient Hardware Project Plan (Hardcaml)

This document is a hardware-oriented project plan for implementing the AoC 2025 puzzles currently present in this repo’s [questions](../../questions) directory (Days 1–6) using Hardcaml.

Goals:
- Maximize **throughput** and exploit **parallelism** aggressively.
- Keep designs **streaming** where possible (avoid full-input buffering).
- When parallelism and efficiency conflict, provide at least two plausible architectures and describe tradeoffs.

Non-goals:
- Perfect minimum-area implementations.
- Handling arbitrary AoC input delivery mechanisms; we assume a host can stream ASCII over a simple interface (file → simulation, or UART/AXI-stream in FPGA).

---

## Common Infrastructure (used by all days)

### A. Input ingestion + parsing primitives
- **ASCII byte stream** interface: `valid/data/ready`.
- Shared parsing blocks:
  - `parse_uint` FSM: ASCII digits → binary integer (configurable width), emits `(value, value_valid)`.
  - `skip_spaces/newlines` helpers.
  - Optional `parse_signed` for Day 1 (direction + magnitude) if you choose to allow signed distances; otherwise parse magnitude as unsigned.
- **Line buffering (optional)**:
  - For “grid / column layout” problems (Day 4, Day 6), plan for BRAM-backed line buffers with an address counter.

### B. Reduction trees
- Parameterized **adder tree** and (if needed) **multiplier tree**.
- Pipelined variants to hit timing at higher clock rates.

### C. Multi-engine parallel scheduler (optional)
For days where input can be decomposed into independent “chunks” (Day 2, potentially Day 6), provide:
- A dispatcher that sends work items to `P` identical engines.
- A completion collector that reduces partial sums.

### D. Verification strategy (common)
- Each day gets a Hardcaml sim harness + a software golden model.
  - Golden model can be the Rust solver already in `src/`.
- Tests:
  - Example from the puzzle statement (where given).
  - Property tests on random small inputs (especially Day 1, Day 2 pattern detection, Day 4 peeling).
  - Cross-check against Rust outputs for the real input files under `inputs/`.

---

## Day 1 — Secret Entrance

### Problem recap
Stream of instructions `L|R` with a distance. Dial is modulo 100.
- Part 1: count times the dial ends at 0 after each rotation.
- Part 2: count number of *clicks* that land on 0 while rotating (includes intermediate wraps).

### Plan A (recommended): 1-instruction/clock streaming update
**Key idea**: compute wrap-counts with integer arithmetic; do not simulate per click.

Data path per instruction:
- `pos` register (0..99)
- Parse `dir` and `mag` (wide enough for worst-case, e.g. 32-bit)
- Compute:
  - `pos_next = (pos ± mag) mod 100`
  - `p1_inc = (pos_next == 0)`
  - `p2_inc`:
    - If `R`: `floor((pos + mag)/100)`
    - If `L`: equivalent formula using “reverse dial” trick:
      - `rev = (100 - pos) mod 100`
      - `p2_inc = floor((rev + mag)/100)`

Parallelism:
- Purely streaming; throughput is fixed at 1 instruction/cycle.
- If input parse becomes the bottleneck, instantiate multiple parsers and interleave instructions (but usually unnecessary).

Tradeoffs:
- **Pros**: tiny area, fully streaming, constant work per instruction.
- **Cons**: limited parallelism because the state (`pos`) is sequential.

### Plan B: block-parallel prefix composition (only if you need more throughput)
Batch `K` instructions, compute each instruction as an affine transform on the state:
- Each instruction becomes `(delta mod 100, p1_count_contrib(state), p2_wraps_contrib(state))`.
- Combine with parallel prefix to process `K` instructions in `O(log K)` stages.

Tradeoffs:
- **Pros**: higher throughput if you can buffer and batch.
- **Cons**: much more complex (state-dependent contributions), likely not worth it.

Milestones:
1. Reuse/extend the existing plan in [hardcaml/day1_plan.md](../day1_plan.md).
2. Implement Day 1 as baseline reference for the rest of the year.

---

## Day 2 — Gift Shop

### Problem recap
Input: comma-separated ID ranges `lo-hi`.
Compute the **sum** of “invalid” IDs in all ranges.
- Part 1 invalid: digits = (some sequence) repeated exactly twice.
- Part 2 invalid: digits = (some sequence) repeated ≥2 times.

### Plan A (recommended for “maximize parallelism”): parallel range partitioning
This matches the approach described in [hardcaml/day2_parallel_design.md](../day2_parallel_design.md).

Architecture:
- Split each input range into `P` subranges.
- `P` checkers iterate in parallel, each producing partial sums for part1/part2.
- Tree-reduce partial sums.

Hot spots:
- BCD incrementer or digit-extraction pipeline.
- Pattern checker: compare digit blocks for each divisor of length.

Tradeoffs:
- **Pros**: straightforward scaling with `P`; easy to reason about.
- **Cons**: still does work per number; can be expensive if ranges are large.

### Plan B (often more efficient): generate invalid IDs, then intersect with ranges
Instead of scanning every ID, **enumerate invalid IDs** by construction:
- For each period `p` and repetition count `k` (k=2 for part1; k>=2 for part2), generate base digits `B` (no leading zeros), form `B` repeated `k` times.
- For each generated invalid ID `x`, add `x` if it lies in any range.

Hardware sketch:
- Generator farm: many small counters for `B` in base-10 with fixed digit width.
- Range membership: store merged ranges in BRAM and do pipelined binary search or linear scan (ranges are usually few).

Tradeoffs:
- **Pros**: complexity proportional to number of invalid IDs, not range width; can be dramatically faster.
- **Cons**: needs careful bounding on digit lengths; generator space can still be large for big max-length.

Recommendation:
- Implement Plan A first (already documented), then add Plan B as an “accelerator mode” for very large ranges.

---

## Day 3 — Lobby

### Problem recap
Each line is a bank of digits (joltage ratings). You must choose:
- Part 1: pick exactly **2 digits** in order → maximize 2-digit number.
- Part 2: pick exactly **12 digits** in order → maximize 12-digit number.
Sum the per-line maxima.

Observations:
- This is “maximum subsequence” / “lexicographically maximum subsequence of fixed length”.

### Plan A (recommended): streaming greedy with small per-line state
#### Part 1 (2 digits)
Streaming scan of digits `d[i]`:
- Keep `best_first` = max digit seen so far (with earliest index preference)
- Keep `best_pair` = best 2-digit result so far
- Update by comparing `best_first*10 + d[i]` against current `best_pair`.

Parallelism:
- Pipeline the compare/update so you can accept 1 digit per cycle.

#### Part 2 (12 digits)
Greedy selection for fixed-length max subsequence:
- Let `N` be line length.
- Need to delete `N-12` digits.
- Standard approach uses a small stack and “pop while you can improve and still have enough remaining”.

Hardware approach:
- A 12-entry register file (the “stack”) + a `drops_remaining` counter.
- Each new digit may trigger a few pops; to keep throughput high:
  - **Option A**: allow multi-cycle per digit when popping (simplest).
  - **Option B**: unroll comparisons with a bounded pop depth per cycle (if N is small and bounded).

Tradeoffs:
- **Pros**: minimal memory, fully streaming.
- **Cons**: worst-case variable work per digit (pop loop) complicates 1-digit/cycle guarantee.

### Plan B (maximize parallelism): fixed-length line + combinational selection network
If line length is bounded (it appears fixed-width in your inputs), you can build a selection network:
- Compute the best digit for position 0 by taking the max over a window.
- Then position 1 from the remaining suffix, etc.

Tradeoffs:
- **Pros**: high parallelism; can be pipelined to constant throughput.
- **Cons**: large comparator network; less flexible if `N` varies.

Recommendation:
- Start with Plan A; if timing/throughput is insufficient, move to Plan B assuming fixed `N` per line.

---

## Day 4 — Printing Department

### Problem recap
Grid of `@` and `.`.
- Part 1: count `@` cells with <4 occupied neighbors (8-neighborhood).
- Part 2: repeatedly remove all currently-accessible `@` (same rule) until no more can be removed; return total removed.

### Plan A (maximize parallelism): bit-parallel stencil + iterative peeling
Represent each row as a bitset (1 for `@`).

Stencil computation per iteration:
- For each row `y`, use a 3-row sliding window: `row[y-1], row[y], row[y+1]`.
- Compute neighbor count bits using shifted versions:
  - `nw = row[y-1] << 1`, `n = row[y-1]`, `ne = row[y-1] >> 1`,
  - `w = row[y] << 1`, `e = row[y] >> 1`,
  - `sw = row[y+1] << 1`, `s = row[y+1]`, `se = row[y+1] >> 1`.
- Build a popcount-per-bit “adder tree” (this is the expensive part): sum eight 1-bit fields into a 4-bit count per cell.

Accessible mask:
- `acc = occupied & (neighbor_count < 4)`

Part 1:
- Single pass, popcount `acc` for all rows.

Part 2:
- Iterate:
  - compute `acc`
  - `occupied := occupied & ~acc`
  - accumulate `removed += popcount(acc)`
- Stop when `acc` is all zeros.

Parallelism:
- Extremely high inside the stencil; process `W` columns per cycle where `W` is your bitset width (e.g., 256/512/1024 bits).

Tradeoffs:
- **Pros**: very high throughput, elegant data-parallel structure.
- **Cons**: per-bit popcount stencil is area-heavy; iterative rounds can be many.

### Plan B (more efficiency on sparse grids): event-driven frontier queue
Maintain neighbor counts and a queue of candidate cells:
- Initialize neighbor counts for all occupied cells.
- Push cells with count<4 into a queue.
- Pop cell, if still occupied and count<4, remove it, decrement neighbor counts for neighbors; newly eligible neighbors get queued.

Tradeoffs:
- **Pros**: work proportional to removed cells; great for sparse or quickly-stabilizing grids.
- **Cons**: queue + random neighbor updates are control-heavy; needs BRAM banking and careful arbitration.

Recommendation:
- If you want “showcase parallelism”, do Plan A.
- If you want “best LUT efficiency”, do Plan B.

---

## Day 5 — Cafeteria

### Problem recap
Input:
- A list of inclusive ranges of “fresh” IDs.
- A blank line.
- A list of ingredient IDs.
Part 1 asks: how many IDs are fresh (membership in union of ranges).

### Plan A (recommended): build merged interval set, then pipelined membership checks
Steps:
1. Parse ranges into a small on-chip RAM (ranges count is typically modest).
2. Sort + merge ranges.
   - If range count `R` is small (≤64): use a sorting network or bitonic sorter.
   - Else: stream to external memory and use an external sort (heavier).
3. For each ID, do pipelined binary search over merged ranges.
   - One ID can be accepted each cycle if you pipeline the compare stages.

Parallelism:
- Pipeline depth ~ `log2(R)`.
- You can replicate the range RAM to process multiple IDs/cycle.

Tradeoffs:
- **Pros**: predictable timing; clean separation of “build” then “query”.
- **Cons**: sorting hardware can dominate if `R` is not small.

### Plan B: merge-with-sorted-streams (lower area if you can sort IDs cheaply)
If you can also sort the ID list:
- Do a linear sweep through merged ranges and sorted IDs → O(R + M).

Tradeoffs:
- **Pros**: linear-time after sorting; simpler membership than binary search.
- **Cons**: sorting `M` IDs can be harder than binary searching them.

Recommendation:
- Implement Plan A with assumption `R` is small enough for on-chip sorting.

---

## Day 6 — Trash Compactor

### Problem recap
A very wide “worksheet” of vertical arithmetic problems laid out side-by-side.
Each column-group is a problem:
- Parse its vertically stacked numbers.
- Apply either `+` or `*` for that problem.
- Sum results across all problems.

This is primarily an **ASCII layout + segmentation** hardware problem.

### Plan A (maximize parallelism, robust parsing): two-pass with column segmentation
Assumptions consistent with the statement:
- All problem boundaries are columns where **all rows are spaces**.
- Each problem is bounded by separator columns.

Pipeline:
1. **Capture rows**
   - Buffer each row into BRAM (byte-addressed). You need `H` rows (numbers rows) + 1 operator row.
2. **Compute separator mask**
   - For each column index `x`, compute `sep[x] = AND_over_rows(is_space(row[r][x]))`.
   - Edge-detect `sep` to find `(start_x, end_x)` for each problem.
3. **Dispatch problems to P workers**
   - Each worker parses the substrings `row[r][start_x..end_x]`, extracts the integer (ignore alignment), and folds via `+` or `*`.
4. **Reduce results**
   - Sum all per-problem results in an adder tree.

Parallelism:
- Column segmentation is massively parallel over `x` if you widen the memory interface.
- Parsing/folding is parallel over problems via `P` workers.

Tradeoffs:
- **Pros**: robust to alignment quirks; scales by adding more workers.
- **Cons**: requires buffering full rows; more BRAM bandwidth.

### Plan B (more efficient, less buffering): token-index alignment (assumes consistent tokenization)
If the input is effectively “whitespace-tokenized columns” (i.e., each row has the same number of numeric tokens and problems are separated by 2+ spaces), then:
- Parse each row into a stream of integers.
- Parse operator row into ops.
- Zip by token index.

Tradeoffs:
- **Pros**: streaming, far less memory.
- **Cons**: can break if columns aren’t token-aligned (the statement suggests true column layout).

Recommendation:
- Start with Plan A for correctness and parallelism. Only adopt Plan B if you confirm the token-alignment invariant.

---

## Implementation Roadmap (practical ordering)

1. **Day 1**: finish the “baseline streaming” template (parsing + 1-cycle update).
2. **Day 4**: implement bitset grid + popcount and verify against small examples.
3. **Day 5**: implement range merge + membership pipeline (reusable for Day 2 Plan B as well).
4. **Day 2**: implement Plan A (partitioned range scanning), then optionally Plan B generator.
5. **Day 3**: implement part1 streaming; part2 choose either stack-greedy or fixed-length selection network.
6. **Day 6**: implement two-pass segmentation + worker farm; this one is the “big parser” effort.

---

## Deliverables (per day)
- `hardcaml/lib/dayX_hardware.ml`: synthesizable core
- `hardcaml/bin/sim_dayX.ml`: simulation runner that reads `inputs/X-1*.txt` or a provided path
- `hardcaml/test/test_dayX.ml`: golden comparison tests
- Update/extend the tutorial markdowns in [hardcaml/tutorials](.) with diagrams and performance notes.
