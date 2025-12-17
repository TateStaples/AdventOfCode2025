open! Core
open Hardcaml
open Signal

(* Day 11 — Reactor

   Option A: Host-computed path counts, combined in hardware.

   The Rust solution performs memoized DFS over a 26^3-node graph to compute path counts for
   specific (from,to) pairs, then combines them:
     part1 = paths(you,out)
     part2 = paths(svr,fft)*paths(fft,dac)*paths(dac,out) + paths(svr,dac)*paths(dac,fft)*paths(fft,out)

   This module accepts those seven counts as a fixed-order stream and performs the multiplies/add.
*)

module I = struct
  type 'a t =
    { clock : 'a
    ; clear : 'a
    ; load : 'a
    ; count_valid : 'a
    ; count : 'a [@bits 64]
    ; count_last : 'a
    }
  [@@deriving sexp_of, hardcaml]
end

module O = struct
  type 'a t =
    { ready : 'a
    ; done_ : 'a
    ; part1_result : 'a [@bits 64]
    ; part2_result : 'a [@bits 64]
    ; idx : 'a [@bits 3]
    }
  [@@deriving sexp_of, hardcaml]
end

let u64 x = uresize x 64

let create (i : _ I.t) : _ O.t =
  let spec = Reg_spec.create ~clock:i.clock ~clear:i.clear () in

  let idx_next = wire 3 in
  let done_next = wire 1 in

  let c0_next = wire 64 in
  let c1_next = wire 64 in
  let c2_next = wire 64 in
  let c3_next = wire 64 in
  let c4_next = wire 64 in
  let c5_next = wire 64 in
  let c6_next = wire 64 in

  let idx = reg spec ~enable:vdd idx_next in
  let done_ = reg spec ~enable:vdd done_next in

  let c0 = reg spec ~enable:vdd c0_next in
  let c1 = reg spec ~enable:vdd c1_next in
  let c2 = reg spec ~enable:vdd c2_next in
  let c3 = reg spec ~enable:vdd c3_next in
  let c4 = reg spec ~enable:vdd c4_next in
  let c5 = reg spec ~enable:vdd c5_next in
  let c6 = reg spec ~enable:vdd c6_next in

  let ready = ~:done_ in
  let accept = ready &: i.count_valid in

  idx_next <== mux2 i.load (zero 3) (mux2 accept (idx +: one 3) idx);
  done_next <== mux2 i.load (zero 1) (mux2 (accept &: i.count_last) (one 1) done_);

  let write_c0 = accept &: (idx ==:. 0) in
  let write_c1 = accept &: (idx ==:. 1) in
  let write_c2 = accept &: (idx ==:. 2) in
  let write_c3 = accept &: (idx ==:. 3) in
  let write_c4 = accept &: (idx ==:. 4) in
  let write_c5 = accept &: (idx ==:. 5) in
  let write_c6 = accept &: (idx ==:. 6) in

  c0_next <== mux2 i.load (zero 64) (mux2 write_c0 i.count c0);
  c1_next <== mux2 i.load (zero 64) (mux2 write_c1 i.count c1);
  c2_next <== mux2 i.load (zero 64) (mux2 write_c2 i.count c2);
  c3_next <== mux2 i.load (zero 64) (mux2 write_c3 i.count c3);
  c4_next <== mux2 i.load (zero 64) (mux2 write_c4 i.count c4);
  c5_next <== mux2 i.load (zero 64) (mux2 write_c5 i.count c5);
  c6_next <== mux2 i.load (zero 64) (mux2 write_c6 i.count c6);

  let part1 = c0 in
  let one = u64 (u64 (c1 *: c2) *: c3) in
  let two = u64 (u64 (c4 *: c5) *: c6) in
  let part2 = u64 (one +: two) in

  { O.ready; done_; part1_result = part1; part2_result = part2; idx }
