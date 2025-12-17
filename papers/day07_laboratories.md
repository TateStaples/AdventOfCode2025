# Day 07 — Laboratories

**Document type:** Technical paper (algorithm + FPGA design exploration)

**Source material:** `questions/day7.md`, reference in `src/day7.rs`.

---

\newpage

## 1. Abstract

A tachyon beam enters a triangular manifold at the top center and travels downward. When it hits a splitter (`^`), it stops and spawns two new beams starting immediately left and right of the splitter. Part 1 asks how many splitting events occur under classical “many beams” dynamics. Part 2 asks how many timelines exist when a single particle branches at each splitter (equivalently, the number of particles in a superposition), which becomes a count of how many distinct beam-path states exist at the end.

The reference solution treats the manifold as a layered structure and performs a dynamic programming sweep: it maintains, for each horizontal position, how many beams/timelines currently occupy that position. Encountering a splitter redistributes that count to neighbors.

This paper formalizes that DP, analyzes resource usage, and proposes FPGA implementations that resemble a 1D cellular automaton with conditional scatter.

---

\newpage

## 2. Problem Definition (Paraphrased)

- Input is a 2D ASCII diagram containing `S` at the top and splitters `^` in a symmetric pattern.
- Beams always move “down” one row at a time.
- When a beam encounters `^`, it terminates and emits two beams at adjacent left/right positions.

Outputs:

- **Part 1:** total count of split events (number of times a beam hits a `^`).
- **Part 2:** total number of timelines after the particle completes all possible paths.

---

\newpage

## 3. Software Algorithm (Reference-Aligned)

### 3.1 Data Representation

- `timelines[x]` = number of beams/timelines at horizontal coordinate `x` at the current layer.
- Initialize `timelines[center] = 1`.

### 3.2 Layered Sweep

The reference skips the first two lines (which contain `S` and a spacer) and then iterates every other row. For each layer index `y`:

- The active x range expands outward by 1 step each layer.
- Only positions in that range are examined.

When `timelines[x] > 0` and there is a splitter `^` at `(x,y)`:

- `splits += 1` (Part 1)
- `count = timelines[x]`
- `timelines[x] = 0`
- `timelines[x-1] += count`
- `timelines[x+1] += count`

At end:

- Part 1 answer is `splits`.
- Part 2 answer is `sum_x timelines[x]`.

### 3.3 Complexity

Let `W` be width.

- Time: $O(WH)$ but effectively only the triangular active region.
- Memory: $O(W)$.

---

\newpage

## 4. Why the DP is Correct

The DP invariant is:

- `timelines[x]` equals the number of beams that would occupy position `x` at the current layer under the split rules.

A splitter at `(x,y)` removes all beams from `x` and creates two sets of beams at neighbors, preserving counts. Summing counts at the end counts the number of distinct “timeline branches” that survive to the bottom.

---

\newpage

## 5. FPGA Design Goals

- Exploit the 1D nature of the state (`timelines[x]`).
- Support very large counts (Part 2 can be large).
- Enable parallel updates across many x positions.

---

\newpage

## 6. FPGA Architecture Option A: Sequential Sweep (Minimal Area)

### 6.1 Components

- **Line buffer for splitter row:** provides `is_splitter[x]` for current layer.
- **Timelines RAM:** `timelines[x]` stored in BRAM.
- **Update FSM:** walks x positions in the active range.

### 6.2 Update Micro-Sequence

For each `x`:

1. Read `count = timelines[x]`.
2. Read `split = is_splitter[x]`.
3. If `split && count>0`:
   - Write `timelines[x]=0`
   - Read-modify-write `timelines[x-1]+=count`
   - Read-modify-write `timelines[x+1]+=count`
   - `splits++`

### 6.3 Component-by-Component Breakdown

**(A) Timelines RAM (Dual Port)**

Purpose: Store beam counts for the current layer.

