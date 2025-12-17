"""
Day 1: Safe Dial Animation - Advent of Code 2025

This animation demonstrates the "Safe Dial" problem in three main scenes:
1. Problem Scene: Visual demonstration of dial mechanics and instruction processing
2. Algorithm Scene: Detailed explanation of Part 1 (landing on zero) and Part 2 (crossing zero)
3. Circuit Scene: Hardware implementation showing dataflow architecture

STYLE PREFERENCES:
================================================================================
FLASH TIMING:
- Flashes occur BEFORE rotation animations for better synchronization
- Part 2 crossings: Flash at 0.15s, then rotate over 0.35s
- This ensures the flash is visibly synchronized with the arrow crossing zero

CODE BLOCKS:
- Use VGroup with styled Text (Monospace font, GRAY color) + SurroundingRectangle
- Avoid Manim's Code class due to compatibility issues with certain parameters
- Example pattern:
    code_lines = VGroup(*[Text(line, font="Monospace", color=GRAY).scale(0.4) for line in lines])
    code_box = SurroundingRectangle(code_lines, color=GRAY, buff=0.15)

FORMULAS:
- Show DIFFERENT formulas for LEFT vs RIGHT directions in Part 2
- RIGHT: ⌊(pos + mag) / 100⌋
- LEFT: ⌊(pos - 1) / 100⌋ - ⌊(pos - mag - 1) / 100⌋

LAYOUT:
- Use ABSOLUTE positioning (e.g., shift(DOWN*2.5)) to prevent overflow
- Avoid relative positioning that can push elements off-screen
- Test that "Why is this better" boxes fit within frame

CIRCUIT DATAFLOW:
- Show PARALLEL computation paths before mux selection
- Both LEFT and RIGHT paths receive position (ORANGE) and magnitude (YELLOW) inputs
- Direction mux selects between the two PRE-COMPUTED results
- Emphasize parallel processing: compute both, select one
- Feedback loop: mux output -> position register
================================================================================
"""

from manim import *
import numpy as np
from typing import List, Tuple, Optional, Any, Union


