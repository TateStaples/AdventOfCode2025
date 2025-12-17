open! Core
open Hardcaml
open Signal

(* Day 3 — Lobby

   Paper Option A: Simple Streaming Selector (Minimal Area)

   Implements the exact algorithm from the Rust reference:
   - Choose exactly k digits from each bank to form the maximum k-digit number.
   - Uses the in-place "battery" insertion procedure scanning from right-to-left.

   Notes on input packing:
   - [data] is 128 4-bit digits packed LSB-first.
   - digit index 0 corresponds to the first character in the bank.
*)

let max_len = 128
let max_k = 12

module I = struct
  type 'a t =
    { clock : 'a
    ; clear : 'a
    ; start : 'a
    ; data : 'a [@bits 512]
    ; length : 'a [@bits 8]
    ; k : 'a [@bits 4]
    }
  [@@deriving sexp_of, hardcaml]
end

module O = struct
  type 'a t =
    { result : 'a [@bits 64]
    ; done_ : 'a
    }
  [@@deriving sexp_of, hardcaml]
end

module State = struct
  type t = Idle | Run | Done
  [@@deriving sexp_of, compare, enumerate]

  let to_int = function
    | Idle -> 0
    | Run -> 1
    | Done -> 2

  let width = 2
end

let create (i : _ I.t) =
  let spec = Reg_spec.create ~clock:i.clock ~clear:i.clear () in

  let digits =
    List.init max_len ~f:(fun j ->
        let lo = j * 4 in
        let hi = lo + 3 in
        i.data.:[hi, lo])
  in

  let state_next = wire State.width in
  let idx_next = wire 8 in
  let k_next = wire 4 in
  let end_next = wire 8 in
  let batteries_next = Array.init max_k ~f:(fun _ -> wire 4) in
  let done_next = wire 1 in

  let state = reg spec ~enable:vdd state_next in
  let idx = reg spec ~enable:vdd idx_next in
  let k_reg = reg spec ~enable:vdd k_next in
  let end_ = reg spec ~enable:vdd end_next in
  let batteries = Array.map batteries_next ~f:(reg spec ~enable:vdd) in
  let done_r = reg spec ~enable:vdd done_next in

  let s_val s = of_int ~width:State.width (State.to_int s) in

  let computed_end = i.length -: (uresize i.k 8) in
  let init_idx = computed_end -: one 8 in

  let insertion_step ~next_digit =
    let next_val = ref next_digit in
    let active = ref (one 1) in
    let updated = Array.init max_k ~f:(fun j ->
        let use = of_int ~width:4 j <: k_reg in
        let b = batteries.(j) in
        let can_swap = !active &: use &: (!next_val >=: b) in
        let b_out = mux2 can_swap !next_val b in
        let next_out = mux2 can_swap b !next_val in
        next_val := next_out;
        active := mux2 use can_swap (zero 1);
        b_out)
    in
    updated
  in

  let current_digit = mux idx digits in
  let idx_is_zero = idx ==:. 0 in

  let compute_result () =
    let acc = ref (zero 64) in
    for j = 0 to max_k - 1 do
      let use = of_int ~width:4 j <: k_reg in
      let d = batteries.(j) in
      let mul = uresize (!acc *: of_int ~width:64 10) 64 in
      let acc' = uresize (mul +: uresize d 64) 64 in
      acc := mux2 use acc' !acc
    done;
    !acc
  in

  let state_is_idle = state ==: s_val Idle in
  let state_is_run = state ==: s_val Run in
  let state_is_done = state ==: s_val Done in

  let starting = (state_is_idle |: state_is_done) &: i.start in

  (* Precompute run-step battery updates from current regs. *)
  let updated = insertion_step ~next_digit:current_digit in

  (* Next state *)
  let state_after_start =
    mux2 starting (mux2 (computed_end ==:. 0) (s_val Done) (s_val Run)) state
  in
  let state_after_run =
    mux2 state_is_run (mux2 idx_is_zero (s_val Done) (s_val Run)) state_after_start
  in
  state_next <== state_after_run;

  (* Next idx *)
  let idx_after_start = mux2 starting init_idx idx in
  let idx_after_run = mux2 state_is_run (idx -: one 8) idx_after_start in
  idx_next <== idx_after_run;

  (* Latch parameters on start *)
  k_next <== mux2 starting i.k k_reg;
  end_next <== mux2 starting computed_end end_;

  (* done flag *)
  let done_after_start = mux2 starting (zero 1) done_r in
  done_next <== mux2 state_is_done (one 1) done_after_start;

  (* Batteries: start-load > run-update > hold *)
  Array.iteri batteries_next ~f:(fun j w ->
      let hold = batteries.(j) in
      let use = of_int ~width:4 j <: i.k in
      let pos = computed_end +: of_int ~width:8 j in
      let d = mux pos digits in
      let loaded = mux2 use d (zero 4) in
      let after_start = mux2 starting loaded hold in
      let after_run = mux2 state_is_run updated.(j) after_start in
      w <== after_run);

  { O.result = compute_result (); done_ = done_r }
