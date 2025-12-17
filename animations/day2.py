"""
Day 2: Gift Shop Invalid IDs Animation - Advent of Code 2025

This animation demonstrates the "Invalid Product IDs" problem in three main scenes:
1. Problem Scene: Visual demonstration of pattern repetition detection
2. Algorithm Scene: Detailed explanation of mathematical formula and optimization
3. Circuit Scene: Hardware implementation for computing invalid ID sums

STYLE PREFERENCES:
================================================================================
CODE BLOCKS:
- Use VGroup with styled Text (Monospace font, GRAY color) + SurroundingRectangle
- Avoid Manim's Code class due to compatibility issues with certain parameters

LAYOUT:
- Use ABSOLUTE positioning (e.g., shift(DOWN*2.5)) to prevent overflow
- Avoid relative positioning that can push elements off-screen

VISUALIZATION:
- Show pattern repetition visually with colored segments
- Animate the transformation from half to full invalid ID
- Use color coding consistently (pattern=BLUE, repetition=RED)

CIRCUIT DATAFLOW:
- Show mathematical computation paths (multiplication, division)
- Emphasize arithmetic sum formulas
- Demonstrate range iteration and accumulation
================================================================================
"""

from manim import *
import numpy as np
from typing import List, Tuple, Optional, Union


