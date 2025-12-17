open! Core
open Hardcaml
open Signal

(* Day 6 — Trash Compactor

   Option A: Host-parsed block streaming.

   The Rust reference identifies blocks using the bottom marker row. To keep the RTL small and
   deterministic, this module assumes the host has already segmented the input into blocks and
   streams only the digit rows (excluding the marker row).

   Per block:
   - If [block_plus]=1, compute sum of row-numbers and sum of column-numbers.
   - If [block_plus]=0, compute product of row-numbers and product of column-numbers.

   Across blocks, the puzzle sums per-block results (matches Rust: (part_one + first, part_two + second)).

   Digits are concatenated left-to-right while ignoring spaces, exactly like:
     acc(number, digit) = if space then number else 10*number + digit
*)

module I = struct
  type 'a t =
    { clock : 'a
    ; clear : 'a
    ; load : 'a
    ; col_valid : 'a
    ; block_start : 'a
    ; block_plus : 'a
    ; col_last : 'a
    ; frame_last : 'a
    ; r0_digit : 'a [@bits 4]
    ; r0_space : 'a
    ; r1_digit : 'a [@bits 4]
    ; r1_space : 'a
    ; r2_digit : 'a [@bits 4]
    ; r2_space : 'a
    ; r3_digit : 'a [@bits 4]
    ; r3_space : 'a
    }
  [@@deriving sexp_of, hardcaml]
end

module O = struct
  type 'a t =
    { ready : 'a
    ; done_ : 'a
    ; part1_result : 'a [@bits 64]
    ; part2_result : 'a [@bits 64]
    ; in_block : 'a
    }
  [@@deriving sexp_of, hardcaml]
end

let u64 x = uresize x 64

let mul10 (x : Signal.t) : Signal.t =
  (* x * 10 = (x << 3) + (x << 1), computed modulo 2^64 *)
  u64 (sll x 3 +: sll x 1)

let acc_digit ~(space : Signal.t) ~(digit : Signal.t) ~(number : Signal.t) : Signal.t =
  let add = u64 (mul10 number +: u64 digit) in
  mux2 space number add

let create (i : _ I.t) : _ O.t =
  let spec = Reg_spec.create ~clock:i.clock ~clear:i.clear () in

  let part1_next = wire 64 in
  let part2_next = wire 64 in
  let in_block_next = wire 1 in
  let plus_next = wire 1 in
  let r0_next = wire 64 in
  let r1_next = wire 64 in
  let r2_next = wire 64 in
  let r3_next = wire 64 in
  let col_agg_next = wire 64 in
  let done_next = wire 1 in

  let part1 = reg spec ~enable:vdd part1_next in
  let part2 = reg spec ~enable:vdd part2_next in
  let in_block = reg spec ~enable:vdd in_block_next in
  let plus = reg spec ~enable:vdd plus_next in
  let r0 = reg spec ~enable:vdd r0_next in
  let r1 = reg spec ~enable:vdd r1_next in
  let r2 = reg spec ~enable:vdd r2_next in
  let r3 = reg spec ~enable:vdd r3_next in
  let col_agg = reg spec ~enable:vdd col_agg_next in
  let done_ = reg spec ~enable:vdd done_next in

  let ready = ~:done_ in
  let accept = ready &: i.col_valid in
  let start_block = accept &: i.block_start in
  let end_block = accept &: i.col_last in

  (* Current column's per-column number (top-to-bottom), ignoring spaces. *)
  let col_num =
    let n0 = acc_digit ~space:i.r0_space ~digit:i.r0_digit ~number:(zero 64) in
    let n1 = acc_digit ~space:i.r1_space ~digit:i.r1_digit ~number:n0 in
    let n2 = acc_digit ~space:i.r2_space ~digit:i.r2_digit ~number:n1 in
    acc_digit ~space:i.r3_space ~digit:i.r3_digit ~number:n2
  in

  let agg_init = mux2 i.block_plus (zero 64) (one 64) in
  let plus_eff = mux2 start_block i.block_plus plus in
  let r0_base = mux2 start_block (zero 64) r0 in
  let r1_base = mux2 start_block (zero 64) r1 in
  let r2_base = mux2 start_block (zero 64) r2 in
  let r3_base = mux2 start_block (zero 64) r3 in
  let col_agg_base = mux2 start_block agg_init col_agg in

  let r0_after = acc_digit ~space:i.r0_space ~digit:i.r0_digit ~number:r0_base in
  let r1_after = acc_digit ~space:i.r1_space ~digit:i.r1_digit ~number:r1_base in
  let r2_after = acc_digit ~space:i.r2_space ~digit:i.r2_digit ~number:r2_base in
  let r3_after = acc_digit ~space:i.r3_space ~digit:i.r3_digit ~number:r3_base in

  let col_agg_after =
    let summed = u64 (col_agg_base +: col_num) in
    let prod = u64 (col_agg_base *: col_num) in
    mux2 plus_eff summed prod
  in

  let rows_sum = u64 (u64 (r0_after +: r1_after) +: u64 (r2_after +: r3_after)) in
  let rows_prod = u64 (u64 (r0_after *: r1_after) *: u64 (r2_after *: r3_after)) in
  let rows_result = mux2 plus_eff rows_sum rows_prod in

  let part1_after_block = u64 (part1 +: rows_result) in
  let part2_after_block = u64 (part2 +: col_agg_after) in

  part1_next <== mux2 i.load (zero 64) (mux2 end_block part1_after_block part1);
  part2_next <== mux2 i.load (zero 64) (mux2 end_block part2_after_block part2);

  r0_next <== mux2 i.load (zero 64) (mux2 accept r0_after r0);
  r1_next <== mux2 i.load (zero 64) (mux2 accept r1_after r1);
  r2_next <== mux2 i.load (zero 64) (mux2 accept r2_after r2);
  r3_next <== mux2 i.load (zero 64) (mux2 accept r3_after r3);
  col_agg_next <== mux2 i.load (zero 64) (mux2 accept col_agg_after col_agg);

  plus_next <== mux2 i.load (zero 1) (mux2 start_block i.block_plus plus);
  in_block_next <==
    mux2 i.load (zero 1)
      (mux2 start_block (one 1) (mux2 end_block (zero 1) in_block));

  done_next <== mux2 i.load (zero 1) (mux2 (end_block &: i.frame_last) (one 1) done_);

  { O.ready; done_; part1_result = part1; part2_result = part2; in_block }
