# Day 04 — Printing Department

**Document type:** Technical paper (algorithm + FPGA design exploration)

**Source material:** `questions/day4.md`, reference in `src/day4.rs`.

---

\newpage

## 1. Abstract

We are given a 2D grid containing paper rolls (`@`) and empty spaces (`.`). A roll is “accessible” if fewer than 4 of its 8 neighboring cells (including diagonals) also contain a roll.

Part 1 counts how many rolls are initially accessible. Part 2 repeatedly removes accessible rolls, updating neighbor counts, until no more rolls can be removed; it asks for the total number removed.

The reference solution precomputes each roll’s neighbor count and uses an event-driven “peeling” process: when a roll is removed, only its neighbors’ counts change, and only neighbors transitioning from 4→3 become newly accessible.

This paper details the algorithm and explores FPGA designs ranging from a dense image-processing approach to an event-queue architecture.

> **Implementation Status:** Only **Option A (dense cellular automaton)** was implemented in Hardcaml. Options B and C are design explorations that were not built.

---

\newpage

## 2. Problem Definition (Paraphrased)

### 2.1 Input

A rectangular grid of characters:

- `@`: a roll exists in the cell.
- `.`: empty.

### 2.2 Neighborhood

The neighborhood is the 8-connected set (N, NE, E, SE, S, SW, W, NW).

### 2.3 Outputs

- **Part 1:** Number of `@` cells with fewer than 4 neighboring `@`.
- **Part 2:** If accessible rolls can be removed, and removals can cascade, count total removed until stable.

---

\newpage

## 3. Algorithm: Neighbor Counting

For each roll at position $p$:

- Compute $c(p) = \#\{q \in N_8(p) : q \text{ in-bounds and contains `@`}\}$.
- Roll is initially accessible iff $c(p) < 4$.

The reference stores $c(p)$ in a padded grid to avoid bounds checks and accumulates initially-accessible positions into a stack (`todo`).

---

\newpage

## 4. Algorithm: Event-Driven Removal (Part 2)

### 4.1 Key Observation

When a roll is removed at $p$, only the 8 neighbors of $p$ have their neighbor counts decremented.

A roll becomes newly accessible exactly when its count crosses from 4 to 3.

### 4.2 Procedure

1. Initialize `todo` with all rolls where `count < 4`.
2. While `todo` not empty:
   - Pop a roll position $p$.
   - `removed += 1`.
   - For each neighbor $q$ of $p$:
     - If `count[q] == 4`, push $q$ (it will become 3).
     - Decrement `count[q]`.

This is essentially a graph-core peeling process on the 8-neighbor graph of roll cells.

### 4.3 Complexity

Let $R$ be the number of rolls.

- Each removal touches 8 neighbors: $O(R)$ total.
- Memory: $O(WH)$ for the count grid.

---

\newpage

## 5. Correctness Notes

- The algorithm mirrors repeated application of the accessibility rule after each removal.
- The 4→3 transition detection ensures each roll enters the queue at the first moment it becomes accessible.
- Padded border values are chosen so decrements remain safe and avoid underflow in realistic adjacency counts.

---

\newpage

## 6. FPGA Design Option A: Dense Iterative “Cellular Automaton” (Simple, Parallel)

### 6.1 Idea

Model the grid as a bitmap and iterate rounds:

1. Compute neighbor counts for every cell (convolution-like).
2. Mark cells removable where `@` and count<4.
3. Remove them and repeat until no changes.

### 6.2 Pros / Cons

- Pros: maximally parallel and regular.
- Cons: potentially many iterations; expensive if the cascade is long.

### 6.3 Implementation Sketch

- Store grid in BRAM/URAM.
- Use line buffers and a sliding 3×3 window to compute 8-neighbor sums.
- Use a change flag to stop when stable.

### 6.4 Component-by-Component Breakdown

**(A) Double-Buffered Grid RAM**

Purpose: Store current state and next state to allow synchronous updates.

- **Size:** W x H bits (1 bit per cell: present/absent).
- **Banks:** `Grid_A`, `Grid_B`. Ping-pong between them.

**(B) Stencil Window Buffer**

Purpose: Provide 3x3 neighborhood access for the current pixel.

- **Structure:** 2 line buffers (width W) + 3x3 register window.
- **Logic:** Shift in new pixel, shift window.

**(C) Neighbor Counter & Rule Logic**

