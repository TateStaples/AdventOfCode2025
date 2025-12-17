# Day 7 — Laboratories (Deep Dive Storyboard)

**Sources of truth**
- Technical paper: [papers/day07_laboratories.md](../papers/day07_laboratories.md)
- Problem statement: [questions/day7.md](../questions/day7.md)
- Animation target: [animations/day7.py](../animations/day7.py)

**Target length:** 10:00–15:00 (Detailed Technical Breakdown)

**Lecture promise:** We’ll use the "Tachyon Beam" puzzle to teach Dynamic Programming and Parallel Simulation. We'll show why simulating individual particles leads to an exponential explosion, and how to solve it by tracking the *distribution* of particles instead.

**Style Note:** Use a Christmas color palette (Red #FF0000, Green #00FF00, Gold #FFD700, Snow White #FFFFFF). Background should be dark winter night blue (#0B0C10). Accent the teleporter pad in festive gold.

---

## Scene 1 (0:00–2:00) Introduction: The Tachyon Manifold

**Visuals**
- **Setting:** A high-tech lab. A glowing "Tachyon Manifold" diagram.
- **Input:** A grid with a start point `S` at the top and splitters `^` scattered below.
- **Physics:**
  - A beam falls down.
  - If it hits empty space `.`, it keeps falling.
  - If it hits a splitter `^`, it stops and spawns two new beams: one Left, one Right.
- **Goal:** Count the split events (Part 1) and the total paths (Part 2).

**Professor's Lecture (Narration)**
"Welcome to the Laboratories.
We're fixing a teleporter, and to do that, we need to calibrate the Tachyon Manifold.
The physics are simple: A beam falls down.
If it hits a splitter, it splits into two.
One goes left, one goes right.
It looks like a Galton Board or a Pachinko machine.
Our job is to predict the behavior of this beam as it cascades down the machine."

---

## Scene 2 (2:00–5:00) The Naive Approach: Exponential Explosion

**Visuals**
- **Simulation:**
  - 1 beam falls. Hits a splitter -> 2 beams.
  - They hit splitters -> 4 beams.
  - Then 8, 16, 32...
- **Graph:** Show the number of particles vs Depth. It's ^N$.
- **Visual:** The screen fills with particles. The simulation slows to a crawl.
- **Text:** "Simulation Failed: Out of Memory".

**Professor's Lecture (Narration)**
"Your first instinct might be to simulate the particles.
Create a 'Beam' object. Move it. If it splits, create two new objects.
This works for the first few rows.
But look at the growth. It's exponential.
By row 50, you could have quadrillions of beams.
Your computer doesn't have enough RAM to store them all.
We need a better way. We need to stop tracking *particles* and start tracking *probabilities*."

---

## Scene 3 (5:00–8:00) The Solution: Dynamic Programming (Histogram)

**Visuals**
- **Concept:** Instead of dots, show a **Histogram** (Bar Chart) for each row.
- **Row 0:** `[0, 0, 1, 0, 0]` (One beam in the center).
- **Row 1:** `[0, 0, 1, 0, 0]` (Falls down).
- **Row 2 (Splitter at center):**
  - The 1 in the center hits the splitter.
  - It adds 1 to the Left neighbor and 1 to the Right neighbor.
  - **Next Row:** `[0, 1, 0, 1, 0]`.
- **Merge Event:**
  - If two beams fall into the same spot, the counts just add up!
  - `[1, 0, 1]` -> Hit 2 Splitters -> `[1, 2, 1]`.
- **Memory:** We only store one row of numbers. Constant space.

**Professor's Lecture (Narration)**
"The solution is Dynamic Programming.
Instead of tracking each individual beam, we track the *count* of beams at each position.
We represent the state of the system as a row of numbers.
'How many beams are at column X?'
When we move to the next row, we calculate the new counts based on the old ones.
If there's a splitter, the count at X flows to X-1 and X+1.
If there's empty space, it just flows down.
We've turned an exponential simulation into a linear update rule."

---

## Scene 4 (8:00–11:00) Part 1 vs Part 2

**Visuals**
- **Part 1:** "Count Split Events".
  - Every time we process a splitter at index $, we add `Count[X]` to a running total.
- **Part 2:** "Total Particles".
  - At the bottom of the grid, we just sum up the entire row.
- **Scale:** The numbers in the histogram might get huge (64-bit integers), but the logic is identical.

**Professor's Lecture (Narration)**
"This DP approach solves both parts of the puzzle simultaneously.
For Part 1, every time we hit a splitter, we add the number of beams hitting it to our 'Split Counter'.
For Part 2, we just let the simulation run to the bottom.
The sum of the final row is the total number of timelines.
The numbers might get huge—trillions or quadrillions—but a 64-bit integer can handle it easily.
We don't need a supercomputer. We just need a loop."

---

## Scene 5 (11:00–14:00) Hardware Architecture: Systolic Array

**Visuals**
- **Diagram:** A row of Processing Elements (PEs).
- **Logic:**
  - **Cell X:** Inputs: `Count(X)`, `Splitter(X)`.
  - **Outputs:** `To_Left`, `To_Right`, `To_Down`.
- **Update:**
  - **Next Row Cell X:** Input: `From_Up(X)` + `From_Right(X+1)` + `From_Left(X-1)`.
- **Animation:** A "Wavefront" of updates moving down the grid.
- **Parallelism:** We update the entire row in a single clock cycle.

**Professor's Lecture (Narration)**
"This algorithm is perfect for hardware.
We can build a 'Systolic Array'.
Each column has a small processing unit.
It looks at the incoming beam count and the local grid character.
It decides where to send the beams for the next clock cycle.
'I have 50 beams. I hit a splitter. Left neighbor, take 50. Right neighbor, take 50.'
All the cells talk to their neighbors simultaneously.
We process the entire row in one tick."

---

## Scene 6 (14:00–15:00) Conclusion

**Visuals**
- **Final State:** The beam distribution is calculated.
- **Action:** The teleporter stabilizes.
- **Effect:** The Professor steps onto the pad and vanishes...
- **Reappear:** ...and reappears instantly. "It works!"
- **Text:** "Day 7: Solved".

**Professor's Lecture (Narration)**
"We tamed the exponential explosion.
By tracking distributions instead of particles, we turned an impossible problem into a trivial one.
The teleporter is calibrated.
And I'm still in one piece. Mostly.
Let's move on to the Playground.
Class dismissed!"
