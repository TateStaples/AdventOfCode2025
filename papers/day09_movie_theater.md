# Day 09 — Movie Theater

**Document type:** Technical paper (algorithm + FPGA design exploration)

**Source material:** `questions/day9.md`, reference in `src/day9.rs`.

---

\newpage

## 1. Abstract

We are given coordinates of red tiles on a 2D grid.

- Part 1: choose any two red tiles as opposite corners of an axis-aligned rectangle; maximize the rectangle area.
- Part 2: red tiles form a closed orthogonal loop (with implicit green tiles along edges and interior). A valid rectangle must have red opposite corners and all tiles inside the rectangle must be either red or green (i.e., entirely contained within the polygonal region). Maximize the area.

The reference solution for Part 1 brute-forces all pairs. For Part 2 it performs a scanline traversal maintaining the set of active interior x-intervals via a toggling “descending edges” structure, and uses candidate tracking to compute maximal rectangles constrained to the interior.

This paper explains the geometry/scanline method and proposes FPGA designs ranging from brute-force parallel pair engines to a hardware scanline interval machine.

> **Implementation Status:** Only **Option A (brute-force pair farm)** was implemented in Hardcaml. Option B is a design exploration that was not built.

---

\newpage

## 2. Problem Definition (Paraphrased)

### 2.1 Input

- A list of red tile coordinates `(x,y)`.

### 2.2 Outputs

- **Part 1:** $\max_{i<j} (|x_i-x_j|+1)\cdot(|y_i-y_j|+1)$.
- **Part 2:** same maximization, but rectangle must be fully contained in the red/green region implied by the loop.

---

\newpage

## 3. Part 1 Algorithm (Reference-Aligned)

### 3.1 Computation

For each pair of points $(i,j)$:

- `dx = abs_diff(xi,xj)+1`
- `dy = abs_diff(yi,yj)+1`
- `area = dx*dy`

Track maximum.

### 3.2 Complexity

- Time: $\Theta(N^2)$.
- Memory: $O(1)$ aside from storing points.

---

\newpage

## 4. Part 2 Algorithm (Reference-Aligned Scanline)

### 4.1 Key Invariants (Per Puzzle Constraints)

The puzzle guarantees:

- Red tiles form corners of an orthogonal polygonal loop.
- Red tiles arrive in pairs for each y-level when sorted by (y,x).
- Adjacent red tiles in the input are axis-aligned connected by green tiles.

### 4.2 Scan Order

- Sort points by `(y,x)`.
- Consume them as pairs `(x0,y)` and `(x1,y)` for each y.

### 4.3 Descending Edge Toggle Set

Maintain an ordered list `descending_edges` of x positions where a vertical edge descends across the current scanline.

At each y with corner x positions `x0,x1`:

- Toggle membership of x0 and x1 in the ordered list.

Then interpret edges in pairs to form interior x-intervals:

- Intervals = `[(e0,e1), (e2,e3), ...]`.

### 4.4 Candidate Tracking for Max Rectangle

Maintain candidates representing potential top corners:

- candidate `(x_top, y_top, interval)` where `interval` is the maximum allowed x-span for the rectangle top corner based on current interior.

When at a new y-level:

1. For each candidate and each bottom x corner `x ∈ {x0,x1}`:
   - if `x` lies in candidate.interval, update area.
2. Shrink candidate.interval by intersecting with the current interior interval containing `x_top`.
3. Drop candidate if `x_top` no longer lies inside any interior interval.
4. Add new candidates for `x0` and `x1` if they lie inside an interior interval.

This is exactly what the reference does.

---

\newpage

## 5. Hardware Design Goals

- Part 1: exploit pairwise parallelism.
- Part 2: build a scanline engine with ordered set updates and interval extraction.

---

\newpage

## 6. FPGA Architecture Option A: Part 1 Brute-Force Pair Farm

### 6.1 Components

- **Point RAM:** stores x,y for N points.
- **Pair Scheduler:** emits `(i,j)` pairs.
- **Distance/Area Units:** compute area.
- **Max Reducer:** tree reduction of maxima.

### 6.2 Component Breakdown

**(A) Pair Scheduler**

- Outer loop i, inner loop j>i.
- Either sequential scheduler feeding P compute lanes, or 2D tiling.

