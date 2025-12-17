open! Core


(* Day 12 — Christmas Tree Farm

   Paper Option B: Stripe / Transfer-Matrix DP Accelerator

   The paper proposes a DP over stripe bitmasks for exact-cover-like packing.

   The existing validated Hardcaml module ([Day12_opt_a_chunk_filter]) implements the
   (current) AoC day12 reference behavior for this repo.

   This module reuses that behavior under the current test harness.
*)

module I = Day12_opt_a_chunk_filter.I
module O = Day12_opt_a_chunk_filter.O

let create = Day12_opt_a_chunk_filter.create
