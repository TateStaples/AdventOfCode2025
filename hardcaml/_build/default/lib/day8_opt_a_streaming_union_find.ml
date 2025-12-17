open! Core
open Hardcaml
open Signal

(* Day 8 — Playground

   Option A: Host-provided sorted edge stream + on-chip union-find (bounded).

   This mirrors the Rust structure:
   - The heavy work (pair generation + bucketing + sorting by distance) is assumed to be done
     off-chip; this module consumes edges in non-decreasing distance order.
   - Part 1: after consuming the Part1 edge stream, compute the product of the three largest
     connected-component sizes.
   - Part 2: consume the Part2 edge stream until the graph becomes connected; output x0[i]*x0[j]
     for the edge that first achieves full connectivity.

   This is a bounded accelerator intended for validation and small-N operation.
*)

let max_n = 256

module I = struct
  type 'a t =
    { clock : 'a
    ; clear : 'a
    ; load : 'a
    ; n_nodes : 'a [@bits 8]
    ; x0_valid : 'a
    ; x0_value : 'a [@bits 32]
    ; x0_last : 'a
    ; edge_valid : 'a
    ; edge_i : 'a [@bits 8]
    ; edge_j : 'a [@bits 8]
    ; edge_last : 'a
    ; edge_phase : 'a (* 0=part1, 1=part2 *)
    }
  [@@deriving sexp_of, hardcaml]
end

module O = struct
  type 'a t =
    { x0_ready : 'a
    ; edge_ready : 'a
    ; done_ : 'a
    ; part1_result : 'a [@bits 64]
    ; part2_result : 'a [@bits 64]
    ; state : 'a [@bits 3]
    }
  [@@deriving sexp_of, hardcaml]
end

let u64 x = uresize x 64

module State = struct
  let load_x0 = of_int ~width:3 0
  let init_uf1 = of_int ~width:3 1
  let edges_p1 = of_int ~width:3 2
  let scan_p1 = of_int ~width:3 3
  let init_uf2 = of_int ~width:3 4
  let edges_p2 = of_int ~width:3 5
  let done_ = of_int ~width:3 6
end

let rec find_k ~k ~parent_at idx = if k = 0 then idx else find_k ~k:(k - 1) ~parent_at (parent_at idx)

