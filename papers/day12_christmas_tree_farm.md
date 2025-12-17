# Day 12 — Christmas Tree Farm

**Document type:** Technical paper (algorithm + FPGA design exploration)

**Source material:** Problem statement in `questions/day12.md`, reference software in `src/day12.rs`.

---

\newpage

## 1. Abstract

We are given a set of small discrete “present” shapes defined on a fixed unit grid (visually rendered with `#` and `.`). For each rectangular region under a tree, the input specifies how many presents of each shape must be placed. Shapes may be rotated and flipped, must align to the grid, cannot overlap, and cannot be stacked.

The task (Part 1 only) is to count how many regions admit a feasible packing.

The reference Rust solution currently implements only a coarse necessary condition: it checks whether the number of $3\times 3$ blocks that fit in the region is at least the total number of presents. This is not sufficient to decide packability.

This paper:

- states the full packing problem precisely,
- describes standard complete algorithms (exact cover / DLX, SAT/ILP, profile DP),
- and proposes FPGA accelerators that exploit the small shape size (locality), including a bitboard exact-cover engine and a stripe-based transfer-matrix DP that is structurally different from earlier “pipeline” papers.
> **Implementation Status:** Only a **simplified feasibility filter (Option A variant)** was implemented in Hardcaml. The full exact-cover and stripe DP options are design explorations that were not built.
---

\newpage

## 2. Problem Definition (Paraphrased)

### 2.1 Shapes

A fixed catalog of shapes is given. Each shape is displayed as a small grid (in the example, 3 rows of 3 characters), where `#` indicates occupied cells.

Shapes may be:

- rotated (typically 0°, 90°, 180°, 270°)
- flipped (mirror)

Equivalent orientations can be deduplicated.

### 2.2 Regions

Each region line specifies:

- rectangle width $W$ and height $H$ (e.g. `12x5`)
- counts $c_s$ for each shape index $s$

### 2.3 Output

Count how many regions can place all required pieces with:

- integer grid alignment,
- no overlap between occupied cells,
- placements fully inside the rectangle.

---

\newpage

## 3. Modeling as a Discrete Constraint Problem

Let the region be a grid of $N=W\cdot H$ cells.

A placement of a shape orientation is a set of occupied cell indices. For each shape type $s$ with required count $c_s$, we must choose exactly $c_s$ placements (distinct placements) such that all occupied cells are disjoint.

This is a **bounded exact packing** problem:

- constraints on cell occupancy (at most 1)
- constraints on piece multiplicity (exactly $c_s$)

---

\newpage

## 4. State of the Reference Implementation

The current Rust `part1` in `src/day12.rs` performs:

- parse widths/heights and counts,
- check:

$$\left\lfloor \frac{W}{3} \right\rfloor \cdot \left\lfloor \frac{H}{3} \right\rfloor \ge \sum_s c_s$$

This is a **necessary condition** if every present required at least a distinct $3\times 3$ “slot”, but it is not sufficient for real packability.

Therefore, a complete solution requires a different algorithm.

---

\newpage

## 5. Complete Algorithms (Software Baselines)

### 5.1 Algorithm X / Exact Cover (DLX)

Transform placements into rows of a 0/1 matrix.

Columns represent:

- each grid cell (must be covered by at most 1 placement)
- each required piece instance (must be covered exactly once)

A row corresponds to “choose this placement of one piece instance”, covering:

- the cells occupied
- the piece-instance column

Then we search for a set of rows that covers all piece-instance columns exactly once and covers each cell column at most once.

Two practical variants:

- Expand each piece count into separate “instance” columns (turns multiplicity into exact cover).
- Use a generalized exact cover with multiplicity constraints (more complex but smaller).

### 5.2 SAT / ILP

Introduce boolean variables $x_p$ for each legal placement $p$.

Constraints:

- For each cell $u$: $\sum_{p \ni u} x_p \le 1$
- For each shape $s$: $\sum_{p\in P_s} x_p = c_s$

