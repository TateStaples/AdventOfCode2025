open! Core
open Hardcaml
open Signal

(* Day 1 — Paper Option A: Minimal-Area Streaming Core

   Streaming interface: one instruction per cycle when instruction_valid=1.
   Keeps running state (position, part1 count, part2 count).

   This is the “do the obvious thing, but make the arithmetic hardware-friendly” option.
*)

module I = struct
  type 'a t =
    { clock : 'a
    ; clear : 'a
    ; instruction_valid : 'a
    ; direction : 'a (* 0 = Left, 1 = Right *)
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

let div_100 x =
  (* x is up to 18 bits. Compute x / 100 using fixed point multiplication.
     2^32 / 100 = 42949672.96 -> 42949673
  *)
  let inv = of_int ~width:32 42949673 in
  let x_50 = uresize x 50 in
  let inv_50 = uresize inv 50 in
  let prod = x_50 *: inv_50 in
  let res = srl prod 32 in
  uresize res 18

let mod_100 x =
  let d = div_100 x in
  let p = d *: of_int ~width:18 100 in
  x -: uresize p 18

let create (i : _ I.t) =
  let spec = Reg_spec.create ~clock:i.clock ~clear:i.clear () in

  (* Explicit next-state wires *)
  let position_d = wire 10 in
  let part1_d = wire 32 in
  let part2_d = wire 32 in

  (* Position resets to 50 *)
  let spec_pos = Reg_spec.override spec ~clear_to:(of_int ~width:10 50) in

  let position_q = reg spec_pos ~enable:vdd position_d in
  let part1_q = reg spec ~enable:vdd part1_d in
  let part2_q = reg spec ~enable:vdd part2_d in

  (* Arithmetic sizing *)
  let pos_18 = uresize position_q 18 in
  let mag_18 = uresize i.magnitude 18 in
  let c100_18 = of_int ~width:18 100 in

  (* Next position *)
  let mag_mod_100 = mod_100 mag_18 in
  let mag_mod_100_10 = uresize mag_mod_100 10 in

  let next_pos_right_10 = uresize (mod_100 (pos_18 +: mag_18)) 10 in
  let next_pos_left_10 =
    (* (pos + 100 - (mag mod 100)) mod 100 *)
    uresize (mod_100 (pos_18 +: c100_18 -: uresize mag_mod_100_10 18)) 10
  in

  let next_pos_10 = mux2 i.direction next_pos_right_10 next_pos_left_10 in

  (* Part 1: count times we land on 0 *)
  let is_zero_at_end = next_pos_10 ==:. 0 in
  let next_part1 = part1_q +: mux2 is_zero_at_end (one 32) (zero 32) in

  (* Part 2: count how many zeros we pass over *)
  let zeros_right = div_100 (pos_18 +: mag_18) in

  (* For left movement, count multiples of 100 in [pos-mag, pos-1].
     Add an offset to avoid underflow in unsigned arithmetic.
  *)
  let offset = of_int ~width:18 65600 in
  let term1_arg = (pos_18 -: one 18) +: offset in
  let term2_arg = (pos_18 -: mag_18 -: one 18) +: offset in
  let term1 = div_100 term1_arg in
  let term2 = div_100 term2_arg in
  let zeros_left = uresize (term1 -: term2) 16 in

  let zeros_passed = mux2 i.direction (uresize zeros_right 16) zeros_left in
  let next_part2 = part2_q +: uresize zeros_passed 32 in

  position_d <== mux2 i.instruction_valid next_pos_10 position_q;
  part1_d <== mux2 i.instruction_valid next_part1 part1_q;
  part2_d <== mux2 i.instruction_valid next_part2 part2_q;

  { O.part1_result = part1_q
  ; part2_result = part2_q
  ; position = position_q
  }
