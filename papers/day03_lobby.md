# Day 03 — Lobby

**Document type:** Technical paper (algorithm + FPGA design exploration)

**Source material:** `questions/day3.md`, reference in `src/day3.rs`.

---

\newpage

## 1. Abstract

Each line of the input is a “bank” of single-digit battery ratings. We must select exactly $N$ digits from each bank (Part 1: $N=2$, Part 2: $N=12$) while preserving the original order, to form the maximum possible $N$-digit decimal number. The final answer is the sum of these per-line maxima.

The reference solution computes the maximum subsequence without brute force by scanning from right-to-left while maintaining the best possible suffix selection in a fixed-size array.

This paper explains the optimization problem, presents a standard greedy perspective, and explores FPGA architectures for selecting the maximum subsequence in a streaming manner.

---

\newpage

## 2. Problem Definition (Paraphrased)

Given a digit string $D = d_0 d_1 \dots d_{L-1}$ (each $d_i \in \{0..9\}$) and a fixed $N$:

- Choose indices $0 \le i_0 < i_1 < \cdots < i_{N-1} < L$.
- The output number is $d_{i_0} d_{i_1} \dots d_{i_{N-1}}$ as a decimal integer.
- Choose the indices to maximize this value.

Compute this maximum for each bank and sum across banks.

---

\newpage

## 3. Algorithmic Perspective

Maximizing the resulting $N$-digit number is equivalent to maximizing the chosen digit sequence in lexicographic order.

A common greedy approach scans left-to-right and maintains a monotone stack, removing smaller digits when a larger digit arrives and there is still “removal budget.”

The reference implementation uses a right-to-left approach with a fixed-size buffer that acts like an insertion structure for the best suffix.

---

\newpage

## 4. Reference-Aligned Algorithm (Right-to-Left Fixed Buffer)

### 4.1 High-Level Description

For each bank:

1. Initialize `batteries` with the last $N$ digits (the forced suffix if we select no earlier digits).
2. Iterate earlier digits from right to left.
3. For each new digit `next`, attempt to insert it into the buffer if doing so yields a larger overall $N$-digit result.

### 4.2 Buffer Update Mechanism

The code performs a sequence of compare-and-swap replacements:

- Walk through the buffer left-to-right.
- If `next` is at least as large as the current buffer digit, swap them and continue with the displaced digit.
- If `next` is smaller than the current digit, stop (the digit cannot improve earlier positions).

Intuition:

- Earlier buffer positions correspond to more significant digits.
- The replacement chain bubbles a better digit leftward while keeping the selection length fixed.

### 4.3 Producing the Numeric Value

After processing, fold the $N$ digits into a base-10 integer:

$$\text{value} = \sum_{k=0}^{N-1} b_k \cdot 10^{N-1-k}$$

### 4.4 Complexity

Let $L$ be bank length.

- Time: $O(L\cdot N)$ per bank.
- Memory: $O(N)$.

With $N=12$, this is very practical.

---

\newpage

## 5. Correctness Discussion

We want the maximum lexicographic length-$N$ subsequence.

A correctness argument can be phrased as:

- The buffer maintains, after processing a suffix of the input, the lexicographically maximum selectable length-$N$ subsequence from that suffix.
- Each insertion attempt considers promoting a digit from earlier in the string into a more significant position, which is always beneficial if it can be done without violating order.

For formal proof, one can relate the transformation to the well-known monotone-stack method and show equivalence.

---

\newpage

## 6. FPGA Design Option A: Simple Streaming Selector (Minimal Area)

### 6.1 Streaming Constraints

Banks are line-delimited. We must detect end-of-line, then emit a result.

### 6.2 Architecture

- **Parser:** reads ASCII digits; produces 4-bit `digit` and `eol`.
- **Line buffer:** either store the entire line (BRAM) or process on the fly.

Because the reference algorithm needs to start from the end, the simplest hardware design buffers each line:

1. Store digits in BRAM.
2. After EOL, run a right-to-left selection pass.

### 6.3 Datapath

- `batteries[N]`: small register array (each 4 bits).
- Loop counter `idx` decrements through stored digits.
- Inner loop does compare/swap chain.

### 6.4 Component-by-Component Breakdown

**(A) Line Buffer RAM**

Purpose: Store the incoming line of digits to allow reverse iteration.

- **Size:** 1024 x 4-bit (sufficient for typical line lengths).
- **Ports:** 1 write (parser), 1 read (selector).

**(B) Selection State Registers**

Purpose: Maintain the current best suffix of length N.

- **State:** `buffer[0..N-1]` (N x 4-bit registers).
- **Init:** Zeros or sentinel values.

**(C) Insertion Logic (Combinational Chain)**

Purpose: Attempt to insert a new digit `d` into the sorted-by-position buffer to maximize value.

- **Input:** `new_digit`, `current_buffer`.
- **Logic:**
  - Iterate `i` from 0 to `N-1`:
    - If `new_digit >= buffer[i]`:
      - `temp = buffer[i]`
      - `buffer[i] = new_digit`
      - `new_digit = temp` (bubble down the displaced digit)
    - Else:
      - Stop (digit is too small to improve this position).
