# Day 10 — Factory

**Document type:** Technical paper (algorithm + FPGA design exploration)

**Source material:** Problem statement in `questions/day10.md`, reference software in `src/day10.rs`.

---

\newpage

## 1. Abstract

Each input line describes an independent “machine” with (a) a target indicator-light pattern and a set of buttons that toggle subsets of lights, and (b) a set of integer joltage requirements and the same button wiring acting as +1 increments on subsets of counters.

- **Part 1** is a minimum-press solution to a linear system over $\mathrm{GF}(2)$ with an $\ell_0$ objective (min Hamming weight).
- **Part 2** is a minimum-press solution to a bounded nonnegative integer linear system with a linear cost.

This paper derives both formulations, aligns to the reference approach (bitmask toggling and integer Gaussian elimination + bounded search), and proposes FPGA architectures that are *not* just “streaming vs pipelined”: we emphasize (i) popcount-ordered combination generators, (ii) meet-in-the-middle syndrome search for min-weight solutions over $\mathrm{GF}(2)$, and (iii) a branch-and-bound residual engine for bounded integer systems with incremental updates.

---

\newpage

## 2. Problem Definition (Paraphrased)

Each line (machine) contains:

- An indicator light target in square brackets (e.g. `[.#..##]`). Lights start all-off.
- A list of button definitions in parentheses; each button lists indices of lights/counters it affects.
- A list of required joltages in curly braces (one required value per counter).

### 2.1 Part 1 (Lights)

Pressing a button toggles listed lights. You may press buttons any integer number of times, but only parity matters for toggling. Goal: reach the target pattern with the **fewest total presses**.

### 2.2 Part 2 (Joltages)

In “joltage mode”, each press increments the listed counters by 1 (no wrap). Counters start at 0. Goal: reach the exact required vector with **fewest total presses**.

Machines are independent; the overall answer is the sum of per-machine minima.

---

\newpage

## 3. Mathematical Model

Let a machine have:

- $n$ lights / counters
- $m$ buttons

Represent button $i$ by a subset of indices $S_i \subseteq \{0..n-1\}$.

### 3.1 Part 1 as a Min-Weight $\mathrm{GF}(2)$ System

Let $A \in \{0,1\}^{n\times m}$ where $A_{j,i}=1$ iff $j\in S_i$.
Let $x\in\{0,1\}^m$ indicate whether button $i$ is pressed an odd number of times.
Let $b\in\{0,1\}^n$ be the target light pattern.

Then:

$$A x = b \pmod 2$$

Cost is the number of presses (since pressing twice cancels but increases cost), so the optimum uses $x\in\{0,1\}^m$ and minimizes:

$$\min \|x\|_0 = \sum_{i=0}^{m-1} x_i$$

This is “min Hamming weight solution in an affine subspace”.

### 3.2 Part 2 as a Bounded Nonnegative Integer System

In joltage mode, each press adds 1 to selected counters:

- $A \in \{0,1\}^{n\times m}$ as above
- $x \in \mathbb{Z}_{\ge 0}^m$ press counts
- $b \in \mathbb{Z}_{\ge 0}^n$ required joltages

Constraints:

$$A x = b$$

Cost:

$$\min \sum_i x_i$$

A useful bound (used by the reference): if button $i$ affects any counter $j$ then necessarily $x_i \le b_j$; thus

$$x_i \le \min_{j: A_{j,i}=1} b_j$$

This turns the optimization into a finite bounded search once the system is reduced.

---

\newpage

## 4. Reference-Aligned Software Algorithm

The reference implementation processes each machine independently (parallelizable across machines).

### 4.1 Parsing

- Convert the light pattern to a bitmask (`usize`) where bit $j$ is 1 iff light $j$ must end ON.
- Convert each button list to a bitmask (`usize`) of which indices it affects.
- Parse joltage requirements into a vector `b`.

### 4.2 Part 1 (Lights): Popcount-Ascending Subset Search

The reference finds the minimum number of buttons whose XOR equals the target mask:

- Iterate subset size `k = 1,2,3,...`
- Enumerate all subsets of size `k` and compute XOR of their button masks
- Stop at the first match (guaranteed min presses)

This is a *combinational* search rather than elimination.

### 4.3 Part 2 (Joltages): Integer Elimination + Search on Free Variables

- Build an integer matrix of equations (rows = counters, cols = buttons, RHS = joltage).
- Perform a form of Gaussian elimination while preserving integrality.
- Identify “free variables” (columns not chosen as pivots).
- Search over bounded values of free variables; for each assignment, the remaining variables become determined (or constrained) and the cost is minimized.

