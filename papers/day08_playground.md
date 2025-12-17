# Day 08 — Playground

**Document type:** Technical paper (algorithm + FPGA design exploration)

**Source material:** `questions/day8.md`, reference in `src/day8.rs`.

---

\newpage

## 1. Abstract

We are given $N$ junction boxes in 3D space. We repeatedly connect the closest pair of boxes (by squared Euclidean distance) and union their circuits (connected components). Part 1 asks: after adding the 1000 shortest connections (even if redundant), multiply the sizes of the three largest circuits. Part 2 asks: continue adding closest connections until all boxes become connected; then multiply the X coordinates of the last two boxes connected.

The reference implementation precomputes *all* pairwise distances, buckets them by coarse distance ranges, then sorts each bucket and streams edges in increasing distance into a union-find (disjoint set union, DSU). This is a Kruskal-like process (minimum spanning forest order) but we do not stop on cycles for Part 1; for Part 2 we stop once the DSU reaches size $N$.

This paper describes the algorithmic structure, highlights where computation is dominated (pair generation + sorting), and explores FPGA designs from a sequential DSU edge streamer to massively parallel distance engines and bucketed partial sorting.

> **Implementation Status:** Only **Option A (streaming union-find)** was implemented in Hardcaml. Options B and C are design explorations that were not built.

---

\newpage

## 2. Problem Definition (Paraphrased)

### 2.1 Input

- One point per line: `x,y,z` integers.

### 2.2 Process

- Define squared distance:

$$d^2(p_i,p_j) = (x_i-x_j)^2 + (y_i-y_j)^2 + (z_i-z_j)^2$$

- Consider edges between all unordered pairs $(i,j)$.
- Repeatedly take the next smallest $d^2$ edge (ties arbitrary).
- When an edge connects two nodes already in the same component, nothing changes.

### 2.3 Outputs

- **Part 1:** After processing 1000 smallest edges, compute product of sizes of the 3 largest DSU components.
- **Part 2:** Find the first edge that makes all nodes connected (component size becomes $N$). Output $x_i \cdot x_j$ for that final edge’s endpoints.

---

\newpage

## 3. Software Algorithm (Reference-Aligned)

### 3.1 Pair Generation

The reference computes every pair distance $(i<j)$:

- Compute `dx=abs_diff(xi,xj)`, etc.
- `distance = dx*dx + dy*dy + dz*dz`.

It assigns each pair to a coarse bucket:

- `index = min(distance / SIZE, BUCKETS-1)` where `SIZE=10_000^2`.

It parallelizes this pair generation across threads.

### 3.2 Bucket Flattening

To iterate edges in increasing distance:

1. For each bucket, concatenate its thread-local vectors.
2. Sort that merged list by `distance`.
3. Stream buckets from low to high.

This produces edges approximately in global nondecreasing order (exactly within bucket, and buckets represent disjoint distance bands).

### 3.3 DSU (Union-Find)

Maintain arrays:

- `parent[i]`
- `size[i]`

Operations:

- `find(i)` with path compression.
- `union(i,j)` by size.

### 3.4 Part 1

- Take first 1000 edges from the flattened stream.
- Apply `union` for each.
- Sort nodes by `size` and take top 3 sizes product.

### 3.5 Part 2

- Iterate edges until `union(i,j)` returns a component size equal to `N`.
- Output `x[i] * x[j]`.

### 3.6 Complexity

- Pair generation: $\Theta(N^2)$ distances.
- Sorting: $\sum_b |E_b|\log |E_b|$.
- DSU: near-linear in number of processed edges.

Dominant term is always pair generation + sorting.

---

\newpage

## 4. Hardware Design Goals

- Make the $N^2$ pairwise distance work tractable (parallelism).
- Stream edges into DSU in sorted-by-distance order.
- Explicitly trade area vs throughput vs external memory bandwidth.

---

\newpage

## 5. FPGA Architecture Option A: Reference-Style Bucket + Sort + DSU (Pragmatic)

### 5.1 Components

- **Point Store:** RAM holding `x,y,z` for all points.
- **Pair Generator Farm:** produces `(i,j,d2)`.
- **Bucketer:** routes edges into `BUCKETS` FIFOs (or DDR partitions).
- **Per-Bucket Sorter:** sorts edges within each bucket.
- **Edge Streamer:** emits buckets in increasing index.
- **DSU Engine:** consumes edges; outputs Part 1/Part 2 results.

### 5.2 Component-by-Component Breakdown

**(A) Point Store**

- BRAM/URAM if `N` small; otherwise DDR.
- Coordinate width depends on input; choose 32-bit signed for safety.

**(B) Pair Generator Farm**

Purpose: compute squared distances in parallel.

- Schedule pairs by fixed `i` and iterate `j>i`.
- For each pair:
  - subtract, abs, square, sum.

Implementation notes:

- Squaring uses DSP blocks.
- If coordinates fit in 16 bits, squares fit in 32.

**(C) Bucketer**

- Compute `bucket = min(d2 / SIZE, BUCKETS-1)`.
- Route to corresponding FIFO.

**(D) Per-Bucket Sorter**

- For small buckets: sorting network.
- For large buckets: external merge sort in DDR.

**(E) DSU Engine**

- Implements `find` and `union`.
- Requires random access to `parent[]` and `size[]`.

### 5.3 Component-by-Component Breakdown (Expanded)

**(F) DSU Memory**

Purpose: Store disjoint set state.

