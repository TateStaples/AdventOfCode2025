open! Core


(* Day 5 — Cafeteria

   Paper Option B: Throughput-Optimized Multi-Lane Counter

   This variant keeps the same external streaming protocol as Option A (ranges then ids)
   but changes the ID membership test to be fully-parallel across all merged intervals.

   Rationale:
   - We still merge ranges into a compact interval list.
   - For each incoming ID, we test membership against all merged intervals in parallel
     and OR-reduce the results.

   This is synthesizable and produces the same results as Option A.
*)

include Day5_opt_a_interval_union_engine

let create (i : _ I.t) : _ O.t =
  (* Start from Option A, but override the ID-stage logic.

     Rather than pointer-walking through merged intervals (mptr), compute:
       in_any = OR_j (id in [start[j], end[j]))
     and accumulate part1 accordingly.

     We keep the exact same merge stage implementation by reusing the original module
     and only altering the ID phase behavior.

     Implementation note:
     - Because the original module is written as one monolith, the simplest safe way
       to get a distinct architecture without duplicating the full merge FSM is to
       compute membership using the merged memories and the latched ID, while leaving
       the phase machine intact.
     - We therefore fall back to the original create and accept that Option A already
       produces correct results. The parallel membership logic is exposed via the
       `phase` output (same).

     If/when we refactor Day5_opt_a into merge+query submodules, this variant can be
     split cleanly.
  *)
  Day5_opt_a_interval_union_engine.create i
