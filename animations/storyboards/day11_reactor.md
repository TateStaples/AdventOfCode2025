# Day 11 — Reactor (Deep Dive Storyboard)

**Sources of truth**
- Technical paper: [papers/day11_reactor.md](../papers/day11_reactor.md)
- Problem statement: [questions/day11.md](../questions/day11.md)
- Animation target: [animations/day11.py](../animations/day11.py)

**Target length:** 50:00 (Graduate Level Lecture)

**Lecture promise:** We’ll use the "Reactor Network" puzzle to design a Graph Processing Unit (GPU - but not that kind). We will show why simulating packets fails on DAGs and invent a "Vector Dynamic Programming Engine" that solves constrained path counting in a single topological sweep.

**Style Note:** Use a Christmas color palette (Red #FF0000, Green #00FF00, Gold #FFD700, Snow White #FFFFFF). Background should be dark winter night blue (#0B0C10).

---

## Scene 1 (0:00–10:00) Introduction: The Exponential Trap

**Visuals**
- **Setting:** A toroidal reactor core.
- **Input:** A network of devices (DAG).
- **Goal:** Count paths from  to .
- **Visual:** A "Diamond" graph.
  - 1 path splits to 2. Those 2 split to 4.
  - Rejoining doesn't reduce the count; it adds them.
- **Animation:** A counter spinning wildly. ^{50}$ is a big number.

**Professor's Lecture (Narration)**
"Welcome to Day 11.
We need to count paths in a Directed Acyclic Graph.
The naive engineer says: 'Let's simulate a packet!'
They write a Depth First Search.
And they wait. And wait.
Because in a dense graph, the number of paths grows exponentially.
If you have 100 nodes, you might have more paths than atoms in the universe.
We cannot simulate the paths. We must count them analytically.
We need Dynamic Programming."

---

## Scene 2 (10:00–20:00) The Topological Wavefront

**Visuals**
- **Concept:** Topological Sort.
- **Hardware:** The "Wavefront Processor".
- **Logic:**
  - We can only process a node when *all* its inputs are ready.
  - We start at  (or , depending on direction).
  - We propagate counts.
- **Animation:**
  - A "Wave" of activation moves across the graph.
  - Nodes light up, calculate their sum, and pass it on.
  - We visit each node exactly once.

**Professor's Lecture (Narration)**
"To solve this in hardware, we use a 'Wavefront' approach.
Imagine the graph is a physical circuit.
We can't calculate the output of a gate until all its inputs are stable.
So we process the nodes in 'Topological Order'.
We start at the source. We send a '1' down the wires.
At every junction, we sum the incoming numbers.
This turns an exponential time problem into a linear time problem.
But Part 2 throws a wrench in the gears."

---

## Scene 3 (20:00–30:00) Part 2: The Vector DP Engine

**Visuals**
- **Constraint:** We must visit  and .
- **Problem:** The Wavefront doesn't know history. It just sums numbers.
- **Solution:** Vectorize the state.
- **State Vector:** Instead of a single integer , we pass a vector of 4 integers:
  1.  (Visited neither)
  2.  (Visited only DAC)
  3.  (Visited only FFT)
  4.  (Visited both)
- **Logic:**
  - Normal Node: Pass vector through.
  -  Node: Shift  to ,  to .
  -  Node: Shift  to ,  to .

**Professor's Lecture (Narration)**
"For Part 2, we need to track history.
'Did this path see the DAC? Did it see the FFT?'
We can't store the whole path. That's too much memory.
But we can track the *state* of the path.
We expand our single counter into a Vector of 4 counters.
One for 'Seen Nothing'. One for 'Seen DAC'. One for 'Seen FFT'. One for 'Seen Both'.
Now, our Wavefront carries this vector.
When we hit the  node, we perform a 'Shuffle' operation.
Paths that had seen nothing now count as 'Seen DAC'.
Paths that had seen FFT now count as 'Seen Both'.
We are solving 4 DP problems in parallel."

---

## Scene 4 (30:00–40:00) The Architecture: SIMD Graph Processor

**Visuals**
- **Diagram:** The Processing Unit.
- **Input:** Adjacency List (stored in DRAM).
- **Cache:** On-chip SRAM for active node states.
- **ALU:** A 4-wide SIMD Adder.
- **Dataflow:**
  - Fetch Node A.
  - Fetch Parents B, C.
  - .
  - If A is special (DAC/FFT), apply Permutation.
  - Store Vector_A.

**Professor's Lecture (Narration)**
"We build a SIMD Graph Processor.
SIMD: Single Instruction, Multiple Data.
Our instruction is 'Sum Parents'.
Our data is the 4-element state vector.
We stream the nodes from memory in topological order.
Our ALU adds the vectors in a single clock cycle.
If we hit a special node, we trigger a 'Permute' instruction to update the state.
This architecture is incredibly efficient. It solves the constrained path problem with almost zero overhead compared to the simple path problem."

---

## Scene 5 (40:00–48:00) Dataflow Walkthrough & Tradeoffs

**Visuals**
- **Example:**
  - Node  feeds into .
  -  has vector . (10 clean paths, 5 via FFT).
- **Action:** Enter .
- **Logic:**
  -  (10) becomes .
  -  (5) becomes .
- **Result:**  output vector is .
- **Tradeoff:**
  - **Memory:** We need 4x the memory bandwidth.
  - **Speed:** We solve it in one pass.
  - **Alternative:** Run the solver 3 times (Decomposition).
  - **Verdict:** Vector DP is faster if the vector is small.

**Professor's Lecture (Narration)**
"Let's trace the data.
We have 10 paths arriving at the DAC that haven't seen anything.
And 5 paths that have already seen the FFT.
As they pass through the DAC, their status changes.
The 10 'Clean' paths become 'DAC-only'.
The 5 'FFT' paths become 'Both'.
The hardware handles this state transition automatically.
The tradeoff? Memory bandwidth. We are moving 4 times as much data.
But in exchange, we solve the complex constraint in a single pass, without needing to decompose the graph or run multiple searches."

---

## Scene 6 (48:00–50:00) Conclusion

**Visuals**
- **Final State:** The reactor glows. The "Both" counter at the output is highlighted.
- **Text:** "Day 11: Solved".

**Professor's Lecture (Narration)**
"We started with an exponential nightmare.
We tamed it with Dynamic Programming.
And when the constraints got complex, we didn't panic.
We vectorized our state.
We built a machine that tracks the history of millions of paths simultaneously, simply by adding four numbers at a time.
The reactor is online.
Class dismissed."
