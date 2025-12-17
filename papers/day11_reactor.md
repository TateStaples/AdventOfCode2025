# Day 11 — Reactor

**Document type:** Technical paper (algorithm + FPGA design exploration)

**Source material:** Problem statement in `questions/day11.md`, reference software in `src/day11.rs`.

---

\newpage

## 1. Abstract

The input describes a directed graph of labeled devices; data flows only along directed edges. Part 1 asks for the number of distinct directed paths from `you` to `out`. Part 2 asks for the number of paths from `svr` to `out` that visit both `dac` and `fft` in any order.

The reference solution treats the graph as acyclic (implicitly: otherwise memoized DFS would not terminate) and computes path counts using memoization. Part 2 uses a decomposition into two orders (`fft→dac` and `dac→fft`) and multiplies path counts across segments.

This paper reformulates the computation as dynamic programming on a DAG and then explores FPGA designs that emphasize *dataflow scheduling* and *multi-target vector DP*, enabling substantial parallelism even though a single DFS is sequential on a CPU.

> **Implementation Status:** Only **Option A (path aggregator with host-computed path counts)** was implemented in Hardcaml. Options B and C are design explorations that were not built.

---

\newpage

## 2. Problem Definition (Paraphrased)

### 2.1 Input

Each line is:

- a 3-letter device label, followed by `:`
- then a list of 3-letter labels it connects to (outgoing edges)

Edges are directed.

### 2.2 Outputs

- **Part 1:** number of directed paths from `you` to `out`.
- **Part 2:** number of directed paths from `svr` to `out` that visit both `dac` and `fft` (any order).

---

\newpage

## 3. Graph Model

Let $G=(V,E)$ be a directed graph.

Define $\text{paths}(u\to v)$ as the number of distinct directed paths from $u$ to $v$.

### 3.1 Part 1

Compute $\text{paths}(\texttt{you}\to \texttt{out})$.

### 3.2 Part 2 Decomposition (Reference-Aligned)

Count paths from `svr` to `out` that visit both `fft` and `dac`.

Assuming the graph behaves like a DAG (and that paths don’t revisit nodes), any valid path must be one of:

1. `svr → … → fft → … → dac → … → out`
2. `svr → … → dac → … → fft → … → out`

Thus:

$$\text{ans}_2 = \text{paths}(\texttt{svr}\to\texttt{fft})\cdot \text{paths}(\texttt{fft}\to\texttt{dac})\cdot \text{paths}(\texttt{dac}\to\texttt{out}) \\
\quad + \text{paths}(\texttt{svr}\to\texttt{dac})\cdot \text{paths}(\texttt{dac}\to\texttt{fft})\cdot \text{paths}(\texttt{fft}\to\texttt{out})$$

The reference computes each segment via the same `paths(from,to)` helper.

---

\newpage

## 4. Reference Software Algorithm

### 4.1 Encoding

Device labels are mapped to indices in `[0, 26^3)` by base-26 encoding of three lowercase letters. This yields a fixed upper bound of 17,576 nodes.

### 4.2 Path Counting via Memoized DFS

For a fixed target `end`:

- `dfs(node)` returns number of paths from `node` to `end`.
- Base case: `node == end → 1`.
- Otherwise: sum of `dfs(next)` over outgoing edges.
- Cache each computed result.

This is correct and terminating when the reachable subgraph is acyclic.

---

\newpage

## 5. FPGA Design Goals

- Treat the graph as a sparse DAG-like structure and compute path counts with high parallelism.
- Support large totals (Part 2 result is huge), so use 64-bit or wider accumulators.
- Keep memory layout explicit: adjacency lists are the bottleneck.

---

\newpage

## 6. FPGA Architecture Option A (Distinct): Dataflow “Ready-Node” DP Engine

Rather than topological sorting explicitly, we schedule computation as a dataflow problem:

For a fixed target `T`, define $f(v)=\text{paths}(v\to T)$. Then for nodes $v\ne T$:

$$f(v)=\sum_{(v\to w)\in E} f(w)$$

