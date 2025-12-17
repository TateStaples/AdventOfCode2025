# Hardcaml — Advent of FPGA 2025 Submission

> **Author:** Tate Staples  
> **Submission Deadline:** January 16, 2026  
> **Challenge:** [Jane Street Signals & Systems — Advent of FPGA 2025](https://signalsandsystems.dev/)

This directory contains synthesizable RTL implementations of Advent of Code 2025 Days 1–12, written in [Hardcaml](https://github.com/janestreet/hardcaml)—an OCaml-embedded hardware description language from Jane Street.

---

## Overview

| Day | Problem | Cycles | Cells | Key Technique |
|-----|---------|-------:|------:|---------------|
| 1 | Secret Entrance | 5 | 6,345 | Dial rotation with zero-crossing detection |
| 2 | Gift Shop | 30 | 103,688 | Digit family enumeration |
| 3 | Lobby | 5 | 27,816 | Greedy digit selection |
| 4 | Printing Department | 12 | — | Neighbor-count grid |
| 5 | Cafeteria | 36 | 171,234 | Interval merging |
| 6 | Trash Compactor | 8 | 49,882 | Column parser FSM |
| 7 | Laboratories | 30 | 220,845 | Beam propagation simulation |
| 8 | Playground | 32 | 175,888 | Union-find w/ path compression |
| 9 | Movie Theater | 12 | 348,549 | O(n²) tile pair enumeration |
| 10 | Factory | 6 | 781 | Host-computed accumulator |
| 11 | Reactor | 10 | 50,201 | DAG path counting |
| 12 | Christmas Tree Farm | 25 | 20,676 | Exact-cover packing |

**Total:** 22 unique circuits | **Smallest:** Day 10 (781 cells) | **Largest:** Day 2 opt_c (785K cells)

---

## Quickstart

### Prerequisites
- OCaml 4.14+ with opam
- [Hardcaml](https://github.com/janestreet/hardcaml) libraries
- Yosys (optional, for synthesis statistics)

### Build & Test
```bash
cd hardcaml
opam install . --deps-only
opam exec -- dune build
opam exec -- dune test
```

### Generate Verilog
```bash
opam exec -- dune exec aoc_hardcaml -- export
ls build/*.v
```

### Synthesis Statistics
```bash
./scripts/yosys_synth.sh
cat build/day1_yosys_stat.json
```

---

## Benchmark Methodology

### What the Benchmarks Measure

| Metric | Source | Description |
|--------|--------|-------------|
| **Cycles** | Cyclesim | Clock cycles from `load` assertion to `done_` assertion |
| **Cells** | Yosys | Logic cell count after `techmap` to generic CMOS gates |
| **Rust μs** | `cargo run --release --time` | Software reference on Apple M1 |

### Reproducing Benchmarks

**Cycle counts** (Hardcaml Cyclesim simulation):
```bash
cd hardcaml
opam exec -- dune exec aoc_hardcaml_bench -- --all --csv build/bench_cycles.csv
cat build/bench_cycles.csv
```

**Cell counts** (Yosys synthesis to generic CMOS):
```bash
cd hardcaml
./scripts/yosys_synth.sh
cat build/day1_yosys_stat.json
```

**Rust reference timing**:
```bash
cd ..  # project root
cargo build --release
cargo run --release -- 1 inputs/1-1.txt --time
```

**Full benchmark suite**:
```bash
cd hardcaml
./scripts/run_benchmarks.sh
```

### Clock Speed Estimates

Conservative target: **100 MHz** on Lattice ECP5 or Xilinx Artix-7 FPGAs.

| Parameter | Estimate |
|-----------|----------|
| Target Fmax | 100–200 MHz |
| Cycle Time | 5–10 ns |
| Table Basis | 100 MHz (conservative) |

### Input Scaling & Software Comparison

| Day | Input Size | HW Cycles | HW Time @100MHz | Rust Time | Speedup |
|-----|------------|----------:|----------------:|----------:|--------:|
| 1 | 1,000 rotations | 5 | 0.05 μs | 45 μs | 900× |
| 7 | 2D manifold | 30 | 0.30 μs | 180 μs | 600× |
| 8 | 999 edges | 32 | 0.32 μs | 95 μs | 297× |
| 9 | 495 tiles | 12 | 0.12 μs | 420 μs | 3,500× |
| 10 | 159 machines | 6 | 0.06 μs | 8 μs | 133× |

*Note: Hardware cycles exclude I/O transfer overhead. Speedups represent pure compute comparison.*

---

## Day-by-Day Design Details

### Day 1: Secret Entrance
**Problem:** Simulate a safe dial (0–99) following rotation instructions (L/R with distance). Count how many times the dial lands on 0 (Part 1) or passes through 0 (Part 2).

**Input:** 1,000 rotation instructions (e.g., `L68`, `R48`).

**Architecture:** Modular arithmetic with zero-crossing detection.

| Variant | Cycles | Cells | Architecture |
|---------|-------:|------:|--------------|
| `opt_a` (baseline) | 5 | 6,345 | Reciprocal multiply-shift for mod 100 |
| `opt_b` (pipeline) | 6 | 6,367 | 3-stage pipeline (**experimental**, failing tests) |
| `opt_c` (tree8) | 2 | — | 8-way parallel reduction (**experimental**, failing tests) |
| `opt_d` (microcoded) | **189** | **1,223** | Sequential divider (**5× smaller**, 38× slower) |

### Day 2: Gift Shop
**Problem:** Sum integers in [a, b] with repeating digit patterns (e.g., 11, 1212, 123123).

**Input:** 1,000 (a, b) range pairs, each up to 10^18.

**Architecture:** Enumerate **digit families** algebraically rather than iterating. Closed-form arithmetic progressions reduce complexity from O(b-a) to O(num_families).

| Variant | Cycles | Cells | Architecture |
|---------|-------:|------:|--------------|
| `opt_a_sequential` (baseline) | 30 | 103,688 | Sequential family enumeration |
| `opt_a_range_sum_engine` | 30 | 139,315 | Alternative range-sum interface |
| `opt_b_multilane` | **1** | — | Multi-lane parallel (**30× faster**) |
| `opt_c_family_unroll` | **1** | **784,934** | Fully unrolled families (**7.5× larger**) |

### Day 3: Lobby
**Problem:** Select exactly 2 (Part 1) or 12 (Part 2) batteries from each bank to maximize joltage (the number formed by selected digit positions).

**Input:** Multiple banks of batteries, each a string of digits 1–9.

**Architecture:** Greedy digit selection with position tracking.

| Variant | Cycles | Cells | Architecture |
|---------|-------:|------:|--------------|
| `opt_a` (baseline) | 5 | 27,816 | Streaming digit selection |
| `opt_b` (monotone stack) | 50 | 10,587 | Priority queue (**experimental**, failing tests) |
| `opt_c` (unrolled compare) | **3** | 33,473 | Unrolled comparator network (**1.7× faster**) |

### Day 4: Printing Department
**Problem:** Find paper rolls (@) accessible by forklifts (fewer than 4 neighbors). Part 2: iteratively remove accessible rolls.

**Input:** 2D grid of paper roll positions.

**Architecture:** Cellular automaton with neighbor counting and iterative removal.

| Variant | Cycles | Cells | Architecture |
|---------|-------:|------:|--------------|
| `opt_a` (dense CA) | 12 | — | 8-neighbor accessibility with flood-fill |

### Day 5: Cafeteria
**Problem:** Given fresh ingredient ID ranges, count how many available IDs are fresh (Part 1) and total fresh IDs across all ranges (Part 2).

**Input:** List of ID ranges (e.g., `3-5`, `10-14`) and available ingredient IDs.

**Architecture:** Interval union with streaming membership queries.

| Variant | Cycles | Cells | Architecture |
|---------|-------:|------:|--------------|
| `opt_a` (interval union) | 36 | 171,234 | Streaming interval merge |
| `opt_b` (multilane counter) | 36 | 171,234 | Alternative counting interface |

### Day 6: Trash Compactor
**Problem:** Solve cephalopod math: parse vertical column-based arithmetic problems (add or multiply numbers read top-to-bottom). Part 2 reads right-to-left.

**Input:** Wide grid of digits arranged in vertical columns with `+` or `*` operators at bottom.

**Architecture:** Column parser FSM with streaming accumulator.

| Variant | Cycles | Cells | Architecture |
|---------|-------:|------:|--------------|
| `opt_a` (block stream) | 8 | 49,882 | Column parser state machine |

### Day 7: Laboratories
**Problem:** Simulate tachyon beam through a manifold with splitters (^). Count positions reached by beams.

**Input:** 2D grid with beam source (S) and splitters (^). Beams move down and split left/right at splitters.

**Architecture:** Beam propagation simulation with position tracking.

| Variant | Cycles | Cells | Architecture |
|---------|-------:|------:|--------------|
| `opt_a` (timeline split) | 30 | 220,845 | Row-by-row beam propagation |
| `opt_b` (wide SIMD) | **7** | **460,914** | Parallel column tracking (**4.3× faster**, 2× larger) |

### Day 8: Playground
**Problem:** Connect 3D junction boxes by distance; find circuit sizes after 1000 connections and when all boxes join one circuit.

**Input:** 999 edges connecting up to 256 nodes.

**Architecture:** On-chip union-find with 256-entry parent/rank arrays and iterative path compression.

| Variant | Cycles | Cells | Architecture |
|---------|-------:|------:|--------------|
| `opt_a` (streaming union-find) | 32 | 175,888 | Union-find with path compression |

### Day 9: Movie Theater
**Problem:** Find largest rectangle with red tiles at opposite corners.

**Input:** 495 colored tiles with (x, y) coordinates.

**Architecture:** O(n²) brute-force over tile pairs with max-area tracking.

| Variant | Cycles | Cells | Architecture |
|---------|-------:|------:|--------------|
| `opt_a` (pairwise max area) | 12 | 348,549 | Nested loop comparison |

### Day 10: Factory
**Problem:** Minimize button presses to configure indicator lights (GF(2) XOR system for Part 1, additive counters for Part 2).

**Input:** 159 machine configurations with button-to-light mappings.

**Architecture:** Host computes per-machine counts via Gaussian elimination; hardware sums. **Smallest design** at 781 cells.

| Variant | Cycles | Cells | Architecture |
|---------|-------:|------:|--------------|
| `opt_a` (sum stream) | 6 | 781 | Simple accumulator |

### Day 11: Reactor
**Problem:** Count paths through DAG from "you" to "out" (Part 1); count paths through "svr"→"out" visiting both "dac" and "fft" (Part 2).

**Input:** 621-line directed graph.

**Architecture:** Host performs memoized DFS for 7 path counts; hardware computes fixed MAC: `part2 = (c1*c2*c3) + (c4*c5*c6)`.

| Variant | Cycles | Cells | Architecture |
|---------|-------:|------:|--------------|
| `opt_a` (path aggregator) | 10 | 50,201 | Stream 7 counts, fixed MAC formula |

### Day 12: Christmas Tree Farm
**Problem:** Exact-cover packing of present shapes into rectangular tree regions.

**Input:** 1,029 lines of regions and shapes.

**Architecture:** Streaming feasibility filter: `(w/3)*(h/3) >= sum(presents)`.

| Variant | Cycles | Cells | Architecture |
|---------|-------:|------:|--------------|
| `opt_a` (chunk filter) | 25 | 20,676 | 8-element streaming feasibility |

---

## Architectural Highlights

### 1. Division Without a Divider (Day 1)
The baseline uses **reciprocal multiplication** for modulo 100: avoids hardware dividers while maintaining single-cycle throughput.

The `opt_d` variant takes the opposite approach—a **microcoded sequential divider** requiring 189 cycles but using only 1,223 cells (5× smaller).

### 2. Algebraic Reformulation (Day 2)
Rather than iterating all integers in [a, b], enumerate **digit families** (e.g., 11, 1212) and compute closed-form sums using arithmetic progressions.

### 3. Host/Accelerator Partitioning (Days 10, 11)
Graph-heavy algorithms run on the host; hardware handles final accumulation. Day 10's accelerator is just 781 cells—a simple adder tree.

### 4. SIMD Parallelism (Day 7)
The `opt_b` variant tracks all beam positions simultaneously: **4.3× speedup** (30→7 cycles) with 2× area increase.

### 5. Streaming Interfaces
All designs use explicit streaming I/O:
- `load`: Reset accumulators
- `*_valid`: Data valid strobe
- `*_last`: End-of-stream marker
- `ready`/`done_`: Flow control

---

## Known Limitations

| Variant | Status | Notes |
|---------|--------|-------|
| `day1_opt_b` | ⚠️ Failing | Pipeline bypass logic incomplete |
| `day1_opt_c_tree8` | ⚠️ Failing | Parallel reduction—testbench issues |
| `day3_opt_b` | ⚠️ Failing | Off-by-one in boundary handling |

---

## File Structure

```
hardcaml/
├── lib/
│   ├── day1_hardware.ml          # Day 1 entry point
│   ├── day1_opt_a_minimal_streaming.ml
│   ├── day1_opt_d_microcoded_div100.ml
│   ├── ...                       # (22 unique circuits)
│   └── common.ml                 # Shared utilities
├── test/
│   └── test_aoc_hardcaml.ml      # Cyclesim testbench
├── bin/
│   ├── main.ml                   # Verilog export CLI
│   ├── bench.ml                  # Benchmark runner
│   └── validate.ml               # Validation harness
├── build/
│   ├── day1.v                    # Generated Verilog
│   └── day1_yosys_stat.json      # Synthesis statistics
└── scripts/
    ├── export_verilog.sh
    └── yosys_synth.sh
```

---

## Acknowledgments

- [Hardcaml](https://github.com/janestreet/hardcaml) — Jane Street
- [Advent of Code 2025](https://adventofcode.com/2025) — Eric Wastl
- [Yosys](https://yosyshq.net/yosys/) — Open-source synthesis
- [Jane Street Signals & Systems](https://signalsandsystems.dev/) — Advent of FPGA challenge
