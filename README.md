# Advent of Code 2025

Solutions for [Advent of Code 2025](https://adventofcode.com/2025) with dual implementations:

| Implementation | Purpose | Location |
|----------------|---------|----------|
| **Rust** | Reference solutions for correctness and timing baselines | [`src/`](src/) |
| **Hardcaml** | Synthesizable RTL for [Jane Street's Advent of FPGA 2025](https://signalsandsystems.dev/) | [`hardcaml/`](hardcaml/) |

## Project Structure

```
├── src/              # Rust solutions (day1.rs - day12.rs)
├── hardcaml/         # Hardcaml RTL implementations (22 unique circuits)
│   ├── lib/          # Hardware modules
│   ├── build/        # Generated Verilog & synthesis reports
│   └── README.md     # Detailed FPGA submission documentation
├── inputs/           # Puzzle inputs
├── questions/        # Problem descriptions
├── papers/           # Design analysis documents
└── animations/       # Manim visualizations
```

## Quickstart

### Rust Reference Solutions
> Rust solutions after day 6 come from [Advent of Code 2025 in Rust](https://github.com/maneatingape/advent-of-code-rust/tree/main/src/year2025) by [maneatingape](https://github.com/maneatingape). I had finals week and couldn't finish them myself!

```bash
cargo build --release
cargo run --release -- 1 inputs/1-1.txt   # Run day N with input
cargo run --release -- 1 inputs/1-1.txt --time  # Include timing
```

### Hardcaml FPGA Implementations
```bash
cd hardcaml
opam install . --deps-only     # Install OCaml dependencies
opam exec -- dune build        # Build all designs
opam exec -- dune test         # Run verification tests
opam exec -- dune exec aoc_hardcaml -- export  # Generate Verilog
```

## Implementation Status

| Day | Problem | Rust | Hardcaml | Unique Variants |
|-----|---------|------|----------|-----------------|
| 1 | Secret Entrance | ✅ | ✅ | 4 (reciprocal, pipeline, tree8, microcoded) |
| 2 | Gift Shop | ✅ | ✅ | 4 (sequential, range-sum, multilane, unrolled) |
| 3 | Lobby | ✅ | ✅ | 3 (streaming, monotone stack, unrolled compare) |
| 4 | Printing Department | ✅ | ✅ | 1 (dense CA) |
| 5 | Cafeteria | ✅ | ✅ | 2 (interval union, multilane counter) |
| 6 | Trash Compactor | ✅ | ✅ | 1 (block stream FSM) |
| 7 | Laboratories | ✅ | ✅ | 2 (timeline split, wide SIMD) |
| 8 | Playground | ✅ | ✅ | 1 (streaming union-find) |
| 9 | Movie Theater | ✅ | ✅ | 1 (pairwise max area) |
| 10 | Factory | ✅ | ✅ | 1 (host-computed accumulator) |
| 11 | Reactor | ✅ | ✅ | 1 (path aggregator MAC) |
| 12 | Christmas Tree Farm | ✅ | ✅ | 1 (chunk filter) |

**Total: 22 unique circuits** across 12 days.

## FPGA Submission
> The challenge mentioned the importance of originality, so for disclosure I did use extensive Copilot for documentation and code generations. This was mostly because I started this project on Monday on a whim and was curious how far agentic AI had progressed. I hadn't built anything substantial through LLMs before so I was curious how well it would work for a project that was very self-contained and testable. 

For Jane Street's Advent of FPGA 2025 submission details, including:
- Benchmark methodology & timing estimates
- Architecture deep-dives for each day
- Synthesis results (cell counts via Yosys)
- Generated Verilog artifacts

See **[hardcaml/README.md](hardcaml/README.md)** for the complete submission documentation.

## Visualizations

The `animations/` directory contains [Manim](https://www.manim.community/) visualizations for each day's problem:

```bash
cd animations
pip install -r requirements.txt
manim -pql day1.py  # Render day 1 animation
```

## License

See [LICENSE](LICENSE).
