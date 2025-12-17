open! Core
open Hardcaml
open Signal

(* Day 10 — Factory

   Option A: Host-precomputed per-machine press counts, summed in hardware.

   The Rust reference parallelizes per-machine work; this bounded RTL assumes the host computes
   each machine's minimal press count for part1 and part2 and streams them here.
*)

module I = struct
  type 'a t =
    { clock : 'a
    ; clear : 'a
    ; load : 'a
    ; item_valid : 'a
    ; presses_p1 : 'a [@bits 32]
    ; presses_p2 : 'a [@bits 32]
    ; item_last : 'a
    }
  [@@deriving sexp_of, hardcaml]
end

module O = struct
  type 'a t =
    { ready : 'a
    ; done_ : 'a
    ; part1_result : 'a [@bits 64]
    ; part2_result : 'a [@bits 64]
    }
  [@@deriving sexp_of, hardcaml]
end

let u64 x = uresize x 64

let create (i : _ I.t) : _ O.t =
  let spec = Reg_spec.create ~clock:i.clock ~clear:i.clear () in

  let sum1_next = wire 64 in
  let sum2_next = wire 64 in
  let done_next = wire 1 in

  let sum1 = reg spec ~enable:vdd sum1_next in
  let sum2 = reg spec ~enable:vdd sum2_next in
  let done_ = reg spec ~enable:vdd done_next in

  let ready = ~:done_ in
  let accept = ready &: i.item_valid in

  let sum1_after = u64 (sum1 +: uresize i.presses_p1 64) in
  let sum2_after = u64 (sum2 +: uresize i.presses_p2 64) in

  sum1_next <== mux2 i.load (zero 64) (mux2 accept sum1_after sum1);
  sum2_next <== mux2 i.load (zero 64) (mux2 accept sum2_after sum2);
  done_next <== mux2 i.load (zero 1) (mux2 (accept &: i.item_last) (one 1) done_);

  { O.ready; done_; part1_result = sum1; part2_result = sum2 }
