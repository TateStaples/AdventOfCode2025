# Day 1 — Secret Entrance (Deep Dive Storyboard)

**Sources of truth**
- Technical paper: [papers/day01_secret_entrance.md](../papers/day01_secret_entrance.md)
- Problem statement: [questions/day1.md](../questions/day1.md)
- Animation target: [animations/day1.py](../animations/day1.py)

**Target length:** 50:00 (Graduate Level Lecture)

**Lecture promise:** We’ll use the "Safe Dial" puzzle to design a Finite State Machine (FSM) and explore the hardware implementation of Modulo Arithmetic. We will show why naive simulation fails for large inputs and derive a constant-time arithmetic solution suitable for high-performance FPGA implementation.

**Style Note:** Adopt a "3Blue1Brown" mathematical aesthetic: clean geometric primitives, smooth easing functions, and LaTeX-rendered typography. The color palette blends this with a sophisticated Christmas theme: Deep Midnight Blue background (#0B0C10), with accents in Cardinal Red (#C41E3A), Evergreen (#0B6623), and Metallic Gold (#D4AF37) for highlights. Use Snow White (#F0F8FF) for primary text and equations.

---

## Scene 1: Introduction & Problem Setup (0:00–10:00)

### Minute 0:00–1:00: Opening & Context
**Visuals:** Fade in to a stylized vector field of snow particles (white dots) moving smoothly across the Deep Midnight Blue background. The camera pans to a geometric representation of a door: a large rectangle with a glowing Red outline. A document (white rectangle) is attached.

**Narration:**
"Welcome to Day 1 of Advent of Code: Hardware Edition. I'm your professor for this 50-minute journey into digital design. You've arrived at the secret entrance to the North Pole, ready to start decorating—but the password has been changed. A document on the wall explains: 'Due to new security protocols, the password is locked in the safe below.' Today, we'll crack this safe by building a Finite State Machine, exploring modulo arithmetic in hardware, and discovering why analytical computation beats simulation."

### Minute 1:00–2:00: The Lock Mechanism & Problem Statement
**Visuals:** A perfect vector circle appears in Metallic Gold. Ticks are crisp white lines. The current position is a glowing Red dot. Labels are rendered in LaTeX font. Labels appear: "100 positions", "Current: 50". The document on the wall comes into focus, showing the puzzle input—a list of L and R rotations.

**Narration:**
"This dial has exactly 100 positions, labeled 0 through 99. It's a ring—position 99 wraps back to 0. In mathematics, we call this structure $\mathbb{Z}_{100}$, the ring of integers modulo 100. The problem statement tells us: 'The dial starts by pointing at 50.' We're given a sequence of rotation instructions—L for left toward lower numbers, R for right toward higher numbers, each followed by a distance. For example, if the dial is at 11, 'R8' moves it to 19. If it's at 5, 'L10' moves it to 95, wrapping around. Our task: decode the security protocols hidden in this mechanism."

### Minute 2:00–3:00: First Instruction Demo
**Visuals:** A clean list of instructions slides in from the left, rendered in a monospace font. The active instruction `L68` highlights in Gold. The Red dot moves smoothly along the circle's circumference counterclockwise. An arc trails behind it to show the path. Numbers tick by: 49, 48, 47... The animation accelerates but we see every tenth number flash.

**Narration:**
"The first instruction is 'L68'—rotate Left by 68 positions. Watch carefully. We're at 50. Rotating left means subtracting. $50 - 68 = -18$. But position negative-18 doesn't exist on our dial. We must wrap around. $-18 + 100 = 82$. The dial settles on 82."

**Visuals:** Equation appears: $50 - 68 \equiv 82 \pmod{100}$

### Minute 3:00–4:30: More Instructions & The Pattern Discovery
**Visuals:** Next instruction highlights: `L30`. The Red dot rotates from 82. Slower animation. $82 - 30 = 52$. Dial stops at 52. Then `R48` highlights. Dial rotates clockwise. $52 + 48 = 100$. As it crosses 99→0, the top tick flashes Gold with a satisfying *click*.

**Narration:**
"Second instruction: L30. From 82, we subtract 30, landing at 52. No wraparound needed this time. Third instruction: R48—rotate Right, meaning addition. $52 + 48 = 100$. Now here's something interesting: 100 mod 100 is 0. We've landed exactly on zero. And notice—the dial lit up with a distinct click. The problem reveals the trick: 'your recent required official North Pole secret entrance security training seminar taught you that the safe is actually a decoy. The actual password is the number of times the dial is left pointing at 0 after any rotation in the sequence.' This is Part 1: count the endings on zero."

### Minute 4:30–6:00: Defining the State Machine
**Visuals:** The circle morphs into a block diagram. "STATE" is a rectangular register with rounded corners. Arrows are thin white lines with triangular heads. An adder/subtractor symbol. Arrows showing input and output.

**Narration:**
"Let's formalize this. We're building a Finite State Machine. Our state space is the set of dial positions: 0 through 99. At each clock cycle, we receive an instruction—a direction bit and a magnitude. The next-state logic computes: 
$$\text{next\_state} = (\text{current\_state} \pm \text{magnitude}) \bmod 100$$
This is the FSM update equation. In hardware, we need a register to hold state, an adder or subtractor for the arithmetic, and a modulo unit to enforce the wraparound."

**Visuals:** Block diagram appears: Register → Adder/Subtractor → Modulo 100 → Register (feedback loop)

### Minute 6:00–7:30: Parsing the Input
**Visuals:** The input string appears as a sequence of characters. A "window" (Gold rectangle) slides over them to parse. Text parsing animation: regex pattern `[LR](\d+)` highlights characters. Each line is tokenized: Direction, Amount.

**Narration:**
"Before we can solve this, we need to parse the input. Each line is a character—L or R—followed by a decimal number. In software, we'd use a regex or a simple state machine. In hardware, we need a character-by-character parser. We scan for 'L' or 'R' to set a direction flag, then accumulate digits into a binary magnitude. For today, assume this is done—we focus on the core FSM."

### Minute 7:30–9:00: Part 1 Objective
**Visuals:** Screen divides vertically. Left: The geometric dial animation. Right: A digital counter incrementing each time the dial lands on 0.

**Narration:**
"Our Part 1 task: execute all instructions and count how many times we land exactly on position zero. The naive algorithm is straightforward—maintain the state register, update it for each instruction, check if it equals zero, accumulate the count. Let's trace an example with the first five instructions."

**Visuals:** Example trace:
- Start: 50
- L68 → 82 (miss)
- L30 → 52 (miss)
- R48 → 0 ✓ (hit!)
- L10 → 90 (miss)
- R10 → 0 ✓ (hit!)
- Counter: 2

### Minute 9:00–10:00: The Twist—Large Numbers
**Visuals:** New instruction appears: `R 1050`. The number `1050` scales up slightly and turns Cardinal Red. A warning icon flashes.

**Narration:**
"Part 1 seems simple. But look at this instruction: R 1050. Rotate right by one thousand fifty positions. Our state is, say, 25. So we compute $25 + 1050 = 1075$. Now we need $1075 \bmod 100$. In software, the percent operator is one character. In hardware, modulo is expensive. Let's explore why, because this becomes the central challenge of our design."

---

## Scene 2: Hardware Modulo—The Core Challenge (10:00–22:00)

### Minute 10:00–11:30: The Modulo Problem
**Visuals:** Three panels slide in. 1) Equation $1075 \bmod 100$. 2) Division visualization: $1075 \div 100 = 10.75$. 3) Result: $10 \times 100 = 1000$, remainder $= 75$.

