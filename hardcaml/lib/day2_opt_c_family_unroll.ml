open! Core
open Hardcaml
open Signal

(* Day 2 — Paper Option C: Max-Parallelism “Family Unroll”

   Evaluates all precomputed families in parallel for a single input range.
   This is intended as an area/throughput tradeoff demonstration.

   Notes:
   - This module assumes the input range is inclusive [from_, to_].
   - It does not attempt to deduplicate across overlapping ranges.
*)

module I = struct
  type 'a t =
    { from_ : 'a [@bits 64]
    ; to_ : 'a [@bits 64]
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

let const64 (x : Int64.t) = of_int64 ~width:64 x
let u64 (x : Signal.t) = uresize x 64

let families : (Int64.t * Int64.t * Int64.t * [ `First | `Second | `Third ]) array =
  let open Day2_families in
  let expand (tag : [ `First | `Second | `Third ]) (fs : Family.t list) =
    List.map fs ~f:(fun f -> Day2_families.Family.step f, Family.start f, Family.stop f, tag)
  in
  Array.of_list (expand `First first @ expand `Second second @ expand `Third third)

let next_multiple_of ~x ~step =
  (* ceil(x/step) * step *)
  let step_minus_1 = u64 (step -: one 64) in
  let q = Division.udiv ~numerator:(u64 (x +: step_minus_1)) ~denominator:step in
  u64 (q *: step)

let family_contribution ~from_ ~to_ ~step ~start_s ~stop_s =
  (* Computes sum of progression elements within [from_,to_] inclusive. *)
  let lower =
    let lower0 = next_multiple_of ~x:from_ ~step in
    mux2 (lower0 >: start_s) lower0 start_s
  in
  let upper = mux2 (to_ <: stop_s) to_ stop_s in
  let in_range = lower <=: upper in

  let n = Division.udiv ~numerator:(u64 (upper -: lower)) ~denominator:step in
  let count = u64 (n +: one 64) in
  let triangular =
    Division.udiv
      ~numerator:(u64 (n *: (u64 (n +: one 64))))
      ~denominator:(of_int ~width:64 2)
  in
  let addend =
    let base = u64 (count *: lower) in
    let extra = u64 (step *: triangular) in
    u64 (base +: extra)
  in

  mux2 in_range addend (zero 64)

let create (i : _ I.t) =
  let from_ = i.from_ in
  let to_ = i.to_ in

  let sums_first = ref (zero 64) in
  let sums_second = ref (zero 64) in
  let sums_third = ref (zero 64) in

  Array.iter families ~f:(fun (step_c, start_c, stop_c, tag) ->
    let step = const64 step_c in
    let start_s = const64 start_c in
    let stop_s = const64 stop_c in
    let add = family_contribution ~from_ ~to_ ~step ~start_s ~stop_s in
    match tag with
    | `First -> sums_first := u64 (!sums_first +: add)
    | `Second -> sums_second := u64 (!sums_second +: add)
    | `Third -> sums_third := u64 (!sums_third +: add));

  let sum_p1 = !sums_first in
  let sum_p2 = u64 (!sums_first +: !sums_second -: !sums_third) in
  { O.sum_p1; sum_p2 }
