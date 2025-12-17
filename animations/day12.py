"""Day 12: Christmas Tree Farm (packing presents).

This animation follows the Day 12 paper themes:
- Shapes (with rotations/flips) must be placed on a grid without overlap.
- The simple capacity check is only necessary, not sufficient.
- Complete solvers: exact cover (DLX), SAT/ILP constraints, stripe/profile DP.
- FPGA accelerators: bitboard exact-cover search vs transfer-matrix DP.
"""

from manim import *
from typing import List


class Day12(Scene):
    """Animation for Day 12 packing/solver hardware."""

    # Pacing: readable without voiceover.
    FAST = 0.8
    STANDARD = 2.0
    LONG = 4.0
    HOLD = 6.0

    COLOR_SHAPE = ORANGE
    COLOR_BOARD = BLUE_C
    COLOR_OK = GREEN_C
    COLOR_BAD = RED_C
    COLOR_ACCENT = PURPLE_C
    COLOR_TEXT = GRAY_E

    SCALE_TITLE = 0.8
    SCALE_SUBTITLE = 0.6
    SCALE_TEXT = 0.5
    SCALE_SMALL = 0.4
    SCALE_CODE = 0.3

    def construct(self) -> None:
        self.scene_problem()
        self.clear()
        self.scene_algorithm()
        self.clear()
        self.scene_bitmasks()
        self.clear()
        self.scene_circuit()

    # Helpers -----------------------------------------------------------------
    def code_block(self, lines: List[str]) -> VGroup:
        text = VGroup(*[
            Text(line, font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_CODE)
            for line in lines
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        box = SurroundingRectangle(text, color=self.COLOR_TEXT, buff=0.18)
        return VGroup(box, text)

    def cell(self, *, filled: bool, size: float = 0.35, color=None) -> Square:
        c = color if color is not None else self.COLOR_SHAPE
        sq = Square(side_length=size)
        sq.set_stroke(color=self.COLOR_TEXT, width=1.1)
        if filled:
            sq.set_fill(color=c, opacity=0.8)
        else:
            sq.set_fill(color=GRAY_E, opacity=0.08)
        return sq

    def shape_from_pattern(self, pattern: List[str], *, color=None, label: str | None = None) -> VGroup:
        rows = []
        for r in pattern:
            row = VGroup(*[self.cell(filled=(ch == "#"), color=color) for ch in r])
            row.arrange(RIGHT, buff=0.03)
            rows.append(row)
        g = VGroup(*rows).arrange(DOWN, buff=0.03)
        if label is None:
            return g
        lbl = Text(label, color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        lbl.next_to(g, UP, buff=0.15)
        return VGroup(lbl, g)

    def board(self, w: int, h: int, *, size: float = 0.35) -> VGroup:
        rows = []
        for _ in range(h):
            row = VGroup(*[self.cell(filled=False, size=size, color=self.COLOR_BOARD) for _ in range(w)])
            row.arrange(RIGHT, buff=0.03)
            rows.append(row)
        return VGroup(*rows).arrange(DOWN, buff=0.03)

    def bit_box(self, bits: str, *, label: str, color) -> VGroup:
        t = Text(bits, font="Monospace", color=WHITE).scale(self.SCALE_TEXT)
        box = SurroundingRectangle(t, color=color, buff=0.18)
        lbl = Text(label, color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        lbl.next_to(box, UP, buff=0.12)
        return VGroup(lbl, box, t)

    # Scene 1 -----------------------------------------------------------------
    def scene_problem(self) -> None:
        title = Text("Day 12: Packing Presents").scale(self.SCALE_TITLE).to_edge(UP)
        self.play(Write(title), run_time=self.STANDARD)
        self.wait(1.0)

        intro = Text("Place required shapes into a region (no overlaps)", color=self.COLOR_TEXT).scale(self.SCALE_TEXT)
        intro.next_to(title, DOWN)
        self.play(FadeIn(intro, shift=DOWN * 0.2), run_time=self.STANDARD)
        self.wait(1.0)

        region = self.board(10, 6, size=0.32)
        region.to_edge(LEFT).shift(UP * 0.1)
        region_box = SurroundingRectangle(region, color=self.COLOR_BOARD, buff=0.15)
        region_lbl = Text("region", color=self.COLOR_BOARD).scale(self.SCALE_SMALL)
        region_lbl.next_to(region_box, UP, buff=0.15)

        self.play(FadeIn(region), Create(region_box), FadeIn(region_lbl), run_time=self.STANDARD)
        self.wait(1.0)

        # A few 3x3-local shapes to illustrate orientation.
        s1 = self.shape_from_pattern([
            "##.",
            ".#.",
            "...",
        ], color=self.COLOR_SHAPE, label="shape A")
        s2 = self.shape_from_pattern([
            "###",
            "..#",
            "...",
        ], color=self.COLOR_SHAPE, label="shape B")
        s3 = self.shape_from_pattern([
            "##.",
            "##.",
            "...",
        ], color=self.COLOR_SHAPE, label="shape C")

        shapes = VGroup(s1, s2, s3).arrange(DOWN, buff=0.5)
        shapes.to_edge(RIGHT).shift(LEFT * 0.4)
        self.play(FadeIn(shapes, shift=LEFT * 0.2), run_time=self.STANDARD)
        self.wait(1.0)

        rules = VGroup(
            Text("Rules:", color=self.COLOR_TEXT).scale(self.SCALE_TEXT),
            Text("• rotate/flip allowed", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("• grid-aligned", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("• no overlap", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        rules.to_edge(DOWN).shift(LEFT * 3.9)
        self.play(FadeIn(rules, shift=UP * 0.2), run_time=self.STANDARD)
        self.wait(1.0)

        # Tiny placement attempt: place A then overlap with B.
        place_a = s1[1].copy().scale(0.95)
        place_a.move_to(region.get_center() + LEFT * 1.3)
        self.play(FadeIn(place_a, shift=DOWN * 0.1), run_time=self.FAST)
        self.wait(0.8)

        place_b = s2[1].copy().scale(0.95)
        place_b.move_to(place_a.get_center() + RIGHT * 0.4)
        self.play(FadeIn(place_b, shift=DOWN * 0.1), run_time=self.FAST)
        x = Text("X", color=self.COLOR_BAD).scale(self.SCALE_TEXT)
        x.move_to(place_b)
        self.play(FadeIn(x, scale=0.8), run_time=self.FAST)

        self.wait(self.HOLD)

    # Scene 2 -----------------------------------------------------------------
    def scene_algorithm(self) -> None:
        title = Text("Solving: Filter vs Complete Solver").scale(self.SCALE_TITLE).to_edge(UP)
        self.play(Write(title), run_time=self.STANDARD)
        self.wait(1.0)

        # Necessary (but not sufficient) check.
        coarse = VGroup(
            Text("Fast filter (necessary)", color=self.COLOR_TEXT).scale(self.SCALE_TEXT),
            MathTex(r"\left\lfloor W/3 \right\rfloor\left\lfloor H/3 \right\rfloor \ge \#\text{pieces}").scale(0.75),
            Text("Passes ⇒ maybe possible", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        coarse.to_edge(LEFT).shift(UP * 0.8)
        self.play(FadeIn(coarse, shift=RIGHT * 0.2), run_time=self.STANDARD)
        self.wait(1.0)

        # Counterexample: passes the filter but cannot pack (visual only).
        ex_board = self.board(6, 4, size=0.34)
        ex_board.to_edge(RIGHT).shift(UP * 0.6 + LEFT * 0.6)
        ex_box = SurroundingRectangle(ex_board, color=self.COLOR_BOARD, buff=0.15)
        ex_lbl = Text("counterexample", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        ex_lbl.next_to(ex_box, UP, buff=0.15)

        self.play(FadeIn(ex_board), Create(ex_box), FadeIn(ex_lbl), run_time=self.STANDARD)
        self.wait(0.8)
        stamp = Text("FILTER PASSES", color=self.COLOR_OK).scale(self.SCALE_TEXT)
        stamp.next_to(ex_box, DOWN, buff=0.2)
        self.play(FadeIn(stamp, scale=0.9), run_time=self.FAST)
        self.wait(0.8)

        fail = Text("…but packing still fails", color=self.COLOR_BAD).scale(self.SCALE_TEXT)
        fail.next_to(stamp, DOWN, buff=0.15)
        self.play(FadeIn(fail, shift=UP * 0.1), run_time=self.STANDARD)
        self.wait(1.0)

        # Complete solvers.
        methods = VGroup(
            Text("Complete solvers", color=self.COLOR_TEXT).scale(self.SCALE_TEXT),
            Text("1) Exact cover (DLX)", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("2) SAT / ILP constraints", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("3) Stripe/profile DP", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        methods.to_edge(LEFT).shift(DOWN * 1.4)
        self.play(FadeIn(methods, shift=UP * 0.1), run_time=self.STANDARD)
        self.wait(1.0)

        # A tiny exact-cover visual: columns and one chosen row.
        col_hdr = VGroup(
            Text("cells", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("pieces", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
        ).arrange(RIGHT, buff=1.2)
        col_hdr.next_to(ex_box, DOWN, buff=0.8)
        matrix = self.code_block([
            "col: cell(0,0) cell(0,1) ... | piece A1 piece B1 ...",
            "row: place(A@x,y) has 1s in its covered cells + A1",
            "choose rows that cover all pieces without cell conflicts",
        ])
        matrix.next_to(col_hdr, DOWN, buff=0.2)
        self.play(FadeIn(col_hdr, shift=UP * 0.1), FadeIn(matrix, shift=UP * 0.1), run_time=self.STANDARD)

        self.wait(self.HOLD)

    # Scene 3 -----------------------------------------------------------------
    def scene_bitmasks(self) -> None:
        title = Text("Hardware View: Bitmasks for Overlap Checks").scale(self.SCALE_TITLE).to_edge(UP)
        self.play(Write(title), run_time=self.STANDARD)
        self.wait(0.8)

        subtitle = Text("Turn a row of cells into a word", color=self.COLOR_TEXT).scale(self.SCALE_TEXT)
        subtitle.next_to(title, DOWN)
        self.play(FadeIn(subtitle, shift=DOWN * 0.2), run_time=self.STANDARD)
        self.wait(0.8)

        occ = self.bit_box("00101100", label="occupancy", color=self.COLOR_BOARD)
        plc = self.bit_box("00001010", label="placement", color=self.COLOR_SHAPE)
        occ.shift(LEFT * 3.2 + UP * 0.7)
        plc.shift(RIGHT * 3.2 + UP * 0.7)
        self.play(FadeIn(occ, shift=UP * 0.1), FadeIn(plc, shift=UP * 0.1), run_time=self.STANDARD)
        self.wait(1.0)

        and_sym = MathTex(r"\&").scale(1.0).set_color(self.COLOR_TEXT)
        and_sym.move_to((occ[1].get_right() + plc[1].get_left()) / 2)
        self.play(Write(and_sym), run_time=self.STANDARD)

        res_bad = self.bit_box("00001000", label="overlap", color=self.COLOR_BAD)
        res_bad.move_to(DOWN * 0.9)
        self.play(FadeIn(res_bad, shift=UP * 0.1), run_time=self.STANDARD)
        bad_note = Text("non-zero ⇒ collision", color=self.COLOR_BAD).scale(self.SCALE_TEXT)
        bad_note.next_to(res_bad, DOWN, buff=0.25)
        self.play(FadeIn(bad_note, shift=UP * 0.1), run_time=self.STANDARD)
        self.wait(1.2)

        self.play(FadeOut(res_bad), FadeOut(bad_note), run_time=self.FAST)
        self.wait(0.5)

        plc2 = self.bit_box("00000011", label="placement", color=self.COLOR_SHAPE)
        plc2.move_to(plc)
        self.play(FadeTransform(plc, plc2), run_time=self.STANDARD)
        res_ok = self.bit_box("00000000", label="overlap", color=self.COLOR_OK)
        res_ok.move_to(DOWN * 0.9)
        self.play(FadeIn(res_ok, shift=UP * 0.1), run_time=self.STANDARD)
        ok_note = Text("zero ⇒ placeable", color=self.COLOR_OK).scale(self.SCALE_TEXT)
        ok_note.next_to(res_ok, DOWN, buff=0.25)
        self.play(FadeIn(ok_note, shift=UP * 0.1), run_time=self.STANDARD)
        self.wait(1.2)

        code = self.code_block([
            "if (occ & mask) == 0:",
            "  occ2 = occ | mask",
            "  recurse(occ2, next_piece)",
        ])
        code.to_edge(DOWN).shift(UP * 0.2)
        self.play(FadeIn(code, shift=UP * 0.1), run_time=self.STANDARD)

        takeaway = Text("This is why bitboards map so well to FPGAs", color=self.COLOR_TEXT).scale(self.SCALE_TEXT)
        takeaway.to_edge(DOWN)
        self.play(FadeIn(takeaway, shift=UP * 0.1), run_time=self.STANDARD)

        self.wait(self.HOLD)

    # Scene 4 -----------------------------------------------------------------
    def scene_circuit(self) -> None:
        title = Text("FPGA Accelerators").scale(self.SCALE_TITLE).to_edge(UP)
        self.play(Write(title), run_time=self.STANDARD)
        self.wait(1.0)

        # Option A: bitboard exact-cover / backtracking.
        opt_a = RoundedRectangle(width=5.2, height=2.3, corner_radius=0.2, color=self.COLOR_SHAPE)
        opt_a.shift(LEFT * 3.1 + UP * 0.8)
        a_lbl = Text("Option A: bitboard search (exact cover)", color=self.COLOR_SHAPE).scale(self.SCALE_SMALL)
        a_lbl.next_to(opt_a, UP, buff=0.15)
        a_inside = VGroup(
            Text("occupancy bitmask", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("placement masks", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("overlap = AND", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("DFS stack + prune", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        a_inside.move_to(opt_a.get_center())

        # Option B: transfer-matrix / profile DP.
        opt_b = RoundedRectangle(width=5.2, height=2.3, corner_radius=0.2, color=self.COLOR_BOARD)
        opt_b.shift(RIGHT * 3.1 + UP * 0.8)
        b_lbl = Text("Option B: stripe/profile DP", color=self.COLOR_BOARD).scale(self.SCALE_SMALL)
        b_lbl.next_to(opt_b, UP, buff=0.15)
        b_inside = VGroup(
            Text("frontier mask RAM", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("enumerate local placements", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("dedup / hash buckets", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("predictable throughput", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        b_inside.move_to(opt_b.get_center())

        # Shared I/O.
        inp = RoundedRectangle(width=3.6, height=1.0, corner_radius=0.15, color=self.COLOR_ACCENT)
        inp.shift(UP * 2.6)
        inp_lbl = Text("region + required counts", color=self.COLOR_ACCENT).scale(self.SCALE_SMALL)
        inp_lbl.next_to(inp, UP, buff=0.12)

        out = RoundedRectangle(width=3.6, height=1.0, corner_radius=0.15, color=self.COLOR_OK)
        out.shift(DOWN * 2.8)
        out_lbl = Text("feasible? yes/no", color=self.COLOR_OK).scale(self.SCALE_SMALL)
        out_lbl.next_to(out, DOWN, buff=0.12)

        self.play(Create(inp), Write(inp_lbl), run_time=self.STANDARD)
        for mob, lbl, inside in [(opt_a, a_lbl, a_inside), (opt_b, b_lbl, b_inside)]:
            self.play(Create(mob), Write(lbl), run_time=self.STANDARD)
            self.play(FadeIn(inside, shift=UP * 0.1), run_time=self.STANDARD)
            self.wait(0.8)
        self.play(Create(out), Write(out_lbl), run_time=self.STANDARD)

        arrows = VGroup(
            Arrow(inp.get_bottom(), opt_a.get_top(), buff=0.1, color=WHITE),
            Arrow(inp.get_bottom(), opt_b.get_top(), buff=0.1, color=WHITE),
            Arrow(opt_a.get_bottom(), out.get_top(), buff=0.1, color=WHITE),
            Arrow(opt_b.get_bottom(), out.get_top(), buff=0.1, color=WHITE),
        )
        self.play(*[Create(a) for a in arrows], run_time=self.STANDARD)

        note = Text("FPGA takeaway: bitmasks + AND checks are extremely fast", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        note.to_edge(DOWN)
        self.play(FadeIn(note, shift=UP * 0.1), run_time=self.STANDARD)

        self.wait(self.HOLD)
