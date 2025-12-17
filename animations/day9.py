"""animations/day9.py

Day 9 — Movie Theater (Max Rectangle + Constrained Interior)

Storyboard: animations/day_by_day_video_scripts.md (Day 9)
"""

from __future__ import annotations

from typing import List, Tuple

from manim import *


class Day9(Scene):
    # Timing
    FAST = 0.25
    STANDARD = 0.7
    LONG = 1.3
    HOLD = 34.25

    # Colors
    COLOR_TEXT = GRAY_E
    COLOR_DIM = GRAY_C
    COLOR_POINT = RED_C
    COLOR_RECT = ORANGE
    COLOR_GOOD = GREEN_C
    COLOR_LOOP = RED_C
    COLOR_FILL = GREEN_E
    COLOR_SCAN = YELLOW_E
    COLOR_ACC = BLUE_D

    SCALE_TITLE = 0.8
    SCALE_SUB = 0.55
    SCALE_TEXT = 0.5
    SCALE_SMALL = 0.42
    SCALE_CODE = 0.34
    SCALE_TINY = 0.33

    def construct(self) -> None:
        self.scene_hook()
        self.clear()
        self.scene_part1_formula()
        self.clear()
        self.scene_part1_bruteforce_ok()
        self.clear()
        self.scene_part2_inside_loop()
        self.clear()
        self.scene_part2_scanline_pairs()
        self.clear()
        self.scene_toggle_set_to_intervals()
        self.clear()
        self.scene_candidate_tracking()
        self.clear()
        self.scene_fpga_part1_pair_farm()
        self.clear()
        self.scene_fpga_part2_scanline_machine()
        self.clear()
        self.scene_design_comparison()
        self.clear()
        self.scene_takeaway()

    # Helpers -----------------------------------------------------------------
    def make_code_block(self, lines: List[str]) -> VGroup:
        text = VGroup(
            *[Text(line, font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_CODE) for line in lines]
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        box = SurroundingRectangle(text, color=self.COLOR_DIM, buff=0.18)
        return VGroup(box, text)

    def make_grid_points(self, pts: List[Tuple[int, int]], origin: np.ndarray, cell: float = 0.65) -> VGroup:
        dots = VGroup()
        for (x, y) in pts:
            dots.add(Dot(origin + RIGHT * (x * cell) + UP * (y * cell), color=self.COLOR_POINT))
        return dots

    def rect_from_corners(self, a: Tuple[int, int], b: Tuple[int, int], origin: np.ndarray, cell: float = 0.65) -> Rectangle:
        x0, y0 = a
        x1, y1 = b
        w = abs(x0 - x1) + 1
        h = abs(y0 - y1) + 1
        rect = Rectangle(width=w * cell, height=h * cell, color=self.COLOR_RECT)
        cx = (x0 + x1) / 2
        cy = (y0 + y1) / 2
        rect.move_to(origin + RIGHT * (cx * cell) + UP * (cy * cell))
        rect.set_stroke(width=4)
        return rect

    def numberline_with_ticks(self, x_max: int, length: float = 6.2) -> NumberLine:
        nl = NumberLine(x_range=[0, x_max, 1], length=length, include_numbers=True, font_size=22)
        nl.set_color(self.COLOR_TEXT)
        return nl

    def edge_tick(self, nl: NumberLine, x: int, *, color: ManimColor) -> Line:
        p = nl.number_to_point(x)
        return Line(p + UP * 0.25, p + DOWN * 0.25, color=color)

    def interval_span(self, nl: NumberLine, l: int, r: int, *, color: ManimColor) -> Rectangle:
        p0 = nl.number_to_point(l)
        p1 = nl.number_to_point(r)
        w = abs(p1[0] - p0[0])
        bar = Rectangle(width=w, height=0.35, color=color)
        bar.set_fill(color, opacity=0.18)
        bar.move_to((p0 + p1) / 2 + DOWN * 0.8)
        return bar

    # Scene 1 -----------------------------------------------------------------
    def scene_hook(self) -> None:
        title = Text("Day 9 — Movie Theater", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("Biggest rectangle from two corners", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        origin = LEFT * 3.2 + DOWN * 1.0
        pts = [(0, 0), (3, 0), (1, 2), (4, 3)]
        dots = self.make_grid_points(pts, origin)
        self.play(FadeIn(dots, shift=UP * 0.1), run_time=self.STANDARD)

        a, b = pts[0], pts[-1]
        rect = self.rect_from_corners(a, b, origin)
        area = (abs(a[0] - b[0]) + 1) * (abs(a[1] - b[1]) + 1)
        area_text = Text(f"area = {area}", color=self.COLOR_RECT).scale(self.SCALE_TEXT)
        area_text.to_edge(RIGHT).shift(UP * 0.8)
        self.play(Create(rect), FadeIn(area_text, shift=LEFT), run_time=self.STANDARD)
        self.wait(self.HOLD)

    # Scene 2 -----------------------------------------------------------------
    def scene_part1_formula(self) -> None:
        title = Text("Part 1: area formula (+1)", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("count tiles, not gaps", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        grid = VGroup(*[Square(0.55, color=self.COLOR_DIM).set_fill(self.COLOR_DIM, opacity=0.05) for _ in range(12)])
        grid.arrange_in_grid(rows=3, buff=0.05)
        grid.to_edge(LEFT).shift(RIGHT * 1.2)
        self.play(FadeIn(grid), run_time=self.STANDARD)

        brace_x = Brace(grid, DOWN)
        brace_y = Brace(grid, LEFT)
        dx = Text(r"dx = |x1-x2| + 1", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        dy = Text(r"dy = |y1-y2| + 1", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        dx.next_to(brace_x, DOWN, buff=0.2)
        dy.next_to(brace_y, LEFT, buff=0.2)
        self.play(GrowFromCenter(brace_x), FadeIn(dx), GrowFromCenter(brace_y), FadeIn(dy), run_time=self.STANDARD)

        formula = Text(r"area = dx \cdot dy", color=self.COLOR_ACC).scale(self.SCALE_TEXT)
        formula.to_edge(RIGHT).shift(UP * 0.2)
        self.play(Write(formula), run_time=self.STANDARD)
        self.wait(self.HOLD)

    # Scene 3 -----------------------------------------------------------------
    def scene_part1_bruteforce_ok(self) -> None:
        title = Text("Part 1: brute force is fine", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("N²/2 pairs — parallel lanes on FPGA", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        pts_box = RoundedRectangle(width=3.2, height=1.4, corner_radius=0.18, color=self.COLOR_DIM)
        pts_box.set_fill(self.COLOR_DIM, opacity=0.06)
        pts_lbl = Text("point list", color=self.COLOR_TEXT).scale(self.SCALE_SMALL).move_to(pts_box)
        pts = VGroup(pts_box, pts_lbl).to_edge(LEFT).shift(RIGHT * 1.1 + UP * 0.8)

        lanes = VGroup()
        for i in range(4):
            b = RoundedRectangle(width=2.4, height=0.85, corner_radius=0.15, color=self.COLOR_ACC)
            b.set_fill(self.COLOR_ACC, opacity=0.06)
            t = Text(f"area lane {i}", color=self.COLOR_ACC).scale(self.SCALE_TINY).move_to(b)
            lanes.add(VGroup(b, t))
        lanes.arrange(DOWN, buff=0.25).move_to(ORIGIN).shift(UP * 0.3)

        reducer = RoundedRectangle(width=3.0, height=1.1, corner_radius=0.18, color=self.COLOR_GOOD)
        reducer.set_fill(self.COLOR_GOOD, opacity=0.06)
        reducer_lbl = Text("max reducer", color=self.COLOR_GOOD).scale(self.SCALE_SMALL).move_to(reducer)
        red = VGroup(reducer, reducer_lbl).to_edge(RIGHT).shift(LEFT * 1.0 + UP * 0.2)

        self.play(FadeIn(pts), FadeIn(lanes), FadeIn(red), run_time=self.STANDARD)
        fan = VGroup(*[Arrow(pts.get_right(), lane.get_left(), buff=0.1, color=self.COLOR_DIM) for lane in lanes])
        merge = VGroup(*[Arrow(lane.get_right(), red.get_left(), buff=0.1, color=self.COLOR_DIM) for lane in lanes])
        self.play(Create(fan), Create(merge), run_time=self.STANDARD)
        self.wait(self.HOLD)

    # Scene 4 -----------------------------------------------------------------
    def scene_part2_inside_loop(self) -> None:
        title = Text("Part 2: rectangle must stay inside", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("inside the orthogonal loop region", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        loop = Polygon(
            LEFT * 4.2 + UP * 1.3,
            LEFT * 4.2 + DOWN * 2.3,
            LEFT * 1.8 + DOWN * 2.3,
            LEFT * 1.8 + DOWN * 0.8,
            LEFT * 3.1 + DOWN * 0.8,
            LEFT * 3.1 + UP * 0.2,
            LEFT * 1.4 + UP * 0.2,
            LEFT * 1.4 + UP * 2.0,
            LEFT * 3.2 + UP * 2.0,
            LEFT * 3.2 + UP * 1.3,
            color=self.COLOR_LOOP,
        ).set_stroke(width=4)
        interior = loop.copy().set_fill(self.COLOR_FILL, opacity=0.16).set_stroke(opacity=0)
        self.play(Create(loop), FadeIn(interior), run_time=self.STANDARD)

        valid = Rectangle(width=1.4, height=0.9, color=self.COLOR_GOOD).set_stroke(width=3)
        valid.move_to(LEFT * 2.7 + DOWN * 1.2)
        invalid = Rectangle(width=2.8, height=1.8, color=self.COLOR_RECT).set_stroke(width=3)
        invalid.move_to(LEFT * 2.0 + DOWN * 0.9)
        x = Text("X", color=self.COLOR_RECT).scale(self.SCALE_TEXT).move_to(invalid)
        self.play(Create(valid), run_time=self.FAST)
        self.play(Create(invalid), FadeIn(x, scale=0.95), run_time=self.STANDARD)
        self.wait(self.HOLD)

    # Scene 5 -----------------------------------------------------------------
    def scene_part2_scanline_pairs(self) -> None:
        title = Text("Scanline: process y-levels", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("corners arrive as (x0,x1) pairs per y", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        rows = VGroup(
            Text("y=5: (x0,x1) = (2,8)", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("y=4: (x0,x1) = (1,9)", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("y=3: (x0,x1) = (3,7)", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        rows.to_edge(RIGHT).shift(LEFT * 0.8)
        self.play(FadeIn(rows, shift=LEFT), run_time=self.STANDARD)

        scan = Line(LEFT * 6.2, LEFT * 0.8, color=self.COLOR_SCAN)
        scan.shift(UP * 1.2)
        scan_lbl = Text("scanline y", color=self.COLOR_SCAN).scale(self.SCALE_SMALL)
        scan_lbl.next_to(scan, UP, buff=0.1)
        self.play(Create(scan), FadeIn(scan_lbl, shift=UP * 0.1), run_time=self.STANDARD)
        self.play(scan.animate.shift(DOWN * 2.2), FadeOut(scan_lbl), run_time=self.LONG)
        self.wait(self.HOLD)

    # Scene 6 -----------------------------------------------------------------
    def scene_toggle_set_to_intervals(self) -> None:
        title = Text("Descending-edge toggle set", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("toggle x0 and x1 → pair edges into intervals", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        nl = self.numberline_with_ticks(10, length=6.6)
        nl.move_to(LEFT * 1.0 + UP * 0.8)
        lbl = Text("descending_edges", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        lbl.next_to(nl, UP, buff=0.25)
        self.play(FadeIn(nl), FadeIn(lbl), run_time=self.STANDARD)

        ticks = VGroup()
        for x in [2, 8, 1, 9]:
            t = self.edge_tick(nl, x, color=self.COLOR_ACC)
            ticks.add(t)
            self.play(Create(t), run_time=self.FAST)

        interval1 = self.interval_span(nl, 1, 2, color=self.COLOR_GOOD)
        interval2 = self.interval_span(nl, 8, 9, color=self.COLOR_GOOD)
        ilbl = Text("interior intervals", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        ilbl.next_to(interval1, DOWN, buff=0.15)
        self.play(FadeIn(interval1), FadeIn(interval2), FadeIn(ilbl), run_time=self.STANDARD)
        self.wait(self.HOLD)

    # Scene 7 -----------------------------------------------------------------
    def scene_candidate_tracking(self) -> None:
        title = Text("Candidate tracking", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("shrink intervals, drop invalid, update best", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        table_box = RoundedRectangle(width=6.4, height=3.2, corner_radius=0.2, color=self.COLOR_DIM)
        table_box.set_fill(self.COLOR_DIM, opacity=0.05)
        table_box.to_edge(LEFT).shift(RIGHT * 1.1 + DOWN * 0.1)
        header = Text("candidates", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        header.next_to(table_box, UP, buff=0.2)

        rows = VGroup(
            Text("(y_top=5, x_top=2, [1..9])", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("(y_top=5, x_top=8, [1..9])", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        rows.move_to(table_box)
        self.play(FadeIn(table_box), FadeIn(header), FadeIn(rows, shift=RIGHT), run_time=self.STANDARD)

        best = Text("best area = 0", color=self.COLOR_GOOD).scale(self.SCALE_TEXT)
        best.to_edge(RIGHT).shift(UP * 0.4)
        self.play(Write(best), run_time=self.STANDARD)

        shrink = Text("intersect with current interior", color=self.COLOR_ACC).scale(self.SCALE_SMALL)
        shrink.next_to(best, DOWN, buff=0.3)
        self.play(FadeIn(shrink, shift=DOWN * 0.1), run_time=self.STANDARD)

        new_rows = VGroup(
            Text("(y_top=5, x_top=2, [1..6])", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("(y_top=5, x_top=8, [8..9])", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        new_rows.move_to(rows)
        self.play(Transform(rows, new_rows), run_time=self.STANDARD)
        self.play(
            Transform(best, Text("best area = 18", color=self.COLOR_GOOD).scale(self.SCALE_TEXT).move_to(best)),
            run_time=self.STANDARD,
        )
        self.play(FadeOut(rows[1], shift=DOWN * 0.2), run_time=self.STANDARD)
        self.wait(self.HOLD)

    # Scene 8 -----------------------------------------------------------------
    def scene_fpga_part1_pair_farm(self) -> None:
        title = Text("FPGA Option A: Part 1 pair farm", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("replicate area lanes, max-reduce", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        blocks = VGroup()
        for name in ["Point\nRAM", "Pair\nScheduler", "P Area\nLanes", "Max\nReducer"]:
            b = RoundedRectangle(width=2.3, height=1.2, corner_radius=0.18, color=self.COLOR_DIM)
            b.set_fill(self.COLOR_DIM, opacity=0.06)
            t = Text(name, color=self.COLOR_TEXT).scale(self.SCALE_SMALL).move_to(b)
            blocks.add(VGroup(b, t))
        blocks.arrange(RIGHT, buff=0.55).move_to(ORIGIN).shift(DOWN * 0.2)
        arrows = VGroup(*[
            Arrow(blocks[i].get_right(), blocks[i + 1].get_left(), buff=0.12, color=self.COLOR_DIM)
            for i in range(len(blocks) - 1)
        ])
        self.play(FadeIn(blocks), Create(arrows), run_time=self.STANDARD)
        lanes = Text("P copies", color=self.COLOR_ACC).scale(self.SCALE_SMALL)
        lanes.next_to(blocks[2], DOWN, buff=0.2)
        self.play(FadeIn(lanes), run_time=self.STANDARD)
        self.wait(self.HOLD)

    # Scene 9 -----------------------------------------------------------------
    def scene_fpga_part2_scanline_machine(self) -> None:
        title = Text("FPGA Option B: scanline interval machine", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("toggle set + interval extraction + candidates", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        blocks = VGroup()
        for name in ["Sorter", "Toggle\nSet", "Intervals", "Candidates", "Evaluator"]:
            b = RoundedRectangle(width=2.0, height=1.1, corner_radius=0.18, color=self.COLOR_DIM)
            b.set_fill(self.COLOR_DIM, opacity=0.06)
            t = Text(name, color=self.COLOR_TEXT).scale(self.SCALE_SMALL).move_to(b)
            blocks.add(VGroup(b, t))
        blocks.arrange(RIGHT, buff=0.45).move_to(ORIGIN).shift(DOWN * 0.1)
        arrows = VGroup(*[
            Arrow(blocks[i].get_right(), blocks[i + 1].get_left(), buff=0.12, color=self.COLOR_DIM)
            for i in range(len(blocks) - 1)
        ])
        self.play(FadeIn(blocks), Create(arrows), run_time=self.STANDARD)

        callout = Text("toggle set is the hard part", color=self.COLOR_ACC).scale(self.SCALE_SMALL)
        callout.next_to(blocks[1], DOWN, buff=0.25)
        self.play(FadeIn(callout, shift=DOWN * 0.1), run_time=self.STANDARD)

        bitset = self.make_code_block([
            "compress x → bitset",
            "toggle = bit flip",
            "scan bits → intervals",
        ])
        bitset.to_edge(DOWN)
        self.play(FadeIn(bitset, shift=UP), run_time=self.STANDARD)
        self.wait(self.HOLD)

    # Scene 10 ----------------------------------------------------------------
    def scene_design_comparison(self) -> None:
        title = Text("Design comparison", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("pair farm (simple) vs scanline (structure)", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        table = VGroup(
            Text("Pair farm", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("Scanline", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("Simplicity: high", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("Simplicity: medium", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("Memory: low", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("Memory: more state", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("Part 2 support: no", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("Part 2 support: yes", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
        )
        table.arrange_in_grid(rows=4, cols=2, buff=0.5, aligned_edge=LEFT)
        box = SurroundingRectangle(table, color=self.COLOR_DIM, buff=0.35)
        box.set_fill(self.COLOR_DIM, opacity=0.05)
        group = VGroup(box, table).move_to(ORIGIN).shift(DOWN * 0.2)
        self.play(FadeIn(group, shift=UP * 0.1), run_time=self.STANDARD)
        self.wait(self.HOLD)

    # Scene 11 ----------------------------------------------------------------
    def scene_takeaway(self) -> None:
        title = Text("Takeaway", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("Turn geometry into intervals", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        bars = VGroup(*[
            Rectangle(width=9.8, height=0.25, color=self.COLOR_DIM).set_fill(self.COLOR_DIM, opacity=0.05)
            for _ in range(6)
        ])
        bars.arrange(DOWN, buff=0.22)
        bars.shift(DOWN * 0.2)
        scan = Rectangle(width=9.8, height=0.35, color=self.COLOR_SCAN)
        scan.set_fill(self.COLOR_SCAN, opacity=0.12)
        scan.move_to(bars[0])
        self.play(FadeIn(bars), FadeIn(scan), run_time=self.STANDARD)
        self.play(scan.animate.move_to(bars[-1]), run_time=self.LONG)
        self.wait(self.HOLD)

    # Scene 5 -----------------------------------------------------------------
    def scene_part2_scanline_pairs(self) -> None:
        title = Text("Scanline: process y-levels", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("corners arrive as (x0,x1) pairs per y", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        rows = VGroup(
            Text("y=5: (x0,x1) = (2,8)", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("y=4: (x0,x1) = (1,9)", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("y=3: (x0,x1) = (3,7)", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        rows.to_edge(RIGHT).shift(LEFT * 0.8)
        self.play(FadeIn(rows, shift=LEFT), run_time=self.STANDARD)

        scan = Line(LEFT * 6.2, LEFT * 0.8, color=self.COLOR_SCAN)
        scan.shift(UP * 1.2)
        scan_lbl = Text("scanline y", color=self.COLOR_SCAN).scale(self.SCALE_SMALL)
        scan_lbl.next_to(scan, UP, buff=0.1)
        self.play(Create(scan), FadeIn(scan_lbl, shift=UP * 0.1), run_time=self.STANDARD)
        self.play(scan.animate.shift(DOWN * 2.2), FadeOut(scan_lbl), run_time=self.LONG)
        self.wait(self.HOLD)

    # Scene 6 -----------------------------------------------------------------
    def scene_toggle_set_to_intervals(self) -> None:
        title = Text("Descending-edge toggle set", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("toggle x0 and x1 → pair edges into intervals", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        nl = self.numberline_with_ticks(10, length=6.6)
        nl.move_to(LEFT * 1.0 + UP * 0.8)
        lbl = Text("descending_edges", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        lbl.next_to(nl, UP, buff=0.25)
        self.play(FadeIn(nl), FadeIn(lbl), run_time=self.STANDARD)

        # Toggle a few x values.
        ticks = VGroup()
        for x in [2, 8, 1, 9]:
            t = self.edge_tick(nl, x, color=self.COLOR_ACC)
            ticks.add(t)
            self.play(Create(t), run_time=self.FAST)

        interval1 = self.interval_span(nl, 1, 2, color=self.COLOR_GOOD)
        interval2 = self.interval_span(nl, 8, 9, color=self.COLOR_GOOD)
        ilbl = Text("interior intervals", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        ilbl.next_to(interval1, DOWN, buff=0.15)
        self.play(FadeIn(interval1), FadeIn(interval2), FadeIn(ilbl), run_time=self.STANDARD)
        self.wait(self.HOLD)

    # Scene 7 -----------------------------------------------------------------
    def scene_candidate_tracking(self) -> None:
        title = Text("Candidate tracking", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("shrink intervals, drop invalid, update best", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        table_box = RoundedRectangle(width=6.4, height=3.2, corner_radius=0.2, color=self.COLOR_DIM)
        table_box.set_fill(self.COLOR_DIM, opacity=0.05)
        table_box.to_edge(LEFT).shift(RIGHT * 1.1 + DOWN * 0.1)
        header = Text("candidates", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        header.next_to(table_box, UP, buff=0.2)

        rows = VGroup(
            Text("(x_top=2, y_top=5, [1..9])", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("(x_top=8, y_top=5, [1..9])", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        rows.move_to(table_box)
        self.play(FadeIn(table_box), FadeIn(header), FadeIn(rows, shift=RIGHT), run_time=self.STANDARD)

        best = Text("best area = 0", color=self.COLOR_GOOD).scale(self.SCALE_TEXT)
        best.to_edge(RIGHT).shift(UP * 0.4)
        self.play(Write(best), run_time=self.STANDARD)

        # Show shrinking interval + dropping.
        shrink = Text("intersect with current interior", color=self.COLOR_ACC).scale(self.SCALE_SMALL)
        shrink.next_to(best, DOWN, buff=0.3)
        self.play(FadeIn(shrink, shift=DOWN * 0.1), run_time=self.STANDARD)
        new_rows = VGroup(
            Text("(x_top=2, y_top=5, [1..6])", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("(x_top=8, y_top=5, [8..9])", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        new_rows.move_to(rows)
        self.play(Transform(rows, new_rows), run_time=self.STANDARD)
        self.play(Transform(best, Text("best area = 18", color=self.COLOR_GOOD).scale(self.SCALE_TEXT).move_to(best)), run_time=self.STANDARD)
        self.play(FadeOut(rows[1], shift=DOWN * 0.2), run_time=self.STANDARD)
        self.wait(self.HOLD)

    # Scene 8 -----------------------------------------------------------------
    def scene_fpga_part1_pair_farm(self) -> None:
        title = Text("FPGA Option A: Part 1 pair farm", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("replicate area lanes, max-reduce", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        blocks = VGroup()
        for name in ["Point\nRAM", "Pair\nScheduler", "P Area\nLanes", "Max\nReducer"]:
            b = RoundedRectangle(width=2.3, height=1.2, corner_radius=0.18, color=self.COLOR_DIM)
            b.set_fill(self.COLOR_DIM, opacity=0.06)
            t = Text(name, color=self.COLOR_TEXT).scale(self.SCALE_SMALL).move_to(b)
            blocks.add(VGroup(b, t))
        blocks.arrange(RIGHT, buff=0.55).move_to(ORIGIN).shift(DOWN * 0.2)
        arrows = VGroup(*[
            Arrow(blocks[i].get_right(), blocks[i + 1].get_left(), buff=0.12, color=self.COLOR_DIM)
            for i in range(len(blocks) - 1)
        ])
        self.play(FadeIn(blocks), Create(arrows), run_time=self.STANDARD)
        lanes = Text("P copies", color=self.COLOR_ACC).scale(self.SCALE_SMALL)
        lanes.next_to(blocks[2], DOWN, buff=0.2)
        self.play(FadeIn(lanes), run_time=self.STANDARD)
        self.wait(self.HOLD)

    # Scene 9 -----------------------------------------------------------------
    def scene_fpga_part2_scanline_machine(self) -> None:
        title = Text("FPGA Option B: scanline interval machine", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("toggle set + interval extraction + candidates", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        blocks = VGroup()
        for name in ["Sorter", "Toggle\nSet", "Intervals", "Candidates", "Evaluator"]:
            b = RoundedRectangle(width=2.0, height=1.1, corner_radius=0.18, color=self.COLOR_DIM)
            b.set_fill(self.COLOR_DIM, opacity=0.06)
            t = Text(name, color=self.COLOR_TEXT).scale(self.SCALE_SMALL).move_to(b)
            blocks.add(VGroup(b, t))
        blocks.arrange(RIGHT, buff=0.45).move_to(ORIGIN).shift(DOWN * 0.1)
        arrows = VGroup(*[
            Arrow(blocks[i].get_right(), blocks[i + 1].get_left(), buff=0.12, color=self.COLOR_DIM)
            for i in range(len(blocks) - 1)
        ])
        self.play(FadeIn(blocks), Create(arrows), run_time=self.STANDARD)

        callout = Text("toggle set is the hard part", color=self.COLOR_ACC).scale(self.SCALE_SMALL)
        callout.next_to(blocks[1], DOWN, buff=0.25)
        self.play(FadeIn(callout, shift=DOWN * 0.1), run_time=self.STANDARD)

        bitset = self.make_code_block([
            "compress x → bitset",
            "toggle = bit flip",
            "scan bits → intervals",
        ])
        bitset.to_edge(DOWN)
        self.play(FadeIn(bitset, shift=UP), run_time=self.STANDARD)
        self.wait(self.HOLD)

    # Scene 10 ----------------------------------------------------------------
    def scene_design_comparison(self) -> None:
        title = Text("Design comparison", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("pair farm (simple) vs scanline (structure)", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        table = VGroup(
            Text("Pair farm", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("Scanline", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("Simplicity: high", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("Simplicity: medium", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("Memory: low", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("Memory: more state", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("Part 2 support: no", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("Part 2 support: yes", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
        )
        table.arrange_in_grid(rows=4, cols=2, buff=0.5, aligned_edge=LEFT)
        box = SurroundingRectangle(table, color=self.COLOR_DIM, buff=0.35)
        box.set_fill(self.COLOR_DIM, opacity=0.05)
        group = VGroup(box, table).move_to(ORIGIN).shift(DOWN * 0.2)
        self.play(FadeIn(group, shift=UP * 0.1), run_time=self.STANDARD)
        self.wait(self.HOLD)

    # Scene 11 ----------------------------------------------------------------
    def scene_takeaway(self) -> None:
        title = Text("Takeaway", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("Turn geometry into intervals", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        bars = VGroup(*[
            Rectangle(width=9.8, height=0.25, color=self.COLOR_DIM).set_fill(self.COLOR_DIM, opacity=0.05)
            for _ in range(6)
        ])
        bars.arrange(DOWN, buff=0.22)
        bars.shift(DOWN * 0.2)
        scan = Rectangle(width=9.8, height=0.35, color=self.COLOR_SCAN)
        scan.set_fill(self.COLOR_SCAN, opacity=0.12)
        scan.move_to(bars[0])
        self.play(FadeIn(bars), FadeIn(scan), run_time=self.STANDARD)
        self.play(scan.animate.move_to(bars[-1]), run_time=self.LONG)
        self.wait(self.HOLD)
