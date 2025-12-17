open! Core
open Hardcaml
open Signal

(* Day 1 — Paper Option B: Deeply Pipelined High-Throughput Core

   Same external behavior as Option A, but with a 1-cycle pipeline stage on the
   arithmetic so the critical path is shorter.

   Throughput: 1 instruction/cycle.
   Latency: 1 cycle (effects apply one cycle after instruction_valid).
*)

module I = struct
  type 'a t =
    { clock : 'a
    ; clear : 'a
    ; instruction_valid : 'a
    ; direction : 'a
    ; magnitude : 'a [@bits 16]
    }
  [@@deriving sexp_of, hardcaml]
end

module O = struct
  type 'a t =
    { part1_result : 'a [@bits 32]
    ; part2_result : 'a [@bits 32]
    ; position : 'a [@bits 10]
    }
  [@@deriving sexp_of, hardcaml]
end

let div_100 = Day1_opt_a_minimal_streaming.div_100
let mod_100 = Day1_opt_a_minimal_streaming.mod_100

let create (i : _ I.t) =
  let spec = Reg_spec.create ~clock:i.clock ~clear:i.clear () in

  (* State (explicit next-state wires) *)
  let spec_pos = Reg_spec.override spec ~clear_to:(of_int ~width:10 50) in
  let position_d = wire 10 in
  let part1_d = wire 32 in
  let part2_d = wire 32 in

  let position_q = reg spec_pos ~enable:vdd position_d in
  let part1_q = reg spec ~enable:vdd part1_d in
  let part2_q = reg spec ~enable:vdd part2_d in

  (* Stage 1 registers (explicit wires so stage 0 can forward the pending update). *)
  let valid_1_d = wire 1 in
  let pos_1_d = wire 10 in
  let p1_inc_1_d = wire 32 in
  let p2_inc_1_d = wire 32 in

  let valid_1 = reg spec ~enable:vdd valid_1_d in
  let pos_1 = reg spec ~enable:i.instruction_valid pos_1_d in
  let p1_inc_1 = reg spec ~enable:i.instruction_valid p1_inc_1_d in
  let p2_inc_1 = reg spec ~enable:i.instruction_valid p2_inc_1_d in

  (* Forward the pending (previous-cycle) update so we can accept a new instruction every cycle. *)
  let position_fwd = mux2 valid_1 pos_1 position_q in

  (* Stage 0: compute next values combinationally *)
  let pos_18 = uresize position_fwd 18 in
  let mag_18 = uresize i.magnitude 18 in
  let c100_18 = of_int ~width:18 100 in

  let mag_mod_100 = mod_100 mag_18 in
  let mag_mod_100_10 = uresize mag_mod_100 10 in

  let next_pos_right_10 = uresize (mod_100 (pos_18 +: mag_18)) 10 in
  let next_pos_left_10 =
    uresize (mod_100 (pos_18 +: c100_18 -: uresize mag_mod_100_10 18)) 10
  in
  let next_pos_10 = mux2 i.direction next_pos_right_10 next_pos_left_10 in

  let is_zero_at_end = next_pos_10 ==:. 0 in
  let part1_inc = mux2 is_zero_at_end (one 32) (zero 32) in

  let zeros_right = div_100 (pos_18 +: mag_18) in
  let offset = of_int ~width:18 65600 in
  let term1_arg = (pos_18 -: one 18) +: offset in
  let term2_arg = (pos_18 -: mag_18 -: one 18) +: offset in
  let term1 = div_100 term1_arg in
  let term2 = div_100 term2_arg in
  let zeros_left = uresize (term1 -: term2) 16 in
  let zeros_passed = mux2 i.direction (uresize zeros_right 16) zeros_left in
  let part2_inc = uresize zeros_passed 32 in

  (* Drive stage 1 wires. *)
  valid_1_d <== i.instruction_valid;
  pos_1_d <== next_pos_10;
  p1_inc_1_d <== part1_inc;
  p2_inc_1_d <== part2_inc;

  (* Apply registered updates *)
  position_d <== mux2 valid_1 pos_1 position_q;
  part1_d <== mux2 valid_1 (part1_q +: p1_inc_1) part1_q;
  part2_d <== mux2 valid_1 (part2_q +: p2_inc_1) part2_q;

  { O.part1_result = part1_q
  ; part2_result = part2_q
  ; position = position_q
  }