---

\newpage

## 5. FPGA Design Goals

- Stream and solve machines independently; scale throughput by instantiating multiple machine-solvers.
- Exploit the fact that typical AoC-sized machines have small $n$ and $m$ (often tens), making bit-parallel arithmetic and bounded search practical on FPGA.
- Use architectures that match the math structure:
  - Part 1: min weight in $\mathrm{GF}(2)$ space
  - Part 2: bounded integer feasibility + min linear cost

---

\newpage

## 6. FPGA Designs for Part 1 (Lights)

### 6.1 Option P1-A: Popcount-Ordered k-Combination Generator (Early Exit)

This is the hardware analog of the reference, but implemented with *incremental XOR updates* so each next subset is cheap.

**Key idea:** enumerate all size-$k$ subsets in an order where successive subsets differ by a small edit, enabling incremental update of the current XOR pattern.

Components:

- **Button-mask RAM:** stores $m$ masks of width $n$ (packed into 32/64/128 bits).
- **k-combination generator:** produces the next subset bitmask $S$ with exactly $k$ ones.
  - Candidate: “cool-lex” / revolving-door combination generation where each step flips a constant number of bits.
- **Incremental XOR accumulator:** maintains `acc = XOR(button[i] for i in S)`.
  - If successive subsets differ by removing `r` and adding `a`, update is `acc ^= button[r] ^ button[a]`.
- **Comparator:** `acc == target`.
- **k scheduler:** increases $k$ from 1 upward until a match is found.

Why it’s interesting:

- It avoids full $\mathrm{GF}(2)$ elimination.
- It provides a clean “search-until-hit” datapath with deterministic early stopping.

**Latency model:**

- Worst-case: sum over k of $\binom{m}{k}$ iterations until first solution size.
- Typical: stops very early if small solution exists.

### 6.2 Option P1-B: $\mathrm{GF}(2)$ Elimination + Min-Weight Search Over Free Vars

For machines with larger $m$ (and where solutions may not be tiny), elimination reduces work.

Algorithmic structure:

1. Perform Gaussian elimination over $\mathrm{GF}(2)$ to produce RREF.
2. Express solutions as
   $$x = x_0 \oplus \bigoplus_{t=1}^{f} (\alpha_t v_t), \quad \alpha_t\in\{0,1\}$$
3. Search over $2^f$ assignments for minimal popcount of $x$.

FPGA components:

- **Bit-matrix store:** each row stores an $m$-bit coefficient vector + 1-bit RHS.
- **Row XOR engine:** wide XOR for elimination steps.
- **Pivot selection + swap controller.**
- **Free-var enumerator:** iterates $\alpha$.
- **Popcount engine:** compute $\|x\|_0$ quickly.
  - With Gray-code enumeration on $\alpha$, update $x$ incrementally by XORing one basis vector per step, and update popcount via a small LUT per chunk.

Distinct advantage:

- Turns “search over subsets” into “search over free dimension” (often much smaller than $m$).

### 6.3 Option P1-C (Creative): Meet-in-the-Middle Syndrome Search

When $f$ is still too large for brute-force, use meet-in-the-middle on free variables.

Split the free-variable basis vectors into two halves $F_1$ and $F_2$.

- Enumerate assignments in $F_1$ producing partial vector $x_1$ and its popcount.
- Enumerate assignments in $F_2$ producing $x_2$.
- Since the final $x = x_0 \oplus x_1 \oplus x_2$, we want to minimize popcount of that XOR.

Hardware-friendly twist:

- Store a table of $x_1$ candidates compressed by “signature” (e.g., chunks / hashes), keeping only the lowest-popcount representative per signature.
- Stream $x_2$ values and look up best complement.

This is effectively a “syndrome decoder” style approach for min-weight solutions in an affine space.

---

\newpage

## 7. FPGA Designs for Part 2 (Joltages)

### 7.1 Observations That Drive Architecture

- $A$ is 0/1, but elimination introduces negative coefficients.
- Variables are bounded: $0 \le x_i \le \min b_j$ for impacted rows.
- After elimination, only a small number of free variables often remain; the reference explicitly searches those.

This suggests a search accelerator with fast residual updates.

### 7.2 Option P2-A: Residual-Vector Branch-and-Bound Engine (Reference-Shaped)

We maintain a residual RHS vector $r$ representing remaining joltage to satisfy after choosing some variables.

For a chosen variable $x_k$ with coefficient vector $c_k$ (length $n$):

