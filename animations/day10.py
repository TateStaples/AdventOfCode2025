"""animations/day10.py

Day 10 — Factory (Buttons, GF(2), and Integer Systems)

Storyboard: animations/day_by_day_video_scripts.md (Day 10)
"""

from __future__ import annotations

from typing import List

from manim import *


class Day10(Scene):
    # Timing
    FAST = 0.25
    STANDARD = 0.7
    LONG = 1.3
    HOLD = 36.0

    # Colors
    COLOR_TEXT = GRAY_E
    COLOR_DIM = GRAY_C
    COLOR_P1 = BLUE_C
    COLOR_P2 = GREEN_C
    COLOR_ACC = ORANGE
    COLOR_ON = YELLOW_E
    COLOR_OFF = GRAY_D

    SCALE_TITLE = 0.8
    SCALE_SUB = 0.55
    SCALE_TEXT = 0.5
    SCALE_SMALL = 0.42
    SCALE_CODE = 0.34
    SCALE_TINY = 0.33

    def construct(self) -> None:
        self.scene_hook_machine_buttons()
        self.clear()
        self.scene_part1_bitmask_puzzle()
        self.clear()
        self.scene_math_model()
        self.clear()
        self.scene_reference_subset_search()
        self.clear()
        self.scene_incremental_xor_update()
        self.clear()
        self.scene_elimination_free_vars()
        self.clear()
        self.scene_meet_in_middle()
        self.clear()
        self.scene_part2_integers_switch()
        self.clear()
        self.scene_bounds_make_finite()
        self.clear()
        self.scene_fpga_part2_residual_branch_bound()
        self.clear()
        self.scene_gray_code_residual_updates()
        self.clear()
        self.scene_takeaway_comparison()

    # Helpers -----------------------------------------------------------------
    def make_code_block(self, lines: List[str]) -> VGroup:
        text = VGroup(
            *[Text(line, font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_CODE) for line in lines]
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        box = SurroundingRectangle(text, color=self.COLOR_DIM, buff=0.18)
        return VGroup(box, text)

    def bit_row(self, bits: List[int], *, label: str = "", box_color: ManimColor | None = None) -> VGroup:
        cell = 0.42
        cells = VGroup()
        for b in bits:
            sq = Square(side_length=cell)
            sq.set_stroke(color=self.COLOR_TEXT, width=1.1)
            sq.set_fill(self.COLOR_ON if b else self.COLOR_OFF, opacity=0.9 if b else 0.35)
            cells.add(sq)
        cells.arrange(RIGHT, buff=0.05)
        if label:
            lbl = Text(label, color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
            lbl.next_to(cells, LEFT, buff=0.25)
            group = VGroup(lbl, cells)
        else:
            group = VGroup(cells)
        if box_color is not None:
            box = SurroundingRectangle(group, color=box_color, buff=0.15)
            return VGroup(box, group)
        return group

    def button_card(self, name: str, mask: List[int]) -> VGroup:
        card = RoundedRectangle(width=4.4, height=0.9, corner_radius=0.16, color=self.COLOR_ACC)
        card.set_fill(self.COLOR_ACC, opacity=0.04)
        title = Text(name, color=self.COLOR_ACC).scale(self.SCALE_SMALL)
        title.move_to(card.get_left() + RIGHT * 0.62)
        bits = self.bit_row(mask)
        bits.scale(0.95)
        bits.move_to(card.get_center() + RIGHT * 0.7)
        return VGroup(card, title, bits)

    def xor_toggle(self, row: VGroup, mask: List[int]) -> None:
        # row can be [box, [label, cells]] or [label, cells] or [cells]
        cells = row
        if isinstance(cells, VGroup) and len(cells) == 2 and isinstance(cells[0], SurroundingRectangle):
            cells = cells[1]
        if isinstance(cells, VGroup) and len(cells) == 2 and isinstance(cells[0], Text):
            cells = cells[1]
        if isinstance(cells, VGroup) and len(cells) == 1 and isinstance(cells[0], VGroup):
            cells = cells[0]

        anims = []
        for i, b in enumerate(mask):
            if not b:
                continue
            sq = cells[i]
            is_on = sq.get_fill_opacity() > 0.6
            anims.append(
                sq.animate.set_fill(
                    self.COLOR_OFF if is_on else self.COLOR_ON,
                    opacity=0.35 if is_on else 0.9,
                )
            )
        if anims:
            self.play(*anims, run_time=self.FAST)

    # Scene 1 -----------------------------------------------------------------
    def scene_hook_machine_buttons(self) -> None:
        title = Text("Day 10 — Factory", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("A machine with buttons", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        target = [1, 0, 1, 1, 0, 0, 1, 0]
        current = [0] * len(target)
        target_row = self.bit_row(target, label="target", box_color=self.COLOR_TEXT)
        cur_row = self.bit_row(current, label="current", box_color=self.COLOR_TEXT)
        rows = VGroup(target_row, cur_row).arrange(DOWN, buff=0.45)
        rows.to_edge(LEFT).shift(RIGHT * 1.0 + UP * 0.3)
        self.play(FadeIn(rows, shift=RIGHT * 0.2), run_time=self.STANDARD)

        masks = [
            ("Button A", [1, 1, 0, 0, 0, 0, 0, 0]),
            ("Button B", [0, 1, 1, 0, 0, 0, 1, 0]),
            ("Button C", [0, 0, 1, 1, 0, 0, 0, 1]),
            ("Button D", [1, 0, 0, 1, 0, 1, 0, 0]),
        ]
        buttons = VGroup(*[self.button_card(n, m) for n, m in masks]).arrange(DOWN, buff=0.3)
        buttons.scale(0.9)
        buttons.to_edge(RIGHT).shift(LEFT * 0.6)
        self.play(FadeIn(buttons, shift=LEFT * 0.2), run_time=self.STANDARD)

        note = Text("Part 1: XOR toggle (mod 2)", color=self.COLOR_P1).scale(self.SCALE_SMALL)
        note.to_edge(DOWN).shift(LEFT * 3.8)
        self.play(FadeIn(note, shift=UP * 0.2), run_time=self.STANDARD)

        h = SurroundingRectangle(buttons[0], color=self.COLOR_ACC, buff=0.14)
        self.play(Create(h), run_time=self.FAST)
        self.xor_toggle(cur_row, masks[0][1])
        self.xor_toggle(cur_row, masks[1][1])
        self.xor_toggle(cur_row, masks[0][1])
        cancel = Text("press twice ⇒ cancels", color=self.COLOR_P1).scale(self.SCALE_SMALL)
        cancel.next_to(note, UP, buff=0.25)
        self.play(FadeIn(cancel, shift=UP * 0.1), FadeOut(h), run_time=self.STANDARD)
        self.wait(self.HOLD)

    # Scene 2 -----------------------------------------------------------------
    def scene_part1_bitmask_puzzle(self) -> None:
        title = Text("Part 1: a bitmask puzzle", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("choose x ∈ {0,1}^m so XOR(masks) hits target", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        current = self.bit_row([0, 0, 0, 0, 0, 0, 0, 0], label="state", box_color=self.COLOR_P1)
        current.to_edge(LEFT).shift(RIGHT * 1.0 + UP * 0.3)
        xor_gate = MathTex(r"\oplus", color=self.COLOR_P1).scale(1.2).move_to(ORIGIN).shift(UP * 0.3)
        x_bits = self.bit_row([0, 0, 0, 0], label="x", box_color=self.COLOR_TEXT)
        x_bits.to_edge(RIGHT).shift(LEFT * 1.0 + UP * 0.3)
        self.play(FadeIn(current), FadeIn(xor_gate), FadeIn(x_bits), run_time=self.STANDARD)

        flips = Text("flip bits in x", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        flips.next_to(x_bits, DOWN, buff=0.3)
        self.play(FadeIn(flips, shift=DOWN * 0.1), run_time=self.STANDARD)

        # Flip a couple x bits to emphasize {0,1}.
        h0 = SurroundingRectangle(x_bits[1][1][0][0], color=self.COLOR_ACC, buff=0.05)
        self.play(Create(h0), run_time=self.FAST)
        self.xor_toggle(x_bits, [1, 0, 0, 0])
        self.play(FadeOut(h0), run_time=self.FAST)
        h1 = SurroundingRectangle(x_bits[1][1][2][0], color=self.COLOR_ACC, buff=0.05)
        self.play(Create(h1), run_time=self.FAST)
        self.xor_toggle(x_bits, [0, 0, 1, 0])
        self.play(FadeOut(h1), run_time=self.FAST)
        self.wait(self.HOLD)

    # Scene 3 -----------------------------------------------------------------
    def scene_math_model(self) -> None:
        title = Text("Model: Ax = b (mod 2)", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("minimize popcount(x)", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        eq = MathTex(r"A\,x = b\;\;(\mathrm{mod}\;2)", color=self.COLOR_P1).scale(1.0)
        legend = Text("+ means XOR", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        legend.next_to(eq, DOWN, buff=0.3)
        self.play(FadeIn(eq), FadeIn(legend, shift=DOWN * 0.1), run_time=self.STANDARD)

        cost = Text("cost = popcount(x)", color=self.COLOR_ACC).scale(self.SCALE_TEXT)
        cost.to_edge(RIGHT).shift(DOWN * 0.3)
        self.play(Write(cost), run_time=self.STANDARD)
        self.wait(self.HOLD)

    # Scene 4 -----------------------------------------------------------------
    def scene_reference_subset_search(self) -> None:
        title = Text("Reference: subset search by size", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("k=1,2,3… stop at first match", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        ladder = VGroup(
            Text("k=1", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("k=2", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("k=3", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("k=4", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        ladder.to_edge(LEFT).shift(RIGHT * 1.1 + UP * 0.3)
        self.play(FadeIn(ladder, shift=RIGHT * 0.2), run_time=self.STANDARD)

        acc = self.bit_row([0, 0, 0, 0, 0, 0, 0, 0], label="xor", box_color=self.COLOR_P1)
        acc.to_edge(DOWN).shift(UP * 1.2)
        self.play(FadeIn(acc, shift=UP * 0.1), run_time=self.STANDARD)

        # Flash a couple subset attempts.
        for k in range(1, 4):
            hi = SurroundingRectangle(ladder[k - 1], color=self.COLOR_ACC, buff=0.1)
            self.play(Create(hi), run_time=self.FAST)
            self.xor_toggle(acc, [1, 1, 0, 0, 0, 0, 0, 0])
            self.xor_toggle(acc, [0, 1, 1, 0, 0, 0, 1, 0])
            self.play(FadeOut(hi), run_time=self.FAST)
        self.wait(self.HOLD)

    # Scene 5 -----------------------------------------------------------------
    def scene_incremental_xor_update(self) -> None:
        title = Text("Incremental XOR update", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("next subset differs by small edit", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        prev = Text("subset S", color=self.COLOR_TEXT).scale(self.SCALE_TEXT)
        nxt = Text("subset S'", color=self.COLOR_TEXT).scale(self.SCALE_TEXT)
        panels = VGroup(prev, nxt).arrange(RIGHT, buff=3.0).shift(UP * 1.0)
        self.play(FadeIn(panels), run_time=self.STANDARD)

        mid = VGroup(
            Text("XOR out", color=self.COLOR_P1).scale(self.SCALE_SMALL),
            Text("XOR in", color=self.COLOR_P1).scale(self.SCALE_SMALL),
        ).arrange(DOWN, buff=0.2)
        mid.move_to(ORIGIN)
        self.play(FadeIn(mid), run_time=self.STANDARD)

        acc = self.bit_row([0, 0, 0, 0, 0, 0, 0, 0], label="xor", box_color=self.COLOR_P1)
        acc.to_edge(DOWN).shift(UP * 1.2)
        self.play(FadeIn(acc), run_time=self.STANDARD)
        self.xor_toggle(acc, [1, 1, 0, 0, 0, 0, 0, 0])
        self.xor_toggle(acc, [0, 1, 1, 0, 0, 0, 1, 0])
        # Small edit: remove A, add D
        self.xor_toggle(acc, [1, 1, 0, 0, 0, 0, 0, 0])
        self.xor_toggle(acc, [1, 0, 0, 1, 0, 1, 0, 0])
        self.wait(self.HOLD)

    # Scene 6 -----------------------------------------------------------------
    def scene_elimination_free_vars(self) -> None:
        title = Text("Alternative: elimination + free vars", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("often f ≪ m", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        mat = self.make_code_block([
            "[1 0 1 0 | 1]",
            "[0 1 1 0 | 0]",
            "[1 1 0 1 | 1]",
        ])
        mat.to_edge(LEFT).shift(RIGHT * 1.0 + DOWN * 0.2)
        self.play(FadeIn(mat, shift=RIGHT * 0.2), run_time=self.STANDARD)

        ops = Text("row XORs → RREF", color=self.COLOR_P1).scale(self.SCALE_SMALL)
        ops.next_to(mat, DOWN, buff=0.3)
        self.play(FadeIn(ops, shift=DOWN * 0.1), run_time=self.STANDARD)

        free = VGroup(
            Text("free vars:", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("x3, x4", color=self.COLOR_ACC).scale(self.SCALE_TEXT),
            Text(r"search 2^f", color=self.COLOR_P1).scale(self.SCALE_SMALL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        free.to_edge(RIGHT).shift(LEFT * 1.2)
        self.play(FadeIn(free, shift=LEFT * 0.2), run_time=self.STANDARD)
        self.wait(self.HOLD)

    # Scene 7 -----------------------------------------------------------------
    def scene_meet_in_middle(self) -> None:
        title = Text("Meet-in-the-middle (idea)", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("trade memory for speed", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        left_tbl = self.make_code_block([
            "half 1:",
            "  α=00 → x=…  pop=2",
            "  α=01 → x=…  pop=3",
        ])
        right_tbl = self.make_code_block([
            "half 2:",
            "  β=00 → x=…  pop=1",
            "  β=10 → x=…  pop=2",
        ])
        left_tbl.to_edge(LEFT).shift(RIGHT * 1.0 + DOWN * 0.1)
        right_tbl.to_edge(RIGHT).shift(LEFT * 1.0 + DOWN * 0.1)
        join = Text("match + minimize popcount", color=self.COLOR_ACC).scale(self.SCALE_SMALL)
        join.move_to(ORIGIN).shift(DOWN * 0.3)
        self.play(FadeIn(left_tbl), FadeIn(right_tbl), FadeIn(join), run_time=self.STANDARD)
        box = SurroundingRectangle(join, color=self.COLOR_ACC, buff=0.2)
        self.play(Create(box), run_time=self.FAST)
        self.wait(self.HOLD)

    # Scene 8 -----------------------------------------------------------------
    def scene_part2_integers_switch(self) -> None:
        title = Text("Part 2: integers (joltages)", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("press twice adds twice — no cancellation", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        add = MathTex(r"+", color=self.COLOR_P2).scale(1.4)
        add.move_to(ORIGIN).shift(UP * 0.5)
        self.play(FadeIn(add), run_time=self.STANDARD)

        counters = VGroup(*[Integer(0, color=self.COLOR_P2).scale(0.9) for _ in range(4)]).arrange(RIGHT, buff=0.6)
        counters.shift(DOWN * 0.2)
        lbl = Text("counters", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        lbl.next_to(counters, UP, buff=0.2)
        self.play(FadeIn(counters), FadeIn(lbl), run_time=self.STANDARD)
        # press twice
        for _ in range(2):
            self.play(counters[0].animate.set_value(counters[0].get_value() + 1), run_time=self.FAST)
        self.wait(self.HOLD)

    # Scene 9 -----------------------------------------------------------------
    def scene_bounds_make_finite(self) -> None:
        title = Text("Bounding makes search finite", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text(r"x_i \le \min_{j: A[j,i]=1} b_j", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        caps = self.make_code_block([
            "caps:",
            "  x0 ≤ 3",
            "  x1 ≤ 1",
            "  x2 ≤ 2",
            "  x3 ≤ 1",
        ])
        caps.to_edge(RIGHT).shift(LEFT * 1.0)
        self.play(FadeIn(caps, shift=LEFT * 0.2), run_time=self.STANDARD)

        demo = Text("cap comes from the tightest affected row", color=self.COLOR_ACC).scale(self.SCALE_SMALL)
        demo.to_edge(LEFT).shift(RIGHT * 1.0 + DOWN * 0.2)
        self.play(FadeIn(demo, shift=RIGHT * 0.2), run_time=self.STANDARD)
        self.wait(self.HOLD)

    # Scene 10 ---------------------------------------------------------------
    def scene_fpga_part2_residual_branch_bound(self) -> None:
        title = Text("FPGA Part 2: residual branch-and-bound", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text(r"r := r - x_k \cdot c_k  (prune if any r<0)", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        # Residual bars
        residual = [3, 1, 2, 0]

        def bar(h: int) -> Rectangle:
            r = Rectangle(width=0.6, height=0.25 + 0.35 * max(h, 0), color=self.COLOR_P2)
            r.set_fill(self.COLOR_P2, opacity=0.55)
            return r

        bars = VGroup(*[bar(v) for v in residual]).arrange(RIGHT, buff=0.35)
        bars.to_edge(LEFT).shift(RIGHT * 1.2 + DOWN * 0.2)
        r_lbl = Text("residual r", color=self.COLOR_P2).scale(self.SCALE_SMALL)
        r_lbl.next_to(bars, UP, buff=0.2)
        self.play(FadeIn(bars), FadeIn(r_lbl), run_time=self.STANDARD)

        ck = self.make_code_block([
            "c_k = [1, 0, 1, 0]",
            "choose x_k = 2",
            "r -= 2*c_k",
        ])
        ck.to_edge(RIGHT).shift(LEFT * 1.0 + DOWN * 0.1)
        self.play(FadeIn(ck, shift=LEFT * 0.2), run_time=self.STANDARD)

        # Apply two subtract steps
        for _ in range(2):
            residual[0] -= 1
            residual[2] -= 1
            self.play(
                bars[0].animate.set(height=0.25 + 0.35 * max(residual[0], 0)),
                bars[2].animate.set(height=0.25 + 0.35 * max(residual[2], 0)),
                run_time=self.FAST,
            )

        prune = Text("negative residual ⇒ prune branch", color=self.COLOR_ACC).scale(self.SCALE_SMALL)
        prune.next_to(ck, DOWN, buff=0.25)
        self.play(FadeIn(prune, shift=DOWN * 0.1), run_time=self.STANDARD)
        self.wait(self.HOLD)

    # Scene 11 ---------------------------------------------------------------
    def scene_gray_code_residual_updates(self) -> None:
        title = Text("Gray-code / incremental residual updates", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("change one variable by ±1 → r +=/− c_k", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        counter = self.make_code_block([
            "mixed-radix counter:",
            "  x = [0,0,0]",
            "  next: x2 += 1",
        ])
        counter.to_edge(LEFT).shift(RIGHT * 1.1)
        self.play(FadeIn(counter, shift=RIGHT * 0.2), run_time=self.STANDARD)

        residual = Integer(6, color=self.COLOR_P2).scale(1.0)
        r_lbl = Text("residual summary", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        r_group = VGroup(r_lbl, residual).arrange(DOWN, buff=0.2)
        r_group.to_edge(RIGHT).shift(LEFT * 1.2)
        self.play(FadeIn(r_group, shift=LEFT * 0.2), run_time=self.STANDARD)

        delta = Text("apply Δr", color=self.COLOR_ACC).scale(self.SCALE_SMALL)
        delta.next_to(r_group, DOWN, buff=0.3)
        self.play(FadeIn(delta, shift=DOWN * 0.1), run_time=self.STANDARD)
        for dv in [-1, -1, +1, -1]:
            self.play(residual.animate.set_value(residual.get_value() + dv), run_time=self.FAST)
        self.wait(self.HOLD)

    # Scene 12 ---------------------------------------------------------------
    def scene_takeaway_comparison(self) -> None:
        title = Text("Takeaway", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("same goal, different math worlds", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        left = VGroup(
            Text("Part 1", color=self.COLOR_P1).scale(self.SCALE_TEXT),
            Text("bitmasks", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("XOR", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("popcount", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
        ).arrange(DOWN, buff=0.18)
        right = VGroup(
            Text("Part 2", color=self.COLOR_P2).scale(self.SCALE_TEXT),
            Text("integer vectors", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("bounds", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("residual + prune", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
        ).arrange(DOWN, buff=0.18)
        cols = VGroup(left, right).arrange(RIGHT, buff=3.0).shift(DOWN * 0.2)
        box = SurroundingRectangle(cols, color=self.COLOR_DIM, buff=0.4)
        box.set_fill(self.COLOR_DIM, opacity=0.05)
        self.play(FadeIn(box), FadeIn(cols), run_time=self.STANDARD)
        self.wait(self.HOLD)
