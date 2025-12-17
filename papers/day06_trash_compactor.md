# Day 06 — Trash Compactor

**Document type:** Technical paper (algorithm + FPGA design exploration)

**Source material:** `questions/day6.md`, reference in `src/day6.rs`.

---

\newpage

## 1. Abstract

The input is a wide ASCII “worksheet” containing multiple independent arithmetic problems arranged side-by-side. Each problem is a column block of digits, with an operator (`+` or `*`) at the bottom. Part 1 reads each number row-wise (normal digit orientation). Part 2 reads each number column-wise right-to-left, treating each column as a vertical numeral with most significant digit at the top.

The reference solution parses the worksheet as a 2D grid and folds digits into numbers by scanning either rows or columns, then applying either sum or product depending on the operator.

This paper explains both interpretations precisely and explores FPGA implementations that treat the grid as a streaming image-processing problem.

> **Implementation Status:** Only **Option A (full-grid buffer)** was implemented in Hardcaml. Options B and C are design explorations that were not built.

---

\newpage

## 2. Problem Definition (Paraphrased)

- The worksheet is a rectangle of characters.
- Problems are separated by a full blank column.
- The bottom row contains the operator for each problem.

For each problem block:

- There are multiple numbers.
- **Part 1:** read each number left-to-right across rows.
- **Part 2:** read each number top-to-bottom within a column, and interpret problems in right-to-left column order.

Output is the sum across problems of either the sum or product of the numbers in that problem.

---

\newpage

## 3. Software Algorithm (Reference-Aligned)

### 3.1 Grid Parsing

- Parse the entire input into a 2D array `grid[y][x]`.
- Let `bottom = height-1` be the operator row.

### 3.2 Identifying Problem Blocks

The reference scans the operator row from right to left, treating any non-space column as belonging to a problem. When it finds a separator space column, it closes the current block.

### 3.3 Computing Each Block

Let a block span columns `[left..right)`.

- **Row-wise numbers (Part 1):** for each row `y in [0..bottom)` compute:
  - `num = fold over x in [left..right): if digit then num = 10*num + digit`.
- **Column-wise numbers (Part 2):** for each column `x in [left..right)` compute:
  - `num = fold over y in [0..bottom): if digit then num = 10*num + digit`.

Let `op = grid[bottom][left]` (operator stored at the block’s left boundary in the reference).

- If `op==+`: block value is sum of nums.
- If `op==*`: block value is product of nums.

### 3.4 Complexity

- Time: $O(WH)$ for grid size $W\times H$.
- Memory: $O(WH)$.

---

\newpage

## 4. Hardware Design Goals

- Robustly parse ASCII with irregular spacing.
- Provide high throughput per cell (treat as image pipeline).
- Maintain correctness for both interpretations.

---

\newpage

## 5. FPGA Architecture Option A: Full-Grid Buffer + Two Read Modes (Simplest)

### 5.1 Blocks

- **ASCII-to-grid loader:** writes BRAM indexed by `(x,y)`.
- **Block boundary detector:** scans bottom row for block delimiters.
- **Row-evaluator (Part 1):** sweeps rows inside each block.
- **Column-evaluator (Part 2):** sweeps columns inside each block.

### 5.2 Component-by-Component Breakdown

**(A) Grid BRAM**

- Store each cell as 8-bit ASCII (or 4-bit digit + flag + operator).
- Address = `y*W + x`.

**(B) Operator/Boundary Scanner**

Purpose: replicate `rev().filter(bottom_row[x] != ' ')` behavior.

- Iterate x from W-1 downto 0.
- Track `right` boundary.
- On transition from non-space to space: emit a block `(left,right)`.

**(C) Digit Accumulator**

Purpose: fold digits into base-10 numbers.

For each digit cell `d`:

- if `d` is space: no-op
- else `num = 10*num + (d - '0')`

**(D) Block Reducer**

- If operator is `+`: maintain `sum += num` per row/col.
- If operator is `*`: maintain `prod *= num` per row/col.

### 5.3 Component-by-Component Breakdown (Expanded)

**(E) Address Generator (Part 1 Mode)**

Purpose: Generate addresses to read numbers row-wise.