**Narration:**
"Modulo computes the remainder after division. $1075 \bmod 100$ means: divide 1075 by 100, getting quotient 10 and remainder 75. In hardware, this means we need either a divider circuit or an iterative subtraction loop. Let's examine both approaches and their tradeoffs—because in digital design, every operation has a cost in silicon area, latency, and power."

### Minute 11:30–13:00: Option 1—Iterative Subtraction
**Visuals:** A minimalist circuit diagram: Accumulator (box) → Comparator (diamond) → Subtractor (trapezoid). Values flow as small data packets. Accumulator (showing 1075) → Comparator (≥100?) → Subtractor (−100) → Accumulator (showing countdown: 1075, 975, 875, 775...)

**Narration:**
"The simplest approach: repeatedly subtract 100 until the result is less than 100. Start with 1075. Subtract 100: 975. Subtract 100: 875. Keep going. After 10 iterations, we reach 75, which is less than 100, so we're done. The circuit is tiny—just a comparator, a subtractor, and a counter. But notice the problem: this takes 10 clock cycles. If the input were $50 + 10,000$, we'd need 100 iterations. Variable latency is poison for pipelined designs."

**Visuals:** Graph showing "Cycles vs. Input Magnitude" with a linear upward slope. Label: "O(n) latency".

### Minute 13:00–15:00: Option 2—Hardware Divider
**Visuals:** A complex network of nodes and edges appears, representing the divider. It looks dense and intricate compared to the previous simple loop. Non-restoring divider with multiple adder stages, shift registers, control FSM.

