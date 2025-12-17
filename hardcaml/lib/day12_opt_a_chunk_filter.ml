open! Core
open Hardcaml
open Signal

(* Day 12 — Christmas Tree Farm

   Option A: Streaming integer parser output + filter/count.

   Matches Rust part1 behavior:
     iter_unsigned::<u32>()
       .skip(6)
       .chunk::<8>()
       .filter(|[w,h,presents..]| (w/3)*(h/3) >= sum(presents))
       .count()

   Part2 is "n/a" in the Rust reference; this module returns 0 for part2.
*)

module I = struct
  type 'a t =
    { clock : 'a
    ; clear : 'a
    ; load : 'a
    ; num_valid : 'a
    ; num : 'a [@bits 32]
    ; num_last : 'a
    }
  [@@deriving sexp_of, hardcaml]
end

module O = struct
  type 'a t =
    { ready : 'a
    ; done_ : 'a
    ; part1_result : 'a [@bits 64]
    ; part2_result : 'a [@bits 64]
    ; idx_mod8 : 'a [@bits 3]
    }
  [@@deriving sexp_of, hardcaml]
end

let u64 x = uresize x 64

let create (i : _ I.t) : _ O.t =
  let spec = Reg_spec.create ~clock:i.clock ~clear:i.clear () in

  let skip_next = wire 3 in
  let idx_next = wire 3 in
  let w_next = wire 32 in
  let h_next = wire 32 in
  let sum_presents_next = wire 32 in
  let count_next = wire 64 in
  let done_next = wire 1 in

  let skip = reg spec ~enable:vdd skip_next in
  let idx = reg spec ~enable:vdd idx_next in
  let w = reg spec ~enable:vdd w_next in
  let h = reg spec ~enable:vdd h_next in
  let sum_presents = reg spec ~enable:vdd sum_presents_next in
  let count = reg spec ~enable:vdd count_next in
  let done_ = reg spec ~enable:vdd done_next in

  let ready = ~:done_ in
  let accept = ready &: i.num_valid in

  let skipping = skip <: of_int ~width:3 6 in
  let skip_inc = skip +: one 3 in
  let skip_after = mux2 (accept &: skipping) skip_inc skip in

  let idx_inc = mux2 accept (idx +: one 3) idx in

  (* local helpers *)
  let in_w = idx ==:. 0 in
  let in_h = idx ==:. 1 in
  let in_present = idx >=:. 2 in

  let sum_presents_after = uresize (sum_presents +: i.num) 32 in

  (* when we finish a record (idx==7 and accepting), evaluate predicate *)
  let end_record = accept &: (idx ==:. 7) in

  let w_div3 = Division.udiv ~numerator:w ~denominator:(of_int ~width:32 3) in
  let h_div3 = Division.udiv ~numerator:h ~denominator:(of_int ~width:32 3) in
  let capacity = u64 (uresize w_div3 64 *: uresize h_div3 64) in
  let presents_total = uresize sum_presents_after 64 in
  let ok = capacity >=: presents_total in
  let count_after = u64 (count +: mux2 ok (one 64) (zero 64)) in

  skip_next <== mux2 i.load (zero 3) skip_after;

  idx_next <==
    mux2 i.load (zero 3)
      (mux2 (accept &: skipping) (zero 3)
         (mux2 end_record (zero 3) idx_inc));

  w_next <== mux2 i.load (zero 32) (mux2 (accept &: ~:skipping &: in_w) i.num w);
  h_next <== mux2 i.load (zero 32) (mux2 (accept &: ~:skipping &: in_h) i.num h);

  sum_presents_next <==
    mux2 i.load (zero 32)
      (mux2 (accept &: skipping) sum_presents
         (mux2 (accept &: ~:skipping &: in_w) (zero 32)
            (mux2 (accept &: ~:skipping &: in_h) (zero 32)
               (mux2 (accept &: ~:skipping &: in_present) sum_presents_after sum_presents))));

  count_next <== mux2 i.load (zero 64) (mux2 end_record count_after count);

  done_next <== mux2 i.load (zero 1) (mux2 (accept &: i.num_last) (one 1) done_);

  { O.ready; done_; part1_result = count; part2_result = zero 64; idx_mod8 = idx }
