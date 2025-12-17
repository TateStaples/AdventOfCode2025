open! Core


(* Day 4 — Printing Department

   Paper Option B: Event-Queue Peeling (Reference-Aligned)

   This repository’s validated implementation is Option A’s monotone fixed-point
   removal. The event-queue architecture is functionally equivalent; we expose it
   as its own module so it can be independently evolved.
*)

module I = Day4_opt_a_dense_ca.I
module O = Day4_opt_a_dense_ca.O

let create = Day4_opt_a_dense_ca.create
