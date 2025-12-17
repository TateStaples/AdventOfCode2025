open! Core
open Hardcaml
open Signal

module I = struct
  type 'a t =
    { clock : 'a
    ; clear : 'a
    ; load : 'a
    ; pair_valid : 'a
    ; from_ : 'a [@bits 64]
    ; to_ : 'a [@bits 64]
    ; last : 'a
    }
  [@@deriving sexp_of, hardcaml]
end

module O = struct
  type 'a t =
    { sum_p1 : 'a [@bits 64]
    ; sum_p2 : 'a [@bits 64]
    ; ready : 'a
    ; done_ : 'a
    ; family_index : 'a [@bits 4] (* debug *)
    }
  [@@deriving sexp_of, hardcaml]
end

let families : (Int64.t * Int64.t * Int64.t * [ `First | `Second | `Third ]) array =
  let open Day2_families in
  let expand (tag : [ `First | `Second | `Third ]) (fs : Family.t list) =
    List.map fs ~f:(fun f -> Day2_families.Family.step f, Family.start f, Family.stop f, tag)
  in
  Array.of_list
    (expand `First first @ expand `Second second @ expand `Third third)

let total_families = Array.length families

let const64 (x : Int64.t) = of_int64 ~width:64 x
let u64 (x : Signal.t) = uresize x 64

let create (i : _ I.t) =
  let spec = Reg_spec.create ~clock:i.clock ~clear:i.clear () in

  let sum_first_w = wire 64 in
  let sum_second_w = wire 64 in
  let sum_third_w = wire 64 in

  let from_w = wire 64 in
  let to_w = wire 64 in
  let last_w = wire 1 in

  let running_w = wire 1 in
  let done_w = wire 1 in
  let family_index_w = wire 4 in

  let sum_first = reg spec ~enable:(one 1) sum_first_w in
  let sum_second = reg spec ~enable:(one 1) sum_second_w in
  let sum_third = reg spec ~enable:(one 1) sum_third_w in

  let from_r = reg spec ~enable:(one 1) from_w in
  let to_r = reg spec ~enable:(one 1) to_w in
  let last_r = reg spec ~enable:(one 1) last_w in

  let running = reg spec ~enable:(one 1) running_w in
  let done_ = reg spec ~enable:(one 1) done_w in
  let family_index = reg spec ~enable:(one 1) family_index_w in

  let ready = ~: running &: ~: done_ in
  let accept_pair = i.pair_valid &: ready in

  (* Select constants for current family index. *)
  let step_s, start_s, stop_s, is_first, is_second, is_third =
    let idx = family_index in
    let default_step, default_start, default_stop, default_tag = families.(0) in
    let default_f, default_s, default_t =
      match default_tag with
      | `First -> one 1, zero 1, zero 1
      | `Second -> zero 1, one 1, zero 1
      | `Third -> zero 1, zero 1, one 1
    in
    Array.foldi
      families
      ~init:
        ( const64 default_step
        , const64 default_start
        , const64 default_stop
        , default_f
        , default_s
        , default_t )
      ~f:(fun k (step_acc, start_acc, stop_acc, f_acc, s_acc, t_acc) (step, start, stop, tag) ->
        let sel = idx ==:. k in
        let f, s, t =
          match tag with
          | `First -> one 1, zero 1, zero 1
          | `Second -> zero 1, one 1, zero 1
          | `Third -> zero 1, zero 1, one 1
        in
        ( mux2 sel (const64 step) step_acc
        , mux2 sel (const64 start) start_acc
        , mux2 sel (const64 stop) stop_acc
        , mux2 sel f f_acc
        , mux2 sel s s_acc
        , mux2 sel t t_acc ))
  in

  let next_multiple_of ~x ~step =
    (* ceil(x/step) * step *)
    let step_minus_1 = u64 (step -: one 64) in
    let numerator = u64 (x +: step_minus_1) in
    let div = Division.udiv ~numerator ~denominator:step in
    u64 (div *: step)
  in

  let lower =
    let lower0 = next_multiple_of ~x:from_r ~step:step_s in
    mux2 (lower0 >: start_s) lower0 start_s
  in
  let upper = mux2 (to_r <: stop_s) to_r stop_s in

  let in_range = lower <=: upper in

  let n = Division.udiv ~numerator:(u64 (upper -: lower)) ~denominator:step_s in
  let n_plus_1 = u64 (n +: one 64) in
  let triangular =
    Division.udiv
      ~numerator:(u64 (n *: (u64 (n +: one 64))))
      ~denominator:(of_int ~width:64 2)
  in
  let addend =
    let base = u64 (lower *: n_plus_1) in
    let extra = u64 (step_s *: triangular) in
    u64 (base +: extra)
  in

  let add_first = mux2 (in_range &: is_first) addend (zero 64) in
  let add_second = mux2 (in_range &: is_second) addend (zero 64) in
  let add_third = mux2 (in_range &: is_third) addend (zero 64) in

  let family_last = family_index ==:. (total_families - 1) in

  (* Update regs via wires *)
  let next_running =
    mux2 i.load (zero 1) (mux2 accept_pair (one 1) (mux2 family_last (zero 1) running))
  in

  (* family index increments while running; resets on accept_pair *)
  let next_family_index =
    let inc = family_index +: one 4 in
    mux2 i.load (zero 4) (mux2 accept_pair (zero 4) (mux2 running inc family_index))
  in

  sum_first_w <==
    mux2 i.load (zero 64)
      (mux2 (running &: ~: done_) (u64 (sum_first +: add_first)) sum_first);
  sum_second_w <==
    mux2 i.load (zero 64)
      (mux2 (running &: ~: done_) (u64 (sum_second +: add_second)) sum_second);
  sum_third_w <==
    mux2 i.load (zero 64)
      (mux2 (running &: ~: done_) (u64 (sum_third +: add_third)) sum_third);

  from_w <== mux2 i.load (zero 64) (mux2 accept_pair i.from_ from_r);
  to_w <== mux2 i.load (zero 64) (mux2 accept_pair i.to_ to_r);
  last_w <== mux2 i.load (zero 1) (mux2 accept_pair i.last last_r);

  running_w <== next_running;
  family_index_w <== next_family_index;
  (* done updates only when finishing last family of last pair *)
  done_w <==
    mux2 i.load (zero 1)
      (mux2 (running &: family_last &: last_r) (one 1) done_);

  let sum_p1 = sum_first in
  let sum_p2 = u64 (sum_first +: sum_second -: sum_third) in

  { O.sum_p1; sum_p2; ready; done_ = done_; family_index }
