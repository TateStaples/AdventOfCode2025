"""animations/day11.py

Day 11 — Reactor (Path Counts in a Directed Graph)

Storyboard: animations/day_by_day_video_scripts.md (Day 11)
"""

from __future__ import annotations

from typing import List

from manim import *


class Day11(Scene):
    # Timing
    FAST = 0.25
    STANDARD = 0.7
    LONG = 1.3
    HOLD = 38.0

    # Colors
    COLOR_TEXT = GRAY_E
    COLOR_DIM = GRAY_C
    COLOR_EDGE = GRAY_C
    COLOR_NODE = BLUE_C
    COLOR_OUT = GREEN_C
    COLOR_DAC = ORANGE
    COLOR_FFT = PINK
    COLOR_ACC = YELLOW_E

    SCALE_TITLE = 0.8
    SCALE_SUB = 0.55
    SCALE_TEXT = 0.5
    SCALE_SMALL = 0.42
    SCALE_CODE = 0.34
    SCALE_TINY = 0.33

    def construct(self) -> None:
        self.scene_hook_paths()
        self.clear()
        self.scene_memoized_dfs()
        self.clear()
        self.scene_encoding()
        self.clear()
        self.scene_part2_decomposition()
        self.clear()
        self.scene_dp_on_dag()
        self.clear()
        self.scene_fpga_ready_node_engine()
        self.clear()
        self.scene_atomic_hazards()
        self.clear()
        self.scene_vector_dp()
        self.clear()
        self.scene_toposort_reverse_dp()
        self.clear()
        self.scene_takeaway()

    # Helpers -----------------------------------------------------------------
    def make_code_block(self, lines: List[str]) -> VGroup:
        text = VGroup(
            *[Text(line, font="Monospace", color=self.COLOR_TEXT).scale(self.SCALE_CODE) for line in lines]
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        box = SurroundingRectangle(text, color=self.COLOR_DIM, buff=0.18)
        return VGroup(box, text)

    def node(self, label: str, *, color: ManimColor | None = None) -> VGroup:
        c = self.COLOR_NODE if color is None else color
        circ = Circle(radius=0.34, color=c)
        circ.set_fill(color=c, opacity=0.22)
        txt = Text(label, color=WHITE).scale(self.SCALE_TINY)
        txt.move_to(circ.get_center())
        return VGroup(circ, txt)

    def edge(self, a: VGroup, b: VGroup, *, color: ManimColor | None = None) -> Arrow:
        c = self.COLOR_EDGE if color is None else color
        return Arrow(a[0].get_center(), b[0].get_center(), buff=0.42, color=c, stroke_width=3)

    def build_example_graph(self) -> tuple[dict[str, VGroup], VGroup, VGroup]:
        you = self.node("you")
        svr = self.node("svr")
        a = self.node("aaa")
        b = self.node("bbb")
        fft = self.node("fft", color=self.COLOR_FFT)
        dac = self.node("dac", color=self.COLOR_DAC)
        out = self.node("out", color=self.COLOR_OUT)

        you.shift(LEFT * 4 + UP * 1.9)
        svr.shift(LEFT * 4 + UP * 0.1)
        a.shift(LEFT * 2 + UP * 1.8)
        b.shift(LEFT * 2 + UP * 0.2)
        fft.shift(RIGHT * 0.2 + UP * 1.8)
        dac.shift(RIGHT * 0.2 + UP * 0.2)
        out.shift(RIGHT * 2.8 + UP * 1.0)

        nodes = {"you": you, "svr": svr, "aaa": a, "bbb": b, "fft": fft, "dac": dac, "out": out}
        nodes_group = VGroup(you, svr, a, b, fft, dac, out)

        edges_group = VGroup(
            self.edge(you, a),
            self.edge(you, b),
            self.edge(svr, a),
            self.edge(svr, b),
            self.edge(a, fft),
            self.edge(b, fft),
            self.edge(a, dac),
            self.edge(b, dac),
            self.edge(fft, out),
            self.edge(dac, out),
            self.edge(fft, dac),
        )
        return nodes, nodes_group, edges_group

    def labeled_box(self, title: str, *, w: float, h: float, color: ManimColor) -> VGroup:
        box = RoundedRectangle(width=w, height=h, corner_radius=0.18, color=color)
        box.set_fill(color, opacity=0.06)
        lbl = Text(title, color=color).scale(self.SCALE_SMALL)
        lbl.move_to(box.get_top() + DOWN * 0.28)
        return VGroup(box, lbl)

    # Scene 1 -----------------------------------------------------------------
    def scene_hook_paths(self) -> None:
        title = Text("Day 11: Reactor", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        sub = Text("How many ways can data reach out?", color=self.COLOR_TEXT).scale(self.SCALE_SUB)
        sub.next_to(title, DOWN, buff=0.15)
        self.play(Write(title), run_time=self.STANDARD)
        self.play(FadeIn(sub, shift=DOWN * 0.15), run_time=self.STANDARD)

        nodes_by_name, nodes, edges = self.build_example_graph()
        graph = VGroup(edges, nodes).scale(0.95)
        self.play(FadeIn(nodes, shift=UP * 0.08), run_time=self.STANDARD)
        self.play(*[Create(e) for e in edges], run_time=self.LONG)

        badges = VGroup(
            self.labeled_box("out", w=1.2, h=0.7, color=self.COLOR_OUT),
            self.labeled_box("dac", w=1.2, h=0.7, color=self.COLOR_DAC),
            self.labeled_box("fft", w=1.2, h=0.7, color=self.COLOR_FFT),
        ).arrange(DOWN, buff=0.22)
        badges.to_edge(RIGHT).shift(UP * 0.2)
        self.play(FadeIn(badges, shift=LEFT * 0.2), run_time=self.STANDARD)

        p1 = VGroup(
            self.edge(nodes_by_name["you"], nodes_by_name["aaa"], color=self.COLOR_ACC),
            self.edge(nodes_by_name["aaa"], nodes_by_name["fft"], color=self.COLOR_ACC),
            self.edge(nodes_by_name["fft"], nodes_by_name["out"], color=self.COLOR_ACC),
        )
        p2 = VGroup(
            self.edge(nodes_by_name["you"], nodes_by_name["bbb"], color=self.COLOR_ACC),
            self.edge(nodes_by_name["bbb"], nodes_by_name["dac"], color=self.COLOR_ACC),
            self.edge(nodes_by_name["dac"], nodes_by_name["out"], color=self.COLOR_ACC),
        )
        counter = VGroup(
            Text("paths(you → out)", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            MathTex("0", color=self.COLOR_ACC).scale(0.8),
        ).arrange(RIGHT, buff=0.25)
        counter.to_edge(DOWN)
        self.play(FadeIn(counter, shift=UP * 0.2), run_time=self.STANDARD)

        for i, path in enumerate([p1, p2, p1.copy(), p2.copy()], start=1):
            self.play(*[Create(e) for e in path], run_time=self.STANDARD)
            new_num = MathTex(str(i), color=self.COLOR_ACC).scale(0.8)
            new_num.move_to(counter[1])
            self.play(Transform(counter[1], new_num), run_time=self.FAST)
            self.play(FadeOut(path), run_time=self.FAST)

        note = Text("Part 2: paths(svr → out) visiting dac and fft (any order)", color=self.COLOR_TEXT).scale(
            self.SCALE_SMALL
        )
        note.next_to(counter, UP, buff=0.2)
        self.play(FadeIn(note, shift=UP * 0.15), run_time=self.STANDARD)
        self.wait(self.HOLD)

    # Scene 2 -----------------------------------------------------------------
    def scene_memoized_dfs(self) -> None:
        title = Text("Memoized DFS (software baseline)", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        self.play(Write(title), run_time=self.STANDARD)

        recur = MathTex(r"dfs(v)=\sum_{v\to u} dfs(u)", color=self.COLOR_TEXT).scale(0.7)
        recur.to_edge(LEFT).shift(UP * 2.55)
        base = MathTex(r"dfs(\text{end})=1", color=self.COLOR_TEXT).scale(0.7)
        base.next_to(recur, DOWN, aligned_edge=LEFT)
        self.play(FadeIn(recur, shift=RIGHT * 0.2), FadeIn(base, shift=RIGHT * 0.2), run_time=self.STANDARD)

        # A tiny call tree with an explicit repeated subcall.
        root = Text("dfs(you)", color=WHITE).scale(self.SCALE_SMALL)
        c1 = Text("dfs(aaa)", color=WHITE).scale(self.SCALE_SMALL)
        c2 = Text("dfs(bbb)", color=WHITE).scale(self.SCALE_SMALL)
        g1 = Text("dfs(fft)", color=self.COLOR_FFT).scale(self.SCALE_SMALL)
        g2 = Text("dfs(dac)", color=self.COLOR_DAC).scale(self.SCALE_SMALL)
        g3 = Text("dfs(fft)", color=self.COLOR_FFT).scale(self.SCALE_SMALL)
        g4 = Text("dfs(dac)", color=self.COLOR_DAC).scale(self.SCALE_SMALL)

        root.move_to(LEFT * 4.1 + UP * 1.15)
        c1.next_to(root, DOWN, buff=0.65).shift(LEFT * 0.9)
        c2.next_to(root, DOWN, buff=0.65).shift(RIGHT * 0.9)
        g1.next_to(c1, DOWN, buff=0.55).shift(LEFT * 0.3)
        g2.next_to(c1, DOWN, buff=0.55).shift(RIGHT * 0.8)
        g3.next_to(c2, DOWN, buff=0.55).shift(LEFT * 0.8)
        g4.next_to(c2, DOWN, buff=0.55).shift(RIGHT * 0.3)

        arrows = VGroup(
            Arrow(root.get_bottom(), c1.get_top(), buff=0.12, color=self.COLOR_DIM),
            Arrow(root.get_bottom(), c2.get_top(), buff=0.12, color=self.COLOR_DIM),
            Arrow(c1.get_bottom(), g1.get_top(), buff=0.12, color=self.COLOR_DIM),
            Arrow(c1.get_bottom(), g2.get_top(), buff=0.12, color=self.COLOR_DIM),
            Arrow(c2.get_bottom(), g3.get_top(), buff=0.12, color=self.COLOR_DIM),
            Arrow(c2.get_bottom(), g4.get_top(), buff=0.12, color=self.COLOR_DIM),
        )
        tree = VGroup(root, c1, c2, g1, g2, g3, g4, arrows)

        cache_title = Text("cache", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        cache_box = RoundedRectangle(width=3.8, height=3.0, corner_radius=0.16, color=self.COLOR_DIM)
        cache_box.set_fill(self.COLOR_DIM, opacity=0.04)
        cache_title.move_to(cache_box.get_top() + DOWN * 0.28)
        rows = VGroup(
            Text("fft → ?", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("dac → ?", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("out → ?", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        rows.move_to(cache_box.get_center() + DOWN * 0.15)
        cache = VGroup(cache_box, cache_title, rows)
        cache.to_edge(RIGHT).shift(DOWN * 0.15)

        self.play(FadeIn(tree, shift=RIGHT * 0.1), run_time=self.STANDARD)
        self.play(FadeIn(cache, shift=LEFT * 0.2), run_time=self.STANDARD)

        hit = Text("cache hit", color=self.COLOR_ACC).scale(self.SCALE_SMALL)
        hit.next_to(g3, RIGHT, buff=0.25)
        x = Cross(g3, stroke_color=self.COLOR_ACC, stroke_width=5)
        self.play(FadeIn(hit, shift=LEFT * 0.1), Create(x), run_time=self.STANDARD)

        caution = Text("Works cleanly when the reachable subgraph is acyclic", color=self.COLOR_TEXT).scale(
            self.SCALE_SMALL
        )
        caution.to_edge(DOWN)
        self.play(FadeIn(caution, shift=UP * 0.15), run_time=self.STANDARD)
        self.wait(self.HOLD)

    # Scene 3 -----------------------------------------------------------------
    def scene_encoding(self) -> None:
        title = Text("Encoding 3-letter labels", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        self.play(Write(title), run_time=self.STANDARD)

        word = Text("abc", color=WHITE).scale(1.1).move_to(LEFT * 4.3 + UP * 1.2)
        step = MathTex(r"(a-\text{'a'})\cdot 26^2 + (b-\text{'a'})\cdot 26 + (c-\text{'a'})", color=self.COLOR_TEXT)
        step.scale(0.55).next_to(word, DOWN, buff=0.4).align_to(word, LEFT)
        bound = MathTex(r"26^3 = 17576", color=self.COLOR_ACC).scale(0.8)
        bound.next_to(step, DOWN, aligned_edge=LEFT, buff=0.35)

        arr = RoundedRectangle(width=6.4, height=1.2, corner_radius=0.16, color=self.COLOR_DIM)
        arr.set_fill(self.COLOR_DIM, opacity=0.04)
        arr.move_to(RIGHT * 1.55 + DOWN * 0.4)
        arr_lbl = Text("arrays indexed by 0..17575", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        arr_lbl.move_to(arr.get_center())
        idx = MathTex(r"idx(\text{" + "abc" + r"})=\;?", color=self.COLOR_ACC).scale(0.9)
        idx.next_to(arr, UP, buff=0.25)

        self.play(FadeIn(word, shift=UP * 0.15), run_time=self.STANDARD)
        self.play(FadeIn(step, shift=RIGHT * 0.2), run_time=self.STANDARD)
        self.play(FadeIn(bound, shift=RIGHT * 0.2), run_time=self.STANDARD)
        self.play(FadeIn(arr, arr_lbl, idx, shift=UP * 0.15), run_time=self.STANDARD)

        pointer = Triangle(color=self.COLOR_ACC).scale(0.2).rotate(PI)
        pointer.next_to(arr, LEFT, buff=0.15)
        self.play(FadeIn(pointer), run_time=self.FAST)
        self.play(pointer.animate.shift(RIGHT * 2.2), run_time=self.STANDARD)
        self.play(pointer.animate.shift(RIGHT * 2.2), run_time=self.STANDARD)

        note = Text("Now DP tables can just be RAMs", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        note.to_edge(DOWN)
        self.play(FadeIn(note, shift=UP * 0.15), run_time=self.STANDARD)
        self.wait(self.HOLD)

    # Scene 4 -----------------------------------------------------------------
    def scene_part2_decomposition(self) -> None:
        title = Text("Part 2: two valid orders", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        self.play(Write(title), run_time=self.STANDARD)

        def pipeline(labels: List[str], colors: List[ManimColor]) -> VGroup:
            boxes = VGroup()
            for lab, col in zip(labels, colors, strict=True):
                b = RoundedRectangle(width=1.3, height=0.75, corner_radius=0.16, color=col)
                b.set_fill(col, opacity=0.06)
                t = Text(lab, color=col).scale(self.SCALE_SMALL)
                t.move_to(b.get_center())
                boxes.add(VGroup(b, t))
            boxes.arrange(RIGHT, buff=0.35)
            arrows = VGroup(
                *[
                    Arrow(boxes[i].get_right(), boxes[i + 1].get_left(), buff=0.12, color=self.COLOR_DIM)
                    for i in range(len(boxes) - 1)
                ]
            )
            return VGroup(boxes, arrows)

        top = pipeline(["svr", "fft", "dac", "out"], [WHITE, self.COLOR_FFT, self.COLOR_DAC, self.COLOR_OUT])
        bot = pipeline(["svr", "dac", "fft", "out"], [WHITE, self.COLOR_DAC, self.COLOR_FFT, self.COLOR_OUT])
        top.move_to(ORIGIN).shift(UP * 1.2)
        bot.next_to(top, DOWN, buff=0.85)

        f1 = MathTex(
            r"paths(svr\to fft)\cdot paths(fft\to dac)\cdot paths(dac\to out)",
            color=self.COLOR_TEXT,
        ).scale(0.55)
        f1.next_to(top, DOWN, buff=0.25)
        f2 = MathTex(
            r"paths(svr\to dac)\cdot paths(dac\to fft)\cdot paths(fft\to out)",
            color=self.COLOR_TEXT,
        ).scale(0.55)
        f2.next_to(bot, DOWN, buff=0.25)

        ans = MathTex(r"ans_2 = (\cdots) + (\cdots)", color=self.COLOR_ACC).scale(0.8)
        ans.to_edge(DOWN)

        self.play(FadeIn(top, shift=UP * 0.1), run_time=self.STANDARD)
        self.play(FadeIn(f1, shift=UP * 0.1), run_time=self.STANDARD)
        self.play(FadeIn(bot, shift=UP * 0.1), run_time=self.STANDARD)
        self.play(FadeIn(f2, shift=UP * 0.1), run_time=self.STANDARD)
        self.play(FadeIn(ans, shift=UP * 0.15), run_time=self.STANDARD)

        self.wait(self.HOLD)

    # Scene 5 -----------------------------------------------------------------
    def scene_dp_on_dag(self) -> None:
        title = Text("Turn recursion into DP on a DAG", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        self.play(Write(title), run_time=self.STANDARD)

        nodes_by_name, nodes, edges = self.build_example_graph()
        self.play(FadeIn(nodes, shift=UP * 0.08), run_time=self.STANDARD)
        self.play(*[Create(e) for e in edges], run_time=self.LONG)

        eq = MathTex(r"f_T(v)=\sum_{v\to u} f_T(u),\ \ f_T(T)=1", color=self.COLOR_TEXT).scale(0.62)
        eq.to_edge(LEFT).shift(UP * 2.65)
        self.play(FadeIn(eq, shift=RIGHT * 0.2), run_time=self.STANDARD)

        # Visualize values appearing "backwards" from the target.
        vals = {
            "out": "1",
            "dac": "1",
            "fft": "2",
            "aaa": "3",
            "bbb": "3",
            "you": "6",
        }
        labels: dict[str, Mobject] = {}

        def drop_value(name: str, *, color: ManimColor = self.COLOR_ACC) -> None:
            lbl = MathTex(vals[name], color=color).scale(0.75)
            lbl.next_to(nodes_by_name[name], RIGHT, buff=0.18)
            labels[name] = lbl
            ring = SurroundingRectangle(nodes_by_name[name], color=color, buff=0.2)
            self.play(Create(ring), FadeIn(lbl, shift=UP * 0.08), run_time=self.STANDARD)
            self.play(FadeOut(ring), run_time=self.FAST)

        drop_value("out")
        drop_value("dac")
        drop_value("fft")
        drop_value("aaa")
        drop_value("bbb")
        drop_value("you")

        arrow = Arrow(nodes_by_name["out"].get_left(), nodes_by_name["you"].get_right(), buff=0.2, color=self.COLOR_ACC)
        arrow_lbl = Text("compute backwards", color=self.COLOR_ACC).scale(self.SCALE_SMALL)
        arrow_lbl.next_to(arrow, DOWN, buff=0.12)
        self.play(Create(arrow), FadeIn(arrow_lbl, shift=UP * 0.1), run_time=self.STANDARD)
        self.wait(self.HOLD)

    # Scene 6 -----------------------------------------------------------------
    def scene_fpga_ready_node_engine(self) -> None:
        title = Text("FPGA Option A: ready-node dataflow engine", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        self.play(Write(title), run_time=self.STANDARD)

        rev = self.labeled_box("reverse adjacency\n(predecessor lists)", w=3.7, h=1.8, color=self.COLOR_TEXT)
        rev.move_to(LEFT * 4.0 + UP * 0.6)
        ready = self.labeled_box("ready queue", w=2.6, h=1.0, color=self.COLOR_ACC)
        ready.move_to(LEFT * 0.4 + UP * 0.6)
        state = self.labeled_box("node state RAM\n(sum, pending, f)", w=3.6, h=1.8, color=self.COLOR_TEXT)
        state.move_to(RIGHT * 3.7 + UP * 0.6)

        self.play(FadeIn(rev, shift=UP * 0.1), FadeIn(ready, shift=UP * 0.1), FadeIn(state, shift=UP * 0.1), run_time=self.STANDARD)

        w = self.labeled_box("worker", w=2.4, h=0.85, color=self.COLOR_DAC)
        w.move_to(LEFT * 0.4 + DOWN * 0.95)
        self.play(FadeIn(w, shift=UP * 0.1), run_time=self.STANDARD)

        a1 = Arrow(ready.get_bottom(), w.get_top(), buff=0.12, color=self.COLOR_DIM)
        a2 = Arrow(w.get_left(), rev.get_right(), buff=0.12, color=self.COLOR_DIM)
        a3 = Arrow(w.get_right(), state.get_left(), buff=0.12, color=self.COLOR_DIM)
        self.play(Create(a1), Create(a2), Create(a3), run_time=self.STANDARD)

        bullet = VGroup(
            Text("Initialize: f[T]=1", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("pending[v]=outdegree[v]", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("When pending[v]==0 → v is ready", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("Pop ready w; scatter-add to predecessors", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        bullet.to_edge(DOWN).shift(LEFT * 3.6)
        self.play(FadeIn(bullet, shift=UP * 0.15), run_time=self.STANDARD)

        token = Text("w", color=self.COLOR_ACC).scale(self.SCALE_SMALL)
        token.move_to(ready[0].get_center() + UP * 0.05)
        self.play(FadeIn(token), run_time=self.FAST)
        self.play(token.animate.move_to(w[0].get_center()), run_time=self.STANDARD)
        self.play(token.animate.move_to(state[0].get_center() + LEFT * 0.6), run_time=self.STANDARD)
        plus = MathTex(r"+", color=self.COLOR_ACC).scale(0.9)
        plus.move_to(state[0].get_center() + RIGHT * 0.6)
        self.play(FadeIn(plus), run_time=self.FAST)
        self.play(FadeOut(token), FadeOut(plus), run_time=self.FAST)

        cyc = Text("If there’s a cycle: nothing becomes ready", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        cyc.to_edge(DOWN).shift(RIGHT * 3.4)
        self.play(FadeIn(cyc, shift=UP * 0.15), run_time=self.STANDARD)
        self.wait(self.HOLD)

    # Scene 7 -----------------------------------------------------------------
    def scene_atomic_hazards(self) -> None:
        title = Text("Hardware reality: atomic update hazards", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        self.play(Write(title), run_time=self.STANDARD)

        lane1 = self.labeled_box("worker lane 0", w=3.0, h=0.9, color=self.COLOR_TEXT)
        lane2 = self.labeled_box("worker lane 1", w=3.0, h=0.9, color=self.COLOR_TEXT)
        lane1.move_to(LEFT * 3.8 + UP * 0.9)
        lane2.move_to(LEFT * 3.8 + DOWN * 0.5)
        ram = self.labeled_box("sum/pending RAM", w=3.2, h=2.2, color=self.COLOR_ACC)
        ram.move_to(RIGHT * 3.5 + UP * 0.2)
        self.play(FadeIn(lane1, shift=UP * 0.1), FadeIn(lane2, shift=UP * 0.1), FadeIn(ram, shift=UP * 0.1), run_time=self.STANDARD)

        addr = Text("v=42", color=self.COLOR_ACC).scale(self.SCALE_SMALL)
        addr.move_to(ORIGIN).shift(UP * 0.2)
        a1 = Arrow(lane1.get_right(), ram.get_left(), buff=0.12, color=self.COLOR_DIM)
        a2 = Arrow(lane2.get_right(), ram.get_left(), buff=0.12, color=self.COLOR_DIM)
        self.play(Create(a1), Create(a2), FadeIn(addr, shift=UP * 0.1), run_time=self.STANDARD)

        collide = SurroundingRectangle(addr, color=RED, buff=0.14)
        self.play(Create(collide), run_time=self.STANDARD)

        arb = self.labeled_box("arbiter / interlock", w=3.0, h=0.9, color=RED)
        arb.move_to(ORIGIN + DOWN * 1.75)
        self.play(FadeIn(arb, shift=UP * 0.1), run_time=self.STANDARD)
        fix1 = Arrow(lane1.get_bottom(), arb.get_top(), buff=0.12, color=RED)
        fix2 = Arrow(lane2.get_bottom(), arb.get_top(), buff=0.12, color=RED)
        fix3 = Arrow(arb.get_right(), ram.get_left(), buff=0.12, color=RED)
        self.play(Create(fix1), Create(fix2), Create(fix3), run_time=self.STANDARD)

        msg = Text("Need correct read-modify-write ordering", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        msg.to_edge(DOWN)
        self.play(FadeIn(msg, shift=UP * 0.15), run_time=self.STANDARD)
        self.wait(self.HOLD)

    # Scene 8 -----------------------------------------------------------------
    def scene_vector_dp(self) -> None:
        title = Text("Option B: vector DP (multiple targets at once)", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        self.play(Write(title), run_time=self.STANDARD)

        n = self.node("v")
        vec = MathTex(r"[f_{out},\ f_{dac},\ f_{fft}]", color=self.COLOR_ACC).scale(0.65)
        g = VGroup(n, vec).arrange(RIGHT, buff=0.35)
        g.move_to(LEFT * 3.4 + UP * 1.0)
        self.play(FadeIn(g, shift=UP * 0.1), run_time=self.STANDARD)

        add = MathTex(r"F(v)=\sum_{v\to u} F(u) + I(v)", color=self.COLOR_TEXT).scale(0.7)
        add.next_to(g, DOWN, buff=0.5).align_to(g, LEFT)
        self.play(FadeIn(add, shift=RIGHT * 0.15), run_time=self.STANDARD)

        read = VGroup(
            Text("Read once:", color=self.COLOR_TEXT).scale(self.SCALE_SMALL),
            Text("paths(svr→fft)=f_fft[svr]", color=self.COLOR_FFT).scale(self.SCALE_SMALL),
            Text("paths(fft→dac)=f_dac[fft]", color=self.COLOR_DAC).scale(self.SCALE_SMALL),
            Text("paths(dac→out)=f_out[dac]", color=self.COLOR_OUT).scale(self.SCALE_SMALL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        read.to_edge(RIGHT).shift(UP * 0.15)
        self.play(FadeIn(read, shift=LEFT * 0.2), run_time=self.STANDARD)

        benefit = Text("6 DFS runs → 1 DP run (wider adds)", color=self.COLOR_ACC).scale(self.SCALE_SMALL)
        benefit.to_edge(DOWN)
        self.play(FadeIn(benefit, shift=UP * 0.15), run_time=self.STANDARD)
        self.wait(self.HOLD)

    # Scene 9 -----------------------------------------------------------------
    def scene_toposort_reverse_dp(self) -> None:
        title = Text("Option C: topo-sort then reverse DP", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        self.play(Write(title), run_time=self.STANDARD)

        q = self.labeled_box("Kahn queue", w=2.6, h=0.9, color=self.COLOR_ACC)
        q.move_to(LEFT * 4.0 + UP * 0.8)
        order = self.labeled_box("topo order", w=6.0, h=0.9, color=self.COLOR_TEXT)
        order.move_to(ORIGIN + UP * 0.8)
        sweep = self.labeled_box("reverse sweep", w=6.0, h=0.9, color=self.COLOR_TEXT)
        sweep.next_to(order, DOWN, buff=0.55)
        self.play(FadeIn(q, shift=UP * 0.1), FadeIn(order, shift=UP * 0.1), FadeIn(sweep, shift=UP * 0.1), run_time=self.STANDARD)

        dots = VGroup(*[Dot(radius=0.05, color=self.COLOR_ACC) for _ in range(6)]).arrange(RIGHT, buff=0.35)
        dots.move_to(order[0].get_center() + DOWN * 0.05)
        self.play(FadeIn(dots), run_time=self.FAST)

        arrow = Arrow(order.get_bottom(), sweep.get_top(), buff=0.12, color=self.COLOR_ACC)
        self.play(Create(arrow), run_time=self.STANDARD)
        self.play(dots.animate.move_to(sweep[0].get_center() + DOWN * 0.05), run_time=self.STANDARD)

        msg = Text("Deterministic schedule; different memory tradeoffs", color=self.COLOR_TEXT).scale(self.SCALE_SMALL)
        msg.to_edge(DOWN)
        self.play(FadeIn(msg, shift=UP * 0.15), run_time=self.STANDARD)
        self.wait(self.HOLD)

    # Scene 10 ----------------------------------------------------------------
    def scene_takeaway(self) -> None:
        title = Text("Takeaway", color=WHITE).scale(self.SCALE_TITLE).to_edge(UP)
        self.play(Write(title), run_time=self.STANDARD)

        # A tiny graph icon...
        a = Dot(color=self.COLOR_TEXT)
        b = Dot(color=self.COLOR_TEXT)
        c = Dot(color=self.COLOR_TEXT)
        a.shift(LEFT * 1.0 + UP * 0.5)
        b.shift(RIGHT * 0.6 + UP * 0.8)
        c.shift(RIGHT * 0.7 + DOWN * 0.5)
        e1 = Arrow(a.get_center(), b.get_center(), buff=0.1, color=self.COLOR_DIM)
        e2 = Arrow(a.get_center(), c.get_center(), buff=0.1, color=self.COLOR_DIM)
        e3 = Arrow(b.get_center(), c.get_center(), buff=0.1, color=self.COLOR_DIM)
        graph_icon = VGroup(a, b, c, e1, e2, e3).scale(1.6).move_to(LEFT * 3.0)

        # ...morphs into a pipeline icon.
        p1 = RoundedRectangle(width=1.3, height=0.7, corner_radius=0.16, color=self.COLOR_TEXT)
        p2 = RoundedRectangle(width=1.3, height=0.7, corner_radius=0.16, color=self.COLOR_TEXT)
        p3 = RoundedRectangle(width=1.3, height=0.7, corner_radius=0.16, color=self.COLOR_TEXT)
        for p in [p1, p2, p3]:
            p.set_fill(self.COLOR_TEXT, opacity=0.04)
        pipeline = VGroup(p1, p2, p3).arrange(RIGHT, buff=0.4).scale(1.1).move_to(RIGHT * 2.8)
        pa = VGroup(
            Arrow(p1.get_right(), p2.get_left(), buff=0.12, color=self.COLOR_ACC),
            Arrow(p2.get_right(), p3.get_left(), buff=0.12, color=self.COLOR_ACC),
        )
        pipeline_icon = VGroup(pipeline, pa)

        self.play(FadeIn(graph_icon, shift=UP * 0.1), run_time=self.STANDARD)
        self.play(FadeIn(pipeline_icon, shift=UP * 0.1), run_time=self.STANDARD)

        tag = Text("Path counting is add-and-store… but scheduling is the whole game.", color=self.COLOR_TEXT).scale(
            self.SCALE_SMALL
        )
        tag.to_edge(DOWN)
        self.play(FadeIn(tag, shift=UP * 0.15), run_time=self.STANDARD)
        self.wait(self.HOLD)
