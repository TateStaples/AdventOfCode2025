# Day 3 — Lobby (Deep Dive Storyboard)

**Sources of truth**
- Technical paper: [papers/day03_lobby.md](../papers/day03_lobby.md)
- Problem statement: [questions/day3.md](../questions/day3.md)
- Animation target: [animations/day3.py](../animations/day3.py)

**Target length:** 10:00–15:00 (Detailed Technical Breakdown)

**Lecture promise:** We’ll use the "Battery Selection" puzzle to teach Greedy Algorithms and Stack Architectures. We'll show why "picking the biggest number" fails, derive the Monotone Stack algorithm, and implement it as a high-speed hardware pipeline.

**Style Note:** Use a Christmas color palette (Red #FF0000, Green #00FF00, Gold #FFD700, Snow White #FFFFFF). Background should be dark winter night blue (#0B0C10).

---

## Scene 1 (0:00–2:00) Introduction: The Dead Elevators

**Visuals**
- **Setting:** A grand Art Deco lobby. The elevators are dark, red lights flashing.
- **Object:** A bank of batteries labeled with digits.
- **Input:** A sequence like `9 1 8 2 7`.
- **Goal:** Select exactly **2** batteries to form the largest possible number.
- **Constraint:** You cannot rearrange them. You must pick them in their original relative order.
- **Example:**
  - Pick `9` and `1` -> **91**.
  - Pick `9` and `8` -> **98**. (Winner!)
  - Pick `1` and `7` -> **17**. (Loser).

**Professor's Lecture (Narration)**
"Welcome to the Lobby.
The elevators are dead, and the only way down is to jump-start them.
We have banks of batteries, each with a voltage rating.
We need to select a subsequence of length K to create the maximum possible voltage.
Order matters. We can't shuffle the batteries.
This is the 'Lexicographically Largest Subsequence' problem.
It sounds fancy, but it's just a greedy strategy.
We want the biggest digits in the most significant positions.
But we can't just grab every 9 we see, because we might run out of digits to fill the rest of the slots."

---

## Scene 2 (2:00–5:00) The Algorithm: The Monotone Stack

**Visuals**
- **Scenario:** Input `1 9 2 9 3`. Target Length: **3**.
- **Metaphor:** The "VIP Line" at a club.
- **Animation:**
  1.  **Input 1:** Line is empty. `1` enters. Stack: `[1]`.
  2.  **Input 9:** `9` arrives. `9 > 1`.
      - Can we kick `1` out? Yes, we have 3 digits left (`2, 9, 3`) and we only need 2 more.
      - Kick `1`. Stack: `[9]`.
  3.  **Input 2:** `2 < 9`. `2` enters. Stack: `[9, 2]`.
  4.  **Input 9:** `9 > 2`.
      - Can we kick `2` out? Yes, we have 1 digit left (`3`) and need 1 more.
      - Kick `2`. Stack: `[9, 9]`.
  5.  **Input 3:** `3 < 9`. `3` enters. Stack: `[9, 9, 3]`.
- **Result:** `993`. The largest possible number.

**Professor's Lecture (Narration)**
"Let's visualize this with a stack.
Imagine a VIP line.
A '1' is at the front. A '9' shows up.
The '9' says, 'I'm bigger than you, get out of my way!'
Does the '1' leave? Only if there are enough people behind the '9' to fill the club.
If there are, the '1' gets booted. The '9' takes the spot.
This is the Monotone Stack.
We maintain a decreasing sequence.
If a larger number comes along, we pop smaller elements off the stack—*provided* we still have enough remaining input to reach length K.
It's ruthless. It's efficient. It's (N)$."

---

## Scene 3 (5:00–8:00) Hardware Implementation: The Pipelined Stack

**Visuals**
- **Diagram:**
  - **Stack Memory:** A small RAM or Shift Register.
  - **Pointer:** Points to the "Top" of the stack.
  - **Counter:** Tracks "Remaining Digits".
  - **Comparator:** Checks `Input > Stack[Top]`.
- **Logic Flow:**
  - In every clock cycle:
  - If `Input > Top` AND `Remaining + StackSize > K`: **POP** (Decrement Pointer).
  - Else If `StackSize < K`: **PUSH** (Write to RAM, Increment Pointer).
  - Else: **DISCARD**.
- **Speed:** We process one digit per cycle. No backtracking.

**Professor's Lecture (Narration)**
"Now, how do we build this in silicon?
We need a memory for the stack.
We need a counter for 'Remaining Input'.
And we need a comparator.
In every clock cycle, we look at the incoming digit and the top of the stack.
If the new digit is bigger, and we have enough 'budget' to pop, we pop.
If the stack isn't full, we push.
It's a simple state machine controlling a memory pointer.
We can process one digit per cycle.
This is a 'Streaming Algorithm'. We don't need to store the whole input array. We just flow through it."

---

## Scene 4 (8:00–11:00) Part 2: Scaling to 12 Digits

**Visuals**
- **Challenge:** Now we need to pick **12** digits.
- **Input:** `987654321111111`.
- **Result:** `987654321111`.
- **Input:** `818181911112111`.
- **Result:** `888911112111`.
- **Hardware Change:** Just increase the Stack RAM size from 2 to 12.
- **Impact:** The logic is identical. The complexity is still (N)$.
- **Joltage Meter:** Shows the sum growing into the trillions.

**Professor's Lecture (Narration)**
"Part 2 asks us to pick 12 digits instead of 2.
In a brute-force solution, this would be a disaster. The combinations explode.
But for our Monotone Stack?
We just make the stack deeper.
We change a parameter  from 2 to 12.
The logic doesn't change. The speed doesn't change.
This is the beauty of a good algorithm. It scales.
Whether we need 2 digits or 200, the hardware cost is linear."

---

## Scene 5 (11:00–15:00) Conclusion

**Visuals**
- **Final State:** All battery banks are processed.
- **Action:** The Professor pulls a giant lever.
- **Effect:** The elevators light up. The doors slide open with a pleasant *ding*.
- **Text:** "Day 3: Solved".
- **Transition:** We step into the elevator, ready to descend to the Printing Department.

**Professor's Lecture (Narration)**
"We've successfully reconfigured the power grid.
By using a greedy stack, we maximized our voltage without wasting a single clock cycle.
The elevators are online.
Going down?
Next stop: The Printing Department.
I hear they have a paper jam.
Class dismissed!"
