open! Core
open Hardcaml
open Signal

(* Day 1 — Paper Option C: Parallel Reduction Tree (fixed 8-leaf demo)

   This module matches the “Option C (Parallel, 8-leaf)” style used in the papers:
   it takes 8 instructions at once and produces the resulting position and counts
   for a given starting position.

   This is intended for synthesis/tapeout demonstration (TinyTapeout-friendly scale).
*)

module Chunk = struct
  type 'a t =
    { total_rotation_mod100 : 'a [@bits 7]
    ; crossings : 'a array [@length 100] [@bits 16]
    }
  [@@deriving sexp_of, hardcaml]
end

module I = struct
  type 'a t =
    { clock : 'a
    ; clear : 'a
    ; start : 'a
    ; directions : 'a array [@length 8]
    ; magnitudes : 'a array [@length 8] [@bits 16]
    ; start_pos : 'a [@bits 7] (* 0..99 *)
    }
  [@@deriving sexp_of, hardcaml]
end

module O = struct
  type 'a t =
    { done_ : 'a
    ; end_pos : 'a [@bits 7]
    ; crossings : 'a [@bits 16]
    }
  [@@deriving sexp_of, hardcaml]
end

let add_mod100_7 a b =
  let sum = uresize a 8 +: uresize b 8 in
  let ge100 = sum >=: of_int ~width:8 100 in
  uresize (mux2 ge100 (sum -: of_int ~width:8 100) sum) 7

let mod100_16 x =
  let _, r = Division.udivmod ~numerator:x ~denominator:(of_int ~width:16 100) in
  r

let mod100_7 x =
  let x8 = uresize x 8 in
  let ge100 = x8 >=: of_int ~width:8 100 in
  uresize (mux2 ge100 (x8 -: of_int ~width:8 100) x8) 7

let chunk_of_instruction ~clock ~enable ~direction ~magnitude =
  let spec = Reg_spec.create ~clock () in
  let mag16 = uresize magnitude 16 in
  let mag_mod100_7 = uresize (mod100_16 mag16) 7 in
  let rot_mod100_7 =
    mux2 direction
      mag_mod100_7
      (mod100_7 (of_int ~width:8 100 -: uresize mag_mod100_7 8))
  in
  let crossings =
    Array.init 100 ~f:(fun start_pos ->
      let start = of_int ~width:16 start_pos in
      let crosses_right =
        let q =
          Division.udiv ~numerator:(start +: mag16) ~denominator:(of_int ~width:16 100)
        in
        uresize q 16
      in
      let crosses_left =
        (* Rust formula: reversed = (100 - dial) % 100; crossings = (reversed + amount) / 100 *)
        let reversed = 
          if start_pos = 0 then zero 16 
          else of_int ~width:16 (100 - start_pos) 
        in
        let q = Division.udiv ~numerator:(reversed +: mag16) ~denominator:(of_int ~width:16 100) in
        uresize q 16
      in
      reg spec ~enable (mux2 direction crosses_right crosses_left))
  in
  { Chunk.total_rotation_mod100 = reg spec ~enable rot_mod100_7; crossings }

let merge_chunks ~clock ~enable (c1 : _ Chunk.t) (c2 : _ Chunk.t) =
  let spec = Reg_spec.create ~clock () in
  let total_rotation_mod100 =
    reg spec ~enable (add_mod100_7 c1.total_rotation_mod100 c2.total_rotation_mod100)
  in
  let crossings =
    Array.init 100 ~f:(fun start_pos ->
      let start = of_int ~width:16 start_pos in
      let crossings1 = c1.crossings.(start_pos) in
      let intermediate_mod100 =
        add_mod100_7 (uresize start 7) c1.total_rotation_mod100
      in
      let idx = intermediate_mod100 in
      let crossings2 = mux idx (Array.to_list c2.crossings) in
      reg spec ~enable (crossings1 +: crossings2))
  in
  { Chunk.total_rotation_mod100; crossings }

let create (i : _ I.t) =
  let spec = Reg_spec.create ~clock:i.clock ~clear:i.clear () in

  (* Propagate enable through pipeline stages *)
  let enable_0 = i.start in
  let enable_1 = reg spec ~enable:vdd enable_0 in
  let enable_2 = reg spec ~enable:vdd enable_1 in
  let enable_3 = reg spec ~enable:vdd enable_2 in

  let chunks =
    Array.init 8 ~f:(fun k ->
      chunk_of_instruction
        ~clock:i.clock
        ~enable:enable_0
        ~direction:i.directions.(k)
        ~magnitude:i.magnitudes.(k))
  in

  let m01 = merge_chunks ~clock:i.clock ~enable:enable_1 chunks.(0) chunks.(1) in
  let m23 = merge_chunks ~clock:i.clock ~enable:enable_1 chunks.(2) chunks.(3) in
  let m45 = merge_chunks ~clock:i.clock ~enable:enable_1 chunks.(4) chunks.(5) in
  let m67 = merge_chunks ~clock:i.clock ~enable:enable_1 chunks.(6) chunks.(7) in

  let m0123 = merge_chunks ~clock:i.clock ~enable:enable_2 m01 m23 in
  let m4567 = merge_chunks ~clock:i.clock ~enable:enable_2 m45 m67 in

  let m_all = merge_chunks ~clock:i.clock ~enable:enable_3 m0123 m4567 in

  let start_pos_16 = uresize i.start_pos 16 in
  let end_pos_7 = add_mod100_7 (uresize start_pos_16 7) m_all.total_rotation_mod100 in
  let crossings = mux i.start_pos (Array.to_list m_all.crossings) in

  (* Pipeline has 4 levels: chunks(1) + merge01(1) + merge0123(1) + merge_all(1) = 4 cycles *)
  let done_4 = reg spec ~enable:vdd enable_3 in

  { O.done_ = done_4
  ; end_pos = end_pos_7
  ; crossings
  }
