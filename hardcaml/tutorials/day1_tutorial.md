# Day 1: Sleigh Circuit Tutorial

This document explains the HardCaml implementation for the Day 1 "Sleigh" problem.

## Overview

The circuit tracks the position of a sleigh on a circular track of length 100. It processes a stream of instructions, each consisting of a direction (Left/Right) and a magnitude.

## Interface

### Inputs
- `clock`, `clear`: Standard control signals.
- `instruction_valid`: Asserted when valid instruction data is present.
- `direction`: 1 bit. `0` for Left, `1` for Right.
- `magnitude`: 16 bits. The distance to move.

### Outputs
- `part1_result`: 32 bits. The count of times the sleigh lands exactly on position 0.
- `part2_result`: 32 bits. The total count of times the sleigh passes position 0 (including landing on it).
- `position`: 10 bits. The current position of the sleigh (0-99).

## Implementation Details

### Fixed-Point Arithmetic
To handle division and modulo operations by 100 efficiently in hardware without a divider, we use fixed-point multiplication.

```ocaml
let div_100 x = 
  (* x is 18 bits. Compute x / 100 using fixed point multiplication. *)
  (* 2^32 / 100 = 42949672.96 -> 42949673 *)
  let inv = of_int ~width:32 42949673 in
  (* ... multiplication and shift ... *)
```

The `mod_100` function uses this division to compute the remainder: `x % 100 = x - (x / 100) * 100`.

### Position Update
The position is stored in a register initialized to 50.
- **Right Move**: `next_pos = (current_pos + magnitude) % 100`
- **Left Move**: `next_pos = (current_pos + 100 - (magnitude % 100)) % 100`

### Part 1 Logic
We simply check if the `next_pos` is 0. If so, we increment the `part1_result` counter.

```ocaml
let is_zero_at_end = next_pos ==:. 0 in
let next_part1_count = part1_count_val +: (mux2 is_zero_at_end (one 32) (zero 32)) in
```

### Part 2 Logic
This is more complex. We need to count how many multiples of 100 are crossed.
- **Right**: The number of zeros passed is `(current_pos + magnitude) / 100`.
- **Left**: We calculate the number of multiples of 100 in the interval `[current_pos - magnitude, current_pos]`. This is done by computing `div_100` for the endpoints (with an offset to handle negative numbers/underflow wrapping).

```ocaml
(* Left: Count multiples of 100 in [P - Mag, P - 1] *)
let term1 = div_100 term1_arg in
let term2 = div_100 term2_arg in
let zeros_left = uresize (term1 -: term2) 16 in
```
