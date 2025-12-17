# Day 9 — Movie Theater (Deep Dive Storyboard)

**Sources of truth**
- Technical paper: [papers/day09_movie_theater.md](../papers/day09_movie_theater.md)
- Problem statement: [questions/day9.md](../questions/day9.md)
- Animation target: [animations/day9.py](../animations/day9.py)

**Target length:** 10:00–15:00 (Detailed Technical Breakdown)

**Lecture promise:** We’ll use the "Movie Theater Tiling" puzzle to teach Computational Geometry and Scanline Algorithms. We'll show how to move from a simple (N^2)$ pair check to a sophisticated "Interval Machine" that solves complex containment problems using the Even-Odd Rule.

**Style Note:** Use a Christmas color palette (Red #FF0000, Green #00FF00, Gold #FFD700, Snow White #FFFFFF). Background should be dark winter night blue (#0B0C10). The "Scanline" should be a bright horizontal laser beam.

---

## Scene 1 (0:00–2:00) Introduction: The Tiling Problem

**Visuals**
- **Setting:** A grand movie theater. The floor is a grid.
- **Input:** A list of Red Tile coordinates.
- **Goal:** Find the largest rectangle defined by two Red Tiles as corners.
- **Part 1:** Any two red tiles work.
- **Part 2:** The red tiles form a boundary. The rectangle must be strictly *inside* the polygon defined by this boundary.

**Professor's Lecture (Narration)**
"Welcome to the Movie Theater.
The Elves are re-tiling the floor, and they have a specific aesthetic in mind.
They've given us a list of Red Tiles.
Our job is to find the largest rectangle we can make using two Red Tiles as corners.
For Part 1, it's simple: Pick any two red tiles, draw a box, calculate the area.
But for Part 2, the Red Tiles form a wall.
The rectangle must be valid—it has to fit entirely inside the 'safe zone' enclosed by the tiles."

---

## Scene 2 (2:00–5:00) Part 1: The Parallel Pair Engine

**Visuals**
- **Concept:** Brute Force.
- **Action:**
  - We have $ tiles.
  - We check every pair $.
  - Area = $|x_A - x_B| \times |y_A - y_B|$.
- **Hardware:**
  - A "Systolic Array" or "Parallel Pair Engine".
  - We can check thousands of pairs in parallel.
- **Complexity:** (N^2)$.
- **Animation:** A matrix of processors lighting up as they compute areas.

**Professor's Lecture (Narration)**
"Part 1 is a warmup.
We have a list of points. We want the max area.
Since the number of tiles is manageable, we can just check every single pair.
In hardware, this is trivial.
We can build a 'Pair Engine' that streams points and calculates areas in parallel.
It's (N^2)$, but for a few thousand points, modern silicon eats this for breakfast."

---

## Scene 3 (5:00–8:00) Part 2: The Polygon Problem (Even-Odd Rule)

**Visuals**
- **Problem:** How do we know if a rectangle is 'Inside'?
- **Concept:** Ray Casting / Scanline.
- **Visual:** A laser beam shoots horizontally across the floor.
- **Rule:**
  - Cross a Red Wall -> You are **Inside**.
  - Cross another Red Wall -> You are **Outside**.
- **Animation:**
  - The floor is dark.
  - The laser sweeps.
  - The "Inside" regions light up Green.
  - This creates a set of "Active Intervals".

**Professor's Lecture (Narration)**
"Part 2 is where the real geometry begins.
We need to ensure our rectangle doesn't cross a wall.
To do this, we use the 'Even-Odd Rule'.
Imagine walking across the floor.
When you cross a wall, you enter the room. When you cross the next wall, you leave.
We can formalize this with a 'Scanline Algorithm'.
We sweep a line from top to bottom.
As we hit horizontal edges, we toggle the state of the intervals between them."

---

## Scene 4 (8:00–11:00) The Scanline Interval Machine

**Visuals**
- **Mechanism:** The Scanline moves down, row by row.
- **State:** A list of "Active X-Intervals" (e.g., , ).
- **Events:**
  - We hit a horizontal wall at =20$ spanning =10$ to =50$.
  - We toggle that interval.
- **Hardware:**
  - This isn't just memory. It's an "Interval Machine".
  - It maintains a sorted list of disjoint segments.
  - It supports fast updates (Insert/Delete/Merge).

**Professor's Lecture (Narration)**
"We build a machine that tracks these intervals.
As the scanline moves down, the 'Active Intervals' change.
A horizontal wall appears? We toggle that segment.
If it was off, it turns on. If it was on, it turns off.
This machine gives us a slice of the floor at every Y-coordinate.
It tells us exactly which parts of the current row are valid 'Green' tiles."

---

## Scene 5 (11:00–14:00) Finding the Maximal Rectangle

**Visuals**
- **Challenge:** We have the slices. Now we need the rectangle.
- **Algorithm:**
  - For every pair of Red Tiles on the current scanline...
  - Check if the horizontal segment between them is fully 'On'.
  - Check if the vertical height back to their partners is valid.
- **Optimization:**
  - We don't check every pair.
  - We only check pairs that align with the "Active Intervals".
- **Animation:**
  - As the scanline sweeps, "Ghost Rectangles" extend downwards.
  - When a wall hits, the rectangle is finalized and measured.

**Professor's Lecture (Narration)**
"Now we combine the Pair Engine with the Interval Machine.
As we scan, we look for Red Tiles.
When we find two on the same row, we ask the Interval Machine: 'Is the space between us clear?'
If yes, we have a valid bottom edge.
We then look up to find the matching top edge.
By processing the geometry row-by-row, we convert a complex 2D containment problem into a series of efficient 1D interval checks."

---

## Scene 6 (14:00–15:00) Conclusion

**Visuals**
- **Final State:** The largest valid rectangle glows bright Gold.
- **Action:** The movie screen turns on.
- **Effect:** The theater fills with light.
- **Text:** "Day 9: Solved".

**Professor's Lecture (Narration)**
"We started with a simple pair check, but the constraints forced us to build a Scanline Interval Machine.
This is the heart of Computational Geometry: breaking 2D problems into 1D slices.
The floor is tiled. The safe zones are marked.
And the movie is about to start.
Grab some popcorn.
Class dismissed!"
