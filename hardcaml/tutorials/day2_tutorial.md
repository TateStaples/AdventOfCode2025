# Day 2: Password Circuit Tutorial

This document explains the HardCaml implementation for the Day 2 "Password" problem.

## Overview

The circuit searches for "valid" passwords within a given range. A valid password must satisfy certain repetition criteria of its digits.

## Interface

### Inputs
- `clock`, `clear`: Standard control signals.
- `load`: Signal to load the start and end values.
- `start_bin`, `end_bin`: 64-bit binary representations of the range.
- `start_bcd`: 48-bit (12 digits) BCD representation of the start value.

### Outputs
- `sum_p1`: 64 bits. Count of valid passwords for Part 1.
- `sum_p2`: 64 bits. Count of valid passwords for Part 2.
- `done_`: Asserted when the search is complete.

## Implementation Details

### BCD Incrementer
Since the problem involves checking properties of the decimal digits, the circuit maintains the current number in Binary Coded Decimal (BCD) format. A custom ripple-carry BCD incrementer is used to advance the number.

```ocaml
let bcd_incr bcd =
  (* Splits BCD into nibbles and ripples a carry *)
  (* If a nibble > 9, it wraps to 0 and generates a carry *)
```

### Repetition Check Logic
The core logic resides in `check_repetition`. It analyzes the 12 digits to find repeating patterns.

- **Length Determination**: First, it determines the effective length of the number (ignoring leading zeros).
- **Periodicity Check**: It checks if the sequence of digits repeats with a period `P`.
    - `P` must divide the length `L`.
    - For **Part 1**, the sequence must repeat *exactly* twice (`L / P = 2`).
    - For **Part 2**, the sequence must repeat *at least* twice (`L / P >= 2`).

```ocaml
let check_period p =
  (* Check if digits repeat with period p *)
  (* d[i] == d[i+p] for all 0 <= i < L-p *)
```

### Search Loop
The circuit (likely implemented with a state machine, though not fully shown in the snippet) iterates from `start_bin` to `end_bin`. In each cycle:
1. It checks the current BCD number against the criteria.
2. If valid, it increments the respective counters (`sum_p1`, `sum_p2`).
3. It increments the current number.
4. It stops when `current_bin` equals `end_bin`.