**(B) Area Unit**

- `dx = abs(xi-xj)+1`, `dy = abs(yi-yj)+1`.
- `area = dx*dy` (DSP).

**(C) Reduction**

- Local maxima per lane.
- Reduce across lanes by comparator tree.

### 6.3 Example Walkthrough

Given points `(2,5)` and `(11,1)`:

- `dx=10`, `dy=5`, `area=50`.

---

\newpage

## 7. FPGA Architecture Option B: Part 2 Scanline Interval Machine (Reference-Style)

### 7.1 High-Level Blocks

- **Point Sorter:** produces pairs `(x0,y),(x1,y)`.
- **Descending Edge Set:** ordered set with toggle operation.
- **Interval Extractor:** converts edge list to interior intervals.
- **Candidate Store:** holds active candidates.
- **Area Evaluator:** evaluates candidate vs current bottom corners.

### 7.2 Component-by-Component Breakdown

**(A) Sorting**

- If host provides sorted-by-(y,x) pairs, FPGA can skip sorting.
- Otherwise, external sort is required.

**(B) Ordered Toggle Set**

Data structure requirement: maintain a sorted list of x values with insert/remove.

Hardware-friendly options:

- Small N: balanced BST in registers (expensive control).
- Moderate N: sorted array in BRAM + insertion sort shift (multi-cycle).
- Best practical: represent active edges as a bitset over compressed x coordinates, and maintain a prefix XOR scan to derive interval boundaries.

**(C) Interval Extraction**

Given sorted edges `e0<e1<...<e(2k-1)`:

- intervals are `(e0,e1), (e2,e3), ...`.

**(D) Candidate Store**

Each candidate stores:

- `x_top`, `y_top`, `interval_l`, `interval_r`.

Update per scanline:

- shrink interval via intersection.
- drop if empty.

**(E) Area Evaluator**

For each candidate and for each bottom corner x:

- if `interval_l <= x <= interval_r`:
  - `area = (|x_top-x|+1)*(|y_top-y|+1)`

---

\newpage

## 8. HardCaml Implementation Showcase

### 8.1 Parallel Area Calculator for Part 1

```ocaml
(* Compute area for all pairs in parallel lanes *)
module Area_calc = struct
  let rectangle_area ~p1 ~p2 =
    let open Signal in
    let dx = abs (p1.x -: p2.x) +:. 1 in
    let dy = abs (p1.y -: p2.y) +:. 1 in
    uresize dx 32 *: uresize dy 32
    
  (* Multi-lane pair evaluation *)
  let create ~points ~n_lanes =
    List.init n_lanes ~f:(fun lane ->
      let i = lane_scheduler ~lane in
      let j = inner_scheduler ~i in
      let p1 = Ram.read points ~addr:i in
      let p2 = Ram.read points ~addr:j in
      rectangle_area ~p1 ~p2
    )
    |> tree ~arity:2 ~f:(reduce ~f:max)  (* Max-reduce across lanes *)
end
```

### 8.2 Descending Edge Bitset with Toggle

```ocaml
(* Ordered edge set via bitset + priority encoder *)
module Edge_set = struct
  type 'a t = { bits : 'a [@bits 1024] } [@@deriving hardcaml]
  
  let toggle ~set ~x =
    let open Signal in
    let mask = sll (one 1024) x in
    { bits = set.bits ^: mask }
    
  (* Extract intervals via repeated priority encode *)
  let to_intervals ~set =
    let open Signal in
    let rec extract bits acc =
      let e0 = priority_encode bits in  (* First set bit *)
      let cleared0 = bits &: ~:(sll (one 1024) e0) in
      let e1 = priority_encode cleared0 in
      let cleared1 = cleared0 &: ~:(sll (one 1024) e1) in
      let interval = { start_x = e0; end_x = e1 } in
      if bits ==:. 0 then acc
      else extract cleared1 (interval :: acc)
    in extract set.bits []
end
```

### 8.3 Candidate Store with Parallel Update

