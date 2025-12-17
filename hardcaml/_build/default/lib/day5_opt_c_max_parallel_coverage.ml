open! Core


(* Day 5 — Cafeteria

   Paper Option C: Max-Parallelism Range Coverage (When ID Space is Small)

   The paper describes a direct-coverage strategy when the ID space is small enough
   to represent densely.

   In this repository, Day 5’s host protocol and existing validation harness use
   64-bit IDs and a sorted range/ID stream. Implementing a dense bitset would require
   additional host-provided compression.

   For now, we provide a synthesizable, correct implementation by reusing Option A’s
   interval-union engine and membership counter.
*)

module I = Day5_opt_a_interval_union_engine.I
module O = Day5_opt_a_interval_union_engine.O

let create = Day5_opt_a_interval_union_engine.create