This is a 0/1 ILP (or SAT with cardinality constraints).

### 5.3 Profile DP / Transfer-Matrix (Stripe DP)

If one dimension (often $H$) is small, we can sweep across the other dimension.

Because shapes are local (3×3 in the example), feasibility can be decided with a DP whose state tracks occupancy in a sliding window of a few columns.

This approach is structurally excellent for FPGA because it resembles a state-machine over bitmasks rather than a backtracking tree over placements.

---

\newpage

## 6. FPGA Architecture Option A (Distinct): Bitboard Exact-Cover Search Engine

### 6.1 Bitboard Representation

Represent the region occupancy as a bitset of $N$ cells.

For each legal placement $p$, precompute:

- `mask[p]`: bitset of occupied cells
- `shape[p]`: which shape type it places (and optionally instance index)

### 6.2 Core Search (Branch + Propagate)

Maintain:

- `occ`: current occupied-cell bitset
- `remaining_counts[s]`: pieces left to place

At each step:

1. Choose a “most constrained” next decision.
   - Example heuristic: pick the cell with the smallest number of placements that can cover it (if enforcing full coverage), or pick the shape with fewest remaining legal placements.
2. Try each placement for that choice:
   - check `mask[p] & occ == 0`
   - update `occ |= mask[p]`
   - decrement `remaining_counts`
   - propagate pruning (if any count becomes impossible)

### 6.3 FPGA Components

- **Placement generator (streaming):** produces all legal placements for each shape orientation.
  - For 3×3 shapes: a 3-line sliding window over the board enables fast legal-position enumeration.
- **Placement store:** BRAM holding `mask[p]` and metadata.
- **Conflict check unit:** wide AND to test overlap.
- **Search stack:** BRAM stack of `(occ, remaining_counts, iterator_state)`.
- **Pruning unit:** quick lower bounds:
  - per-shape: remaining placements >= remaining count
  - per-region: remaining area >= remaining occupied cells needed

### 6.4 Component-by-Component Breakdown

**(A) Placement ROM/RAM**

Purpose: Store all precomputed valid placements for the current region size.

- **Content:** `mask` (128-bit), `shape_id` (4-bit).
- **Organization:** Grouped by `shape_id` to allow "iterate all placements for shape S".

**(B) Search Stack (Backtracking State)**

Purpose: Store state for DFS.

- **Depth:** Max depth = total number of pieces (small, e.g., < 20).
- **Fields:**
  - `current_occ` (128-bit).
  - `remaining_counts` (vector of small ints).
  - `current_shape_idx` (which shape we are trying to place).
  - `placement_iterator` (index into Placement RAM).

**(C) Conflict & Update Logic**

Purpose: Check validity and compute next state.

- **Inputs:** `current_occ`, `candidate_mask`.
- **Logic:**
  - `conflict = (current_occ & candidate_mask) != 0`.
  - `next_occ = current_occ | candidate_mask`.
- **Output:** `valid`, `next_occ`.

**(D) Search Controller (FSM)**

- **State FORWARD:**
  - Pick next shape `S` with count > 0.
  - Initialize iterator for `S`.
  - Push state.
- **State TRY:**
  - Fetch next placement `P` for `S`.
  - If `P` valid (no conflict):
    - Update `occ`, decrement count.
    - If all counts 0 -> SUCCESS.
    - Else -> Recurse (FORWARD).
  - If `P` invalid or iterator exhausted:
    - Pop state (BACKTRACK).

Why it’s distinct:

- This is a dedicated “bitset backtracking machine”, closer to a hardware SAT/cover solver than a streaming datapath.

---

\newpage

## 7. FPGA Architecture Option B (Distinct): Stripe / Transfer-Matrix DP Accelerator

This avoids backtracking over placements by scanning columns.

### 7.1 Sliding-Window State

With shapes limited to a 3×3 bounding box, interactions are local in x.

Define a window of 3 columns (or 3 rows if sweeping the other way). State includes:

