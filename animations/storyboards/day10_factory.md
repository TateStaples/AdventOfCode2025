# Day 10 — Factory (Deep Dive Storyboard)

**Sources of truth**
- Technical paper: [papers/day10_factory.md](../papers/day10_factory.md)
- Problem statement: [questions/day10.md](../questions/day10.md)
- Animation target: [animations/day10.py](../animations/day10.py)

**Target length:** 50:00 (Graduate Level Lecture)

**Lecture promise:** We’ll use the "Factory Machine" puzzle to design a Linear Algebra Accelerator. We will build a Systolic Array that solves systems of equations over different fields ((2)$ vs $\mathbb{Z}$) and invent a "Null Space Walker" to handle integer constraints in hardware.

**Style Note:** Use a Christmas color palette (Red #FF0000, Green #00FF00, Gold #FFD700, Snow White #FFFFFF). Background should be dark winter night blue (#0B0C10).

---

## Scene 1 (0:00–10:00) Introduction: The Linear Factory

**Visuals**
- **Setting:** A factory floor with broken machines.
- **Input:** Target patterns (Vectors) and Button effects (Vectors).
- **Goal:** Find the combination of button presses to match the target.
- **Math:**  = b$.
- **Part 1:** Lights (Modulo 2).
- **Part 2:** Voltages (Integers, Non-negative).

**Professor's Lecture (Narration)**
"Welcome to Day 10.
The machines are broken. We need to reverse-engineer the startup sequence.
To a casual observer, this is a puzzle.
To an engineer, this is  = b$.
We have a target vector $. We have column vectors in matrix $. We need to find $.
But there's a twist.
For the lights, +1=0$. We are in the Field of Two.
For the voltages, +1=2$. We are in the Integers.
And crucially, we can't press a button negative times.
We need a hardware solver that can handle both physics."

---

## Scene 2 (10:00–20:00) Part 1: The GF(2) Systolic Array

**Visuals**
- **Algorithm:** Gaussian Elimination.
- **Hardware:** A Systolic Array.
- **Cell Logic:**
  - Input: Row $ and Row $.
  - Operation: If Pivot is 1,  = Row_j \oplus Row_i$.
- **Dataflow:**
  - The matrix flows down.
  - Row 1 eliminates Column 1.
  - Row 2 eliminates Column 2.
- **Animation:** The matrix transforming into Identity (RREF) as it flows through the triangle.

**Professor's Lecture (Narration)**
"For Part 1, we build a Systolic Array.
Imagine a triangular grid of processors.
The equations flow in from the top.
The first row of processors eliminates the first variable.
The second row eliminates the second.
Because we are in (2)$, 'elimination' is just XOR.
It's incredibly fast.
We can solve a 100x100 system in 100 clock cycles.
This gives us a candidate solution. But is it the best one?"

---

## Scene 3 (20:00–30:00) Part 2: The Integer Challenge & Null Space

**Visuals**
- **Problem:** We solve =b$ and get  = [-5, 10, 3]$.
- **Constraint:** We can't press a button -5 times.
- **Concept:** The Null Space.
- **Visual:**
  - Show the solution space as a line in 3D.
  - {general} = x_{particular} + c \cdot x_{null}$.
  - We can slide along this line without changing the output $.
- **Goal:** Slide until all components are $\ge 0$.

**Professor's Lecture (Narration)**
"Part 2 is harder.
We run our Gaussian Elimination (using Adders instead of XORs) and we get a solution.
But the solution says: 'Press Button A negative 5 times'.
Impossible.
Does this mean the machine is broken? No.
It means we found *a* solution, not *the* solution.
We need to explore the Null Space.
The Null Space contains all the combinations of buttons that sum to zero.
We can add these 'ghost presses' to our solution to fix the negative numbers."

---

## Scene 4 (30:00–40:00) The Architecture: The Null Space Walker

**Visuals**
- **Diagram:** The Optimization Engine.
- **Component 1:** The Solver (produces $).
- **Component 2:** The Null Generator (produces basis vectors , n_2 \dots$).
- **Component 3:** The Walker.
  - Logic: .
  - Parallelism: We can check multiple multiples of $ in parallel.
- **Animation:**
  - A point starts in the "Negative Zone".
  - The Walker pushes it along the Null Vector.
  - It crosses the axis and enters the "Positive Zone".

**Professor's Lecture (Narration)**
"We build a 'Null Space Walker'.
First, our Systolic Array gives us a particular solution $ and a set of null vectors.
Then, the Walker takes over.
It checks: Is any element of $ negative?
Yes? Then add a Null Vector.
Still negative? Add it again.
We are essentially sliding our solution along the line of validity until it enters the positive quadrant.
In hardware, this is a feedback loop.
We can unroll this loop to check 10 steps at once."

---

## Scene 5 (40:00–48:00) Dataflow Walkthrough & Tradeoffs

**Visuals**
- **Example:**
  - Target: 10V.
  - Button A: 2V. Button B: 5V.
  - Equation: a + 5b = 10$.
- **Step 1:** Solver finds =5, b=0$. (Valid).
- **Step 2:** Solver finds =0, b=2$. (Valid).
- **Step 3:** Solver finds =-5, b=4$. (Invalid).
- **Step 4:** Null Vector.
  - (5) + 5(-2) = 0$. Null vector is $.
- **Correction:**
  - Start at $.
  - Add $.
  - Result: $. Valid!
- **Tradeoff:**
  - **Bit Width:** Integer math requires wide adders (64-bit). XOR is 1-bit.
  - **Area:** The Integer solver is 64x larger than the Light solver.

**Professor's Lecture (Narration)**
"Let's trace a simple example.
Our solver might be 'lazy' and give us a mathematically correct but physically impossible answer: $.
The Walker identifies the Null Vector: $.
It adds them together:  = (0, 2)$.
Now we have 0 presses of A and 2 presses of B.
That's valid.
The hardware automatically corrects the math to match reality.
The cost? Area.
Our Integer Solver needs 64-bit adders, making it significantly larger than the 1-bit XOR gates of Part 1."

---

## Scene 6 (48:00–50:00) Conclusion

**Visuals**
- **Final State:** The factory hums to life.
- **Text:** "Day 10: Solved".

**Professor's Lecture (Narration)**
"We started with a system of equations.
We built a Systolic Array to solve it.
And when the math gave us impossible answers, we built a Null Space Walker to find the physical reality hidden in the numbers.
Linear Algebra is the language of the universe.
And today, we taught silicon how to speak it.
Class dismissed."
