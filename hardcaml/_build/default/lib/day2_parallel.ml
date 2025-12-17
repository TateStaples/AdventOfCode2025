(* Massively Parallel Day 2 Solution using Range Partitioning
   
   This design achieves massive speedup by:
   1. Partitioning the input ranges into smaller sub-ranges
   2. Processing each sub-range in parallel using dedicated checkers
   3. Using tree reduction to sum all the results
   
   Key Optimizations:
   - Each checker processes a small range (e.g., 1000 numbers) in parallel
   - Pattern matching logic is replicated per checker
   - Results are combined using a logarithmic adder tree
   
   For a range of N numbers with P parallel checkers:
   - Sequential: N cycles
   - Parallel: ceil(N/P) + log2(P) cycles
*)

open! Core
open Hardcaml
open Signal

(* Check if a number (in BCD form) is invalid according to part1 or part2 rules *)
module Pattern_Checker = struct
  (* Check if BCD digits form a repeated pattern *)
  let check_repetition ~part2 digits =
    (* digits is list of 4-bit signals, LSB first *)
    (* Returns a bit signal: 1 if invalid, 0 otherwise *)
    
    (* Determine length *)
    let len_is l = 
      let upper_zeros = 
        if l = 12 then one 1 
        else 
          let upper = List.drop digits l in
          List.reduce_exn (List.map upper ~f:(fun d -> d ==:. 0)) ~f:(&:)
      in
      let current_nonzero = 
        if l = 0 then zero 1
        else (List.nth_exn digits (l-1)) <>:. 0
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
              d_i ==: d_ip
            )
          in
          List.reduce_exn checks ~f:(&:)
        in
        
        let periods_to_check = 
          if part2 then valid_periods
          else List.filter valid_periods ~f:(fun p -> l / p = 2)
        in
        
        if List.is_empty periods_to_check then zero 1
        else
          List.reduce_exn (List.map periods_to_check ~f:check_period) ~f:(|:)
    in
    
    let len_checks = 
      List.init 12 ~f:(fun i -> i + 1)
      |> List.map ~f:(fun l -> (len_is l) &: (check_len_l l))
    in
    
    List.reduce_exn len_checks ~f:(|:)
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
      (uresize next_n 4) :: (ripple rest next_carry)
  in
  let res_nibbles = ripple nibbles (one 1) in
  concat_lsb res_nibbles

(* Single parallel checker - processes a sub-range *)
module Range_Checker = struct
  module I = struct
    type 'a t =
      { clock : 'a
      ; clear : 'a
      ; start : 'a  (* Start processing *)
      ; start_bin : 'a [@bits 64]
      ; start_bcd : 'a [@bits 48]
      ; count : 'a [@bits 32]  (* How many numbers to check *)
      }
    [@@deriving sexp_of, hardcaml]
  end

  module O = struct
    type 'a t =
      { sum_p1 : 'a [@bits 64]
      ; sum_p2 : 'a [@bits 64]
      ; done_ : 'a
      }
    [@@deriving sexp_of, hardcaml]
  end

  let create (i : _ I.t) =
    let spec = Reg_spec.create ~clock:i.clock ~clear:i.clear () in
    
    let curr_bin = wire 64 in
    let curr_bcd = wire 48 in
    let counter = wire 32 in
    let sum_p1 = wire 64 in
    let sum_p2 = wire 64 in
    let done_wire = wire 1 in
    
    let curr_bin_reg = reg spec ~enable:(one 1) curr_bin in
    let curr_bcd_reg = reg spec ~enable:(one 1) curr_bcd in
    let counter_reg = reg spec ~enable:(one 1) counter in
    let sum_p1_reg = reg spec ~enable:(one 1) sum_p1 in
    let sum_p2_reg = reg spec ~enable:(one 1) sum_p2 in
    let done_reg = reg spec ~enable:(one 1) done_wire in
    
    (* State machine *)
    let is_idle = done_reg in
    let is_starting = i.start &: is_idle in
    let is_running = ~: is_idle &: (counter_reg <: i.count) in
    
    (* Next values *)
    let next_bin = curr_bin_reg +: (one 64) in
    let next_bcd = bcd_incr curr_bcd_reg in
    let next_counter = counter_reg +: (one 32) in
    
    (* Check current number *)
    let digits = split_lsb ~part_width:4 curr_bcd_reg in
    let is_inv_p1 = Pattern_Checker.check_repetition ~part2:false digits in
    let is_inv_p2 = Pattern_Checker.check_repetition ~part2:true digits in
    
    let next_sum_p1 = sum_p1_reg +: (mux2 is_inv_p1 curr_bin_reg (zero 64)) in
    let next_sum_p2 = sum_p2_reg +: (mux2 is_inv_p2 curr_bin_reg (zero 64)) in
    
    (* Update logic *)
    curr_bin <== mux2 is_starting i.start_bin (mux2 is_running next_bin curr_bin_reg);
    curr_bcd <== mux2 is_starting i.start_bcd (mux2 is_running next_bcd curr_bcd_reg);
    counter <== mux2 is_starting (zero 32) (mux2 is_running next_counter counter_reg);
    
    sum_p1 <== mux2 is_starting (zero 64) (mux2 is_running next_sum_p1 sum_p1_reg);
    sum_p2 <== mux2 is_starting (zero 64) (mux2 is_running next_sum_p2 sum_p2_reg);
    
    let finished = counter_reg >=: i.count in
    done_wire <== mux2 is_starting (zero 1) (mux2 finished (one 1) done_reg);
    
    { O.sum_p1 = sum_p1_reg
    ; O.sum_p2 = sum_p2_reg
    ; O.done_ = done_reg
    }
