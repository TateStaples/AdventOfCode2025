open! Core
open Hardcaml
open Signal

(* Day 2 — Paper Option B: Throughput-Optimized Multi-Lane Range Processor

   This module demonstrates lane-parallelism at the “range contribution” level.

   It computes the Option-C-style family-unrolled contribution per lane and
   then reduces the lane sums.

   Intended use: feed P independent ranges in parallel each cycle.
*)

module I = struct
  type 'a t =
    { lane_valid : 'a array [@length 4]
    ; lane_from : 'a array [@length 4] [@bits 64]
    ; lane_to : 'a array [@length 4] [@bits 64]
    }
  [@@deriving sexp_of, hardcaml]
end

module O = struct
  type 'a t =
    { sum_p1 : 'a [@bits 64]
    ; sum_p2 : 'a [@bits 64]
    }
  [@@deriving sexp_of, hardcaml]
end

let u64 (x : Signal.t) = uresize x 64

let create (i : _ I.t) =
  let lane_sums =
    Array.init 4 ~f:(fun k ->
      let lane_i : _ Day2_opt_c_family_unroll.I.t =
        { from_ = i.lane_from.(k)
        ; to_ = i.lane_to.(k)
        }
      in
      let o = Day2_opt_c_family_unroll.create lane_i in
      let v = i.lane_valid.(k) in
      let p1 = mux2 v o.sum_p1 (zero 64) in
      let p2 = mux2 v o.sum_p2 (zero 64) in
      p1, p2)
  in

  let sum_p1 =
    Array.fold lane_sums ~init:(zero 64) ~f:(fun acc (p1, _p2) -> u64 (acc +: p1))
  in
  let sum_p2 =
    Array.fold lane_sums ~init:(zero 64) ~f:(fun acc (_p1, p2) -> u64 (acc +: p2))
  in

  { O.sum_p1; sum_p2 }