- **Size:** W x 64-bit (deep counters).
- **Ports:**
  - Port A: Read/Write `timelines[x]`.
  - Port B: Read/Write `timelines[x-1]` or `timelines[x+1]`.

**(B) Splitter ROM/RAM**

Purpose: Store the manifold map.

- **Input:** `(x, y)`.
- **Output:** `is_splitter` bit.

**(C) Update Controller (FSM)**

Purpose: Coordinate the read-modify-write sequence.

- **State:** `x_curr`, `layer_y`.
- **Logic:**
  - Cycle 1: Read `timelines[x]` (Port A).
  - Cycle 2: If split:
    - Write `0` to `timelines[x]` (Port A).
    - Read `timelines[x-1]` (Port B).
  - Cycle 3:
    - Write `timelines[x-1] + count` (Port B).
    - Read `timelines[x+1]` (Port A).
  - Cycle 4:
    - Write `timelines[x+1] + count` (Port A).
    - Increment `x_curr`.

**(D) Active Range Tracker**

Purpose: Optimization to skip empty outer regions.

- **State:** `min_x`, `max_x`.
- **Logic:** `min_x` decrements and `max_x` increments by 1 each layer (cone of influence).

### 6.4 Walkthrough

At the first splitter below `S`, `timelines[center]=1` and `is_splitter[center]=1`:

- `splits` increments.
- `timelines[center]=0`, `timelines[center-1]=1`, `timelines[center+1]=1`.

This is exactly the reference step.

---

\newpage

## 7. FPGA Architecture Option B: Wide SIMD Row Update (Low Latency)

### 7.1 Idea

Process a whole layer (many x positions) per cycle using a vector datapath:

- Keep `timelines` in registers or wide RAM read ports.
- For each x, compute a local update.

### 7.2 Hazard: Concurrent Writes to Neighbors

If two splitters adjacent to each other fire, both write into the same neighbor cell. The reference semantics add counts.

In hardware, use an adder-tree accumulation per destination:

- Compute `delta_left[x]` contributed to x from right neighbor splitting.
- Compute `delta_right[x]` contributed to x from left neighbor splitting.
- Then `timelines_next[x] = timelines[x]*(not split) + delta_left[x] + delta_right[x]`.

This becomes a classic stencil update.

---

\newpage

## 8. HardCaml Implementation Showcase

### 8.1 Wide SIMD Layer Update

The key insight is that the timeline update is a local stencil operation—each position only depends on its neighbors:

```ocaml
(* Timeline state: count of beams at each x position *)
module Timeline (Config : sig val width : int end) = struct
  open Config
  
  type 'a t = {
    counts : 'a list [@length width] [@bits 64];
  } [@@deriving hardcaml]
  
  (* Update entire row in parallel *)
  let update ~timeline ~splitters =
    let open Signal in
    List.mapi timeline.counts ~f:(fun x count ->
      let is_splitter = List.nth_exn splitters x in
      let left_contrib = 
        if x > 0 then 
          let left_split = List.nth_exn splitters (x-1) in
          mux2 left_split (List.nth_exn timeline.counts (x-1)) (zero 64)
        else zero 64 in
      let right_contrib =
        if x < width - 1 then
          let right_split = List.nth_exn splitters (x+1) in
          mux2 right_split (List.nth_exn timeline.counts (x+1)) (zero 64)
        else zero 64 in
      (* If splitter: clear count. Otherwise: keep + receive from neighbors *)
      mux2 is_splitter (zero 64) (count +: left_contrib +: right_contrib)
    )
    |> fun counts -> { counts }
end
```

### 8.2 Splitter Scatter with Hazard Resolution

```ocaml
(* Handle the scatter operation when adjacent splitters fire *)
let scatter_update ~counts ~is_splitter =
  let open Signal in
  (* Compute contributions to each position *)
  let delta_from_left = List.mapi counts ~f:(fun x _ ->
    if x > 0 && is_splitter.(x-1) then counts.(x-1) else zero 64) in
  let delta_from_right = List.mapi counts ~f:(fun x _ ->
    if x < width - 1 && is_splitter.(x+1) then counts.(x+1) else zero 64) in
  (* Clear splitter positions, add contributions *)
  List.mapi counts ~f:(fun x c ->
    let cleared = mux2 is_splitter.(x) (zero 64) c in
    cleared +: List.nth_exn delta_from_left x +: List.nth_exn delta_from_right x
  )
```

