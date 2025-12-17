open! Core


(* Day 11 — Reactor

   Paper Option B: Multi-Target Vector DP in One Pass

   The paper describes vectorizing multiple DP targets simultaneously.

   In this repo, the validated approach is to accept host-computed path counts and
   combine them on-chip. This module reuses Option A’s stream protocol and combine
   logic.
*)

module I = Day11_opt_a_path_aggregator.I
module O = Day11_opt_a_path_aggregator.O

let create = Day11_opt_a_path_aggregator.create