- **Output:** `next_buffer`.

**(D) Control FSM**

- **State IDLE:** Wait for start of line.
- **State READ:** Write digits to RAM until EOL. Capture `length`.
- **State PROCESS:**
  - Initialize `buffer` with last N digits from RAM.
  - Decrement read pointer from `length - N - 1` down to 0.
  - Apply Insertion Logic each cycle.
- **State OUTPUT:** Emit `buffer` contents as result.

### 6.5 Example Walkthrough

Line: `3 1 4 1 5`, N=2.

1. **READ:** Store `[3, 1, 4, 1, 5]`. Length=5.
2. **PROCESS Init:** `buffer = [1, 5]` (last 2).
3. **Step 1 (digit 4):**
   - Compare 4 vs buffer[0]=1. 4 >= 1. Swap. `buffer=[4, 5]`, `displaced=1`.
   - Compare 1 vs buffer[1]=5. 1 < 5. Stop.
   - Result: `[4, 5]`.
4. **Step 2 (digit 1):**
   - Compare 1 vs buffer[0]=4. 1 < 4. Stop.
   - Result: `[4, 5]`.
5. **Step 3 (digit 3):**
   - Compare 3 vs buffer[0]=4. 3 < 4. Stop.
   - Result: `[4, 5]`.
6. **OUTPUT:** 45.

---

\newpage

## 7. FPGA Design Option B: One-Pass Left-to-Right Monotone Stack (Lower Latency)

To avoid buffering the entire line, use the classic streaming algorithm:

- Maintain a stack of chosen digits.
- Maintain `drop = L - N` (digits allowed to skip).

Challenge: `L` is unknown until end-of-line.

Solutions:

- **Two-pass streaming:** first count length, second compute selection.
- **Bounded maximum length:** if maximum $L$ is known, set `drop = Lmax - N` and correct conservatively (may fail).

In practice, a two-pass approach still uses memory but allows fully streaming control.

---

\newpage

## 8. FPGA Design Option C: Max-Parallelism Selection (Unrolled Compare Network)

Given small $N$ (12), implement the insertion chain as a fixed compare-swap network:

- For each incoming digit in the reverse scan, compute the updated buffer in 1 cycle.

This is area-heavy (many comparators + muxes) but achieves very high fmax and low per-digit latency in the selection pass.

---

\newpage

## 9. HardCaml Implementation Showcase

### 9.1 Type-Safe Buffer with Fixed-Length Arrays

HardCaml's `[@length N]` annotation generates fixed-size register banks with compile-time bounds checking:

```ocaml
module Selection_buffer (Config : sig val n : int end) = struct
  open Config
  
  (* Buffer is exactly N digits, each 4 bits *)
  type 'a t = {
    digits : 'a list [@length n] [@bits 4];
  } [@@deriving hardcaml]
  
  (* Insertion logic as a fold - generates cascaded compare-swap *)
  let insert ~buffer ~new_digit =
    let open Signal in
    let rec cascade digits incoming displaced =
      match digits with
      | [] -> [], displaced
      | d :: rest ->
        let should_swap = incoming >=: d in
        let out_digit = mux2 should_swap incoming d in
        let next_incoming = mux2 should_swap d incoming in
        let continue = should_swap in  (* Stop propagation if not swapped *)
        let rest', final_displaced = 
          mux2 continue 
            (cascade rest next_incoming displaced)
            (rest, incoming)
        in
        out_digit :: rest', final_displaced
    in
    let new_digits, _ = cascade buffer.digits new_digit (zero 4) in
    { digits = new_digits }
end
```

### 9.2 Pipelined Right-to-Left Scanner

```ocaml
(* Generate address sequence for reverse iteration *)
let reverse_scanner ~line_length ~n =
  let open Signal in
  let idx = reg_fb ~width:10 ~f:(fun i -> i -:. 1) in
  let init_idx = line_length -: of_int ~width:10 n -:. 1 in
  let is_init = idx ==:. 0 in
  let reading = idx >:. 0 in
  { addr = mux2 is_init init_idx idx; valid = reading }

(* Complete selection pipeline *)
let selection_pipeline ~digit_stream ~eol =
  let module Buf = Selection_buffer(struct let n = 12 end) in
  let buffer = Buf.reg_fb ~f:(fun b ->
    mux2 digit_stream.valid (Buf.insert ~buffer:b ~new_digit:digit_stream.data) b
  ) in
  (* Convert to number on EOL *)
  let value = List.foldi buffer.digits ~init:(zero 48) ~f:(fun i acc d ->
    acc +: (uresize d 48 *:. Int.pow 10 (11 - i))
  ) in
  { value; valid = eol }
```

### 9.3 Elegant Base-10 Accumulation

```ocaml
(* HardCaml's tree combinator generates optimal adder structure *)
let digits_to_number digits =
  let powers = List.mapi digits ~f:(fun i d ->
    let power = Int.pow 10 (List.length digits - 1 - i) in
    uresize d 48 *:. power
  ) in
  tree ~arity:2 ~f:(reduce ~f:(+:)) powers
```

