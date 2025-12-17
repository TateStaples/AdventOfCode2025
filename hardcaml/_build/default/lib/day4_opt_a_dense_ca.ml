open! Core
open Hardcaml
open Hardcaml.Signal

(* Day 4 — Printing Department

   Paper Option A: Dense Iterative “Cellular Automaton” (Simple, Parallel)

   Computes, each iteration, all rolls (@) that have <4 neighbors, removes them
   simultaneously, and repeats until convergence.

   Because removability is monotonic (removing rolls only decreases neighbor
   counts), this produces the same fixed-point total as the event-queue peeling
   reference.
*)

let rows = 139
let cols = 139
let grid_size = rows * cols

module I = struct
  type 'a t =
    { clock : 'a
    ; clear : 'a
    ; start : 'a
    ; grid_in : 'a [@bits grid_size]
    }
  [@@deriving sexp_of, hardcaml]
end

module O = struct
  type 'a t =
    { part1_result : 'a [@bits 64]
    ; part2_result : 'a [@bits 64]
    ; done_ : 'a
    ; debug_count : 'a [@bits 64]
    ; active_out : 'a
    ; grid_popcount : 'a [@bits 64]
    }
  [@@deriving sexp_of, hardcaml]
end

let create (i : _ I.t) =
  let spec = Reg_spec.create ~clock:i.clock ~clear:i.clear () in

  let next_grid_wire = wire grid_size in
  let next_accumulator_wire = wire 64 in
  let next_active_wire = wire 1 in
  let next_first_cycle_wire = wire 1 in
  let next_part1_res_wire = wire 64 in

  let grid = reg spec ~enable:vdd next_grid_wire in
  let accumulator = reg spec ~enable:vdd next_accumulator_wire in
  let active = reg spec ~enable:vdd next_active_wire in
  let first_cycle = reg spec ~enable:vdd next_first_cycle_wire in
  let part1_res = reg spec ~enable:vdd next_part1_res_wire in

  let get_cell g r c =
    if r < 0 || r >= rows || c < 0 || c >= cols then gnd else bit g (r * cols + c)
  in

  let next_grid_bits = Array.init grid_size ~f:(fun _ -> wire 1) in
  let removable_bits = Array.init grid_size ~f:(fun _ -> wire 1) in

  for r = 0 to rows - 1 do
    for c = 0 to cols - 1 do
      let idx = r * cols + c in
      let current = get_cell grid r c in

      let neighbors =
        [ get_cell grid (r - 1) (c - 1)
        ; get_cell grid (r - 1) c
        ; get_cell grid (r - 1) (c + 1)
        ; get_cell grid r (c - 1)
        ; get_cell grid r (c + 1)
        ; get_cell grid (r + 1) (c - 1)
        ; get_cell grid (r + 1) c
        ; get_cell grid (r + 1) (c + 1)
        ]
        |> List.map ~f:(fun x -> uresize x 4)
        |> List.reduce_exn ~f:(+:)
      in

      let is_removable = current &: (neighbors <: of_int ~width:(width neighbors) 4) in

      removable_bits.(idx) <== is_removable;
      next_grid_bits.(idx) <== (current &: ~:is_removable)
    done
  done;

  let removable_list = Array.to_list removable_bits in
  let removable_count = popcount (concat_lsb removable_list) in

  let calculated_next_grid = Array.to_list next_grid_bits |> concat_lsb in

  next_active_wire <== mux2 i.start vdd (mux2 (removable_count ==:. 0) gnd active);

  next_accumulator_wire <==
    mux2 i.start (of_int ~width:64 0)
      (mux2 active (accumulator +: uresize removable_count 64) accumulator);

  next_first_cycle_wire <== mux2 i.start vdd gnd;

  next_part1_res_wire <==
    mux2 i.start (of_int ~width:64 0)
      (mux2 (active &: first_cycle) (uresize removable_count 64) part1_res);

  next_grid_wire <== mux2 i.start i.grid_in calculated_next_grid;

  { O.part1_result = part1_res
  ; part2_result = accumulator
  ; done_ = ~:active
  ; debug_count = uresize removable_count 64
  ; active_out = active
  ; grid_popcount = uresize (popcount grid) 64
  }