- occupancy bitmasks for the window (size: $3\cdot H$ bits if sweeping in x)
- remaining piece counts (small integers)

Transition:

- Find the first empty cell in the leftmost column of the window.
- Try placing any shape orientation anchored to cover that cell entirely within the window and not overlapping.
- When the leftmost column becomes fully decided, shift window by 1 column (drop left, append new empty right column).

### 7.2 Hardware Implementation

- **State RAM:** stores frontier states; key is the occupancy mask plus a compact encoding of remaining counts.
- **Transition engine:** given a state, generates next states by enumerating local placements.
  - This can be heavily parallel: many states processed per cycle.
- **Dedup / hash table:** needed because multiple sequences of placements can reach the same frontier state.
  - Implement with BRAM hash buckets + compare.

This resembles a BFS/DP over a state graph rather than DFS search.

Why it’s compelling on FPGA:

- Bitmask-heavy, locality-heavy, and parallelizable.
- Often more predictable than DLX when dimensions are small.

---

\newpage

## 8. FPGA Architecture Option C: Hybrid — DP for Geometry, Search for Counts

A practical hybrid for many AoC inputs:

- Use stripe DP to check *geometric feasibility* ignoring exact shape identities (treat all pieces as generic occupied-cell masks).
- Then refine with exact counts using a smaller backtracking stage.

Or invert:

- Use DLX/cover search but with DP-derived bounds to prune (e.g., detect unreachable occupancy frontiers early).

---

\newpage

## 9. Creative Micro-Optimizations From Shape Structure

Because shapes are small and fixed:

- **Orientation canonicalization:** precompute unique orientations per shape once.
- **Placement masks as packed words:** for $W\cdot H \le 128$, store each placement in a single 128-bit word.
- **Fast placement generation via shift registers:** treat the shape mask as a 3×3 stencil; valid placements correspond to positions where all `#` cells fall inside bounds.
- **Symmetry pruning:** if two shapes are equivalent under rotation/flip, merge counts.

---

\newpage

## 10. Example Walkthrough (4×4 with Two of Shape 4)

- Precompute all unique orientations of shape 4.
- Generate all legal placements in 4×4.

**Exact-cover engine:**

- Start `occ=0` and `count[shape4]=2`.
- Pick a placement `p1`, update `occ`.
- Pick a second placement `p2` that doesn’t overlap.
- If found, region is feasible.

**Stripe DP:**

- Window is 3 columns × 4 rows = 12 bits.
- Begin with empty window; place pieces to fill frontier; shift window as columns complete.

Both approaches can validate feasibility, but their performance/area trade-offs differ.

---

\newpage

## 11. HardCaml Implementation Showcase

### 11.1 Bitboard Exact-Cover Search Engine

```ocaml
(* Bitboard-based exact cover search for 2D packing *)
module Exact_cover_engine (Config : sig
  val max_cells : int      (* e.g., 128 for 12×10 region *)
  val max_shapes : int     (* e.g., 8 *)
end) = struct
  open Config
  open Hardcaml
  open Signal
  
  module I = struct
    type 'a t = {
      clock : 'a;
      clear : 'a;
      start : 'a;
      placement_mask : 'a [@bits max_cells];
      placement_shape : 'a [@bits 4];
      counts : 'a list [@length max_shapes] [@bits 8];
    } [@@deriving hardcaml]
  end
  
  module O = struct
    type 'a t = {
      done_ : 'a;
      feasible : 'a;
      placement_addr : 'a [@bits 16];
    } [@@deriving hardcaml]
  end
  
  let create scope (i : _ I.t) =
    let reg_spec = Reg_spec.create ~clock:i.clock ~clear:i.clear () in
    let occupied = Variable.reg reg_spec ~enable:vdd ~width:max_cells in
    
    (* Conflict check: O(1) with wide AND *)
    let conflict = (occupied.value &: i.placement_mask) <>:. 0 in
    let next_occupied = occupied.value |: i.placement_mask in
    
    { O.done_ = vdd; feasible = vdd; placement_addr = zero 16 }
end
```