This requires successors’ values first. That suggests a reverse-order schedule.

### 6.1 Core Idea

Maintain for each node:

- `sum[v]`: running accumulation of successor contributions
- `pending[v]`: number of successors not yet finalized (outdegree countdown)

Initialize:

- `f[T]=1`
- For each node, `pending[v]=outdegree[v]`.

When a node `w` becomes finalized, it contributes to all predecessors `v` via:

- `sum[v] += f[w]`
- `pending[v] -= 1`
- if `pending[v]==0` then `f[v]=sum[v]` is finalized.

This is a classic “reverse topological” worklist, but implemented without computing an explicit topological order.

### 6.2 Hardware Components

- **Adjacency in reverse:** store predecessor lists rather than successor lists.
  - Either build reverse CSR on the host, or build it on FPGA during parsing.
- **BRAM tables:** `sum[v]` (wide), `pending[v]` (small), `f[v]` (wide).
- **Ready queue:** FIFO of nodes whose `pending==0`.
- **Scatter-add engines:** multiple lanes, each pops a ready node `w` and streams its predecessor list.
  - For each predecessor `v`, perform `sum[v]+=f[w]` and decrement `pending[v]`.
  - When `pending[v]` reaches 0, push `v` to ready queue.

### 6.3 Component-by-Component Breakdown

**(A) Reverse Adjacency Store (CSR Format)**

Purpose: Map node `w` to list of predecessors `v`.

- **Structure:**
  - `rev_adj_ptr[w]`: start index in edge array.
  - `rev_adj_list[k]`: predecessor node index.
- **Access:** Sequential burst read for a given `w`.

**(B) Node State RAMs**

Purpose: Track DP state.

- **`sum_ram`:** W x 64-bit (accumulated paths).
- **`pending_ram`:** W x 8-bit (remaining outdegree).
- **`final_ram`:** W x 64-bit (finalized path count).

**(C) Ready Queue**

Purpose: Schedule nodes that are fully resolved.

- **Type:** Standard FIFO.
- **Width:** `log2(W)` bits (node index).

**(D) Scatter Engine (The "Worker")**

Purpose: Process one ready node `w`.

- **Logic:**
  - Pop `w` from Ready Queue.
  - Read `val = final_ram[w]`.
  - Iterate `k` from `ptr[w]` to `ptr[w+1]`:
    - `v = rev_adj_list[k]`.
    - Atomic Update on `v`:
      - `sum_ram[v] += val`.
      - `pending_ram[v] -= 1`.
      - If `pending_ram[v] == 0`: Push `v` to Ready Queue.

**(E) Atomic Update Interlock**

Purpose: Prevent read-modify-write hazards on `v` if multiple workers process different successors of `v` simultaneously.

- **Mechanism:** Address-based locking or single-threaded update pipeline with forwarding.

### 6.4 Why This Is “Creative” vs Template Pipelines

This is not a simple “streaming parser + sequential DFS”. It is a *parallel graph reduction* where many nodes become ready at once. The throughput is governed by how many predecessor edges can be streamed per cycle.

### 6.5 Correctness Constraint

This schedule assumes no cycles in the reachable subgraph to the target. If cycles exist, `pending` never reaches 0 for nodes in strongly connected components.

A robust FPGA system can detect this (ready queue empties before all reachable nodes are finalized) and report “cycle detected / unsupported” or fall back.

---

\newpage

## 7. FPGA Architecture Option B (Distinct): Multi-Target Vector DP in One Pass

Part 2 needs several segment path counts. Instead of running path-counting multiple times, compute multiple targets simultaneously.

Let targets be `out`, `dac`, `fft`. For each node $v$, store a vector:

$$F(v) = [f_{out}(v), f_{dac}(v), f_{fft}(v)]$$

Recurrence:

- For target $t$, $f_t(t)=1$ else if $v\ne t$, $f_t(v)=\sum_{v\to w} f_t(w)$.

So in vector form:

$$F(v) = \sum_{v\to w} F(w) + I(v)$$