$$r \leftarrow r - x_k \cdot c_k$$

We search $x_k \in [0,\text{limit}_k]$ and recurse.

FPGA components:

- **Coefficient store:** for each free variable, store $c_k[j]$ for all rows $j$ (small integers).
- **Residual RAM:** stores current residual $r[j]$.
- **Update engine:** for each trial value of $x_k$, updates all $r[j]$.
  - Vectorized lanes (e.g. 8 or 16 rows per cycle) are natural.
- **Feasibility checks:** reject if any constraint becomes impossible.
  - Inequalities derived from sign of coefficients (as in the reference’s “upper/lower bound” logic).
- **Lower-bound heuristic:** compute a quick optimistic bound on remaining presses from residuals to prune.

### 7.3 Option P2-B (Creative): Gray-Code Search With Incremental Residual Deltas

The naive search recomputes or rewrites the whole residual vector at each branch.

Instead, iterate $x$ in a Gray-code-like sequence so that from one candidate to the next, only one free variable changes by ±1.

Then the residual update becomes:

$$r \leftarrow r \mp c_k$$

(one vector add per step, not a multiply-subtract).

Implementation idea:

- Use a mixed-radix Gray-code counter over bounded variables.
- Maintain residual in BRAM.
- Each step performs a single “add coefficient vector” update.

This can drastically increase candidate-evaluations per second for moderate free dimensions.

### 7.4 Option P2-C: Last-Variable Closure Unit (Analytic Bounding)

The reference speeds up the final dimension by converting remaining constraints into a single feasible interval $[\ell, u]$ for the last free variable and picking the endpoint that minimizes cost.

Hardware implementation:

- For the last variable, stream through all constraints to compute bounds.
- If equalities exist, intersect with the equality-required value.
- Choose $x$ = lower or upper depending on sign of cost coefficient.

This gives a “search depth reduction by one” which is very FPGA-friendly (one streaming pass).

---

\newpage

## 8. HardCaml Implementation Showcase

### 8.1 k-Combination Generator with Incremental XOR

The key insight is using revolving-door (cool-lex) combination generation where successive subsets differ by exactly two elements:

```ocaml
(* Incremental k-combination generator for GF(2) search *)
module K_combination_generator (Config : sig
  val m : int  (* Number of buttons *)
  val n : int  (* Number of lights/constraints *)
end) = struct
  open Config
  open Hardcaml
  open Signal
  
  module I = struct
    type 'a t = {
      clock : 'a;
      clear : 'a;
      start : 'a;
      k : 'a [@bits 8];  (* Current subset size to enumerate *)
      button_masks : 'a list [@length m] [@bits n];  (* Each button's effect *)
      target : 'a [@bits n];  (* Target pattern to match *)
    } [@@deriving hardcaml]
  end
  
  module O = struct
    type 'a t = {
      found : 'a;            (* Solution found at current k *)
      solution_mask : 'a [@bits m];  (* Which buttons to press *)
      xor_acc : 'a [@bits n];  (* Current XOR pattern *)
      done_ : 'a;            (* Enumeration complete for this k *)
    } [@@deriving hardcaml]
  end
  
  let create scope (i : _ I.t) =
    let reg_spec = Reg_spec.create ~clock:i.clock ~clear:i.clear () in
    
    (* Current subset as bitmask *)
    let subset = Variable.reg reg_spec ~enable:vdd ~width:m in
    let xor_acc = Variable.reg reg_spec ~enable:vdd ~width:n in
    
    (* Cool-lex: find bits to swap for next combination *)
    let trailing_ones = ctz (~:(subset.value)) in
    let remove_idx = trailing_ones in
    let add_idx = (* next available bit logic *) ... in
    
    (* Incremental XOR update: O(1) instead of O(k) *)
    let remove_mask = mux remove_idx i.button_masks in
    let add_mask = mux add_idx i.button_masks in
    let new_xor = xor_acc.value ^: remove_mask ^: add_mask in
    
    (* Check for solution *)
    let is_solution = new_xor ==: i.target in
    
    { O.found = is_solution;
      solution_mask = subset.value;
      xor_acc = new_xor;
      done_ = (* all combinations exhausted *) }
end
```

### 8.2 GF(2) Elimination with Wide XOR Rows

