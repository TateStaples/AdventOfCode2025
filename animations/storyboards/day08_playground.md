# Day 8 — Playground (Deep Dive Storyboard)

**Sources of truth**
- Technical paper: [papers/day08_playground.md](../papers/day08_playground.md)
- Problem statement: [questions/day8.md](../questions/day8.md)
- Animation target: [animations/day8.py](../animations/day8.py)

**Target length:** 50:00 (Graduate Level Lecture)

**Lecture promise:** We’ll use the "Playground Wiring" puzzle to design a high-throughput Graph Processor. We will move beyond software algorithms (Kruskal's) to invent a hardware architecture that handles the (N^2)$ edge explosion using "Bucketing" and a custom Union-Find accelerator.

**Style Note:** Use a Christmas color palette (Red #FF0000, Green #00FF00, Gold #FFD700, Snow White #FFFFFF). Background should be dark winter night blue (#0B0C10).

---

## Scene 1 (0:00–10:00) Introduction: The Connectivity Crisis

**Visuals**
- **Setting:** A vast 3D void filled with floating junction boxes (nodes).
- **Input:** A stream of $ coordinates.
- **The Task:** Connect the closest pairs first (Greedy/Kruskal's).
- **The Scale:**
  - 10 nodes $\to$ 45 edges.
  - 1,000 nodes $\to$ ~500,000 edges.
  - 10,000 nodes $\to$ ~50,000,000 edges.
- **Animation:** Show the "Edge Explosion". As nodes appear, the potential connections form a blindingly dense web.

**Professor's Lecture (Narration)**
"Welcome to Day 8.
The Elves need to wire up the playground.
The rule is simple: Connect the closest boxes first.
In Computer Science, this is the Minimum Spanning Tree problem.
Standard solution? Kruskal's Algorithm.
1. Calculate all edge weights.
2. Sort them.
3. Add them if they don't form a cycle.
But look at the scale. For $ nodes, we have ^2$ edges.
If =10,000$, we have 50 million edges.
Sorting 50 million items is slow.
Doing it every frame for an animation is impossible.
We need a hardware architecture that can find the 'needle in the haystack'—the shortest edges—without sorting the entire haystack."

---

## Scene 2 (10:00–20:00) The Naive Hardware: The All-Pairs Sorter

**Visuals**
- **Diagram:** A "Brute Force" Architecture.
- **Component 1:** The Distance Matrix Engine.
  - $ processors. Each computes distance to all other -1$ nodes.
- **Component 2:** The Mega-Sorter.
  - A massive Bitonic Merge Sort network.
- **Dataflow:**
  - Edges pour out of the Distance Engine.
  - They clog the Sorter.
  - **Latency:** The first valid edge doesn't appear until the *entire* list is sorted.
- **Critique:** "This is the software approach baked into silicon. It's terrible. We are sorting edges we will never use (the long ones)."

**Professor's Lecture (Narration)**
"Let's try the naive approach first.
We build a massive parallel engine to compute every distance.
Then we feed it into a giant sorting network.
Why does this fail?
Latency.
We can't process the first edge until the sort is finished.
And Bandwidth.
We are moving 50 million edges through our chip, burning power, just to discard 99% of them because they connect nodes that are already connected.
We need to be lazier. We need to process edges 'Just-In-Time'."

---

## Scene 3 (20:00–30:00) Deriving the Solution: The Bucket Router

**Visuals**
- **Insight:** We only care about short edges first.
- **Concept:** "Approximate Sorting" via Bucketing.
- **Hardware:** The "Bucket Router".
  - **Input:** A stream of edges $.
  - **Logic:** Look at the top bits of the distance $.
  - **Routing:**
    - If  < 100$, route to **SRAM Bank 0**.
    - If  \le d < 200$, route to **SRAM Bank 1**.
    - ...
- **Animation:**
  - Edges fly out of the distance engine.
  - A switch network (Crossbar) flicks them into different bins.
  - Bank 0 fills up. Bank 10 (long edges) is ignored for now.

**Professor's Lecture (Narration)**
"We don't need a perfect sort. We just need a 'good enough' order.
We can use the magnitude of the distance to categorize edges.
This is called Bucketing, or Radix Sorting.
In hardware, this is a Router.
We look at the Most Significant Bits of the distance.
Short edges go to Bank 0. Medium to Bank 1. Long to Bank 2.
Now, we only need to sort Bank 0.
We have reduced the problem from sorting 50 million items to sorting a few thousand.
This is a massive win for latency."

---

## Scene 4 (30:00–40:00) The Architecture: Pipelined Union-Find

**Visuals**
- **Diagram:** The Full Pipeline.
  - **Stage 1:** Pair Generator (Streaming $).
  - **Stage 2:** Distance Calculator (^2$).
  - **Stage 3:** Bucket Router (Writes to DRAM/SRAM).
  - **Stage 4:** Local Sorter (Reads Bank 0, sorts it).
  - **Stage 5:** The Union-Find Unit (DSU).
- **Deep Dive: The DSU Unit.**
  - **Memory:** A "Parent Array" stored in fast BRAM.
  - **Logic:** Two read ports (Find A, Find B). One write port (Union).
  - **Hazard:** Read-After-Write. If we update Parent[A], and the next edge uses A, we must forward the data.
- **Animation:**
  - Show the pipeline flowing.
  - Show a "Stall" when Bank 0 is empty, and the Sorter switches to Bank 1.

**Professor's Lecture (Narration)**
"Now we have a stream of short edges.
We feed them into the Union-Find Unit.
This unit is the brain. It decides if an edge is useful.
It reads the 'Parent' of node U and node V.
If they are different, it writes a new Parent.
This is a sequential dependency. We can't process edge 2 until edge 1 is done, because edge 1 might change the connectivity.
However, because our DSU operations are fast (inverse Ackermann function), this unit can keep up with the sorter.
We have balanced the pipeline: The massive parallel work happens in generation, and the sequential decision-making happens on a reduced dataset."

---

## Scene 5 (40:00–48:00) Dataflow Walkthrough & Tradeoffs

**Visuals**
- **Example:** 3 Nodes. A(0,0,0), B(1,0,0), C(10,0,0).
- **Step 1:** Pair Gen produces (A,B), (A,C), (B,C).
- **Step 2:** Dist Calc.
  - (A,B) = 1$.
  - (A,C) = 100$.
  - (B,C) = 81$.
- **Step 3:** Router.
  - =1 \to$ Bank 0.
  - =81 \to$ Bank 0.
  - =100 \to$ Bank 1.
- **Step 4:** Sorter (Bank 0).
  - Output: $, then $.
- **Step 5:** DSU.
  - Process $: Union(A,B). Count = 1.
  - Process $: Union(B,C). Count = 2.
  - Stop. (We connected all nodes).
- **Tradeoff Discussion:**
  - **Area:** We spent area on the Router and Memory Banks.
  - **Benefit:** We saved massive area by removing the giant Sorter.
  - **Bottleneck:** Memory Bandwidth (writing all those edges to buckets).

**Professor's Lecture (Narration)**
"Let's trace the data.
A and B are close. Their edge goes to Bank 0.
A and C are far. Their edge goes to Bank 1.
Our Sorter picks up Bank 0 first.
It sees A-B and B-C.
The DSU connects A and B. Then it connects B and C.
At this point, A, B, and C are all connected.
We stop.
We never even touched Bank 1.
We never sorted the A-C edge.
We saved time, power, and memory bandwidth.
This is the power of hardware-algorithm co-design."

---

## Scene 6 (48:00–50:00) Conclusion

**Visuals**
- **Final State:** The playground is lit up with a minimal web of golden wires.
- **Text:** "Day 8: Solved".

**Professor's Lecture (Narration)**
"We started with an (N^2)$ nightmare.
By understanding the data—that short edges matter most—we built a Bucketing architecture.
We replaced a brute-force sort with a smart routing network.
We pipelined the heavy math and serialized the logic.
The result is a processor that solves the Minimum Spanning Tree in real-time.
Class dismissed."
