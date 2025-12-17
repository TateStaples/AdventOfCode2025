open! Core
open Hardcaml
open Signal

(* Day 7 — Laboratories

   Option A: Sequential timeline split simulator.

   Matches Rust reference:
   - width = line length
   - center = width/2
   - timelines[center] = 1
   - iterate rows y = 0.., using only every other input row (host streams those rows)
   - for x in [center-y .. center+y] step 2:
       if timelines[x] > 0 && row[x] == '^':
         splits += 1; timelines[x]=0; timelines[x-1]+=count; timelines[x+1]+=count
   - part2 = sum timelines

   To keep the interface small, the host streams only the relevant rows as a bitvector where
   bit[x]=1 indicates '^' at x.
*)

let max_w = 256

module I = struct
  type 'a t =
    { clock : 'a
    ; clear : 'a
    ; load : 'a
    ; width : 'a [@bits 8]
    ; row_valid : 'a
    ; row_bits : 'a [@bits max_w]
    ; row_last : 'a
    }
  [@@deriving sexp_of, hardcaml]
end

module O = struct
  type 'a t =
    { ready : 'a
    ; done_ : 'a
    ; part1_result : 'a [@bits 64]
    ; part2_result : 'a [@bits 64]
    ; state : 'a [@bits 3]
    }
  [@@deriving sexp_of, hardcaml]
end

let u64 x = uresize x 64

module State = struct
  let idle = of_int ~width:3 0
  let wait_row = of_int ~width:3 1
  let process = of_int ~width:3 2
  let sum = of_int ~width:3 3
  let done_ = of_int ~width:3 4
end

let create (i : _ I.t) : _ O.t =
  let spec = Reg_spec.create ~clock:i.clock ~clear:i.clear () in

  let state_next = wire 3 in
  let width_next = wire 8 in
  let center_next = wire 8 in
  let y_next = wire 8 in
  let x_next = wire 8 in
  let start_x_next = wire 8 in
  let end_x_next = wire 8 in
  let splits_next = wire 64 in
  let sum_idx_next = wire 8 in
  let sum_acc_next = wire 64 in
  let part2_next = wire 64 in
  let row_bits_next = wire max_w in
  let row_last_latched_next = wire 1 in

  let state = reg spec ~enable:vdd state_next in
  let width = reg spec ~enable:vdd width_next in
  let center = reg spec ~enable:vdd center_next in
  let y = reg spec ~enable:vdd y_next in
  let x = reg spec ~enable:vdd x_next in
  let start_x = reg spec ~enable:vdd start_x_next in
  let end_x = reg spec ~enable:vdd end_x_next in
  let splits = reg spec ~enable:vdd splits_next in
  let sum_idx = reg spec ~enable:vdd sum_idx_next in
  let sum_acc = reg spec ~enable:vdd sum_acc_next in
  let part2 = reg spec ~enable:vdd part2_next in
  let row_bits = reg spec ~enable:vdd row_bits_next in
  let row_last_latched = reg spec ~enable:vdd row_last_latched_next in

  (* timelines[x] array *)
  let timelines_next = Array.init max_w ~f:(fun _ -> wire 64) in
  let timelines = Array.map timelines_next ~f:(reg spec ~enable:vdd) in

  let done_ = state ==: State.done_ in
  let ready = state ==: State.wait_row in
  let accept_row = ready &: i.row_valid in

  (* Derived positions for the current y when latching a new row. *)
  let center_minus_y = uresize (center -: y) 8 in
  let center_plus_y = uresize (center +: y) 8 in

  (* PROCESS step control *)
  let in_process = state ==: State.process in
  let x_in_range = x <=: end_x in
  let finish_row = in_process &: ~:x_in_range in
  let start_sum = finish_row &: row_last_latched in

  (* Row marker at x (dynamic index) *)
  let row_has_hat = mux x (List.init max_w ~f:(fun j -> bit row_bits j)) in

  (* timeline readouts *)
  let timeline_x = mux x (Array.to_list timelines) in
  let x_minus1 = x -: one 8 in
  let x_plus1 = x +: one 8 in
  let timeline_left = mux x_minus1 (Array.to_list timelines) in
  let timeline_right = mux x_plus1 (Array.to_list timelines) in

  let do_split = in_process &: x_in_range &: (timeline_x <>:. 0) &: row_has_hat in
  let add_left = u64 (timeline_left +: timeline_x) in
  let add_right = u64 (timeline_right +: timeline_x) in

  (* SUM step control *)
  let in_sum = state ==: State.sum in
  let sum_in_range = sum_idx <: width in
  let sum_done = in_sum &: ~:sum_in_range in
  let sum_value = mux sum_idx (Array.to_list timelines) in

  (* Next-state: width/center *)
  width_next <== mux2 i.load i.width width;
  center_next <== mux2 i.load (srl i.width 1) center;

  (* Next-state: row latch *)
  row_bits_next <== mux2 i.load (zero max_w) (mux2 accept_row i.row_bits row_bits);
  row_last_latched_next <== mux2 i.load (zero 1) (mux2 accept_row i.row_last row_last_latched);

  (* Next-state: x/y and row ranges *)
  start_x_next <== mux2 i.load (zero 8) (mux2 accept_row center_minus_y start_x);
  end_x_next <== mux2 i.load (zero 8) (mux2 accept_row center_plus_y end_x);

  x_next <==
    mux2 i.load (zero 8)
      (mux2 accept_row center_minus_y
         (mux2 (in_process &: x_in_range) (x +: of_int ~width:8 2) x));

  y_next <== mux2 i.load (zero 8) (mux2 finish_row (y +: one 8) y);

  (* splits counter *)
  splits_next <== mux2 i.load (zero 64) (mux2 do_split (u64 (splits +: one 64)) splits);

  (* SUM accumulator/counter *)
  sum_idx_next <==
    mux2 i.load (zero 8)
      (mux2 start_sum (zero 8) (mux2 in_sum (sum_idx +: one 8) sum_idx));

  sum_acc_next <==
    mux2 i.load (zero 64)
      (mux2 start_sum (zero 64)
         (mux2 (in_sum &: sum_in_range) (u64 (sum_acc +: sum_value)) sum_acc));

  part2_next <== mux2 i.load (zero 64) (mux2 sum_done sum_acc part2);

  (* State machine *)
  state_next <==
    mux2 i.load State.wait_row
      (mux2 accept_row State.process
         (mux2 finish_row (mux2 row_last_latched State.sum State.wait_row)
            (mux2 sum_done State.done_ state)));

  (* timelines update *)
  Array.iteri timelines_next ~f:(fun j w ->
      let init = mux2 (center_next ==:. j) (one 64) (zero 64) in
      let hold = timelines.(j) in
      let updated =
        mux2 (do_split &: (x ==:. j)) (zero 64)
          (mux2 (do_split &: (x_minus1 ==:. j)) add_left
             (mux2 (do_split &: (x_plus1 ==:. j)) add_right hold))
      in
      w <== mux2 i.load init updated);

  { O.ready; done_; part1_result = splits; part2_result = part2; state }