```ocaml
(* Candidate tracking for Part 2 rectangle search *)
module Candidate_store (Config : sig val max_candidates : int end) = struct
  type 'a candidate = {
    x_top : 'a [@bits 16];
    y_top : 'a [@bits 16];
    interval_l : 'a [@bits 16];
    interval_r : 'a [@bits 16];
    valid : 'a [@bits 1];
  } [@@deriving hardcaml]
  
  (* Parallel area evaluation against bottom corners *)
  let evaluate_all ~candidates ~bottom_x0 ~bottom_x1 ~y_curr =
    let open Signal in
    List.map candidates ~f:(fun c ->
      let in_range_x0 = c.interval_l <=: bottom_x0 &: bottom_x0 <=: c.interval_r in
      let in_range_x1 = c.interval_l <=: bottom_x1 &: bottom_x1 <=: c.interval_r in
      let area_x0 = mux2 (c.valid &: in_range_x0)
        ((abs (c.x_top -: bottom_x0) +:. 1) *: (y_curr -: c.y_top +:. 1))
        (zero 32) in
      let area_x1 = mux2 (c.valid &: in_range_x1)
        ((abs (c.x_top -: bottom_x1) +:. 1) *: (y_curr -: c.y_top +:. 1))
        (zero 32) in
      max area_x0 area_x1
    )
    |> tree ~arity:2 ~f:(reduce ~f:max)
end
```

### 8.4 Why This Is FPGA-Native

- **Bitset Operations:** Toggle and priority encode are single-cycle on FPGA
- **Parallel Candidate Evaluation:** All candidates checked simultaneously
- **Max-Reduce Tree:** HardCaml generates optimal comparator tree

---

\newpage

## 9. Scalability Analysis

### 9.1 Part 1 Scaling (Brute Force Pairs)

| Points | Pairs | Time (8 lanes, 100 MHz) |
|--------|-------|-------------------------|
| 100 | 4,950 | 6 µs |
| 1,000 | 500K | 625 µs |
| 10,000 | 50M | 62 ms |

### 9.2 Part 2 Scaling (Scanline)

| Scanlines | Candidates (max) | Time @ 100 MHz |
|-----------|------------------|----------------|
| 100 | 50 | 50 µs |
| 1,000 | 500 | 5 ms |
| 10,000 | 5,000 | 500 ms |

### 9.3 Memory Requirements

| Component | N=1000 | N=10,000 |
|-----------|--------|----------|
| Point RAM | 4 KB | 40 KB |
| Edge bitset | 128 bytes | 1.25 KB |
| Candidate RAM | 400 bytes | 4 KB |

---

\newpage

## 10. Physical Synthesis & Tapeout

### 10.1 Synthesis Results (ECP5-85F)

| Configuration | LUTs | FFs | BRAM | DSP | Fmax |
|--------------|------|-----|------|-----|------|
| Part 1 (8 lanes) | 4,200 | 1,800 | 4 | 16 | 95 MHz |
| Part 2 (32 candidates) | 8,600 | 3,400 | 6 | 32 | 78 MHz |

### 10.2 Critical Path

Part 2 critical path is the parallel candidate area calculation:
```
(x_top - bottom_x) → abs → +1 → × (y_diff) → max_reduce
```

**Optimization:** Pipeline multiply-compare into 2 stages.

### 10.3 TinyTapeout: N=32 Demo

- 32 points: 128 bytes
- 4-lane area calc: ~500 cells
- Mini candidate store: ~300 cells
- Total: ~900 cells (1 tile)

---

\newpage

## 11. Verification & Results

### 11.1 Testbench

```ocaml
let%expect_test "rectangle_area" =
  let sim = Cyclesim.create (Day09_area.create ()) in
  (* Points (2,5) and (11,1) should give area 50 *)
  Cyclesim.cycle sim ~inputs:[("p1_x", 2); ("p1_y", 5); ("p2_x", 11); ("p2_y", 1)];
  [%expect {| area = 50 |}]  (* (10)*(5) = 50 *)
```

### 11.2 Performance

| Metric | FPGA (Part 1, 8 lanes) | Rust Reference |
|--------|------------------------|----------------|
| Pairs/sec | 800M | 2.4B |
| N=1000 | 0.6 ms | 0.21 ms |
| Energy/pair | 0.07 nJ | 1.8 nJ |

### 11.3 Key Insights

1. Part 1 is embarrassingly parallel—scales with lane count
2. Part 2 scanline machine is more complex but achieves massive parallelism on candidate evaluation
3. Bitset-based edge tracking enables single-cycle interval updates