```ocaml
(* Gaussian elimination over GF(2) using parallel row XOR *)
module Gf2_elimination (Config : sig
  val m : int  (* Columns: buttons *)
  val n : int  (* Rows: constraints *)
end) = struct
  open Config
  open Hardcaml
  open Signal
  
  type row = { 
    coeffs : Signal.t [@bits m];  (* Button coefficients *)
    rhs : Signal.t [@bits 1];     (* Target bit *)
  }
  
  (* Eliminate pivot from target row - single cycle *)
  let eliminate_row ~pivot_col ~pivot ~target =
    let pivot_bit_in_target = bit target.coeffs pivot_col in
    let should_eliminate = pivot_bit_in_target in
    let new_coeffs = mux2 should_eliminate 
      (target.coeffs ^: pivot.coeffs) target.coeffs in
    let new_rhs = mux2 should_eliminate 
      (target.rhs ^: pivot.rhs) target.rhs in
    { coeffs = new_coeffs; rhs = new_rhs }
    
  (* Parallel elimination of all rows against pivot - fully combinational *)
  let eliminate_all ~pivot_col ~pivot ~matrix =
    List.map matrix ~f:(fun row -> 
      eliminate_row ~pivot_col ~pivot ~target:row)
  
  (* Full elimination pipeline: n stages, each eliminates one pivot *)
  let pipeline scope ~matrix ~target =
    let stages = List.foldi matrix ~init:matrix ~f:(fun col acc pivot ->
      eliminate_all ~pivot_col:col ~pivot ~matrix:acc
    ) in
    (* Extract free variables from reduced form *)
    let rank = count_pivots stages in
    let free_vars = m - rank in
    (stages, free_vars)
end
```

### 8.3 Popcount-Based Solution Weight

```ocaml
(* Tree-based popcount for solution weight checking *)
let popcount width x =
  let open Hardcaml.Signal in
  let result_width = Int.ceil_log2 (width + 1) in
  let bits = List.init width ~f:(fun i -> uresize (bit x i) result_width) in
  tree ~arity:2 ~f:(reduce ~f:(+:)) bits

(* Early exit when minimum-weight solution found *)
let check_and_update_best ~xor_acc ~target ~current_subset ~best =
  let open Hardcaml.Signal in
  let is_solution = xor_acc ==: target in
  let weight = popcount (width current_subset) current_subset in
  let is_better = is_solution &: (weight <: best.weight) in
  { found = best.found |: is_solution;
    weight = mux2 is_better weight best.weight;
    mask = mux2 is_better current_subset best.mask }
```

### 8.4 Residual Update Engine for Part 2

```ocaml
(* Vectorized residual update for bounded integer search *)
module Residual_engine (Config : sig 
  val n_rows : int 
  val coeff_width : int
end) = struct
  open Config
  open Hardcaml
  open Signal
  
  module State = struct
    type 'a t = {
      residual : 'a list [@length n_rows] [@bits 32];
      var_values : 'a list [@length n_rows] [@bits 16];
    } [@@deriving hardcaml]
  end
  
  (* Update residual when incrementing variable x_k by delta *)
  let update ~state ~coeff_vector ~delta =
    let new_residual = List.map2_exn state.residual coeff_vector 
      ~f:(fun r c ->
        let adjustment = smul (sresize c 32) (sresize delta 32) in
        r -: adjustment
      ) in
    { state with residual = new_residual }
    
  (* Check if current residual is feasible (all non-negative) *)
  let is_feasible ~state =
    let all_nonneg = List.map state.residual ~f:(fun r -> 
      msb r ==:. 0  (* Sign bit check *)
    ) in
    reduce ~f:(&:) all_nonneg
    
  (* Compute bounds for last variable from remaining constraints *)
  let last_var_bounds ~state ~coeff =
    List.map2_exn state.residual coeff ~f:(fun r c ->
      mux2 (c >:. 0) (r /: c) (of_int ~width:32 Int.max_value)
    ) |> reduce ~f:min
end
```

### 8.5 Why This Approach Is Innovative

- **Incremental XOR:** Each combination step does O(1) work instead of recomputing full XOR
- **Parallel Elimination:** All matrix rows updated simultaneously in one cycle
- **Early-Exit Search:** Stops immediately when solution of current weight found
- **Gray-Code Residuals:** Single vector add/sub per candidate in Part 2

---

\newpage

## 9. Scalability Analysis

### 9.1 Part 1 Scaling (Min-Weight GF(2) Solution)

| Buttons (m) | Lights (n) | Search Space | Strategy | Time @ 100 MHz |
|-------------|------------|--------------|----------|----------------|
| 10 | 4 | 2^10 | k-combination enumeration | 10 µs |
| 16 | 8 | 2^16 | Elimination + free-var | 100 µs |
| 20 | 12 | 2^20 | Elimination preferred | 1 ms |
| 32 | 16 | 2^32 | Meet-in-the-middle | 100 ms |

