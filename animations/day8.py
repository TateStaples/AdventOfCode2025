"""animations/day8.py

Day 8 — Playground (3D DSU + Sorted Edges)

Storyboard: animations/day_by_day_video_scripts.md (Day 8)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
from manim import *


@dataclass(frozen=True)
class NodeViz:
    group: VGroup
    dot: Dot
    label: Text


class Day8(Scene):
    # Timing
    FAST = 0.25
    STANDARD = 0.7
    LONG = 1.3
    HOLD = 30.25

    # Colors
    COLOR_TEXT = GRAY_E
    COLOR_DIM = GRAY_C
    COLOR_EDGE = ORANGE
    COLOR_NODE = BLUE_C
    COLOR_COMP = GREEN_C
    COLOR_MEM = PURPLE_C
    COLOR_ACC = BLUE_D

    # Scales
    SCALE_TITLE = 0.8
    SCALE_SUB = 0.55
    SCALE_TEXT = 0.5
    SCALE_SMALL = 0.42
    SCALE_TINY = 0.34
    SCALE_CODE = 0.34

    def construct(self) -> None:
        self.scene_hook()
        self.clear()
        self.scene_distance_formula()
        self.clear()
        self.scene_bottleneck_pairs()
        self.clear()
        self.scene_bucketing()
        self.clear()
        self.scene_dsu_refresher()
        self.clear()
        self.scene_part1_vs_part2()
        self.clear()
        self.scene_fpga_option_a_pipeline()
        self.clear()
        self.scene_dsu_engine_internals()
        self.clear()
        self.scene_option_b_topk()
        self.clear()
        self.scene_option_c_voxels()
        self.clear()
        self.scene_takeaway()

    # Helpers -----------------------------------------------------------------
    def make_code_block(self, lines: List[str]) -> VGroup:
        text = VGroup(
            *[Text(line, font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_CODE) for line in lines]
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        box = SurroundingRectangle(text, color=self.COLOR_DIM, buff=0.18)
        return VGroup(box, text)

    def make_node(self, label: str, pos: np.ndarray, z: float = 0.0) -> NodeViz:
        # Fake 2.5D: z controls vertical nudge and size.
        shift = UP * (0.25 * z)
        size = 0.12 + 0.02 * z
        dot = Dot(point=pos + shift, radius=size, color=self.COLOR_NODE)
        dot.set_fill(self.COLOR_NODE, opacity=0.9)
        txt = Text(label, font="Monospace", color=WHITE).scale(self.SCALE_TINY)
        txt.next_to(dot, DOWN, buff=0.08)
        return NodeViz(group=VGroup(dot, txt), dot=dot, label=txt)

    def recolor_component(self, nodes: Dict[int, NodeViz], idxs: List[int], color: ManimColor) -> Animation:
        return AnimationGroup(*[nodes[i].dot.animate.set_color(color) for i in idxs], lag_ratio=0.0)

    def make_pipeline(self, names: List[str]) -> VGroup:
        blocks = VGroup()
        for name in names:
            box = RoundedRectangle(width=2.2, height=1.1, corner_radius=0.18, color=self.COLOR_DIM)
            box.set_fill(self.COLOR_DIM, opacity=0.06)
            lbl = Text(name, color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
            lbl.move_to(box)
            blocks.add(VGroup(box, lbl))
        blocks.arrange(RIGHT, buff=0.55)
        arrows = VGroup(*[
            Arrow(blocks[i].get_right(), blocks[i + 1].get_left(), buff=0.12, color=self.COLOR_DIM)
            for i in range(len(blocks) - 1)
        ])
        return VGroup(blocks, arrows)

    # Scenes ------------------------------------------------------------------
    def scene_hook(self) -> None:
        title = Text("Day 8 — Playground", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("Connect the closest boxes", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        # Left: fake 3D scatter.
        base = LEFT * 3.2 + DOWN * 0.4
        pts = {
            0: (-2.2, 1.0, 0.5),
            1: (-1.1, 0.4, 0.2),
            2: (0.2, 1.1, 0.9),
            3: (1.3, 0.6, 0.3),
            4: (-0.3, -0.7, 0.6),
            5: (1.6, -0.6, 0.1),
        }
        nodes: Dict[int, NodeViz] = {}
        for i, (x, y, z) in pts.items():
            nodes[i] = self.make_node(str(i), base + RIGHT * x + UP * y, z=z)

        cloud = VGroup(*[n.group for n in nodes.values()])
        self.play(FadeIn(cloud, shift=UP * 0.1))

        # Right: an edge list where the smallest is highlighted.
        edge_list = VGroup(
            Text("(0,1)  d²=7", color=self.COLOR_EDGE).scale(self.SCALE_SMALL),
            Text("(2,3)  d²=9", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("(4,5)  d²=12", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        edge_list.to_edge(RIGHT).shift(UP * 0.5)
        edge_label = Text("smallest edges first", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        edge_label.next_to(edge_list, UP, buff=0.2)
        self.play(FadeIn(edge_label), FadeIn(edge_list, shift=LEFT))

        # Draw a few shortest edges and merge colors.
        def connect(u: int, v: int, comp_color: ManimColor, comp_nodes: List[int]) -> None:
            line = Line(nodes[u].dot.get_center(), nodes[v].dot.get_center(), color=self.COLOR_EDGE)
            self.play(Create(line), run_time=self.STANDARD)
            self.play(self.recolor_component(nodes, comp_nodes, comp_color), run_time=self.STANDARD)

        connect(0, 1, GREEN_C, [0, 1])
        connect(2, 3, TEAL_C, [2, 3])
        connect(1, 2, YELLOW_C, [0, 1, 2, 3])
        self.wait(self.HOLD)

    def scene_distance_formula(self) -> None:
        title = Text("Squared distance is enough", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("compare d², skip sqrt", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        p1 = Dot(LEFT * 3.2 + UP * 0.5, color=self.COLOR_NODE)
        p2 = Dot(LEFT * 1.6 + DOWN * 0.8, color=self.COLOR_NODE)
        self.play(FadeIn(p1), FadeIn(p2))
        seg = Line(p1.get_center(), p2.get_center(), color=self.COLOR_EDGE)
        self.play(Create(seg), run_time=self.STANDARD)

        dx = Brace(seg.copy().set_points_as_corners([p1.get_center(), np.array([p2.get_x(), p1.get_y(), 0])]), DOWN)
        dy = Brace(seg.copy().set_points_as_corners([np.array([p2.get_x(), p1.get_y(), 0]), p2.get_center()]), RIGHT)
        dx_t = Text("dx", color=self.COLOR_TEXT).scale(self.SCALE_SMALL).next_to(dx, DOWN, buff=0.05)
        dy_t = Text("dy", color=self.COLOR_TEXT).scale(self.SCALE_SMALL).next_to(dy, RIGHT, buff=0.05)
        self.play(GrowFromCenter(dx), FadeIn(dx_t), GrowFromCenter(dy), FadeIn(dy_t), run_time=self.STANDARD)

        formula = VGroup(
            Text(r"d^2 = dx^2 + dy^2 + dz^2", color=self.COLOR_TEXT).scale(self.SCALE_TEXT),
            Text(r"(no square root needed)", color=self.COLOR_DIM).scale(self.SCALE_SMALL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        formula.to_edge(RIGHT).shift(UP * 0.2)
        self.play(FadeIn(formula, shift=LEFT), run_time=self.STANDARD)
        self.wait(self.HOLD)

    def scene_bottleneck_pairs(self) -> None:
        title = Text("The bottleneck: N² pairs", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("pair generation + sorting dominates", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        n_points = 9
        points = VGroup(*[
            Dot(color=self.COLOR_NODE).scale(0.8)
            for _ in range(n_points)
        ])
        points.arrange_in_grid(rows=3, buff=0.7)
        points.shift(LEFT * 3.0)
        self.play(FadeIn(points, shift=UP * 0.1), run_time=self.STANDARD)

        pairs_text = Text(r"pairs = N(N-1)/2", color=self.COLOR_ACC).scale(self.SCALE_TEXT)
        pairs_text.to_edge(RIGHT).shift(UP * 0.6)
        warn = Text("too many to sort globally", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        warn.next_to(pairs_text, DOWN, buff=0.25)
        self.play(Write(pairs_text), FadeIn(warn, shift=DOWN * 0.1), run_time=self.STANDARD)

        # Quick "explosion" of pair lines.
        lines = VGroup()
        idxs = list(range(n_points))
        for a in idxs[:5]:
            for b in idxs[a + 1 : a + 4]:
                lines.add(Line(points[a].get_center(), points[b].get_center(), color=self.COLOR_DIM, stroke_width=2))
        self.play(LaggedStart(*[Create(l) for l in lines], lag_ratio=0.03), run_time=self.LONG)
        self.play(lines.animate.set_opacity(0.2), run_time=self.STANDARD)
        self.wait(self.HOLD)

    def scene_bucketing(self) -> None:
        title = Text("Bucket distances, then sort locally", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("stream buckets low → high", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        # Left: histogram buckets.
        bars = VGroup()
        heights = [0.8, 1.2, 0.6, 1.6, 0.9]
        for h in heights:
            r = Rectangle(width=0.6, height=h, color=self.COLOR_ACC)
            r.set_fill(self.COLOR_ACC, opacity=0.15)
            bars.add(r)
        bars.arrange(RIGHT, buff=0.25)
        bars.to_edge(LEFT).shift(RIGHT * 1.2 + DOWN * 0.2)
        axis = Line(bars.get_left() + DOWN * 0.6, bars.get_right() + DOWN * 0.6, color=self.COLOR_DIM)
        self.play(FadeIn(bars), Create(axis), run_time=self.STANDARD)

        # Right: per-bucket sorted list.
        list_box = RoundedRectangle(width=4.9, height=3.6, corner_radius=0.18, color=self.COLOR_DIM)
        list_box.set_fill(self.COLOR_DIM, opacity=0.05)
        list_box.to_edge(RIGHT).shift(DOWN * 0.15)
        list_title = Text("bucket b: sorted by d²", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        list_title.next_to(list_box, UP, buff=0.2)
        items = VGroup(
            Text("(u,v,d²=7)", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("(u,v,d²=9)", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("(u,v,d²=12)", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        items.move_to(list_box)

        self.play(FadeIn(list_box), FadeIn(list_title), FadeIn(items, shift=LEFT), run_time=self.STANDARD)

        # Tokens "fall" into buckets.
        tokens = VGroup(*[Dot(color=self.COLOR_EDGE).scale(0.8) for _ in range(7)])
        for i, t in enumerate(tokens):
            t.move_to(bars[i % len(bars)].get_top() + UP * 1.2 + RIGHT * 0.1)
        self.play(LaggedStart(*[FadeIn(t) for t in tokens], lag_ratio=0.06), run_time=self.STANDARD)
        self.play(
            LaggedStart(
                *[
                    t.animate.move_to(bars[i % len(bars)].get_top() + DOWN * 0.2)
                    for i, t in enumerate(tokens)
                ],
                lag_ratio=0.06,
            ),
            run_time=self.LONG,
        )

        drain = Arrow(bars.get_left() + DOWN * 1.0, bars.get_right() + DOWN * 1.0, buff=0.1, color=self.COLOR_TEXT)
        drain_lbl = Text("drain buckets in order", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        drain_lbl.next_to(drain, DOWN, buff=0.2)
        self.play(Create(drain), FadeIn(drain_lbl), run_time=self.STANDARD)
        self.wait(self.HOLD)

    def scene_dsu_refresher(self) -> None:
        title = Text("DSU refresher", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("parent[] + size[], find/union", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        # Forest diagram.
        root = Dot(LEFT * 3.3 + UP * 0.8, color=self.COLOR_COMP)
        a = Dot(LEFT * 4.4 + DOWN * 0.2, color=self.COLOR_NODE)
        b = Dot(LEFT * 3.3 + DOWN * 0.2, color=self.COLOR_NODE)
        c = Dot(LEFT * 2.2 + DOWN * 0.2, color=self.COLOR_NODE)
        lines = VGroup(
            Line(a.get_center(), root.get_center(), color=self.COLOR_DIM),
            Line(b.get_center(), root.get_center(), color=self.COLOR_DIM),
            Line(c.get_center(), root.get_center(), color=self.COLOR_DIM),
        )
        self.play(FadeIn(root), FadeIn(a), FadeIn(b), FadeIn(c), Create(lines), run_time=self.STANDARD)

        parent_arr = VGroup(
            Text("parent:", color=self.COLOR_MEM).scale(self.SCALE_SMALL),
            Text("[0,0,0,3,4,5,…]", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        size_arr = VGroup(
            Text("size:", color=self.COLOR_MEM).scale(self.SCALE_SMALL),
            Text("[4,1,1,1,1,1,…]", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        panel = VGroup(parent_arr, size_arr).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        panel.to_edge(RIGHT).shift(DOWN * 0.2)
        self.play(FadeIn(panel, shift=LEFT), run_time=self.STANDARD)

        # Path compression hint.
        path = VGroup(
            Dot(LEFT * 0.6 + DOWN * 0.1, color=self.COLOR_NODE),
            Dot(RIGHT * 0.2 + UP * 0.5, color=self.COLOR_NODE),
            Dot(RIGHT * 1.0 + UP * 1.1, color=self.COLOR_COMP),
        )
        chain = VGroup(
            Arrow(path[0].get_center(), path[1].get_center(), buff=0.05, color=self.COLOR_DIM),
            Arrow(path[1].get_center(), path[2].get_center(), buff=0.05, color=self.COLOR_DIM),
        )
        hint = Text("find(): follow pointers, then compress", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        hint.next_to(path, DOWN, buff=0.2)
        grp = VGroup(path, chain, hint).shift(RIGHT * 0.7 + DOWN * 1.6)
        self.play(FadeIn(grp, shift=UP * 0.2), run_time=self.STANDARD)
        self.play(chain[0].animate.set_color(self.COLOR_ACC), chain[1].animate.set_color(self.COLOR_ACC), run_time=self.FAST)
        short = Arrow(path[0].get_center(), path[2].get_center(), buff=0.05, color=self.COLOR_ACC)
        self.play(Transform(chain, VGroup(short)), run_time=self.STANDARD)
        self.wait(self.HOLD)

    def scene_part1_vs_part2(self) -> None:
        title = Text("Part 1 vs Part 2 milestones", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("1000 edges vs connected", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        milestone = RoundedRectangle(width=6.8, height=3.6, corner_radius=0.2, color=self.COLOR_DIM)
        milestone.set_fill(self.COLOR_DIM, opacity=0.05)
        milestone.to_edge(RIGHT).shift(DOWN * 0.2)
        p1 = Text("Part 1: after 1000 edges\nproduct of top 3 sizes", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        p2 = Text("Part 2: stop when components=1\noutput x[i]*x[j]", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        rows = VGroup(p1, p2).arrange(DOWN, aligned_edge=LEFT, buff=0.55)
        rows.move_to(milestone)
        self.play(FadeIn(milestone), FadeIn(rows, shift=LEFT), run_time=self.STANDARD)

        counter_box = RoundedRectangle(width=3.2, height=1.1, corner_radius=0.16, color=self.COLOR_ACC)
        counter_box.set_fill(self.COLOR_ACC, opacity=0.06)
        counter_box.to_edge(LEFT).shift(RIGHT * 1.2 + UP * 0.2)
        counter_lbl = Text("edges processed", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        counter_val = Text("0", font="Monospace", color=self.COLOR_ACC).scale(self.SCALE_TEXT)
        VGroup(counter_lbl, counter_val).arrange(DOWN, buff=0.1).move_to(counter_box)
        self.play(FadeIn(counter_box), FadeIn(counter_lbl), FadeIn(counter_val), run_time=self.STANDARD)

        # Tick quickly to 1000 (illustrative).
        self.play(Transform(counter_val, Text("1000", font="Monospace", color=self.COLOR_ACC).scale(self.SCALE_TEXT).move_to(counter_val)), run_time=self.STANDARD)
        snap = Text("snapshot: sizes → top3 product", color=self.COLOR_COMP).scale(self.SCALE_SMALL)
        snap.next_to(counter_box, DOWN, buff=0.25)
        self.play(FadeIn(snap, shift=DOWN * 0.1), run_time=self.STANDARD)
        self.play(Transform(counter_val, Text("…", font="Monospace", color=self.COLOR_ACC).scale(self.SCALE_TEXT).move_to(counter_val)), run_time=self.FAST)
        self.play(Transform(counter_val, Text("connected", font="Monospace", color=self.COLOR_ACC).scale(self.SCALE_SMALL).move_to(counter_val)), run_time=self.STANDARD)
        out = Text("part2 = x[i]·x[j]", color=self.COLOR_ACC).scale(self.SCALE_SMALL)
        out.next_to(snap, DOWN, buff=0.2)
        self.play(FadeIn(out, shift=DOWN * 0.1), run_time=self.STANDARD)
        self.wait(self.HOLD)

    def scene_fpga_option_a_pipeline(self) -> None:
        title = Text("FPGA Option A: bucket + sort + DSU", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("a pragmatic end-to-end pipeline", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        pipe = self.make_pipeline([
            "Point\nStore",
            "Pair\nGen",
            "Bucketer",
            "Per-Bucket\nSort",
            "Edge\nStream",
            "DSU",
        ])
        pipe.scale(0.9)
        pipe.move_to(ORIGIN)
        self.play(FadeIn(pipe, shift=UP * 0.1), run_time=self.STANDARD)

        ra = Text("DSU needs random access", color=self.COLOR_ACC).scale(self.SCALE_SMALL)
        ra.next_to(pipe[0][-1], DOWN, buff=0.25)  # last block group
        self.play(FadeIn(ra, shift=DOWN * 0.1), run_time=self.STANDARD)

        token = Dot(color=self.COLOR_EDGE).scale(1.0)
        token.move_to(pipe[0][0][0].get_left() + LEFT * 0.2)
        self.play(FadeIn(token), run_time=self.FAST)
        for blk in pipe[0]:
            self.play(token.animate.move_to(blk.get_center()), run_time=self.FAST)
        self.play(FadeOut(token), run_time=self.FAST)
        self.wait(self.HOLD)

    def scene_dsu_engine_internals(self) -> None:
        title = Text("DSU engine internals", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("pointer chasing + writeback", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        # FSM sketch.
        fsm = VGroup(
            RoundedRectangle(width=2.6, height=0.9, corner_radius=0.15, color=self.COLOR_DIM),
            RoundedRectangle(width=2.6, height=0.9, corner_radius=0.15, color=self.COLOR_DIM),
            RoundedRectangle(width=2.6, height=0.9, corner_radius=0.15, color=self.COLOR_DIM),
        ).arrange(DOWN, buff=0.35)
        for b in fsm:
            b.set_fill(self.COLOR_DIM, opacity=0.06)
        fsm.to_edge(LEFT).shift(RIGHT * 1.2 + DOWN * 0.3)
        labels = VGroup(
            Text("FIND u", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("FIND v", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("UNION", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
        )
        for i in range(3):
            labels[i].move_to(fsm[i])

        ram = RoundedRectangle(width=4.6, height=2.8, corner_radius=0.2, color=self.COLOR_MEM)
        ram.set_fill(self.COLOR_MEM, opacity=0.06)
        ram.to_edge(RIGHT).shift(DOWN * 0.25)
        ram_lbl = Text("parent[] / size[] RAM\n(dual-port)", color=self.COLOR_MEM).scale(self.SCALE_SMALL)
        ram_lbl.move_to(ram)
        port_a = Text("A", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL).next_to(ram.get_left(), RIGHT, buff=0.2).shift(UP * 0.7)
        port_b = Text("B", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL).next_to(ram.get_left(), RIGHT, buff=0.2).shift(DOWN * 0.7)

        self.play(FadeIn(fsm), FadeIn(labels), FadeIn(ram), FadeIn(ram_lbl), FadeIn(port_a), FadeIn(port_b), run_time=self.STANDARD)

        chain = VGroup(
            Text("u → parent[u] → parent[parent[u]] → …", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("(several RAM reads)", color=self.COLOR_DIM).scale(self.SCALE_SMALL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        chain.to_edge(DOWN)
        self.play(FadeIn(chain, shift=UP), run_time=self.STANDARD)

        pulse = SurroundingRectangle(ram, color=self.COLOR_ACC, buff=0.08)
        self.play(Create(pulse), FadeOut(pulse), run_time=self.FAST)
        self.play(fsm[0].animate.set_stroke(self.COLOR_ACC, width=4), run_time=self.FAST)
        self.play(fsm[1].animate.set_stroke(self.COLOR_ACC, width=4), run_time=self.FAST)
        self.play(fsm[2].animate.set_stroke(self.COLOR_ACC, width=4), run_time=self.FAST)
        self.wait(self.HOLD)

    def scene_option_b_topk(self) -> None:
        title = Text("Option B: keep only the top-K smallest", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("great for Part 1, still computes all pairs", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        stream = VGroup(
            Text("edge d²=40", font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("edge d²=9", font="Monospace", color=self.COLOR_EDGE).scale(self.SCALE_SMALL),
            Text("edge d²=12", font="Monospace", color=self.COLOR_EDGE).scale(self.SCALE_SMALL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        stream.to_edge(LEFT).shift(RIGHT * 1.0)
        gate = RoundedRectangle(width=2.4, height=1.2, corner_radius=0.18, color=self.COLOR_DIM)
        gate.set_fill(self.COLOR_DIM, opacity=0.06)
        gate_lbl = Text("keep K", color=self.COLOR_TEXT).scale(self.SCALE_SMALL).move_to(gate)
        gate_group = VGroup(gate, gate_lbl)
        gate_group.next_to(stream, RIGHT, buff=0.8)

        heap = VGroup(
            RoundedRectangle(width=3.2, height=3.0, corner_radius=0.18, color=self.COLOR_ACC),
            Text("max-heap\n(size K)", color=self.COLOR_ACC).scale(self.SCALE_SMALL),
        )
        heap[0].set_fill(self.COLOR_ACC, opacity=0.06)
        heap[1].move_to(heap[0])
        heap.next_to(gate_group, RIGHT, buff=0.8)

        self.play(FadeIn(stream, shift=RIGHT), FadeIn(gate_group), FadeIn(heap, shift=LEFT), run_time=self.STANDARD)
        beat = Text("if d² < heap.max: replace", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        beat.to_edge(DOWN)
        self.play(Write(beat), run_time=self.STANDARD)
        self.wait(self.HOLD)

    def scene_option_c_voxels(self) -> None:
        title = Text("Option C: spatial partitioning", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("try nearby voxels first", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        grid = NumberPlane(
            x_range=[-4, 4, 1],
            y_range=[-2.5, 2.5, 1],
            background_line_style={"stroke_color": self.COLOR_DIM, "stroke_width": 1, "stroke_opacity": 0.35},
        )
        grid.fade(0.2)
        self.play(FadeIn(grid), run_time=self.STANDARD)

        cell = SurroundingRectangle(Square(1.0).move_to(LEFT * 1.5 + UP * 0.5), color=self.COLOR_ACC, buff=0)
        ring1 = SurroundingRectangle(Square(3.0).move_to(cell.get_center()), color=self.COLOR_ACC, buff=0)
        ring2 = SurroundingRectangle(Square(5.0).move_to(cell.get_center()), color=self.COLOR_ACC, buff=0)
        lbl = Text("expand radius", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        lbl.to_edge(DOWN)
        self.play(Create(cell), FadeIn(lbl, shift=UP * 0.1), run_time=self.STANDARD)
        self.play(Transform(cell, ring1), run_time=self.STANDARD)
        self.play(Transform(cell, ring2), run_time=self.STANDARD)
        note = Text("may need careful expansion for correctness", color=self.COLOR_DIM).scale(self.SCALE_SMALL)
        note.next_to(lbl, UP, buff=0.2)
        self.play(FadeIn(note, shift=DOWN * 0.1), run_time=self.STANDARD)
        self.wait(self.HOLD)

    def scene_takeaway(self) -> None:
        title = Text("Takeaway", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        subtitle = Text("The whole puzzle is engineering the edge stream", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))

        icons = VGroup(
            RoundedRectangle(width=2.3, height=1.2, corner_radius=0.18, color=self.COLOR_DIM),
            RoundedRectangle(width=2.3, height=1.2, corner_radius=0.18, color=self.COLOR_DIM),
            RoundedRectangle(width=2.3, height=1.2, corner_radius=0.18, color=self.COLOR_DIM),
        ).arrange(RIGHT, buff=0.65)
        for b in icons:
            b.set_fill(self.COLOR_DIM, opacity=0.06)
        labels = VGroup(
            Text("pairs", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("stream", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("DSU", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
        )
        for i in range(3):
            labels[i].move_to(icons[i])
        row = VGroup(icons, labels)
        row.move_to(ORIGIN)

        arr1 = Arrow(icons[0].get_right(), icons[1].get_left(), buff=0.1, color=self.COLOR_DIM)
        arr2 = Arrow(icons[1].get_right(), icons[2].get_left(), buff=0.1, color=self.COLOR_DIM)
        self.play(FadeIn(icons), FadeIn(labels), Create(arr1), Create(arr2), run_time=self.STANDARD)
        end = Text("Huge data → structured pipeline", color=self.COLOR_TEXT).scale(self.SCALE_TEXT)
        end.to_edge(DOWN)
        self.play(Write(end), run_time=self.STANDARD)
        self.wait(self.HOLD)
