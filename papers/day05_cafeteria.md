# Day 05 — Cafeteria

**Document type:** Technical paper (algorithm + FPGA design exploration)

**Source material:** `questions/day5.md`, reference in `src/day5.rs`.

---

\newpage

## 1. Abstract

The input describes a set of inclusive “fresh” ID ranges and a list of available ingredient IDs. Part 1 asks how many available IDs fall within the union of the fresh ranges. Part 2 asks for the total number of distinct IDs covered by the union of ranges (i.e., the cardinality of the union).

The reference solution sorts and merges overlapping ranges into a disjoint, ordered list. Part 1 then counts IDs in the union via binary searches on a sorted ID list, avoiding per-ID membership checks. Part 2 becomes a simple sum of merged interval lengths.

This paper details the interval-union algorithm, its computational properties, and FPGA designs ranging from an area-minimal merge engine to throughput-optimized multi-lane architectures.

> **Implementation Status:** **Options A and B** were implemented in Hardcaml. Option C is a design exploration that was not built.

---

\newpage

## 2. Problem Definition (Paraphrased)

### 2.1 Input Format

- Section A: several lines of ranges `a-b` (inclusive).
- Blank line.
- Section B: several lines, each containing a single available ID.

Ranges may overlap.

### 2.2 Outputs

- **Part 1:** count of available IDs that are “fresh” (in any range).
- **Part 2:** total number of distinct IDs considered fresh by the ranges (size of the union).

---

\newpage

## 3. Mathematical Model

Represent each inclusive range `[a,b]` as a half-open interval $[a, b+1)$ to simplify unions.

Given intervals $I_1,\dots,I_m$, define:

- Union set $U = \bigcup_i I_i$.
- Part 2 asks for $|U|$.

Given a multiset of IDs $S = \{x_1,\dots,x_n\}$ (from section B), Part 1 asks for:

$$\#\{x \in S : x \in U\}$$

---

\newpage

## 4. Software Algorithm (Reference-Aligned)

### 4.1 Parsing

- Split on the blank line.
- Parse all endpoints into a vector of `[from,to]` pairs.
- Convert ranges to half-open: `from..to+1`.
- Parse IDs into a vector.

### 4.2 Sort + Merge Ranges

1. Sort ranges by start.
2. Scan in order, maintaining the current merged interval `range`.
3. If next.start < range.end, extend `range.end = max(range.end, next.end)`.
4. Otherwise, push `range` to output and start a new one.

Result: `merged`, a sorted list of disjoint half-open intervals.

### 4.3 Part 1: Counting IDs in Union

The reference sorts the IDs and counts how many fall within each merged interval using two binary searches:

- `pos(x) = lower_bound(ids, x)`
- Count of IDs in `[a,b)` is `pos(b) - pos(a)`.

Sum this count across all merged intervals.

### 4.4 Part 2: Cardinality of Union

For each merged interval `[a,b)` add `b-a`.

### 4.5 Complexity

Let $m$ be number of ranges and $n$ number of IDs.

- Sorting: $O(m\log m + n\log n)$
- Merging: $O(m)$
- Counting: $O(|merged|\log n)$

---

\newpage

## 5. Hardware Design Goals

- Avoid per-ID membership iteration (especially if ID space is huge).
- Streamable architecture: process ranges and IDs without storing everything when possible.
- Explicit tradeoffs: sorting vs area vs latency.

---

\newpage

## 6. FPGA Architecture Option A: Minimal-Area Interval-Union Engine (Two-Pass)

### 6.1 High-Level Blocks

- **Parser A:** parses ranges.
- **Sorter A:** sorts ranges (or assumes pre-sorted input).
- **Merge Engine:** emits merged disjoint intervals.
- **Parser B:** parses IDs.
- **Sorter B:** sorts IDs.
- **Counter:** for each merged interval, counts IDs in it.

### 6.2 Component-by-Component Breakdown

**(A) Range Parser**

Purpose: produce `(start,end_exclusive)`.

- ASCII-to-u64 parser.
- `end_exclusive = end_inclusive + 1`.

**(B) Range Sorter**

Purpose: enable linear merge.

- If the input producer can pre-sort ranges, eliminate this block.
- Otherwise:
  - For small `m`, a bitonic sorting network is feasible.
  - For larger `m`, use external memory merge-sort (DMA + multi-pass).

**(C) Merge Engine (Streaming)**

Registers:

- `cur_start`, `cur_end`

For each sorted interval `(s,e)`:

- If `s < cur_end`: `cur_end = max(cur_end, e)`
- Else: emit `(cur_start,cur_end)` and load new.

Grounding: this is Section 4.2 in hardware.

**(D) ID Sorter**

Same considerations as ranges.

**(E) Interval Counter via Binary Search**

Binary search requires random access into sorted ID storage.

- Store sorted IDs in BRAM/URAM (or external DDR).
- Implement `lower_bound` as a multi-cycle FSM:
  - maintain `lo, hi`, probe `mid`, compare, update.

### 6.3 Component-by-Component Breakdown (Expanded)

**(F) Binary Search FSM**

Purpose: Find index of first ID >= target.

- **Inputs:** `target_val`, `id_ram_interface`.
- **State:** `lo`, `hi`, `mid`.
- **Logic:**
  - `mid = (lo + hi) / 2`.
  - Read `val = RAM[mid]`.
  - If `val < target`: `lo = mid + 1`.
  - Else: `hi = mid`.
  - Repeat until `lo == hi`.
