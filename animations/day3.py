"""
Day 3: Battery Bank Animation - Advent of Code 2025

This animation demonstrates the "Battery Bank" problem in three main scenes:
1. Problem Scene: Visual demonstration of selecting batteries to maximize joltage
2. Algorithm Scene: Greedy approach for Part 1 (k=2) and Part 2 (k=12)
3. Circuit Scene: Hardware implementation using dynamic programming state machine

STYLE PREFERENCES:
================================================================================
CODE BLOCKS:
- Use VGroup with styled Text (Monospace font, GRAY color) + SurroundingRectangle
- Avoid Manim's Code class due to compatibility issues

LAYOUT:
- Use ABSOLUTE positioning (e.g., shift(DOWN*2.5)) to prevent overflow
- Avoid relative positioning that can push elements off-screen

GREEDY ALGORITHM:
- For k=2: scan left to right, track (unfinished, finished) tuples
- For k=12: streaming monotonic stack (drop smaller digits while you still can)

CIRCUIT DATAFLOW:
- Part 1: Simple linear scan with two registers (tens place, ones place)
- Part 2: Streaming monotonic stack (O(k) storage, 1 digit/cycle)
================================================================================
"""

from manim import *
import numpy as np
from typing import List, Tuple, Optional, Any, Union


class Day3(Scene):
    # ========== VISUAL CONSTANTS ==========
    
    # Colors
    COLOR_BATTERY = YELLOW
    COLOR_SELECTED = GREEN
    COLOR_UNSELECTED = GRAY
    COLOR_PART1 = BLUE
    COLOR_PART2 = ORANGE
    COLOR_CODE = GRAY
    COLOR_TENS = LIGHT_PINK
    COLOR_ONES = TEAL
    COLOR_REGISTER = PURPLE
    COLOR_COMPARATOR = RED
    
    # Text scales
    SCALE_TITLE = 0.8
    SCALE_SUBTITLE = 0.6
    SCALE_TEXT = 0.5
    SCALE_SMALL = 0.4
    SCALE_TINY = 0.3
    SCALE_CODE = 0.25
    
    # Timing
    STANDARD_WAIT = 0.5
    LONG_WAIT = 1.5
    EXTENDED_WAIT = 2.0
    ANIMATION_SPEED = 0.5
    
    def construct(self) -> None:
        """Main entry point - orchestrates all three scenes."""
        self.scene_problem()
        self.clear()
        self.scene_algorithm()
        self.clear()
        self.scene_circuit()
    
    # ========== HELPER FUNCTIONS ==========
    
    def create_battery(self, digit: int, selected: bool = False) -> VGroup:
        """Create a battery visual with digit label."""
        color = self.COLOR_SELECTED if selected else self.COLOR_BATTERY
        
        # Battery shape (rectangle with rounded top)
        body = Rectangle(height=0.8, width=0.4, color=color, fill_opacity=0.3)
        terminal = Rectangle(height=0.1, width=0.2, color=color, fill_opacity=0.5)
        terminal.next_to(body, UP, buff=0)
        
        # Digit label
        label = Text(str(digit), color=WHITE).scale(0.5).move_to(body)
        
        battery = VGroup(body, terminal, label)
        return battery
    
    def create_battery_bank(self, digits: List[int], selected_indices: List[int] = None) -> VGroup:
        """Create a row of batteries."""
        selected_indices = selected_indices or []
        batteries = VGroup(*[
            self.create_battery(digit, i in selected_indices)
            for i, digit in enumerate(digits)
        ])
        batteries.arrange(RIGHT, buff=0.2)
        return batteries
    
    def create_code_block(self, lines: List[str], title: str = None) -> VGroup:
        """Create a code block with optional title."""
        code_lines = VGroup(*[
            Text(line, font="Monospace", color=self.COLOR_CODE).scale(self.SCALE_CODE)
            for line in lines
        ])
        code_lines.arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        
        if title:
            title_text = Text(title, color=WHITE).scale(self.SCALE_SMALL)
            title_text.next_to(code_lines, UP, buff=0.2)
            code_box = SurroundingRectangle(VGroup(title_text, code_lines), color=self.COLOR_CODE, buff=0.15)
            return VGroup(code_box, title_text, code_lines)
        else:
            code_box = SurroundingRectangle(code_lines, color=self.COLOR_CODE, buff=0.15)
            return VGroup(code_box, code_lines)
    
    # ========== SCENE 1: PROBLEM ==========
    
    def scene_problem(self) -> None:
        """
        First scene: Demonstrate the problem visually.
        Show battery banks and how to select digits to maximize joltage.
        """
        title = Text("Day 3: Pick the Best Batteries").scale(self.SCALE_TITLE).to_edge(UP)
        self.play(Write(title))
        self.wait(self.STANDARD_WAIT)
        
        # Show the problem statement
        self.problem_intro(title)
        
        # Demonstrate Part 1 (k=2)
        self.problem_part1_demo(title)
        
        # Demonstrate Part 2 (k=12)
        self.problem_part2_demo(title)
    
    def problem_intro(self, title: Text) -> None:
        """Introduce the battery bank problem."""
        subtitle = Text("Power the Escalator!").scale(self.SCALE_SUBTITLE)
        subtitle.next_to(title, DOWN)
        self.play(Write(subtitle))
        self.wait(self.STANDARD_WAIT)
        
        # Show a battery bank
        digits = [9, 8, 7, 6, 5, 4, 3, 2, 1]
        bank = self.create_battery_bank(digits)
        bank.shift(UP * 0.5)
        
        bank_label = Text("Battery Bank (joltage ratings)").scale(self.SCALE_SMALL)
        bank_label.next_to(bank, UP, buff=0.3)
        
        self.play(FadeIn(bank), Write(bank_label))
        self.wait(self.LONG_WAIT)
        
        # Show selection rule
        rule = Text("Pick exactly k batteries (keep them in order)", color=self.COLOR_PART1).scale(self.SCALE_TEXT)
        rule.shift(DOWN * 1.0)
        self.play(Write(rule))
        self.wait(self.STANDARD_WAIT)
        
        # Show joltage formula
        formula = Text("Joltage = combine digits into one number", color=self.COLOR_PART1).scale(self.SCALE_TEXT)
        formula.next_to(rule, DOWN, buff=0.3)
        self.play(Write(formula))
        self.wait(self.LONG_WAIT)
        
        self.play(FadeOut(VGroup(subtitle, bank, bank_label, rule, formula)))
    
    def problem_part1_demo(self, title: Text) -> None:
        """Demonstrate Part 1: Select k=2 batteries."""
        subtitle = Text("Part 1: Select 2 Batteries").scale(self.SCALE_SUBTITLE)
        subtitle.next_to(title, DOWN)
        self.play(Write(subtitle))
        self.wait(self.STANDARD_WAIT)
        
        # Example bank
        digits = [9, 8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1, 1, 1, 1]
        bank = self.create_battery_bank(digits)
        bank.shift(UP * 1.0)
        
        self.play(FadeIn(bank))
        self.wait(self.STANDARD_WAIT)
        
        # Show different selections
        examples = [
            ([0, 1], "98", "Select first two: 98"),
            ([1, 7], "82", "Select 8 and 2: 82"),
            ([0, 7], "92", "Select 9 and 2: 92 (Best!)"),
        ]
        
        result_text = Text("").scale(self.SCALE_TEXT).shift(DOWN * 1.5)
        
        for indices, value, description in examples:
            # Highlight selected batteries
            highlights = VGroup(*[
                SurroundingRectangle(bank[i], color=self.COLOR_SELECTED, buff=0.05)
                for i in indices
            ])
            
            self.play(Create(highlights))
            
            # Show result
            new_result = Text(description, color=self.COLOR_SELECTED).scale(self.SCALE_TEXT)
            new_result.move_to(result_text)
            
            self.play(Transform(result_text, new_result))
            self.wait(self.LONG_WAIT)
            
            self.play(FadeOut(highlights))
        
        self.play(FadeOut(VGroup(subtitle, bank, result_text)))
    
    def problem_part2_demo(self, title: Text) -> None:
        """Demonstrate Part 2: Select k=12 batteries."""
        subtitle = Text("Part 2: Select 12 Batteries").scale(self.SCALE_SUBTITLE)
        subtitle.next_to(title, DOWN)
        self.play(Write(subtitle))
        self.wait(self.STANDARD_WAIT)
        
        # Example bank
        digits = [9, 8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1, 1, 1, 1]
        bank = self.create_battery_bank(digits)
        bank.scale(0.7).shift(UP * 1.5)
        
        self.play(FadeIn(bank))
        self.wait(self.STANDARD_WAIT)
        
        # Show greedy approach
        approach = Text("Greedy: Pick 12 largest digits (leftmost if tied)").scale(self.SCALE_SMALL)
        approach.shift(UP * 0.3)
        self.play(Write(approach))
        self.wait(self.STANDARD_WAIT)
        
        # Highlight top 12
        selected = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]  # All except last 3 ones
        highlights = VGroup(*[
            SurroundingRectangle(bank[i], color=self.COLOR_SELECTED, buff=0.03)
            for i in selected
        ])
        
        self.play(Create(highlights), run_time=1.5)
        self.wait(self.LONG_WAIT)
        
        # Show result
        result = Text("Result: 987654321111", color=self.COLOR_SELECTED).scale(self.SCALE_TEXT)
        result.shift(DOWN * 0.8)
        self.play(Write(result))
        self.wait(self.EXTENDED_WAIT)
        
        self.play(FadeOut(VGroup(subtitle, bank, approach, highlights, result)))
    
    # ========== SCENE 2: ALGORITHM ==========
    
    def scene_algorithm(self) -> None:
        """
        Second scene: Explain the algorithms for both parts.
        Part 1: Dynamic programming with (unfinished, finished) state
        Part 2: Sort-and-select greedy approach
        """
        title = Text("The Algorithms").scale(self.SCALE_TITLE).to_edge(UP)
        self.play(Write(title))
        self.wait(self.STANDARD_WAIT)
        
        # Part 1 algorithm
        self.algorithm_part1(title)
        
        # Part 2 algorithm
        self.algorithm_part2(title)
    
    def algorithm_part1(self, title: Text) -> None:
        """Explain Part 1 dynamic programming algorithm."""
        subtitle = Text("Part 1: Dynamic Programming (k=2)").scale(self.SCALE_SUBTITLE)
        subtitle.next_to(title, DOWN)
        self.play(Write(subtitle))
        self.wait(self.STANDARD_WAIT)
        
        # Show the idea
        idea = Text("Keep track of two numbers as we scan:").scale(self.SCALE_TEXT)
        idea.shift(UP * 1.8)
        self.play(Write(idea))
        
        state_desc = VGroup(
            Text("- unfinished: best single digit so far (tens spot)", color=self.COLOR_TENS).scale(self.SCALE_SMALL),
            Text("- finished: best 2-digit number completed", color=self.COLOR_ONES).scale(self.SCALE_SMALL)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        state_desc.shift(UP * 1.0)
        
        self.play(Write(state_desc))
        self.wait(self.LONG_WAIT)
        
        # Show the recurrence
        recurrence_title = Text("For each digit d:").scale(self.SCALE_SMALL)
        recurrence_title.shift(UP * 0.0)
        self.play(Write(recurrence_title))
        
        recurrence = VGroup(
            Text("use_ones = unfinished + d  (add to tens)", color=self.COLOR_ONES).scale(self.SCALE_TINY),
            Text("use_tens = 10 x d  (start fresh)", color=self.COLOR_TENS).scale(self.SCALE_TINY),
            Text("finished = max(finished, use_ones)", color=self.COLOR_PART1).scale(self.SCALE_TINY),
            Text("unfinished = max(unfinished, use_tens)", color=self.COLOR_PART1).scale(self.SCALE_TINY)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        recurrence.shift(DOWN * 0.6)
        
        self.play(Write(recurrence))
        self.wait(self.LONG_WAIT)
        
        # Show code
        code_lines = [
            "fn max_joltage(bank: Vec<u8>) -> u8 {",
            "  bank.fold((0, 0), |(unfin, fin), d| {",
            "    let use_ones = unfin + d;",
            "    let use_tens = 10 * d;",
            "    let fin' = fin.max(use_ones);",
            "    let unfin' = use_tens.max(unfin);",
            "    (unfin', fin')",
            "  }).1  // Return finished",
            "}"
        ]
        
        code = self.create_code_block(code_lines, "Rust Implementation")
        code.scale(0.9).shift(DOWN * 2.0)
        self.play(FadeIn(code))
        self.wait(self.EXTENDED_WAIT)
        
        self.play(FadeOut(VGroup(subtitle, idea, state_desc, recurrence_title, recurrence, code)))
    
    def algorithm_part2(self, title: Text) -> None:
        """Explain Part 2 streaming monotonic-stack algorithm."""
        subtitle = Text("Part 2: The Stack Trick (k=12 digits)").scale(self.SCALE_SUBTITLE)
        subtitle.next_to(title, DOWN)
        self.play(Write(subtitle))
        self.wait(self.STANDARD_WAIT)
        
        # Show the strategy
        strategy = Text("Idea: Swap out smaller digits for bigger ones").scale(self.SCALE_TEXT)
        strategy.shift(UP * 1.8)
        self.play(Write(strategy))
        self.wait(self.STANDARD_WAIT)
        
        # Show steps
        steps = VGroup(
            Text("1. Keep a stack of chosen digits (max k)", color=YELLOW).scale(self.SCALE_SMALL),
            Text("2. For each digit d: if stack top < d AND slots left, pop it", color=YELLOW).scale(self.SCALE_SMALL),
            Text("3. If stack not full, push d onto stack", color=GREEN).scale(self.SCALE_SMALL),
            Text("4. Move to next digit, keep order", color=GREEN).scale(self.SCALE_SMALL),
            Text("5. Stack IS the answer!", color=BLUE).scale(self.SCALE_SMALL)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        steps.shift(UP * 0.5)
        
        self.play(Write(steps))
        self.wait(self.LONG_WAIT)
        
        # Example walkthrough
        example_title = Text("Example: [9,8,7,6,5,4,3,2,1,1,1,1,1,1,1], k=12").scale(self.SCALE_TINY)
        example_title.shift(DOWN * 0.5)
        self.play(Write(example_title))
        
        example_steps = VGroup(
            Text("Pop while better digit arrives, keep order", color=GRAY).scale(self.SCALE_TINY),
            Text("Final stack keeps first 12 strongest digits", color=GRAY).scale(self.SCALE_TINY),
            Text("Result: 987654321111", color=self.COLOR_SELECTED).scale(self.SCALE_TINY)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        example_steps.shift(DOWN * 1.0)
        
        self.play(Write(example_steps))
        self.wait(self.LONG_WAIT)
        
        # Show code
        code_lines = [
            "fn top_n_joltage(bank: Vec<u8>, k: usize) -> u64 {",
            "  let mut stack: Vec<u8> = Vec::with_capacity(k);",
            "  let mut remaining = bank.len();",
            "  for d in bank {",
            "    remaining -= 1;",
            "    while let Some(&top) = stack.last() {",
            "      if top < d && stack.len() - 1 + remaining >= k {",
            "        stack.pop();",
            "      } else { break; }",
            "    }",
            "    if stack.len() < k { stack.push(d); }",
            "  }",
            "  stack.into_iter().fold(0u64, |acc, d| acc * 10 + d as u64)",
            "}",
        ]

        code = self.create_code_block(code_lines, "Rust Implementation")
        code.scale(0.8).shift(DOWN * 2.3)
        self.play(FadeIn(code))
        self.wait(self.EXTENDED_WAIT)
        
        self.play(FadeOut(VGroup(subtitle, strategy, steps, example_title, example_steps, code)))
    
    # ========== SCENE 3: CIRCUIT ==========
    
    def scene_circuit(self) -> None:
        """
        Third scene: Hardware implementation.
        Part 1: Simple state machine with two registers
        Part 2: Sorting network for finding top k
        """
        title = Text("Hardware Implementation").scale(self.SCALE_TITLE).to_edge(UP)
        self.play(Write(title))
        self.wait(self.STANDARD_WAIT)
        
        # Part 1 circuit
        self.circuit_part1(title)
        
        # Part 2 circuit
        self.circuit_part2(title)
        
        # Performance summary
        self.circuit_summary(title)
    
    def circuit_part1(self, title: Text) -> None:
        """Show Part 1 hardware: simple dataflow."""
        subtitle = Text("Part 1 Circuit: Two-Register Dataflow").scale(self.SCALE_SUBTITLE)
        subtitle.next_to(title, DOWN)
        self.play(Write(subtitle))
        self.wait(self.STANDARD_WAIT)
        
        # Create dataflow diagram
        # Input: digit stream
        input_box = Rectangle(height=0.6, width=1.5, color=YELLOW)
        input_box.shift(LEFT * 4 + UP * 1.5)
        input_label = Text("digit", color=WHITE).scale(self.SCALE_TINY).move_to(input_box)
        
        self.play(Create(input_box), Write(input_label))
        
        # Registers
        unfin_reg = Rectangle(height=0.8, width=1.2, color=self.COLOR_TENS)
        unfin_reg.shift(LEFT * 1.5 + UP * 0.5)
        unfin_label = Text("unfinished", color=WHITE).scale(self.SCALE_TINY).move_to(unfin_reg)
        
        fin_reg = Rectangle(height=0.8, width=1.2, color=self.COLOR_ONES)
        fin_reg.shift(LEFT * 1.5 + DOWN * 0.8)
        fin_label = Text("finished", color=WHITE).scale(self.SCALE_TINY).move_to(fin_reg)
        
        self.play(Create(unfin_reg), Write(unfin_label))
        self.play(Create(fin_reg), Write(fin_label))
        self.wait(self.STANDARD_WAIT)
        
        # Computation blocks
        use_tens_box = Rectangle(height=0.6, width=1.0, color=BLUE)
        use_tens_box.shift(RIGHT * 1.0 + UP * 1.5)
        use_tens_label = Text("x10", color=WHITE).scale(self.SCALE_TINY).move_to(use_tens_box)
        
        use_ones_box = Rectangle(height=0.6, width=1.0, color=BLUE)
        use_ones_box.shift(RIGHT * 1.0 + DOWN * 0.2)
        use_ones_label = Text("+", color=WHITE).scale(self.SCALE_TINY).move_to(use_ones_box)
        
        self.play(Create(use_tens_box), Write(use_tens_label))
        self.play(Create(use_ones_box), Write(use_ones_label))
        
        # Max blocks
        max_unfin = Rectangle(height=0.6, width=0.8, color=GREEN)
        max_unfin.shift(RIGHT * 3.0 + UP * 0.5)
        max_unfin_label = Text("MAX", color=WHITE).scale(self.SCALE_TINY).move_to(max_unfin)
        
        max_fin = Rectangle(height=0.6, width=0.8, color=GREEN)
        max_fin.shift(RIGHT * 3.0 + DOWN * 0.8)
        max_fin_label = Text("MAX", color=WHITE).scale(self.SCALE_TINY).move_to(max_fin)
        
        self.play(Create(max_unfin), Write(max_unfin_label))
        self.play(Create(max_fin), Write(max_fin_label))
        self.wait(self.STANDARD_WAIT)
        
        # Arrows showing dataflow
        arrows = VGroup(
            Arrow(input_box.get_right(), use_tens_box.get_left(), buff=0.1, color=YELLOW, stroke_width=2),
            Arrow(input_box.get_right(), use_ones_box.get_left(), buff=0.1, color=YELLOW, stroke_width=2),
            Arrow(unfin_reg.get_right(), use_ones_box.get_left(), buff=0.1, color=self.COLOR_TENS, stroke_width=2),
            Arrow(use_tens_box.get_right(), max_unfin.get_left(), buff=0.1, color=BLUE, stroke_width=2),
            Arrow(unfin_reg.get_right(), max_unfin.get_left(), buff=0.1, color=self.COLOR_TENS, stroke_width=2),
            Arrow(use_ones_box.get_right(), max_fin.get_left(), buff=0.1, color=BLUE, stroke_width=2),
            Arrow(fin_reg.get_right(), max_fin.get_left(), buff=0.1, color=self.COLOR_ONES, stroke_width=2),
            Arrow(max_unfin.get_left(), unfin_reg.get_right(), buff=0.1, color=GREEN, stroke_width=2),
            Arrow(max_fin.get_left(), fin_reg.get_right(), buff=0.1, color=GREEN, stroke_width=2)
        )
        
        self.play(Create(arrows), run_time=2)
        self.wait(self.LONG_WAIT)
        
        # Summary
        summary = Text("1 cycle per digit, O(1) hardware", color=GREEN).scale(self.SCALE_SMALL)
        summary.shift(DOWN * 2.2)
        self.play(Write(summary))
        self.wait(self.EXTENDED_WAIT)
        
        self.play(FadeOut(VGroup(
            subtitle, input_box, input_label, unfin_reg, unfin_label, fin_reg, fin_label,
            use_tens_box, use_tens_label, use_ones_box, use_ones_label,
            max_unfin, max_unfin_label, max_fin, max_fin_label, arrows, summary
        )))
    
    def circuit_part2(self, title: Text) -> None:
        """Show Part 2 hardware: streaming monotonic stack."""
        subtitle = Text("Part 2 Circuit: Streaming Stack").scale(self.SCALE_SUBTITLE)
        subtitle.next_to(title, DOWN)
        self.play(Write(subtitle))
        self.wait(self.STANDARD_WAIT)
        
        # Concept
        concept = Text("While top < d and room remains: POP; then PUSH if space", color=YELLOW).scale(self.SCALE_TEXT)
        concept.shift(UP * 1.6)
        self.play(Write(concept))
        
        # Draw stack registers
        stack_regs = VGroup(*[
            Rectangle(height=0.4, width=0.6, color=self.COLOR_REGISTER).shift(LEFT*2 + DOWN* (i*0.5))
            for i in range(6)
        ])
        stack_regs.shift(UP * 0.5)
        
        stack_labels = VGroup(*[
            Text(f"s{i}", color=WHITE).scale(self.SCALE_TINY).move_to(stack_regs[i])
            for i in range(len(stack_regs))
        ])
        
        sp = Text("sp", color=GREEN).scale(self.SCALE_TINY).next_to(stack_regs, LEFT, buff=0.3)
        
        self.play(Create(stack_regs), Write(stack_labels), Write(sp))
        
        # Input digit and comparator
        digit_box = Rectangle(height=0.6, width=1.2, color=YELLOW).shift(RIGHT * 2 + UP * 0.5)
        digit_label = Text("digit d", color=WHITE).scale(self.SCALE_TINY).move_to(digit_box)
        self.play(Create(digit_box), Write(digit_label))
        
        comp = Rectangle(height=0.6, width=0.8, color=self.COLOR_COMPARATOR).shift(RIGHT * 0.0 + UP * 0.5)
        comp_label = Text("< ?", color=WHITE).scale(self.SCALE_TINY).move_to(comp)
        self.play(Create(comp), Write(comp_label))
        
        # Arrows
        arrows = VGroup(
            Arrow(stack_regs[0].get_right(), comp.get_left(), buff=0.1, color=BLUE, stroke_width=2),
            Arrow(digit_box.get_left(), comp.get_right(), buff=0.1, color=YELLOW, stroke_width=2),
        )
        self.play(Create(arrows))
        
        pop_logic = Text("POP if top < d and enough slots left", color=GREEN).scale(self.SCALE_TINY)
        pop_logic.shift(DOWN * 1.4)
        push_logic = Text("PUSH if stack not full", color=GREEN).scale(self.SCALE_TINY)
        push_logic.next_to(pop_logic, DOWN, buff=0.2)
        self.play(Write(pop_logic), Write(push_logic))
        
        # Output
        out_box = Rectangle(height=0.6, width=1.6, color=GREEN).shift(RIGHT * 4 + DOWN * 0.5)
        out_label = Text("result concat", color=WHITE).scale(self.SCALE_TINY).move_to(out_box)
        out_arrow = Arrow(stack_regs.get_right(), out_box.get_left(), buff=0.1, color=GREEN, stroke_width=2)
        self.play(Create(out_arrow), Create(out_box), Write(out_label))
        self.wait(self.LONG_WAIT)
        
        # Complexity note
        complexity = Text("1 digit/cycle, O(k) storage, tiny area", color=BLUE).scale(self.SCALE_TINY)
        complexity.shift(DOWN * 2.5)
        self.play(Write(complexity))
        self.wait(self.EXTENDED_WAIT)
        
        self.play(FadeOut(VGroup(
            subtitle, concept, stack_regs, stack_labels, sp, digit_box, digit_label,
            comp, comp_label, arrows, pop_logic, push_logic, out_box, out_label, out_arrow, complexity
        )))
    
    def circuit_summary(self, title: Text) -> None:
        """Show performance summary."""
        subtitle = Text("Performance Summary").scale(self.SCALE_SUBTITLE)
        subtitle.next_to(title, DOWN)
        self.play(Write(subtitle))
        self.wait(self.STANDARD_WAIT)
        
        # Create comparison table
        table_title = Text("Hardware Comparison").scale(self.SCALE_TEXT)
        table_title.shift(UP * 1.5)
        self.play(Write(table_title))
        
        # Part 1 box
        part1_box = Rectangle(height=2.0, width=3.0, color=self.COLOR_PART1)
        part1_box.set_fill(self.COLOR_PART1, opacity=0.1)
        part1_box.shift(LEFT * 2.5 + DOWN * 0.5)
        
        part1_title = Text("Part 1 (k=2)", color=self.COLOR_PART1).scale(self.SCALE_SMALL)
        part1_title.next_to(part1_box, UP, buff=0.1)
        
        part1_stats = VGroup(
            Text("Latency: n cycles", color=WHITE).scale(self.SCALE_TINY),
            Text("Hardware: O(1)", color=WHITE).scale(self.SCALE_TINY),
            Text("LUTs: ~50", color=WHITE).scale(self.SCALE_TINY),
            Text("Freq: 400 MHz", color=WHITE).scale(self.SCALE_TINY)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        part1_stats.move_to(part1_box)
        
        self.play(Create(part1_box), Write(part1_title))
        self.play(Write(part1_stats))
        self.wait(self.STANDARD_WAIT)
        
        # Part 2 box
        part2_box = Rectangle(height=2.0, width=3.0, color=self.COLOR_PART2)
        part2_box.set_fill(self.COLOR_PART2, opacity=0.1)
        part2_box.shift(RIGHT * 2.5 + DOWN * 0.5)
        
        part2_title = Text("Part 2 (k=12)", color=self.COLOR_PART2).scale(self.SCALE_SMALL)
        part2_title.next_to(part2_box, UP, buff=0.1)
        
        part2_stats = VGroup(
            Text("Latency: n cycles (1 per digit)", color=WHITE).scale(self.SCALE_TINY),
            Text("Hardware: O(k) storage", color=WHITE).scale(self.SCALE_TINY),
            Text("LUTs: ~200 (k=12)", color=WHITE).scale(self.SCALE_TINY),
            Text("Freq: 400+ MHz", color=WHITE).scale(self.SCALE_TINY)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        part2_stats.move_to(part2_box)
        
        self.play(Create(part2_box), Write(part2_title))
        self.play(Write(part2_stats))
        self.wait(self.LONG_WAIT)
        
        # Conclusion
        conclusion = Text("Part 1: Simple and fast. Part 2: Parallel sorting tradeoff", color=GREEN).scale(self.SCALE_SMALL)
        conclusion.shift(DOWN * 2.5)
        self.play(Write(conclusion))
        self.wait(self.EXTENDED_WAIT)
