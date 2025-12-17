# Day 06 — Trash Compactor (Deep Dive Storyboard)

**Sources of truth**
- Technical paper: [papers/day06_trash_compactor.md](../papers/day06_trash_compactor.md)
- Problem statement: [questions/day6.md](../questions/day6.md)
- Animation target: [animations/day6.py](../animations/day6.py)

**Target length:** 45:00–55:00 (full lecture)

**Lecture promise:** We’ll use the "Cephalopod Math" puzzle to teach Parsing and Address Generation. We'll show how to decouple memory access patterns from computation, allowing us to solve two completely different parsing problems with the same hardware pipeline just by changing the "Address Generator".

**Style Note:** Use a Christmas color palette (Red #FF0000, Green #00FF00, Gold #FFD700, Snow White #FFFFFF). Background should be dark winter night blue (#0B0C10).

---

## Scene 1 (0:00–10:00) Introduction: The Homework

**Visuals**
- A trash compactor. The walls are closing in.
- A family of Cephalopods holding a worksheet.
- **Input:** A grid of numbers.
  ```
  123 328
   45  64
    *   +
  ```
- **Structure:** Blocks of numbers separated by spaces.
- **Bottom Row:** The operator (* or +).
- **Goal:** Solve the math problems.

**Professor's Lecture (Narration)**
"Welcome to the Trash Compactor.
Don't worry about the walls closing in; we have plenty of time to help these Cephalopods with their math homework.
The input is a 2D grid of characters.
It looks like a mess, but there's structure here.
We have blocks of numbers, and at the bottom of each block, an operator.
Our job is to parse these numbers, apply the operator, and sum up the results.
But here's the catch: The way we read the numbers changes between Part 1 and Part 2."

---

## Scene 2 (10:00–20:00) Part 1: Row-Major Reading

**Visuals**
- Focus on the first block:
  ```
  123
   45
    *
  ```
- **Reading Rule:** Read left-to-right, top-to-bottom.
- We see "1", "2", "3" -> Number 123.
- We see " ", "4", "5" -> Number 45.
- Operator is *.
- Result: $123 \times 45 = 5535$.
- Show a "Scan Line" moving horizontally across the rows.

**Professor's Lecture (Narration)**
"For Part 1, we read the worksheet like humans.
We scan row by row.
When we see digits, we build a number: 1... 12... 123.
When we hit a space or newline, the number is done.
We collect all the numbers in a block, find the operator at the bottom, and do the math.
This is a standard 'Row-Major' scan.
It's how we read text. It's how TV screens refresh."

---

## Scene 3 (20:00–30:00) Part 2: The Cephalopod Twist

**Visuals**
- The Cephalopods shake their heads. "No, no! Right-to-left columns!"
- **Reading Rule:** Read columns, right-to-left.
- Focus on the same block, but read vertically.
- Column 3: "3", "5" -> Number 35? No, digits are vertical.
- Let's look at the example again.
- **Vertical Digits:**
  ```
  1
  4
  ```
  -> Number 14.
- **Scan Order:** Top-to-bottom within a column. Right-to-left across columns.
- Show the "Scan Line" moving vertically.

**Professor's Lecture (Narration)**
"But wait! Cephalopods don't read like us.
They read columns. And they read them right-to-left.
So we need to completely change how we traverse the grid.
We aren't reading rows anymore. We are reading vertical strips.
The data in memory hasn't changed. The grid is the same.
But our *access pattern* must flip 90 degrees.
This is a 'Column-Major' scan."

---

## Scene 4 (30:00–40:00) The Solution: Address Generators

**Visuals**
- **Memory:** The grid is stored linearly in RAM.
  - Address 0: '1', Address 1: '2', Address 2: '3'...
- **Part 1 Generator:**
  - `for y in 0..H: for x in 0..W: yield (x,y)`
  - Addresses: 0, 1, 2, 3... (Sequential).
- **Part 2 Generator:**
  - `for x in W-1 down to 0: for y in 0..H: yield (x,y)`
  - Addresses: 2, 5, 8... (Strided).
- Show a hardware block "Address Gen" feeding coordinates to the "RAM".

**Professor's Lecture (Narration)**
"How do we build a machine that does both?
We separate the 'Compute' from the 'Access'.
We build an 'Address Generator'.
For Part 1, it counts sequentially: 0, 1, 2, 3...
For Part 2, it counts with a stride: It jumps by the width of the image.
The parsing logic—the part that builds numbers from digits—doesn't care!
It just receives a stream of characters.
By changing the address pattern, we change the problem."

---

## Scene 5 (40:00–50:00) The Pipeline

**Visuals**
- **Stage 1: Address Gen.** Emits `(x,y)`.
- **Stage 2: RAM Read.** Emits `char`.
- **Stage 3: Tokenizer.** Groups digits into numbers.
- **Stage 4: ALU.** Accumulates numbers (Sum or Product).
- **Animation:**
  - Switch from Part 1 to Part 2.
  - The Address Gen changes behavior.
  - The rest of the pipeline stays exactly the same.
  - The numbers coming out of the Tokenizer change, but the Tokenizer itself doesn't know why.

**Professor's Lecture (Narration)**
"This is the beauty of pipelining.
We have a Tokenizer that turns digits into numbers.
It doesn't know if it's reading rows or columns. It just knows 'Digit, Digit, Space'.
We have an ALU that adds or multiplies.
The only thing that changes is the very first stage: the Address Generator.
This is 'Decoupling'. It makes our hardware flexible and reusable."

---

## Scene 6 (50:00–55:00) Conclusion

**Visuals**
- The math is solved.
- The Cephalopods are happy.
- The trash compactor stops.
- **Text:** "Decouple Access from Compute".

**Professor's Lecture (Narration)**
"We survived the trash compactor.
And we learned a valuable lesson about system design.
Don't hardcode your loops into your logic.
Pull the loops out. Make them into an Address Generator.
Then, when the requirements change—or when you meet a Cephalopod—you just reprogram the generator.
Now, let's get out of here before they ask for help with History homework.
Class dismissed!"
