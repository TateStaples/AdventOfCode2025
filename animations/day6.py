"""animations/day6.py

Day 6 — Trash Compactor (ASCII Worksheet Arithmetic)

This animation follows the storyboard in animations/day_by_day_video_scripts.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from manim import *


@dataclass(frozen=True)
class GridRef:
    grid: VGroup
    cells: Dict[Tuple[int, int], VGroup]
    width: int
    height: int
    cell_size: float


class Day6(Scene):
    # Timing
    FAST = 0.25
    STANDARD = 0.7
    LONG = 1.3
    HOLD = 29.0

    # Colors
    COLOR_TEXT = GRAY_E
    COLOR_DIM = GRAY_C
    COLOR_SHEET = GRAY_B
    COLOR_CELL = GRAY_E
    COLOR_SPACE = GRAY_C
    COLOR_HILITE = YELLOW_E
    COLOR_BLOCK = WHITE
    COLOR_PLUS = GOLD_E
    COLOR_MUL = RED_E
    COLOR_CURSOR = TEAL_A
    COLOR_EMIT = ORANGE
    COLOR_PARSER = BLUE_C
    COLOR_ACC = GREEN_C

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
        self.scene_blocks()
        self.clear()
        self.scene_part1_rowwise()
        self.clear()
        self.scene_part2_colwise()
        self.clear()
        self.scene_boundary_scan()
        self.clear()
        self.scene_worked_example()
        self.clear()
        self.scene_fpga_option_a_bram()
        self.clear()
        self.scene_unified_parser()
        self.clear()
        self.scene_fpga_option_b_c()
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

    def make_counter(self, label: str, value: int = 0) -> Tuple[VGroup, VGroup]:
        lbl = Text(label, color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        val = Text(str(value), color=self.COLOR_ACC).scale(self.SCALE_SMALL)
        box = RoundedRectangle(width=2.3, height=0.9, corner_radius=0.15, color=self.COLOR_DIM)
        group = VGroup(lbl, val).arrange(DOWN, buff=0.1).move_to(box)
        return VGroup(box, group), val

    def update_counter_value(self, counter_value_text: VGroup, value: int) -> Animation:
        new_text = Text(str(value), color=self.COLOR_ACC).scale(self.SCALE_SMALL)
        new_text.move_to(counter_value_text)
        return Transform(counter_value_text, new_text)

    def ascii_sheet(self) -> List[str]:
        # Three blocks separated by full blank columns. Last row is the operator row.
        # Spaces are meaningful: they form separators and digit gaps.
        # Layout: block1[0..4] sep[5] block2[6..10] sep[11] block3[12..16]
        return [
            "12 3  " + " " + "9  7 " + " " + "4  5 ",
            "4 56 " + " " + "1  0 " + " " + "6  2 ",
            "7 89 " + " " + "2  3 " + " " + "1  8 ",
            "0 12 " + " " + "4  9 " + " " + "0  1 ",
            "  +  " + " " + "  *  " + " " + "  +  ",
        ]

    def build_grid(self, lines: List[str], cell_size: float = 0.45) -> GridRef:
        height = len(lines)
        width = max(len(line) for line in lines)
        padded = [line.ljust(width) for line in lines]

        cells: Dict[Tuple[int, int], VGroup] = {}
        grid = VGroup()
        for y in range(height):
            for x in range(width):
                ch = padded[y][x]
                is_space = ch == " "
                base = Square(side_length=cell_size, stroke_color=self.COLOR_SHEET, stroke_width=1)
                base.set_fill(self.COLOR_SPACE if is_space else self.COLOR_CELL, opacity=0.12 if is_space else 0.16)
                txt = Text(ch if ch != " " else " ", font="Monospace", color=self.COLOR_TEXT)
                txt.scale(self.SCALE_TINY)
                txt.move_to(base)
                cell = VGroup(base, txt)
                cell.shift(RIGHT * (x * cell_size) + DOWN * (y * cell_size))
                cells[(x, y)] = cell
                grid.add(cell)

        # Normalize origin to top-left-ish
        grid.move_to(ORIGIN)
        grid.shift(UP * (height * cell_size / 2) + LEFT * (width * cell_size / 2))
        return GridRef(grid=grid, cells=cells, width=width, height=height, cell_size=cell_size)

    def cell_center(self, grid: GridRef, x: int, y: int) -> np.ndarray:
        return grid.cells[(x, y)].get_center()

    def column_is_blank(self, grid: GridRef, x: int, y0: int, y1: int, operator_row_y: int) -> bool:
        # Separator columns are blank *in the problem rows*.
        for y in range(y0, y1 + 1):
            if y == operator_row_y:
                continue
            ch = grid.cells[(x, y)][1].text
            if ch.strip() != "":
                return False
        return True

    def highlight_column(self, grid: GridRef, x: int, color: ManimColor, opacity: float = 0.18) -> VGroup:
        rect = Rectangle(
            width=grid.cell_size,
            height=grid.height * grid.cell_size,
            stroke_color=color,
            stroke_width=2,
            fill_color=color,
            fill_opacity=opacity,
        )
        top = self.cell_center(grid, x, 0) + UP * (grid.cell_size / 2)
        rect.move_to(top + DOWN * (grid.height * grid.cell_size / 2))
        return rect

    def block_box(self, grid: GridRef, x0: int, x1: int, y0: int, y1: int) -> RoundedRectangle:
        rect = RoundedRectangle(
            width=(x1 - x0 + 1) * grid.cell_size + 0.18,
            height=(y1 - y0 + 1) * grid.cell_size + 0.18,
            corner_radius=0.12,
            color=self.COLOR_BLOCK,
        )
        center = (self.cell_center(grid, x0, y0) + self.cell_center(grid, x1, y1)) / 2
        rect.move_to(center)
        return rect

    def cursor_rect(self, grid: GridRef, x: int, y: int) -> RoundedRectangle:
        rect = RoundedRectangle(
            width=grid.cell_size * 0.98,
            height=grid.cell_size * 0.98,
            corner_radius=0.08,
            color=self.COLOR_CURSOR,
        )
        rect.move_to(self.cell_center(grid, x, y))
        return rect

    # Scenes ------------------------------------------------------------------
    def scene_hook(self) -> None:
        title = Text("Day 6 — Trash Compactor", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("A worksheet full of problems", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)

        grid = self.build_grid(self.ascii_sheet(), cell_size=0.47)
        sheet_bg = RoundedRectangle(
            width=grid.width * grid.cell_size + 0.6,
            height=grid.height * grid.cell_size + 0.6,
            corner_radius=0.18,
            color=self.COLOR_DIM,
        )
        sheet_bg.set_fill(self.COLOR_DIM, opacity=0.06)
        sheet_bg.move_to(grid.grid)

        legend = Text("operator row: + / *", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        legend.to_corner(DR)

        self.play(Write(title), FadeIn(subtitle, shift=DOWN))
        self.play(FadeIn(sheet_bg), FadeIn(grid.grid))
        self.play(FadeIn(legend, shift=UP))

        # Pan/zoom into the middle block briefly.
        focus_box = self.block_box(grid, x0=6, x1=10, y0=0, y1=4)
        focus_box.set_stroke(self.COLOR_BLOCK, width=3)
        self.play(Create(focus_box), run_time=self.STANDARD)
        self.wait(self.LONG)
        self.play(FadeOut(focus_box), run_time=self.FAST)
        self.wait(self.HOLD)

    def scene_blocks(self) -> None:
        title = Text("What counts as a block?", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("Separated by a fully blank column", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        grid = self.build_grid(self.ascii_sheet(), cell_size=0.52)
        grid.grid.shift(DOWN * 0.2)
        self.play(FadeIn(grid.grid))

        operator_row_y = grid.height - 1
        y0, y1 = 0, operator_row_y
        cursor = self.highlight_column(grid, 0, self.COLOR_CURSOR, opacity=0.08)
        self.play(FadeIn(cursor), run_time=self.FAST)

        blank_cols: List[int] = []
        for x in range(grid.width):
            target_center = self.highlight_column(grid, x, self.COLOR_CURSOR, opacity=0.08).get_center()
            self.play(cursor.animate.move_to(target_center), run_time=0.08)
            if self.column_is_blank(grid, x, y0, y1, operator_row_y=operator_row_y):
                blank_cols.append(x)
                hl = self.highlight_column(grid, x, self.COLOR_HILITE, opacity=0.16)
                self.play(FadeIn(hl), run_time=self.FAST)
            

        # Box the discovered blocks.
        block1 = self.block_box(grid, 0, 4, 0, operator_row_y)
        block2 = self.block_box(grid, 6, 10, 0, operator_row_y)
        block3 = self.block_box(grid, 12, 16, 0, operator_row_y)
        self.play(Create(block1), Create(block2), Create(block3), run_time=self.STANDARD)
        self.wait(self.HOLD)

    def scene_part1_rowwise(self) -> None:
        title = Text("Part 1: Row-wise numbers", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("Scan left→right, ignore spaces", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        grid = self.build_grid(self.ascii_sheet(), cell_size=0.58)
        operator_row_y = grid.height - 1
        block = self.block_box(grid, 0, 4, 0, operator_row_y)
        grid.grid.shift(LEFT * 2.0 + DOWN * 0.3)
        block.shift(LEFT * 2.0 + DOWN * 0.3)
        self.play(FadeIn(grid.grid), Create(block))

        state_box = RoundedRectangle(width=4.2, height=1.8, corner_radius=0.18, color=self.COLOR_PARSER)
        state_box.to_edge(RIGHT).shift(UP * 1.2)
        state_title = Text("parser state", color=self.COLOR_PARSER).scale(self.SCALE_SMALL)
        state_title.next_to(state_box, UP, buff=0.15)
        num_line = Text("num = 0", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        in_line = Text("in_number = false", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        VGroup(num_line, in_line).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to(state_box)
        self.play(Create(state_box), Write(state_title), FadeIn(num_line), FadeIn(in_line))

        emit_title = Text("emitted numbers", color=self.COLOR_EMIT).scale(self.SCALE_SMALL)
        emit_title.next_to(state_box, DOWN, buff=0.5)
        emit_anchor = Dot(radius=0.001, fill_opacity=0, stroke_opacity=0)
        emit_anchor.next_to(emit_title, DOWN, buff=0.2)
        emit_anchor.align_to(emit_title, LEFT)
        emits = VGroup()
        self.play(Write(emit_title))

        rule = self.make_code_block([
            "if digit: num = 10*num + digit",
            "if space and in_number: emit(num)",
        ])
        rule.to_edge(DOWN)
        self.play(FadeIn(rule, shift=UP))

        # Demonstrate row 0 in block1.
        y = 0
        cursor = self.cursor_rect(grid, 0, y)
        self.play(FadeIn(cursor), run_time=self.FAST)
        num = 0
        in_number = False

        def refresh_state() -> AnimationGroup:
            nonlocal num_line, in_line
            new_num = Text(f"num = {num}", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
            new_num.move_to(num_line)
            new_in = Text(f"in_number = {'true' if in_number else 'false'}", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
            new_in.move_to(in_line)
            return AnimationGroup(Transform(num_line, new_num), Transform(in_line, new_in), lag_ratio=0)

        for x in range(0, 5):
            self.play(cursor.animate.move_to(self.cell_center(grid, x, y)), run_time=self.FAST)
            ch = grid.cells[(x, y)][1].text
            if ch.strip() != "":
                num = 10 * num + int(ch)
                in_number = True
                self.play(refresh_state(), run_time=self.FAST)
            else:
                if in_number:
                    emit = Text(str(num), font="Monospace", color=self.COLOR_EMIT).scale(self.SCALE_SMALL)
                    if len(emits) == 0:
                        emit.move_to(emit_anchor)
                    else:
                        emit.next_to(emits[-1], DOWN, buff=0.15).align_to(emits[-1], LEFT)
                    emits.add(emit)
                    self.play(FadeIn(emit, shift=RIGHT * 0.2), run_time=self.FAST)
                    num = 0
                    in_number = False
                    self.play(refresh_state(), run_time=self.FAST)

        # End of row emits if needed.
        if in_number:
            emit = Text(str(num), font="Monospace", color=self.COLOR_EMIT).scale(self.SCALE_SMALL)
            if len(emits) == 0:
                emit.move_to(emit_anchor)
            else:
                emit.next_to(emits[-1], DOWN, buff=0.15).align_to(emits[-1], LEFT)
            emits.add(emit)
            self.play(FadeIn(emit, shift=RIGHT * 0.2), run_time=self.FAST)

        self.play(FadeIn(emits), run_time=self.FAST)
        self.wait(self.LONG)
        self.wait(self.HOLD)

    def scene_part2_colwise(self) -> None:
        title = Text("Part 2: Column-wise numbers", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("Scan columns right→left, top→bottom", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        grid = self.build_grid(self.ascii_sheet(), cell_size=0.56)
        operator_row_y = grid.height - 1
        grid.grid.shift(LEFT * 2.1 + DOWN * 0.2)
        block = self.block_box(grid, 6, 10, 0, operator_row_y)
        block.shift(LEFT * 2.1 + DOWN * 0.2)
        self.play(FadeIn(grid.grid), Create(block))

        emit_box = RoundedRectangle(width=4.2, height=3.2, corner_radius=0.18, color=self.COLOR_EMIT)
        emit_box.to_edge(RIGHT).shift(DOWN * 0.1)
        emit_title = Text("emits (one per column)", color=self.COLOR_EMIT).scale(self.SCALE_SMALL)
        emit_title.next_to(emit_box, UP, buff=0.15)
        emit_anchor = Dot(radius=0.001, fill_opacity=0, stroke_opacity=0)
        emit_anchor.move_to(emit_box.get_top() + DOWN * 0.55)
        emit_anchor.align_to(emit_box, LEFT)
        emit_anchor.shift(RIGHT * 0.25)
        emits = VGroup()
        self.play(Create(emit_box), Write(emit_title))

        cursor = self.cursor_rect(grid, 10, 0)
        self.play(FadeIn(cursor), run_time=self.FAST)

        emitted_vals: List[int] = []
        for x in range(10, 5, -1):
            num = 0
            started = False
            for y in range(0, operator_row_y):
                self.play(cursor.animate.move_to(self.cell_center(grid, x, y)), run_time=self.FAST)
                ch = grid.cells[(x, y)][1].text
                if ch.strip() != "":
                    num = 10 * num + int(ch)
                    started = True
            if started:
                emitted_vals.append(num)
                t = Text(str(num), font="Monospace", color=self.COLOR_EMIT).scale(self.SCALE_SMALL)
                if len(emits) == 0:
                    t.move_to(emit_anchor)
                else:
                    t.next_to(emits[-1], DOWN, buff=0.15).align_to(emits[-1], LEFT)
                emits.add(t)
                self.play(FadeIn(t, shift=RIGHT * 0.2), run_time=self.FAST)
            self.play(cursor.animate.move_to(self.cell_center(grid, x - 1, 0)), run_time=self.FAST)

        self.wait(self.LONG)
        self.wait(self.HOLD)

    def scene_boundary_scan(self) -> None:
        title = Text("Finding blocks: scan the operator row", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("Right→left, group non-space columns", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        grid = self.build_grid(self.ascii_sheet(), cell_size=0.52)
        grid.grid.shift(DOWN * 0.1)
        self.play(FadeIn(grid.grid))

        operator_row_y = grid.height - 1
        scan_y = operator_row_y

        cursor = self.cursor_rect(grid, grid.width - 1, scan_y)
        self.play(FadeIn(cursor), run_time=self.FAST)

        selection = RoundedRectangle(width=grid.cell_size, height=grid.height * grid.cell_size, corner_radius=0.12, color=self.COLOR_BLOCK)
        selection.set_fill(self.COLOR_BLOCK, opacity=0.03)
        self.play(FadeIn(selection), run_time=self.FAST)

        active_x1: int | None = None
        for x in range(grid.width - 1, -1, -1):
            self.play(cursor.animate.move_to(self.cell_center(grid, x, scan_y)), run_time=self.FAST)
            ch = grid.cells[(x, scan_y)][1].text
            if ch.strip() != "":
                if active_x1 is None:
                    active_x1 = x
                selection.width = (active_x1 - x + 1) * grid.cell_size
                selection.move_to((self.cell_center(grid, x, 0) + self.cell_center(grid, active_x1, grid.height - 1)) / 2)
            else:
                if active_x1 is not None:
                    box = self.block_box(grid, x + 1, active_x1, 0, operator_row_y)
                    self.play(Create(box), run_time=self.STANDARD)
                    active_x1 = None
        self.wait(self.HOLD)

    def scene_worked_example(self) -> None:
        title = Text("Worked block example", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("Fold digits, then reduce by operator", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        block_lines = [
            "123",
            "45 ",
            "6  ",
            " * ",
        ]
        grid = self.build_grid(block_lines, cell_size=0.75)
        grid.grid.shift(LEFT * 3.0 + DOWN * 0.4)
        self.play(FadeIn(grid.grid))

        nums = VGroup(
            Text("123", font="Monospace", color=self.COLOR_EMIT).scale(self.SCALE_SUB),
            Text("45", font="Monospace", color=self.COLOR_EMIT).scale(self.SCALE_SUB),
            Text("6", font="Monospace", color=self.COLOR_EMIT).scale(self.SCALE_SUB),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        nums.to_edge(RIGHT).shift(UP * 0.8)
        label = Text("row numbers", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        label.next_to(nums, UP, buff=0.15)
        self.play(Write(label), FadeIn(nums, shift=LEFT))

        op = Text("*", font="Monospace", color=self.COLOR_MUL).scale(self.SCALE_TITLE)
        op.next_to(nums, DOWN, buff=0.6).align_to(nums, LEFT)
        self.play(Write(op))

        prod = Text("123 × 45 × 6", color=self.COLOR_TEXT).scale(self.SCALE_TEXT)
        prod.next_to(op, DOWN, buff=0.35).align_to(nums, LEFT)
        result = Text("= 33210", color=self.COLOR_ACC).scale(self.SCALE_TEXT)
        result.next_to(prod, DOWN, buff=0.2).align_to(prod, LEFT)
        self.play(Write(prod), Write(result))
        self.wait(self.HOLD)

    def scene_fpga_option_a_bram(self) -> None:
        title = Text("FPGA Option A: buffer the grid", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("BRAM + two scan modes", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        bram = RoundedRectangle(width=3.8, height=2.1, corner_radius=0.18, color=self.COLOR_DIM)
        bram.set_fill(self.COLOR_DIM, opacity=0.08)
        bram_label = Text("Grid BRAM\naddr=(x,y)", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        bram_label.move_to(bram)
        bram_group = VGroup(bram, bram_label).shift(UP * 0.2)

        gen_row = RoundedRectangle(width=3.2, height=1.1, corner_radius=0.15, color=self.COLOR_PARSER)
        gen_row.set_fill(self.COLOR_PARSER, opacity=0.06)
        gen_row_label = Text("addr gen\nrow-wise", color=self.COLOR_PARSER).scale(self.SCALE_SMALL)
        gen_row_label.move_to(gen_row)

        gen_col = RoundedRectangle(width=3.2, height=1.1, corner_radius=0.15, color=self.COLOR_EMIT)
        gen_col.set_fill(self.COLOR_EMIT, opacity=0.06)
        gen_col_label = Text("addr gen\ncol-wise", color=self.COLOR_EMIT).scale(self.SCALE_SMALL)
        gen_col_label.move_to(gen_col)

        gens = VGroup(VGroup(gen_row, gen_row_label), VGroup(gen_col, gen_col_label)).arrange(DOWN, buff=0.5)
        gens.to_edge(LEFT).shift(DOWN * 0.5)

        mux = RoundedRectangle(width=1.2, height=1.2, corner_radius=0.15, color=PURPLE_C)
        mux.set_fill(PURPLE_C, opacity=0.08)
        mux_label = Text("mode\nMUX", color=PURPLE_C).scale(self.SCALE_TINY)
        mux_label.move_to(mux)
        mux_group = VGroup(mux, mux_label).next_to(gens, RIGHT, buff=0.6)

        arrow_row = Arrow(gens[0].get_right(), mux_group.get_left(), buff=0.1, color=self.COLOR_PARSER)
        arrow_col = Arrow(gens[1].get_right(), mux_group.get_left(), buff=0.1, color=self.COLOR_EMIT)
        arrow_to_bram = Arrow(mux_group.get_right(), bram_group.get_left(), buff=0.1, color=self.COLOR_TEXT)

        scanner = RoundedRectangle(width=3.8, height=1.0, corner_radius=0.15, color=self.COLOR_BLOCK)
        scanner.set_fill(self.COLOR_BLOCK, opacity=0.04)
        scanner_label = Text("boundary scanner\n(operator row)", color=self.COLOR_BLOCK).scale(self.SCALE_SMALL)
        scanner_label.move_to(scanner)
        scanner_group = VGroup(scanner, scanner_label).next_to(bram_group, DOWN, buff=0.5)

        self.play(FadeIn(gens), FadeIn(mux_group), FadeIn(bram_group), FadeIn(scanner_group))
        self.play(Create(arrow_row), Create(arrow_col), Create(arrow_to_bram), run_time=self.STANDARD)
        self.wait(self.LONG)
        self.wait(self.HOLD)

    def scene_unified_parser(self) -> None:
        title = Text("One unified number parser", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("Only address generation changes", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        left = RoundedRectangle(width=3.2, height=1.3, corner_radius=0.18, color=self.COLOR_DIM)
        left.set_fill(self.COLOR_DIM, opacity=0.06)
        left_label = Text("char stream", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        left_label.move_to(left)

        parser = RoundedRectangle(width=3.0, height=1.6, corner_radius=0.18, color=self.COLOR_PARSER)
        parser.set_fill(self.COLOR_PARSER, opacity=0.08)
        parser_label = Text("digit folder\n+ end-of-number", color=self.COLOR_PARSER).scale(self.SCALE_SMALL)
        parser_label.move_to(parser)

        right = RoundedRectangle(width=3.2, height=1.3, corner_radius=0.18, color=self.COLOR_EMIT)
        right.set_fill(self.COLOR_EMIT, opacity=0.08)
        right_label = Text("number stream", color=self.COLOR_EMIT).scale(self.SCALE_SMALL)
        right_label.move_to(right)

        chain = VGroup(VGroup(left, left_label), VGroup(parser, parser_label), VGroup(right, right_label)).arrange(RIGHT, buff=0.8)
        chain.shift(DOWN * 0.2)

        a1 = Arrow(chain[0].get_right(), chain[1].get_left(), buff=0.1, color=self.COLOR_TEXT)
        a2 = Arrow(chain[1].get_right(), chain[2].get_left(), buff=0.1, color=self.COLOR_TEXT)

        self.play(FadeIn(chain), Create(a1), Create(a2))

        digits = VGroup(
            Text("'1'", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("'2'", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("'3'", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("end", font="Monospace", color=self.COLOR_ACC).scale(self.SCALE_SMALL),
        ).arrange(RIGHT, buff=0.25)
        digits.next_to(chain, DOWN, buff=0.7)
        self.play(FadeIn(digits, shift=UP * 0.2))
        self.wait(self.LONG)
        self.wait(self.HOLD)

    def scene_fpga_option_b_c(self) -> None:
        title = Text("Option B/C: streaming vs. parallel blocks", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("Segmentation depends on the bottom row", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        left = RoundedRectangle(width=5.5, height=3.6, corner_radius=0.18, color=self.COLOR_DIM)
        left.set_fill(self.COLOR_DIM, opacity=0.06)
        left.to_edge(LEFT).shift(DOWN * 0.2)
        right = RoundedRectangle(width=5.5, height=3.6, corner_radius=0.18, color=self.COLOR_DIM)
        right.set_fill(self.COLOR_DIM, opacity=0.06)
        right.to_edge(RIGHT).shift(DOWN * 0.2)
        self.play(FadeIn(left), FadeIn(right))

        lt = Text("Two-pass stream", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        lt.next_to(left, UP, buff=0.15)
        rt = Text("Per-block engines", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        rt.next_to(right, UP, buff=0.15)
        self.play(Write(lt), Write(rt))

        pass1 = Text("pass 1: read operator row", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        pass2 = Text("pass 2: parse blocks", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        VGroup(pass1, pass2).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to(left)

        lock = Text("needs bottom row first", color=self.COLOR_HILITE).scale(self.SCALE_SMALL)
        lock.next_to(pass2, DOWN, buff=0.35).align_to(pass2, LEFT)

        engines = VGroup(
            RoundedRectangle(width=1.4, height=0.9, corner_radius=0.12, color=self.COLOR_PARSER),
            RoundedRectangle(width=1.4, height=0.9, corner_radius=0.12, color=self.COLOR_PARSER),
            RoundedRectangle(width=1.4, height=0.9, corner_radius=0.12, color=self.COLOR_PARSER),
        ).arrange(DOWN, buff=0.35).move_to(right)
        for e in engines:
            e.set_fill(self.COLOR_PARSER, opacity=0.06)
        engine_lbl = Text("replicate when blocks bounded", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        engine_lbl.next_to(engines, DOWN, buff=0.35)

        self.play(FadeIn(pass1), FadeIn(pass2), FadeIn(lock), FadeIn(engines), FadeIn(engine_lbl))
        self.wait(self.HOLD)

    def scene_takeaway(self) -> None:
        title = Text("Takeaway", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        tagline = Text("Treat text like an image.", color=self.COLOR_TEXT).scale(0.9)
        tagline.move_to(ORIGIN)

        bg_grid = self.build_grid(self.ascii_sheet(), cell_size=0.58)
        bg_grid.grid.set_opacity(0.18)
        bg_grid.grid.shift(DOWN * 0.2)

        self.play(Write(title), FadeIn(bg_grid.grid))
        self.play(Write(tagline))
        self.wait(self.HOLD)
