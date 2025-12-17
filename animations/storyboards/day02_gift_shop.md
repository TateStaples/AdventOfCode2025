# Day 2 — Gift Shop (Deep Dive Storyboard)

**Sources of truth**
- Technical paper: [papers/day02_gift_shop.md](../papers/day02_gift_shop.md)
- Problem statement: [questions/day2.md](../questions/day2.md)
- Animation target: [animations/day2.py](../animations/day2.py)

**Target length:** 50:00 (Graduate Level Lecture)

**Lecture promise:** We will replace a brute-force string parsing algorithm with Number Theory. We will prove that "repeated pattern" numbers form Arithmetic Progressions, allowing us to sum millions of them in constant time using a custom "Intersection Unit" in hardware.

**Style Note:** Bright, commercial colors (Neon Pink #FF6EC7, Cyan #00FFFF, White #FFFFFF). Background is a sleek, modern retail interface.

---

## Scene 1 (0:00–10:00) Introduction: The Barcode Scanner

**Visuals**
- **Setting:** The North Pole Gift Shop. A conveyor belt of presents.
- **Action:** A laser scanner reads barcodes.
- **Problem:** We are given a list of ranges, e.g., `100-500`, `1200-1300`.
- **Task:** Find "Invalid IDs".
  - An ID is invalid if it is a repeating pattern.
  - Example: `1212` (12 repeated), `333` (3 repeated), `123123` (123 repeated).
- **Goal:** Sum all invalid IDs in the ranges.

**Professor's Lecture (Narration)**
"Day 2. The Gift Shop.
We have a database of product IDs, defined by ranges.
We need to find the 'Invalid' ones—the glitches.
These are numbers formed by repeating a sequence.
`1212`. `456456`.
A human looks at `1212` and sees a pattern.
A computer sees a binary integer.
To a CPU, `1212` is just `0x4BC`. The pattern is lost.
So, how do we find them?
The naive approach is to convert every number to a string and check it.
Let's see how that performs."

---

## Scene 2 (10:00–20:00) The Naive Approach: String Parsing

**Visuals**
- **Animation:**
  - Range: `1000` to `9999`.
  - Counter starts at 1000.
  - **Step 1:** Convert `1000` to string "1000".
  - **Step 2:** Check substrings. "10" == "00"? No.
  - **Step 3:** Increment to 1001.
  - ...
  - **Step N:** Reach `1212`. "12" == "12"? Yes! Add to sum.
- **Performance Meter:** The bar is red. "Throughput: 100 items/sec".
- **Bottleneck:** Integer-to-String conversion (Division/Modulo loop) is extremely expensive in hardware.

**Professor's Lecture (Narration)**
"This is the software approach.
Loop through the range. `itoa`. String compare.
It works for a thousand items.
But what if our range is `1` to `1,000,000,000`?
We are burning cycles converting binary to decimal, just to look for a visual pattern.
We are fighting the representation.
We need to stop looking at these as strings and start looking at them as numbers.
What is the mathematical structure of a repeated number?"

---

## Scene 3 (20:00–30:00) Mathematical Derivation: Arithmetic Progressions

**Visuals**
- **Equation:** Take the number `1212`.
  - $1212 = 12 \times 100 + 12 \times 1$.
  - $1212 = 12 \times (100 + 1)$.
  - $1212 = 12 \times 101$.
- **Equation:** Take `123123`.
  - $123123 = 123 \times 1000 + 123 \times 1$.
  - $123123 = 123 \times 1001$.
- **Generalization:**
  - For a pattern $s$ of length $m$, repeated $k$ times:
  - $N = s \times \text{Constant}$.
  - The constant depends only on $m$ and $k$.
- **Visualization:**
  - Show the number line.
  - Mark multiples of 101: `101, 202, 303... 1212...`
  - These are evenly spaced!
  - They form an **Arithmetic Progression (AP)**.

**Professor's Lecture (Narration)**
"Look closer.
`1212` isn't just a string. It's `12` times `101`.
`3434` is `34` times `101`.
All 4-digit numbers formed by repeating a 2-digit sequence are just multiples of 101.
They form an Arithmetic Progression.
Start: $10 \times 101 = 1010$.
Step: $101$.
End: $99 \times 101 = 9999$.
We don't need to search for them. We can generate them.
We have transformed a search problem into a generation problem."

---

## Scene 4 (30:00–40:00) Hardware Architecture: The Intersection Unit

**Visuals**
- **Concept:** We have a Query Range $[L, U]$. We have an AP $\{Start, Step, End\}$.
- **Task:** Find the sum of the AP elements that fall inside $[L, U]$.
- **Logic:**
  - Effective Start $S' = \max(Start, \text{First multiple of Step } \ge L)$.
  - Effective End $E' = \min(End, U)$.
  - If $S' > E'$, sum is 0.
  - Count $n = (E' - S') / Step$.
  - Sum = Arithmetic Series Formula: $\frac{n}{2}(2S' + (n-1)Step)$.
- **Block Diagram:**
  - Inputs: Range $[L, U]$, Pattern Config $(m, k)$.
  - **Stage 1:** Pattern Generator (Lookup Table for Step/Limits).
  - **Stage 2:** Intersection Logic (Min/Max/Round-up).
  - **Stage 3:** Arithmetic Series Unit (Multiplier/Adder).
  - **Output:** Partial Sum.

**Professor's Lecture (Narration)**
"Now we build the hardware.
We don't loop. We calculate.
We have a 'Pattern Generator' that spits out the parameters for every family of repeats.
Multiples of 11. Multiples of 101. Multiples of 1001.
For each family, we feed it into an 'Intersection Unit'.
This unit calculates the overlap between our query range and the pattern progression.
It finds the first term, the last term, and the count.
Then, using the Gaussian summation formula—the one you learned in grade school—it computes the sum in a single clock cycle.
$O(1)$ per pattern family."

---

## Scene 5 (40:00–48:00) Dataflow Walkthrough: Summing the Glitches

**Visuals**
- **Example:** Range `[1200, 1500]`.
- **Pattern Family:** 2-digit repeats (Multiples of 101).
  - AP: $1010, 1111, 1212, 1313, 1414, 1515 \dots$
- **Intersection:**
  - Lower Bound: $\max(1010, 1200) \to 1200$.
  - Next multiple of 101 after 1200?
  - $1200 / 101 = 11.88$. Round up to 12.
  - $12 \times 101 = 1212$.
  - Effective Start: $1212$.
  - Upper Bound: $\min(9999, 1500) \to 1500$.
  - Last multiple of 101 before 1500?
  - $1500 / 101 = 14.85$. Round down to 14.
  - $14 \times 101 = 1414$.
  - Effective End: $1414$.
- **Calculation:**
  - Terms: $1212, 1313, 1414$.
  - Count: 3.
  - Sum: $1212 + 1313 + 1414 = 3939$.
- **Result:** The hardware outputs `3939` instantly.

**Professor's Lecture (Narration)**
"Let's trace the electrons.
Our range is 1200 to 1500.
The hardware checks the '101' family.
It calculates the first multiple of 101 after 1200. That's 1212.
It calculates the last multiple before 1500. That's 1414.
It sees three terms: 1212, 1313, 1414.
It applies the formula.
Boom. 3939.
No loops. No string conversion. Just pure arithmetic.
We processed a range of 300 numbers in the time it takes to add two integers."

---

## Scene 6 (48:00–50:00) Conclusion

**Visuals**
- **Final State:** The total sum is displayed on the register.
- **Text:** "Day 2: Solved".

**Professor's Lecture (Narration)**
"We started with a string parsing problem.
We ended with a geometry problem.
By recognizing the Arithmetic Progressions hidden inside the numbers, we built a machine that scales infinitely.
Whether the range is ten or ten billion, the latency is the same.
That is the power of hardware-oriented algorithms.
See you tomorrow."