end

(* Parallel tree adder for combining results *)
module Tree_Adder = struct
  (* Add N pairs of 64-bit numbers using a tree structure *)
  (* Latency: ceil(log2 N) cycles *)
  
  module I = struct
    type 'a t =
      { clock : 'a
      ; values : 'a array [@length 64] [@bits 64]  (* Values to sum *)
      ; start : 'a
      }
    [@@deriving sexp_of, hardcaml]
  end

  module O = struct
    type 'a t =
      { sum : 'a [@bits 64]
      ; done_ : 'a
      }
    [@@deriving sexp_of, hardcaml]
  end

  let create (i : _ I.t) =
    let spec = Reg_spec.create ~clock:i.clock () in
    
    (* Build tree levels *)
    let rec build_tree_level inputs =
      let n = Array.length inputs in
      if n = 1 then
        inputs.(0)
      else
        let pairs = n / 2 in
        let has_odd = n mod 2 = 1 in
        
        let sums = Array.init pairs ~f:(fun j ->
          reg spec ~enable:(one 1) (inputs.(2*j) +: inputs.(2*j + 1))
        ) in
        
        let next_level = 
          if has_odd then
            Array.append sums [| reg spec ~enable:(one 1) inputs.(n-1) |]
          else
            sums
        in
        build_tree_level next_level
    in
    
    let final_sum = build_tree_level i.values in
    
    (* Calculate tree depth for done signal *)
    let depth = Int.ceil_log2 (Array.length i.values) in
    let done_signal = 
      let rec delay sig_ count =
        if count = 0 then sig_
        else delay (reg spec ~enable:(one 1) sig_) (count - 1)
      in
      delay i.start depth
    in
    
    { O.sum = final_sum
    ; O.done_ = done_signal
    }
end

(* Top-level parallel processor *)
module Parallel_Processor = struct
  module I = struct
    type 'a t =
      { clock : 'a
      ; clear : 'a
      ; start : 'a
      ; range_low : 'a [@bits 64]
      ; range_high : 'a [@bits 64]
      ; num_checkers : 'a [@bits 8]  (* How many parallel checkers to use *)
      }
    [@@deriving sexp_of, hardcaml]
  end

  module O = struct
    type 'a t =
      { sum_p1 : 'a [@bits 64]
      ; sum_p2 : 'a [@bits 64]
      ; done_ : 'a
      ; checkers_done : 'a [@bits 64]  (* Debug: which checkers finished *)
      }
    [@@deriving sexp_of, hardcaml]
  end

  let create ~num_checkers (i : _ I.t) =
    (* Create N parallel range checkers *)
    (* Each checker gets: start + k*(range_size/N), count = range_size/N *)
    
    (* For simplicity, assume we have a fixed number of checkers *)
    (* In practice, you'd compute range divisions dynamically *)
    
    (* Placeholder: This would need BCD conversion logic for arbitrary starts *)
    (* For now, just demonstrate the parallel structure *)
    
    let checker_outputs = Array.init num_checkers ~f:(fun _k ->
      (* Each checker would get its sub-range *)
      (* For demonstration, create dummy checkers *)
      let checker_i : _ Range_Checker.I.t =
        { clock = i.clock
        ; clear = i.clear
        ; start = i.start
        ; start_bin = i.range_low  (* Would be computed *)
        ; start_bcd = zero 48  (* Would be computed from binary *)
        ; count = of_int ~width:32 1000  (* Would be computed *)
        }
      in
      Range_Checker.create checker_i
    ) in
    
    (* Collect sums from all checkers using tree adder *)
    let p1_values = Array.map checker_outputs ~f:(fun o -> o.sum_p1) in
    let p2_values = Array.map checker_outputs ~f:(fun o -> o.sum_p2) in
    
    (* Pad to power of 2 for tree *)
    let next_pow2 = Int.pow 2 (Int.ceil_log2 num_checkers) in
    let p1_padded = Array.append p1_values 
      (Array.create ~len:(next_pow2 - num_checkers) (zero 64)) in
    let p2_padded = Array.append p2_values 
      (Array.create ~len:(next_pow2 - num_checkers) (zero 64)) in
    
    let tree_p1_i : _ Tree_Adder.I.t =
      { clock = i.clock
      ; values = p1_padded
      ; start = i.start
      }
    in
    let tree_p1_o = Tree_Adder.create tree_p1_i in
    
    let tree_p2_i : _ Tree_Adder.I.t =
      { clock = i.clock
      ; values = p2_padded
      ; start = i.start
      }
    in
    let tree_p2_o = Tree_Adder.create tree_p2_i in
    
    (* Wait for all checkers to finish *)
    let all_done = 
      Array.map checker_outputs ~f:(fun o -> o.done_)
      |> Array.to_list
      |> List.reduce_exn ~f:(&:)
    in
    
    let checkers_done_bits = 
      Array.map checker_outputs ~f:(fun o -> o.done_)
      |> Array.to_list
      |> (fun lst -> lst @ List.init (64 - num_checkers) ~f:(fun _ -> zero 1))
      |> concat_lsb
    in
    
    { O.sum_p1 = tree_p1_o.sum
    ; O.sum_p2 = tree_p2_o.sum
    ; O.done_ = all_done &: tree_p1_o.done_ &: tree_p2_o.done_
    ; O.checkers_done = checkers_done_bits
    }
end