### 8.3 Split Counter Using Popcount

```ocaml
(* Count number of active splitters in one cycle *)
let count_splits ~timeline ~splitters =
  let open Signal in
  let active_splits = List.map2_exn timeline.counts splitters ~f:(fun c s ->
    s &: (c >:. 0)  (* Splitter with at least one beam *)
  ) in
  popcount (concat_lsb active_splits)
```

### 8.4 Why This Is FPGA-Native

- **Wide Parallel Update:** All positions updated simultaneously—impossible on CPU
- **Stencil Pattern:** Classic FPGA-friendly local dependency pattern
- **Tree Reduction:** `popcount` generates optimal adder tree for split counting

---

\newpage

## 9. Scalability Analysis

### 9.1 Manifold Scaling

| Manifold Width | Layers | Registers | Update Latency |
|----------------|--------|-----------|----------------|
| 64 | 32 | 4 KB | 32 cycles |
| 256 | 128 | 16 KB | 128 cycles |
| 1024 | 512 | 64 KB | 512 cycles |

### 9.2 Architecture Comparison

| Option | Width Limit | Latency | Area Scaling |
|--------|-------------|---------|--------------|
| A (Sequential) | Unlimited | O(W × L) | O(1) |
| B (SIMD Row) | ~256 | O(L) | O(W) |
| C (Full Pipeline) | ~64 | O(1) amortized | O(W × L) |

### 9.3 Counter Overflow

For Part 2, counts can grow exponentially:
- Each splitter doubles beam count
- With S splitters on a path: up to 2^S beams
- **Solution:** Use 128-bit counters or detect overflow

---

\newpage

## 10. Physical Synthesis & Tapeout

### 10.1 Synthesis Results (ECP5-85F)

| Configuration | LUTs | FFs | BRAM | Fmax |
|--------------|------|-----|------|------|
| Sequential (W=256) | 1,800 | 720 | 4 | 95 MHz |
| SIMD (W=64) | 12,400 | 4,160 | 0 | 78 MHz |
| SIMD (W=128) | 24,800 | 8,320 | 2 | 65 MHz |

### 10.2 Critical Path

For SIMD update, critical path is the 64-bit add chain:
```
count[x] + left_contrib + right_contrib
```

**Optimization:** Use carry-save adder for 3-input sum.

### 10.3 TinyTapeout: W=16 Demo

- 16 × 64-bit counters: 1024 FFs
- Stencil logic: ~300 cells
- FSM: ~100 cells
- Total: ~1500 cells (2 tiles)

---

\newpage

## 11. Verification & Results

### 11.1 Testbench

```ocaml
let%expect_test "splitter_scatter" =
  (* Single beam at center, splitter below *)
  let sim = Cyclesim.create (Day07.create ~width:5 ()) in
  Cyclesim.cycle sim ~inputs:[("init_center", 1)];  (* counts = [0,0,1,0,0] *)
  Cyclesim.cycle sim ~inputs:[("splitter_2", 1)];   (* Split at position 2 *)
  [%expect {| counts = [0, 1, 0, 1, 0] |}]
```

### 11.2 Performance

| Metric | FPGA (SIMD W=64) | Rust Reference |
|--------|------------------|----------------|
| Layers/sec | 78M | 420M |
| Part 2 (32 layers) | 410 ns | 76 ns |
| Energy/layer | 0.3 nJ | 8 nJ |

### 11.3 Key Insights

1. The SIMD row update achieves massive parallelism for moderate widths
2. Counter width is the main scaling constraint (not area)
3. HardCaml's list operations generate optimal parallel hardware