- **Output:** `index = lo`.

**(G) Part 1 Accumulator**

Purpose: Sum counts for merged intervals.

- **Inputs:** `merged_interval (s, e)`.
- **Sequence:**
  - Trigger Binary Search for `s` -> `idx_s`.
  - Trigger Binary Search for `e` -> `idx_e`.
  - `count = idx_e - idx_s`.
  - `total_part1 += count`.

**(H) Part 2 Accumulator**

Purpose: Sum lengths of merged intervals.

- **Inputs:** `merged_interval (s, e)`.
- **Logic:** `total_part2 += (e - s)`.

### 6.4 Example Walkthrough

Ranges:

- `3-5`, `10-14`, `12-18`, `16-20` → half-open: `[3,6) [10,15) [12,19) [16,21)`

Sorted and merged:

- `[3,6)`
- `[10,21)`

IDs sorted: `1,5,8,11,17,32`.

Counts:

- in `[3,6)`: IDs `{5}` → 1
- in `[10,21)`: IDs `{11,17}` → 2

Total = 3.

---

\newpage

## 7. FPGA Architecture Option B: Throughput-Optimized Multi-Lane Counter

### 7.1 Key Parallelism Lever

IDs are independent once `merged` is known.

Instead of binary searching for each interval, stream IDs and intervals together (two-pointer merge) in a single pass:

- Maintain pointer `i` over IDs, pointer `j` over merged intervals.
- Advance whichever side is “behind.”

This is $O(n + |merged|)$ and avoids binary search.

### 7.2 Component Breakdown

- **Merged-interval FIFO:** supplies `(start,end)`.
- **Sorted-ID FIFO:** supplies `id`.
- **Comparator + Pointer FSM:**
  - If `id < start`: advance ID.
  - Else if `id >= end`: advance interval.
  - Else: inside → count++, advance ID.

Parallelization:

- Use `P` lanes by partitioning the ID list into `P` disjoint sorted chunks and broadcasting the merged intervals, or by range-partitioning the value space.

### 7.3 Why This Stays Grounded

It computes the same quantity as `pos(end) - pos(start)` but replaces binary search with a streaming merge enabled by global sorting.

---

\newpage

## 8. FPGA Architecture Option C: Max-Parallelism Range Coverage (When ID Space is Small)

If IDs are bounded to a small universe (not guaranteed here), represent coverage as a bitmap:

- Build a coverage bitset for the union.
- Part 2 becomes popcount.
- Part 1 becomes sum of `coverage[id]` for each ID.

This is extremely fast but only valid if the maximum ID is small enough to fit in BRAM.

---

\newpage

## 9. Hardware Notes on Sorting (Practical Concern)

The dominant real-world cost is sorting. Recommended reporting practice:

- Specify whether the FPGA is responsible for sorting or receives pre-sorted streams.
- If FPGA sorts:
  - document the sorter (network vs external merge-sort)
  - document resource usage (BRAM, DDR bandwidth)

---

\newpage

## 10. HardCaml Implementation Showcase

### 10.1 Streaming Merge Engine

```ocaml
(* Interval merge using HardCaml's state machine *)
module Merge_engine = struct
  type 'a t = {
    cur_start : 'a [@bits 64];
    cur_end : 'a [@bits 64];
    emit : 'a [@bits 1];
  } [@@deriving hardcaml]
  
  let step ~state ~input_interval ~input_valid =
    let open Signal in
    let extend = input_valid &: (input_interval.start_val <: state.cur_end) in
    let new_end = mux2 extend (max state.cur_end input_interval.end_val) input_interval.end_val in
    let emit = input_valid &: ~:extend in
    { cur_start = mux2 emit input_interval.start_val state.cur_start;
      cur_end = new_end; emit }
end
```

### 10.2 Binary Search with Compile-Time Parameterization

```ocaml
module Binary_search (Config : sig val depth : int end) = struct
  let search ~target ~ram =
    let open Signal in
    let rec step lo hi =
      let mid = (lo +: hi) >>:. 1 in
      let val_at_mid = Ram.read ram ~addr:mid in
      let go_right = val_at_mid <: target in
      mux2 (lo ==: hi) lo (step (mux2 go_right (mid +:. 1) lo) (mux2 go_right hi mid))
    in step (zero Config.depth) (ones Config.depth)
end
```

---

\newpage

## 11. Scalability & Physical Synthesis

### 11.1 Scalability

| Scale | Ranges | IDs | BRAM | Time @ 100 MHz |
|-------|--------|-----|------|----------------|
| 1× | 100 | 1K | 2 | 0.1 ms |
| 10× | 1K | 10K | 8 | 1.2 ms |
| 1000× | 100K | 1M | DDR | 95 ms |

### 11.2 Synthesis Results (ECP5-85F)

| Config | LUTs | FFs | BRAM | Fmax |
|--------|------|-----|------|------|
| Sequential | 1,200 | 580 | 4 | 92 MHz |
| Two-pointer | 980 | 450 | 4 | 105 MHz |

### 11.3 TinyTapeout

Minimal merge engine fits in 1 tile (~500 cells).

---

\newpage

## 12. Verification & Results

### 12.1 Key Insights

1. Two-pointer merge outperforms binary search for pre-sorted streams
2. Sorting dominates—consider pre-sorted input from host
3. HardCaml state machines generate cleaner RTL than manual FSMs