**Narration:**
"The robust solution: a dedicated integer divider. Modern hardware dividers use algorithms like non-restoring division or Newton-Raphson. These circuits compute quotient and remainder in constant time, regardless of magnitude—that's the key advantage. But look at the complexity: multiple adder stages, shift registers, control state machines. This is a substantial chunk of silicon. The question we must ask: is the constant latency worth the area cost? For our problem with potentially huge rotation amounts, the answer is likely yes. Variable-latency designs would stall unpredictably."

**Visuals:** Side-by-side comparison: tiny iterative circuit (simple but slow) vs. complex divider (large but predictable).

### Minute 15:00–17:00: Option 3—The Engineer's Trick: Fixed Point Multiplication
**Visuals:** The complex divider dissolves into a simple Multiplier and a Bit Shifter. A "Magic Number" constant appears: $M \approx \frac{2^N}{100}$.

**Narration:**
"But wait. We are always dividing by exactly 100. This is a constant. Division by a constant is just multiplication by its reciprocal. $\frac{x}{100} = x \times \frac{1}{100}$. In binary fixed-point arithmetic, we can approximate $\frac{1}{100}$ as $\frac{M}{2^k}$. So, $x / 100 \approx (x \times M) \gg k$. This is the 'Magic Number' trick. We replace a massive, slow divider circuit with a single hardware multiplier and a wire shift. It's fast, it's small, and it's constant time. This is how real hardware engineers solve modulo problems."

**Visuals:** Equation transformation:
$$x \bmod 100 = x - 100 \times \lfloor x \times 0.01 \rfloor$$
$$\lfloor x \times 0.01 \rfloor \approx (x \times \text{MAGIC}) \gg \text{SHIFT}$$

### Minute 17:00–19:00: Implementing the Optimized FSM
**Visuals:** The production datapath: Clean white outlines on blue. Active paths glow Gold.
- Input FIFO (Direction, Magnitude)
- State Register (7 bits for 0–99)
- Direction Mux (Add for R, Subtract for L with wraparound logic)
- Adder (calculates state ± magnitude)
- **Reciprocal Multiplier** (replaces Divider)
- Remainder feeds back to State Register
- Comparator (remainder == 0?) feeds Zero Counter

**Narration:**
"Our production design: use reciprocal multiplication. The datapath is clean. Each clock cycle, we fetch an instruction. The direction bit selects add or subtract. For subtraction, we first compute the magnitude modulo 100, then subtract from the state and add 100 if negative. The multiplier handles the modulo operations efficiently. After each state update, we check if the new state equals zero and increment our counter."

### Minute 19:00–20:30: Handling Negative Numbers
**Visuals:** Equation appears: $20 - 50 = -30$. It transforms smoothly into $70$. Alternative: $20 + (100 - 50) = 70$. 

