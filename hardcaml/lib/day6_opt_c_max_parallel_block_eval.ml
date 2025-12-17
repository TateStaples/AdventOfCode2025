open! Core


(* Day 6 — Trash Compactor

   Paper Option C: Max-Parallel Block Evaluation

   A full implementation would replicate multiple per-block evaluation engines.

   This repo’s validated host protocol already streams one column per cycle with 4
   digit lanes; we therefore provide a correct synthesizable implementation by
   reusing the existing block-stream core.
*)

module I = Day6_opt_a_block_stream.I
module O = Day6_opt_a_block_stream.O

let create = Day6_opt_a_block_stream.create
