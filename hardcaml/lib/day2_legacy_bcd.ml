open! Core
open Hardcaml
open Signal

module I = struct
  type 'a t =
    { clock : 'a
    ; clear : 'a
    ; load : 'a
    ; start_bin : 'a [@bits 64]
    ; start_bcd : 'a [@bits 48] (* 12 digits *)
    ; end_bin : 'a [@bits 64]
    }
  [@@deriving sexp_of, hardcaml]
end

module O = struct
  type 'a t =
    { sum_p1 : 'a [@bits 64]
    ; sum_p2 : 'a [@bits 64]
    ; done_ : 'a
    ; current_bin : 'a [@bits 64] (* Debug *)
    }
  [@@deriving sexp_of, hardcaml]
end

(* BCD Incrementer *)
let bcd_incr bcd =
  let nibbles = split_lsb ~part_width:4 bcd in
  let rec ripple nibbles carry_in =
    match nibbles with
    | [] -> []
    | n :: rest ->
      let sum = uresize n 5 +: uresize carry_in 5 in
      let is_gt_9 = sum >: (of_int ~width:5 9) in
      let next_n = mux2 is_gt_9 (sum -: (of_int ~width:5 10)) sum in
      let next_carry = mux2 is_gt_9 (one 1) (zero 1) in
      (uresize next_n 4) :: ripple rest next_carry
  in
  let res_nibbles = ripple nibbles (one 1) in
  concat_lsb res_nibbles

(* Check Logic *)
let check_repetition ~part2 digits =
  (* digits is list of 4-bit signals, LSB first *)
  (* Returns a bit signal: 1 if invalid, 0 otherwise *)
  let is_nonzero x = x <>:. 0 in
  let len_is l =
    let upper_zeros =
      if l = 12 then one 1
      else
        let upper = List.drop digits l in
        List.reduce_exn (List.map upper ~f:(fun d -> d ==:. 0)) ~f:(&:)
    in
    let current_nonzero =
      if l = 0 then zero 1
      else is_nonzero (List.nth_exn digits (l - 1))
    in
    upper_zeros &: current_nonzero
  in

  let check_len_l l =
    if l < 2 then zero 1
    else
      let valid_periods =
        List.init (l / 2) ~f:(fun i -> i + 1)
        |> List.filter ~f:(fun p -> l % p = 0)
      in
      let check_period p =
        let checks =
          List.init (l - p) ~f:(fun i ->
            let d_i = List.nth_exn digits i in
            let d_ip = List.nth_exn digits (i + p) in
            d_i ==: d_ip)
        in
        List.reduce_exn checks ~f:(&:)
      in

      let periods_to_check =
        if part2 then valid_periods
        else List.filter valid_periods ~f:(fun p -> l / p = 2)
      in

      if List.is_empty periods_to_check then zero 1
      else List.reduce_exn (List.map periods_to_check ~f:check_period) ~f:(|:)
  in

  let len_checks =
    List.init 12 ~f:(fun i -> i + 1)
    |> List.map ~f:(fun l -> (len_is l) &: check_len_l l)
  in

  List.reduce_exn len_checks ~f:(|:)

let create (i : _ I.t) =
  let spec = Reg_spec.create ~clock:i.clock ~clear:i.clear () in

  let curr_bin = wire 64 in
  let curr_bcd = wire 48 in
  let sum_p1 = wire 64 in
  let sum_p2 = wire 64 in
  let done_wire = wire 1 in

  let curr_bin_reg = reg spec ~enable:(one 1) curr_bin in
  let curr_bcd_reg = reg spec ~enable:(one 1) curr_bcd in
  let sum_p1_reg = reg spec ~enable:(one 1) sum_p1 in
  let sum_p2_reg = reg spec ~enable:(one 1) sum_p2 in
  let done_reg = reg spec ~enable:(one 1) done_wire in

  let is_loading = i.load in
  let is_running = ~:is_loading &: ~:done_reg in

  let next_bin = curr_bin_reg +: one 64 in
  let next_bcd = bcd_incr curr_bcd_reg in

  let finished = curr_bin_reg >: i.end_bin in

  let digits = split_lsb ~part_width:4 curr_bcd_reg in
  let is_inv_p1 = check_repetition ~part2:false digits in
  let is_inv_p2 = check_repetition ~part2:true digits in

  let next_sum_p1 = sum_p1_reg +: mux2 is_inv_p1 curr_bin_reg (zero 64) in
  let next_sum_p2 = sum_p2_reg +: mux2 is_inv_p2 curr_bin_reg (zero 64) in

  curr_bin <== mux2 is_loading i.start_bin (mux2 is_running next_bin curr_bin_reg);
  curr_bcd <== mux2 is_loading i.start_bcd (mux2 is_running next_bcd curr_bcd_reg);

  sum_p1 <==
    mux2 is_loading (zero 64) (mux2 (is_running &: ~:finished) next_sum_p1 sum_p1_reg);
  sum_p2 <==
    mux2 is_loading (zero 64) (mux2 (is_running &: ~:finished) next_sum_p2 sum_p2_reg);

  done_wire <== mux2 is_loading (zero 1) (mux2 finished (one 1) done_reg);

  { O.sum_p1 = sum_p1_reg; sum_p2 = sum_p2_reg; done_ = done_reg; current_bin = curr_bin_reg }