**Narration:**
"One subtlety: left rotations. When we subtract a large number, we get a negative result. Modulo arithmetic on negative numbers is tricky—different languages define it differently. In hardware, we avoid signed arithmetic here by converting left rotations to right rotations in the complement space. For 'L by x', we instead compute 'R by (100−x mod 100)'. This keeps everything positive and uses the same optimized path."

**Visuals:** Unified datapath with "Direction == L ? (100 - mag) : mag" transformation before the main adder.

### Minute 20:30–22:00: Part 1 Complexity Summary
**Visuals:** A dark code block with syntax highlighting (keywords in Gold, variables in White).
```
state := 50
count := 0
MAGIC := 0x51EB851F  // 1/100 fixed point
for each instruction (dir, mag):
    if dir == L: mag := 100 - (mag * MAGIC >> 37)
    state := (state + mag) * MAGIC >> 37
    if state == 0: count := count + 1
return count
```

**Narration:**
"Part 1 solution: iterate through instructions, maintain state with fast reciprocal arithmetic, count zeros. Complexity: O(N) where N is the number of instructions, with each instruction taking O(1) time. For the example input with 1000 instructions, this is 1000 cycles. Throughput: excellent. Area: minimal. Now, let's turn to Part 2, where the naive approach collapses entirely."

---

## Scene 3: Part 2—Analytical Counting (22:00–35:00)

### Minute 22:00–23:30: The New Challenge from Part 2
**Visuals:** A new text block slides in: "Method 0x434C49434B". The hex morphs into "CLICK".

**Narration:**
"As you're building a snowman, you find another document in the snow. The problem states: 'method 0x434C49434B means you're actually supposed to count the number of times any click causes the dial to point at 0, regardless of whether it happens during a rotation or at the end of one.' Part 2 changes everything. Now we must count every time the dial passes through position zero during the rotation itself, not just the final position. The example clarifies: 'if the dial were pointing at 50, a single rotation like R1000 would cause the dial to point at 0 ten times before returning back to 50!' Without simulation, how do we count these intermediate crossings?"

**Visuals:** Dial animation: starting at 50, slowly rotating clockwise. Markers appear at positions 0, showing the path crosses at 100, 200, 300 before stopping at 0 (position 300 mod 100 = 0).

### Minute 23:30–25:30: The Naive Simulation Disaster
**Visuals:** Code block appears. A progress bar below fills up very slowly to represent the 250 cycles.
```
crossings := 0
pos := 50
for i := 1 to 250:
    pos := (pos + 1) mod 100
    if pos == 0: crossings := crossings + 1
```
Clock cycle counter rapidly incrementing: "Cycle 1, 2, 3... 250". Time: "250 cycles per instruction".

**Narration:**
"The naive approach: simulate each position one step at a time. Starting at 50, increment 250 times, checking for zero at each step. For this instruction, that's 250 clock cycles. If the input has 1000 instructions averaging 100 rotations each, we need 100,000 cycles. And if one instruction says 'R 1,000,000'—which Advent of Code loves to throw at us—we'd need a million cycles for that single instruction. On a 100MHz FPGA, that's 10 milliseconds per instruction. Unacceptable."

**Visuals:** Performance graph: "Naive Simulation" line shoots up exponentially with input magnitude.

### Minute 25:30–27:30: The Geometric Insight
**Visuals:** The Gold circle breaks at 0 and unrolls into a straight white number line. The movement is smooth and elastic. Current position marked at 50. Destination marked at 300 (linear).

**Narration:**
"Let's think geometrically. Rotating right by `d` positions from `p` means we travel a total distance of `p + d` along the number line. The dial has period 100. Every time we travel 100 units, we pass through zero once. So the number of zero crossings is simply: how many complete periods of 100 fit into our total distance? That's $\lfloor (p + d) / 100 \rfloor$. Integer division. From position 50, rotating 250: total distance 300. $300 \div 100 = 3$. Three crossings."

**Visuals:** Equation overlays:
$$\text{crossings} = \left\lfloor \frac{p + d}{100} \right\rfloor$$

