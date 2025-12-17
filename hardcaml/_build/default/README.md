# Advent of FPGA 2025 — Hardcaml Solutions

Synthesizable RTL implementations of Advent of Code 2025 puzzles using [Hardcaml](https://github.com/janestreet/hardcaml), an OCaml-embedded hardware description language.

**For submission details, see [SUBMISSION.md](SUBMISSION.md).**

---

## What's Included

- **Days 1–12:** Complete Hardcaml implementations with multiple architecture variants
- **Testbench:** Cycle-accurate verification against reference solutions
- **Verilog Export:** Synthesizable Verilog output for all designs
- **Synthesis Scripts:** Optional Yosys integration for resource analysis

---

## Quick Start

### Prerequisites

- OCaml 4.14+ with opam
- Hardcaml (via Jane Street's opam repository)

```bash
# Add Jane Street's opam repository (if not already)
opam repo add janestreet https://github.com/janestreet/opam-repository.git

# Install dependencies
cd hardcaml
opam install . --deps-only
```

### Build & Test

```bash
# Build all modules
opam exec -- dune build

# Run testbench (verifies all designs)
opam exec -- dune test

# Export Verilog to build/
./scripts/export_verilog.sh
```

### Export Single Design

```bash
opam exec -- dune exec aoc_hardcaml -- --verilog day7 > build/day7.v
```

### Synthesis Stats (Optional)

Requires [Yosys](https://yosyshq.net/yosys/):

```bash
./scripts/yosys_synth.sh
```

---

## Design Summary

| Day | Puzzle | Cycles | Cells | Key Architecture |
|-----|--------|--------|-------|------------------|
| 1 | Secret Entrance | 5 | 6,345 | Reciprocal multiply for mod 100 |
| 2 | Gift Shop | 1 | 103,688 | Algebraic digit-family enumeration |
| 3 | Lobby | 3 | 33,473 | Unrolled comparator network |
| 4 | Printing Department | 12 | — | Parallel cellular automaton |
| 5 | Cafeteria | 36 | 171,234 | Two-pass interval merge + search |
| 6 | Trash Compactor | 8 | 49,882 | Streaming block accumulator |
| 7 | Laboratories | 7 | 460,914 | 256-wide SIMD timeline update |
| 8 | Playground | 32 | 175,888 | Bounded union-find array |
| 9 | Movie Theater | 12 | 348,549 | O(n²) tile-pair enumeration |
| 10 | Factory | 6 | 781 | Host-computed, hardware sums |
| 11 | Reactor | 10 | 50,201 | Fixed multiply-accumulate |
| 12 | Christmas Tree Farm | 25 | 20,676 | Streaming chunk filter |

---

## Project Structure

```
hardcaml/
├── lib/                    # Hardcaml source
│   ├── dayN_hardware.ml    # Stable entry points
│   └── dayN_opt_*.ml       # Architecture variants
├── test/
│   └── test_aoc_hardcaml.ml  # Cyclesim testbench
├── bin/
│   ├── main.ml             # Verilog export CLI
│   └── bench.ml            # Benchmark runner
├── scripts/
│   ├── export_verilog.sh   # Batch Verilog export
│   ├── yosys_synth.sh      # Synthesis stats
│   └── run_benchmarks.sh   # Full benchmark suite
└── build/                  # Generated outputs
    ├── dayN.v              # Verilog files
    └── dayN_yosys_stat.json  # Synthesis reports
```

---

## Host-Assisted Architecture

Several designs use **host-assisted streaming**: the host pre-processes or reformats inputs into a stream that the RTL consumes deterministically. This keeps the RTL synthesizable and interfaces explicit while demonstrating hardware-oriented architectures.

For example:
- **Day 7:** Host filters input grid to only relevant rows (containing `^`)
- **Day 10/11:** Host computes graph traversals; hardware performs final accumulation

---

## Variants

Most days include multiple architecture variants exploring area/throughput tradeoffs:

- `opt_a`: Minimal-area sequential baseline
- `opt_b`: Pipelined or multi-lane parallelism
- `opt_c`: Maximum unrolling for lowest latency

See [SUBMISSION.md](SUBMISSION.md) for detailed comparisons.