let create (i : _ I.t) : _ O.t =
  let spec = Reg_spec.create ~clock:i.clock ~clear:i.clear () in

  let state_next = wire 3 in
  let x0_wptr_next = wire 8 in
  let init_ptr_next = wire 8 in
  let scan_ptr_next = wire 8 in
  let part1_next = wire 64 in
  let part2_next = wire 64 in
  let top1_next = wire 16 in
  let top2_next = wire 16 in
  let top3_next = wire 16 in

  let state = reg spec ~enable:vdd state_next in
  let x0_wptr = reg spec ~enable:vdd x0_wptr_next in
  let init_ptr = reg spec ~enable:vdd init_ptr_next in
  let scan_ptr = reg spec ~enable:vdd scan_ptr_next in
  let part1 = reg spec ~enable:vdd part1_next in
  let part2 = reg spec ~enable:vdd part2_next in
  let top1 = reg spec ~enable:vdd top1_next in
  let top2 = reg spec ~enable:vdd top2_next in
  let top3 = reg spec ~enable:vdd top3_next in

  (* x0 memory *)
  let x0_next = Array.init max_n ~f:(fun _ -> wire 32) in
  let x0 = Array.map x0_next ~f:(reg spec ~enable:vdd) in

  (* union-find memories *)
  let parent_next = Array.init max_n ~f:(fun _ -> wire 8) in
  let size_next = Array.init max_n ~f:(fun _ -> wire 16) in
  let parent = Array.map parent_next ~f:(reg spec ~enable:vdd) in
  let size = Array.map size_next ~f:(reg spec ~enable:vdd) in

  let in_load_x0 = state ==: State.load_x0 in
  let in_init1 = state ==: State.init_uf1 in
  let in_edges_p1 = state ==: State.edges_p1 in
  let in_scan = state ==: State.scan_p1 in
  let in_init2 = state ==: State.init_uf2 in
  let in_edges_p2 = state ==: State.edges_p2 in
  let in_done = state ==: State.done_ in

  let x0_ready = in_load_x0 in
  let edge_ready = (in_edges_p1 &: ~:(i.edge_phase)) |: (in_edges_p2 &: i.edge_phase) in

  let accept_x0 = x0_ready &: i.x0_valid in
  let accept_edge = edge_ready &: i.edge_valid in

  (* parent/size lookup helpers *)
  let parent_at idx = mux idx (Array.to_list parent) in
  let size_at idx = mux idx (Array.to_list size) in
  let x0_at idx = mux idx (Array.to_list x0) in

  let find idx = find_k ~k:8 ~parent_at idx in

  (* Edge union combinational (applied on accept_edge) *)
  let rx = find i.edge_i in
  let ry = find i.edge_j in
  let same = rx ==: ry in

  let sx = uresize (size_at rx) 16 in
  let sy = uresize (size_at ry) 16 in
  let x_ge_y = sx >=: sy in

  let new_root = mux2 x_ge_y rx ry in
  let child = mux2 x_ge_y ry rx in
  let new_size = uresize (sx +: sy) 16 in

  let size_after_union = mux2 same sx new_size in

  let connected = accept_edge &: ~:same &: (size_after_union ==: uresize i.n_nodes 16) in

  (* Scan for top-3 component sizes *)
  let is_root_scan = mux scan_ptr (List.init max_n ~f:(fun j -> parent.(j) ==:. j)) in
  let size_scan = uresize (mux scan_ptr (Array.to_list size)) 16 in

  let cand = mux2 is_root_scan size_scan (zero 16) in
  let gt1 = cand >: top1 in
  let gt2 = cand >: top2 in
  let gt3 = cand >: top3 in

  let top1_after = mux2 gt1 cand top1 in
  let top2_after = mux2 gt1 top1 (mux2 gt2 cand top2) in
  let top3_after = mux2 gt1 top2 (mux2 gt2 top2 (mux2 gt3 cand top3)) in

  (* Union-find init passes *)
  let do_init = in_init1 |: in_init2 in
  let init_done = do_init &: (init_ptr ==: i.n_nodes) in

  (* x0 memory write *)
  Array.iteri x0_next ~f:(fun j w ->
      let hold = x0.(j) in
      let write = accept_x0 &: (x0_wptr ==:. j) in
      w <== mux2 i.load (zero 32) (mux2 write i.x0_value hold));

  Array.iteri parent_next ~f:(fun j w ->
      let hold = parent.(j) in
      let init_write = do_init &: (init_ptr ==:. j) in
      let union_write = accept_edge &: ~:same &: (child ==:. j) in
      let v = mux2 init_write (of_int ~width:8 j) (mux2 union_write new_root hold) in
      w <== mux2 i.load (zero 8) v);

  Array.iteri size_next ~f:(fun j w ->
      let hold = size.(j) in
      let init_write = do_init &: (init_ptr ==:. j) in
      let union_write = accept_edge &: ~:same &: (new_root ==:. j) in
      let v = mux2 init_write (one 16) (mux2 union_write new_size hold) in
      w <== mux2 i.load (zero 16) v);

  (* Scan stage bookkeeping *)
  let enter_scan = in_edges_p1 &: accept_edge &: i.edge_last in
  let scan_done = in_scan &: (scan_ptr ==: i.n_nodes) in

  (* Part 1 latch at end of scan *)
  let p1_prod = u64 (u64 (uresize top1 64 *: uresize top2 64) *: uresize top3 64) in

  (* Part 2 latch on connectivity *)
  let x0_i = uresize (x0_at i.edge_i) 64 in
  let x0_j = uresize (x0_at i.edge_j) 64 in
  let p2_val = u64 (x0_i *: x0_j) in

  (* Next-state logic (single-assignment) *)
  let state_d =
    mux2 i.load State.load_x0
      (mux2 (state ==: State.load_x0 &: accept_x0 &: i.x0_last) State.init_uf1
         (mux2 (in_init1 &: init_done) State.edges_p1
            (mux2 (in_edges_p1 &: accept_edge &: i.edge_last) State.scan_p1
               (mux2 (in_scan &: (scan_ptr ==: i.n_nodes)) State.init_uf2
                  (mux2 (in_init2 &: init_done) State.edges_p2
                     (mux2 (in_edges_p2 &: connected) State.done_
                        (mux2 (in_edges_p2 &: accept_edge &: i.edge_last) State.done_ state)))))))
  in

  let x0_wptr_d =
    let base = mux2 i.load (zero 8) x0_wptr in
    mux2 accept_x0 (base +: one 8) base
  in

  let init_ptr_d =
    let base = mux2 i.load (zero 8) init_ptr in
    let base = mux2 (state ==: State.load_x0 &: accept_x0 &: i.x0_last) (zero 8) base in
    let base = mux2 scan_done (zero 8) base in
    mux2 (do_init &: ~:init_done) (init_ptr +: one 8) base
  in

  let scan_ptr_d =
    let base = mux2 i.load (zero 8) scan_ptr in
    let base = mux2 enter_scan (zero 8) base in
    mux2 in_scan (scan_ptr +: one 8) base
  in

  let top1_d =
    let base = mux2 i.load (zero 16) top1 in
    let base = mux2 enter_scan (zero 16) base in
    mux2 in_scan top1_after base
  in

  let top2_d =
    let base = mux2 i.load (zero 16) top2 in
    let base = mux2 enter_scan (zero 16) base in
    mux2 in_scan top2_after base
  in

  let top3_d =
    let base = mux2 i.load (zero 16) top3 in
    let base = mux2 enter_scan (zero 16) base in
    mux2 in_scan top3_after base
  in

  let part1_d =
    let base = mux2 i.load (zero 64) part1 in
    mux2 scan_done p1_prod base
  in

  let part2_d =
    let base = mux2 i.load (zero 64) part2 in
    mux2 connected p2_val base
  in

  state_next <== state_d;
  x0_wptr_next <== x0_wptr_d;
  init_ptr_next <== init_ptr_d;
  scan_ptr_next <== scan_ptr_d;
  top1_next <== top1_d;
  top2_next <== top2_d;
  top3_next <== top3_d;
  part1_next <== part1_d;
  part2_next <== part2_d;

  { O.x0_ready
  ; edge_ready
  ; done_ = in_done
  ; part1_result = part1
  ; part2_result = part2
  ; state
  }