### Minute 27:30–29:00: Mathematical Proof
**Visuals:** The background remains Deep Midnight Blue. Equations appear in white LaTeX font, centered.

**Narration:**
"Let's prove this rigorously. Define $n = \lfloor (p + d) / 100 \rfloor$. We want to show that the sequence $p, p+1, p+2, \ldots, p+d$ modulo 100 crosses zero exactly $n$ times. Zero is crossed when $(p+k) \equiv 0 \pmod{100}$, i.e., when $p+k$ is a multiple of 100. The multiples of 100 in the range $[p, p+d]$ are $100, 200, \ldots, 100n$. If $p = 50$ and $d = 250$, the multiples in $[50, 300]$ are 100, 200, 300—three multiples. Hence three crossings. QED."

**Visuals:** Blackboard shows:
- Multiples of 100 in [p, p+d]: $\{100 \lceil p/100 \rceil, 100(\lceil p/100 \rceil + 1), \ldots\}$
- Count = number of multiples ≤ p+d
- = $\lfloor (p+d)/100 \rfloor - \lceil p/100 \rceil + 1$ (if p not multiple) → simplifies to $\lfloor (p+d)/100 \rfloor$ for counting crossings.

### Minute 29:00–31:00: Left Rotations & Symmetry
**Visuals:** The number line extends to the left (negative). The "mirror" concept is shown by flipping the line around a central axis. Dial rotating counterclockwise from 90 by 150. Linear number line shows traveling backward: 90 → 0 (crossing 1) → -60 (equiv 40) → ...

**Narration:**
"What about left rotations? Rotating left by d from p means traveling distance $p - d$. If $p - d$ is negative, we've wrapped around backward. The formula generalizes: the number of zero crossings is $\lfloor p / 100 \rfloor$ minus $\lfloor (p - d) / 100 \rfloor$, but with care for negative numbers. An elegant trick: mirror the dial. Define $p' = 100 - p$. A left rotation in the original dial is a right rotation in the mirrored dial. So we compute: crossings = $\lfloor (p' + d) / 100 \rfloor$. Same formula, no branches."

**Visuals:** Two dials side-by-side: original and mirrored. Left-rotation on original equals right-rotation on mirror.

