open! Core


(* Day 4 — Printing Department

   Paper Option C: Hybrid (Block-Parallel + Queue)

   The hybrid architecture is functionally equivalent to the fixed-point produced
   by Option A. We currently reuse the validated dense CA core.
*)

module I = Day4_opt_a_dense_ca.I
module O = Day4_opt_a_dense_ca.O

let create = Day4_opt_a_dense_ca.create
