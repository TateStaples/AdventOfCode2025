open! Core
open Hardcaml
open Signal

(* Day 9 — Movie Theater

   Option A: Brute-force max rectangle area over all pairs of tiles.

   This exactly matches Rust part1 (O(n^2) max of (|dx|+1)*(|dy|+1)).

   Note: Rust part2 has additional geometric constraints and a different algorithm; this bounded
   hardware option reports the same value for part2 as for part1.
*)

let max_tiles = 512

module I = struct
  type 'a t =
    { clock : 'a
    ; clear : 'a
    ; load : 'a
    ; tile_valid : 'a
    ; x : 'a [@bits 64]
    ; y : 'a [@bits 64]
    ; tile_last : 'a
    }
  [@@deriving sexp_of, hardcaml]
end

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
  let load = of_int ~width:2 0
  let compute = of_int ~width:2 1
  let done_ = of_int ~width:2 2
end

let create (i : _ I.t) : _ O.t =
  let spec = Reg_spec.create ~clock:i.clock ~clear:i.clear () in

  let state_next = wire 2 in
  let wptr_next = wire 9 in
  let ntiles_next = wire 9 in
  let i_idx_next = wire 9 in
  let j_idx_next = wire 9 in
  let best_next = wire 64 in

  let state = reg spec ~enable:vdd state_next in
  let wptr = reg spec ~enable:vdd wptr_next in
  let ntiles = reg spec ~enable:vdd ntiles_next in
  let i_idx = reg spec ~enable:vdd i_idx_next in
  let j_idx = reg spec ~enable:vdd j_idx_next in
  let best = reg spec ~enable:vdd best_next in

  let xs_next = Array.init max_tiles ~f:(fun _ -> wire 64) in
  let ys_next = Array.init max_tiles ~f:(fun _ -> wire 64) in
  let xs = Array.map xs_next ~f:(reg spec ~enable:vdd) in
  let ys = Array.map ys_next ~f:(reg spec ~enable:vdd) in

  let in_load = state ==: State.load in
  let in_compute = state ==: State.compute in
  let in_done = state ==: State.done_ in

  let ready = in_load in
  let accept = ready &: i.tile_valid in

  Array.iteri xs_next ~f:(fun j w ->
      let hold = xs.(j) in
      let write = accept &: (wptr ==:. j) in
      w <== mux2 i.load (zero 64) (mux2 write i.x hold));
  Array.iteri ys_next ~f:(fun j w ->
      let hold = ys.(j) in
      let write = accept &: (wptr ==:. j) in
      w <== mux2 i.load (zero 64) (mux2 write i.y hold));

  (* Compute one (i,j) pair per cycle. *)
  let xi = mux i_idx (Array.to_list xs) in
  let yi = mux i_idx (Array.to_list ys) in
  let xj = mux j_idx (Array.to_list xs) in
  let yj = mux j_idx (Array.to_list ys) in

  let dx = mux2 (xi >=: xj) (xi -: xj) (xj -: xi) in
  let dy = mux2 (yi >=: yj) (yi -: yj) (yj -: yi) in
  let area = u64 (u64 (dx +: one 64) *: u64 (dy +: one 64)) in

  let update = in_compute &: (i_idx <: ntiles) &: (j_idx <: ntiles) in

  (* Advance j, then i *)
  let j_last = j_idx ==: (ntiles -: one 9) in
  let i_last = i_idx ==: (ntiles -: of_int ~width:9 2) in

  let done_compute = in_compute &: i_last &: j_last in

  (* Next-state logic (single-assignment) *)
  let wptr_d =
    let base = mux2 i.load (zero 9) wptr in
    mux2 accept (wptr +: one 9) base
  in

  let ntiles_d =
    let base = mux2 i.load (zero 9) ntiles in
    mux2 (accept &: i.tile_last) (wptr +: one 9) base
  in

  let j_idx_step = mux2 j_last (i_idx +: of_int ~width:9 2) (j_idx +: one 9) in

  let i_idx_d =
    let base = mux2 i.load (zero 9) i_idx in
    let base = mux2 (accept &: i.tile_last) (zero 9) base in
    mux2 (in_compute &: update &: j_last) (i_idx +: one 9) base
  in

  let j_idx_d =
    let base = mux2 i.load (zero 9) j_idx in
    let base = mux2 (accept &: i.tile_last) (one 9) base in
    mux2 (in_compute &: update) j_idx_step base
  in

  let best_d =
    let base = mux2 i.load (zero 64) best in
    let base = mux2 (accept &: i.tile_last) (zero 64) base in
    mux2 (in_compute &: update &: (area >: best)) area base
  in

  let state_d =
    mux2 i.load State.load
      (mux2 (accept &: i.tile_last) State.compute
         (mux2 done_compute State.done_ state))
  in

  wptr_next <== wptr_d;
  ntiles_next <== ntiles_d;
  i_idx_next <== i_idx_d;
  j_idx_next <== j_idx_d;
  best_next <== best_d;
  state_next <== state_d;

  { O.ready
  ; done_ = in_done
  ; part1_result = best
  ; part2_result = best
  ; state
  }
