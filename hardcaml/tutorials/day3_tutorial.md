# Day 3: Lobby Circuit Tutorial

This document explains the HardCaml implementation for the Day 3 "Lobby" problem.

## Overview

The circuit implements a greedy algorithm to find the largest possible number formed by selecting `k` digits from a given sequence, while maintaining their relative order.

## Interface

### Inputs
- `clock`, `clear`: Standard control signals.
- `start`: Pulse to start the computation.
- `data`: 512 bits. The input sequence of digits (up to 128 nibbles).
- `length`: 8 bits. The actual length of the input sequence.
- `k`: 4 bits. The number of digits to select.

### Outputs
- `result`: 64 bits. The constructed number (up to 16 hex digits).
- `done_`: Asserted when the computation is finished.

## Implementation Details

### State Machine
The control logic is a Finite State Machine (FSM) with the following states:
1. **Idle**: Waits for the `start` signal.
2. **Init_scan**: Prepares to scan for the next digit. Sets the search window.
3. **Scan**: Iterates through the valid window of the input data to find the maximum digit.
4. **Update**: Appends the found maximum digit to the result and updates the starting position for the next search.
5. **Finished**: Signals completion.

### Greedy Algorithm in Hardware
The algorithm works by repeatedly finding the largest digit in the "allowed" range.
- If we need to pick `k` more digits, and there are `R` digits remaining in the input starting from `current_idx`, we must pick the next digit from the range `[current_idx, length - k]`. This ensures we leave enough digits (`k-1`) to complete the selection.

#### Scan State
In the `Scan` state, the circuit iterates an index `scan_idx`.
- It reads the nibble at `scan_idx` using a large multiplexer: `current_scan_val = mux scan_idx data_chunks`.
- It compares `current_scan_val` with the current `max_val`.
- If `current_scan_val > max_val`, it updates `max_val` and records the position `max_idx`.

#### Update State
Once the scan covers the valid window:
- The `max_val` is shifted into the `result` register.
- The `current_idx` is advanced to `max_idx + 1` (we can't pick digits before the one we just picked).
- `digits_remaining` (k) is decremented.
- If `digits_remaining` is 0, we go to `Finished`; otherwise, back to `Init_scan`.

### Data Path
- **Data Storage**: The 512-bit input is treated as an array of 128 4-bit values.
- **Result Accumulation**: The result is built by shifting: `next_result = (result << 4) | max_val`.

```ocaml
(* Example of Mux Logic for State Transitions *)
let next_state = 
  mux state [
    idle_next_state;
    init_next_state;
    scan_next_state;
    update_next_state;
    finished_next_state
  ]
```
