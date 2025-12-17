open! Core
open Hardcaml
open Signal

(* Day 5 — Cafeteria

    Paper Option A: Minimal-Area Interval-Union Engine (Two-Pass)

    Assumptions (matches Rust reference behavior):
    - Ranges are presented sorted by (from,to).
    - IDs are presented sorted ascending.

    Interface:
    - Pulse [load]=1 for 1 cycle to clear accumulators/state.
    - Stream ranges while [range_ready]=1, asserting [range_last] on final range.
    - Then stream IDs while [id_ready]=1, asserting [id_last] on final id.

    Outputs:
    - [part2_result] = union length of merged ranges.
    - [part1_result] = number of ids that fall within the union.
*)

let max_merged = 256

module I = struct
   type 'a t =
      { clock : 'a
      ; clear : 'a
      ; load : 'a
      ; range_valid : 'a
      ; range_from : 'a [@bits 64]
      ; range_to : 'a [@bits 64] (* inclusive *)
      ; range_last : 'a
      ; id_valid : 'a
      ; id : 'a [@bits 64]
      ; id_last : 'a
      }
   [@@deriving sexp_of, hardcaml]
end

module O = struct
   type 'a t =
      { part1_result : 'a [@bits 64]
      ; part2_result : 'a [@bits 64]
      ; range_ready : 'a
      ; id_ready : 'a
      ; done_ : 'a
      ; phase : 'a [@bits 2]
      }
   [@@deriving sexp_of, hardcaml]
end

let u64 (x : Signal.t) = uresize x 64

module Phase = struct
   let ranges = of_int ~width:2 0
   let ids = of_int ~width:2 1
   let done_ = of_int ~width:2 2
end

