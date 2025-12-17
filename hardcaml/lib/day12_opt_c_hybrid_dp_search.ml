open! Core


(* Day 12 — Christmas Tree Farm

   Paper Option C: Hybrid — DP for Geometry, Search for Counts

   This is a distinct architecture in the paper.

   Under the current repo’s validated protocol, we reuse the Option A chunk-filter
   implementation.
*)

module I = Day12_opt_a_chunk_filter.I
module O = Day12_opt_a_chunk_filter.O

let create = Day12_opt_a_chunk_filter.create