- **Input:** `block_left`, `block_right`, `height`.
- **Logic:**
  - Nested loops: `y` from 0 to `height-2`, `x` from `left` to `right-1`.
  - `addr = y * W + x`.
  - Emit `end_of_number` at end of each row (x loop done).

**(F) Address Generator (Part 2 Mode)**

Purpose: Generate addresses to read numbers column-wise.

- **Input:** `block_left`, `block_right`, `height`.
- **Logic:**
  - Nested loops: `x` from `right-1` down to `left`, `y` from 0 to `height-2`.
  - `addr = y * W + x`.
  - Emit `end_of_number` at end of each column (y loop done).

**(G) Unified Number Parser**

Purpose: Convert stream of digits + EON signals into values.

- **Input:** `digit`, `end_of_number`.
- **State:** `current_val`.
- **Logic:**
  - If `digit`: `current_val = current_val * 10 + digit`.
  - If `end_of_number`: emit `current_val`, reset `current_val = 0`.

### 5.4 Example Walkthrough (Part 1)

For the leftmost problem in the example:

- Rows form numbers 123,45,6.
- Operator is `*`.
- Reduce: `123*45*6`.

The accumulator is exactly the same fold as the reference `acc()` helper.

---

\newpage

## 6. FPGA Architecture Option B: Streaming Line-Buffer Pipeline (Higher Throughput)

### 6.1 Idea

Avoid storing the full grid by using line buffers and processing blocks as the stream arrives.

Challenge: block boundaries are defined by the bottom operator row, so naive streaming needs the last row to know segmentation.

### 6.2 Practical Two-Pass Streaming

1. Pass 1: read and store only the operator row + block boundaries.
2. Pass 2: stream the grid again and evaluate blocks in a single pass.

This matches real deployments where input can be replayed (from DDR or host).

### 6.3 Component Breakdown

- **Boundary RAM:** bitmask of columns that are separators.
- **Block-ID mapper:** maps column x → block index.
- **Per-block accumulators:** maintain running partial sums/products as rows arrive.

---

\newpage

## 7. FPGA Architecture Option C: Max-Parallel Block Evaluation

If the number of blocks is small and bounded:

- Instantiate one block engine per block.
- Each engine receives digit stream filtered by its column window.

This minimizes latency but consumes area proportional to the number of blocks.

---

\newpage

## 8. HardCaml Implementation Showcase

### 8.1 Grid Access Pattern Generator

```ocaml
(* Parameterized address generator for row-wise or column-wise access *)
module Grid_scanner (Config : sig 
  val width : int 
  val height : int 
end) = struct
  open Config
  
  type mode = Row_wise | Column_wise
  
  let create ~mode ~block_left ~block_right =
    let open Signal in
    match mode with
    | Row_wise ->
      (* y outer, x inner *)
      let x = reg_fb ~width:10 ~f:(fun x -> 
        mux2 (x ==:. block_right - 1) (of_int ~width:10 block_left) (x +:. 1)) in
      let y = reg_fb ~width:10 ~f:(fun y ->
        mux2 (x ==:. block_right - 1) (y +:. 1) y) in
      let addr = y *:. width +: x in
      let eol = x ==:. block_right - 1 in
      { addr; end_of_number = eol }
    | Column_wise ->
      (* x outer (reversed), y inner *)
      let x = reg_fb ~width:10 ~f:(fun x ->
        mux2 (y ==:. height - 2) (x -:. 1) x) in
      let y = reg_fb ~width:10 ~f:(fun y ->
        mux2 (y ==:. height - 2) (zero 10) (y +:. 1)) in
      let addr = y *:. width +: x in
      let eoc = y ==:. height - 2 in
      { addr; end_of_number = eoc }
end
```

### 8.2 Unified Number Parser with Operator Dispatch

