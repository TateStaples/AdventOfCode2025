"""animations/day7.py

Day 7 — Laboratories (Tachyon Splitters DP)

Storyboard: animations/day_by_day_video_scripts.md (Day 7)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
from manim import *


@dataclass(frozen=True)
class GridRef:
    grid: VGroup
    cells: Dict[Tuple[int, int], VGroup]
    width: int
    height: int
    cell_size: float


class Day7(Scene):
    # Timing
    FAST = 0.25
    STANDARD = 0.7
    LONG = 1.3
    HOLD = 28.0

    # Colors
    COLOR_TEXT = GRAY_E
    COLOR_DIM = GRAY_C
    COLOR_GRID = GRAY_B
    COLOR_CELL = GRAY_E
    COLOR_SPLITTER = YELLOW_E
    COLOR_BEAM = TEAL_A
    COLOR_TIMELINE = PURPLE_C
    COLOR_SPLIT = GREEN_C
    COLOR_ACC = BLUE_D

    # Scales
    SCALE_TITLE = 0.8
    SCALE_SUB = 0.55
    SCALE_TEXT = 0.5
    SCALE_SMALL = 0.42
    SCALE_TINY = 0.32
    SCALE_CODE = 0.34

    def construct(self) -> None:
        self.scene_hook()
        self.clear()
        self.scene_state_trick()
        self.clear()
        self.scene_update_rule()
        self.clear()
        self.scene_active_range()
        self.clear()
        self.scene_tiny_example()
        self.clear()
        self.scene_correctness()
        self.clear()
        self.scene_fpga_option_a_sequential()
        self.clear()
        self.scene_fpga_option_b_simd()
        self.clear()
        self.scene_split_popcount()
        self.clear()
        self.scene_takeaway()

    # Helpers -----------------------------------------------------------------
    def make_code_block(self, lines: List[str], scale: float | None = None) -> VGroup:
        use_scale = self.SCALE_CODE if scale is None else scale
        text = VGroup(
            *[Text(line, font="Monospace", color=self.COLOR_TEXT).scale(use_scale) for line in lines]
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        box = SurroundingRectangle(text, color=self.COLOR_DIM, buff=0.18)
        return VGroup(box, text)

    def make_counter(self, label: str, value: int = 0) -> Tuple[VGroup, Text]:
        lbl = Text(label, color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        val = Text(str(value), color=self.COLOR_ACC).scale(self.SCALE_SMALL)
        box = RoundedRectangle(width=2.6, height=0.95, corner_radius=0.15, color=self.COLOR_DIM)
        body = VGroup(lbl, val).arrange(DOWN, buff=0.1).move_to(box)
        return VGroup(box, body), val

    def update_counter_value(self, counter_value_text: Text, value: int) -> Animation:
        new_text = Text(str(value), color=self.COLOR_ACC).scale(self.SCALE_SMALL)
        new_text.move_to(counter_value_text)
        return Transform(counter_value_text, new_text)

    def build_grid(self, lines: List[str], cell_size: float = 0.55) -> GridRef:
        height = len(lines)
        width = max(len(line) for line in lines)
        padded = [line.ljust(width) for line in lines]
        cells: Dict[Tuple[int, int], VGroup] = {}
        grid = VGroup()
        for y in range(height):
            for x in range(width):
                ch = padded[y][x]
                is_space = ch == " "
                base = Square(side_length=cell_size, stroke_color=self.COLOR_GRID, stroke_width=1)
                base.set_fill(self.COLOR_CELL, opacity=0.07 if is_space else 0.12)
                txt_color = self.COLOR_SPLITTER if ch == "^" else self.COLOR_TEXT
                txt = Text(ch if ch != " " else " ", font="Monospace", color=txt_color)
                txt.scale(self.SCALE_TINY)
                txt.move_to(base)
                cell = VGroup(base, txt)
                cell.shift(RIGHT * (x * cell_size) + DOWN * (y * cell_size))
                cells[(x, y)] = cell
                grid.add(cell)
        grid.move_to(ORIGIN)
        grid.shift(UP * (height * cell_size / 2) + LEFT * (width * cell_size / 2))
        return GridRef(grid=grid, cells=cells, width=width, height=height, cell_size=cell_size)

    def cell_center(self, grid: GridRef, x: int, y: int) -> np.ndarray:
        return grid.cells[(x, y)].get_center()

    def timeline_slots(self, values: List[int], highlight: int | None = None) -> VGroup:
        slots = VGroup()
        for i, val in enumerate(values):
            rect = RoundedRectangle(width=0.75, height=0.75, corner_radius=0.12, color=self.COLOR_TIMELINE)
            rect.set_fill(self.COLOR_TIMELINE, opacity=0.10)
            if highlight is not None and i == highlight:
                rect.set_stroke(self.COLOR_SPLIT, width=4)
                rect.set_fill(self.COLOR_SPLIT, opacity=0.10)
            txt = Text(str(val), font="Monospace", color=WHITE).scale(self.SCALE_SMALL)
            txt.move_to(rect)
            slots.add(VGroup(rect, txt))
        slots.arrange(RIGHT, buff=0.12)
        return slots

    def bit_row(self, bits: List[bool], label: str = "splitters") -> VGroup:
        row = VGroup()
        for b in bits:
            ch = "^" if b else "·"
            color = self.COLOR_SPLITTER if b else self.COLOR_DIM
            row.add(Text(ch, font="Monospace", color=color).scale(self.SCALE_SMALL))
        row.arrange(RIGHT, buff=0.28)
        name = Text(label, color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        name.next_to(row, UP, buff=0.15)
        return VGroup(name, row)

    # Scenes ------------------------------------------------------------------
    def scene_hook(self) -> None:
        title = Text("Day 7 — Laboratories", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("One beam becomes many", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        lines = [
            "   S   ",
            "       ",
            "   ^   ",
            "       ",
            "  ^ ^  ",
        ]
        grid = self.build_grid(lines, cell_size=0.62)
        grid.grid.shift(LEFT * 3.1 + DOWN * 0.2)
        self.play(FadeIn(grid.grid))

        splits_counter, splits_val = self.make_counter("splits (Part 1)", 0)
        splits_counter.to_edge(RIGHT).shift(UP * 1.2)
        timelines_counter, timelines_val = self.make_counter("timelines (Part 2)", 1)
        timelines_counter.next_to(splits_counter, DOWN, buff=0.4)
        self.play(FadeIn(splits_counter, shift=LEFT), FadeIn(timelines_counter, shift=LEFT))

        beam = Dot(color=self.COLOR_BEAM)
        beam.move_to(self.cell_center(grid, 3, 0))
        self.play(FadeIn(beam), run_time=self.FAST)

        self.play(beam.animate.move_to(self.cell_center(grid, 3, 2)), run_time=self.STANDARD)
        self.play(Flash(grid.cells[(3, 2)][1], color=self.COLOR_SPLIT, flash_radius=0.35), run_time=self.FAST)

        left_beam = Dot(color=self.COLOR_BEAM).move_to(self.cell_center(grid, 2, 3))
        right_beam = Dot(color=self.COLOR_BEAM).move_to(self.cell_center(grid, 4, 3))
        self.play(FadeIn(left_beam, shift=LEFT * 0.2), FadeIn(right_beam, shift=RIGHT * 0.2), FadeOut(beam), run_time=self.STANDARD)
        self.play(
            self.update_counter_value(splits_val, 1),
            self.update_counter_value(timelines_val, 2),
            run_time=self.STANDARD,
        )
        self.play(left_beam.animate.move_to(self.cell_center(grid, 2, 4)), right_beam.animate.move_to(self.cell_center(grid, 4, 4)), run_time=self.STANDARD)
        self.wait(self.HOLD)

    def scene_state_trick(self) -> None:
        title = Text("The 1D state trick", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("timelines[x] counts beams at x", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        lines = [
            "   S   ",
            "       ",
            "   ^   ",
            "       ",
            "  ^ ^  ",
        ]
        grid = self.build_grid(lines, cell_size=0.6)
        grid.grid.shift(LEFT * 3.0 + UP * 0.2)
        self.play(FadeIn(grid.grid))

        timeline = self.timeline_slots([0, 0, 0, 1, 0, 0, 0], highlight=3)
        timeline_label = Text("timelines[x]", color=self.COLOR_TIMELINE).scale(self.SCALE_SUB)
        timeline_label.next_to(timeline, UP, buff=0.2)
        timeline_group = VGroup(timeline_label, timeline)
        timeline_group.to_edge(DOWN).shift(RIGHT * 0.2)
        self.play(FadeIn(timeline_group, shift=UP))

        fade_card = Text("O(W) memory", color=self.COLOR_TEXT).scale(self.SCALE_TEXT)
        fade_card.next_to(timeline_group, LEFT, buff=0.8)
        self.play(FadeIn(fade_card, shift=RIGHT * 0.2), run_time=self.STANDARD)

        self.play(grid.grid.animate.set_opacity(0.18), run_time=self.STANDARD)
        self.wait(self.LONG)

        # Show a single layer-to-layer update.
        updated = self.timeline_slots([0, 0, 1, 0, 1, 0, 0])
        updated.move_to(timeline)
        self.play(Transform(timeline, updated), run_time=self.STANDARD)
        self.wait(self.HOLD)

    def scene_update_rule(self) -> None:
        title = Text("Layer sweep update rule", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("splitter: clear center, add to neighbors", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        counts = [0, 0, 0, 2, 0, 0, 0]
        splitters = [False, False, False, True, False, False, False]

        row = self.bit_row(splitters, label="splitters in this layer")
        row.shift(LEFT * 2.6 + UP * 1.2)
        timeline = self.timeline_slots(counts, highlight=3)
        timeline.shift(LEFT * 2.6 + UP * 0.0)

        rule = self.make_code_block([
            "if splitter[x] and count>0:",
            "  splits += 1",
            "  timelines[x] = 0",
            "  timelines[x-1] += count",
            "  timelines[x+1] += count",
        ])
        rule.to_edge(RIGHT).shift(DOWN * 0.2)

        splits_counter, splits_val = self.make_counter("splits", 0)
        splits_counter.to_edge(DOWN).shift(RIGHT * 4.1)
        self.play(FadeIn(row), FadeIn(timeline), FadeIn(rule), FadeIn(splits_counter, shift=UP * 0.2))

        # Animate clearing + neighbor adds.
        cleared = self.timeline_slots([0, 0, 0, 0, 0, 0, 0], highlight=3)
        cleared.move_to(timeline)
        self.play(Transform(timeline, cleared), run_time=self.STANDARD)
        plus_left = Text("+2", font="Monospace", color=self.COLOR_SPLIT).scale(self.SCALE_SMALL)
        plus_right = Text("+2", font="Monospace", color=self.COLOR_SPLIT).scale(self.SCALE_SMALL)
        plus_left.next_to(timeline[2], UP, buff=0.15)
        plus_right.next_to(timeline[4], UP, buff=0.15)
        self.play(FadeIn(plus_left, shift=DOWN * 0.1), FadeIn(plus_right, shift=DOWN * 0.1), run_time=self.FAST)
        updated = self.timeline_slots([0, 0, 2, 0, 2, 0, 0])
        updated.move_to(timeline)
        self.play(Transform(timeline, updated), FadeOut(plus_left), FadeOut(plus_right), run_time=self.STANDARD)
        self.play(self.update_counter_value(splits_val, 1), run_time=self.STANDARD)
        self.wait(self.HOLD)

    def scene_active_range(self) -> None:
        title = Text("Active range expands like a cone", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("skip edges that must be zero", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        values = [0, 0, 0, 1, 0, 0, 0]
        timeline = self.timeline_slots(values)
        timeline.shift(DOWN * 0.2)
        label = Text("timelines[x]", color=self.COLOR_TIMELINE).scale(self.SCALE_SUB)
        label.next_to(timeline, UP, buff=0.25)
        self.play(FadeIn(label), FadeIn(timeline))

        min_marker = Triangle(color=self.COLOR_SPLIT, fill_opacity=1.0).scale(0.18)
        max_marker = Triangle(color=self.COLOR_SPLIT, fill_opacity=1.0).scale(0.18).rotate(PI)
        min_marker.next_to(timeline[3], UP, buff=0.15)
        max_marker.next_to(timeline[3], UP, buff=0.15)
        self.play(FadeIn(min_marker), FadeIn(max_marker), run_time=self.FAST)

        for (lo, hi) in [(3, 3), (2, 4), (1, 5)]:
            self.play(
                min_marker.animate.move_to(timeline[lo].get_top() + UP * 0.15),
                max_marker.animate.move_to(timeline[hi].get_top() + UP * 0.15),
                run_time=self.STANDARD,
            )
        self.wait(self.HOLD)

    def scene_tiny_example(self) -> None:
        title = Text("Tiny worked example", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("[0,0,1,0,0] with ^ at center", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        before = self.timeline_slots([0, 0, 1, 0, 0], highlight=2)
        after = self.timeline_slots([0, 1, 0, 1, 0])
        before.move_to(LEFT * 3.0)
        after.move_to(RIGHT * 3.0)
        arrow = Arrow(before.get_right(), after.get_left(), buff=0.3, color=self.COLOR_TEXT)

        self.play(FadeIn(before, shift=LEFT), Create(arrow), FadeIn(after, shift=RIGHT), run_time=self.STANDARD)
        self.wait(self.HOLD)

    def scene_correctness(self) -> None:
        title = Text("Why the DP is correct", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        self.play(Write(title))

        card = RoundedRectangle(width=11.2, height=3.2, corner_radius=0.2, color=self.COLOR_DIM)
        card.set_fill(self.COLOR_DIM, opacity=0.06)
        inv = Text("Invariant: timelines[x] == number of beams at x", color=self.COLOR_TEXT).scale(self.SCALE_TEXT)
        inv.move_to(card.get_center() + UP * 0.6)
        note = Text("A splitter rewrites beams exactly like the physics.", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        note.next_to(inv, DOWN, buff=0.35)
        self.play(Create(card), Write(inv), FadeIn(note, shift=DOWN))

        example = self.timeline_slots([0, 0, 3, 0, 0], highlight=2)
        example.next_to(card, DOWN, buff=0.7)
        sum_line = Text("sum(timelines) == number of timelines", color=self.COLOR_ACC).scale(self.SCALE_SMALL)
        sum_line.next_to(example, DOWN, buff=0.25)
        self.play(FadeIn(example), Write(sum_line))
        self.wait(self.HOLD)

    def scene_fpga_option_a_sequential(self) -> None:
        title = Text("FPGA Option A: sequential sweep", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("RAM + read-modify-write micro-sequence", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        ram = RoundedRectangle(width=4.0, height=2.3, corner_radius=0.18, color=self.COLOR_TIMELINE)
        ram.set_fill(self.COLOR_TIMELINE, opacity=0.08)
        ram_label = Text("timelines RAM\n(dual-port)", color=self.COLOR_TIMELINE).scale(self.SCALE_SMALL)
        ram_label.move_to(ram)

        rowbuf = RoundedRectangle(width=4.0, height=1.1, corner_radius=0.18, color=self.COLOR_SPLITTER)
        rowbuf.set_fill(self.COLOR_SPLITTER, opacity=0.06)
        rowbuf_label = Text("splitter row buffer", color=self.COLOR_SPLITTER).scale(self.SCALE_SMALL)
        rowbuf_label.move_to(rowbuf)

        fsm = RoundedRectangle(width=4.0, height=1.5, corner_radius=0.18, color=self.COLOR_DIM)
        fsm.set_fill(self.COLOR_DIM, opacity=0.06)
        fsm_label = Text("update FSM", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        fsm_label.next_to(fsm, UP, buff=0.15)

        blocks = VGroup(VGroup(ram, ram_label), VGroup(rowbuf, rowbuf_label)).arrange(DOWN, buff=0.6)
        blocks.shift(LEFT * 3.0)
        fsm_group = VGroup(fsm, fsm_label)
        fsm_group.to_edge(RIGHT).shift(DOWN * 0.1)

        a1 = Arrow(blocks[1].get_right(), blocks[0].get_right(), buff=0.1, color=self.COLOR_TEXT)
        a2 = Arrow(fsm_group.get_left(), blocks[0].get_right(), buff=0.1, color=self.COLOR_TEXT)
        self.play(FadeIn(blocks), FadeIn(fsm_group), Create(a1), Create(a2))

        steps = self.make_code_block([
            "read count = timelines[x]",
            "if split & count>0:",
            "  write timelines[x]=0",
            "  timelines[x-1]+=count",
            "  timelines[x+1]+=count",
        ])
        steps.to_edge(DOWN)
        self.play(FadeIn(steps, shift=UP))

        hazard = Text("Hazard: neighbor updates overlap", color=self.COLOR_SPLIT).scale(self.SCALE_SMALL)
        hazard.next_to(fsm, DOWN, buff=0.3)
        self.play(FadeIn(hazard, shift=UP * 0.2), run_time=self.STANDARD)
        self.wait(self.HOLD)

    def scene_fpga_option_b_simd(self) -> None:
        title = Text("FPGA Option B: wide SIMD stencil", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("accumulate contributions per destination", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        counts = [0, 2, 0, 5, 0, 1, 0]
        splits = [False, True, False, True, False, False, False]
        base = self.timeline_slots(counts)
        base_label = Text("counts", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        base_label.next_to(base, UP, buff=0.15)

        split_bits = self.bit_row(splits, label="splitters")
        split_bits.next_to(base, UP, buff=0.9)

        self.play(FadeIn(split_bits), FadeIn(base_label), FadeIn(base))

        left_shift = self.timeline_slots([2, 0, 5, 0, 0, 0, 0])
        right_shift = self.timeline_slots([0, 0, 0, 0, 1, 0, 0])
        left_shift.next_to(base, DOWN, buff=0.5)
        right_shift.next_to(left_shift, DOWN, buff=0.35)
        ltxt = Text("delta_from_right (shift-left)", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        rtxt = Text("delta_from_left (shift-right)", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        ltxt.next_to(left_shift, UP, buff=0.15)
        rtxt.next_to(right_shift, UP, buff=0.15)
        self.play(FadeIn(ltxt), FadeIn(left_shift), FadeIn(rtxt), FadeIn(right_shift), run_time=self.STANDARD)

        formula = self.make_code_block([
            "next[x] = (not split[x])*count[x]",
            "        + delta_from_left[x]",
            "        + delta_from_right[x]",
        ])
        formula.to_edge(RIGHT).shift(DOWN * 1.0)
        self.play(FadeIn(formula, shift=LEFT), run_time=self.STANDARD)
        self.wait(self.HOLD)

    def scene_split_popcount(self) -> None:
        title = Text("Counting splits in hardware", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("active_split = splitter & (count>0)", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        active = [False, True, False, True, False, False, True]
        bits = self.bit_row(active, label="active_split bits")
        bits.shift(LEFT * 2.6 + UP * 0.8)
        self.play(FadeIn(bits, shift=RIGHT * 0.2), run_time=self.STANDARD)

        tree = VGroup(
            RoundedRectangle(width=2.2, height=0.9, corner_radius=0.15, color=self.COLOR_DIM),
            RoundedRectangle(width=2.2, height=0.9, corner_radius=0.15, color=self.COLOR_DIM),
            RoundedRectangle(width=2.2, height=0.9, corner_radius=0.15, color=self.COLOR_DIM),
        ).arrange(DOWN, buff=0.35)
        for b in tree:
            b.set_fill(self.COLOR_DIM, opacity=0.06)
        tree.to_edge(RIGHT).shift(DOWN * 0.3)
        labels = VGroup(
            Text("popcount", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("adder tree", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("sum", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
        )
        for i in range(3):
            labels[i].move_to(tree[i])
        self.play(FadeIn(tree), FadeIn(labels), run_time=self.STANDARD)

        counter, counter_val = self.make_counter("splits +=", 0)
        counter.to_edge(DOWN).shift(LEFT * 3.2)
        self.play(FadeIn(counter, shift=UP * 0.2))
        self.play(self.update_counter_value(counter_val, 3), run_time=self.STANDARD)
        self.wait(self.HOLD)

    def scene_takeaway(self) -> None:
        title = Text("Takeaway", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("A 2D picture collapses into 1D state", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        lines = [
            "   S   ",
            "       ",
            "  ^ ^  ",
            "       ",
            " ^   ^ ",
        ]
        grid = self.build_grid(lines, cell_size=0.62)
        grid.grid.shift(LEFT * 3.0 + DOWN * 0.1)
        timeline = self.timeline_slots([0, 1, 0, 2, 0, 1, 0])
        timeline.to_edge(RIGHT).shift(DOWN * 0.2)
        tlbl = Text("timelines[x]", color=self.COLOR_TIMELINE).scale(self.SCALE_SUB)
        tlbl.next_to(timeline, UP, buff=0.2)
        self.play(FadeIn(grid.grid), FadeIn(tlbl), FadeIn(timeline), run_time=self.STANDARD)

        self.play(grid.grid.animate.set_opacity(0.12), run_time=self.STANDARD)
        self.play(timeline.animate.scale(1.05), run_time=self.FAST)
        self.play(timeline.animate.scale(1 / 1.05), run_time=self.FAST)
        end = Text("Tiny array. Big story.", color=self.COLOR_TEXT).scale(0.9)
        end.to_edge(DOWN)
        self.play(Write(end))
        self.wait(self.HOLD)
