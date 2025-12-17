# Day 12 — Christmas Tree Farm (Deep Dive Storyboard)

**Sources of truth**
- Technical paper: [papers/day12_christmas_tree_farm.md](../papers/day12_christmas_tree_farm.md)
- Problem statement: [questions/day12.md](../questions/day12.md)
- Animation target: [animations/day12.py](../animations/day12.py)

**Target length:** 45:00–55:00 (full lecture)

**Lecture promise:** We’ll use the "Present Packing" puzzle to teach Combinatorial Optimization and Exact Cover. We'll show why greedy algorithms fail at Tetris-like problems and how to build a solver that finds the perfect fit every time.

**Style Note:** Use a Christmas color palette (Red #FF0000, Green #00FF00, Gold #FFD700, Snow White #FFFFFF). Background should be dark winter night blue (#0B0C10).

---

## Scene 1 (0:00–10:00) Introduction: The Packing Problem

**Visuals**
- A cavern full of Christmas trees.
- **Input:**
  - **Shapes:** Polyominoes (Tetris pieces).
  - **Region:** A 12x5 grid.
  - **Requirement:** Fit 2 of Shape A, 1 of Shape B, 3 of Shape C.
- **Goal:** Pack them all in without overlap.
- Show the pieces floating around the grid.

**Professor's Lecture (Narration)**
"Welcome to the Christmas Tree Farm.
The Elves are panicking. They have piles of presents and limited space under the trees.
This is a classic 'Packing Problem'.
We have a set of weirdly shaped items—polyominoes—and a rectangular container.
We need to fit them all in perfectly. No overlaps. No hanging off the edge.
It sounds like Tetris, but it's harder. In Tetris, you can clear lines. Here, you have to fill the space exactly."

---

## Scene 2 (10:00–20:00) The Naive Approach: Greedy Failure

**Visuals**
- Try to place pieces one by one.
- Place Shape A in the top left.
- Place Shape B next to it.
- Place Shape C... oh no, it doesn't fit!
- We created a "hole" that is too small for any piece.
- **Text:** "Greedy Algorithms Fail".
- We need to backtrack and try again.

**Professor's Lecture (Narration)**
"Your first instinct is to just shove pieces in wherever they fit.
That's a 'Greedy' approach.
But look what happens. We placed the first few pieces, but we left a gap.
Now the last piece doesn't fit.
We painted ourselves into a corner.
To solve this, we need to be willing to undo our mistakes. We need 'Backtracking'."

---

## Scene 3 (20:00–30:00) The Solution: Bitboards and Backtracking

**Visuals**
- Represent the grid as a 64-bit integer (Bitboard).
- 0 = Empty, 1 = Filled.
- Represent each Piece as a bitmask.
- **Check:** `Grid & Piece == 0` (No collision).
- **Place:** `Grid = Grid | Piece`.
- **Remove:** `Grid = Grid ^ Piece`.
- Show the recursive search tree.
- It tries a spot. If it works, it recurses. If it gets stuck, it backtracks.

**Professor's Lecture (Narration)**
"To solve this efficiently, we use 'Bitboards'.
We represent the grid as a single 64-bit integer.
Checking for collisions becomes a single CPU instruction: bitwise AND.
Placing a piece is bitwise OR.
We build a recursive solver.
It tries to place the first piece. Then it calls itself to place the second.
If it hits a dead end, it returns, undoes the move, and tries the next spot.
This is 'Depth First Search' on the state space."

---

## Scene 4 (30:00–40:00) Advanced Technique: Exact Cover (DLX)

**Visuals**
- Introduce the "Exact Cover" matrix.
- **Columns:** Each cell of the grid + Each piece we need to place.
- **Rows:** Every possible placement of every piece.
- **Goal:** Select rows such that every column has exactly one '1'.
- This is the "Dancing Links" algorithm (Algorithm X).
- It's the fastest way to solve Sudoku, Pentominoes, and this puzzle.

**Professor's Lecture (Narration)**
"If we want to get fancy, we can frame this as an 'Exact Cover' problem.
We create a matrix where the columns are the constraints: 'Cell (0,0) must be filled', 'We must place one Shape A'.
The rows are the options: 'Place Shape A at (0,0)'.
We need to pick a set of rows that satisfies every column exactly once.
Donald Knuth's 'Dancing Links' algorithm is the gold standard for this.
It's elegant, fast, and perfect for this kind of combinatorial puzzle."

---

## Scene 5 (40:00–50:00) Hardware Architecture: Solver Array

**Visuals**
- **Block Diagram:**
  - **Problem Loader:** Loads the shapes and counts.
  - **Solver Core:** A hardware backtracking engine.
  - **Stack:** Stores the state for recursion.
- **Parallelism:**
  - We have many trees (regions) to solve.
  - We can instantiate 100 Solver Cores on the FPGA.
  - Each core solves one tree independently.
- Show the "Solved" counter racing up.

**Professor's Lecture (Narration)**
"On an FPGA, we can brute-force this with massive parallelism.
Since each tree is independent, we can build hundreds of tiny 'Solver Cores'.
Each core is a simple state machine that implements the backtracking logic.
We feed them problems, and they spit out solutions.
It's a 'Single Instruction, Multiple Data' (SIMD) approach to puzzle solving."

---

## Scene 6 (50:00–55:00) Conclusion

**Visuals**
- All the presents are packed.
- The trees look beautiful.
- The Elves cheer.
- **Text:** "Presents Packed".

**Professor's Lecture (Narration)**
"We did it.
We packed the presents, saved the holiday, and learned about Combinatorial Optimization along the way.
From Greedy failures to Bitboard victories, we've mastered the art of fitting things into places.
The North Pole is ready for Christmas.
And I think... yes, I think I hear sleigh bells.
Happy Holidays, everyone!
Class dismissed!"