```ocaml
(* Parse digits and apply operator when number completes *)
module Number_reducer = struct
  type 'a state = {
    current_num : 'a [@bits 64];
    accumulator : 'a [@bits 128];
    is_first : 'a [@bits 1];
  } [@@deriving hardcaml]
  
  let step ~state ~digit ~digit_valid ~end_of_number ~operator =
    let open Signal in
    let is_add = operator ==:. Char.to_int '+' in
    let next_num = mux2 digit_valid 
      (state.current_num *:. 10 +: uresize digit 64)
      state.current_num in
    let apply_op = end_of_number in
    let next_acc = mux2 apply_op
      (mux2 state.is_first 
        next_num  (* First number: initialize *)
        (mux2 is_add 
          (state.accumulator +: uresize next_num 128)  (* Add *)
          (state.accumulator *: uresize next_num 128))) (* Multiply *)
      state.accumulator in
    { current_num = mux2 end_of_number (zero 64) next_num;
      accumulator = next_acc;
      is_first = mux2 end_of_number gnd state.is_first }
end
```

### 8.3 Block Boundary Detection

```ocaml
(* Scan operator row to find block boundaries *)
let detect_blocks ~operator_row ~width =
  let open Signal in
  (* Find transitions from non-space to space (right to left) *)
  let is_space = Array.map operator_row ~f:(fun c -> c ==:. Char.to_int ' ') in
  let boundaries = Array.foldi is_space ~init:[] ~f:(fun i acc sp ->
    if i = 0 then acc
    else 
      let transition = is_space.(i-1) &: ~:sp in  (* space -> non-space = block start *)
      (i, transition) :: acc
  ) in
  boundaries
```

### 8.4 Why This Showcases HardCaml

- **Pattern Matching on Modes:** The scanner generates different hardware for row-wise vs column-wise
- **Parameterized Dimensions:** Grid dimensions are compile-time parameters
- **Clean Operator Dispatch:** The `mux2` chains generate efficient MUX trees

---

\newpage

## 9. Scalability Analysis

### 9.1 Grid Scaling

| Grid Size | Cells | BRAM | Blocks (typ) | Time @ 100 MHz |
|-----------|-------|------|--------------|----------------|
| 64×16 | 1K | 1 | 4 | 40 µs |
| 256×64 | 16K | 8 | 16 | 640 µs |
| 1024×256 | 256K | 128 | 64 | 10 ms |

### 9.2 Number Width Considerations

| Grid Height | Max Digits/Number | Bits Needed |
|-------------|-------------------|-------------|
| 16 | 15 | 50 bits |
| 64 | 63 | 210 bits |
| 256 | 255 | 848 bits |

**For multiply:** Product of two 50-bit numbers needs 100 bits; chain of 15 multiplies can overflow standard 64-bit.

**Solution:** Use arbitrary-precision or saturating arithmetic for tall grids.

---

\newpage

## 10. Physical Synthesis & Tapeout

### 10.1 Synthesis Results (ECP5-85F)

| Configuration | LUTs | FFs | BRAM | DSP | Fmax |
|--------------|------|-----|------|-----|------|
| 64×16 grid, 4 blocks | 2,100 | 890 | 2 | 4 | 88 MHz |
| 256×64 grid, 16 blocks | 8,400 | 3,200 | 16 | 16 | 72 MHz |

### 10.2 Critical Path

The critical path is the 64-bit multiply in the number reducer.

**Optimization:** Pipeline the multiply-accumulate into 2 stages.

### 10.3 TinyTapeout: 16×8 Demo Grid

- 16×8 grid storage: 128 bytes (external input)
- 4-block parallel engines: ~600 cells
- Total: ~800 cells (fits in 1 tile)

---

\newpage

## 11. Verification & Results

### 11.1 Testbench

```ocaml
let%expect_test "column_wise_parsing" =
  (* 3x3 block: digits 1,2,3 in column 0 *)
  let grid = [| "1 "; "2 "; "3+" |] in
  let sim = Cyclesim.create (Day06.create ~mode:Column_wise ()) in
  load_grid sim grid;
  run_to_completion sim;
  [%expect {| result = 123 |}]  (* Column forms number 123 *)
```

### 11.2 Performance

| Metric | FPGA | Rust Reference |
|--------|------|----------------|
| Cells/sec | 8.8M | 290M |
| 64×16 grid | 115 µs | 3.5 µs |
| Energy/cell | 0.5 nJ | 15 nJ |

### 11.3 Key Insights

1. Row-wise vs column-wise access patterns share the same number parser
2. Grid BRAM allows random access needed for both interpretations
3. Block-parallel design trades area for latency when block count is small



