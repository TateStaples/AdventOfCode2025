open! Core
open Hardcaml
open Signal

(* Day 3 — Lobby

   Paper Option B: One-Pass Left-to-Right Monotone Stack (Lower Latency)

   This is the earlier streaming monotonic-stack style implementation. It is kept
   as a separate option module for comparison.
*)

let max_len = 128
let max_k = 12

module I = struct
  type 'a t =
    { clock : 'a
    ; clear : 'a
    ; start : 'a
    ; data : 'a [@bits 512]  (* 128 * 4-bit BCD digits, LSB-first *)
    ; length : 'a [@bits 8]  (* number of valid digits *)
    ; k : 'a [@bits 4]       (* digits to keep, <= 12 *)
    }
  [@@deriving sexp_of, hardcaml]
end

module O = struct
  type 'a t =
    { result : 'a [@bits 64]  (* enough for 12 digits *)
    ; done_ : 'a
    }
  [@@deriving sexp_of, hardcaml]
end

module State = struct
  type t = Idle | Load | Process | Finished
  [@@deriving sexp_of, compare, enumerate]

  let to_int = function
    | Idle -> 0
    | Load -> 1
    | Process -> 2
    | Finished -> 3

  let width = 2
end

let create (i : _ I.t) =
  let spec = Reg_spec.create ~clock:i.clock ~clear:i.clear () in

  (* Registers with explicit D wires *)
  let state_d = wire State.width in
  let idx_d = wire 8 in
  let k_d = wire 4 in
  let batteries_d = Array.init max_k ~f:(fun _ -> wire 4) in
  let result_d = wire 64 in
  let done_d = wire 1 in

  let state = reg spec ~enable:(one 1) state_d in
  let idx = reg spec ~enable:(one 1) idx_d in
  let k_reg = reg spec ~enable:(one 1) k_d in
  let batteries = Array.map batteries_d ~f:(reg spec ~enable:(one 1)) in
  let result = reg spec ~enable:(one 1) result_d in
  let done_r = reg spec ~enable:(one 1) done_d in

  let s_val s = of_int ~width:State.width (State.to_int s) in

  let digits =
    List.init max_len ~f:(fun j ->
        let lo = j * 4 in
        let hi = lo + 3 in
        i.data.:[hi, lo])
  in
  let current_digit = mux idx digits in

  (* Load phase: idx goes from (length - k) to (length - 1), loads last k digits *)
  (* Use i.k directly on start cycle, k_reg thereafter for stable computation *)
  let k_for_load = mux2 i.start i.k k_reg in
  let load_start = i.length -: uresize k_for_load 8 in
  let load_done = idx >=: i.length in
  
  (* Process phase: idx counts DOWN from (length - k - 1) to 0, processing one per cycle *)
  let process_start = load_start -: one 8 in
  let process_active = state ==: s_val Process in
  (* Stop when idx wraps from 0 to 255 after decrement *)
  let process_done = process_active &: (idx ==:. 255) in

  (* Battery insertion logic (combinational) *)
  let insert_digit digit =
    let next_val = ref digit in
    let stopped = ref (zero 1) in  (* Track if we've hit the break condition *)
    Array.init max_k ~f:(fun j ->
      let use_slot = of_int ~width:4 j <: k_reg in
      let batt = batteries.(j) in
      (* Can only swap if: in active slot, not stopped, and next >= battery *)
      let should_check = use_slot &: ~: (!stopped) in
      let next_lt_batt = !next_val <: batt in
      let can_swap = should_check &: ~: next_lt_batt in
      (* Update stop condition: if we're in an active slot and next < battery, stop *)
      stopped := !stopped |: (should_check &: next_lt_batt);
      let batt_out = mux2 can_swap !next_val batt in
      next_val := mux2 can_swap batt !next_val;
      batt_out)
  in

  (* State transitions *)
  let idle_to_load = i.start in
  let load_to_process = load_done in
  let process_to_finished = process_done in

  state_d <== (
    mux2 idle_to_load (s_val Load)
      (mux2 (state ==: s_val Load &: load_to_process) (s_val Process)
        (mux2 (state ==: s_val Process &: process_to_finished) (s_val Finished)
          (mux2 (state ==: s_val Finished) (s_val Idle)
            state))));

  (* Index management *)
  idx_d <== (
    mux2 i.start load_start
      (mux2 (state ==: s_val Load &: load_done) process_start
        (mux2 (state ==: s_val Load) (idx +: one 8)
          (mux2 (state ==: s_val Process) (idx -: one 8)
            idx))));

  k_d <== mux2 i.start i.k k_reg;

  (* Battery updates *)
  let updated_batteries = insert_digit current_digit in
  Array.iteri batteries_d ~f:(fun j d_wire ->
    let cur = batteries.(j) in
    let load_pos = idx -: load_start in
    let load_write = (state ==: s_val Load) &: (uresize load_pos 4 ==: of_int ~width:4 j) in
    let process_write = state ==: s_val Process in
    d_wire <== (
      mux2 i.start (zero 4)
        (mux2 load_write current_digit
          (mux2 process_write updated_batteries.(j)
            cur))));

  (* Result computation *)
  let final_result =
    List.init max_k ~f:Fn.id
    |> List.fold ~init:(zero 64) ~f:(fun acc j ->
           let use = of_int ~width:4 j <: k_reg in
           let d = batteries.(j) in
           let acc10 = uresize (acc *: of_int ~width:64 10) 64 in
           let acc' = acc10 +: uresize d 64 in
           mux2 use acc' acc)
  in

  result_d <== mux2 (state ==: s_val Finished) final_result result;
  done_d <== mux2 (state ==: s_val Finished) (one 1) (mux2 i.start (zero 1) done_r);

  { O.result = result; done_ = done_r }
