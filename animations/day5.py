"""Day 5: Cafeteria (Intervals + IDs)

Storyboard target: 6:00–7:30

Core idea:
- Convert inclusive [a,b] into half-open [a,b+1).
- Sort + merge ranges into disjoint blocks once.
- Part 2: union size is sum of (end-start).
- Part 1: count IDs in union via lower_bound(b) - lower_bound(a).

FPGA thread:
- Option A: sorting + merge engine + binary-search FSM into ID RAM.
- Option B: streaming two-pointer merge (linear pass).
- Option C: bitmap when the value universe is small.
"""

from __future__ import annotations

from typing import Iterable

from manim import *


class Day5(Scene):
    # Timing (intentionally generous for student readability)
    FAST = 0.9
    STANDARD = 2.2
    LONG = 4.0
    HOLD = 10.0

    # Palette
    COLOR_RANGE = BLUE_C
    COLOR_MERGED = TEAL_C
    COLOR_ID = GOLD_E
    COLOR_BUFFER = PURPLE_C
    COLOR_ACCUM = GREEN_C
    COLOR_TEXT = GRAY_E
    COLOR_BAD = RED

    # Example from the prompt
    EXAMPLE_RANGES_INCL = [(3, 5), (10, 14), (16, 20), (12, 18)]
    EXAMPLE_IDS = [1, 5, 8, 11, 17, 32]

    def construct(self) -> None:
        self.scene_hook()
        self.clear()
        self.scene_half_open()
        self.clear()
        self.scene_sort_and_merge()
        self.clear()
        self.scene_part2_union_size()
        self.clear()
        self.scene_part1_lower_bound()
        self.clear()
        self.scene_example_walkthrough()
        self.clear()
        self.scene_fpga_option_a_binary_search_fsm()
        self.clear()
        self.scene_fpga_option_b_two_pointer()
        self.clear()
        self.scene_fpga_option_c_bitmap()
        self.clear()
        self.scene_takeaway()

    # -------------------- helpers --------------------
    def make_code_block(self, lines: list[str], width: float = 6.4) -> VGroup:
        text = VGroup(*[Text(line, font="Monospace", color=self.COLOR_TEXT).scale(0.34) for line in lines])
        text.arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        box = SurroundingRectangle(text, color=self.COLOR_TEXT, buff=0.2)
        block = VGroup(box, text)
        block.width = width
        return block

    def make_counter_box(self, label: str, value: int, color: str) -> VGroup:
        box = RoundedRectangle(width=4.35, height=1.05, corner_radius=0.2, color=color)
        lbl = Text(label, color=color).scale(0.42)
        lbl.move_to(box.get_left() + RIGHT * 1.9)
        val = Text(str(value), color=WHITE).scale(0.62)
        val.move_to(box.get_right() + LEFT * 0.75)
        return VGroup(box, lbl, val)

    def update_counter_value(self, counter: VGroup, value: int) -> Animation:
        new_val = Text(str(value), color=WHITE).scale(0.62)
        new_val.move_to(counter[2])
        return Transform(counter[2], new_val)

    def axis_for_example(self) -> NumberLine:
        axis = NumberLine(x_range=[0, 22, 1], include_numbers=True, color=WHITE)
        axis.width = 10.2
        return axis

    def interval_on_axis(
        self,
        axis: NumberLine,
        start: int,
        end: int,
        label: str,
        color: str,
        height: float = 0.45,
        fill_opacity: float = 0.35,
    ) -> VGroup:
        left = axis.n2p(start)
        right = axis.n2p(end)
        width = right[0] - left[0]
        bar = Rectangle(width=width, height=height, color=color, fill_color=color, fill_opacity=fill_opacity)
        bar.move_to((left + right) / 2)
        if label:
            text = Text(label, color=WHITE).scale(0.38)
            text.move_to(bar.get_center())
            return VGroup(bar, text)
        return VGroup(bar)

    def to_half_open(self, ranges_incl: Iterable[tuple[int, int]]) -> list[tuple[int, int]]:
        return [(a, b + 1) for (a, b) in ranges_incl]

    def merge_sorted_half_open(self, ranges_sorted: list[tuple[int, int]]) -> list[tuple[int, int]]:
        out: list[tuple[int, int]] = []
        if not ranges_sorted:
            return out
        cur_s, cur_e = ranges_sorted[0]
        for s, e in ranges_sorted[1:]:
            if s < cur_e:
                cur_e = max(cur_e, e)
            else:
                out.append((cur_s, cur_e))
                cur_s, cur_e = s, e
        out.append((cur_s, cur_e))
        return out

    # -------------------- scenes --------------------
    def scene_hook(self) -> None:
        title = Text("Day 5: Cafeteria", color=WHITE).scale(0.9).to_edge(UP)
        subtitle = Text("Fresh ranges + available IDs", color=self.COLOR_TEXT).scale(0.56)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(FadeIn(title), FadeIn(subtitle, shift=DOWN), run_time=self.STANDARD)

        left_panel = RoundedRectangle(width=5.7, height=5.6, corner_radius=0.2, color=self.COLOR_RANGE)
        left_panel.to_edge(LEFT, buff=0.7).shift(DOWN * 0.2)
        right_panel = RoundedRectangle(width=5.7, height=5.6, corner_radius=0.2, color=self.COLOR_ID)
        right_panel.to_edge(RIGHT, buff=0.7).shift(DOWN * 0.2)
        self.play(Create(left_panel), Create(right_panel), run_time=self.STANDARD)

        ranges_lbl = Text("Fresh ranges (inclusive)", color=self.COLOR_RANGE).scale(0.52)
        ids_lbl = Text("Available IDs", color=self.COLOR_ID).scale(0.52)
        ranges_lbl.next_to(left_panel.get_top(), DOWN, buff=0.25)
        ids_lbl.next_to(right_panel.get_top(), DOWN, buff=0.25)
        self.play(Write(ranges_lbl), Write(ids_lbl), run_time=self.STANDARD)

        ranges = VGroup(
            *[Text(f"{a}-{b}", font="Monospace", color=WHITE).scale(0.54) for (a, b) in self.EXAMPLE_RANGES_INCL]
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        ranges.move_to(left_panel.get_center() + UP * 0.4 + LEFT * 0.2)

        ids_sorted = sorted(self.EXAMPLE_IDS)
        ids = VGroup(*[Text(str(x), font="Monospace", color=WHITE).scale(0.54) for x in ids_sorted])
        ids.arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        ids.move_to(right_panel.get_center() + UP * 0.4 + LEFT * 0.2)

        self.play(FadeIn(ranges, shift=LEFT), FadeIn(ids, shift=RIGHT), run_time=self.STANDARD)

        p1 = self.make_counter_box("Part 1: fresh IDs", 0, self.COLOR_ACCUM)
        p2 = self.make_counter_box("Part 2: union size", 0, self.COLOR_MERGED)
        counters = VGroup(p1, p2).arrange(DOWN, buff=0.2)
        counters.move_to(DOWN * 3.15)
        self.play(FadeIn(counters, shift=UP), run_time=self.STANDARD)

        # Stamp fresh IDs in the example.
        half_open = self.to_half_open(self.EXAMPLE_RANGES_INCL)
        merged = self.merge_sorted_half_open(sorted(half_open, key=lambda t: t[0]))
        hits = 0
        for t in ids:
            x = int(t.text)
            is_hit = any(a <= x < b for (a, b) in merged)
            stamp = Text("FRESH" if is_hit else "spoiled", color=self.COLOR_ACCUM if is_hit else self.COLOR_BAD)
            stamp.scale(0.34)
            stamp.next_to(t, RIGHT, buff=0.35)
            self.play(FadeIn(stamp, shift=RIGHT), run_time=self.FAST)
            if is_hit:
                hits += 1
                self.play(self.update_counter_value(p1, hits), run_time=self.FAST)

        self.wait(self.HOLD)

    def scene_half_open(self) -> None:
        title = Text("Half-open intervals make unions easy", color=WHITE).scale(0.82).to_edge(UP)
        self.play(FadeIn(title), run_time=self.STANDARD)

        axis = self.axis_for_example().shift(UP * 0.2)
        self.play(Create(axis), run_time=self.STANDARD)

        incl = self.interval_on_axis(axis, 10, 14, "[10,14]", self.COLOR_RANGE, height=0.58, fill_opacity=0.2)
        incl.shift(UP * 1.0)
        half = self.interval_on_axis(axis, 10, 15, "[10,15)", self.COLOR_MERGED, height=0.58, fill_opacity=0.25)
        half.shift(DOWN * 0.2)
        self.play(FadeIn(incl), FadeIn(half), run_time=self.STANDARD)

        rule = MathTex(r"[a,b] \;\Rightarrow\; [a, b{+}1)", color=self.COLOR_TEXT).scale(0.9)
        rule.to_edge(RIGHT, buff=0.7).shift(UP * 1.15)
        self.play(FadeIn(rule, shift=LEFT), run_time=self.STANDARD)

        bump = Text("+1", color=self.COLOR_ACCUM).scale(0.55)
        bump.next_to(incl[0].get_right(), UP, buff=0.12)
        self.play(Flash(incl[0].get_right(), color=self.COLOR_ACCUM, flash_radius=0.45), FadeIn(bump), run_time=self.STANDARD)
        self.play(TransformFromCopy(incl, half), run_time=self.LONG)

        touch_a = self.interval_on_axis(axis, 3, 6, "[3,6)", self.COLOR_MERGED, height=0.45, fill_opacity=0.25)
        touch_b = self.interval_on_axis(axis, 6, 10, "[6,10)", self.COLOR_MERGED, height=0.45, fill_opacity=0.25)
        touch = VGroup(touch_a, touch_b).arrange(RIGHT, buff=0)
        touch.move_to(DOWN * 2.1)
        note = Text("Touching intervals don't overlap", color=self.COLOR_TEXT).scale(0.5)
        note.next_to(touch, DOWN, buff=0.25)
        seam = Line(touch_a[0].get_right(), touch_a[0].get_right() + UP * 0.55, color=YELLOW)
        self.play(FadeIn(touch), Create(seam), FadeIn(note, shift=DOWN), run_time=self.STANDARD)
        self.wait(self.HOLD)

    def scene_sort_and_merge(self) -> None:
        title = Text("Sort + merge ranges", color=WHITE).scale(0.86).to_edge(UP)
        self.play(FadeIn(title), run_time=self.STANDARD)

        axis = self.axis_for_example().shift(DOWN * 2.0)
        self.play(Create(axis), run_time=self.STANDARD)

        unsorted_label = Text("unsorted", color=self.COLOR_TEXT).scale(0.48)
        sorted_label = Text("sorted", color=self.COLOR_TEXT).scale(0.48)
        merged_label = Text("merged", color=self.COLOR_TEXT).scale(0.48)
        labels = VGroup(unsorted_label, sorted_label, merged_label).arrange(RIGHT, buff=2.2)
        labels.to_edge(UP, buff=1.35)
        self.play(FadeIn(labels), run_time=self.STANDARD)

        half_open = self.to_half_open(self.EXAMPLE_RANGES_INCL)
        unsorted = list(half_open)
        sorted_ranges = sorted(half_open, key=lambda t: t[0])
        merged = self.merge_sorted_half_open(sorted_ranges)

        def bars_for(ranges: list[tuple[int, int]], color: str, y: float) -> VGroup:
            bars = VGroup(*[self.interval_on_axis(axis, a, b, f"[{a},{b})", color, height=0.42, fill_opacity=0.25) for (a, b) in ranges])
            bars.arrange(DOWN, aligned_edge=LEFT, buff=0.18)
            bars.move_to(ORIGIN + LEFT * 4.1 + UP * y)
            return bars

        uns = bars_for(unsorted, self.COLOR_RANGE, y=1.35)
        srt = bars_for(sorted_ranges, self.COLOR_RANGE, y=0.05)
        mrg = bars_for(merged, self.COLOR_MERGED, y=-1.2)
        self.play(FadeIn(uns, shift=LEFT), run_time=self.STANDARD)
        self.wait(self.STANDARD)

        sort_arrow = Arrow(uns.get_right(), srt.get_left(), buff=0.25, color=WHITE)
        merge_arrow = Arrow(srt.get_right(), mrg.get_left(), buff=0.25, color=WHITE)
        self.play(Create(sort_arrow), Create(merge_arrow), run_time=self.STANDARD)
        self.play(TransformFromCopy(uns, srt), run_time=self.LONG)

        cursor = Triangle(color=YELLOW).scale(0.25)
        cursor.rotate(PI)
        cursor.next_to(srt[0], LEFT, buff=0.2)
        self.play(FadeIn(cursor), run_time=self.FAST)

        merge_rule = self.make_code_block(
            [
                "scan sorted intervals:",
                "  if s < cur_end: cur_end = max(cur_end, e)",
                "  else: emit(cur); cur = (s,e)",
            ],
            width=6.3,
        )
        merge_rule.to_edge(RIGHT, buff=0.75).shift(UP * 0.55)
        self.play(FadeIn(merge_rule, shift=LEFT), run_time=self.STANDARD)
        self.wait(self.LONG)

        self.play(cursor.animate.next_to(srt[1], LEFT, buff=0.2), run_time=self.FAST)
        self.play(cursor.animate.next_to(srt[2], LEFT, buff=0.2), run_time=self.FAST)
        self.play(cursor.animate.next_to(srt[3], LEFT, buff=0.2), run_time=self.FAST)
        self.play(FadeIn(mrg, shift=RIGHT), run_time=self.LONG)
        self.wait(self.HOLD)

    def scene_part2_union_size(self) -> None:
        title = Text("Part 2: union size", color=WHITE).scale(0.9).to_edge(UP)
        self.play(FadeIn(title), run_time=self.STANDARD)

        axis = self.axis_for_example().shift(UP * 0.4)
        self.play(Create(axis), run_time=self.STANDARD)

        merged = self.merge_sorted_half_open(sorted(self.to_half_open(self.EXAMPLE_RANGES_INCL), key=lambda t: t[0]))
        blocks = VGroup(*[self.interval_on_axis(axis, a, b, f"[{a},{b})", self.COLOR_MERGED, height=0.7, fill_opacity=0.25) for (a, b) in merged])
        blocks.arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        blocks.move_to(ORIGIN + UP * 0.9)
        self.play(FadeIn(blocks, shift=DOWN), run_time=self.STANDARD)

        total = 0
        total_box = self.make_counter_box("union size", total, self.COLOR_MERGED)
        total_box.to_edge(RIGHT, buff=0.8).shift(DOWN * 1.35)
        self.play(FadeIn(total_box, shift=LEFT), run_time=self.STANDARD)

        for (a, b), block in zip(merged, blocks):
            length = b - a
            brace = Brace(block[0], DOWN)
            lbl = Text(f"len = {b}-{a} = {length}", color=WHITE).scale(0.46)
            lbl.next_to(brace, DOWN, buff=0.15)
            self.play(FadeIn(brace), FadeIn(lbl, shift=DOWN), run_time=self.STANDARD)
            total += length
            self.play(self.update_counter_value(total_box, total), run_time=self.STANDARD)
            self.play(FadeOut(brace), FadeOut(lbl), run_time=self.STANDARD)

        self.wait(self.HOLD)

    def scene_part1_lower_bound(self) -> None:
        title = Text("Part 1: count IDs with lower_bound", color=WHITE).scale(0.82).to_edge(UP)
        self.play(FadeIn(title), run_time=self.STANDARD)

        merged = self.merge_sorted_half_open(sorted(self.to_half_open(self.EXAMPLE_RANGES_INCL), key=lambda t: t[0]))
        (a, b) = merged[0]  # [3,6)

        left_panel = RoundedRectangle(width=6.2, height=5.8, corner_radius=0.2, color=self.COLOR_ID)
        left_panel.to_edge(LEFT, buff=0.7).shift(DOWN * 0.2)
        right_panel = RoundedRectangle(width=5.0, height=3.2, corner_radius=0.2, color=self.COLOR_MERGED)
        right_panel.to_edge(RIGHT, buff=0.9).shift(UP * 0.2)
        self.play(Create(left_panel), Create(right_panel), run_time=self.STANDARD)

        ids_sorted = sorted(self.EXAMPLE_IDS)
        id_texts = VGroup(*[Text(f"{x}", font="Monospace", color=WHITE).scale(0.54) for x in ids_sorted])
        id_texts.arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        id_texts.move_to(left_panel.get_center() + UP * 0.6 + LEFT * 0.9)
        idx_texts = VGroup(*[Text(f"{i}", font="Monospace", color=self.COLOR_TEXT).scale(0.42) for i in range(len(ids_sorted))])
        idx_texts.arrange(DOWN, aligned_edge=RIGHT, buff=0.25)
        idx_texts.next_to(id_texts, LEFT, buff=0.35)
        self.play(FadeIn(id_texts, shift=RIGHT), FadeIn(idx_texts, shift=RIGHT), run_time=self.STANDARD)

        axis = self.axis_for_example().scale(0.82)
        axis.move_to(right_panel.get_center() + DOWN * 0.2)
        interval = self.interval_on_axis(axis, a, b, f"[{a},{b})", self.COLOR_MERGED, height=0.6, fill_opacity=0.25)
        interval.shift(UP * 0.75)
        self.play(Create(axis), FadeIn(interval), run_time=self.STANDARD)

        formula = MathTex(r"\#\,\text{IDs in }[a,b) = \text{lb}(b) - \text{lb}(a)", color=WHITE).scale(0.7)
        formula.next_to(left_panel, DOWN, buff=0.25)
        self.play(FadeIn(formula, shift=DOWN), run_time=self.STANDARD)
        self.wait(self.LONG)

        lb_a = Text(f"lb({a})", color=self.COLOR_ACCUM).scale(0.52)
        lb_b = Text(f"lb({b})", color=self.COLOR_ACCUM).scale(0.52)
        lb_a.next_to(right_panel.get_top(), DOWN, buff=0.25)
        lb_b.next_to(lb_a, DOWN, buff=0.15, aligned_edge=LEFT)
        self.play(FadeIn(lb_a), FadeIn(lb_b), run_time=self.STANDARD)

        window = SurroundingRectangle(id_texts[2], color=YELLOW, buff=0.15)
        self.play(Create(window), run_time=self.STANDARD)

        def jump(idx: int, rt: float) -> None:
            self.play(Transform(window, SurroundingRectangle(id_texts[idx], color=YELLOW, buff=0.15)), run_time=rt)

        # lb(a=3): show a couple of comparisons, then land on idx 1
        step1 = Text("mid=2 → 8 ≥ 3 → hi=2", color=self.COLOR_TEXT).scale(0.42)
        step1.next_to(window, RIGHT, buff=0.25)
        self.play(FadeIn(step1), run_time=self.FAST)
        jump(0, self.FAST)
        self.play(Transform(step1, Text("mid=0 → 1 < 3 → lo=1", color=self.COLOR_TEXT).scale(0.42).move_to(step1)), run_time=self.STANDARD)
        jump(1, self.FAST)
        self.play(FadeOut(step1), run_time=self.FAST)

        idx_a = 1
        a_mark = Text(f"idx(a) = {idx_a}", color=self.COLOR_ACCUM).scale(0.5)
        a_mark.next_to(lb_b, DOWN, buff=0.2, aligned_edge=LEFT)
        self.play(FadeIn(a_mark, shift=DOWN), run_time=self.STANDARD)
        self.wait(self.STANDARD)

        # lb(b=6): a couple more comparisons, then idx 2
        jump(3, self.FAST)
        step2 = Text("mid=3 → 11 ≥ 6 → hi=3", color=self.COLOR_TEXT).scale(0.42)
        step2.next_to(window, RIGHT, buff=0.25)
        self.play(FadeIn(step2), run_time=self.FAST)
        jump(2, self.FAST)
        self.play(Transform(step2, Text("mid=2 → 8 ≥ 6 → hi=2", color=self.COLOR_TEXT).scale(0.42).move_to(step2)), run_time=self.STANDARD)
        self.play(FadeOut(step2), run_time=self.FAST)

        idx_b = 2
        b_mark = Text(f"idx(b) = {idx_b}", color=self.COLOR_ACCUM).scale(0.5)
        b_mark.next_to(a_mark, DOWN, buff=0.18, aligned_edge=LEFT)
        self.play(FadeIn(b_mark, shift=DOWN), run_time=self.STANDARD)

        diff_box = SurroundingRectangle(VGroup(a_mark, b_mark), color=self.COLOR_ACCUM, buff=0.18)
        diff_lbl = Text(f"count = {idx_b} - {idx_a} = {idx_b - idx_a}", color=self.COLOR_ACCUM).scale(0.52)
        diff_lbl.next_to(diff_box, DOWN, buff=0.2)
        self.play(Create(diff_box), FadeIn(diff_lbl, shift=DOWN), run_time=self.STANDARD)
        self.wait(self.HOLD)

    def scene_example_walkthrough(self) -> None:
        title = Text("Example walkthrough", color=WHITE).scale(0.9).to_edge(UP)
        self.play(FadeIn(title), run_time=self.STANDARD)

        axis = self.axis_for_example().shift(UP * 1.35)
        self.play(Create(axis), run_time=self.STANDARD)

        merged = self.merge_sorted_half_open(sorted(self.to_half_open(self.EXAMPLE_RANGES_INCL), key=lambda t: t[0]))
        blocks = VGroup(*[self.interval_on_axis(axis, a, b, f"[{a},{b})", self.COLOR_MERGED, height=0.7, fill_opacity=0.25) for (a, b) in merged])
        blocks.arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        blocks.next_to(axis, DOWN, buff=0.55)
        self.play(FadeIn(blocks, shift=DOWN), run_time=self.STANDARD)

        ids = VGroup(*[Text(str(x), font="Monospace", color=WHITE).scale(0.58) for x in self.EXAMPLE_IDS])
        ids.arrange(RIGHT, buff=0.6)
        ids.to_edge(DOWN, buff=1.15)
        ids_lbl = Text("available IDs", color=self.COLOR_ID).scale(0.5)
        ids_lbl.next_to(ids, UP, buff=0.25)
        self.play(FadeIn(ids_lbl), FadeIn(ids, shift=UP), run_time=self.STANDARD)

        p1 = self.make_counter_box("Part 1", 0, self.COLOR_ACCUM)
        p2 = self.make_counter_box("Part 2", 0, self.COLOR_MERGED)
        counters = VGroup(p1, p2).arrange(DOWN, buff=0.25)
        counters.to_edge(RIGHT, buff=0.85).shift(DOWN * 1.15)
        self.play(FadeIn(counters, shift=LEFT), run_time=self.STANDARD)

        # Part 2
        union_size = sum(b - a for (a, b) in merged)
        self.play(self.update_counter_value(p2, union_size), run_time=self.STANDARD)

        # Part 1: show 1 + 2 = 3.
        total = 0
        for (a, b), block in zip(merged, blocks):
            per = 0
            hi = SurroundingRectangle(block, color=YELLOW, buff=0.08)
            self.play(Create(hi), run_time=self.FAST)
            for t in ids:
                x = int(t.text)
                if a <= x < b:
                    per += 1
                    self.play(t.animate.set_color(self.COLOR_ACCUM), run_time=self.FAST)
            total += per
            add = Text(f"+{per}", color=self.COLOR_ACCUM).scale(0.52)
            add.next_to(p1, LEFT, buff=0.25)
            self.play(FadeIn(add), self.update_counter_value(p1, total), run_time=self.STANDARD)
            self.play(FadeOut(add), FadeOut(hi), run_time=self.STANDARD)
        self.wait(self.HOLD)

    def scene_fpga_option_a_binary_search_fsm(self) -> None:
        title = Text("FPGA Option A: binary-search FSM", color=WHITE).scale(0.9).to_edge(UP)
        self.play(FadeIn(title), run_time=self.STANDARD)

        pipe = VGroup(
            RoundedRectangle(width=2.2, height=1.0, corner_radius=0.2, color=self.COLOR_RANGE),
            RoundedRectangle(width=2.2, height=1.0, corner_radius=0.2, color=self.COLOR_RANGE),
            RoundedRectangle(width=2.4, height=1.0, corner_radius=0.2, color=self.COLOR_MERGED),
            RoundedRectangle(width=2.6, height=1.0, corner_radius=0.2, color=self.COLOR_BUFFER),
            RoundedRectangle(width=2.8, height=1.0, corner_radius=0.2, color=self.COLOR_ID),
        ).arrange(RIGHT, buff=0.35)
        pipe.shift(UP * 1.35)

        labels = VGroup(
            Text("parse\nranges", color=self.COLOR_RANGE).scale(0.38),
            Text("sort\nranges", color=self.COLOR_RANGE).scale(0.38),
            Text("merge\nengine", color=self.COLOR_MERGED).scale(0.38),
            Text("IDs RAM", color=self.COLOR_BUFFER).scale(0.42),
            Text("lower_bound\nFSM", color=self.COLOR_ID).scale(0.38),
        )
        for lbl, box in zip(labels, pipe):
            lbl.move_to(box)
        self.play(Create(pipe), FadeIn(labels), run_time=self.STANDARD)

        arrows = VGroup(*[Arrow(pipe[i].get_right(), pipe[i + 1].get_left(), buff=0.12) for i in range(4)])
        self.play(Create(arrows), run_time=self.STANDARD)

        callout = RoundedRectangle(width=6.9, height=3.0, corner_radius=0.2, color=self.COLOR_ID)
        callout.to_edge(DOWN, buff=0.7)
        callout_title = Text("One lower_bound iteration", color=self.COLOR_ID).scale(0.52)
        callout_title.next_to(callout.get_top(), DOWN, buff=0.25)

        state = VGroup(
            Text("lo", font="Monospace", color=WHITE).scale(0.48),
            Text("mid", font="Monospace", color=WHITE).scale(0.48),
            Text("hi", font="Monospace", color=WHITE).scale(0.48),
        ).arrange(RIGHT, buff=0.9)
        state.move_to(callout.get_center() + UP * 0.45)

        ram = RoundedRectangle(width=2.4, height=0.9, corner_radius=0.18, color=self.COLOR_BUFFER)
        ram.move_to(callout.get_center() + DOWN * 0.55)
        ram_lbl = Text("RAM[mid]", color=self.COLOR_BUFFER).scale(0.46)
        ram_lbl.move_to(ram)

        step = self.make_code_block(
            [
                "mid = (lo+hi)/2",
                "val = RAM[mid]",
                "if val < target: lo = mid+1",
                "else: hi = mid",
            ],
            width=6.4,
        )
        step.next_to(callout, RIGHT, buff=0.45)

        self.play(Create(callout), FadeIn(callout_title), FadeIn(state), FadeIn(ram), FadeIn(ram_lbl), run_time=self.STANDARD)
        self.play(FadeIn(step, shift=LEFT), run_time=self.STANDARD)
        self.wait(self.LONG)

        pulse = SurroundingRectangle(state[1], color=YELLOW, buff=0.08)
        self.play(Create(pulse), run_time=self.FAST)
        self.play(Flash(ram, color=YELLOW, flash_radius=0.5), run_time=self.STANDARD)
        self.play(FadeOut(pulse), run_time=self.FAST)
        self.wait(self.HOLD)

    def scene_fpga_option_b_two_pointer(self) -> None:
        title = Text("FPGA Option B: two-pointer streaming merge", color=WHITE).scale(0.86).to_edge(UP)
        self.play(FadeIn(title), run_time=self.STANDARD)

        left_fifo = RoundedRectangle(width=4.0, height=1.2, corner_radius=0.2, color=self.COLOR_MERGED)
        left_fifo.to_edge(LEFT, buff=0.8).shift(UP * 1.2)
        right_fifo = RoundedRectangle(width=4.0, height=1.2, corner_radius=0.2, color=self.COLOR_ID)
        right_fifo.to_edge(LEFT, buff=0.8).shift(DOWN * 0.1)
        comp = RoundedRectangle(width=3.0, height=2.0, corner_radius=0.2, color=WHITE)
        comp.move_to(RIGHT * 2.7 + UP * 0.55)
        comp_lbl = Text("compare\n& advance", color=WHITE).scale(0.42)
        comp_lbl.move_to(comp)

        self.play(Create(left_fifo), Create(right_fifo), Create(comp), FadeIn(comp_lbl), run_time=self.STANDARD)
        self.play(
            FadeIn(Text("merged intervals", color=self.COLOR_MERGED).scale(0.46).next_to(left_fifo, UP, buff=0.22)),
            FadeIn(Text("sorted IDs", color=self.COLOR_ID).scale(0.46).next_to(right_fifo, UP, buff=0.22)),
            run_time=self.STANDARD,
        )

        a1 = Arrow(left_fifo.get_right(), comp.get_left(), buff=0.12)
        a2 = Arrow(right_fifo.get_right(), comp.get_left(), buff=0.12)
        out = Arrow(comp.get_right(), RIGHT * 6.0 + UP * 0.55, buff=0.12)
        self.play(Create(a1), Create(a2), Create(out), run_time=self.STANDARD)

        rule = self.make_code_block(
            [
                "if id < start: take id",
                "elif id >= end: take interval",
                "else: hit++; take id",
            ],
            width=6.0,
        )
        rule.to_edge(DOWN, buff=0.7)
        self.play(FadeIn(rule, shift=UP), run_time=self.STANDARD)
        self.wait(self.LONG)

        merged = self.merge_sorted_half_open(sorted(self.to_half_open(self.EXAMPLE_RANGES_INCL), key=lambda t: t[0]))
        ids = sorted(self.EXAMPLE_IDS)
        i = 0
        j = 0
        hits = 0
        hit_box = self.make_counter_box("hits", hits, self.COLOR_ACCUM)
        hit_box.to_edge(RIGHT, buff=0.9).shift(DOWN * 1.6)
        self.play(FadeIn(hit_box, shift=LEFT), run_time=self.STANDARD)

        for _ in range(8):
            if i >= len(ids) or j >= len(merged):
                break
            (s, e) = merged[j]
            x = ids[i]
            tok_i = Text(f"id={x}", font="Monospace", color=WHITE).scale(0.42)
            tok_r = Text(f"[{s},{e})", font="Monospace", color=WHITE).scale(0.42)
            tok_i.move_to(right_fifo)
            tok_r.move_to(left_fifo)
            self.play(FadeIn(tok_r), FadeIn(tok_i), run_time=self.FAST)

            if x < s:
                note = Text("id < start → advance id", color=self.COLOR_TEXT).scale(0.42)
                note.next_to(comp, DOWN, buff=0.2)
                self.play(FadeIn(note), run_time=self.FAST)
                self.play(tok_i.animate.move_to(comp), tok_r.animate.move_to(comp.get_top() + DOWN * 0.55), run_time=self.STANDARD)
                self.play(FadeOut(tok_i), FadeOut(note), run_time=self.FAST)
                i += 1
            elif x >= e:
                note = Text("id ≥ end → advance interval", color=self.COLOR_TEXT).scale(0.42)
                note.next_to(comp, DOWN, buff=0.2)
                self.play(FadeIn(note), run_time=self.FAST)
                self.play(tok_i.animate.move_to(comp), tok_r.animate.move_to(comp.get_top() + DOWN * 0.55), run_time=self.STANDARD)
                self.play(FadeOut(tok_r), FadeOut(note), run_time=self.FAST)
                j += 1
            else:
                note = Text("start ≤ id < end → hit", color=self.COLOR_ACCUM).scale(0.42)
                note.next_to(comp, DOWN, buff=0.2)
                self.play(FadeIn(note), run_time=self.FAST)
                self.play(tok_i.animate.move_to(comp), tok_r.animate.move_to(comp.get_top() + DOWN * 0.55), run_time=self.STANDARD)
                hits += 1
                self.play(self.update_counter_value(hit_box, hits), run_time=self.FAST)
                self.play(FadeOut(tok_i), FadeOut(note), run_time=self.FAST)
                i += 1
            self.play(FadeOut(tok_r), run_time=self.FAST)

        self.wait(self.HOLD)

    def scene_fpga_option_c_bitmap(self) -> None:
        title = Text("FPGA Option C: bitmap (only if universe is small)", color=WHITE).scale(0.74).to_edge(UP)
        self.play(FadeIn(title), run_time=self.STANDARD)

        bar = VGroup(*[Square(side_length=0.28, stroke_width=1, color=self.COLOR_TEXT) for _ in range(33)])
        bar.arrange(RIGHT, buff=0.02)
        bar.move_to(UP * 0.55)
        self.play(FadeIn(bar, shift=UP), run_time=self.STANDARD)

        ticks = VGroup(
            Text("0", color=self.COLOR_TEXT).scale(0.35).next_to(bar[0], DOWN, buff=0.15),
            Text("16", color=self.COLOR_TEXT).scale(0.35).next_to(bar[16], DOWN, buff=0.15),
            Text("32", color=self.COLOR_TEXT).scale(0.35).next_to(bar[32], DOWN, buff=0.15),
        )
        self.play(FadeIn(ticks), run_time=self.STANDARD)

        note = Text("Memory cost: U bits", color=self.COLOR_TEXT).scale(0.55)
        note.to_edge(RIGHT, buff=0.8).shift(UP * 0.7)
        self.play(FadeIn(note, shift=LEFT), run_time=self.STANDARD)

        merged = self.merge_sorted_half_open(sorted(self.to_half_open(self.EXAMPLE_RANGES_INCL), key=lambda t: t[0]))
        for (a, b) in merged:
            a2 = max(0, min(a, 32))
            b2 = max(0, min(b, 33))
            self.play(*[bar[i].animate.set_fill(self.COLOR_ACCUM, opacity=0.65) for i in range(a2, b2)], run_time=self.STANDARD)
        self.wait(self.HOLD)

    def scene_takeaway(self) -> None:
        title = Text("Takeaway", color=WHITE).scale(1.0).to_edge(UP)
        self.play(FadeIn(title), run_time=self.STANDARD)

        before = Text("overlaps", color=self.COLOR_RANGE).scale(0.62)
        after = Text("disjoint blocks", color=self.COLOR_MERGED).scale(0.62)
        before.to_edge(LEFT, buff=1.2).shift(UP * 2.0)
        after.to_edge(RIGHT, buff=1.2).shift(UP * 2.0)
        self.play(FadeIn(before), FadeIn(after), run_time=self.STANDARD)

        axis = self.axis_for_example().shift(UP * 0.4)
        self.play(Create(axis), run_time=self.STANDARD)

        overlaps = VGroup(
            self.interval_on_axis(axis, 3, 6, "[3,6)", self.COLOR_RANGE, height=0.45, fill_opacity=0.25),
            self.interval_on_axis(axis, 10, 15, "[10,15)", self.COLOR_RANGE, height=0.45, fill_opacity=0.25),
            self.interval_on_axis(axis, 12, 19, "[12,19)", self.COLOR_RANGE, height=0.45, fill_opacity=0.25),
            self.interval_on_axis(axis, 16, 21, "[16,21)", self.COLOR_RANGE, height=0.45, fill_opacity=0.25),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        overlaps.move_to(LEFT * 3.2 + DOWN * 0.4)

        merged = VGroup(
            self.interval_on_axis(axis, 3, 6, "[3,6)", self.COLOR_MERGED, height=0.6, fill_opacity=0.25),
            self.interval_on_axis(axis, 10, 21, "[10,21)", self.COLOR_MERGED, height=0.6, fill_opacity=0.25),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        merged.move_to(RIGHT * 3.0 + DOWN * 0.45)

        self.play(FadeIn(overlaps, shift=LEFT), FadeIn(merged, shift=RIGHT), run_time=self.STANDARD)

        banner_text = Text("Merge once, then counting becomes simple", color=WHITE).scale(0.72)
        banner_box = SurroundingRectangle(banner_text, color=self.COLOR_ACCUM, buff=0.25)
        banner = VGroup(banner_box, banner_text)
        banner.move_to(DOWN * 2.7)
        self.play(FadeIn(banner, shift=UP), run_time=self.LONG)
        self.wait(self.HOLD)
