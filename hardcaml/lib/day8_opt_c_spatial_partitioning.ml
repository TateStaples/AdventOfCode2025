open! Core


(* Day 8 — Playground

   Paper Option C: Spatial Partitioning

   This design shifts much of the complexity to a spatial bucketing scheme.

   The existing validated Hardcaml core expects a host-provided sorted edge stream.
   To keep results correct under the current harness, we reuse Option A.
*)

module I = Day8_opt_a_streaming_union_find.I
module O = Day8_opt_a_streaming_union_find.O

let create = Day8_opt_a_streaming_union_find.create