class Day2(Scene):
    # ========== VISUAL CONSTANTS ==========
    
    # Timing configuration (in seconds)
    FLASH_DURATION = 0.15
    STANDARD_WAIT = 0.5
    LONG_WAIT = 1.5
    EXTENDED_WAIT = 2.0
    
    # Colors - consistent color scheme
    COLOR_PATTERN = BLUE
    COLOR_REPEAT = RED
    COLOR_VALID = GREEN
    COLOR_INVALID = RED
    COLOR_RANGE = YELLOW
    COLOR_SUM = PURPLE
    COLOR_CODE = GRAY
    COLOR_COMPUTE_BOX = BLUE
    COLOR_HALF = ORANGE
    COLOR_FULL = PINK
    
    # Text scales
    SCALE_TITLE = 0.8
    SCALE_SUBTITLE = 0.6
    SCALE_TEXT = 0.5
    SCALE_SMALL = 0.4
    SCALE_TINY = 0.3
    SCALE_CODE = 0.25
    
    def construct(self) -> None:
        """Main entry point - orchestrates all three scenes."""
        self.scene_problem()
        self.clear()
        self.scene_algorithm()
        self.clear()
        self.scene_circuit()
    
    # ========== HELPER FUNCTIONS FOR VISUAL CONSISTENCY ==========
    
    def create_code_block(self, lines: List[str], scale: Optional[float] = None) -> Tuple[VGroup, SurroundingRectangle]:
        """
        Create a styled code block using VGroup and Text.
        
        Args:
            lines: List of strings, each representing a line of code
            scale: Scale factor for the text (default: self.SCALE_CODE)
            
        Returns:
            Tuple of (code_lines VGroup, code_box Rectangle)
        """
        if scale is None:
            scale = self.SCALE_CODE
            
        code_lines = VGroup(*[
            Text(line, font="Monospace", color=self.COLOR_CODE).scale(scale)
            for line in lines
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        
        code_box = SurroundingRectangle(code_lines, color=self.COLOR_CODE, buff=0.15)
        
        return code_lines, code_box
    
    def create_digit_blocks(self, number: str, colors: Optional[List[str]] = None) -> VGroup:
        """
        Create visual blocks for each digit in a number.
        
        Args:
            number: String representation of the number
            colors: Optional list of colors for each digit
            
        Returns:
            VGroup containing digit blocks
        """
        if colors is None:
            colors = [WHITE] * len(number)
        
        blocks = VGroup()
        for i, (digit, color) in enumerate(zip(number, colors)):
            square = Square(side_length=0.5, color=color, fill_opacity=0.3)
            text = Text(digit, color=WHITE).scale(0.4).move_to(square)
            block = VGroup(square, text)
            blocks.add(block)
        
        blocks.arrange(RIGHT, buff=0.05)
        return blocks
    
    # ========== SCENE 1: PROBLEM DEMONSTRATION ==========
    
    def scene_problem(self) -> None:
        """
        First scene: Demonstrate the invalid ID pattern detection.
        
        Shows:
        - What makes an ID invalid (repeated patterns)
        - Examples of valid vs invalid IDs
        - Part 1: exact double repetition (11, 6464, 123123)
        - Part 2: any number of repetitions (111, 123123123, etc.)
        """
        title = Text("Day 2: Gift Shop Invalid IDs").scale(self.SCALE_TITLE).to_edge(UP)
        self.play(Write(title))
        self.wait(self.STANDARD_WAIT)
        
        # Introduction
        intro = Text("Find numbers where a pattern repeats (like 55 or 1212)").scale(self.SCALE_TEXT)
        intro.next_to(title, DOWN, buff=0.5)
        self.play(Write(intro))
        self.wait(self.LONG_WAIT)
        
        # Show Part 1 criteria
        self.problem_part1(title, intro)
        
        # Show Part 2 criteria
        self.problem_part2(title)
    
    def problem_part1(self, title: Text, intro: Text) -> None:
        """Demonstrate Part 1: exactly two repetitions."""
        p1_title = Text("Part 1: Pattern Appears Twice").scale(self.SCALE_SUBTITLE)
        p1_title.next_to(intro, DOWN, buff=0.5)
        self.play(Write(p1_title))
        self.wait(self.STANDARD_WAIT)
        
        # Example 1: 55 (5 repeated twice)
        ex1_label = Text("Example: 55", color=self.COLOR_INVALID).scale(self.SCALE_TEXT)
        ex1_label.to_edge(LEFT).shift(UP*0.5)
        self.play(Write(ex1_label))
        
        # Visual breakdown
        digits_55 = self.create_digit_blocks("55", [self.COLOR_PATTERN, self.COLOR_REPEAT])
        digits_55.next_to(ex1_label, DOWN, buff=0.3)
        self.play(FadeIn(digits_55))
        
        # Annotate the pattern
        brace1 = Brace(digits_55[0], DOWN, color=self.COLOR_PATTERN)
        text1 = Text("Pattern: 5", color=self.COLOR_PATTERN).scale(self.SCALE_SMALL)
        text1.next_to(brace1, DOWN)
        
        brace2 = Brace(digits_55[1], DOWN, color=self.COLOR_REPEAT)
        text2 = Text("Repeat: 5", color=self.COLOR_REPEAT).scale(self.SCALE_SMALL)
        text2.next_to(brace2, DOWN)
        
        self.play(Create(brace1), Write(text1))
        self.play(Create(brace2), Write(text2))
        self.wait(self.LONG_WAIT)
        
        # Example 2: 6464 (64 repeated twice)
        ex2_label = Text("Example: 6464", color=self.COLOR_INVALID).scale(self.SCALE_TEXT)
        ex2_label.shift(RIGHT*2 + UP*0.5)
        self.play(Write(ex2_label))
        
        colors_6464 = [self.COLOR_PATTERN, self.COLOR_PATTERN, self.COLOR_REPEAT, self.COLOR_REPEAT]
        digits_6464 = self.create_digit_blocks("6464", colors_6464)
        digits_6464.next_to(ex2_label, DOWN, buff=0.3)
        self.play(FadeIn(digits_6464))
        
        brace3 = Brace(VGroup(digits_6464[0], digits_6464[1]), DOWN, color=self.COLOR_PATTERN)
        text3 = Text("Pattern: 64", color=self.COLOR_PATTERN).scale(self.SCALE_SMALL)
        text3.next_to(brace3, DOWN)
        
        brace4 = Brace(VGroup(digits_6464[2], digits_6464[3]), DOWN, color=self.COLOR_REPEAT)
        text4 = Text("Repeat: 64", color=self.COLOR_REPEAT).scale(self.SCALE_SMALL)
        text4.next_to(brace4, DOWN)
        
        self.play(Create(brace3), Write(text3))
        self.play(Create(brace4), Write(text4))
        self.wait(self.LONG_WAIT)
        
        # Example 3: 123123 (123 repeated twice)
        ex3_label = Text("Example: 123123", color=self.COLOR_INVALID).scale(self.SCALE_TEXT)
        ex3_label.to_edge(LEFT).shift(DOWN*1.2)
        self.play(Write(ex3_label))
        
        colors_123123 = [self.COLOR_PATTERN] * 3 + [self.COLOR_REPEAT] * 3
        digits_123123 = self.create_digit_blocks("123123", colors_123123)
        digits_123123.next_to(ex3_label, DOWN, buff=0.3)
        self.play(FadeIn(digits_123123))
        
        brace5 = Brace(VGroup(*digits_123123[0:3]), DOWN, color=self.COLOR_PATTERN)
        text5 = Text("Pattern: 123", color=self.COLOR_PATTERN).scale(self.SCALE_SMALL)
        text5.next_to(brace5, DOWN)
        
        brace6 = Brace(VGroup(*digits_123123[3:6]), DOWN, color=self.COLOR_REPEAT)
        text6 = Text("Repeat: 123", color=self.COLOR_REPEAT).scale(self.SCALE_SMALL)
        text6.next_to(brace6, DOWN)
        
        self.play(Create(brace5), Write(text5))
        self.play(Create(brace6), Write(text6))
        self.wait(self.EXTENDED_WAIT)
        
        # Show the formula
        formula = MathTex(r"\text{Invalid ID} = \text{half} \times 10^n + \text{half}")
        formula.scale(self.SCALE_TEXT).shift(RIGHT*1.5 + DOWN*1.2)
        formula_box = SurroundingRectangle(formula, color=self.COLOR_INVALID, buff=0.2)
        
        self.play(Write(formula), Create(formula_box))
        self.wait(self.EXTENDED_WAIT)
        
        # Clear for Part 2
        self.play(
            FadeOut(VGroup(
                intro, p1_title, ex1_label, digits_55, brace1, text1, brace2, text2,
                ex2_label, digits_6464, brace3, text3, brace4, text4,
                ex3_label, digits_123123, brace5, text5, brace6, text6,
                formula, formula_box
            ))
        )
    
    def problem_part2(self, title: Text) -> None:
        """Demonstrate Part 2: any number of repetitions."""
        p2_title = Text("Part 2: Pattern Repeats 2+ Times").scale(self.SCALE_SUBTITLE)
        p2_title.next_to(title, DOWN, buff=0.5)
        self.play(Write(p2_title))
        self.wait(self.STANDARD_WAIT)
        
        # Example 1: 111 (1 repeated three times)
        ex1_label = Text("Example: 111", color=self.COLOR_INVALID).scale(self.SCALE_TEXT)
        ex1_label.to_edge(LEFT).shift(UP*0.5)
        self.play(Write(ex1_label))
        
        colors_111 = [self.COLOR_PATTERN, self.COLOR_REPEAT, self.COLOR_REPEAT]
        digits_111 = self.create_digit_blocks("111", colors_111)
        digits_111.next_to(ex1_label, DOWN, buff=0.3)
        self.play(FadeIn(digits_111))
        
        annot_111 = Text("1 repeated 3 times", color=self.COLOR_INVALID).scale(self.SCALE_SMALL)
        annot_111.next_to(digits_111, DOWN, buff=0.3)
        self.play(Write(annot_111))
        self.wait(self.LONG_WAIT)
        
        # Example 2: 12341234 (1234 repeated twice - still invalid!)
        ex2_label = Text("Example: 12341234", color=self.COLOR_INVALID).scale(self.SCALE_TEXT)
        ex2_label.shift(RIGHT*1.5 + UP*0.5)
        self.play(Write(ex2_label))
        
        colors_12341234 = [self.COLOR_PATTERN] * 4 + [self.COLOR_REPEAT] * 4
        digits_12341234 = self.create_digit_blocks("12341234", colors_12341234)
        digits_12341234.next_to(ex2_label, DOWN, buff=0.3)
        self.play(FadeIn(digits_12341234))
        
        annot_12341234 = Text("1234 repeated 2 times", color=self.COLOR_INVALID).scale(self.SCALE_SMALL)
        annot_12341234.next_to(digits_12341234, DOWN, buff=0.3)
        self.play(Write(annot_12341234))
        self.wait(self.LONG_WAIT)
        
        # Example 3: 123123123 (123 repeated three times)
        ex3_label = Text("Example: 123123123", color=self.COLOR_INVALID).scale(self.SCALE_TEXT)
        ex3_label.to_edge(LEFT).shift(DOWN*1.0)
        self.play(Write(ex3_label))
        
        colors_123123123 = [self.COLOR_PATTERN] * 3 + [self.COLOR_REPEAT] * 6
        digits_123123123 = self.create_digit_blocks("123123123", colors_123123123)
        digits_123123123.next_to(ex3_label, DOWN, buff=0.3)
        self.play(FadeIn(digits_123123123))
        
        annot_123123123 = Text("123 repeated 3 times", color=self.COLOR_INVALID).scale(self.SCALE_SMALL)
        annot_123123123.next_to(digits_123123123, DOWN, buff=0.3)
        self.play(Write(annot_123123123))
        self.wait(self.EXTENDED_WAIT)
        
        # Show key insight
        insight = VGroup(
            Text("Rule: Total digits / pattern length must be a whole number", color=YELLOW).scale(self.SCALE_SMALL),
            Text("And the pattern must show up at least twice", color=YELLOW).scale(self.SCALE_SMALL)
        ).arrange(DOWN, buff=0.2).shift(DOWN*2.8)
        insight_box = SurroundingRectangle(insight, color=YELLOW, buff=0.2)
        
        self.play(Create(insight_box), Write(insight))
        self.wait(self.EXTENDED_WAIT)
    
    # ========== SCENE 2: ALGORITHM EXPLANATION ==========
    
    def scene_algorithm(self) -> None:
        """
        Second scene: Explain the algorithm for both parts.
        
        Covers:
        - Part 1: Mathematical formula for invalid IDs
        - Computing sum over a range
        - Part 2: Extended to multiple repetitions
        - Arithmetic series optimization
        """
        title = Text("The Algorithm").scale(self.SCALE_TITLE).to_edge(UP)
        self.play(Write(title))
        self.wait(self.STANDARD_WAIT)
        
        # Part 1 Algorithm
        self.algorithm_part1(title)
        
        # Sum formula
        self.algorithm_sum_formula(title)
        
        # Part 2 Extension
        self.algorithm_part2(title)
    
    def algorithm_part1(self, title: Text) -> None:
        """Explain Part 1 algorithm."""
        p1_title = Text("Part 1: Finding Invalid IDs").scale(self.SCALE_SUBTITLE)
        p1_title.next_to(title, DOWN)
        self.play(Write(p1_title))
        self.wait(self.STANDARD_WAIT)
        
        # Show the transformation
        transform_label = Text("From half to full invalid ID:").scale(self.SCALE_TEXT)
        transform_label.to_edge(LEFT).shift(UP*1.0)
        self.play(Write(transform_label))
        
        # Example: 64 -> 6464
        half_64 = self.create_digit_blocks("64", [self.COLOR_HALF, self.COLOR_HALF])
        half_64.next_to(transform_label, DOWN, buff=0.4).shift(LEFT*1.5)
        half_label = Text("half = 64", color=self.COLOR_HALF).scale(self.SCALE_SMALL)
        half_label.next_to(half_64, DOWN)
        
        self.play(FadeIn(half_64), Write(half_label))
        self.wait(self.STANDARD_WAIT)
        
        # Arrow
        arrow = Arrow(half_64.get_right(), half_64.get_right() + RIGHT * 2, color=WHITE)
        self.play(Create(arrow))
        
        # Full invalid ID
        full_6464 = self.create_digit_blocks("6464", [self.COLOR_FULL] * 4)
        full_6464.next_to(arrow, RIGHT, buff=0.5)
        full_label = Text("invalid = 6464", color=self.COLOR_FULL).scale(self.SCALE_SMALL)
        full_label.next_to(full_6464, DOWN)
        
        self.play(FadeIn(full_6464), Write(full_label))
        self.wait(self.LONG_WAIT)
        
        # Show the formula
        formula_text = MathTex(
            r"\text{invalid} &= \text{half} \times 10^{\text{digits}} + \text{half}\\\\",
            r"&= \text{half} \times (10^{\text{digits}} + 1)\\\\",
            r"&= 64 \times (10^2 + 1)\\\\",
            r"&= 64 \times 101\\\\",
            r"&= 6464"
        ).scale(self.SCALE_SMALL)
        formula_text.shift(RIGHT*2.5 + UP*1.0)
        
        for i in range(len(formula_text)):
            self.play(Write(formula_text[i]))
            self.wait(0.5)
        
        self.wait(self.EXTENDED_WAIT)
        
        # Clear
        self.play(
            FadeOut(VGroup(
                p1_title, transform_label, half_64, half_label, arrow,
                full_6464, full_label, formula_text
            ))
        )
    
    def algorithm_sum_formula(self, title: Text) -> None:
        """Show the sum formula over a range."""
        sum_title = Text("Computing the Sum Over a Range").scale(self.SCALE_SUBTITLE)
        sum_title.next_to(title, DOWN)
        self.play(Write(sum_title))
        self.wait(self.STANDARD_WAIT)
        
        # Show example range
        range_label = Text("Example: Sum invalid IDs in range [11, 22]").scale(self.SCALE_TEXT)
        range_label.to_edge(LEFT).shift(UP*1.0)
        self.play(Write(range_label))
        
        # List the invalid IDs
        invalid_list = VGroup(
            Text("11 = 1 x 11", color=self.COLOR_INVALID).scale(self.SCALE_SMALL),
            Text("22 = 2 x 11", color=self.COLOR_INVALID).scale(self.SCALE_SMALL)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        invalid_list.next_to(range_label, DOWN, buff=0.5)
        
        for item in invalid_list:
            self.play(Write(item))
            self.wait(0.3)
        
        # Sum them
        sum_calc = MathTex(
            r"\text{Sum} &= 11 + 22\\",
            r"&= 1 \times 11 + 2 \times 11\\",
            r"&= (1 + 2) \times 11\\",
            r"&= 3 \times 11\\",
            r"&= 33"
        ).scale(self.SCALE_SMALL)
        sum_calc.next_to(invalid_list, DOWN, buff=0.5)
        
        for i in range(len(sum_calc)):
            self.play(Write(sum_calc[i]))
            self.wait(0.5)
        
        self.wait(self.LONG_WAIT)
        
        # General formula
        general_label = Text("General Formula:").scale(self.SCALE_TEXT)
        general_label.next_to(sum_calc, DOWN, buff=0.5)
        self.play(Write(general_label))
        
        general_formula = MathTex(
            r"\text{Sum} = \left(\sum_{h=\text{low}}^{\text{high}} h\right) \times (10^n + 1)"
        ).scale(self.SCALE_SMALL)
        general_formula.next_to(general_label, DOWN, buff=0.3)
        self.play(Write(general_formula))
        self.wait(self.STANDARD_WAIT)
        
        # Arithmetic series
        arith_formula = MathTex(
            r"\sum_{h=a}^{b} h = \frac{(b-a+1)(a+b)}{2}"
        ).scale(self.SCALE_SMALL)
        arith_formula.next_to(general_formula, DOWN, buff=0.3)
        arith_box = SurroundingRectangle(arith_formula, color=GREEN, buff=0.15)
        
        self.play(Write(arith_formula), Create(arith_box))
        self.wait(self.EXTENDED_WAIT)
        
        # Clear
        self.play(
            FadeOut(VGroup(
                sum_title, range_label, invalid_list, sum_calc,
                general_label, general_formula, arith_formula, arith_box
            ))
        )
    
    def algorithm_part2(self, title: Text) -> None:
        """Explain Part 2 extension."""
        p2_title = Text("Part 2: Multiple Repetitions").scale(self.SCALE_SUBTITLE)
        p2_title.next_to(title, DOWN)
        self.play(Write(p2_title))
        self.wait(self.STANDARD_WAIT)
        
        # Show the key difference
        diff_label = Text("Now we must check ALL possible pattern lengths").scale(self.SCALE_TEXT)
        diff_label.to_edge(LEFT).shift(UP*1.0)
        self.play(Write(diff_label))
        
        # Example: Number 111
        ex_label = Text("Example: 111").scale(self.SCALE_TEXT)
        ex_label.next_to(diff_label, DOWN, buff=0.5)
        self.play(Write(ex_label))
        
        # Show different interpretations
        interp1 = Text("Pattern length 1: '1' repeated 3 times - YES", color=GREEN).scale(self.SCALE_SMALL)
        interp1.next_to(ex_label, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(Write(interp1))
        self.wait(self.STANDARD_WAIT)
        
        interp2 = Text("Pattern length 3: '111' repeated 1 time - NO", color=RED).scale(self.SCALE_SMALL)
        interp2.next_to(interp1, DOWN, buff=0.2, aligned_edge=LEFT)
        self.play(Write(interp2))
        self.wait(self.LONG_WAIT)
        
        # Algorithm approach
        approach_label = Text("Algorithm: Try all divisors of total length").scale(self.SCALE_TEXT)
        approach_label.next_to(interp2, DOWN, buff=0.5)
        approach_box = SurroundingRectangle(approach_label, color=YELLOW, buff=0.15)
        self.play(Create(approach_box), Write(approach_label))
        self.wait(self.STANDARD_WAIT)
        
        # Show code
        code_lines, code_box = self.create_code_block([
            "for pattern_len in divisors(total_len):",
            "    if total_len / pattern_len >= 2:",
            "        # Check if pattern repeats",
            "        if is_repeating(num, pattern_len):",
            "            mark as invalid",
            "            break  # Only count once"
        ], scale=self.SCALE_SMALL)
        code_group = VGroup(code_lines, code_box)
        code_group.next_to(approach_label, DOWN, buff=0.5)
        
        self.play(Create(code_box), Write(code_lines))
        self.wait(self.EXTENDED_WAIT)
    
    # ========== SCENE 3: CIRCUIT IMPLEMENTATION ==========
    
    def scene_circuit(self) -> None:
        """
        Third scene: Show the hardware circuit implementation.
        
        Demonstrates:
        - Arithmetic computation units (multiply, add, divide)
        - Range iteration logic
        - Accumulator for sum
        - Complete dataflow for one iteration
        """
        title = Text("The Hardware Circuit").scale(self.SCALE_TITLE).to_edge(UP)
        self.play(Write(title))
        self.wait(self.STANDARD_WAIT)
        
        # Build circuit
        range_group = self.circuit_stage_range(title)
        compute_group = self.circuit_stage_compute(title, range_group)
        sum_group = self.circuit_stage_accumulator(title, compute_group)
        
        # Dataflow demo
        self.circuit_dataflow_demo(title, range_group, compute_group, sum_group)
    
    def circuit_stage_range(self, title: Text) -> VGroup:
        """Stage 1: Range iteration."""
        stage_title = Text("Stage 1: Range Iterator").scale(self.SCALE_SUBTITLE)
        stage_title.next_to(title, DOWN)
        self.play(Write(stage_title))
        
        # Range bounds
        range_box = RoundedRectangle(height=1.5, width=2.5, corner_radius=0.2, color=self.COLOR_RANGE)
        range_box.set_fill(self.COLOR_RANGE, opacity=0.2)
        range_label = Text("Range\nIterator").scale(self.SCALE_SMALL).move_to(range_box).shift(UP*0.3)
        range_values = Text("low -> high").scale(self.SCALE_TINY).move_to(range_box).shift(DOWN*0.3)
        range_group = VGroup(range_box, range_label, range_values).to_edge(LEFT).shift(UP*0.3)
        
        self.play(FadeIn(range_group))
        
        expl = Text("Iterate through 'half' values\nthat produce invalid IDs in range").scale(self.SCALE_CODE)
        expl.next_to(range_group, DOWN, buff=0.3)
        self.play(Write(expl))
        self.wait(self.LONG_WAIT)
        
        self.play(FadeOut(expl), FadeOut(stage_title))
        return range_group
    
    def circuit_stage_compute(self, title: Text, range_group: VGroup) -> VGroup:
        """Stage 2: Compute invalid ID from half."""
        stage_title = Text("Stage 2: Compute Invalid ID").scale(self.SCALE_SUBTITLE)
        stage_title.next_to(title, DOWN)
        self.play(Write(stage_title))
        
        # Multiplier box
        mult_box = RoundedRectangle(height=1.8, width=2.5, corner_radius=0.2, color=self.COLOR_COMPUTE_BOX)
        mult_box.set_fill(self.COLOR_COMPUTE_BOX, opacity=0.2)
        mult_label = Text("Compute").scale(self.SCALE_SMALL).move_to(mult_box).shift(UP*0.5)
        mult_formula = MathTex(r"h \times (10^n + 1)").scale(0.35).move_to(mult_box).shift(DOWN*0.2)
        mult_group = VGroup(mult_box, mult_label, mult_formula).next_to(range_group, RIGHT, buff=2)
        
        self.play(FadeIn(mult_group))
        
        # Arrow from range to compute
        arrow = Arrow(range_group.get_right(), mult_group.get_left(), color=WHITE)
        arrow_label = Text("half").scale(self.SCALE_TINY).next_to(arrow, UP, buff=0.1)
        self.play(Create(arrow), Write(arrow_label))
        self.wait(self.LONG_WAIT)
        
        self.play(FadeOut(stage_title))
        return mult_group
    
    def circuit_stage_accumulator(self, title: Text, compute_group: VGroup) -> VGroup:
        """Stage 3: Sum accumulator."""
        stage_title = Text("Stage 3: Accumulate Sum").scale(self.SCALE_SUBTITLE)
        stage_title.next_to(title, DOWN)
        self.play(Write(stage_title))
        
        # Accumulator
        sum_box = RoundedRectangle(height=1.5, width=2, corner_radius=0.2, color=self.COLOR_SUM)
        sum_box.set_fill(self.COLOR_SUM, opacity=0.2)
        sum_label = Text("Sum\nAccumulator").scale(self.SCALE_SMALL).move_to(sum_box).shift(UP*0.3)
        sum_value = Text("0").scale(self.SCALE_TEXT).move_to(sum_box).shift(DOWN*0.3)
        sum_group = VGroup(sum_box, sum_label, sum_value).next_to(compute_group, RIGHT, buff=2)
        
        self.play(FadeIn(sum_group))
        
        # Arrow from compute to sum
        arrow = Arrow(compute_group.get_right(), sum_group.get_left(), color=WHITE)
        arrow_label = Text("invalid").scale(self.SCALE_TINY).next_to(arrow, UP, buff=0.1)
        self.play(Create(arrow), Write(arrow_label))
        self.wait(self.LONG_WAIT)
        
        self.play(FadeOut(stage_title))
        return sum_group
    
    def circuit_dataflow_demo(self, title: Text, range_group: VGroup, compute_group: VGroup, sum_group: VGroup) -> None:
        """Animate complete dataflow."""
        demo_title = Text("Complete Dataflow: Range [1, 2]").scale(self.SCALE_SUBTITLE)
        demo_title.next_to(title, DOWN)
        self.play(Write(demo_title))
        
        # Simulate processing half=1 -> invalid=11
        self.play(Flash(range_group[0], color=self.COLOR_RANGE))
        current_half = Text("half: 1", color=self.COLOR_HALF).scale(self.SCALE_TINY)
        current_half.next_to(range_group, DOWN, buff=0.2)
        self.play(Write(current_half))
        self.wait(self.STANDARD_WAIT)
        
        # Compute
        self.play(Flash(compute_group[0], color=self.COLOR_COMPUTE_BOX))
        computed = Text("1x11=11", color=self.COLOR_FULL).scale(self.SCALE_TINY)
        computed.next_to(compute_group, DOWN, buff=0.2)
        self.play(Write(computed))
        self.wait(self.STANDARD_WAIT)
        
        # Add to sum
        self.play(Flash(sum_group[0], color=self.COLOR_SUM))
        sum_group[2].become(Text("11").scale(self.SCALE_TEXT).move_to(sum_group[0]).shift(DOWN*0.3))
        self.wait(self.STANDARD_WAIT)
        
        # Process half=2 -> invalid=22
        self.play(FadeOut(current_half), FadeOut(computed))
        current_half = Text("half: 2", color=self.COLOR_HALF).scale(self.SCALE_TINY)
        current_half.next_to(range_group, DOWN, buff=0.2)
        self.play(Flash(range_group[0], color=self.COLOR_RANGE), Write(current_half))
        self.wait(self.STANDARD_WAIT)
        
        self.play(Flash(compute_group[0], color=self.COLOR_COMPUTE_BOX))
        computed = Text("2x11=22", color=self.COLOR_FULL).scale(self.SCALE_TINY)
        computed.next_to(compute_group, DOWN, buff=0.2)
        self.play(Write(computed))
        self.wait(self.STANDARD_WAIT)
        
        self.play(Flash(sum_group[0], color=self.COLOR_SUM))
        sum_group[2].become(Text("33").scale(self.SCALE_TEXT).move_to(sum_group[0]).shift(DOWN*0.3))
        self.wait(self.STANDARD_WAIT)
        
        # Final result
        result = Text("Final Sum: 33", color=GREEN).scale(self.SCALE_TEXT)
        result.next_to(sum_group, DOWN, buff=0.5)
        result_box = SurroundingRectangle(result, color=GREEN, buff=0.15)
        self.play(Create(result_box), Write(result))
        self.wait(self.EXTENDED_WAIT)
        
        # Summary
        summary = VGroup(
            Text("How the chip works:").scale(self.SCALE_SMALL),
            Text("1. Loop through half values (1, 2, 3...)").scale(self.SCALE_TINY),
            Text("2. Double each half to get full ID (64 -> 6464)").scale(self.SCALE_TINY),
            Text("3. Keep a running total").scale(self.SCALE_TINY),
            Text("4. Use a math shortcut to add ranges fast").scale(self.SCALE_TINY)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_corner(DL)
        
        self.play(Write(summary))
        self.wait(3)
