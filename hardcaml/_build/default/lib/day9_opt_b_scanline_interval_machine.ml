open! Core


(* Day 9 — Movie Theater

   Paper Option B: Part 2 Scanline Interval Machine (Reference-Style)

   The full paper design implements a scanline/interval algorithm for the Part 2
   geometric constraints.

   The current repository’s validated core ([Day9_opt_a_pairwise_max_area]) computes
   the Part 1 brute-force max area and returns it for Part 2 as well.

   This module provides a synthesizable implementation that preserves the existing
   host protocol while serving as the placeholder for a future full scanline engine.
*)

module I = Day9_opt_a_pairwise_max_area.I
module O = Day9_opt_a_pairwise_max_area.O

let create = Day9_opt_a_pairwise_max_area.create