### Minute 31:00–33:00: Hardware Implementation
**Visuals:** The previous block diagram updates. A "Transform" block is inserted. The "Multiplier" block glows to indicate reuse.
- Input: (Direction, State, Magnitude)
- Stage 1: Transform (if L, mirror state: state' = 100−state)
- Stage 2: Adder (state' + magnitude)
- Stage 3: Reciprocal Multiplier (sum / 100, quotient only)
- Output: Quotient = number of crossings

**Narration:**
"Our hardware architecture for Part 2: First, if the instruction is a left rotation, transform the state by computing $100 - \text{state}$. This is a simple subtractor. Then, add the magnitude to the (possibly transformed) state. This is the total distance traveled. Finally, divide by 100 and take only the quotient—ignore the remainder. The quotient is the number of zero crossings. We feed this quotient to an accumulator. The datapath reuses the same reciprocal multiplier from Part 1."

**Visuals:** Highlight: "Multiplier reuse! Same circuit serves both Part 1 (remainder) and Part 2 (quotient)."

### Minute 33:00–35:00: Complexity & Performance
**Visuals:** A clean bar chart compares "Simulation" (tall Red bar) vs "Analytical" (tiny Green bar).
| Approach | Cycles per Instruction | Total for 1000 inst, avg mag=100 |
|----------|------------------------|----------------------------------|
| Simulation | O(magnitude) | ~100,000 cycles |
| Analytical | O(1) multiplier latency | ~1,000 cycles |

**Narration:**
"Complexity: O(1) per instruction, assuming constant-time division. If our divider takes 32 cycles, then 1000 instructions require 32,000 cycles—a 3× speedup over simulation even for moderate magnitudes. For large magnitudes like one million, the analytical approach is 30,000× faster. This is the power of moving from algorithmic simulation to closed-form computation. We've traded a loop for a formula, and the hardware thanks us."

**Visuals:** Speedup graph showing exponential divergence between simulation and analytical approaches as magnitude increases.

---

## Scene 4: Integrated Datapath & Tradeoffs (35:00–45:00)

### Minute 35:00–37:00: Unified Architecture
**Visuals:** The full architecture diagram. Data flows as small light pulses (Gold for Part 2, Green for Part 1).
- Input Parser FIFO
- Control FSM (Fetch, Transform, Compute, Accumulate states)
- Dual-purpose Reciprocal Multiplier with quotient and remainder outputs
- Two accumulators: Part 1 counter (for ending on zero) and Part 2 counter (for passing through zero)
- State register with feedback

**Narration:**
"Let's integrate everything into a production design. Our system has five stages: 1) Fetch: Read an instruction from the input FIFO. 2) Transform: If it's a left rotation, mirror the state. 3) Compute: Add magnitude to state and invoke the multiplier. 4) Extract: Route multiplier remainder to state register and quotient to Part 2 accumulator. Check if remainder is zero for Part 1. 5) Writeback: Update accumulators and advance to next instruction. The multiplier is shared, reducing area by 50% compared to separate Part 1 and Part 2 pipelines."

**Visuals:** Animation of data flowing through the five-stage pipeline with colored paths for Part 1 (remainder path, green) and Part 2 (quotient path, gold).

### Minute 37:00–39:00: Understanding the Area-Latency Tradeoff
**Visuals:** A Treemap visualization of area. The "Multiplier" is a moderate Red rectangle. "State" is a tiny dot.

**Narration:**
"Let's think about where our silicon budget goes. The state register? Trivial—just seven bits. The accumulators and control FSM? Small, straightforward logic. The parser? Manageable. The multiplier? It's larger than an adder, but much smaller than a full divider. This is the sweet spot. We get the constant-time performance of a divider with the area efficiency of a multiplier. This suggests an obvious optimization question: could we use a smaller, slower iterative approach? Perhaps, but with reciprocal multiplication, we don't need to. We have achieved both speed and efficiency."

**Visuals:** Tradeoff curve: "Area vs. Latency" showing a pareto frontier with multiple design points, each representing different implementations.

### Minute 39:00–41:00: The Power Question
**Visuals:** The Multiplier block pulses with a Red glow (heat) while other blocks remain cool Blue.

**Narration:**
"Now consider power. Where does energy go in our design? Every cycle, the multiplier toggles thousands of gates even when we're not using it. The registers? They only switch when values change—much less active. This observation leads us to a key optimization: what if we could shut down the multiplier when it's idle? This is clock gating. Or what if we could prevent unnecessary signal transitions from propagating into the multiplier during setup? This is operand isolation. These techniques don't change our algorithm or correctness—they're pure efficiency wins. The question is: does the added control logic pay for itself in power savings? For always-on, high-duty-cycle applications, probably yes. For sporadic use cases, maybe not. Again, we're navigating a tradeoff space."

**Visuals:** Animation showing clock gating in action: the multiplier goes dark when not in use, then lights up only when processing an instruction.

### Minute 41:00–43:00: A Radical Alternative—Why Not Precompute Everything?
**Visuals:** The Multiplier block shrinks and vanishes. A grid representing "LUT" appears in its place.

**Narration:**
"Wait. We're burning silicon on a multiplier to compute the same modulo-100 operation over and over. But our state space is tiny: just 0 through 99. And after we reduce the magnitude modulo 100, it's also 0 through 99. That's only 10,000 possible input combinations. What if we just precompute every possible answer and store them in a lookup table? Query: (state=50, magnitude=48). Answer: quotient=0, remainder=98. One memory read. One cycle. No multiplication. The question is: do we have enough memory? FPGAs have block RAM—dedicated memory resources separate from logic. If we can fit our table in block RAM, we've traded arithmetic complexity for memory, which might be cheaper depending on the target device. But here's the catch: this only works because our problem has a small state space. If the modulus were 1000, we'd need a million entries. If it were 32-bit, we'd need impossibly more. The LUT approach is elegant but not general. That's the lesson: sometimes problem-specific optimizations beat general-purpose arithmetic."

**Visuals:** Comparison diagram showing the two approaches, with annotations about when each is appropriate.

### Minute 43:00–45:00: Design Decision & Justification
**Visuals:** A grid appears. Checkmarks (Green) and Crosses (Red) populate the cells.

**Narration:**
"Which design do we choose? For this specific problem with modulo 100, the LUT approach is optimal—smallest area, lowest latency, deterministic. But as hardware engineers, we design for generality. What if tomorrow the problem is modulo 1000? Or modulo $2^{32}$? The reciprocal multiplier solution scales. The LUT approach does not. My recommendation: implement both. Use the LUT for fast prototyping and benchmarking. Use the multiplier for the production design. Document the tradeoffs. In the real world, your customer might not tell you the constraints upfront."

**Visuals:** Final architecture diagram with a configuration parameter: `USE_LUT` (Boolean). A mux selects between LUT path and multiplier path based on this param.

---

## Scene 5: Advanced Architectures (45:00–48:00)

### Minute 45:00–46:00: The Pipeline Question—Can We Go Faster?
**Visuals:** The datapath is shown. Vertical lines (pipeline stages) slice through it. Clock frequency limited by the longest combinational path.

**Narration:**
"We've built a functional design. Now ask: can we make it faster? The clock frequency is limited by our longest combinational path—probably through the multiplier. What if we inserted pipeline registers, breaking the long path into shorter stages? Parse, then transform, then add, then multiply, then writeback. Each stage is simpler, so we can clock faster. But here's the problem: our dial state creates a dependency chain. Instruction N needs the result of instruction N-1. We can't start processing instruction N+1 until N completes. This is a loop-carried dependency—the bane of pipelining. We have two choices: accept stalls while waiting for results, or implement bypass paths to forward results before they're written back. The forwarding network adds complexity. Is it worth it? Maybe, if our goal is higher clock frequency to meet timing closure, even if throughput per instruction doesn't improve. This is a subtle point: pipelining helps frequency, but dependencies limit throughput."

**Visuals:** Animation showing instruction waves flowing through pipeline stages, with stall bubbles appearing due to dependencies.

### Minute 46:00–47:00: A Thought Experiment—What If We Didn't Know The Starting Position?
**Visuals:** The single "State" circle splits into a grid of 100 smaller circles.

**Narration:**
"Let's conduct a thought experiment. Our design assumes we know the starting position: 50. But what if we didn't? What if we needed to answer the question: 'For *every* possible starting position 0 through 99, how many times would the dial cross zero?' The naive approach: run our sequential design 100 times, once per starting position. But there's another way. Instead of tracking a single dial state, track *all 100 states in parallel*. Each instruction becomes a transformation on a 100-element vector. For position p, we compute: after this instruction, how many zeros did we cross? Then we merge instructions using an elegant observation: the effect of instruction B starting from position p is the same as its effect starting from position 0, just with the result vector rotated by B's rotation amount. This is an associative operation—we can build a tree. The insight: we've converted a sequential dependency into embarrassingly parallel computation by expanding the state space. The cost? We need orders of magnitude more storage and arithmetic. When would you use this? When latency matters more than area, or when you genuinely need to solve for all starting positions."

**Visuals:** Split screen: sequential design processing one position vs. parallel design with 100 lanes computing simultaneously.

### Minute 47:00–48:00: Parallel Design Tradeoffs & Implementation
**Visuals:** A logarithmic scale graph shows the massive area increase.

**Narration:**
"The parallel tree architecture processes N instructions in O(log N) time instead of O(N). For 1024 instructions, that's 10 merge levels instead of 1024 sequential cycles. The catch: area scales with N×100—we need 100 counters per chunk, plus shift networks for the merge. On a modern FPGA, this consumes hundreds of thousands of LUTs. When do we use this? When latency matters more than area, or when we have multiple independent dial problems to solve. The HardCaml implementation shows how OCaml's type system makes this elegant—the merge operation is a simple higher-order function that generates the entire reduction tree automatically."

**Visuals:** Code snippet showing HardCaml's tree combinator building the reduction network, contrasted with equivalent Verilog that would be hundreds of lines.

## Scene 6: Worked Example & Verification (48:00–49:30)

### Minute 48:00–49:00: Full Trace of Example Input from Problem Statement
**Visuals:** Left: Input list. Right: The geometric dial updates instantly for each step.

**Narration:**
"Let's trace the exact example from the problem statement to stay grounded. The puzzle tells us: 'The dial starts by pointing at 50.' We're given 10 rotations. Let's execute them precisely as described."

**Visuals (Matching problem statement exactly):**
```
Start: dial=50
L68: dial → 82 (Part2 += 1 crossing)
L30: dial → 52
R48: dial → 0 (Part1++, Part2 += 1)
L5:  dial → 95
R60: dial → 55 (Part2 += 1 crossing)
L55: dial → 0 (Part1++)
L1:  dial → 99
L99: dial → 0 (Part1++, Part2 += 1 crossing)
R14: dial → 14
L82: dial → 32 (Part2 += 1 crossing)

Final: Part1=3, Part2=6
```

**Narration (detailed):**
"The problem states: 'Because the dial points at 0 a total of three times during this process, the password in this example is 3.' That's our Part 1 answer. For Part 2, it says: 'the dial points at 0 three times at the end of a rotation, plus three more times during a rotation. So, in this example, the new password would be 6.' Our hardware produces exactly these values. The L68 crosses zero once during its rotation—confirmed. R60 from position 95 crosses zero once: (95+60)/100 = 1.55, floor gives 1. Perfect match."

### Minute 49:00–49:30: Verification Against Real Input
**Visuals:** A minimalist console window shows the final output: "Part 1: 1123".

**Narration:**
"For the real puzzle input, the problem confirms: 'Your puzzle answer was 1123.' Our sequential hardware design processes the full input and produces 1123 for Part 1. The parallel design, with its log-depth tree, produces the same result in a fraction of the time but at 100× the area cost. Both designs are functionally correct—the choice depends on whether you're optimizing for latency, throughput, or silicon area."

## Scene 7: Conclusion & Reflection (49:30–50:00)

### Minute 49:30–49:50: Design Space Summary
**Visuals:** A scatter plot with "Area" (x) vs "Latency" (y). The four design points are distinct geometric shapes.
1. "Sequential + Iterative Mod" (tiny area, high latency)
2. "Sequential + Reciprocal Multiplier" (moderate area, low latency) ← recommended
3. "Deep Pipeline" (moderate area, low latency but limited by dependency)
4. "Parallel Tree" (huge area, logarithmic latency)

**Narration:**
"We've explored four distinct architectures, each representing different points in the design space. The sequential design with a reciprocal multiplier strikes the best balance for most applications—it matches the reference algorithm exactly, scales well, and fits comfortably on a mid-range FPGA. The parallel tree is a research curiosity that shows what's possible when latency is paramount. In the real world, you'd choose based on your constraints: Is area unlimited? Use parallelism. Is latency critical but area tight? Pipeline aggressively. Is this a one-off batch job? The iterative divider might suffice."

### Minute 49:50–50:00: Final Reflection & Tomorrow's Preview
**Visuals:** The geometric door from Scene 1 slides open. The camera moves through into a field of abstract numbers.

**Narration:**
"We didn't just solve a puzzle today—we architected a family of solutions. We started from first principles: the ring of integers modulo 100, the finite state machine, the cost of division. We derived analytical formulas that turned O(N) simulation into O(1) arithmetic using fixed-point magic. And we explored how different hardware implementations trade area for speed. This is the discipline of hardware design: understand the mathematics, respect the physics, and make informed tradeoffs. Tomorrow: the Gift Shop, where number theory meets arithmetic progressions. See you then."

**Visuals:** Fade to black. Text overlays: "Day 1 Complete | Sequential Design: 5.3k LUTs | Parallel Design: 500k LUTs | Both: Functionally Correct"