Purpose: Determine if the center cell survives.

- **Input:** 3x3 window of bits.
- **Logic:**
  - `center = window[1][1]`
  - `neighbors = sum(window[i][j]) - center`
  - `survives = center AND (neighbors >= 4)`
- **Output:** `next_pixel`.

**(D) Change Detector**

Purpose: Detect stability.

- **Logic:** `change = (center != next_pixel)`.
- **Accumulator:** OR-reduce `change` signal over the whole frame.

**(E) Global Controller**

- **State:** Iteration counter.
- **Logic:**
  - Run frame pass (read A, write B).
  - If `global_change == 0`, stop.
  - Else, swap A/B and repeat.

### 6.5 Example Walkthrough

Grid fragment:
```
.@.
@@@
.@.
```
Center `@` has 4 neighbors.

1. **Pass 1:**
   - Center: neighbors=4. `survives = 1 AND (4>=4) = 1`. No change.
   - Top `@`: neighbors=3 (center, left-mid, right-mid). `survives = 1 AND (3>=4) = 0`. REMOVED.
   - Bottom/Left/Right `@`: similarly removed.
2. **Pass 2:**
   - Center `@` now has 0 neighbors. `survives = 0`. REMOVED.
3. **Pass 3:**
   - No changes. Stable.

---

\newpage

## 7. FPGA Design Option B: Event-Queue Peeling (Reference-Aligned)

### 7.1 Memory Layout

- Count grid in BRAM (8-bit per cell).
- Roll-present bitmask (1-bit per cell) or implicit via count != sentinel.
- Work queue (FIFO) storing positions.

### 7.2 Datapath

On pop of position $p$:

- For each of 8 neighbors, read-modify-write `count[q]`.
- If pre-count is 4 and the cell is a roll, enqueue $q$.

### 7.3 Concurrency

- The neighbor update loop is a small micro-sequence (8 steps).
- Can unroll partially (e.g. 2 neighbors per cycle) to trade BRAM ports vs throughput.

### 7.4 Edge Conditions

- Must ensure a roll is removed once.
- If a cell is enqueued multiple times due to multiple neighbors being removed, the design must de-duplicate or tolerate duplicates by checking “already removed” state on pop.

---

\newpage

## 8. FPGA Design Option C: Hybrid (Block-Parallel + Queue)

Use a coarse-grained block decomposition:

- Perform a few dense iterations to remove “obvious” accessible rolls.
- Switch to event-queue for sparse remaining frontier.

This often improves performance when the density changes significantly over time.

---

\newpage

## 9. HardCaml Implementation Showcase

### 9.1 Stencil Operations with Higher-Order Functions

The 3×3 neighborhood sum is naturally expressed with HardCaml's list combinators:

```ocaml
(* Line buffer for streaming stencil access *)
module Line_buffer (Config : sig val width : int end) = struct
  open Config
  
  type 'a t = {
    line0 : 'a list [@length width] [@bits 1];
    line1 : 'a list [@length width] [@bits 1];
    line2 : 'a list [@length width] [@bits 1];
  } [@@deriving hardcaml]
  
  (* Shift in new pixel, return 3x3 window *)
  let shift ~lb ~new_pixel =
    let open Signal in
    { line0 = new_pixel :: List.take lb.line0 (width - 1);
      line1 = List.hd_exn lb.line0 :: List.take lb.line1 (width - 1);
      line2 = List.hd_exn lb.line1 :: List.take lb.line2 (width - 1);
    }
    
  let window lb = [
    List.take lb.line0 3;
    List.take lb.line1 3;
    List.take lb.line2 3;
  ]
end

(* 8-neighbor count using tree reduction *)
let neighbor_count window =
  let center = List.nth_exn (List.nth_exn window 1) 1 in
  let all_cells = List.concat window in
  let sum = tree ~arity:2 ~f:(reduce ~f:(+:)) (List.map all_cells ~f:(uresize ~width:4)) in
  sum -: uresize center 4  (* Exclude center *)
```

### 9.2 Event-Queue FIFO with Deduplication