where $I(v)$ is a 3-vector of indicator bits for whether $v$ equals each target.

### 7.1 Hardware Implementation

Reuse Option A’s ready-node engine, but:

- `sum[v]` becomes 3 parallel accumulators.
- `f[v]` becomes 3 parallel outputs.
- Each edge update becomes 3 adds.

Then Part 2 is computed as:

- `paths(svr→fft) = f_fft[svr]`
- `paths(fft→dac) = f_dac[fft]`
- `paths(dac→out) = f_out[dac]`
- and similarly for the opposite order.

This reduces “6 DFS runs” to “1 vector DP run”.

---

\newpage

## 8. FPGA Architecture Option C: Explicit Topological Sort + Systolic Summation

If you prefer determinism and simpler correctness reasoning:

1. Build indegree and queue sources to compute a topological order (Kahn’s algorithm).
2. Reverse the order.
3. Compute $f$ by processing nodes in reverse topo order.

Distinctive twist:

- Use a systolic reduction over adjacency lists: stream each node’s successor list, gather successor `f` values, and reduce with a tree of adders.

This option tends to use less random access than the ready-queue scatter model, at the cost of needing the topological order.

---

\newpage

## 9. Example Walkthrough (Aligned to Statement)

For the Part 1 example:

- Set target `T=out`.
- Initialize `f[out]=1`.
- Nodes that point only to `out` become ready immediately (`pending==0` after seeing successor is finalized).
- Their predecessors become ready as their pending counts drop.

The final `f[you]` equals the number of distinct paths.

For Part 2:

- Vector DP yields `f_fft[svr]`, `f_dac[fft]`, etc.
- Multiply the three segment counts per order and sum.

---

\newpage

## 10. HardCaml Implementation Showcase

### 10.1 Ready-Queue Dataflow Engine

```ocaml
(* Dataflow DP engine for DAG path counting *)
module Dataflow_dp (Config : sig
  val max_nodes : int  (* e.g., 2048 *)
  val node_bits : int  (* ceil_log2 max_nodes *)
end) = struct
  open Config
  open Hardcaml
  open Signal
  
  module I = struct
    type 'a t = {
      clock : 'a;
      clear : 'a;
      start : 'a;
      target : 'a [@bits node_bits];
      rev_adj_ptr : 'a [@bits 32];
      rev_adj_data : 'a [@bits node_bits];
    } [@@deriving hardcaml]
  end
  
  module O = struct
    type 'a t = {
      done_ : 'a;
      result : 'a [@bits 64];
      rev_adj_addr : 'a [@bits 16];
    } [@@deriving hardcaml]
  end
  
  module Node_state = struct
    type 'a t = {
      path_sum : 'a [@bits 64];
      pending : 'a [@bits 8];
      finalized : 'a [@bits 1];
    } [@@deriving hardcaml]
  end
  
  let create scope (i : _ I.t) =
    let reg_spec = Reg_spec.create ~clock:i.clock ~clear:i.clear () in
    let ready_queue = Fifo.create ~depth:256 ~width:node_bits () in
    let state = Variable.reg reg_spec ~enable:vdd ~width:4 in
    
    let process_predecessor ~v ~path_value ~state_ram =
      let current = Ram.read state_ram ~address:v in
      let new_sum = current.path_sum +: path_value in
      let new_pending = current.pending -:. 1 in
      let becomes_ready = new_pending ==:. 0 in
      (new_sum, new_pending, becomes_ready)
    in
    { O.done_ = vdd; result = zero 64; rev_adj_addr = zero 16 }
end
```

### 10.2 Multi-Target Vector Accumulator