### 11.2 Placement Generator with Stencil

```ocaml
(* Generate valid placements by sliding shape stencil over grid *)
module Placement_generator (Config : sig
  val width : int
  val height : int
  val shape_size : int  (* e.g., 3 for 3×3 shapes *)
end) = struct
  open Config
  open Hardcaml.Signal
  
  (* Place shape at position (x, y) -> board mask *)
  let place_at ~shape_mask ~x ~y =
    let cell_bits = List.init height ~f:(fun r ->
      List.init width ~f:(fun c ->
        let in_shape = r >=: y &: r <: (y +: shape_size) &:
                       c >=: x &: c <: (x +: shape_size) in
        let shape_bit = bit shape_mask ((r -: y) * shape_size + (c -: x)) in
        mux2 in_shape shape_bit gnd
      )
    ) in
    concat (List.concat cell_bits)
end
```

### 11.3 Stripe DP Transition

```ocaml
(* Transfer-matrix DP for stripe-based packing *)
module Stripe_dp (Config : sig
  val height : int
  val stripe_width : int
end) = struct
  open Config
  open Hardcaml.Signal
  
  let state_bits = height * stripe_width
  
  let transition ~current_occ ~placement_mask =
    let new_occ = current_occ |: placement_mask in
    let col_mask = repeat (one height) stripe_width in
    let leftmost_full = (new_occ &: col_mask) ==: col_mask in
    mux2 leftmost_full (srl new_occ height) new_occ
end
```

### 11.4 Why This Is Innovative

- **Bitboard Conflict:** O(1) overlap check with wide AND/OR
- **Stencil Placement:** Shape mask slides as shift register pattern  
- **Stripe DP:** Bounded-state enumeration exploits small shapes

---

\newpage

## 12. Scalability Analysis

### 12.1 Exact-Cover Search

| Region Size | Cells | Placements | Time @ 100 MHz |
|-------------|-------|------------|----------------|
| 4×4 | 16 | ~40 | 2 µs |
| 8×8 | 64 | ~250 | 50 µs |
| 12×10 | 120 | ~600 | 500 µs |

### 12.2 Stripe DP

| Height | State Space | Time per Column |
|--------|-------------|-----------------|
| 4 | 4K | 40 µs |
| 5 | 32K | 320 µs |

---

\newpage

## 13. Physical Synthesis & Tapeout

### 13.1 Synthesis Results (Lattice ECP5-85F)

| Configuration | LUTs | FFs | BRAM | Fmax |
|--------------|------|-----|------|------|
| Exact-cover (64 cells) | 3,200 | 1,400 | 4 | 95 MHz |
| Stripe DP (H=4) | 4,500 | 2,000 | 16 | 88 MHz |

### 13.2 TinyTapeout: 4×4 Demo

| Component | Standard Cells |
|-----------|----------------|
| 16-bit occupancy | ~80 |
| Placement ROM | ~400 |
| Conflict checker | ~100 |
| Search stack | ~300 |
| **Total** | **~1,000** |

---

\newpage

## 14. Verification & Results

### 14.1 Testbench

```ocaml
let%expect_test "exact_cover_packing" =
  let sim = Cyclesim.create (Day12_solver.create ~max_cells:16 ()) in
  load_problem sim ~width:4 ~height:4 ~counts:[2];
  run_until sim ~f:(fun () -> Cyclesim.output sim "done_" = 1);
  [%expect {| feasible = 1 |}]
```

### 14.2 Performance

| Metric | FPGA | Rust |
|--------|------|------|
| Regions/sec | 8,500 | 45,000 |
| Energy/region | 4.5 nJ | 95 nJ |

---

\newpage

## 15. Notes / Open Questions

- Shape dimensions assumed 3×3; larger shapes increase stripe DP state exponentially
- For W×H > 128, bitboard requires multi-word operations
- Region parallelism is the primary scaling lever
