open! Core
open Hardcaml
open Signal

(* Day 1 — Paper Option D: Microcoded Multi-Cycle Divider

   Uses a shared sequential restoring divider to compute div/mod by 100.
   This trades throughput/latency for smaller combinational logic.
*)

module I = struct
  type 'a t =
    { clock : 'a
    ; clear : 'a
    ; instruction_valid : 'a
    ; instruction_dir : 'a
    ; instruction_mag : 'a [@bits 16]
    }
  [@@deriving hardcaml]
end

module O = struct
  type 'a t =
    { ready : 'a
    ; part1_result : 'a [@bits 32]
    ; part2_result : 'a [@bits 32]
    ; position : 'a [@bits 10]
    }
  [@@deriving hardcaml]
end

let create (i : _ I.t) =
  let spec = Reg_spec.create ~clock:i.clock ~clear:i.clear () in

  (* Architectural state *)
  let spec_pos = Reg_spec.override spec ~clear_to:(of_int ~width:10 50) in
  let position_d = wire 10 in
  let position_q = reg spec_pos ~enable:vdd position_d in

  let part1_d = wire 32 in
  let part2_d = wire 32 in
  let part1_q = reg spec ~enable:vdd part1_d in
  let part2_q = reg spec ~enable:vdd part2_d in

  (* Latched instruction *)
  let dir_d = wire 1 in
  let mag_d = wire 18 in
  let dir_q = reg spec ~enable:vdd dir_d in
  let mag_q = reg spec ~enable:vdd mag_d in

  (* Microcode phase: 0=idle, 1=div(mag), 2=div(next_pos_arg), 3=div(term1), 4=div(term2), 5=apply *)
  let phase_d = wire 3 in
  let phase_q = reg spec ~enable:vdd phase_d in

  (* Divider engine: restoring divider, MSB-first, 18 iterations *)
  let div_busy_d = wire 1 in
  let div_busy_q = reg spec ~enable:vdd div_busy_d in
  let div_cnt_d = wire 5 in
  let div_cnt_q = reg spec ~enable:vdd div_cnt_d in
  let div_rem_d = wire 18 in
  let div_rem_q = reg spec ~enable:vdd div_rem_d in
  let div_quot_d = wire 18 in
  let div_quot_q = reg spec ~enable:vdd div_quot_d in
  let div_shift_d = wire 18 in
  let div_shift_q = reg spec ~enable:vdd div_shift_d in

  (* Saved intermediate results *)
  let mag_mod_d = wire 7 in
  let mag_mod_q = reg spec ~enable:vdd mag_mod_d in
  let q_posmag_d = wire 18 in
  let q_posmag_q = reg spec ~enable:vdd q_posmag_d in
  let q_term1_d = wire 18 in
  let q_term1_q = reg spec ~enable:vdd q_term1_d in
  let q_term2_d = wire 18 in
  let q_term2_q = reg spec ~enable:vdd q_term2_d in
  let next_pos_d = wire 10 in
  let next_pos_q = reg spec ~enable:vdd next_pos_d in

  let denom = of_int ~width:18 100 in

  (* Divider iteration (combinational next-state) *)
  let bring = msb div_shift_q in
  let rem_shift = concat_msb [ select div_rem_q 16 0; bring ] in
  let ge = rem_shift >=: denom in
  let rem_next = mux2 ge (rem_shift -: denom) rem_shift in
  let quot_next = concat_msb [ select div_quot_q 16 0; ge ] in
  let shift_next = concat_msb [ select div_shift_q 16 0; gnd ] in
  let cnt_next = div_cnt_q -: one 5 in
  let div_last = div_busy_q &: (div_cnt_q ==: one 5) in
  let div_done = div_last in
  let rem_after = mux2 div_busy_q rem_next div_rem_q in
  let quot_after = mux2 div_busy_q quot_next div_quot_q in

  let idle = phase_q ==: of_int ~width:3 0 in
  let kick = idle &: ~:div_busy_q &: i.instruction_valid in

  let phase1_done = div_done &: (phase_q ==: of_int ~width:3 1) in
  let phase2_done = div_done &: (phase_q ==: of_int ~width:3 2) in
  let phase3_done = div_done &: (phase_q ==: of_int ~width:3 3) in
  let phase4_done = div_done &: (phase_q ==: of_int ~width:3 4) in
  let apply = phase_q ==: of_int ~width:3 5 in

  (* Divider start conditions for each phase *)
  let start_phase2 = phase1_done in
  let start_phase3 = phase2_done &: ~:dir_q in
  let start_phase4 = phase3_done in
  let start_div = kick |: start_phase2 |: start_phase3 |: start_phase4 in

  let div_arg =
    let arg_kick = uresize i.instruction_mag 18 in
    let arg_phase2 =
      let mag_mod_100_18 = uresize rem_after 18 in
      mux2 dir_q
        (uresize position_q 18 +: mag_q)
        (uresize position_q 18 +: of_int ~width:18 100 -: mag_mod_100_18)
    in
    (* For left movement, count multiples of 100 in [pos-mag, pos-1].
       Use a large offset to keep the unsigned divider inputs non-negative.
    *)
    let offset = of_int ~width:18 65600 in
    let arg_phase3 = (uresize position_q 18 -: one 18) +: offset in
    let arg_phase4 = (uresize position_q 18 -: mag_q -: one 18) +: offset in
    mux2 kick arg_kick
      (mux2 start_phase2 arg_phase2 (mux2 start_phase3 arg_phase3 arg_phase4))
  in

  (* Drive divider state with priority: start_div > iterate > hold *)
  div_busy_d <== mux2 start_div vdd (mux2 div_last gnd div_busy_q);
  div_cnt_d <== mux2 start_div (of_int ~width:5 18) (mux2 div_busy_q cnt_next div_cnt_q);
  div_rem_d <== mux2 start_div (zero 18) (mux2 div_busy_q rem_next div_rem_q);
  div_quot_d <== mux2 start_div (zero 18) (mux2 div_busy_q quot_next div_quot_q);
  div_shift_d <== mux2 start_div div_arg (mux2 div_busy_q shift_next div_shift_q);

  (* Latch instruction on kick *)
  dir_d <== mux2 kick i.instruction_dir dir_q;
  mag_d <== mux2 kick (uresize i.instruction_mag 18) mag_q;

  (* Save intermediate results on division completion *)
  mag_mod_d <== mux2 phase1_done (uresize rem_after 7) mag_mod_q;
  next_pos_d <== mux2 phase2_done (uresize rem_after 10) next_pos_q;
  q_posmag_d <== mux2 phase2_done quot_after q_posmag_q;
  q_term1_d <== mux2 phase3_done quot_after q_term1_q;
  q_term2_d <== mux2 phase4_done quot_after q_term2_q;

  (* Phase transitions *)
  let phase_next =
    mux2 kick (of_int ~width:3 1)
      (mux2 phase1_done (of_int ~width:3 2)
         (mux2 (phase2_done &: dir_q) (of_int ~width:3 5)
            (mux2 start_phase3 (of_int ~width:3 3)
               (mux2 phase3_done (of_int ~width:3 4)
                  (mux2 phase4_done (of_int ~width:3 5)
                     (mux2 apply (of_int ~width:3 0) phase_q))))))
  in
  phase_d <== phase_next;

  (* Apply updates *)
  let zeros_left = q_term1_q -: q_term2_q in
  let zeros_passed = mux2 dir_q q_posmag_q zeros_left in
  let p1_inc = mux2 (next_pos_q ==:. 0) (one 32) (zero 32) in
  position_d <== mux2 apply next_pos_q position_q;
  part1_d <== mux2 apply (part1_q +: p1_inc) part1_q;
  part2_d <== mux2 apply (part2_q +: uresize zeros_passed 32) part2_q;

  { O.ready = idle
  ; part1_result = part1_q
  ; part2_result = part2_q
  ; position = position_q
  }