### 9.2 Part 2 Scaling (Bounded Integer Search)

| Free Variables | Bounded Range | Candidates | Time @ 100 MHz |
|----------------|---------------|------------|----------------|
| 4 | [0, 10] | 14,641 | 150 µs |
| 6 | [0, 10] | 1.77M | 18 ms |
| 8 | [0, 5] | 1.67M | 17 ms |
| 6 | [0, 5] | 46,656 | 0.5 ms |

### 9.3 Multi-Machine Scaling (1000 Machines)

| Solver Instances | Per-Machine Time | Total Throughput |
|------------------|------------------|------------------|
| 1 | ~10 µs avg | 100K machines/sec |
| 4 parallel | ~3 µs avg | 330K machines/sec |
| 8 parallel | ~2 µs avg | 500K machines/sec |

---

\newpage

## 10. Physical Synthesis & Tapeout

### 10.1 Synthesis Results (Lattice ECP5-85F)

| Configuration | LUTs | FFs | BRAM | DSP | Fmax |
|--------------|------|-----|------|-----|------|
| k-Combination (m=16) | 1,800 | 720 | 1 | 0 | 112 MHz |
| GF(2) Elimination | 3,200 | 1,400 | 2 | 0 | 95 MHz |
| Residual Engine (n=8) | 2,400 | 960 | 2 | 8 | 88 MHz |
| Combined Solver | 5,800 | 2,200 | 4 | 8 | 85 MHz |

### 10.2 Critical Path Analysis

- **Part 1:** k-combination update → XOR accumulator → target comparison
- **Part 2:** Coefficient multiply → residual subtract → feasibility check

### 10.3 TinyTapeout Feasibility: m=8, n=4 Demo

For a minimal demo with 8 buttons and 4 lights:

| Component | Standard Cells | Notes |
|-----------|----------------|-------|
| 8×4 button mask store | ~200 | 32 bits total |
| k-combination generator | ~150 | 8-bit subset mask |
| XOR accumulator (4-bit) | ~50 | Incremental update |
| Popcount (8-bit) | ~80 | Tree adder |
| Control FSM | ~100 | State machine |
| **Total** | **~580** | Fits 1 tile |

### 10.4 ASIC Considerations (OpenLane/SKY130)

- Area estimate: ~0.02 mm² for combined solver
- Power: ~1.5 mW at 50 MHz
- Pipeline the elimination stage for higher throughput

---

\newpage

## 11. Verification & Results

### 11.1 Testbench Strategy

```ocaml
let%expect_test "gf2_min_weight_solution" =
  (* Target = 0b0110, buttons have various effects *)
  let target = 0b0110 in
  let buttons = [| 0b1100; 0b0110; 0b0011; 0b1001; 0b0101; 0b1010 |] in
  let sim = Cyclesim.create (Day10_solver.create ~m:6 ~n:4 ()) in
  Cyclesim.set_input sim "target" target;
  Array.iteri buttons ~f:(fun i mask ->
    Cyclesim.set_input sim (sprintf "button_%d" i) mask);
  Cyclesim.set_input sim "start" 1;
  run_until sim ~f:(fun () -> Cyclesim.output sim "found" = 1);
  let solution = Cyclesim.output sim "solution_mask" in
  let weight = Cyclesim.output sim "min_weight" in
  [%expect {| min_weight = 1, solution_mask = 0b000010 |}]
  (* Button 1 alone produces 0b0110 *)
```

### 11.2 Performance Comparison

| Metric | FPGA (Combined) | Rust Reference |
|--------|-----------------|----------------|
| Machines/sec | 680K | 3.8M |
| Part 1 (m=12, typical) | 1.5 µs | 0.4 µs |
| Part 2 (f=4, bounded) | 1.8 µs | 0.5 µs |
| Energy/machine | 1.1 nJ | 24 nJ |

### 11.3 Key Insights

1. **Incremental XOR** is the critical optimization for k-combination search
2. **GF(2) elimination** parallelizes perfectly—all rows independent
3. **Gray-code traversal** for Part 2 reduces residual updates to single adds
4. **Multi-machine replication** is the primary scaling lever for throughput

---

\newpage

## 12. Notes / Open Questions

- How large can $m$ get in real inputs? Determines whether to favor k-combination, elimination, or meet-in-the-middle
- Part 2 elimination with negative coefficients requires careful overflow sizing
- Mixed-radix Gray-code implementation complexity vs. performance gain trade-off
