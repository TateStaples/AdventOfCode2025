open! Core
open Hardcaml
open Signal

(* Day 7 — Laboratories

   Paper Option B: Wide SIMD Row Update (Low Latency)

   This variant updates the entire timeline vector for each streamed row in one cycle.
   It keeps the same host streaming interface as Option A:
   - Host asserts [row_valid] with [row_bits] for each relevant layer.
   - [row_last] marks the final row.

   Correctness matches the reference DP:
     f[x] = (split[x] && count[x] != 0)
     next[x] = (if f[x] then 0 else count[x])
               + (if f[x-1] then count[x-1] else 0)
               + (if f[x+1] then count[x+1] else 0)
*)

let max_w = Day7_opt_a_timeline_split.max_w

module I = Day7_opt_a_timeline_split.I

module O = struct
  type 'a t =
    { ready : 'a
    ; done_ : 'a
    ; part1_result : 'a [@bits 64]
    ; part2_result : 'a [@bits 64]
    ; state : 'a [@bits 2]
    }
  [@@deriving sexp_of, hardcaml]
end

let u64 x = uresize x 64

module State = struct
  let wait_row = of_int ~width:2 0
  let done_ = of_int ~width:2 1
end

let create (i : _ I.t) : _ O.t =
  let spec = Reg_spec.create ~clock:i.clock ~clear:i.clear () in

  let state_next = wire 2 in
  let width_next = wire 8 in
  let center_next = wire 8 in
  let splits_next = wire 64 in
  let part2_next = wire 64 in
  let parity_next = wire 1 in

  let state = reg spec ~enable:vdd state_next in
  let width = reg spec ~enable:vdd width_next in
  let center = reg spec ~enable:vdd center_next in
  let splits = reg spec ~enable:vdd splits_next in
  let part2 = reg spec ~enable:vdd part2_next in
  let parity = reg spec ~enable:vdd parity_next in

  let counts_next = Array.init max_w ~f:(fun _ -> wire 64) in
  let counts = Array.map counts_next ~f:(reg spec ~enable:vdd) in

  let in_wait = state ==: State.wait_row in
  let in_done = state ==: State.done_ in

  let ready = in_wait in
  let accept_row = ready &: i.row_valid in

  (* Latch params on load *)
  width_next <== mux2 i.load i.width width;
  center_next <== mux2 i.load (srl i.width 1) center;

    (* The reference/Option A only considers every other column per row:
      x = (center - y) .. (center + y), step 2.
      Track parity = (center - y) mod 2, toggling each accepted row. *)
    parity_next <== mux2 i.load (lsb center_next) (mux2 accept_row (~:parity) parity);

  let row_hat = List.init max_w ~f:(fun j -> bit i.row_bits j) in
  let count_nonzero = List.init max_w ~f:(fun j -> counts.(j) <>:. 0) in

  let parity_ok =
    List.init max_w ~f:(fun j ->
      let j_lsb = if j land 1 = 0 then gnd else vdd in
      (* parity_ok = (j_lsb == parity) *)
      ~:(j_lsb ^: parity))
  in

  let fire =
    List.map3_exn row_hat count_nonzero parity_ok ~f:(fun hat nz ok -> hat &: nz &: ok)
  in
  let fire_bits = concat_lsb fire in
  let fired_count = uresize (popcount fire_bits) 64 in

  let splits_after = u64 (splits +: fired_count) in

  let count_at j = counts.(j) in
  let fire_at j = List.nth_exn fire j in

  (* Compute next counts vector *)
  let next_counts =
    Array.init max_w ~f:(fun j ->
      let self = mux2 (fire_at j) (zero 64) (count_at j) in
      let from_left =
        if j = 0 then zero 64
        else mux2 (fire_at (j - 1)) (count_at (j - 1)) (zero 64)
      in
      let from_right =
        if j = max_w - 1 then zero 64
        else mux2 (fire_at (j + 1)) (count_at (j + 1)) (zero 64)
      in
      u64 (u64 (self +: from_left) +: from_right))
  in

  let sum_counts (arr : Signal.t array) : Signal.t =
    Array.fold arr ~init:(zero 64) ~f:(fun acc x -> u64 (acc +: x))
  in

  let part2_after = sum_counts next_counts in

  splits_next <== mux2 i.load (zero 64) (mux2 accept_row splits_after splits);
  part2_next <== mux2 i.load (zero 64) (mux2 (accept_row &: i.row_last) part2_after part2);

  state_next <==
    mux2 i.load State.wait_row
      (mux2 (accept_row &: i.row_last) State.done_ state);

  Array.iteri counts_next ~f:(fun j w ->
    let init = mux2 (center_next ==:. j) (one 64) (zero 64) in
    let updated = mux2 accept_row next_counts.(j) counts.(j) in
    w <== mux2 i.load init updated);

  { O.ready; done_ = in_done; part1_result = splits; part2_result = part2; state }