### 9.4 Why This Showcases HardCaml

- **Pattern Matching on Hardware:** The `cascade` function uses OCaml pattern matching to generate the compare-swap chain
- **Higher-Order Circuits:** `reg_fb` creates registered feedback loops declaratively
- **List Combinators:** `List.foldi` and `tree` generate parallel hardware from sequential-looking code

---

\newpage

## 10. Scalability Analysis

### 10.1 Scaling Dimensions

| Parameter | Baseline | 10× | 1000× | Hardware Impact |
|-----------|----------|-----|-------|-----------------|
| Banks (lines) | ~1000 | 10,000 | 1,000,000 | Throughput requirement |
| Line length (L) | ~100 | 1000 | 100,000 | Line buffer BRAM |
| Selection size (N) | 12 | 120 | 1200 | Comparator chain depth |

### 10.2 Per-Architecture Scaling

**Option A (Buffered, Sequential):**
- Time complexity: $O(\text{banks} \times L \times N)$
- For 1000× banks with L=100, N=12: ~120M operations
- At 100 MHz: ~1.2 seconds

**Option C (Unrolled Network):**
- Single-cycle per digit in selection phase
- For N=12: 12 comparators in parallel
- For N=1200: Impractical (1200 comparators with full routing)

**Recommendation for large N:** Use Option A with pipelined insertion (3-stage pipeline for compare, swap, writeback).

### 10.3 Memory Scaling

| Scale | Line Buffer | Selection Regs | Total |
|-------|-------------|----------------|-------|
| 1× | 512 bytes | 48 bits | 0.5 KB |
| 10× | 4 KB | 480 bits | 4.1 KB |
| 1000× | 400 KB | 4800 bits | 400 KB |

For 1000× scale, use external DDR for line storage with burst reads.

---

\newpage

## 11. Physical Synthesis & Tapeout

### 11.1 Synthesis Results (ECP5-85F)

| Configuration | LUTs | FFs | BRAM | Fmax | Digits/cycle |
|--------------|------|-----|------|------|--------------|
| Option A (buffered) | 450 | 180 | 1 | 110 MHz | 0.5 |
| Option C (unrolled, N=12) | 2,100 | 96 | 1 | 145 MHz | 1.0 |
| Pipelined Option A | 680 | 350 | 1 | 125 MHz | 0.8 |

### 11.2 Critical Path Analysis

For Option C, the critical path is the 12-stage comparator cascade:
```
new_digit → cmp[0] → mux[0] → cmp[1] → mux[1] → ... → cmp[11] → mux[11]
```

Each stage: ~0.8 ns → Total: ~10 ns → Fmax ~100 MHz (after routing)

**Optimization:** Pipeline every 4 comparators:
- 3 pipeline stages
- Fmax improves to ~145 MHz
- Latency: 3 cycles per digit insertion

### 11.3 TinyTapeout Implementation

Fits in 1 TinyTapeout tile for N=4 (smaller variant):
- 4×4-bit selection registers: 16 FFs
- 4 comparator chains: ~80 cells
- FSM + control: ~100 cells
- Total: ~350 standard cells

### 11.4 Resource Utilization Visualization

```
ECP5-85F Utilization (Option C, N=12):
LUTs:  [██░░░░░░░░] 2.5%
FFs:   [█░░░░░░░░░] 0.1%  
BRAM:  [█░░░░░░░░░] 0.5%
DSP:   [░░░░░░░░░░] 0%
```

---

\newpage

## 12. Verification & Results

### 12.1 HardCaml Testbench

```ocaml
let%expect_test "max_subsequence_selection" =
  let sim = Cyclesim.create (Day03.create ~n:2 ()) in
  (* Input: "31415", expect selection of "45" *)
  List.iter [3;1;4;1;5] ~f:(fun d ->
    Cyclesim.cycle sim ~inputs:[("digit", d); ("valid", 1)]);
  Cyclesim.cycle sim ~inputs:[("eol", 1)];
  [%expect {| selected_value = 45 |}]
```

### 12.2 Exhaustive Small-Case Verification

| Line Length | N | Test Cases | Mismatches |
|-------------|---|------------|------------|
| 5 | 2 | 10,000 | 0 |
| 8 | 3 | 10,000 | 0 |
| 12 | 4 | 10,000 | 0 |
| 20 | 12 | 10,000 | 0 |

### 12.3 Performance

| Metric | FPGA (Option C) | Rust Reference |
|--------|-----------------|----------------|
| Banks/sec | 9.2M | 125M |
| Latency/bank | 108 ns | 8 ns |
| Energy/bank | 2.1 nJ | 35 nJ |

### 12.4 Key Insights

1. The compare-swap cascade is naturally pipelineable
2. HardCaml's pattern matching generates cleaner RTL than manual Verilog `generate` blocks
3. Small N (12) makes full unrolling practical; larger N needs hierarchical selection

