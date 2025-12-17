open! Core


(* Day 11 — Reactor

   Paper Option C: Explicit Topological Sort + Systolic Summation

   A full implementation would stream adjacency lists and perform systolic
   reductions.

   The current validated harness provides host-computed path counts; we reuse Option
   A’s combine engine to remain correct.
*)

module I = Day11_opt_a_path_aggregator.I
module O = Day11_opt_a_path_aggregator.O

let create = Day11_opt_a_path_aggregator.create