let create (i : _ I.t) =
   let spec = Reg_spec.create ~clock:i.clock ~clear:i.clear () in

   (* Next wires (single-assignment style) *)
   let phase_next = wire 2 in
   let wptr_next = wire 8 in
   let merged_count_next = wire 8 in
   let have_cur_next = wire 1 in
   let cur_start_next = wire 64 in
   let cur_end_next = wire 64 in
   let part2_next = wire 64 in
   let part1_next = wire 64 in
   let mptr_next = wire 8 in
   let id_active_next = wire 1 in
   let id_latched_next = wire 64 in
   let id_last_reg_next = wire 1 in

   (* State regs *)
   let phase = reg spec ~enable:vdd phase_next in
   let wptr = reg spec ~enable:vdd wptr_next in
   let merged_count = reg spec ~enable:vdd merged_count_next in
   let have_cur = reg spec ~enable:vdd have_cur_next in
   let cur_start = reg spec ~enable:vdd cur_start_next in
   let cur_end = reg spec ~enable:vdd cur_end_next in
   let part2 = reg spec ~enable:vdd part2_next in
   let part1 = reg spec ~enable:vdd part1_next in
   let mptr = reg spec ~enable:vdd mptr_next in
   let id_active = reg spec ~enable:vdd id_active_next in
   let id_latched = reg spec ~enable:vdd id_latched_next in
   let id_last_reg = reg spec ~enable:vdd id_last_reg_next in

   (* Merged range memories (half-open) *)
   let starts_next = Array.init max_merged ~f:(fun _ -> wire 64) in
   let ends_next = Array.init max_merged ~f:(fun _ -> wire 64) in
   let starts = Array.map starts_next ~f:(reg spec ~enable:vdd) in
   let ends = Array.map ends_next ~f:(reg spec ~enable:vdd) in

   let in_ranges = phase ==: Phase.ranges in
   let in_ids = phase ==: Phase.ids in
   let in_done = phase ==: Phase.done_ in

   let range_ready = in_ranges in
   let id_ready = in_ids &: ~:id_active in

   let accept_range = range_ready &: i.range_valid in
   let accept_id = id_ready &: i.id_valid in

   let loading = i.load in

   (* ---------------- Range merge stage ---------------- *)
   let to_excl = u64 (i.range_to +: one 64) in
   let overlaps = i.range_from <: cur_end in
   let extend_end = mux2 (to_excl >: cur_end) to_excl cur_end in

   let is_first = accept_range &: ~:have_cur in
   let is_overlap = accept_range &: have_cur &: overlaps in
   let is_split = accept_range &: have_cur &: ~:overlaps in

   let cur_start_after_range = mux2 is_first i.range_from (mux2 is_split i.range_from cur_start) in
   let cur_end_after_range =
      mux2 is_first to_excl (mux2 is_overlap extend_end (mux2 is_split to_excl cur_end))
   in
   let have_cur_after_range = mux2 accept_range (one 1) have_cur in

   (* Emit previous range when split *)
   let push_prev = is_split in
   let prev_len = u64 (cur_end -: cur_start) in
   let wptr_after_prev = mux2 push_prev (wptr +: one 8) wptr in
   let part2_after_prev = mux2 push_prev (u64 (part2 +: prev_len)) part2 in

   (* Emit final current range at end of range stream *)
   let push_final = accept_range &: i.range_last in
   let final_start = cur_start_after_range in
   let final_end = cur_end_after_range in
   let final_len = u64 (final_end -: final_start) in

   let wptr_after_final = mux2 push_final (wptr_after_prev +: one 8) wptr_after_prev in
   let part2_after_final = mux2 push_final (u64 (part2_after_prev +: final_len)) part2_after_prev in

   (* ---------------- ID stage ---------------- *)
   let current_start = mux mptr (Array.to_list starts) in
   let current_end = mux mptr (Array.to_list ends) in

   let has_any_ranges = merged_count <>:. 0 in
   let merged_count_minus1 = mux2 has_any_ranges (merged_count -: one 8) (zero 8) in
   let has_more_ranges = mptr <: merged_count_minus1 in
   let advance = in_ids &: id_active &: has_any_ranges &: (id_latched >=: current_end) &: has_more_ranges in
   let resolved = in_ids &: id_active &: ~:advance in
   let in_range = has_any_ranges &: (id_latched >=: current_start) &: (id_latched <: current_end) in

   (* ---------------- Next-state assignments ---------------- *)
   phase_next <==
      mux2 loading Phase.ranges
         (mux2 (in_ranges &: push_final) Phase.ids (mux2 (resolved &: id_last_reg) Phase.done_ phase));

   wptr_next <== mux2 loading (zero 8) (mux2 in_ranges wptr_after_final wptr);
   merged_count_next <== mux2 loading (zero 8) (mux2 (in_ranges &: push_final) wptr_after_final merged_count);

   have_cur_next <== mux2 loading (zero 1) (mux2 in_ranges have_cur_after_range have_cur);
   cur_start_next <== mux2 loading (zero 64) (mux2 in_ranges cur_start_after_range cur_start);
   cur_end_next <== mux2 loading (zero 64) (mux2 in_ranges cur_end_after_range cur_end);
   part2_next <== mux2 loading (zero 64) (mux2 in_ranges part2_after_final part2);

   mptr_next <==
      mux2 loading (zero 8) (mux2 (in_ranges &: push_final) (zero 8) (mux2 advance (mptr +: one 8) mptr));

   id_latched_next <== mux2 loading (zero 64) (mux2 accept_id i.id id_latched);
   id_last_reg_next <== mux2 loading (zero 1) (mux2 accept_id i.id_last id_last_reg);

   id_active_next <==
      mux2 loading (zero 1) (mux2 accept_id (one 1) (mux2 resolved (zero 1) id_active));

   part1_next <== mux2 loading (zero 64) (mux2 (resolved &: in_range) (u64 (part1 +: one 64)) part1);

   (* Memories: hold, with optional writes for prev/final pushes *)
   Array.iteri starts_next ~f:(fun j w ->
         let hold = starts.(j) in
         let write_prev = in_ranges &: push_prev &: (wptr ==:. j) in
         let write_final = in_ranges &: push_final &: (wptr_after_prev ==:. j) in
         w <== mux2 write_prev cur_start (mux2 write_final final_start hold));
   Array.iteri ends_next ~f:(fun j w ->
         let hold = ends.(j) in
         let write_prev = in_ranges &: push_prev &: (wptr ==:. j) in
         let write_final = in_ranges &: push_final &: (wptr_after_prev ==:. j) in
         w <== mux2 write_prev cur_end (mux2 write_final final_end hold));

   { O.part1_result = part1
   ; part2_result = part2
   ; range_ready
   ; id_ready
   ; done_ = in_done
   ; phase
   }