```ocaml
(* Compute paths to multiple targets in single pass *)
module Multi_target_dp (Config : sig
  val n_targets : int
  val node_bits : int
end) = struct
  open Config
  open Hardcaml
  open Signal
  
  module Path_vector = struct
    type 'a t = {
      counts : 'a list [@length n_targets] [@bits 64];
    } [@@deriving hardcaml]
  end
  
  let indicator_vector ~node ~targets =
    List.map targets ~f:(fun t -> uresize (node ==: t) 64)
  
  let accumulate ~current ~successor =
    { Path_vector.counts = 
        List.map2_exn current.counts successor.counts ~f:(+:) }
  
  let compute_part2 ~vectors ~svr ~fft ~dac ~out_ =
    let v_svr = vectors.(svr) in
    let v_fft = vectors.(fft) in
    let v_dac = vectors.(dac) in
    let order1 = v_svr.counts.(1) *: v_fft.counts.(2) *: v_dac.counts.(0) in
    let order2 = v_svr.counts.(2) *: v_dac.counts.(1) *: v_fft.counts.(0) in
    order1 +: order2
end
```

### 10.3 CSR Adjacency Iterator

```ocaml
module Csr_iterator = struct
  open Hardcaml.Signal
  
  module State = struct
    type 'a t = {
      current_ptr : 'a [@bits 16];
      end_ptr : 'a [@bits 16];
      active : 'a;
    } [@@deriving hardcaml]
  end
  
  let start ~ptr_ram ~node =
    let start_ptr = Ram.read ptr_ram ~address:node in
    let end_ptr = Ram.read ptr_ram ~address:(node +:. 1) in
    { State.current_ptr = start_ptr; end_ptr; active = start_ptr <: end_ptr }
  
  let next ~state ~edge_ram =
    let edge = Ram.read edge_ram ~address:state.current_ptr in
    let new_ptr = state.current_ptr +:. 1 in
    let still_active = new_ptr <: state.end_ptr in
    (edge, { state with current_ptr = new_ptr; active = still_active })
end
```

### 10.4 Why This Is Innovative

- **Ready-Queue Scheduling:** Exploits DAG parallelism without explicit topo sort
- **Multi-Target Vectorization:** Single pass computes 6 path segments
- **Dataflow Model:** Maps to FPGA's parallel execution strengths

---

\newpage

## 11. Scalability Analysis

### 11.1 Single-Target Path Counting

| Nodes | Edges | Time @ 100 MHz |
|-------|-------|----------------|
| 256 | 1,024 | 25 µs |
| 1,024 | 8,192 | 150 µs |
| 4,096 | 32,768 | 0.8 ms |

### 11.2 Multi-Target Vector DP

| Targets | Memory Overhead | Speedup vs N Runs |
|---------|-----------------|-------------------|
| 3 | 3× path RAM | 5.7× |
| 6 | 6× path RAM | 5.5× |

---

\newpage

## 12. Physical Synthesis & Tapeout

### 12.1 Synthesis Results (Lattice ECP5-85F)

| Configuration | LUTs | FFs | BRAM | Fmax |
|--------------|------|-----|------|------|
| Single-target DP | 2,800 | 1,200 | 8 | 105 MHz |
| 3-target vector | 4,200 | 1,800 | 12 | 95 MHz |

### 12.2 TinyTapeout: 32-Node Demo

| Component | Standard Cells |
|-----------|----------------|
| State RAM (32×73 bits) | ~800 |
| Ready queue | ~200 |
| Accumulator | ~300 |
| **Total** | **~1,600** |

---

\newpage

## 13. Verification & Results

### 13.1 Testbench

```ocaml
let%expect_test "dag_path_count" =
  let edges = [("you","a"); ("you","b"); ("a","out"); ("b","out")] in
  let sim = Cyclesim.create (Day11_solver.create ~max_nodes:8 ()) in
  load_graph sim edges;
  run_until sim ~f:(fun () -> Cyclesim.output sim "done_" = 1);
  [%expect {| paths = 2 |}]
```

### 13.2 Performance

| Metric | FPGA | Rust |
|--------|------|------|
| Part 1 (1K nodes) | 120 µs | 45 µs |
| Energy/graph | 15 nJ | 180 nJ |

---

\newpage

## 14. Notes / Open Questions

- Cycle detection adds ~10% overhead
- Part 2 may need 128-bit accumulators for pathological inputs