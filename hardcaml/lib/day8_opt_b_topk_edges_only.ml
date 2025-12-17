open! Core


(* Day 8 — Playground

   Paper Option B: “Top-K Edges Only” Accelerator for Part 1

   The paper discusses optimizing Part 1 by only considering a bounded number of
   smallest-distance edges.

   In this repo, the validated interface already assumes the host provides the exact
   edges required (sorted streams for Part 1 and Part 2). This module therefore
   reuses the Option A core so it remains correct and synthesizable.
*)

module I = Day8_opt_a_streaming_union_find.I
module O = Day8_opt_a_streaming_union_find.O

let create = Day8_opt_a_streaming_union_find.create
