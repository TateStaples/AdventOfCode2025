# Day 4: Printing Department Circuit Tutorial

This document explains the HardCaml implementation for the Day 4 "Printing Department" problem.

## Overview

The circuit simulates a process of optimizing paper roll storage. It represents the storage area as a grid where paper rolls (`@`) can be accessed (removed) if they have fewer than 4 neighbors. The process repeats until no more rolls can be accessed.

## Interface

### Inputs
- `clock`, `clear`: Standard control signals.
- `start`: Pulse to load the initial grid and start the simulation.
- `grid_in`: A large bit vector representing the initial state of the grid (1 for paper roll, 0 for empty). The size is `rows * cols`.

### Outputs
- `part1_result`: 64 bits. The number of rolls accessible in the very first step.
- `part2_result`: 64 bits. The total number of rolls accessible over the entire process until stabilization.
- `done_`: Asserted when the grid stabilizes (no more rolls can be removed).

## Implementation Details

### Grid Representation
The grid is flattened into a single bit vector.
- `rows = 139`, `cols = 139` (fixed size based on input).
- `grid_size = 19321` bits.

### Cellular Automaton Logic
The core logic operates like a cellular automaton, updating the entire grid in parallel in each clock cycle.

For every cell `(r, c)`:
1. **Neighbor Count**: It sums the values of the 8 surrounding cells (Moore neighborhood).
   ```ocaml
   let neighbors = [ ... ] |> reduce ~f:(+: )
   ```
2. **Removability Condition**: A roll is removable if it exists (`current == 1`) AND has fewer than 4 neighbors.
   ```ocaml
   let is_removable = current &: (neighbors <: 4)
   ```
3. **Next State**: The cell remains if it is NOT removable.
   ```ocaml
   next_grid_bits.(idx) <== (current &: ~:is_removable)
   ```

### Accumulation and Control
- **Population Count**: The circuit calculates the total number of removable cells in the current cycle using `popcount`.
- **Accumulator**: Adds the `removable_count` to the total `part2_result` every cycle.
- **Part 1 Logic**: A `first_cycle` register detects the first step of the simulation and captures the `removable_count` into `part1_result`.
- **Termination**: The simulation stops (`active` goes low) when `removable_count` is 0.

### Parallelism
This design exploits the massive parallelism of hardware. All 19,000+ cells are evaluated simultaneously, and the population count is computed in a tree-like structure, allowing for very fast simulation of each step.
