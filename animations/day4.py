"""Day 4: Printing Department (Roll Peeling)

Storyboard target: 6:00–7:30

Core idea:
- A roll '@' is accessible if it has <4 of its 8 neighbors as '@'.
- Part 1: count accessible at the start.
- Part 2: repeatedly remove accessible rolls until stable.

Key trick (paper + storyboard aligned):
Removing one roll only affects its 8 neighbors, and a roll becomes newly
accessible exactly when its neighbor count crosses 4→3. That enables an
event-driven queue instead of full rescans.
"""

from __future__ import annotations

from manim import *


class Day4(Scene):
    # Timing
    # These are intentionally generous so students can read/absorb.
    FAST = 0.9
    STANDARD = 2.2
    LONG = 4.0
    HOLD = 7.0

    # Visual constants
    CELL_SIZE = 0.45
    COLOR_ROLL = YELLOW
    COLOR_EMPTY = DARK_GRAY
    COLOR_HIGHLIGHT = RED
    COLOR_TODO = PURPLE_C
    COLOR_GOOD = GREEN_C
    COLOR_TEXT = GRAY_E

    EXAMPLE = [
        "..@@.@@@@.",
        "@@@.@.@.@@",
        "@@@@@.@.@@",
        "@.@@@@..@.",
        "@@.@@@@.@@",
        ".@@@@@@@.@",
        ".@.@.@.@@@",
        "@.@@@.@@@@",
        ".@@@@@@@@.",
        "@.@.@@@.@.",
    ]

    MINI = [
        ".@.",
        "@@@",
        ".@.",
    ]

    MEDIUM = [
        "..@..",
        ".@@@.",
        "..@..",
        ".@@@.",
        "..@..",
    ]

    def construct(self) -> None:
        self.scene_intro_through_event_queue()
        self.clear()
        self.scene_correctness()
        self.clear()
        self.scene_fpga_option_a_dense()
        self.clear()
        self.scene_fpga_option_b_queue()
        self.clear()
        self.scene_fpga_option_c_hybrid()
        self.clear()
        self.scene_hardcaml_highlight()
        self.clear()
        self.scene_takeaway()

    # ---------- helpers ----------
    def build_grid(self, lines: list[str]) -> tuple[VGroup, dict[tuple[int, int], Square]]:
        rows = []
        pos_to_square: dict[tuple[int, int], Square] = {}
        for r, line in enumerate(lines):
            row = []
            for c, ch in enumerate(line):
                sq = Square(side_length=self.CELL_SIZE, stroke_width=1, color=self.COLOR_TEXT)
                sq.set_fill(self.COLOR_ROLL if ch == "@" else self.COLOR_EMPTY, opacity=1 if ch == "@" else 0.15)
                pos_to_square[(r, c)] = sq
                row.append(sq)
            rows.append(VGroup(*row).arrange(RIGHT, buff=0))
        grid = VGroup(*rows).arrange(DOWN, buff=0).scale(0.9)
        return grid, pos_to_square

    def build_magnifier(self, lines: list[str], center: tuple[int, int]) -> VGroup:
        """Small 3x3 neighborhood view with a counter."""
        cr, cc = center
        rows, cols = len(lines), len(lines[0])
        panel = RoundedRectangle(width=3.6, height=2.8, corner_radius=0.2, color=WHITE)
        title = Text("3×3 neighborhood", color=WHITE).scale(0.42)
        title.next_to(panel.get_top(), DOWN, buff=0.2)

        cells = VGroup()
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                r, c = cr + dr, cc + dc
                ch = "."
                in_bounds = 0 <= r < rows and 0 <= c < cols
                if in_bounds:
                    ch = lines[r][c]
                sq = Square(side_length=0.45, stroke_width=1, color=self.COLOR_TEXT)
                if ch == "@":
                    sq.set_fill(self.COLOR_ROLL, opacity=1)
                else:
                    sq.set_fill(self.COLOR_EMPTY, opacity=0.12)
                label = Text(ch if in_bounds else " ", color=WHITE).scale(0.35)
                label.move_to(sq)
                cell = VGroup(sq, label)
                if dr == 0 and dc == 0:
                    cell.add(SurroundingRectangle(sq, color=self.COLOR_HIGHLIGHT, buff=0.05))
                cells.add(cell)
        cells.arrange_in_grid(rows=3, cols=3, buff=0.05)
        cells.move_to(panel.get_center() + DOWN * 0.1)

        count = self.neighbor_count(lines, cr, cc)
        count_text = Text(f"neighbors = {count}", color=self.COLOR_HIGHLIGHT).scale(0.45)
        count_text.next_to(panel.get_bottom(), UP, buff=0.2)
        rule = Text("accessible if < 4", color=self.COLOR_TEXT).scale(0.4)
        rule.next_to(count_text, DOWN, buff=0.12)

        return VGroup(panel, title, cells, count_text, rule)

    def make_counter_box(self, label: str, value: int, color: str) -> VGroup:
        box = RoundedRectangle(width=3.7, height=1.05, corner_radius=0.2, color=color)
        lbl = Text(label, color=color).scale(0.42).to_edge(LEFT)
        lbl.move_to(box.get_left() + RIGHT * 1.2)
        val = Text(str(value), color=WHITE).scale(0.6)
        val.move_to(box.get_right() + LEFT * 0.7)
        return VGroup(box, lbl, val)

    def make_todo_queue(self, title: str = "todo queue") -> VGroup:
        panel = RoundedRectangle(width=4.2, height=2.2, corner_radius=0.2, color=self.COLOR_TODO)
        t = Text(title, color=self.COLOR_TODO).scale(0.46)
        t.next_to(panel.get_top(), DOWN, buff=0.2)
        slots = VGroup(*[
            Rectangle(width=3.6, height=0.35, color=self.COLOR_TODO, fill_opacity=0.08)
            for _ in range(4)
        ]).arrange(DOWN, buff=0.12)
        slots.move_to(panel.get_center() + DOWN * 0.25)
        return VGroup(panel, t, slots)

    def todo_set_text(self, todo: VGroup, lines: list[str]) -> VGroup:
        # todo[2] is slots
        texts = VGroup(*[
            Text(s, font="Monospace", color=WHITE).scale(0.32) for s in lines
        ])
        texts.arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        texts.move_to(todo[2].get_center())
        return texts

    def neighbor_count(self, grid_data: list[str], r: int, c: int) -> int:
        rows, cols = len(grid_data), len(grid_data[0])
        total = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid_data[nr][nc] == "@":
                    total += 1
        return total

    def accessible_cells(self, grid_data: list[str]) -> list[tuple[int, int]]:
        rows, cols = len(grid_data), len(grid_data[0])
        cells = []
        for r in range(rows):
            for c in range(cols):
                if grid_data[r][c] != "@":
                    continue
                if self.neighbor_count(grid_data, r, c) < 4:
                    cells.append((r, c))
        return cells

    def removal_waves(self, grid_data: list[str]) -> list[list[tuple[int, int]]]:
        data = [list(row) for row in grid_data]
        waves: list[list[tuple[int, int]]] = []
        while True:
            accessible = []
            for r in range(len(data)):
                for c in range(len(data[0])):
                    if data[r][c] != "@":
                        continue
                    if self.neighbor_count(["".join(row) for row in data], r, c) < 4:
                        accessible.append((r, c))
            if not accessible:
                break
            for r, c in accessible:
                data[r][c] = "."
            waves.append(accessible)
        return waves

    # ---------- scenes ----------
    def scene_intro_through_event_queue(self) -> None:
        """Storyboard Scenes 1–5: Hook, outputs, neighbor counting, 4→3 queue trick, mini example."""

        title = Text("Day 4: Printing Department", color=WHITE).scale(0.8).to_edge(UP)
        subtitle = Text("A roll is accessible if it has <4 neighbors (8 directions)", color=self.COLOR_TEXT).scale(0.5)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(FadeIn(title), FadeIn(subtitle, shift=DOWN), run_time=self.STANDARD)

        grid, pos = self.build_grid(self.EXAMPLE)
        grid.to_edge(LEFT, buff=0.7).shift(DOWN * 0.15)
        self.play(Create(grid), run_time=self.STANDARD)

        # Pick one accessible roll to magnify.
        accessible = self.accessible_cells(self.EXAMPLE)
        focus = accessible[0] if accessible else (0, 2)
        r0, c0 = focus
        focus_rect = SurroundingRectangle(pos[(r0, c0)], color=self.COLOR_HIGHLIGHT, buff=0.05)
        self.play(Create(focus_rect), run_time=self.FAST)

        magnifier = self.build_magnifier(self.EXAMPLE, focus)
        magnifier.to_edge(RIGHT, buff=0.6).shift(UP * 1.25)
        self.play(FadeIn(magnifier, shift=LEFT), run_time=self.STANDARD)

        # Count the 8 neighbors explicitly (visual + pacing).
        cr, cc = focus
        cells = magnifier[2]
        shown = Text("neighbors = 0", color=self.COLOR_HIGHLIGHT).scale(0.45)
        shown.move_to(magnifier[3])
        self.play(Transform(magnifier[3], shown), run_time=self.STANDARD)

        ring = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]
        running = 0
        for dr, dc in ring:
            idx = (dr + 1) * 3 + (dc + 1)
            nbr_r, nbr_c = cr + dr, cc + dc
            in_bounds = 0 <= nbr_r < len(self.EXAMPLE) and 0 <= nbr_c < len(self.EXAMPLE[0])
            is_roll = in_bounds and self.EXAMPLE[nbr_r][nbr_c] == "@"
            self.play(Flash(cells[idx], color=YELLOW, flash_radius=0.32), run_time=self.FAST)
            if is_roll:
                running += 1
                new_text = Text(f"neighbors = {running}", color=self.COLOR_HIGHLIGHT).scale(0.45)
                new_text.move_to(magnifier[3])
                self.play(Transform(magnifier[3], new_text), run_time=self.FAST)
            else:
                self.wait(0.15)

        final = self.neighbor_count(self.EXAMPLE, cr, cc)
        final_text = Text(f"neighbors = {final}", color=self.COLOR_HIGHLIGHT).scale(0.45)
        final_text.move_to(magnifier[3])
        self.play(Transform(magnifier[3], final_text), run_time=self.STANDARD)
        self.wait(self.HOLD)

        # Scene 2: outputs + counters (persistent through Scene 5)
        p1 = self.make_counter_box("Part 1: accessible at start", 0, self.COLOR_HIGHLIGHT)
        p2 = self.make_counter_box("Part 2: total removed", 0, self.COLOR_GOOD)
        counters = VGroup(p1, p2).arrange(DOWN, buff=0.25)
        counters.next_to(magnifier, DOWN, buff=0.35)
        self.play(FadeIn(counters, shift=DOWN), run_time=self.STANDARD)

        # Mark initial accessible for Part 1.
        x_marks = VGroup()
        for r, c in accessible[:22]:
            cross = Cross(scale_factor=0.32).set_color(self.COLOR_HIGHLIGHT)
            cross.move_to(pos[(r, c)].get_center())
            x_marks.add(cross)
        self.play(LaggedStart(*[Create(x) for x in x_marks], lag_ratio=0.03), run_time=self.LONG)

        p1_value = Text(str(len(accessible)), color=WHITE).scale(0.6)
        p1_value.move_to(p1[2].get_center())
        self.play(Transform(p1[2], p1_value), run_time=self.STANDARD)
        self.wait(self.LONG)

        # Part 2 preview: removal happens in waves, and removing can unlock more.
        p2_total = 0
        self.play(Transform(p2[2], Text(str(p2_total), color=WHITE).scale(0.6).move_to(p2[2])), run_time=self.FAST)

        waves = self.removal_waves(self.EXAMPLE)
        preview_title = Text("Part 2: removing accessible rolls can cause a cascade", color=self.COLOR_GOOD).scale(0.46)
        preview_title.next_to(counters, DOWN, buff=0.35)
        self.play(FadeIn(preview_title, shift=DOWN), run_time=self.STANDARD)

        for wave_idx, wave in enumerate(waves[:3], start=1):
            if not wave:
                continue
            label = Text(f"Wave {wave_idx}: remove {len(wave)}", color=self.COLOR_GOOD).scale(0.48)
            label.next_to(grid, DOWN, buff=0.4)
            highlights = VGroup(*[
                SurroundingRectangle(pos[(r, c)], color=self.COLOR_GOOD, buff=0.05)
                for (r, c) in wave
            ])
            self.play(FadeIn(label), LaggedStart(*[Create(h) for h in highlights], lag_ratio=0.02), run_time=self.LONG)
            self.play(*[pos[(r, c)].animate.set_fill(self.COLOR_EMPTY, opacity=0.12) for (r, c) in wave], run_time=self.LONG)
            p2_total += len(wave)
            self.play(Transform(p2[2], Text(str(p2_total), color=WHITE).scale(0.6).move_to(p2[2])), run_time=self.STANDARD)
            self.play(FadeOut(label), FadeOut(highlights), run_time=self.STANDARD)
            self.wait(self.STANDARD)

        self.play(FadeOut(preview_title), run_time=self.STANDARD)
        self.wait(self.STANDARD)

        # Scene 3: neighbor counting in 8 directions (zoomed explanation)
        formula = MathTex(r"c(p) = \sum_{q \in N_8(p)} [q\;\text{is}\;@]", color=WHITE).scale(0.65)
        formula.to_edge(RIGHT, buff=0.75).shift(UP * 0.1)
        threshold = MathTex(r"\text{accessible} \iff c(p) < 4", color=self.COLOR_HIGHLIGHT).scale(0.7)
        threshold.next_to(formula, DOWN, buff=0.35)
        self.play(FadeIn(formula, shift=UP), FadeIn(threshold, shift=UP), run_time=self.STANDARD)
        self.wait(self.LONG)

        # Scene 4: the 4→3 transition trick
        trick_title = Text("Trick: only neighbors change", color=WHITE).scale(0.55)
        trick_title.next_to(threshold, DOWN, buff=0.35)
        trick_lines = VGroup(
            Text("Remove one @  →  only its 8 neighbors' counts decrement", color=self.COLOR_TEXT).scale(0.42),
            Text("Newly accessible happens exactly on 4 → 3", color=self.COLOR_TODO).scale(0.42),
            Text("So we keep a todo queue of candidates", color=self.COLOR_TODO).scale(0.42),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        trick_lines.next_to(trick_title, DOWN, buff=0.15, aligned_edge=LEFT)
        self.play(Write(trick_title), FadeIn(trick_lines, shift=DOWN), run_time=self.STANDARD)
        self.wait(self.STANDARD)

        # Animate a single removal + neighbor decrement (on the full grid, just as a concept).
        remove_target = accessible[1] if len(accessible) > 1 else focus
        rr, rc = remove_target
        remove_glow = SurroundingRectangle(pos[(rr, rc)], color=self.COLOR_GOOD, buff=0.05)
        self.play(Create(remove_glow), run_time=self.FAST)
        self.play(pos[(rr, rc)].animate.set_fill(self.COLOR_EMPTY, opacity=0.12), FadeOut(remove_glow), run_time=self.STANDARD)
        # Restore for later scenes (we're not simulating the full grid here).
        self.play(pos[(rr, rc)].animate.set_fill(self.COLOR_ROLL, opacity=1), run_time=self.FAST)

        todo = self.make_todo_queue()
        todo.next_to(trick_lines, DOWN, buff=0.25)
        todo_text = self.todo_set_text(todo, ["(r,c)", "...", "...", "..."])
        self.play(FadeIn(todo), FadeIn(todo_text, shift=DOWN), run_time=self.STANDARD)
        self.wait(self.LONG)

        # Scene 5: worked mini example (actual event-driven steps)
        self.play(
            FadeOut(magnifier), FadeOut(formula), FadeOut(threshold), FadeOut(trick_title), FadeOut(trick_lines),
            FadeOut(todo_text),
            run_time=self.STANDARD,
        )

        mini_title = Text("Worked example: a tiny cluster", color=WHITE).scale(0.65)
        mini_title.to_edge(UP)
        self.play(Transform(title, mini_title), FadeOut(subtitle), run_time=self.STANDARD)

        mini_grid, mini_pos = self.build_grid(self.MINI)
        mini_grid.scale(1.25).move_to(ORIGIN + LEFT * 2.1)
        self.play(FadeOut(grid), FadeOut(focus_rect), FadeOut(x_marks), run_time=self.STANDARD)
        self.play(Create(mini_grid), run_time=self.STANDARD)

        # Persistent counters stay on the right.
        self.play(
            counters.animate.next_to(mini_grid, RIGHT, buff=0.8),
            todo.animate.next_to(counters, DOWN, buff=0.45),
            run_time=self.STANDARD,
        )

        # Precompute counts for the mini grid.
        present: dict[tuple[int, int], bool] = {}
        counts: dict[tuple[int, int], int] = {}
        for r in range(3):
            for c in range(3):
                if self.MINI[r][c] == "@":
                    present[(r, c)] = True
                    counts[(r, c)] = self.neighbor_count(self.MINI, r, c)

        count_labels: dict[tuple[int, int], Text] = {}
        for (r, c), cnt in counts.items():
            t = Text(str(cnt), color=WHITE).scale(0.35)
            t.move_to(mini_pos[(r, c)].get_center())
            count_labels[(r, c)] = t
        self.play(*[FadeIn(t) for t in count_labels.values()], run_time=self.STANDARD)
        self.wait(self.STANDARD)

        # Initialize todo with all rolls where count < 4.
        # In the plus-shape: edges are 3 (accessible), center is 4 (not yet accessible).
        todo_items = [(0, 1), (1, 0), (1, 2), (2, 1)]
        todo_text = self.todo_set_text(todo, [f"{p}" for p in todo_items[:4]])
        self.play(FadeIn(todo_text), run_time=self.FAST)
        center_rect = SurroundingRectangle(mini_pos[(1, 1)], color=self.COLOR_HIGHLIGHT, buff=0.06)
        center_note = Text("center has 4 → not accessible yet", color=self.COLOR_HIGHLIGHT).scale(0.42)
        center_note.next_to(center_rect, RIGHT, buff=0.35)
        self.play(Create(center_rect), FadeIn(center_note, shift=RIGHT), run_time=self.STANDARD)
        self.wait(self.LONG)

        removed_total = 0
        p2_value = Text(str(removed_total), color=WHITE).scale(0.6)
        p2_value.move_to(p2[2].get_center())
        self.play(Transform(p2[2], p2_value), run_time=self.FAST)

        def neighbors8(r: int, c: int) -> list[tuple[int, int]]:
            out: list[tuple[int, int]] = []
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < 3 and 0 <= cc < 3 and (rr, cc) in present:
                        out.append((rr, cc))
            return out

        # Step through 4 removals quickly, then show the center removal.
        for step_idx in range(5):
            if not todo_items:
                break
            cur = todo_items.pop(0)
            r, c = cur

            # Update queue display.
            q_lines = [f"{p}" for p in todo_items[:4]]
            q_lines += ["..."] * max(0, 4 - len(q_lines))
            new_todo_text = self.todo_set_text(todo, q_lines)
            self.play(Transform(todo_text, new_todo_text), run_time=self.FAST)

            # Skip duplicates if already removed.
            if not present.get((r, c), False):
                skip = Text("present? no → skip", color=self.COLOR_TEXT).scale(0.42)
                skip.next_to(todo, DOWN, buff=0.15)
                self.play(FadeIn(skip), run_time=self.FAST)
                self.play(FadeOut(skip), run_time=self.FAST)
                continue

            # Remove current.
            hi = SurroundingRectangle(mini_pos[(r, c)], color=self.COLOR_GOOD, buff=0.05)
            self.play(Create(hi), run_time=self.FAST)
            self.play(mini_pos[(r, c)].animate.set_fill(self.COLOR_EMPTY, opacity=0.12), FadeOut(hi), run_time=self.STANDARD)
            present[(r, c)] = False
            removed_total += 1
            self.play(Transform(p2[2], Text(str(removed_total), color=WHITE).scale(0.6).move_to(p2[2])), run_time=self.FAST)

            # Decrement neighbor counts and enqueue on 4→3 (in this tiny example counts are small,
            # but we still animate the local-update idea).
            for nr, nc in neighbors8(r, c):
                if not present.get((nr, nc), False):
                    continue
                old = counts[(nr, nc)]
                counts[(nr, nc)] = max(0, old - 1)
                self.play(
                    Transform(
                        count_labels[(nr, nc)],
                        Text(str(counts[(nr, nc)]), color=WHITE).scale(0.35).move_to(count_labels[(nr, nc)]),
                    ),
                    run_time=0.6,
                )
                if old == 4:
                    # enqueue: newly accessible.
                    todo_items.append((nr, nc))
                    enqueue_note = Text("4→3: enqueue", color=self.COLOR_TODO).scale(0.4)
                    enqueue_note.next_to(mini_pos[(nr, nc)], UP, buff=0.2)
                    self.play(Flash(mini_pos[(nr, nc)], color=self.COLOR_TODO, flash_radius=0.35), FadeIn(enqueue_note), run_time=self.STANDARD)
                    self.play(FadeOut(enqueue_note), run_time=self.FAST)

            # Duplicate enqueue demo (intentionally push one duplicate once)
            if step_idx == 1:
                todo_items.insert(0, (r, c))

            self.wait(0.2)

        self.wait(self.LONG)

        # A slightly larger toy example to show the 4→3 rule *actually* creating new work.
        toy_note = Text(
            "Now a bigger toy: some cells start at 4 (locked),\n"
            "and only become accessible when a neighbor is removed.",
            color=self.COLOR_TEXT,
        ).scale(0.48)
        toy_note.next_to(title, DOWN, buff=0.25)
        self.play(FadeIn(toy_note, shift=DOWN), run_time=self.STANDARD)
        self.wait(self.STANDARD)

        self.play(
            FadeOut(mini_grid),
            *[FadeOut(t) for t in count_labels.values()],
            FadeOut(center_rect),
            FadeOut(center_note),
            FadeOut(todo_text),
            run_time=self.STANDARD,
        )

        toy_grid, toy_pos = self.build_grid(self.MEDIUM)
        toy_grid.scale(1.1).move_to(ORIGIN + LEFT * 2.0)
        self.play(Create(toy_grid), run_time=self.STANDARD)

        # Recompute counts/present for the toy.
        present2: dict[tuple[int, int], bool] = {}
        counts2: dict[tuple[int, int], int] = {}
        for r in range(5):
            for c in range(5):
                if self.MEDIUM[r][c] == "@":
                    present2[(r, c)] = True
                    counts2[(r, c)] = self.neighbor_count(self.MEDIUM, r, c)

        count_labels2: dict[tuple[int, int], Text] = {}
        for (r, c), cnt in counts2.items():
            t = Text(str(cnt), color=WHITE).scale(0.33)
            t.move_to(toy_pos[(r, c)].get_center())
            count_labels2[(r, c)] = t
        self.play(*[FadeIn(t) for t in count_labels2.values()], run_time=self.STANDARD)
        self.wait(self.STANDARD)

        # Highlight the two "locked" 4-count cells.
        locked = [(r, c) for (r, c), cnt in counts2.items() if cnt == 4]
        locked_rects = VGroup(*[SurroundingRectangle(toy_pos[p], color=self.COLOR_HIGHLIGHT, buff=0.06) for p in locked])
        locked_lbl = Text("count = 4 → not accessible yet", color=self.COLOR_HIGHLIGHT).scale(0.44)
        locked_lbl.next_to(locked_rects, RIGHT, buff=0.35)
        self.play(Create(locked_rects), FadeIn(locked_lbl, shift=RIGHT), run_time=self.STANDARD)
        self.wait(self.LONG)

        # Reset Part 2 counter for this toy walkthrough.
        removed_total = 0
        self.play(Transform(p2[2], Text(str(removed_total), color=WHITE).scale(0.6).move_to(p2[2])), run_time=self.STANDARD)

        # Initialize todo with all accessible cells (count < 4).
        todo_items2 = [p for p, cnt in counts2.items() if cnt < 4]

        def format_queue(items: list[tuple[int, int]]) -> list[str]:
            head = [f"{p}" for p in items[:4]]
            if len(items) > 4:
                head[-1] = head[-1] + "  …"
            head += [" "] * max(0, 4 - len(head))
            return head

        todo_text2 = self.todo_set_text(todo, format_queue(todo_items2))
        self.play(FadeIn(todo_text2), run_time=self.STANDARD)
        self.wait(self.STANDARD)

        def neighbors8_5(r: int, c: int) -> list[tuple[int, int]]:
            out: list[tuple[int, int]] = []
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < 5 and 0 <= cc < 5 and (rr, cc) in present2:
                        out.append((rr, cc))
            return out

        step_title = Text("pop → remove → update 8 neighbors", color=WHITE).scale(0.5)
        step_title.next_to(todo, DOWN, buff=0.18)
        self.play(FadeIn(step_title, shift=DOWN), run_time=self.STANDARD)

        # Walk several pops, slowly enough to see the 4→3 enqueue.
        for step_idx in range(7):
            if not todo_items2:
                break

            cur = todo_items2.pop(0)
            r, c = cur
            self.play(Transform(todo_text2, self.todo_set_text(todo, format_queue(todo_items2))), run_time=self.FAST)

            if not present2.get((r, c), False):
                skip = Text("present? no → skip", color=self.COLOR_TEXT).scale(0.42)
                skip.next_to(step_title, DOWN, buff=0.12)
                self.play(FadeIn(skip), run_time=self.FAST)
                self.play(FadeOut(skip), run_time=self.FAST)
                continue

            popped = Text(f"pop {cur}", color=self.COLOR_TODO).scale(0.48)
            popped.next_to(step_title, DOWN, buff=0.12)
            hi = SurroundingRectangle(toy_pos[(r, c)], color=self.COLOR_TODO, buff=0.06)
            self.play(Create(hi), FadeIn(popped, shift=DOWN), run_time=self.STANDARD)

            self.play(toy_pos[(r, c)].animate.set_fill(self.COLOR_EMPTY, opacity=0.12), FadeOut(hi), run_time=self.STANDARD)
            present2[(r, c)] = False
            removed_total += 1
            self.play(
                Transform(p2[2], Text(str(removed_total), color=WHITE).scale(0.6).move_to(p2[2])),
                FadeOut(popped),
                run_time=self.STANDARD,
            )

            # Update neighbors and enqueue on 4→3.
            for nr, nc in neighbors8_5(r, c):
                if not present2.get((nr, nc), False):
                    continue
                old = counts2[(nr, nc)]
                counts2[(nr, nc)] = max(0, old - 1)
                self.play(
                    Flash(toy_pos[(nr, nc)], color=YELLOW, flash_radius=0.28),
                    Transform(
                        count_labels2[(nr, nc)],
                        Text(str(counts2[(nr, nc)]), color=WHITE).scale(0.33).move_to(count_labels2[(nr, nc)]),
                    ),
                    run_time=0.75,
                )
                if old == 4:
                    todo_items2.append((nr, nc))
                    note = Text("4→3: enqueue", color=self.COLOR_TODO).scale(0.38)
                    note.next_to(toy_pos[(nr, nc)], UP, buff=0.18)
                    self.play(FadeIn(note), run_time=self.FAST)
                    self.play(Transform(todo_text2, self.todo_set_text(todo, format_queue(todo_items2))), run_time=self.STANDARD)
                    self.play(FadeOut(note), run_time=self.FAST)

            # Intentionally demonstrate duplicate work entries once.
            if step_idx == 2 and locked:
                dup = locked[0]
                todo_items2.insert(0, dup)
                dup_note = Text("(duplicates can happen; we just check present)", color=self.COLOR_TEXT).scale(0.42)
                dup_note.next_to(step_title, DOWN, buff=0.12)
                self.play(
                    Transform(todo_text2, self.todo_set_text(todo, format_queue(todo_items2))),
                    FadeIn(dup_note, shift=DOWN),
                    run_time=self.STANDARD,
                )
                self.play(FadeOut(dup_note), run_time=self.STANDARD)

            self.wait(0.25)

        self.play(
            FadeOut(step_title),
            FadeOut(todo_text2),
            FadeOut(locked_rects),
            FadeOut(locked_lbl),
            FadeOut(toy_grid),
            *[FadeOut(t) for t in count_labels2.values()],
            FadeOut(toy_note),
            run_time=self.STANDARD,
        )

        self.wait(self.LONG)

    def scene_correctness(self) -> None:
        title = Text("Why the queue trick is correct", color=WHITE).scale(0.8).to_edge(UP)
        self.play(FadeIn(title), run_time=self.STANDARD)

        card = RoundedRectangle(width=11.0, height=5.8, corner_radius=0.25, color=self.COLOR_TEXT)
        card.shift(DOWN * 0.2)
        bullets = VGroup(
            Text("Invariant: when a roll becomes <4, it must be a neighbor of a removed roll", color=WHITE).scale(0.48),
            Text("We enqueue exactly on the first moment it can change: 4 → 3", color=self.COLOR_TODO).scale(0.48),
            Text("Duplicates are harmless: on pop, check if it's still present", color=WHITE).scale(0.48),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        bullets.move_to(card.get_center())
        self.play(Create(card), FadeIn(bullets, shift=UP), run_time=self.STANDARD)
        self.wait(self.HOLD)

    def scene_fpga_option_a_dense(self) -> None:
        title = Text("FPGA Option A: dense stencil passes", color=WHITE).scale(0.8).to_edge(UP)
        self.play(FadeIn(title), run_time=self.STANDARD)

        stencil = RoundedRectangle(width=3.3, height=2.4, corner_radius=0.2, color=BLUE_C)
        stencil.to_edge(LEFT, buff=0.8).shift(UP * 0.8)
        stencil_lbl = Text("3×3 window\n+ popcount", color=BLUE_C).scale(0.45)
        stencil_lbl.move_to(stencil)

        buf_a = RoundedRectangle(width=3.2, height=1.0, corner_radius=0.2, color=PURPLE_C)
        buf_b = RoundedRectangle(width=3.2, height=1.0, corner_radius=0.2, color=PURPLE_C)
        bufs = VGroup(buf_a, buf_b).arrange(DOWN, buff=0.25)
        bufs.move_to(ORIGIN + RIGHT * 1.8 + UP * 0.6)
        bufs_lbl = Text("Grid A / Grid B\n(ping-pong)", color=PURPLE_C).scale(0.45)
        bufs_lbl.next_to(bufs, UP, buff=0.25)

        loop = RoundedRectangle(width=5.0, height=1.2, corner_radius=0.2, color=ORANGE)
        loop.to_edge(DOWN, buff=0.7)
        loop_lbl = Text("repeat full-frame until\nno changes", color=ORANGE).scale(0.45)
        loop_lbl.move_to(loop)

        a1 = Arrow(stencil.get_right(), bufs.get_left(), buff=0.15)
        a2 = Arrow(bufs.get_bottom(), loop.get_top(), buff=0.15)
        a3 = Arrow(loop.get_left(), stencil.get_bottom(), buff=0.2)

        self.play(Create(stencil), Write(stencil_lbl), run_time=self.STANDARD)
        self.play(Create(bufs), Write(bufs_lbl), Create(a1), run_time=self.STANDARD)
        self.play(Create(loop), Write(loop_lbl), Create(a2), Create(a3), run_time=self.STANDARD)

        notes = VGroup(
            Text("Pros: extremely regular + parallel", color=self.COLOR_GOOD).scale(0.48),
            Text("Cons: may take many passes if the cascade is long", color=self.COLOR_HIGHLIGHT).scale(0.48),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        notes.to_edge(RIGHT, buff=0.8).shift(UP * 0.6)
        self.play(FadeIn(notes, shift=LEFT), run_time=self.STANDARD)
        self.wait(self.HOLD)

    def scene_fpga_option_b_queue(self) -> None:
        title = Text("FPGA Option B: event queue peeling", color=WHITE).scale(0.8).to_edge(UP)
        self.play(FadeIn(title), run_time=self.STANDARD)

        count_bram = RoundedRectangle(width=3.4, height=1.2, corner_radius=0.2, color=BLUE_C)
        count_bram.to_edge(LEFT, buff=0.8).shift(UP * 1.3)
        count_lbl = Text("count BRAM\n(8-bit)", color=BLUE_C).scale(0.45)
        count_lbl.move_to(count_bram)

        present_bram = RoundedRectangle(width=3.4, height=1.2, corner_radius=0.2, color=TEAL_C)
        present_bram.next_to(count_bram, DOWN, buff=0.35)
        present_lbl = Text("present bit\n(1-bit)", color=TEAL_C).scale(0.45)
        present_lbl.move_to(present_bram)

        fifo = RoundedRectangle(width=3.0, height=2.0, corner_radius=0.2, color=self.COLOR_TODO)
        fifo.move_to(ORIGIN + LEFT * 0.2 + UP * 0.8)
        fifo_lbl = Text("FIFO\n(todo)", color=self.COLOR_TODO).scale(0.5)
        fifo_lbl.move_to(fifo)

        micro = RoundedRectangle(width=5.0, height=3.0, corner_radius=0.2, color=ORANGE)
        micro.to_edge(RIGHT, buff=0.8).shift(UP * 0.6)
        micro_lbl = Text("8-neighbor update\n(micro-sequence)", color=ORANGE).scale(0.5)
        micro_lbl.next_to(micro.get_top(), DOWN, buff=0.25)
        steps = VGroup(*[
            Rectangle(width=4.4, height=0.25, color=ORANGE, fill_opacity=0.08)
            for _ in range(8)
        ]).arrange(DOWN, buff=0.08)
        steps.move_to(micro.get_center() + DOWN * 0.2)

        a1 = Arrow(fifo.get_right(), micro.get_left(), buff=0.15)
        a2 = Arrow(count_bram.get_right(), micro.get_left(), buff=0.15)
        a3 = Arrow(present_bram.get_right(), micro.get_left(), buff=0.15)

        self.play(Create(count_bram), Write(count_lbl), run_time=self.STANDARD)
        self.play(Create(present_bram), Write(present_lbl), run_time=self.STANDARD)
        self.play(Create(fifo), Write(fifo_lbl), run_time=self.STANDARD)
        self.play(Create(micro), Write(micro_lbl), Create(steps), Create(a1), Create(a2), Create(a3), run_time=self.STANDARD)
        self.wait(self.STANDARD)

        # Light the micro-sequence steps.
        for i in range(8):
            self.play(steps[i].animate.set_fill(ORANGE, opacity=0.25), run_time=0.55)
            self.play(steps[i].animate.set_fill(ORANGE, opacity=0.08), run_time=0.35)

        dup = Text("Duplicates ok: on pop check present==1", color=WHITE).scale(0.48)
        dup.to_edge(DOWN)
        self.play(Write(dup), run_time=self.STANDARD)
        self.wait(self.HOLD)

    def scene_fpga_option_c_hybrid(self) -> None:
        title = Text("FPGA Option C: hybrid", color=WHITE).scale(0.8).to_edge(UP)
        self.play(FadeIn(title), run_time=self.STANDARD)

        timeline = RoundedRectangle(width=10.6, height=2.0, corner_radius=0.25, color=WHITE)
        timeline.shift(UP * 0.6)
        left = Rectangle(width=5.0, height=1.2, color=BLUE_C, fill_opacity=0.1)
        right = Rectangle(width=5.0, height=1.2, color=self.COLOR_TODO, fill_opacity=0.1)
        halves = VGroup(left, right).arrange(RIGHT, buff=0.3)
        halves.move_to(timeline.get_center())
        left_lbl = Text("Phase A\n2 dense passes", color=BLUE_C).scale(0.5).move_to(left)
        right_lbl = Text("Phase B\nqueue peeling", color=self.COLOR_TODO).scale(0.5).move_to(right)

        self.play(Create(timeline), FadeIn(halves), Write(left_lbl), run_time=self.STANDARD)
        self.play(Write(right_lbl), run_time=self.STANDARD)

        trade = VGroup(
            Text("Idea: remove the big obvious frontier fast", color=WHITE).scale(0.48),
            Text("Then switch to queue when sparse", color=WHITE).scale(0.48),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        trade.next_to(timeline, DOWN, buff=0.5)
        self.play(FadeIn(trade, shift=UP), run_time=self.STANDARD)
        self.wait(self.HOLD)

    def scene_hardcaml_highlight(self) -> None:
        title = Text("HardCaml highlight: stencils are natural", color=WHITE).scale(0.8).to_edge(UP)
        self.play(FadeIn(title), run_time=self.STANDARD)

        code = VGroup(
            Text("window = 3x3 bits", font="Monospace", color=WHITE).scale(0.38),
            Text("neighbors = popcount(window) - center", font="Monospace", color=WHITE).scale(0.38),
            Text("survives = center & (neighbors >= 4)", font="Monospace", color=WHITE).scale(0.38),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        box = SurroundingRectangle(code, color=self.COLOR_TEXT, buff=0.25)
        code_block = VGroup(box, code)
        code_block.to_edge(LEFT, buff=0.9).shift(UP * 0.2)

        diagram = VGroup(
            RoundedRectangle(width=3.1, height=1.1, corner_radius=0.2, color=BLUE_C),
            RoundedRectangle(width=3.1, height=1.1, corner_radius=0.2, color=YELLOW_C),
            RoundedRectangle(width=3.1, height=1.1, corner_radius=0.2, color=GREEN_C),
        ).arrange(DOWN, buff=0.35)
        diagram.to_edge(RIGHT, buff=0.9)
        diagram_labels = VGroup(
            Text("window", color=BLUE_C).scale(0.5).move_to(diagram[0]),
            Text("popcount", color=YELLOW_C).scale(0.5).move_to(diagram[1]),
            Text("threshold", color=GREEN_C).scale(0.5).move_to(diagram[2]),
        )

        arrows = VGroup(
            Arrow(diagram[0].get_bottom(), diagram[1].get_top(), buff=0.1),
            Arrow(diagram[1].get_bottom(), diagram[2].get_top(), buff=0.1),
        )

        self.play(FadeIn(code_block, shift=RIGHT), run_time=self.STANDARD)
        self.play(Create(diagram), FadeIn(diagram_labels), Create(arrows), run_time=self.STANDARD)

        for i in range(3):
            self.play(Indicate(code[i], color=YELLOW), Indicate(diagram[i], color=YELLOW), run_time=1.6)
        self.wait(self.HOLD)

    def scene_takeaway(self) -> None:
        title = Text("Takeaway", color=WHITE).scale(0.9).to_edge(UP)
        self.play(FadeIn(title), run_time=self.STANDARD)

        stamp = Text("ONLY NEIGHBORS MATTER", color=self.COLOR_HIGHLIGHT).scale(1.0)
        stamp.move_to(ORIGIN)
        stamp_box = SurroundingRectangle(stamp, color=self.COLOR_HIGHLIGHT, buff=0.25)
        self.play(Create(stamp_box), Write(stamp), run_time=self.STANDARD)

        note = Text(
            "We avoid rescanning the whole grid\nby updating counts locally.",
            color=self.COLOR_TEXT,
        ).scale(0.55)
        note.next_to(stamp_box, DOWN, buff=0.6)
        self.play(FadeIn(note, shift=UP), run_time=self.STANDARD)
        self.wait(self.HOLD)
