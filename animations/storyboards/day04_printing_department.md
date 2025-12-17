# Day 4 — Printing Department (Deep Dive Storyboard)

**Sources of truth**
- Technical paper: [papers/day04_printing_department.md](../papers/day04_printing_department.md)
- Problem statement: [questions/day4.md](../questions/day4.md)
- Animation target: [animations/day4.py](../animations/day4.py)

**Target length:** 10:00–15:00 (Detailed Technical Breakdown)

**Lecture promise:** We’ll use the "Paper Jam" puzzle to teach Stencil Computations, Memory Bandwidth optimization, and Event-Driven Simulation. We'll show why naive grid processing kills performance and how "Line Buffers" and "Peeling Queues" solve the bottleneck.

**Style Note:** Use a Christmas color palette (Red #FF0000, Green #00FF00, Gold #FFD700, Snow White #FFFFFF). Background should be dark winter night blue (#0B0C10). Use red/green states for jammed/free rolls.

---

## Scene 1 (0:00–2:00) Introduction: The Paper Jam

**Visuals**
- **Setting:** The Printing Department. Massive rolls of paper stacked in a grid.
- **Problem:** We need to clear a path to the Cafeteria.
- **Rule:** A roll is "Accessible" (can be removed) if it has **fewer than 4** neighbors.
- **Grid:**
  - `@` = Paper Roll.
  - `.` = Empty Space.
- **Example:**
  - A roll surrounded by 8 rolls -> **Locked** (Count 8).
  - A roll on the edge with 2 neighbors -> **Accessible** (Count 2).
- **Part 1 Goal:** Count how many rolls are currently accessible.

**Professor's Lecture (Narration)**
"Welcome to the Printing Department.
It's a maze of paper.
The Elves need to clear these rolls to break through the wall.
But safety first! A forklift can only grab a roll if it's not wedged in tight.
The rule is: If a roll has fewer than 4 neighbors, it's loose. We can take it.
If it has 4 or more, it's stuck.
For Part 1, we just need to scan the grid and count the loose rolls.
Sounds easy?
On a 4000x4000 grid, that's 16 million cells.
And for each cell, we check 8 neighbors.
That's over 100 million memory accesses."

---

## Scene 2 (2:00–5:00) The Bottleneck: Memory Bandwidth

**Visuals**
- **Diagram:** CPU connected to DRAM.
- **Animation:**
  - To check Cell $, the CPU reads $ through $.
  - It moves to $. It reads almost the same neighbors again!
  - **Red Flash:** The Memory Bus is glowing red hot.
- **Stats:** "9 Reads per Pixel". "90% Redundant Data".
- **Concept:** The Von Neumann Bottleneck. The CPU is fast, but it's starving for data.

**Professor's Lecture (Narration)**
"Let's look at the hardware.
To update one cell, we need to look at its 8 neighbors.
That's 9 reads from memory.
Then we move one pixel to the right... and we read 6 of those same pixels again!
We are thrashing the memory bus.
We are asking the DRAM for the same data over and over.
This is the 'Von Neumann Bottleneck'.
Our compute units are sitting idle, waiting for pixels.
We need to stop fetching and start buffering."

---

## Scene 3 (5:00–8:00) The Solution: Line Buffers (Stencil)

**Visuals**
- **Diagram:** A "Line Buffer" architecture.
- **Mechanism:**
  - Stream pixels in from DRAM, row by row.
  - Store the last **2 full rows** in fast on-chip memory (BRAM).
  - Create a **3x3 Sliding Window** from these buffered rows.
- **Animation:**
  - As a new pixel enters, the window shifts right.
  - We have all 9 neighbors available instantly in local registers.
- **Result:** We read each pixel from DRAM exactly **once**.
- **Speedup:** 9x reduction in bandwidth.

**Professor's Lecture (Narration)**
"The solution is the 'Line Buffer'.
Instead of random access, we stream the grid row by row.
We store the previous two rows in the FPGA's internal memory.
This gives us a local 3x3 window that slides across the image.
As new data flows in, old data flows out.
We perform the neighbor check using only local, on-chip data.
We read each pixel from main memory exactly once.
This is how your camera processes video in real-time.
It's a 'Stencil Computation'."

---

## Scene 4 (8:00–11:00) Part 2: The Chain Reaction (Peeling)

**Visuals**
- **New Rule:** When a roll is removed, it might free up its neighbors.
- **Animation:**
  - A roll is removed.
  - Its neighbor (who had 4 neighbors) now has 3.
  - That neighbor turns Green (Accessible).
  - It gets removed.
  - *Its* neighbor drops from 4 to 3...
- **Effect:** A wave of removals propagates inward from the edges.
- **Naive Approach:** Rescan the whole grid every time? Too slow!
- **Better Approach:** Event-Driven Simulation.

**Professor's Lecture (Narration)**
"Part 2 is where it gets interesting.
Removing a roll changes the physics of the grid.
A roll that was stuck might suddenly become loose.
This triggers a chain reaction. A 'Peeling' effect.
If we re-scan the whole grid after every removal, we'll be here until New Year's.
We need to be smarter.
We only care about the *neighbors* of the roll we just removed.
Nobody else is affected."

---

## Scene 5 (11:00–14:00) Hardware Architecture: The Event Queue

**Visuals**
- **Diagram:**
  - **Grid Memory:** Stores the "Neighbor Count" for each cell (0-8).
  - **Queue:** A FIFO of "Rolls to Remove".
- **Logic:**
  1.  Pop a roll $ from the Queue.
  2.  Send "Decrement" signals to its 8 neighbors.
  3.  Update the counts in Grid Memory.
  4.  If a neighbor's count drops to **3**, Push it to the Queue.
- **Animation:** The queue fills and empties rapidly. The grid counts update in parallel.
- **Efficiency:** We only touch the cells that matter. (1)$ per removal.

**Professor's Lecture (Narration)**
"We build an 'Event Queue'.
We start with a list of all initially loose rolls.
When we process a roll, we don't scan the grid.
We just look at its 8 neighbors and decrement their counts.
If a neighbor drops from 4 to 3, it just became accessible!
We throw it into the queue.
This is a 'Topological Sort' or 'Peeling' algorithm.
It's incredibly efficient because we never look at a stable cell twice.
We follow the wave of destruction."

---

## Scene 6 (14:00–15:00) Conclusion

**Visuals**
- **Final State:** The grid is cleared (or stabilized).
- **Action:** The forklifts break through the back wall.
- **Reveal:** The Cafeteria! Tables full of food.
- **Text:** "Day 4: Solved".

**Professor's Lecture (Narration)**
"By switching from a naive scan to an event-driven queue, we turned an exponential problem into a linear one.
The wall is down.
The Cafeteria is open.
And I believe I smell... pizza?
Excellent work, class.
Grab a slice. You've earned it.
Class dismissed!"