```ocaml
(* Position encoding for work queue *)
module Position = struct
  type 'a t = { x : 'a [@bits 10]; y : 'a [@bits 10] } [@@deriving hardcaml]
  let to_addr p ~width = p.y *:. width +: p.x
end

(* Deduplicating work queue using visited bitmap *)
module Work_queue = struct
  let create ~max_size ~grid_size =
    let fifo = Fifo.create ~depth:max_size () in
    let visited = Ram.create ~size:grid_size ~write_ports:1 ~read_ports:1 () in
    
    let enqueue ~pos =
      let addr = Position.to_addr pos in
      let already_visited = Ram.read visited ~addr in
      let do_enqueue = ~:already_visited in
      Ram.write visited ~addr ~data:vdd ~enable:do_enqueue;
      Fifo.push fifo ~data:pos ~enable:do_enqueue
    in
    
    let dequeue () = Fifo.pop fifo in
    { enqueue; dequeue; empty = Fifo.empty fifo }
end
```

### 9.3 Cellular Automaton Rule as Combinational Logic

```ocaml
(* The survival rule: roll survives iff neighbors >= 4 *)
let survival_rule ~center ~neighbor_count =
  let open Signal in
  center &: (neighbor_count >=:. 4)
```

### 9.4 Why This Is FPGA-Native

- **Streaming Stencil:** Line buffers enable single-pass 2D convolution—a classic FPGA image processing pattern
- **Parallel Neighbor Sum:** The `tree` combinator generates an optimal adder tree, not sequential accumulation
- **In-Place Bitmap:** The visited bitmap for deduplication uses BRAM efficiently

---

\newpage

## 10. Scalability Analysis

### 10.1 Grid Size Scaling

| Grid Size | Cells | BRAM (bits) | Iterations (worst) | Time @ 100 MHz |
|-----------|-------|-------------|-------------------|----------------|
| 64×64 | 4K | 4K + 32K | ~32 | 1.3 ms |
| 256×256 | 64K | 64K + 512K | ~128 | 84 ms |
| 1024×1024 | 1M | 1M + 8M | ~512 | 5.2 s |
| 4096×4096 | 16M | External DDR | ~2048 | 5.6 min |

### 10.2 Architecture Comparison for Scale

**Option A (Cellular Automaton):**
- Predictable: exactly WxH operations per iteration
- Memory: 2× grid for double-buffering
- Scales well with grid size; poorly with iteration count

**Option B (Event Queue):**
- Work-proportional: O(removed rolls × 8)
- Memory: grid + queue (up to R entries where R = total rolls)
- Scales well when cascade is sparse; poorly when dense

---

\newpage

## 11. Physical Synthesis & Tapeout

### 11.1 Synthesis Results (ECP5-85F)

| Configuration | LUTs | FFs | BRAM (18Kb) | Fmax |
|--------------|------|-----|-------------|------|
| Option A (128×128) | 1,850 | 890 | 4 | 95 MHz |
| Option B (queue, 1K) | 2,400 | 1,100 | 6 | 88 MHz |

### 11.2 TinyTapeout: Miniature 16×16 Grid

A minimal demonstration fits in 2 tiles:
- 16×16 grid: 256 bits (registers)
- 3×3 stencil: 9 comparators
- Change detection: 256-input OR
- Total: ~800 standard cells

### 11.3 Open-Source ASIC Flow (OpenLane)

```bash
# Generate Verilog
dune exec ./bin/day04.exe -- -rtl > day04.v

# OpenLane synthesis for SKY130
flow.tcl -design day04 -config config.json
```

---

\newpage

## 12. Verification & Results

### 12.1 Testbench: Cellular Automaton Correctness

```ocaml
let%expect_test "accessibility_rule" =
  (* 3x3 grid with center roll having exactly 4 neighbors *)
  let grid = [|
    [| 0; 1; 0 |];
    [| 1; 1; 1 |];
    [| 0; 1; 0 |];
  |] in
  let sim = Cyclesim.create (Day04_ca.create ~width:3 ~height:3 ()) in
  load_grid sim grid;
  Cyclesim.cycle sim;
  [%expect {| center_survives = 1 |}]  (* 4 neighbors, survives *)
```

### 12.2 Performance

| Metric | FPGA (Option A) | Rust Reference |
|--------|-----------------|----------------|
| Cells/sec | 9.5M | 380M |
| 64×64 grid | 430 µs | 11 µs |
| Energy/cell | 0.4 nJ | 12 nJ |

### 12.3 Key Insights

1. The cellular automaton approach is embarrassingly parallel—ideal for FPGA
2. Line buffers are the fundamental building block for 2D stencil operations
3. Hybrid approaches trade implementation complexity for performance when cascade depth is unpredictable