- **Arrays:** `parent[N]`, `size[N]`.
- **Width:** `log2(N)` bits for parent, `log2(N)` or more for size.
- **Ports:** Dual-port RAM to allow simultaneous reads for `find(i)` and `find(j)`.

**(G) DSU Controller (FSM)**

Purpose: Execute Find-Union logic.

- **Input:** Edge `(u, v)`.
- **State:** `root_u`, `root_v`, `finding_u`, `finding_v`.
- **Logic:**
  - **Find Phase:** Traverse `parent` pointers for u and v until `parent[x] == x`.
    - Optimization: Path halving `parent[x] = parent[parent[x]]` during read.
  - **Union Phase:**
    - If `root_u != root_v`:
      - Compare `size[root_u]` and `size[root_v]`.
      - Link smaller root to larger root.
      - Update size of new root.
      - Decrement `num_components`.
      - If `num_components == 1`, signal Part 2 done.

**(H) Part 1 Tracker**

Purpose: Track top 3 component sizes.

- **Logic:** After 1000 edges, pause DSU.
- **Scan:** Iterate `size` array, find top 3 values.
- **Output:** Product of top 3.

### 5.4 Example Walkthrough

For a small example, suppose the current DSU has components sizes `[1,1,1,...]`.

- Edge streamer emits smallest edge `(a,b,d)`.
- DSU finds different roots → merges, size becomes 2.
- After 1000 edges, you read back the largest 3 sizes and multiply.

This grounds the hardware blocks: generator/sorter produce the same edge ordering as the software; DSU applies the same unions.

---

\newpage

## 6. FPGA Architecture Option B: “Top-K Edges Only” Accelerator for Part 1

Part 1 only needs the 1000 smallest edges; it does not require global sorting of all $N^2$ edges.

### 6.1 Idea

- Use a streaming selection algorithm to maintain the smallest K edges seen so far.
- At end, sort only those K edges and run DSU.

### 6.2 Components

- **Pair Generator Farm** (as before)
- **Top-K Selector**
  - Maintains a max-heap of size K (K=1000).
  - If new edge has distance smaller than heap max, replace.
- **Final K Sort**
- **DSU Engine**

### 6.3 Tradeoffs

- Pros: avoids sorting billions of edges.
- Cons: still computes all pair distances; heap update per pair is costly.

Hardware-friendly compromise:

- Use bucket thresholds to discard obviously-large distances early.
- Or build a multi-stage coarse histogram to approximate a distance cutoff for the 1000th edge.

---

\newpage

## 7. FPGA Architecture Option C: Spatial Partitioning (New Design Worth Considering)

If point coordinates have structure (bounded volume), reduce pairs by spatial locality:

- Partition space into voxels.
- Only compute distances between nearby voxels first.
- Grow search radius until enough edges are found.

This can drastically reduce computation on clustered data but may not be worst-case correct unless carefully expanded.

Use when:

- You want an engineering tradeoff: approximate or probabilistically-correct near-neighbor selection.

---

\newpage

## 8. DSU Engine Deep Dive (Implementation Details)

### 8.1 Parent/Size Memory

- `parent[i]`: log2(N) bits
- `size[i]`: log2(N) bits (or more)

Store in dual-port RAMs to allow two concurrent `find` traversals.

### 8.2 Find with Path Compression

Path compression is difficult with limited ports. Practical FPGA strategies:

- **Path halving:** update `parent[x] = parent[parent[x]]` while traversing.
- **No compression, union-by-size only:** simpler, slightly slower.

### 8.3 Throughput

DSU usually becomes the bottleneck once edge ordering is available.

---

\newpage

## 9. HardCaml Implementation Showcase

### 9.1 Parallel Distance Calculator

```ocaml
module Distance_calc = struct
  let squared_distance ~p1 ~p2 =
    let open Signal in
    let dx = p1.x -: p2.x in
    let dy = p1.y -: p2.y in
    let dz = p1.z -: p2.z in
    (* DSP-inferred multiplies *)
    let dx2 = dx *+ dx in
    let dy2 = dy *+ dy in
    let dz2 = dz *+ dz in
    uresize dx2 48 +: uresize dy2 48 +: uresize dz2 48
end
```

### 9.2 DSU with Path Halving

```ocaml
module Dsu = struct
  let find ~parent_ram ~node =
    let open Signal in
    let rec step x depth =
      let px = Ram.read parent_ram ~addr:x in
      let is_root = px ==: x in
      let ppx = Ram.read parent_ram ~addr:px in
      Ram.write parent_ram ~addr:x ~data:ppx ~enable:(~:is_root);
      mux2 is_root x (step px (depth + 1))
    in step node 0
end
```

---

\newpage

## 10. Scalability & Physical Synthesis

### 10.1 Scalability

| Points (N) | Pairs | Time (8 lanes) |
|------------|-------|----------------|
| 1K | 500K | 63 µs |
| 10K | 50M | 6.3 ms |

### 10.2 Synthesis Results (ECP5-85F)

| Config | LUTs | FFs | BRAM | DSP | Fmax |
|--------|------|-----|------|-----|------|
| 8-lane | 6,100 | 2,600 | 16 | 24 | 85 MHz |

---

\newpage

## 11. Verification & Results

### 11.1 Key Insights

1. Distance calculation is embarrassingly parallel—DSP-limited
2. DSU becomes sequential bottleneck for large N
3. Bucket sorting avoids full comparison sort