class Day1(Scene):
    # ========== VISUAL CONSTANTS ==========
    
    # Dial configuration
    DIAL_RADIUS = 2.5
    DEMO_DIAL_RADIUS = 1.5
    SIM_DIAL_RADIUS = 0.8
    TICK_SPACING = 5  # Tick marks every 5 units
    LABEL_SPACING = 10  # Labels every 10 units
    LONG_TICK_SPACING = 25
    TICK_LENGTH = 0.2
    LONG_TICK_LENGTH = 0.35
    
    # Timing configuration (in seconds)
    FLASH_DURATION = 0.15  # Flash before rotation
    ROTATION_DURATION = 0.35  # Rotation per crossing segment
    STANDARD_WAIT = 0.5
    LONG_WAIT = 1.5
    EXTENDED_WAIT = 2.0
    
    # Colors - following established color scheme
    COLOR_DIAL = BLUE
    COLOR_ARROW = RED
    COLOR_PART1 = GREEN
    COLOR_PART2 = YELLOW
    COLOR_DIRECTION = RED
    COLOR_POSITION = ORANGE
    COLOR_MAGNITUDE = YELLOW
    COLOR_MUX = PURPLE
    COLOR_CODE = GRAY
    COLOR_COMPUTE_BOX = BLUE
    COLOR_RIGHT = LIGHT_PINK
    COLOR_LEFT = TEAL
    COLOR_CHUNK = GREEN
    COLOR_MERGE = ORANGE
    COLOR_TREE = PURPLE
    
    # Text scales
    SCALE_TITLE = 0.8
    SCALE_SUBTITLE = 0.6
    SCALE_TEXT = 0.5
    SCALE_SMALL = 0.4
    SCALE_TINY = 0.3
    SCALE_CODE = 0.25
    
    def construct(self) -> None:
        """Main entry point - orchestrates all four scenes."""
        self.scene_problem()
        self.clear()
        self.scene_algorithm()
        self.clear()
        self.scene_circuit()
        self.clear()
        self.scene_parallel()
    
    # ========== HELPER FUNCTIONS FOR VISUAL CONSISTENCY ==========
    
    def create_dial(self, radius: float, center: np.ndarray = ORIGIN, include_labels: bool = True) -> VGroup:
        """
        Create a circular dial with tick marks and labels.
        
        Args:
            radius: Radius of the dial circle
            center: Center point of the dial (default: ORIGIN)
            include_labels: Whether to include numeric labels (default: True)
            
        Returns:
            VGroup containing circle, ticks, and optionally labels
            
        Note:
            - 0 is positioned at right (angle 0)
            - Values increase counterclockwise
            - Tick marks every 5 units, longer ticks every 25 units
            - Labels every 10 units
        """
        dial_circle = Circle(radius=radius, color=self.COLOR_DIAL).move_to(center)
        ticks = VGroup()
        labels = VGroup()
        
        for i in range(0, 100, self.TICK_SPACING):
            angle = -i * TAU / 100  # Negative for counterclockwise
            start = dial_circle.point_at_angle(angle)
            direction = (start - center)
            if np.linalg.norm(direction) > 0:
                direction = direction / np.linalg.norm(direction)
            else:
                direction = start / np.linalg.norm(start)
            
            # Longer ticks every 25 units
            length = self.LONG_TICK_LENGTH if i % self.LONG_TICK_SPACING == 0 else self.TICK_LENGTH
            end = start + direction * length
            ticks.add(Line(start, end, stroke_width=2, color=WHITE))
            
            # Labels every 10 units
            if include_labels and i % self.LABEL_SPACING == 0:
                label_scale = self.SCALE_SMALL if radius > 2 else self.SCALE_TINY
                lbl = Text(str(i)).scale(label_scale)
                lbl.move_to(start + direction * (length + 0.25))
                labels.add(lbl)
        
        if include_labels:
            return VGroup(dial_circle, ticks, labels)
        else:
            return VGroup(dial_circle, ticks)
    
    
    def create_arrow_pointer(self, dial_or_circle: Union[VGroup, Circle], position: int, center: np.ndarray = ORIGIN, stroke_width: int = 6) -> Arrow:
        """
        Create an arrow pointer for the dial.
        
        Args:
            dial_or_circle: The dial VGroup or Circle object to point on
            position: Current position on the dial (0-99)
            center: Center point of the dial
            stroke_width: Width of the arrow stroke
            
        Returns:
            Arrow object pointing to the specified position
        """
        angle = -position * TAU / 100
        if isinstance(dial_or_circle, VGroup):
            endpoint = dial_or_circle[0].point_at_angle(angle)
        else:
            endpoint = dial_or_circle.point_at_angle(angle)
        
        arrow = Arrow(center, endpoint, buff=0, color=self.COLOR_ARROW, stroke_width=stroke_width)
        return arrow
    
    def animate_dial_rotation(self, arrow: Arrow, dial_center: np.ndarray, position_tracker: ValueTracker,
                             direction: str, magnitude: int,
                             show_crossings: bool = False, p2_counter: Optional[ValueTracker] = None,
                             dial_radius: Optional[float] = None) -> int:
        """
        Animate the dial rotation with proper flash timing for crossings.
        
        Args:
            arrow: Arrow object to rotate
            dial_center: Center point of the dial
            position_tracker: ValueTracker for current position
            direction: "R" for right (clockwise) or "L" for left (counterclockwise)
            magnitude: Distance to move
            show_crossings: Whether to show flashes for zero crossings
            p2_counter: ValueTracker for Part 2 counter (optional)
            dial_radius: Radius of dial for flash positioning (optional)
            
        Returns:
            new_pos: The final position after rotation
        """
        current_pos = int(position_tracker.get_value())
        radius = dial_radius if dial_radius else self.DIAL_RADIUS
        
        # Calculate new position and crossings
        if direction == "R":
            new_pos = (current_pos + magnitude) % 100
            crossings = (current_pos + magnitude) // 100
        else:  # L
            new_pos = (current_pos - magnitude) % 100
            if magnitude >= current_pos:
                crossings = 1 + ((magnitude - current_pos - 1) // 100)
            else:
                crossings = 0
        
        # Calculate angle change
        if direction == "R":
            angle_change = -magnitude * TAU / 100  # Clockwise (negative)
        else:
            angle_change = magnitude * TAU / 100  # Counterclockwise (positive)
        
        # Animate with crossings
        if show_crossings and crossings > 0:
            # Flash before rotation for each crossing
            for i in range(crossings):
                if i > 0 or crossings > 0:
                    self.play(
                        Flash(dial_center + RIGHT * radius, color=self.COLOR_PART2, flash_radius=0.4),
                        run_time=self.FLASH_DURATION
                    )
                
                # Rotate one full loop (or remaining distance)
                segment_angle = min(100, magnitude - i * 100) * (TAU / 100)
                if direction == "L":
                    segment_angle = -segment_angle
                else:
                    segment_angle = -segment_angle
                    
                self.play(
                    Rotate(arrow, angle=segment_angle, about_point=dial_center),
                    run_time=self.ROTATION_DURATION
                )
            
            if p2_counter:
                p2_counter.set_value(p2_counter.get_value() + crossings)
        else:
            self.play(
                Rotate(arrow, angle=angle_change, about_point=dial_center),
                run_time=self.ROTATION_DURATION
            )
        
        return new_pos
    
    def create_code_block(self, lines: List[str], scale: Optional[float] = None) -> Tuple[VGroup, SurroundingRectangle]:
        """
        Create a styled code block using VGroup and Text.
        
        Args:
            lines: List of strings, each representing a line of code
            scale: Scale factor for the text (default: self.SCALE_CODE)
            
        Returns:
            Tuple of (code_lines VGroup, code_box Rectangle)
            
        Note:
            STYLE PREFERENCE: Use VGroup with Monospace Text instead of Code class
            - Avoids compatibility issues with Manim's Code class
            - Provides consistent gray-on-transparent styling
        """
        if scale is None:
            scale = self.SCALE_CODE
            
        code_lines = VGroup(*[
            Text(line, font="Monospace", color=self.COLOR_CODE).scale(scale)
            for line in lines
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        
        code_box = SurroundingRectangle(code_lines, color=self.COLOR_CODE, buff=0.15)
        
        return code_lines, code_box
    
    # ========== SCENE 1: PROBLEM DEMONSTRATION ==========
    
    def scene_problem(self) -> None:
        """
        First scene: Demonstrate the dial mechanics and instruction processing.
        
        Shows:
        - Circular dial with 0-99 positions
        - Arrow pointer starting at 50
        - Series of R/L instructions
        - Part 1 counter (lands on 0)
        - Part 2 counter (crosses 0)
        """
        title = Text("Day 1: Safe Dial").scale(self.SCALE_TITLE).to_edge(UP)
        self.play(Write(title))
        self.wait(self.STANDARD_WAIT)
        
        # Create main dial
        dial = self.create_dial(self.DIAL_RADIUS)
        self.play(Create(dial[0]), Create(dial[1]), FadeIn(dial[2]))
        self.wait(self.STANDARD_WAIT)
        
        # Arrow pointer starting at 50
        pos_tracker = ValueTracker(50)
        arrow = self.create_arrow_pointer(dial, 50)
        pos_label = always_redraw(
            lambda: Text(f"Position: {int(pos_tracker.get_value())}").scale(self.SCALE_TEXT)
            .next_to(dial, DOWN, buff=0.5)
        )
        
        self.play(Create(arrow), Write(pos_label))
        self.wait(self.STANDARD_WAIT)
        
        # Show starting position
        start_text = Text("Dial starts at 50").scale(self.SCALE_TEXT).next_to(dial, DOWN, buff=1.5)
        self.play(Write(start_text))
        self.wait(1)
        self.play(FadeOut(start_text))
        
        # Instructions list - examples including landing on 0 and multiple loops
        instructions = VGroup(
            Text("R 10"),
            Text("L 5"),
            Text("R 45"),  # Lands on 0 from position 55
            Text("R 105"),
            Text("L 50"),  # Crosses 0 once
            Text("R 200")  # Multiple loops
        ).scale(0.7).arrange(DOWN, aligned_edge=LEFT).to_edge(LEFT).shift(UP)
        
        # Part 1 and Part 2 counters with color coding
        p1_counter = ValueTracker(0)
        p2_counter = ValueTracker(0)
        p1_label = always_redraw(
            lambda: Text(f"Part 1 (lands on 0): {int(p1_counter.get_value())}", color=self.COLOR_PART1)
            .scale(self.SCALE_TEXT)
            .to_edge(RIGHT).shift(UP*2)
        )
        p2_label = always_redraw(
            lambda: Text(f"Part 2 (crosses 0): {int(p2_counter.get_value())}", color=self.COLOR_PART2)
            .scale(self.SCALE_TEXT)
            .to_edge(RIGHT).shift(UP)
        )
        
        self.play(Write(p1_label), Write(p2_label))
        self.wait(self.STANDARD_WAIT)
        
        # Helper function for animating each instruction
        def animate_instruction(idx: int, direction: str, magnitude: int) -> None:
            """Animate a single instruction with highlighting and counter updates."""
            highlight = SurroundingRectangle(instructions[idx], color=self.COLOR_PART2)
            self.play(Write(instructions[idx]), Create(highlight))
            self.wait(0.3)
            
            # Animate the dial rotation
            new_pos = self.animate_dial_rotation(
                arrow, ORIGIN, pos_tracker, direction, magnitude,
                show_crossings=True, p2_counter=p2_counter
            )
            
            # Check if landed on 0 (Part 1)
            if new_pos == 0:
                click = Star(color=self.COLOR_PART1, fill_opacity=1).scale(self.SCALE_TEXT)
                click.move_to(dial[0].point_at_angle(0))
                self.play(FadeIn(click), Flash(click, color=self.COLOR_PART1))
                p1_counter.set_value(p1_counter.get_value() + 1)
                self.play(FadeOut(click))
            
            self.play(FadeOut(highlight))
            self.wait(0.3)
        
        # Animate all the moves
        animate_instruction(0, "R", 10)   # 50 + 10 = 60
        animate_instruction(1, "L", 5)    # 60 - 5 = 55
        animate_instruction(2, "R", 45)   # 55 + 45 = 0 (LANDS ON ZERO - Part 1!)
        animate_instruction(3, "R", 105)  # 0 + 105 = 5, crosses once (Part 2)
        animate_instruction(4, "L", 50)   # 5 - 50 crosses 0 once
        animate_instruction(5, "R", 200)  # 5 + 200 = 5, crosses 2 times!
        
        self.wait(1)
    
    # ========== SCENE 2: ALGORITHM EXPLANATION ==========
    
    def scene_algorithm(self) -> None:
        """
        Second scene: Explain the algorithm for both parts.
        
        Covers:
        - Part 1: Landing on zero (simple modulo check)
        - Part 2: Crossing zero (different formulas for L/R)
        - Fixed-point division optimization
        """
        title = Text("The Algorithm").scale(self.SCALE_TITLE).to_edge(UP)
        self.play(Write(title))
        self.wait(self.STANDARD_WAIT)
        
        # Create demo dial for illustrations
        demo_dial = self.create_dial(self.DEMO_DIAL_RADIUS, center=RIGHT*3)
        demo_arrow = self.create_arrow_pointer(demo_dial, 50, center=RIGHT*3, stroke_width=4)
        demo_pos = ValueTracker(50)
        
        # Part 1: Landing on Zero
        self.algorithm_part1(title, demo_dial, demo_arrow, demo_pos)
        
        # Part 2: Crossing Zero
        self.algorithm_part2(title, demo_dial, demo_arrow, demo_pos)
        
        # Fixed-Point Division
        self.algorithm_fixed_point(title, demo_dial, demo_arrow)
    
    def algorithm_part1(self, title: Text, demo_dial: VGroup, demo_arrow: Arrow, demo_pos: ValueTracker) -> None:
        """Sub-scene for Part 1 algorithm explanation."""
        scene1_title = Text("Part 1: Landing on Zero").scale(self.SCALE_SUBTITLE).next_to(title, DOWN)
        self.play(Write(scene1_title))
        self.wait(self.STANDARD_WAIT)
        
        # Show dial
        self.play(Create(demo_dial[0]), Create(demo_dial[1]), FadeIn(demo_dial[2]), Create(demo_arrow))
        
        expl1 = Text("Count how many times we stop exactly at 0").scale(self.SCALE_TEXT).to_edge(LEFT).shift(UP*2)
        self.play(Write(expl1))
        self.wait(1)
        
        # Example: Start at 55, move R45 to land on 0
        demo_pos.set_value(55)
        self.play(
            demo_arrow.animate.become(
                self.create_arrow_pointer(demo_dial, 55, center=RIGHT*3, stroke_width=4)
            )
        )
        
        inst1 = Text("Start at 55, move R 45").scale(0.45).next_to(expl1, DOWN, aligned_edge=LEFT)
        self.play(Write(inst1))
        self.wait(self.STANDARD_WAIT)
        
        # Animate the rotation
        self.play(
            Rotate(demo_arrow, angle=-45 * TAU / 100, about_point=RIGHT*3),
            run_time=2
        )
        
        # Show it landed on 0
        result1 = Text("Stopped at 0 - add 1 to Part 1!", color=self.COLOR_PART1).scale(0.45)
        result1.next_to(inst1, DOWN, aligned_edge=LEFT)
        self.play(
            Write(result1),
            Flash(demo_dial[0].point_at_angle(0), color=self.COLOR_PART1)
        )
        self.wait(self.LONG_WAIT)
        
        # Show code - STYLE PREFERENCE: Use VGroup with Text
        code_lines_p1, code_box_p1 = self.create_code_block([
            "new_pos = (pos + mag) % 100",
            "if next_pos == 0:",
            "    part1_count += 1"
        ], scale=self.SCALE_SMALL)
        code_group_p1 = VGroup(code_lines_p1, code_box_p1).next_to(result1, DOWN, aligned_edge=LEFT, buff=0.3)
        self.play(Create(code_box_p1), Write(code_lines_p1))
        self.wait(self.EXTENDED_WAIT)
        
        self.play(
            FadeOut(expl1), FadeOut(inst1), FadeOut(result1), 
            FadeOut(code_lines_p1), FadeOut(code_box_p1), FadeOut(scene1_title)
        )
    
    def algorithm_part2(self, title: Text, demo_dial: VGroup, demo_arrow: Arrow, demo_pos: ValueTracker) -> None:
        """Sub-scene for Part 2 algorithm explanation."""
        scene2_title = Text("Part 2: Crossing Zero").scale(self.SCALE_SUBTITLE).next_to(title, DOWN)
        self.play(Write(scene2_title))
        self.wait(self.STANDARD_WAIT)
        
        # Reset to position 5
        demo_pos.set_value(5)
        self.play(
            demo_arrow.animate.become(
                self.create_arrow_pointer(demo_dial, 5, center=RIGHT*3, stroke_width=4)
            )
        )
        
        expl2 = Text("Count each time we pass through 0").scale(self.SCALE_TEXT)
        expl2.to_edge(LEFT).shift(UP*2)
        self.play(Write(expl2))
        self.wait(1)
        
        inst2 = Text("Ex. Start at 5, move R 300").scale(0.45).next_to(expl2, DOWN, aligned_edge=LEFT)
        self.play(Write(inst2))
        self.wait(self.STANDARD_WAIT)
        
        # Show that 300 = 3 full loops
        calc2 = MathTex(r"300 = 3 \times 100").scale(self.SCALE_TEXT).next_to(inst2, DOWN, aligned_edge=LEFT)
        self.play(Write(calc2))
        self.wait(1)
        
        # Animate 3 crossings with flashes
        crossing_label = Text("Crossings: 0", color=self.COLOR_PART2).scale(self.SCALE_TEXT)
        crossing_label.next_to(calc2, DOWN, aligned_edge=LEFT)
        self.play(Write(crossing_label))
        
        for i in range(3):
            self.play(
                Rotate(demo_arrow, angle=-100 * TAU / 100, about_point=RIGHT*3),
                Flash(demo_dial[0].point_at_angle(0), color=self.COLOR_PART2),
                run_time=self.LONG_WAIT
            )
            crossing_label.become(
                Text(f"Crossings: {i+1}", color=self.COLOR_PART2).scale(self.SCALE_TEXT)
                .next_to(calc2, DOWN, aligned_edge=LEFT)
            )
            self.wait(0.3)
        
        result2 = Text("Part 2 += 3", color=self.COLOR_PART2).scale(0.45)
        result2.next_to(crossing_label, DOWN, aligned_edge=LEFT)
        self.play(Write(result2))
        self.wait(self.LONG_WAIT)
        
        # Show formulas - STYLE PREFERENCE: Different for left vs right!
        formula_title = Text("Formula (direction matters!):").scale(self.SCALE_SMALL)
        formula_title.next_to(result2, DOWN, aligned_edge=LEFT, buff=0.3)
        self.play(Write(formula_title))
        self.wait(self.STANDARD_WAIT)
        
        formula_p2_right = MathTex(r"\text{Right: } \lfloor (\text{pos} + \text{mag}) / 100 \rfloor")
        formula_p2_right.scale(self.SCALE_TEXT).next_to(formula_title, DOWN, aligned_edge=LEFT)
        self.play(Write(formula_p2_right))
        self.wait(1)
        
        formula_p2_left = MathTex(
            r"\text{Left: } \lfloor (\text{pos} - 1) / 100 \rfloor - \lfloor (\text{pos} - \text{mag} - 1) / 100 \rfloor"
        )
        formula_p2_left.scale(0.45).next_to(formula_p2_right, DOWN, aligned_edge=LEFT)
        self.play(Write(formula_p2_left))
        self.wait(1)
        
        example_calc = MathTex(r"(5 + 300) / 100 = 3.05 \rightarrow \lfloor 3.05 \rfloor = 3")
        example_calc.scale(0.45).next_to(formula_p2_left, DOWN, aligned_edge=LEFT)
        self.play(Write(example_calc))
        self.wait(1)
        
        # Show code - STYLE PREFERENCE: Different logic for LEFT vs RIGHT
        code_lines_p2, code_box_p2 = self.create_code_block([
            "if direction == RIGHT:",
            "    crossings = (pos + mag) // 100",
            "else:  # LEFT",
            "    crossings = (pos - 1) // 100 -",
            "                (pos - mag - 1) // 100",
            "part2_count += crossings"
        ])
        code_group_p2 = VGroup(code_lines_p2, code_box_p2)
        code_group_p2.next_to(example_calc, DOWN, aligned_edge=LEFT, buff=0.2)
        self.play(Create(code_box_p2), Write(code_lines_p2))
        self.wait(self.EXTENDED_WAIT)
        
        self.play(
            FadeOut(expl2), FadeOut(inst2), FadeOut(calc2), FadeOut(crossing_label),
            FadeOut(result2), FadeOut(formula_title), FadeOut(formula_p2_right), 
            FadeOut(formula_p2_left), FadeOut(example_calc), FadeOut(code_lines_p2), 
            FadeOut(code_box_p2), FadeOut(scene2_title)
        )
    
    def algorithm_fixed_point(self, title: Text, demo_dial: VGroup, demo_arrow: Arrow) -> None:
        """Sub-scene for fixed-point division optimization."""
        scene3_title = Text("Hardware Trick: Fixed-Point Division").scale(self.SCALE_SUBTITLE).next_to(title, DOWN)
        self.play(Write(scene3_title))
        self.wait(self.STANDARD_WAIT)
        
        prob = Text("Problem: Division is slow in hardware!").scale(self.SCALE_TEXT).to_edge(LEFT).shift(UP*2)
        self.play(Write(prob))
        self.wait(1)
        
        sol = Text("Trick: Multiply by a magic number instead!").scale(self.SCALE_TEXT).next_to(prob, DOWN, aligned_edge=LEFT)
        self.play(Write(sol))
        self.wait(1)
        
        # Show the trick visually
        div_label = Text("Division by 100:").scale(self.SCALE_SMALL).next_to(sol, DOWN, aligned_edge=LEFT, buff=0.5)
        self.play(Write(div_label))
        
        # Traditional division - show as complex circuit
        trad_div = VGroup(
            Text("Traditional:", color=RED).scale(self.SCALE_CODE),
            MathTex(r"x \div 100").scale(self.SCALE_TEXT),
            Text("Needs special divider chip\n(slow and uses lots of space)", color=RED).scale(self.SCALE_TINY)
        ).arrange(DOWN, buff=0.2).next_to(div_label, DOWN, aligned_edge=LEFT)
        
        self.play(FadeIn(trad_div))
        self.wait(self.LONG_WAIT)
        
        # Fixed-point trick - show as simple operations
        fp_trick = VGroup(
            Text("Fixed-Point:", color=GREEN).scale(self.SCALE_CODE),
            MathTex(r"\frac{1}{100} \approx 42949673 \times 2^{-32}").scale(0.45),
            Text("Just multiply and shift bits!\n(super fast and tiny)", color=GREEN).scale(self.SCALE_TINY)
        ).arrange(DOWN, buff=0.2).next_to(trad_div, RIGHT, buff=1)
        
        self.play(FadeIn(fp_trick))
        self.wait(self.EXTENDED_WAIT)
        
        # Show the actual computation
        comp_title = Text("Computing (305) ÷ 100:").scale(self.SCALE_SMALL)
        comp_title.next_to(trad_div, DOWN, buff=0.5, aligned_edge=LEFT)
        self.play(Write(comp_title))
        self.wait(self.STANDARD_WAIT)
        
        step1 = MathTex(r"305 \times 42949673 = 13099648265").scale(self.SCALE_SMALL)
        step1.next_to(comp_title, DOWN, aligned_edge=LEFT)
        self.play(Write(step1))
        self.wait(1)
        
        step2 = MathTex(r"13099648265 \gg 32 = 3").scale(self.SCALE_SMALL)
        step2.next_to(step1, DOWN, aligned_edge=LEFT)
        self.play(Write(step2))
        self.wait(1)
        
        verify = Text("Correct! 305 / 100 = 3", color=GREEN).scale(self.SCALE_SMALL)
        verify.next_to(step2, DOWN, aligned_edge=LEFT)
        self.play(Write(verify))
        self.wait(self.EXTENDED_WAIT)
        
        # STYLE PREFERENCE: Use ABSOLUTE positioning to prevent overflow
        why_box = Rectangle(height=1.3, width=4.5, color=BLUE).shift(DOWN*2.5)
        why_title = Text("Why is this better?").scale(self.SCALE_SMALL).next_to(why_box, UP, buff=0.05)
        why_text = VGroup(
            Text("- Multiply: 1 clock tick", color=GREEN).scale(self.SCALE_TINY),
            Text("- Shift bits: instant (free!)", color=GREEN).scale(self.SCALE_TINY),
            Text("- Divide: 10+ clock ticks", color=RED).scale(self.SCALE_TINY)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to(why_box)
        
        self.play(Create(why_box), Write(why_title))
        self.play(Write(why_text))
        self.wait(3)
        
        self.play(
            FadeOut(demo_dial), FadeOut(demo_arrow),
            FadeOut(prob), FadeOut(sol), FadeOut(div_label), FadeOut(trad_div), FadeOut(fp_trick),
            FadeOut(comp_title), FadeOut(step1), FadeOut(step2), FadeOut(verify),
            FadeOut(why_box), FadeOut(why_title), FadeOut(why_text), FadeOut(scene3_title)
        )
    
    # ========== SCENE 3: CIRCUIT IMPLEMENTATION ==========
    
    def scene_circuit(self) -> None:
        """
        Third scene: Show the hardware circuit implementation.
        
        Demonstrates:
        - Input buffer for instructions
        - Position register
        - PARALLEL computation paths (LEFT and RIGHT)
        - Direction mux selecting between paths
        - Part 1 and Part 2 counters
        - Complete dataflow animation
        """
        title = Text("The Hardware Circuit").scale(self.SCALE_TITLE).to_edge(UP)
        self.play(Write(title))
        self.wait(self.STANDARD_WAIT)
        
        # Build circuit step by step
        input_group, current_highlight, buffer_contents = self.circuit_stage_input(title)
        pos_group, arrow1 = self.circuit_stage_position(title, input_group)
        right_group, left_group, arrow_pos_r, arrow_pos_l, arrow_mag_r, arrow_mag_l = \
            self.circuit_stage_parallel_compute(title, input_group, pos_group)
        dir_group, arrow_r_mux, arrow_l_mux, arrow_dir_mux, dir_sig_label = \
            self.circuit_stage_mux(title, input_group, right_group, left_group)
        arrow_feedback, feedback_label = self.circuit_stage_feedback(title, dir_group, pos_group)
        p1_box_group, p2_box_group, arrow_p1, arrow_p2, p1_logic, p2_logic = \
            self.circuit_stage_counters(title, dir_group)
        
        # Animate complete dataflow
        self.circuit_dataflow_demo(
            title, input_group, current_highlight, buffer_contents,
            pos_group, right_group, left_group, dir_group,
            p1_box_group, p2_box_group,
            arrow_pos_r, arrow_pos_l, arrow_mag_r, arrow_mag_l, arrow_dir_mux
        )
    
    def circuit_stage_input(self, title: Text) -> Tuple[VGroup, SurroundingRectangle, VGroup]:
        """Stage 1: Input handling."""
        stage1_title = Text("Input: Instruction Buffer").scale(self.SCALE_SUBTITLE).next_to(title, DOWN)
        self.play(Write(stage1_title))
        
        input_buffer = Rectangle(height=2, width=1.5, color=BLUE)
        input_buffer.set_fill(BLUE, opacity=0.2)
        input_label = Text("Instruction\nBuffer").scale(self.SCALE_SMALL).move_to(input_buffer).shift(UP*0.6)
        
        # Show buffer contents
        buffer_contents = VGroup(
            Text("R 10", color=self.COLOR_MAGNITUDE).scale(0.25),
            Text("L 5").scale(0.25),
            Text("R 45").scale(0.25),
            Text("...").scale(0.25)
        ).arrange(DOWN, buff=0.1).move_to(input_buffer).shift(DOWN*0.2)
        
        input_group = VGroup(input_buffer, input_label, buffer_contents).to_edge(LEFT).shift(UP*0.5)
        
        self.play(FadeIn(input_group))
        self.wait(self.STANDARD_WAIT)
        
        input_expl = Text("Instructions stored in buffer\nProcessed one per clock cycle").scale(self.SCALE_CODE)
        input_expl.next_to(input_group, DOWN, buff=0.3)
        self.play(Write(input_expl))
        self.wait(self.EXTENDED_WAIT)
        
        # Highlight current instruction
        current_highlight = SurroundingRectangle(buffer_contents[0], color=self.COLOR_MAGNITUDE)
        self.play(Create(current_highlight))
        self.wait(1)
        self.play(FadeOut(input_expl), FadeOut(stage1_title))
        
        return input_group, current_highlight, buffer_contents
    
    def circuit_stage_position(self, title: Text, input_group: VGroup) -> Tuple[VGroup, Arrow]:
        """Stage 2: Position register."""
        stage2_title = Text("Stage 1: Position Register").scale(self.SCALE_SUBTITLE).next_to(title, DOWN)
        self.play(Write(stage2_title))
        
        pos_reg = RoundedRectangle(height=1.2, width=1.8, corner_radius=0.2, color=self.COLOR_POSITION)
        pos_reg.set_fill(self.COLOR_POSITION, opacity=0.2)
        pos_label = Text("Position\nReg").scale(self.SCALE_SMALL).move_to(pos_reg).shift(UP*0.2)
        pos_value = Text("50").scale(self.SCALE_TEXT).move_to(pos_reg).shift(DOWN*0.2)
        pos_group = VGroup(pos_reg, pos_label, pos_value).next_to(input_group, DOWN, buff=1.2).shift(DOWN*0.3)
        
        self.play(FadeIn(pos_group))
        arrow1 = Arrow(input_group.get_bottom(), pos_group.get_top(), color=WHITE)
        self.play(Create(arrow1))
        self.wait(1)
        self.play(FadeOut(stage2_title))
        
        return pos_group, arrow1
    
    def circuit_stage_parallel_compute(self, title: Text, input_group: VGroup, pos_group: VGroup) -> Tuple[VGroup, VGroup, Arrow, Arrow, Arrow, Arrow]:
        """
        Stage 3: Parallel computation for both directions.
        
        STYLE PREFERENCE: Show BOTH paths computing in parallel,
        receiving position and magnitude inputs.
        """
        stage3_title = Text("Stage 2: Compute Both Paths").scale(self.SCALE_SUBTITLE).next_to(title, DOWN)
        self.play(Write(stage3_title))
        
        # RIGHT path computation
        right_box = RoundedRectangle(height=1.5, width=1.8, corner_radius=0.2, color=self.COLOR_RIGHT)
        right_box.set_fill(self.COLOR_RIGHT, opacity=0.2)
        right_label = Text("RIGHT\nPath").scale(self.SCALE_CODE).move_to(right_box).shift(UP*0.5)
        right_calc = Text("pos+mag\nmod 100\nzeros").scale(0.25).move_to(right_box).shift(DOWN*0.3)
        right_group = VGroup(right_box, right_label, right_calc).next_to(input_group, RIGHT, buff=1.5).shift(UP*0.8)
        
        # LEFT path computation
        left_box = RoundedRectangle(height=1.5, width=1.8, corner_radius=0.2, color=self.COLOR_LEFT)
        left_box.set_fill(self.COLOR_LEFT, opacity=0.2)
        left_label = Text("LEFT\nPath").scale(self.SCALE_CODE).move_to(left_box).shift(UP*0.5)
        left_calc = Text("pos-mag\nmod 100\nzeros").scale(0.25).move_to(left_box).shift(DOWN*0.3)
        left_group = VGroup(left_box, left_label, left_calc).next_to(input_group, RIGHT, buff=1.5).shift(DOWN*0.8)
        
        self.play(FadeIn(right_group), FadeIn(left_group))
        
        arrow_pos_r = Arrow(pos_group.get_right(), right_group.get_left()+UP*0.2, color=self.COLOR_POSITION)
        arrow_pos_l = Arrow(pos_group.get_right(), left_group.get_left()+UP*0.2, color=self.COLOR_POSITION)
        arrow_mag_r = Arrow(
            input_group.get_right()+RIGHT*0.2, right_group.get_left()+LEFT*0.2,
            color=self.COLOR_MAGNITUDE
        )
        arrow_mag_l = Arrow(
            input_group.get_right()+RIGHT*0.4, left_group.get_left()+LEFT*0.2,
            color=self.COLOR_MAGNITUDE
        )
        
        self.play(Create(arrow_pos_r), Create(arrow_pos_l))
        self.play(Create(arrow_mag_r), Create(arrow_mag_l))
        self.wait(self.LONG_WAIT)
        self.play(FadeOut(stage3_title))
        
        return right_group, left_group, arrow_pos_r, arrow_pos_l, arrow_mag_r, arrow_mag_l
    
    def circuit_stage_mux(self, title: Text, input_group: VGroup, right_group: VGroup, left_group: VGroup) -> Tuple[VGroup, Arrow, Arrow, CurvedArrow, Text]:
        """Stage 4: Direction mux selects which path."""
        stage4_title = Text("Stage 3: Select Path (Mux)").scale(self.SCALE_SUBTITLE).next_to(title, DOWN)
        self.play(Write(stage4_title))
        
        # Mux selects between the two paths
        dir_mux = Polygon(
            ORIGIN, UP*0.8+LEFT*0.3, UP*0.8+RIGHT*1, DOWN*0.8+RIGHT*1, DOWN*0.8+LEFT*0.3,
            color=self.COLOR_MUX, fill_opacity=0.2, stroke_width=2
        )
        dir_label = Text("Dir\nMux").scale(self.SCALE_CODE).move_to(dir_mux)
        dir_group = VGroup(dir_mux, dir_label).next_to(right_group, RIGHT, buff=1.2).shift(DOWN*0.8)
        
        self.play(FadeIn(dir_group))
        
        # Arrows from both paths to mux
        arrow_r_mux = Arrow(right_group.get_right(), dir_group.get_left()+UP*0.3, color=WHITE)
        arrow_l_mux = Arrow(left_group.get_right(), dir_group.get_left()+DOWN*0.3, color=WHITE)
        self.play(Create(arrow_r_mux), Create(arrow_l_mux))
        
        # Direction signal (RED) to mux
        arrow_dir_mux = CurvedArrow(
            input_group.get_top()+UP*0.1, dir_group.get_top()+LEFT*0.3,
            color=self.COLOR_DIRECTION, angle=-TAU/4
        )
        dir_sig_label = Text("dir").scale(0.25).next_to(arrow_dir_mux, UP, buff=0.1)
        self.play(Create(arrow_dir_mux), Write(dir_sig_label))
        self.wait(self.LONG_WAIT)
        self.play(FadeOut(stage4_title))
        
        return dir_group, arrow_r_mux, arrow_l_mux, arrow_dir_mux, dir_sig_label
    
    def circuit_stage_feedback(self, title: Text, dir_group: VGroup, pos_group: VGroup) -> Tuple[CurvedArrow, Text]:
        """Stage 5: Feedback to position register."""
        stage5_title = Text("Stage 4: Update Position").scale(self.SCALE_SUBTITLE).next_to(title, DOWN)
        self.play(Write(stage5_title))
        
        # Arrow from mux back to position register
        arrow_feedback = CurvedArrow(
            dir_group.get_bottom()+DOWN*0.2, pos_group.get_right()+RIGHT*0.2,
            color=self.COLOR_POSITION, angle=-TAU/6
        )
        feedback_label = Text("new pos").scale(0.25).next_to(arrow_feedback, DOWN, buff=0.1).shift(LEFT*0.5)
        self.play(Create(arrow_feedback), Write(feedback_label))
        self.wait(self.LONG_WAIT)
        self.play(FadeOut(stage5_title))
        
        return arrow_feedback, feedback_label
    
    def circuit_stage_counters(self, title: Text, dir_group: VGroup) -> Tuple[VGroup, VGroup, Arrow, Arrow, Text, Text]:
        """Stage 6: Part 1 and Part 2 counters."""
        stage6_title = Text("Stage 5: Counting Logic").scale(self.SCALE_SUBTITLE).next_to(title, DOWN)
        self.play(Write(stage6_title))
        
        # Part 1 counter - checking if new_pos == 0
        p1_box = RoundedRectangle(height=1, width=1.5, corner_radius=0.2, color=self.COLOR_PART1)
        p1_box.set_fill(self.COLOR_PART1, opacity=0.2)
        p1_box_label = Text("Part 1").scale(self.SCALE_CODE).move_to(p1_box).shift(UP*0.25)
        p1_check = Text("pos==0?").scale(0.25).move_to(p1_box).shift(DOWN*0.2)
        p1_box_group = VGroup(p1_box, p1_box_label, p1_check).next_to(dir_group, RIGHT, buff=1.5).shift(UP*0.5)
        
        # Part 2 counter - counting crossings
        p2_box = RoundedRectangle(height=1, width=1.5, corner_radius=0.2, color=self.COLOR_PART2)
        p2_box.set_fill(self.COLOR_PART2, opacity=0.2)
        p2_box_label = Text("Part 2").scale(self.SCALE_CODE).move_to(p2_box).shift(UP*0.25)
        p2_check = Text("crossings").scale(0.25).move_to(p2_box).shift(DOWN*0.2)
        p2_box_group = VGroup(p2_box, p2_box_label, p2_check).next_to(p1_box_group, DOWN, buff=0.8)
        
        self.play(FadeIn(p1_box_group), FadeIn(p2_box_group))
        
        # Arrows to counters from mux
        arrow_p1 = Arrow(dir_group.get_right(), p1_box_group.get_left(), color=WHITE)
        arrow_p2 = Arrow(dir_group.get_right(), p2_box_group.get_left()+UP*0.1, color=WHITE)
        
        self.play(Create(arrow_p1), Create(arrow_p2))
        
        p1_logic = Text("Inc if\nnew==0").scale(self.SCALE_TINY).next_to(p1_box_group, RIGHT, buff=0.2)
        p2_logic = Text("Add\nzeros").scale(self.SCALE_TINY).next_to(p2_box_group, RIGHT, buff=0.2)
        
        self.play(Write(p1_logic), Write(p2_logic))
        self.wait(self.EXTENDED_WAIT)
        self.play(FadeOut(stage6_title))
        
        return p1_box_group, p2_box_group, arrow_p1, arrow_p2, p1_logic, p2_logic
    
    def circuit_dataflow_demo(self, title: Text, input_group: VGroup, current_highlight: SurroundingRectangle, buffer_contents: VGroup,
                             pos_group: VGroup, right_group: VGroup, left_group: VGroup, dir_group: VGroup,
                             p1_box_group: VGroup, p2_box_group: VGroup,
                             arrow_pos_r: Arrow, arrow_pos_l: Arrow, arrow_mag_r: Arrow, arrow_mag_l: Arrow, arrow_dir_mux: CurvedArrow) -> None:
        """Animate the complete dataflow with dial simulation."""
        final_title = Text("Complete Dataflow Example").scale(self.SCALE_SUBTITLE).next_to(title, DOWN)
        self.play(Write(final_title))
        
        # Create a small dial for simulation
        sim_dial = Circle(radius=self.SIM_DIAL_RADIUS, color=self.COLOR_DIAL).to_corner(UR).shift(LEFT*0.5+DOWN)
        sim_arrow = Arrow(sim_dial.get_center(), 
                         sim_dial.get_center()+RIGHT*self.SIM_DIAL_RADIUS,
                         buff=0, color=self.COLOR_ARROW, stroke_width=3)
        sim_pos_label = Text("Pos: 50").scale(self.SCALE_TINY).next_to(sim_dial, DOWN, buff=0.2)
        
        self.play(Create(sim_dial), Create(sim_arrow), Write(sim_pos_label))
        self.wait(self.STANDARD_WAIT)
        
        # Simulate R 10 instruction flowing through
        # 1. Highlight instruction in buffer
        self.play(current_highlight.animate.surround(buffer_contents[0]))
        self.wait(0.3)
        
        # 2. STYLE PREFERENCE: Position and magnitude flow to BOTH computation paths
        pos_dot1 = Dot(color=self.COLOR_POSITION).move_to(pos_group.get_right())
        pos_dot2 = Dot(color=self.COLOR_POSITION).move_to(pos_group.get_right())
        mag_dot1 = Dot(color=self.COLOR_MAGNITUDE).move_to(input_group.get_top()+RIGHT*0.2)
        mag_dot2 = Dot(color=self.COLOR_MAGNITUDE).move_to(input_group.get_top()+RIGHT*0.4)
        
        self.play(
            MoveAlongPath(pos_dot1, arrow_pos_r),
            MoveAlongPath(pos_dot2, arrow_pos_l),
            MoveAlongPath(mag_dot1, arrow_mag_r),
            MoveAlongPath(mag_dot2, arrow_mag_l),
            run_time=0.8
        )
        self.wait(0.3)
        
        # 3. STYLE PREFERENCE: Both paths compute in PARALLEL
        self.play(Flash(right_group[0], color=self.COLOR_COMPUTE_BOX), Flash(left_group[0], color=self.COLOR_COMPUTE_BOX))
        self.wait(0.3)
        
        # 4. Direction signal selects RIGHT path
        dir_dot = Dot(color=self.COLOR_DIRECTION).move_to(input_group.get_right()+UP*0.1)
        self.play(MoveAlongPath(dir_dot, arrow_dir_mux), run_time=0.6)
        self.wait(0.2)
        
        # 5. Mux selects the result
        self.play(Flash(dir_group[0], color=self.COLOR_MUX))
        self.wait(0.3)
        
        # 6. Update position register and dial
        self.play(
            pos_group[2].animate.become(Text("60").scale(self.SCALE_TEXT).move_to(pos_group[0]).shift(DOWN*0.2)),
            Rotate(sim_arrow, angle=-10*TAU/100, about_point=sim_dial.get_center()),
            sim_pos_label.animate.become(Text("Pos: 60").scale(self.SCALE_TINY).next_to(sim_dial, DOWN, buff=0.2)),
            run_time=1
        )
        self.wait(self.STANDARD_WAIT)
        
        # 7. Check counters (no change for this move)
        self.play(Flash(p1_box_group[0], color=self.COLOR_PART1), Flash(p2_box_group[0], color=self.COLOR_PART2))
        self.wait(1)
        
        # Show one more: R 45 (lands on 0)
        self.play(current_highlight.animate.surround(buffer_contents[2]))
        self.wait(0.3)
        
        # Fast dataflow - parallel computation
        self.play(Flash(right_group[0], color=self.COLOR_COMPUTE_BOX), Flash(left_group[0], color=self.COLOR_COMPUTE_BOX), run_time=0.5)
        self.play(Flash(dir_group[0], color=self.COLOR_MUX), run_time=0.5)
        
        # Update to 0
        self.play(
            pos_group[2].animate.become(Text("0").scale(self.SCALE_TEXT).move_to(pos_group[0]).shift(DOWN*0.2)),
            Rotate(sim_arrow, angle=-45*TAU/100, about_point=sim_dial.get_center()),
            sim_pos_label.animate.become(Text("Pos: 0").scale(self.SCALE_TINY).next_to(sim_dial, DOWN, buff=0.2)),
            Flash(sim_dial.point_at_angle(0), color=self.COLOR_PART1),
            run_time=self.LONG_WAIT
        )
        self.wait(self.STANDARD_WAIT)
        
        # Part 1 increments!
        p1_count = Text("1").scale(self.SCALE_SMALL).next_to(p1_box_group, DOWN, buff=0.1)
        self.play(
            Flash(p1_box_group[0], color=self.COLOR_PART1, flash_radius=0.5),
            Write(p1_count)
        )
        self.wait(self.EXTENDED_WAIT)
        
        summary = VGroup(
            Text("Every clock cycle:").scale(self.SCALE_SMALL),
            Text("1. Fetch instruction from buffer").scale(self.SCALE_TINY),
            Text("2. Compute BOTH paths in parallel").scale(self.SCALE_TINY),
            Text("3. Direction mux selects result").scale(self.SCALE_TINY),
            Text("4. Update position register").scale(self.SCALE_TINY),
            Text("5. Check and update counters").scale(self.SCALE_TINY)
        ).arrange(DOWN, aligned_edge=RIGHT, buff=0.15).to_corner(DL)
        
        self.play(Write(summary))
        self.wait(3)
    
    # ========== SCENE 4: MASSIVELY PARALLEL SOLUTION ==========
    
    def scene_parallel(self) -> None:
        """
        Fourth scene: Massively parallel tree-based solution.
        
        Demonstrates:
        - Chunk abstraction (total rotation + crossings from all 100 positions)
        - Tree reduction for O(log N) latency
        - Parallel merge operations
        - Hardware complexity vs speedup tradeoff
        """
        title = Text("Massively Parallel Solution").scale(self.SCALE_TITLE).to_edge(UP)
        self.play(Write(title))
        self.wait(self.STANDARD_WAIT)
        
        # Introduce the concept
        self.parallel_intro(title)
        
        # Show chunk structure
        self.parallel_chunk_structure(title)
        
        # Demonstrate merge operation
        self.parallel_merge_demo(title)
        
        # Show tree reduction
        self.parallel_tree_reduction(title)
        
        # Performance comparison
        self.parallel_performance(title)
    
    def parallel_intro(self, title: Text) -> None:
        """Introduce the parallel approach."""
        subtitle = Text("From Sequential to Parallel").scale(self.SCALE_SUBTITLE)
        subtitle.next_to(title, DOWN)
        self.play(Write(subtitle))
        self.wait(self.STANDARD_WAIT)
        
        # Show the problem
        problem = Text("Sequential: Process N instructions in N cycles").scale(self.SCALE_TEXT)
        problem.to_edge(LEFT).shift(UP*1.0)
        self.play(Write(problem))
        
        # Show N instructions
        instructions = VGroup(
            Text("R10").scale(self.SCALE_SMALL),
            Text("L5").scale(self.SCALE_SMALL),
            Text("R45").scale(self.SCALE_SMALL),
            Text("...").scale(self.SCALE_SMALL),
            Text("R200").scale(self.SCALE_SMALL)
        ).arrange(RIGHT, buff=0.3).next_to(problem, DOWN, buff=0.5)
        
        self.play(FadeIn(instructions))
        self.wait(self.STANDARD_WAIT)
        
        # Show sequential processing
        arrow = Arrow(instructions[0].get_bottom(), instructions[0].get_bottom() + DOWN*0.5, color=YELLOW)
        self.play(Create(arrow))
        
        for i in range(4):
            if i < len(instructions) - 1:
                self.play(arrow.animate.next_to(instructions[i+1], UP, buff=0.1), run_time=0.5)
                self.wait(0.3)
        
        latency = Text("Latency: O(N)", color=RED).scale(self.SCALE_TEXT)
        latency.next_to(instructions, DOWN, buff=0.8)
        self.play(Write(latency))
        self.wait(self.LONG_WAIT)
        
        # Introduce parallel idea
        idea = Text("Parallel: Process in O(log N) using tree reduction!", color=GREEN).scale(self.SCALE_TEXT)
        idea.next_to(latency, DOWN, buff=0.5)
        idea_box = SurroundingRectangle(idea, color=GREEN, buff=0.15)
        self.play(Create(idea_box), Write(idea))
        self.wait(self.EXTENDED_WAIT)
        
        self.play(FadeOut(VGroup(subtitle, problem, instructions, arrow, latency, idea, idea_box)))
    
    def parallel_chunk_structure(self, title: Text) -> None:
        """Show the chunk data structure."""
        subtitle = Text("The Chunk Abstraction").scale(self.SCALE_SUBTITLE)
        subtitle.next_to(title, DOWN)
        self.play(Write(subtitle))
        self.wait(self.STANDARD_WAIT)
        
        # Define chunk
        chunk_label = Text("A Chunk represents a sequence of instructions:").scale(self.SCALE_TEXT)
        chunk_label.to_edge(LEFT).shift(UP*1.0)
        self.play(Write(chunk_label))
        
        # Chunk box
        chunk_box = Rectangle(height=2.5, width=4, color=self.COLOR_CHUNK)
        chunk_box.set_fill(self.COLOR_CHUNK, opacity=0.1)
        chunk_box.shift(LEFT*2)
        
        chunk_title = Text("Chunk").scale(self.SCALE_SMALL).next_to(chunk_box, UP, buff=0.1)
        
        # Fields
        field1 = Text("total_rotation: int16").scale(self.SCALE_TINY).move_to(chunk_box).shift(UP*0.6)
        field2 = Text("crossings[100]: int16").scale(self.SCALE_TINY).move_to(chunk_box).shift(UP*0.1)
        field3 = Text("(one per start position)").scale(0.2).move_to(chunk_box).shift(DOWN*0.4)
        
        self.play(Create(chunk_box), Write(chunk_title))
        self.play(Write(field1))
        self.play(Write(field2), Write(field3))
        self.wait(self.LONG_WAIT)
        
        # Show example values
        example_label = Text("Example: chunk from R105").scale(self.SCALE_SMALL)
        example_label.shift(RIGHT*2 + UP*1.5)
        self.play(Write(example_label))
        
        example_box = Rectangle(height=2.5, width=3.5, color=self.COLOR_CHUNK)
        example_box.set_fill(self.COLOR_CHUNK, opacity=0.1)
        example_box.shift(RIGHT*2 + DOWN*0.3)
        
        ex_rot = Text("rotation = 105").scale(self.SCALE_TINY).move_to(example_box).shift(UP*0.8)
        ex_cross1 = Text("crossings[0] = 1").scale(self.SCALE_TINY).move_to(example_box).shift(UP*0.3)
        ex_cross2 = Text("crossings[50] = 1").scale(self.SCALE_TINY).move_to(example_box).shift(DOWN*0.2)
        ex_cross3 = Text("crossings[96] = 2").scale(self.SCALE_TINY).move_to(example_box).shift(DOWN*0.7)
        
        self.play(Create(example_box))
        self.play(Write(ex_rot))
        self.play(Write(ex_cross1), Write(ex_cross2), Write(ex_cross3))
        self.wait(self.EXTENDED_WAIT)
        
        self.play(FadeOut(VGroup(
            subtitle, chunk_label, chunk_box, chunk_title, field1, field2, field3,
            example_label, example_box, ex_rot, ex_cross1, ex_cross2, ex_cross3
        )))
    
    def parallel_merge_demo(self, title: Text) -> None:
        """Demonstrate merging two chunks."""
        subtitle = Text("Merging Chunks").scale(self.SCALE_SUBTITLE)
        subtitle.next_to(title, DOWN)
        self.play(Write(subtitle))
        self.wait(self.STANDARD_WAIT)
        
        merge_label = Text("Chunk A ++ Chunk B = Combined effect").scale(self.SCALE_TEXT)
        merge_label.to_edge(LEFT).shift(UP*1.5)
        self.play(Write(merge_label))
        
        # Show two chunks
        chunk_a = Rectangle(height=1.2, width=1.5, color=self.COLOR_CHUNK)
        chunk_a.set_fill(self.COLOR_CHUNK, opacity=0.2)
        chunk_a.shift(LEFT*3 + UP*0.3)
        label_a = Text("A: R10").scale(self.SCALE_TINY).next_to(chunk_a, UP, buff=0.1)
        
        chunk_b = Rectangle(height=1.2, width=1.5, color=self.COLOR_CHUNK)
        chunk_b.set_fill(self.COLOR_CHUNK, opacity=0.2)
        chunk_b.shift(LEFT*0.8 + UP*0.3)
        label_b = Text("B: L5").scale(self.SCALE_TINY).next_to(chunk_b, UP, buff=0.1)
        
        self.play(Create(chunk_a), Write(label_a))
        self.play(Create(chunk_b), Write(label_b))
        self.wait(self.STANDARD_WAIT)
        
        # Merge operation
        merge_symbol = Text("+").scale(0.8).shift(LEFT*1.9 + UP*0.3)
        self.play(Write(merge_symbol))
        
        arrow = Arrow(chunk_b.get_right(), chunk_b.get_right() + RIGHT*1.5, color=self.COLOR_MERGE)
        self.play(Create(arrow))
        
        # Result chunk
        chunk_c = Rectangle(height=1.2, width=1.5, color=self.COLOR_MERGE)
        chunk_c.set_fill(self.COLOR_MERGE, opacity=0.2)
        chunk_c.shift(RIGHT*1.5 + UP*0.3)
        label_c = Text("C: R10+L5").scale(self.SCALE_TINY).next_to(chunk_c, UP, buff=0.1)
        
        self.play(Create(chunk_c), Write(label_c))
        self.wait(self.LONG_WAIT)
        
        # Show merge formula
        formula = VGroup(
            Text("For each position p:").scale(self.SCALE_SMALL),
            Text("  mid = (p + A.rotation) mod 100").scale(self.SCALE_TINY),
            Text("  C.crossings[p] = A.crossings[p] + B.crossings[mid]").scale(self.SCALE_TINY),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).shift(DOWN*1.2)
        
        formula_box = SurroundingRectangle(formula, color=YELLOW, buff=0.15)
        self.play(Create(formula_box), Write(formula))
        self.wait(self.EXTENDED_WAIT)
        
        self.play(FadeOut(VGroup(
            subtitle, merge_label, chunk_a, label_a, chunk_b, label_b, merge_symbol,
            arrow, chunk_c, label_c, formula, formula_box
        )))
    
    def parallel_tree_reduction(self, title: Text) -> None:
        """Show the tree reduction process."""
        subtitle = Text("Tree Reduction: O(log N) Latency").scale(self.SCALE_SUBTITLE)
        subtitle.next_to(title, DOWN)
        self.play(Write(subtitle))
        self.wait(self.STANDARD_WAIT)
        
        tree_label = Text("Process 8 instructions in 3 parallel stages:").scale(self.SCALE_TEXT)
        tree_label.to_edge(LEFT).shift(UP*1.5)
        self.play(Write(tree_label))
        
        # Level 0: 8 chunks
        level0_y = 0.8
        chunks_l0 = VGroup(*[
            VGroup(
                Circle(radius=0.25, color=self.COLOR_CHUNK, fill_opacity=0.3),
                Text(f"C{i}").scale(0.2)
            )
            for i in range(8)
        ]).arrange(RIGHT, buff=0.4).shift(UP*level0_y)
        
        level0_label = Text("Level 0: 8 chunks").scale(self.SCALE_TINY).next_to(chunks_l0, LEFT, buff=0.5)
        self.play(FadeIn(chunks_l0), Write(level0_label))
        self.wait(self.STANDARD_WAIT)
        
        # Level 1: 4 merges
        level1_y = -0.3
        chunks_l1 = VGroup(*[
            VGroup(
                Circle(radius=0.25, color=self.COLOR_MERGE, fill_opacity=0.3),
                Text(f"M{i}").scale(0.2)
            )
            for i in range(4)
        ]).arrange(RIGHT, buff=0.9).shift(UP*level1_y)
        
        # Arrows from level 0 to level 1
        arrows_01 = VGroup()
        for i in range(4):
            arr1 = Arrow(chunks_l0[i*2].get_bottom(), chunks_l1[i].get_top(), color=GRAY, stroke_width=2, buff=0.1)
            arr2 = Arrow(chunks_l0[i*2+1].get_bottom(), chunks_l1[i].get_top(), color=GRAY, stroke_width=2, buff=0.1)
            arrows_01.add(arr1, arr2)
        
        level1_label = Text("Level 1: 4 merges").scale(self.SCALE_TINY).next_to(chunks_l1, LEFT, buff=0.5)
        self.play(Create(arrows_01))
        self.play(FadeIn(chunks_l1), Write(level1_label))
        self.wait(self.STANDARD_WAIT)
        
        # Level 2: 2 merges
        level2_y = -1.4
        chunks_l2 = VGroup(*[
            VGroup(
                Circle(radius=0.25, color=self.COLOR_TREE, fill_opacity=0.3),
                Text(f"M{i+4}").scale(0.2)
            )
            for i in range(2)
        ]).arrange(RIGHT, buff=1.8).shift(UP*level2_y)
        
        arrows_12 = VGroup()
        for i in range(2):
            arr1 = Arrow(chunks_l1[i*2].get_bottom(), chunks_l2[i].get_top(), color=GRAY, stroke_width=2, buff=0.1)
            arr2 = Arrow(chunks_l1[i*2+1].get_bottom(), chunks_l2[i].get_top(), color=GRAY, stroke_width=2, buff=0.1)
            arrows_12.add(arr1, arr2)
        
        level2_label = Text("Level 2: 2 merges").scale(self.SCALE_TINY).next_to(chunks_l2, LEFT, buff=0.5)
        self.play(Create(arrows_12))
        self.play(FadeIn(chunks_l2), Write(level2_label))
        self.wait(self.STANDARD_WAIT)
        
        # Level 3: Final result
        level3_y = -2.5
        chunk_final = VGroup(
            Circle(radius=0.3, color=GREEN, fill_opacity=0.3),
            Text("Result").scale(0.2)
        ).shift(UP*level3_y)
        
        arrows_23 = VGroup(
            Arrow(chunks_l2[0].get_bottom(), chunk_final.get_top(), color=GRAY, stroke_width=2, buff=0.1),
            Arrow(chunks_l2[1].get_bottom(), chunk_final.get_top(), color=GRAY, stroke_width=2, buff=0.1)
        )
        
        level3_label = Text("Level 3: Final").scale(self.SCALE_TINY).next_to(chunk_final, LEFT, buff=0.5)
        self.play(Create(arrows_23))
        self.play(FadeIn(chunk_final), Write(level3_label))
        self.wait(self.LONG_WAIT)
        
        # Highlight the result
        result_text = Text("result[50] = answer!", color=GREEN).scale(self.SCALE_SMALL)
        result_text.next_to(chunk_final, RIGHT, buff=0.5)
        self.play(Write(result_text), Flash(chunk_final, color=GREEN))
        self.wait(self.EXTENDED_WAIT)
        
        self.play(FadeOut(VGroup(
            subtitle, tree_label, level0_label, level1_label, level2_label, level3_label,
            chunks_l0, chunks_l1, chunks_l2, chunk_final, arrows_01, arrows_12, arrows_23, result_text
        )))
    
    def parallel_performance(self, title: Text) -> None:
        """Show performance comparison."""
        subtitle = Text("Performance Analysis").scale(self.SCALE_SUBTITLE)
        subtitle.next_to(title, DOWN)
        self.play(Write(subtitle))
        self.wait(self.STANDARD_WAIT)
        
        # Comparison table
        table_title = Text("Sequential vs Parallel (N=1024)").scale(self.SCALE_TEXT)
        table_title.shift(UP*1.5)
        self.play(Write(table_title))
        
        # Sequential
        seq_box = Rectangle(height=2, width=3, color=RED)
        seq_box.set_fill(RED, opacity=0.1)
        seq_box.shift(LEFT*2.5 + DOWN*0.5)
        
        seq_title = Text("Sequential", color=RED).scale(self.SCALE_SMALL).next_to(seq_box, UP, buff=0.1)
        seq_latency = Text("Latency: 1024 cycles").scale(self.SCALE_TINY).move_to(seq_box).shift(UP*0.5)
        seq_luts = Text("LUTs: ~100").scale(self.SCALE_TINY).move_to(seq_box).shift(UP*0.0)
        seq_power = Text("Power: Low").scale(self.SCALE_TINY).move_to(seq_box).shift(DOWN*0.5)
        
        self.play(Create(seq_box), Write(seq_title))
        self.play(Write(seq_latency), Write(seq_luts), Write(seq_power))
        self.wait(self.STANDARD_WAIT)
        
        # Parallel
        par_box = Rectangle(height=2, width=3, color=GREEN)
        par_box.set_fill(GREEN, opacity=0.1)
        par_box.shift(RIGHT*2.5 + DOWN*0.5)
        
        par_title = Text("Parallel Tree", color=GREEN).scale(self.SCALE_SMALL).next_to(par_box, UP, buff=0.1)
        par_latency = Text("Latency: 11 cycles", color=GREEN).scale(self.SCALE_TINY).move_to(par_box).shift(UP*0.5)
        par_luts = Text("LUTs: ~13M").scale(self.SCALE_TINY).move_to(par_box).shift(UP*0.0)
        par_power = Text("Power: High").scale(self.SCALE_TINY).move_to(par_box).shift(DOWN*0.5)
        
        self.play(Create(par_box), Write(par_title))
        self.play(Write(par_latency), Write(par_luts), Write(par_power))
        self.wait(self.LONG_WAIT)
        
        # Speedup
        speedup = Text("Speedup: 93x faster!", color=YELLOW).scale(self.SCALE_TEXT)
        speedup.shift(DOWN*2.3)
        speedup_box = SurroundingRectangle(speedup, color=YELLOW, buff=0.2)
        
        self.play(Create(speedup_box), Write(speedup))
        self.wait(self.EXTENDED_WAIT)
        
        # Tradeoff note
        tradeoff = Text("Trade chip size for speed - great for lots of data!").scale(self.SCALE_SMALL)
        tradeoff.shift(DOWN*3.0)
        self.play(Write(tradeoff))
        self.wait(3)
