open! Core
open Hardcaml
open Aoc_hardcaml

module Csv = struct
  let escape (s : string) =
    if String.exists s ~f:(fun c -> Char.(c = ',' || c = '"' || c = '\n' || c = '\r')) then
      let s = String.substr_replace_all s ~pattern:"\"" ~with_:"\"\"" in
      "\"" ^ s ^ "\""
    else
      s

  let row (cols : string list) = String.concat ~sep:"," (List.map cols ~f:escape)
end

type bench_result =
  { design : string
  ; day : int
  ; variant : string
  ; work_units : int
  ; cycles : int
  ; ok : bool
  }

let with_variant (variant : string) (r : bench_result) = { r with variant }

let in_port_any sim (names : string list) =
  let rec go = function
    | [] -> failwith "Couldn't find input port (tried multiple names)"
    | name :: rest ->
      (try Cyclesim.in_port sim name with
       | _ -> go rest)
  in
  go names

let[@warning "-32"] out_port_any sim (names : string list) =
  let rec go = function
    | [] -> failwith "Couldn't find output port (tried multiple names)"
    | name :: rest ->
      (try Cyclesim.out_port sim name with
       | _ -> go rest)
  in
  go names

let in_port_indexed sim ~(base : string) ~(idx : int) =
  in_port_any sim [ Printf.sprintf "%s_%d" base idx; Printf.sprintf "%s%d" base idx ]

let write_csv (results : bench_result list) (out : Out_channel.t) =
  Out_channel.output_string out (Csv.row [ "design"; "day"; "variant"; "work_units"; "cycles"; "ok" ] ^ "\n");
  List.iter results ~f:(fun r ->
    Out_channel.output_string out
      (Csv.row
         [ r.design
         ; Int.to_string r.day
         ; r.variant
         ; Int.to_string r.work_units
         ; Int.to_string r.cycles
         ; Bool.to_string r.ok
         ]
       ^ "\n"))

let lobby_reference ~(k : int) (bank : string) : int =
  let bytes = Bytes.of_string bank in
  let len = Bytes.length bytes in
  let end_ = len - k in
  let batteries = Array.init k ~f:(fun j -> Bytes.get bytes (end_ + j)) in
  for pos = end_ - 1 downto 0 do
    let next = ref (Bytes.get bytes pos) in
    let stop = ref false in
    for j = 0 to k - 1 do
      if !stop then ()
      else if Char.to_int !next < Char.to_int batteries.(j) then stop := true
      else (
        let tmp = batteries.(j) in
        batteries.(j) <- !next;
        next := tmp)
    done
  done;
  Array.fold batteries ~init:0 ~f:(fun acc c -> (acc * 10) + (Char.to_int c - Char.to_int '0'))

let bits_of_bank (bank : string) : Bits.t =
  let digits =
    String.to_list bank
    |> List.map ~f:(fun c -> Bits.of_int ~width:4 (Char.to_int c - Char.to_int '0'))
  in
  let padded =
    if List.length digits >= 128 then List.take digits 128
    else digits @ List.init (128 - List.length digits) ~f:(fun _ -> Bits.zero 4)
  in
  Bits.concat_lsb padded

let is_repeat_exactly_twice (n : int) =
  let s = Int.to_string n in
  let len = String.length s in
  if len mod 2 <> 0 then false
  else
    let half = len / 2 in
    String.(sub s ~pos:0 ~len:half = sub s ~pos:half ~len:half)

let is_repeat_k_ge_2 (n : int) =
  let s = Int.to_string n in
  let len = String.length s in
  let rec check_period p =
    if p > len / 2 then false
    else if len mod p <> 0 then check_period (p + 1)
    else
      let k = len / p in
      if k < 2 then check_period (p + 1)
      else
        let unit = String.sub s ~pos:0 ~len:p in
        let ok =
          List.init k ~f:(fun i -> String.sub s ~pos:(i * p) ~len:p)
          |> List.for_all ~f:(String.equal unit)
        in
        ok || check_period (p + 1)
  in
  check_period 1

let brute_force_sums ~(ranges : (int * int) list) =
  List.fold ranges ~init:(0, 0) ~f:(fun (acc1, acc2) (a, b) ->
    let sum1 = ref acc1 in
    let sum2 = ref acc2 in
    for x = a to b do
      if is_repeat_exactly_twice x then sum1 := !sum1 + x;
      if is_repeat_k_ge_2 x then sum2 := !sum2 + x
    done;
    !sum1, !sum2)

let run_day1_opt_a () : bench_result =
  let circuit =
    Circuit.create_with_interface
      (module Day1_opt_a_minimal_streaming.I)
      (module Day1_opt_a_minimal_streaming.O)
      ~name:"day1_opt_a"
      Day1_opt_a_minimal_streaming.create
  in
  let sim = Cyclesim.create circuit in

  let clear = Cyclesim.in_port sim "clear" in
  let instruction_valid = Cyclesim.in_port sim "instruction_valid" in
  let direction = Cyclesim.in_port sim "direction" in
  let magnitude = Cyclesim.in_port sim "magnitude" in

  let part1 = Cyclesim.out_port sim "part1_result" in
  let part2 = Cyclesim.out_port sim "part2_result" in
  let position = Cyclesim.out_port sim "position" in

  let set_instr ~valid ~dir ~mag =
    instruction_valid := if valid then Bits.one 1 else Bits.zero 1;
    direction := Bits.of_int ~width:1 dir;
    magnitude := Bits.of_int ~width:16 mag
  in

  Cyclesim.reset sim;
  clear := Bits.one 1;
  set_instr ~valid:false ~dir:1 ~mag:0;

  let cycles = ref 0 in
  let cycle () =
    incr cycles;
    Cyclesim.cycle sim
  in

  (* establish cleared state *)
  cycle ();
  clear := Bits.zero 1;

  (* 4 instruction test vector from the unit test *)
  let program = [ 1, 50; 1, 1; 0, 2; 1, 1 ] in
  List.iter program ~f:(fun (dir, mag) ->
    set_instr ~valid:true ~dir ~mag;
    cycle ();
    set_instr ~valid:false ~dir:1 ~mag:0);

  let ok =
    Bits.to_int !part1 = 2
    && Bits.to_int !part2 = 3
    && Bits.to_int !position = 0
  in

  { design = "day1"; day = 1; variant = "day1_opt_a"; work_units = List.length program; cycles = !cycles; ok }

let run_day1_opt_b () : bench_result =
  let circuit =
    Circuit.create_with_interface
      (module Day1_opt_b_pipelined.I)
      (module Day1_opt_b_pipelined.O)
      ~name:"day1_opt_b"
      Day1_opt_b_pipelined.create
  in
  let sim = Cyclesim.create circuit in

  let clear = Cyclesim.in_port sim "clear" in
  let instruction_valid = Cyclesim.in_port sim "instruction_valid" in
  let direction = Cyclesim.in_port sim "direction" in
  let magnitude = Cyclesim.in_port sim "magnitude" in

  let part1 = Cyclesim.out_port sim "part1_result" in
  let part2 = Cyclesim.out_port sim "part2_result" in
  let position = Cyclesim.out_port sim "position" in

  let set_instr ~valid ~dir ~mag =
    instruction_valid := if valid then Bits.one 1 else Bits.zero 1;
    direction := Bits.of_int ~width:1 dir;
    magnitude := Bits.of_int ~width:16 mag
  in

  Cyclesim.reset sim;
  clear := Bits.one 1;
  set_instr ~valid:false ~dir:1 ~mag:0;

  let cycles = ref 0 in
  let cycle () =
    incr cycles;
    Cyclesim.cycle sim
  in

  cycle ();
  clear := Bits.zero 1;

  let program = [ 1, 50; 1, 1; 0, 2; 1, 1 ] in
  List.iter program ~f:(fun (dir, mag) ->
    set_instr ~valid:true ~dir ~mag;
    cycle ();
    set_instr ~valid:false ~dir:1 ~mag:0);

  (* allow 1-cycle pipeline latency to retire *)
  cycle ();

  let ok =
    Bits.to_int !part1 = 2
    && Bits.to_int !part2 = 3
    && Bits.to_int !position = 0
  in

  { design = "day1"; day = 1; variant = "day1_opt_b"; work_units = List.length program; cycles = !cycles; ok }

let run_day1_opt_c_tree8 () : bench_result =
  let circuit =
    Circuit.create_with_interface
      (module Day1_opt_c_tree8.I)
      (module Day1_opt_c_tree8.O)
      ~name:"day1_opt_c_tree8"
      Day1_opt_c_tree8.create
  in
  let sim = Cyclesim.create circuit in

  let clear = Cyclesim.in_port sim "clear" in
  let start = Cyclesim.in_port sim "start" in
  let start_pos = Cyclesim.in_port sim "start_pos" in
  let dirs = Array.init 8 ~f:(fun k -> in_port_indexed sim ~base:"directions" ~idx:k) in
  let mags = Array.init 8 ~f:(fun k -> in_port_indexed sim ~base:"magnitudes" ~idx:k) in

  let done_ = Cyclesim.out_port sim "done_" in
  let end_pos = Cyclesim.out_port sim "end_pos" in
  let crossings = Cyclesim.out_port sim "crossings" in

  Cyclesim.reset sim;
  clear := Bits.one 1;
  start := Bits.zero 1;
  start_pos := Bits.of_int ~width:7 50;
  Array.iter dirs ~f:(fun p -> p := Bits.zero 1);
  Array.iter mags ~f:(fun p -> p := Bits.zero 16);

  let cycles = ref 0 in
  let cycle () =
    incr cycles;
    Cyclesim.cycle sim
  in

  (* clear *)
  cycle ();
  clear := Bits.zero 1;

  (* Use first 4 instructions of the day1 unit test; pad remaining with no-ops. *)
  let program = [ 1, 50; 1, 1; 0, 2; 1, 1 ] in
  let dirs8 = Array.create ~len:8 1 in
  let mags8 = Array.create ~len:8 0 in
  List.iteri program ~f:(fun i (d, m) ->
    dirs8.(i) <- d;
    mags8.(i) <- m);

  start := Bits.one 1;
  start_pos := Bits.of_int ~width:7 50;
  for i = 0 to 7 do
    dirs.(i) := Bits.of_int ~width:1 dirs8.(i);
    mags.(i) := Bits.of_int ~width:16 mags8.(i)
  done;
  cycle ();
  start := Bits.zero 1;

  (* wait done_ *)
  let rec wait n =
    if n > 20 then failwith "Day1 opt C timeout";
    if Bits.to_int !done_ = 1 then ()
    else (
      cycle ();
      wait (n + 1))
  in
  wait 0;

  let ok = Bits.to_int !end_pos = 0 && Bits.to_int !crossings = 3 in

  { design = "day1"; day = 1; variant = "day1_opt_c_tree8"; work_units = 8; cycles = !cycles; ok }

let run_day1_opt_d_microcoded () : bench_result =
  let circuit =
    Circuit.create_with_interface
      (module Day1_opt_d_microcoded_div100.I)
      (module Day1_opt_d_microcoded_div100.O)
      ~name:"day1_opt_d_microcoded"
      Day1_opt_d_microcoded_div100.create
  in
  let sim = Cyclesim.create circuit in

  let clear = Cyclesim.in_port sim "clear" in
  let instruction_valid = Cyclesim.in_port sim "instruction_valid" in
  let instruction_dir = Cyclesim.in_port sim "instruction_dir" in
  let instruction_mag = Cyclesim.in_port sim "instruction_mag" in
  let ready = Cyclesim.out_port sim "ready" in

  let part1 = Cyclesim.out_port sim "part1_result" in
  let part2 = Cyclesim.out_port sim "part2_result" in
  let position = Cyclesim.out_port sim "position" in

  let set_instr ~valid ~dir ~mag =
    instruction_valid := if valid then Bits.one 1 else Bits.zero 1;
    instruction_dir := Bits.of_int ~width:1 dir;
    instruction_mag := Bits.of_int ~width:16 mag
  in

  Cyclesim.reset sim;
  clear := Bits.one 1;
  set_instr ~valid:false ~dir:1 ~mag:0;

  let cycles = ref 0 in
  let cycle () =
    incr cycles;
    Cyclesim.cycle sim
  in

  cycle ();
  clear := Bits.zero 1;

  let program = [ 1, 50; 1, 1; 0, 2; 1, 1 ] in
  List.iter program ~f:(fun (dir, mag) ->
    (* wait ready *)
    while Bits.to_int !ready = 0 do
      cycle ()
    done;
    set_instr ~valid:true ~dir ~mag;
    cycle ();
    set_instr ~valid:false ~dir:1 ~mag:0);

  (* allow last apply to land *)
  while Bits.to_int !ready = 0 do
    cycle ()
  done;

  let ok =
    Bits.to_int !part1 = 2
    && Bits.to_int !part2 = 3
    && Bits.to_int !position = 0
  in

  { design = "day1"; day = 1; variant = "day1_opt_d_microcoded"; work_units = List.length program; cycles = !cycles; ok }

let run_day2_sequential () : bench_result =
  let ranges = [ 10, 250; 300, 450 ] in
  let exp1, exp2 = brute_force_sums ~ranges in

  let circuit =
    Circuit.create_with_interface
      (module Day2_opt_a_sequential.I)
      (module Day2_opt_a_sequential.O)
      ~name:"day2_opt_a_sequential"
      Day2_opt_a_sequential.create
  in
  let sim = Cyclesim.create circuit in

  let clear = Cyclesim.in_port sim "clear" in
  let load = Cyclesim.in_port sim "load" in
  let pair_valid = Cyclesim.in_port sim "pair_valid" in
  let from_ = Cyclesim.in_port sim "from_" in
  let to_ = Cyclesim.in_port sim "to_" in
  let last = Cyclesim.in_port sim "last" in

  let ready = Cyclesim.out_port sim "ready" in
  let done_ = Cyclesim.out_port sim "done_" in
  let sum_p1 = Cyclesim.out_port sim "sum_p1" in
  let sum_p2 = Cyclesim.out_port sim "sum_p2" in

  let cycles = ref 0 in
  let cycle () =
    incr cycles;
    Cyclesim.cycle sim
  in

  let set_pair ~valid ~a ~b ~is_last =
    pair_valid := if valid then Bits.one 1 else Bits.zero 1;
    from_ := Bits.of_int ~width:64 a;
    to_ := Bits.of_int ~width:64 b;
    last := if is_last then Bits.one 1 else Bits.zero 1
  in

  Cyclesim.reset sim;
  clear := Bits.one 1;
  load := Bits.zero 1;
  set_pair ~valid:false ~a:0 ~b:0 ~is_last:false;
  cycle ();
  clear := Bits.zero 1;

  (* Explicitly clear accumulators *)
  load := Bits.one 1;
  cycle ();
  load := Bits.zero 1;

  List.iteri ranges ~f:(fun idx (a, b) ->
    while Bits.to_int !ready = 0 do
      cycle ()
    done;
    let is_last = idx = List.length ranges - 1 in
    set_pair ~valid:true ~a ~b ~is_last;
    cycle ();
    set_pair ~valid:false ~a:0 ~b:0 ~is_last:false;
    if is_last then (
      while Bits.to_int !done_ = 0 do
        cycle ()
      done
    ) else (
      while Bits.to_int !ready = 0 do
        cycle ()
      done
    ));

  let ok = Bits.to_int !sum_p1 = exp1 && Bits.to_int !sum_p2 = exp2 in

  { design = "day2"; day = 2; variant = "day2_opt_a_sequential"; work_units = List.length ranges; cycles = !cycles; ok }

let run_day2_opt_a_range_sum_engine () : bench_result =
  (* Day2_hardware aliases this, but we instantiate it directly so it can be compared/synthesized as its own top. *)
  let ranges = [ 10, 250; 300, 450 ] in
  let exp1, exp2 = brute_force_sums ~ranges in

  let circuit =
    Circuit.create_with_interface
      (module Day2_opt_a_range_sum_engine.I)
      (module Day2_opt_a_range_sum_engine.O)
      ~name:"day2_opt_a_range_sum_engine"
      Day2_opt_a_range_sum_engine.create
  in
  let sim = Cyclesim.create circuit in

  let clear = Cyclesim.in_port sim "clear" in
  let load = Cyclesim.in_port sim "load" in
  let pair_valid = Cyclesim.in_port sim "pair_valid" in
  let from_ = Cyclesim.in_port sim "from_" in
  let to_ = Cyclesim.in_port sim "to_" in
  let last = Cyclesim.in_port sim "last" in

  let ready = Cyclesim.out_port sim "ready" in
  let done_ = Cyclesim.out_port sim "done_" in
  let sum_p1 = Cyclesim.out_port sim "sum_p1" in
  let sum_p2 = Cyclesim.out_port sim "sum_p2" in

  let cycles = ref 0 in
  let cycle () =
    incr cycles;
    Cyclesim.cycle sim
  in

  let set_pair ~valid ~a ~b ~is_last =
    pair_valid := if valid then Bits.one 1 else Bits.zero 1;
    from_ := Bits.of_int ~width:64 a;
    to_ := Bits.of_int ~width:64 b;
    last := if is_last then Bits.one 1 else Bits.zero 1
  in

  Cyclesim.reset sim;
  clear := Bits.one 1;
  load := Bits.zero 1;
  set_pair ~valid:false ~a:0 ~b:0 ~is_last:false;
  cycle ();
  clear := Bits.zero 1;

  (* Explicitly clear accumulators *)
  load := Bits.one 1;
  cycle ();
  load := Bits.zero 1;

  List.iteri ranges ~f:(fun idx (a, b) ->
    while Bits.to_int !ready = 0 do
      cycle ()
    done;
    let is_last = idx = List.length ranges - 1 in
    set_pair ~valid:true ~a ~b ~is_last;
    cycle ();
    set_pair ~valid:false ~a:0 ~b:0 ~is_last:false;
    if is_last then (
      while Bits.to_int !done_ = 0 do
        cycle ()
      done
    ) else (
      while Bits.to_int !ready = 0 do
        cycle ()
      done
    ));

  let ok = Bits.to_int !sum_p1 = exp1 && Bits.to_int !sum_p2 = exp2 in
  { design = "day2"; day = 2; variant = "day2_opt_a_range_sum_engine"; work_units = List.length ranges; cycles = !cycles; ok }

let run_day2_opt_c_family_unroll () : bench_result =
  let a, b = 10, 500 in
  let exp1, exp2 = brute_force_sums ~ranges:[ a, b ] in

  let circuit =
    Circuit.create_with_interface
      (module Day2_opt_c_family_unroll.I)
      (module Day2_opt_c_family_unroll.O)
      ~name:"day2_opt_c_family_unroll"
      Day2_opt_c_family_unroll.create
  in
  let sim = Cyclesim.create circuit in

  let from_ = Cyclesim.in_port sim "from_" in
  let to_ = Cyclesim.in_port sim "to_" in
  let sum_p1 = Cyclesim.out_port sim "sum_p1" in
  let sum_p2 = Cyclesim.out_port sim "sum_p2" in

  Cyclesim.reset sim;
  from_ := Bits.of_int ~width:64 a;
  to_ := Bits.of_int ~width:64 b;
  Cyclesim.cycle sim;

  let ok = Bits.to_int !sum_p1 = exp1 && Bits.to_int !sum_p2 = exp2 in

  { design = "day2"; day = 2; variant = "day2_opt_c_family_unroll"; work_units = 1; cycles = 1; ok }

let run_day2_opt_b_multilane () : bench_result =
  (* Two ranges, map into lane0 and lane1; remaining lanes idle. *)
  let ranges = [ 10, 250; 300, 450 ] in
  let exp1, exp2 = brute_force_sums ~ranges in

  let circuit =
    Circuit.create_with_interface
      (module Day2_opt_b_multilane.I)
      (module Day2_opt_b_multilane.O)
      ~name:"day2_opt_b_multilane"
      Day2_opt_b_multilane.create
  in
  let sim = Cyclesim.create circuit in

  let lane_valid = Array.init 4 ~f:(fun k -> in_port_indexed sim ~base:"lane_valid" ~idx:k) in
  let lane_from = Array.init 4 ~f:(fun k -> in_port_indexed sim ~base:"lane_from" ~idx:k) in
  let lane_to = Array.init 4 ~f:(fun k -> in_port_indexed sim ~base:"lane_to" ~idx:k) in

  let sum_p1 = Cyclesim.out_port sim "sum_p1" in
  let sum_p2 = Cyclesim.out_port sim "sum_p2" in

  Cyclesim.reset sim;
  for k = 0 to 3 do
    lane_valid.(k) := Bits.zero 1;
    lane_from.(k) := Bits.zero 64;
    lane_to.(k) := Bits.zero 64
  done;

  List.iteri ranges ~f:(fun i (a, b) ->
    lane_valid.(i) := Bits.one 1;
    lane_from.(i) := Bits.of_int ~width:64 a;
    lane_to.(i) := Bits.of_int ~width:64 b);

  (* Combinational core; 1 cycle is enough to observe outputs in Cyclesim. *)
  Cyclesim.cycle sim;

  let ok = Bits.to_int !sum_p1 = exp1 && Bits.to_int !sum_p2 = exp2 in

  { design = "day2"; day = 2; variant = "day2_opt_b_multilane"; work_units = List.length ranges; cycles = 1; ok }

let run_day3_opt_a () : bench_result =
  let k = 12 in
  let bank = "818181911112111" in
  let expected = lobby_reference ~k bank in

  let circuit =
    Circuit.create_with_interface
      (module Day3_opt_a_streaming_selector.I)
      (module Day3_opt_a_streaming_selector.O)
      ~name:"day3_opt_a"
      Day3_opt_a_streaming_selector.create
  in
  let sim = Cyclesim.create circuit in

  let start = Cyclesim.in_port sim "start" in
  let data = Cyclesim.in_port sim "data" in
  let length = Cyclesim.in_port sim "length" in
  let k_in = Cyclesim.in_port sim "k" in

  let done_ = Cyclesim.out_port sim "done_" in
  let result = Cyclesim.out_port sim "result" in

  Cyclesim.reset sim;
  start := Bits.one 1;
  data := bits_of_bank bank;
  length := Bits.of_int ~width:8 (String.length bank);
  k_in := Bits.of_int ~width:4 k;

  let cycles = ref 0 in
  let cycle () =
    incr cycles;
    Cyclesim.cycle sim
  in

  cycle ();
  start := Bits.zero 1;

  let rec run () =
    if !cycles > 500 then failwith "Day3 opt A sim timeout";
    if Bits.to_int !done_ = 1 then ()
    else (
      cycle ();
      run ())
  in
  run ();

  let ok = Bits.to_int !result = expected in

  { design = "day3"; day = 3; variant = "day3_opt_a"; work_units = String.length bank; cycles = !cycles; ok }

let run_day3_opt_b () : bench_result =
  let k = 12 in
  let bank = "818181911112111" in
  let expected = lobby_reference ~k bank in

  let circuit =
    Circuit.create_with_interface
      (module Day3_opt_b_monotone_stack.I)
      (module Day3_opt_b_monotone_stack.O)
      ~name:"day3_opt_b"
      Day3_opt_b_monotone_stack.create
  in
  let sim = Cyclesim.create circuit in

  let start = Cyclesim.in_port sim "start" in
  let data = Cyclesim.in_port sim "data" in
  let length = Cyclesim.in_port sim "length" in
  let k_in = Cyclesim.in_port sim "k" in

  let done_ = Cyclesim.out_port sim "done_" in
  let result = Cyclesim.out_port sim "result" in

  Cyclesim.reset sim;
  start := Bits.one 1;
  data := bits_of_bank bank;
  length := Bits.of_int ~width:8 (String.length bank);
  k_in := Bits.of_int ~width:4 k;

  let cycles = ref 0 in
  let cycle () =
    incr cycles;
    Cyclesim.cycle sim
  in

  cycle ();
  start := Bits.zero 1;

  let rec run () =
    if !cycles > 500 then failwith "Day3 opt B sim timeout";
    if Bits.to_int !done_ = 1 then ()
    else (
      cycle ();
      run ())
  in
  run ();

  let ok = Bits.to_int !result = expected in

  { design = "day3"; day = 3; variant = "day3_opt_b"; work_units = String.length bank; cycles = !cycles; ok }

let run_day3_opt_c () : bench_result =
  let k = 12 in
  let bank = "818181911112111" in
  let expected = lobby_reference ~k bank in

  let circuit =
    Circuit.create_with_interface
      (module Day3_opt_c_unrolled_compare_network.I)
      (module Day3_opt_c_unrolled_compare_network.O)
      ~name:"day3_opt_c"
      Day3_opt_c_unrolled_compare_network.create
  in
  let sim = Cyclesim.create circuit in

  let start = Cyclesim.in_port sim "start" in
  let data = Cyclesim.in_port sim "data" in
  let length = Cyclesim.in_port sim "length" in
  let k_in = Cyclesim.in_port sim "k" in

  let done_ = Cyclesim.out_port sim "done_" in
  let result = Cyclesim.out_port sim "result" in

  Cyclesim.reset sim;
  start := Bits.one 1;
  data := bits_of_bank bank;
  length := Bits.of_int ~width:8 (String.length bank);
  k_in := Bits.of_int ~width:4 k;

  let cycles = ref 0 in
  let cycle () =
    incr cycles;
    Cyclesim.cycle sim
  in

  cycle ();
  start := Bits.zero 1;

  let rec run () =
    if !cycles > 500 then failwith "Day3 opt C sim timeout";
    if Bits.to_int !done_ = 1 then ()
    else (
      cycle ();
      run ())
  in
  run ();

  let ok = Bits.to_int !result = expected in

  { design = "day3"; day = 3; variant = "day3_opt_c"; work_units = String.length bank; cycles = !cycles; ok }

let run_day4_opt_a () : bench_result =
  let day4_reference (lines : string list) : int * int =
    let h = List.length lines in
    let w =
      match lines with
      | [] -> 0
      | hd :: _ -> String.length hd
    in
    let dirs = [ -1, -1; -1, 0; -1, 1; 0, -1; 0, 1; 1, -1; 1, 0; 1, 1 ] in
    let is_at r c =
      if r < 0 || r >= h || c < 0 || c >= w then false
      else Char.equal (String.get (List.nth_exn lines r) c) '@'
    in
    let pw = w + 2 in
    let ph = h + 2 in
    let idx r c = (r * pw) + c in
    let padded = Array.create ~len:(pw * ph) 255 in
    let todo = ref [] in
    for r = 0 to h - 1 do
      for c = 0 to w - 1 do
        if is_at r c then (
          let count = List.count dirs ~f:(fun (dr, dc) -> is_at (r + dr) (c + dc)) in
          if count < 4 then todo := (r + 1, c + 1) :: !todo;
          padded.(idx (r + 1) (c + 1)) <- count)
      done
    done;
    let part1 = List.length !todo in
    let removed = ref 0 in
    while not (List.is_empty !todo) do
      match !todo with
      | [] -> ()
      | (r, c) :: rest ->
        todo := rest;
        removed := !removed + 1;
        List.iter dirs ~f:(fun (dr, dc) ->
          let rr = r + dr in
          let cc = c + dc in
          let i = idx rr cc in
          if padded.(i) = 4 then todo := (rr, cc) :: !todo;
          padded.(i) <- padded.(i) - 1)
    done;
    part1, !removed
  in

  let bits_of_day4_lines_139 (lines : string list) : Bits.t =
    let rows = 139 in
    let cols = 139 in
    let buffer = Buffer.create (rows * cols) in
    for r = rows - 1 downto 0 do
      for c = cols - 1 downto 0 do
        let is_set =
          if r < List.length lines then (
            let line = List.nth_exn lines r in
            c < String.length line && Char.equal line.[c] '@')
          else false
        in
        Buffer.add_char buffer (if is_set then '1' else '0')
      done
    done;
    Bits.of_string (Buffer.contents buffer)
  in

  let day4_lines =
    [ "..@@.@@@@."
    ; "@@@.@.@.@@"
    ; "@@@@@.@.@@"
    ; "@.@@@@..@."
    ; "@@.@@@@.@@"
    ; ".@@@@@@@.@"
    ; ".@.@.@.@@@"
    ; "@.@@@.@@@@"
    ; ".@@@@@@@@."
    ; "@.@.@@@.@."
    ]
  in
  let exp_p1, exp_p2 = day4_reference day4_lines in

  let circuit =
    Circuit.create_with_interface
      (module Day4_opt_a_dense_ca.I)
      (module Day4_opt_a_dense_ca.O)
      ~name:"day4_opt_a"
      Day4_opt_a_dense_ca.create
  in
  let sim = Cyclesim.create circuit in
  let clear = Cyclesim.in_port sim "clear" in
  let start = Cyclesim.in_port sim "start" in
  let grid_in = Cyclesim.in_port sim "grid_in" in
  let done_ = Cyclesim.out_port sim "done_" in
  let part1 = Cyclesim.out_port sim "part1_result" in
  let part2 = Cyclesim.out_port sim "part2_result" in

  let cycles = ref 0 in
  let cycle () =
    incr cycles;
    Cyclesim.cycle sim
  in

  Cyclesim.reset sim;
  clear := Bits.one 1;
  start := Bits.zero 1;
  grid_in := Bits.zero (139 * 139);
  cycle ();
  clear := Bits.zero 1;
  start := Bits.one 1;
  grid_in := bits_of_day4_lines_139 day4_lines;
  cycle ();
  start := Bits.zero 1;

  let rec run n =
    if n > 600 then failwith "Day4 sim timeout";
    cycle ();
    if Bits.to_int !done_ = 1 then () else run (n + 1)
  in
  run 0;

  let ok = Bits.to_int !part1 = exp_p1 && Bits.to_int !part2 = exp_p2 in
  { design = "day4"; day = 4; variant = "day4_opt_a"; work_units = List.length day4_lines; cycles = !cycles; ok }

let run_day5_opt_a () : bench_result =
  let day5_reference ~(ranges : (int * int) list) ~(ids : int list) : int * int =
    let ranges =
      List.sort ranges ~compare:(fun (a1, b1) (a2, b2) ->
        match Int.compare a1 a2 with
        | 0 -> Int.compare b1 b2
        | x -> x)
    in
    let ids = List.sort ids ~compare:Int.compare in
    let merged = ref [] in
    let cur_s = ref 0 in
    let cur_e = ref 0 in
    let have = ref false in
    List.iter ranges ~f:(fun (from_, to_) ->
      let end_excl = to_ + 1 in
      if not !have then (
        have := true;
        cur_s := from_;
        cur_e := end_excl)
      else if from_ < !cur_e then cur_e := Int.max !cur_e end_excl
      else (
        merged := (!cur_s, !cur_e) :: !merged;
        cur_s := from_;
        cur_e := end_excl));
    if !have then merged := (!cur_s, !cur_e) :: !merged;
    let merged = List.rev !merged in
    let part2 = List.fold merged ~init:0 ~f:(fun acc (s, e) -> acc + (e - s)) in
    let rec count ids merged acc =
      match ids, merged with
      | [], _ -> acc
      | _, [] -> acc
      | id :: ids', (s, e) :: merged' ->
        if id < s then count ids' merged acc
        else if id >= e then count ids merged' acc
        else count ids' merged (acc + 1)
    in
    let part1 = count ids merged 0 in
    part1, part2
  in

  let day5_ranges = [ 10, 20; 15, 30; 40, 40; 41, 42; 100, 105 ] in
  let day5_ids = [ 9; 10; 15; 20; 21; 30; 31; 40; 41; 42; 43; 104; 200 ] in
  let exp_p1, exp_p2 = day5_reference ~ranges:day5_ranges ~ids:day5_ids in

  let circuit =
    Circuit.create_with_interface
      (module Day5_opt_a_interval_union_engine.I)
      (module Day5_opt_a_interval_union_engine.O)
      ~name:"day5_opt_a"
      Day5_opt_a_interval_union_engine.create
  in
  let sim = Cyclesim.create circuit in
  let clear = Cyclesim.in_port sim "clear" in
  let load = Cyclesim.in_port sim "load" in
  let range_valid = Cyclesim.in_port sim "range_valid" in
  let range_from = Cyclesim.in_port sim "range_from" in
  let range_to = Cyclesim.in_port sim "range_to" in
  let range_last = Cyclesim.in_port sim "range_last" in
  let id_valid = Cyclesim.in_port sim "id_valid" in
  let id = Cyclesim.in_port sim "id" in
  let id_last = Cyclesim.in_port sim "id_last" in
  let range_ready = Cyclesim.out_port sim "range_ready" in
  let id_ready = Cyclesim.out_port sim "id_ready" in
  let done_ = Cyclesim.out_port sim "done_" in
  let part1 = Cyclesim.out_port sim "part1_result" in
  let part2 = Cyclesim.out_port sim "part2_result" in

  let cycles = ref 0 in
  let cycle () =
    incr cycles;
    Cyclesim.cycle sim
  in

  let set_range ~valid ~from_ ~to_ ~last =
    range_valid := if valid then Bits.one 1 else Bits.zero 1;
    range_from := Bits.of_int ~width:64 from_;
    range_to := Bits.of_int ~width:64 to_;
    range_last := if last then Bits.one 1 else Bits.zero 1
  in
  let set_id ~valid ~v ~last =
    id_valid := if valid then Bits.one 1 else Bits.zero 1;
    id := Bits.of_int ~width:64 v;
    id_last := if last then Bits.one 1 else Bits.zero 1
  in

  Cyclesim.reset sim;
  clear := Bits.one 1;
  load := Bits.zero 1;
  set_range ~valid:false ~from_:0 ~to_:0 ~last:false;
  set_id ~valid:false ~v:0 ~last:false;
  cycle ();
  clear := Bits.zero 1;
  load := Bits.one 1;
  cycle ();
  load := Bits.zero 1;

  let ranges =
    List.sort day5_ranges ~compare:(fun (a1, b1) (a2, b2) ->
      match Int.compare a1 a2 with
      | 0 -> Int.compare b1 b2
      | x -> x)
  in
  let ids = List.sort day5_ids ~compare:Int.compare in

  List.iteri ranges ~f:(fun idx (a, b) ->
    while Bits.to_int !range_ready = 0 do
      cycle ()
    done;
    let last = idx = List.length ranges - 1 in
    set_range ~valid:true ~from_:a ~to_:b ~last;
    cycle ();
    set_range ~valid:false ~from_:0 ~to_:0 ~last:false);

  List.iteri ids ~f:(fun idx v ->
    while Bits.to_int !id_ready = 0 do
      cycle ()
    done;
    let last = idx = List.length ids - 1 in
    set_id ~valid:true ~v ~last;
    cycle ();
    set_id ~valid:false ~v:0 ~last:false);

  let rec run n =
    if n > 2000 then failwith "Day5 sim timeout";
    cycle ();
    if Bits.to_int !done_ = 1 then () else run (n + 1)
  in
  run 0;

  let ok = Bits.to_int !part1 = exp_p1 && Bits.to_int !part2 = exp_p2 in
  { design = "day5"; day = 5; variant = "day5_opt_a"; work_units = List.length ranges + List.length ids; cycles = !cycles; ok }

let run_day5_opt_b () : bench_result =
  let day5_ranges = [ 10, 20; 15, 30; 40, 40; 41, 42; 100, 105 ] in
  let day5_ids = [ 9; 10; 15; 20; 21; 30; 31; 40; 41; 42; 43; 104; 200 ] in
  let exp_p1, exp_p2 =
    let ranges =
      List.sort day5_ranges ~compare:(fun (a1, b1) (a2, b2) ->
        match Int.compare a1 a2 with
        | 0 -> Int.compare b1 b2
        | x -> x)
    in
    let ids = List.sort day5_ids ~compare:Int.compare in
    let merged = ref [] in
    let cur_s = ref 0 in
    let cur_e = ref 0 in
    let have = ref false in
    List.iter ranges ~f:(fun (from_, to_) ->
      let end_excl = to_ + 1 in
      if not !have then (
        have := true;
        cur_s := from_;
        cur_e := end_excl)
      else if from_ < !cur_e then cur_e := Int.max !cur_e end_excl
      else (
        merged := (!cur_s, !cur_e) :: !merged;
        cur_s := from_;
        cur_e := end_excl));
    if !have then merged := (!cur_s, !cur_e) :: !merged;
    let merged = List.rev !merged in
    let part2 = List.fold merged ~init:0 ~f:(fun acc (s, e) -> acc + (e - s)) in
    let rec count ids merged acc =
      match ids, merged with
      | [], _ -> acc
      | _, [] -> acc
      | id :: ids', (s, e) :: merged' ->
        if id < s then count ids' merged acc
        else if id >= e then count ids merged' acc
        else count ids' merged (acc + 1)
    in
    let part1 = count ids merged 0 in
    part1, part2
  in

  let circuit =
    Circuit.create_with_interface
      (module Day5_opt_b_multilane_counter.I)
      (module Day5_opt_b_multilane_counter.O)
      ~name:"day5_opt_b"
      Day5_opt_b_multilane_counter.create
  in
  let sim = Cyclesim.create circuit in
  let clear = Cyclesim.in_port sim "clear" in
  let load = Cyclesim.in_port sim "load" in
  let range_valid = Cyclesim.in_port sim "range_valid" in
  let range_from = Cyclesim.in_port sim "range_from" in
  let range_to = Cyclesim.in_port sim "range_to" in
  let range_last = Cyclesim.in_port sim "range_last" in
  let id_valid = Cyclesim.in_port sim "id_valid" in
  let id = Cyclesim.in_port sim "id" in
  let id_last = Cyclesim.in_port sim "id_last" in
  let range_ready = Cyclesim.out_port sim "range_ready" in
  let id_ready = Cyclesim.out_port sim "id_ready" in
  let done_ = Cyclesim.out_port sim "done_" in
  let part1 = Cyclesim.out_port sim "part1_result" in
  let part2 = Cyclesim.out_port sim "part2_result" in

  let cycles = ref 0 in
  let cycle () =
    incr cycles;
    Cyclesim.cycle sim
  in

  let set_range ~valid ~from_ ~to_ ~last =
    range_valid := if valid then Bits.one 1 else Bits.zero 1;
    range_from := Bits.of_int ~width:64 from_;
    range_to := Bits.of_int ~width:64 to_;
    range_last := if last then Bits.one 1 else Bits.zero 1
  in
  let set_id ~valid ~v ~last =
    id_valid := if valid then Bits.one 1 else Bits.zero 1;
    id := Bits.of_int ~width:64 v;
    id_last := if last then Bits.one 1 else Bits.zero 1
  in

  Cyclesim.reset sim;
  clear := Bits.one 1;
  load := Bits.zero 1;
  set_range ~valid:false ~from_:0 ~to_:0 ~last:false;
  set_id ~valid:false ~v:0 ~last:false;
  cycle ();
  clear := Bits.zero 1;
  load := Bits.one 1;
  cycle ();
  load := Bits.zero 1;

  List.iteri day5_ranges ~f:(fun idx (from_, to_) ->
    while Bits.to_int !range_ready = 0 do
      cycle ()
    done;
    let last = idx = List.length day5_ranges - 1 in
    set_range ~valid:true ~from_ ~to_ ~last;
    cycle ();
    set_range ~valid:false ~from_:0 ~to_:0 ~last:false);

  List.iteri day5_ids ~f:(fun idx v ->
    while Bits.to_int !id_ready = 0 do
      cycle ()
    done;
    let last = idx = List.length day5_ids - 1 in
    set_id ~valid:true ~v ~last;
    cycle ();
    set_id ~valid:false ~v:0 ~last:false);

  let rec run n =
    if n > 2000 then failwith "Day5 sim timeout";
    cycle ();
    if Bits.to_int !done_ = 1 then () else run (n + 1)
  in
  run 0;

  let ok = Bits.to_int !part1 = exp_p1 && Bits.to_int !part2 = exp_p2 in
  { design = "day5"; day = 5; variant = "day5_opt_b"; work_units = List.length day5_ranges + List.length day5_ids; cycles = !cycles; ok }

let run_day5_opt_c () : bench_result =
  let day5_ranges = [ 10, 20; 15, 30; 40, 40; 41, 42; 100, 105 ] in
  let day5_ids = [ 9; 10; 15; 20; 21; 30; 31; 40; 41; 42; 43; 104; 200 ] in
  let exp_p1, exp_p2 =
    let ranges =
      List.sort day5_ranges ~compare:(fun (a1, b1) (a2, b2) ->
        match Int.compare a1 a2 with
        | 0 -> Int.compare b1 b2
        | x -> x)
    in
    let ids = List.sort day5_ids ~compare:Int.compare in
    let merged = ref [] in
    let cur_s = ref 0 in
    let cur_e = ref 0 in
    let have = ref false in
    List.iter ranges ~f:(fun (from_, to_) ->
      let end_excl = to_ + 1 in
      if not !have then (
        have := true;
        cur_s := from_;
        cur_e := end_excl)
      else if from_ < !cur_e then cur_e := Int.max !cur_e end_excl
      else (
        merged := (!cur_s, !cur_e) :: !merged;
        cur_s := from_;
        cur_e := end_excl));
    if !have then merged := (!cur_s, !cur_e) :: !merged;
    let merged = List.rev !merged in
    let part2 = List.fold merged ~init:0 ~f:(fun acc (s, e) -> acc + (e - s)) in
    let rec count ids merged acc =
      match ids, merged with
      | [], _ -> acc
      | _, [] -> acc
      | id :: ids', (s, e) :: merged' ->
        if id < s then count ids' merged acc
        else if id >= e then count ids merged' acc
        else count ids' merged (acc + 1)
    in
    let part1 = count ids merged 0 in
    part1, part2
  in

  let circuit =
    Circuit.create_with_interface
      (module Day5_opt_c_max_parallel_coverage.I)
      (module Day5_opt_c_max_parallel_coverage.O)
      ~name:"day5_opt_c"
      Day5_opt_c_max_parallel_coverage.create
  in
  let sim = Cyclesim.create circuit in
  let clear = Cyclesim.in_port sim "clear" in
  let load = Cyclesim.in_port sim "load" in
  let range_valid = Cyclesim.in_port sim "range_valid" in
  let range_from = Cyclesim.in_port sim "range_from" in
  let range_to = Cyclesim.in_port sim "range_to" in
  let range_last = Cyclesim.in_port sim "range_last" in
  let id_valid = Cyclesim.in_port sim "id_valid" in
  let id = Cyclesim.in_port sim "id" in
  let id_last = Cyclesim.in_port sim "id_last" in
  let range_ready = Cyclesim.out_port sim "range_ready" in
  let id_ready = Cyclesim.out_port sim "id_ready" in
  let done_ = Cyclesim.out_port sim "done_" in
  let part1 = Cyclesim.out_port sim "part1_result" in
  let part2 = Cyclesim.out_port sim "part2_result" in

  let cycles = ref 0 in
  let cycle () =
    incr cycles;
    Cyclesim.cycle sim
  in

  let set_range ~valid ~from_ ~to_ ~last =
    range_valid := if valid then Bits.one 1 else Bits.zero 1;
    range_from := Bits.of_int ~width:64 from_;
    range_to := Bits.of_int ~width:64 to_;
    range_last := if last then Bits.one 1 else Bits.zero 1
  in
  let set_id ~valid ~v ~last =
    id_valid := if valid then Bits.one 1 else Bits.zero 1;
    id := Bits.of_int ~width:64 v;
    id_last := if last then Bits.one 1 else Bits.zero 1
  in

  Cyclesim.reset sim;
  clear := Bits.one 1;
  load := Bits.zero 1;
  set_range ~valid:false ~from_:0 ~to_:0 ~last:false;
  set_id ~valid:false ~v:0 ~last:false;
  cycle ();
  clear := Bits.zero 1;
  load := Bits.one 1;
  cycle ();
  load := Bits.zero 1;

  List.iteri day5_ranges ~f:(fun idx (from_, to_) ->
    while Bits.to_int !range_ready = 0 do
      cycle ()
    done;
    let last = idx = List.length day5_ranges - 1 in
    set_range ~valid:true ~from_ ~to_ ~last;
    cycle ();
    set_range ~valid:false ~from_:0 ~to_:0 ~last:false);

  List.iteri day5_ids ~f:(fun idx v ->
    while Bits.to_int !id_ready = 0 do
      cycle ()
    done;
    let last = idx = List.length day5_ids - 1 in
    set_id ~valid:true ~v ~last;
    cycle ();
    set_id ~valid:false ~v:0 ~last:false);

  let rec run n =
    if n > 2000 then failwith "Day5 sim timeout";
    cycle ();
    if Bits.to_int !done_ = 1 then () else run (n + 1)
  in
  run 0;

  let ok = Bits.to_int !part1 = exp_p1 && Bits.to_int !part2 = exp_p2 in
  { design = "day5"; day = 5; variant = "day5_opt_c"; work_units = List.length day5_ranges + List.length day5_ids; cycles = !cycles; ok }

let run_day6_opt_b () : bench_result =
  let blocks =
    [ ( true
      , [ [| Some 1; None; Some 3; Some 0 |]
        ; [| Some 2; Some 4; None; Some 5 |]
        ; [| None; Some 1; Some 7; None |]
        ] )
    ; ( false
      , [ [| Some 9; Some 0; None; Some 1 |]
        ; [| Some 8; None; Some 2; Some 3 |]
        ] )
    ]
  in
  let exp_p1, exp_p2 =
    let acc (n : int64) (cell : int option) =
      match cell with
      | None -> n
      | Some d -> Stdlib.Int64.(add (mul n 10L) (of_int d))
    in
    let block_eval (plus, cols) : int64 * int64 =
      let row_nums = Array.create ~len:4 0L in
      let col_agg = ref (if plus then 0L else 1L) in
      List.iter cols ~f:(fun col ->
        for r = 0 to 3 do
          row_nums.(r) <- acc row_nums.(r) col.(r)
        done;
        let col_num = ref 0L in
        for r = 0 to 3 do
          col_num := acc !col_num col.(r)
        done;
        col_agg :=
          if plus then Stdlib.Int64.add !col_agg !col_num
          else Stdlib.Int64.mul !col_agg !col_num);
      let rows_res =
        if plus then Array.fold row_nums ~init:0L ~f:Stdlib.Int64.add
        else Array.fold row_nums ~init:1L ~f:Stdlib.Int64.mul
      in
      rows_res, !col_agg
    in
    List.fold blocks ~init:(0L, 0L) ~f:(fun (a, b) blk ->
      let x, y = block_eval blk in
      Stdlib.Int64.(add a x, add b y))
  in

  let circuit =
    Circuit.create_with_interface
      (module Day6_opt_b_streaming_line_buffer_pipeline.I)
      (module Day6_opt_b_streaming_line_buffer_pipeline.O)
      ~name:"day6_opt_b"
      Day6_opt_b_streaming_line_buffer_pipeline.create
  in
  let sim = Cyclesim.create circuit in
  let clear = Cyclesim.in_port sim "clear" in
  let load = Cyclesim.in_port sim "load" in
  let col_valid = Cyclesim.in_port sim "col_valid" in
  let block_start = Cyclesim.in_port sim "block_start" in
  let block_plus = Cyclesim.in_port sim "block_plus" in
  let col_last = Cyclesim.in_port sim "col_last" in
  let frame_last = Cyclesim.in_port sim "frame_last" in
  let r0_digit = Cyclesim.in_port sim "r0_digit" in
  let r0_space = Cyclesim.in_port sim "r0_space" in
  let r1_digit = Cyclesim.in_port sim "r1_digit" in
  let r1_space = Cyclesim.in_port sim "r1_space" in
  let r2_digit = Cyclesim.in_port sim "r2_digit" in
  let r2_space = Cyclesim.in_port sim "r2_space" in
  let r3_digit = Cyclesim.in_port sim "r3_digit" in
  let r3_space = Cyclesim.in_port sim "r3_space" in
  let done_ = Cyclesim.out_port sim "done_" in
  let p1 = Cyclesim.out_port sim "part1_result" in
  let p2 = Cyclesim.out_port sim "part2_result" in

  let cycles = ref 0 in
  let cycle () =
    incr cycles;
    Cyclesim.cycle sim
  in

  let drive_cell digit_port space_port = function
    | None ->
      digit_port := Bits.zero 4;
      space_port := Bits.one 1
    | Some d ->
      digit_port := Bits.of_int ~width:4 d;
      space_port := Bits.zero 1
  in

  Cyclesim.reset sim;
  clear := Bits.one 1;
  load := Bits.zero 1;
  col_valid := Bits.zero 1;
  block_start := Bits.zero 1;
  block_plus := Bits.zero 1;
  col_last := Bits.zero 1;
  frame_last := Bits.zero 1;
  cycle ();
  clear := Bits.zero 1;
  load := Bits.one 1;
  cycle ();
  load := Bits.zero 1;

  List.iteri blocks ~f:(fun bi (plus, cols) ->
    List.iteri cols ~f:(fun ci col ->
      col_valid := Bits.one 1;
      block_start := if ci = 0 then Bits.one 1 else Bits.zero 1;
      block_plus := if plus then Bits.one 1 else Bits.zero 1;
      let is_last_col = ci = List.length cols - 1 in
      col_last := if is_last_col then Bits.one 1 else Bits.zero 1;
      frame_last :=
        if bi = List.length blocks - 1 && is_last_col then Bits.one 1 else Bits.zero 1;
      drive_cell r0_digit r0_space col.(0);
      drive_cell r1_digit r1_space col.(1);
      drive_cell r2_digit r2_space col.(2);
      drive_cell r3_digit r3_space col.(3);
      cycle ();
      col_valid := Bits.zero 1;
      block_start := Bits.zero 1;
      col_last := Bits.zero 1;
      frame_last := Bits.zero 1));

  let rec run n =
    if n > 500 then failwith "Day6 sim timeout";
    cycle ();
    if Bits.to_int !done_ = 1 then () else run (n + 1)
  in
  run 0;

  let ok = Int64.equal (Bits.to_int64 !p1) exp_p1 && Int64.equal (Bits.to_int64 !p2) exp_p2 in
  let total_cols = List.sum (module Int) blocks ~f:(fun (_plus, cols) -> List.length cols) in
  { design = "day6"; day = 6; variant = "day6_opt_b"; work_units = total_cols; cycles = !cycles; ok }

let run_day6_opt_c () : bench_result =
  let blocks =
    [ ( true
      , [ [| Some 1; None; Some 3; Some 0 |]
        ; [| Some 2; Some 4; None; Some 5 |]
        ; [| None; Some 1; Some 7; None |]
        ] )
    ; ( false
      , [ [| Some 9; Some 0; None; Some 1 |]
        ; [| Some 8; None; Some 2; Some 3 |]
        ] )
    ]
  in
  let exp_p1, exp_p2 =
    let acc (n : int64) (cell : int option) =
      match cell with
      | None -> n
      | Some d -> Stdlib.Int64.(add (mul n 10L) (of_int d))
    in
    let block_eval (plus, cols) : int64 * int64 =
      let row_nums = Array.create ~len:4 0L in
      let col_agg = ref (if plus then 0L else 1L) in
      List.iter cols ~f:(fun col ->
        for r = 0 to 3 do
          row_nums.(r) <- acc row_nums.(r) col.(r)
        done;
        let col_num = ref 0L in
        for r = 0 to 3 do
          col_num := acc !col_num col.(r)
        done;
        col_agg :=
          if plus then Stdlib.Int64.add !col_agg !col_num
          else Stdlib.Int64.mul !col_agg !col_num);
      let rows_res =
        if plus then Array.fold row_nums ~init:0L ~f:Stdlib.Int64.add
        else Array.fold row_nums ~init:1L ~f:Stdlib.Int64.mul
      in
      rows_res, !col_agg
    in
    List.fold blocks ~init:(0L, 0L) ~f:(fun (a, b) blk ->
      let x, y = block_eval blk in
      Stdlib.Int64.(add a x, add b y))
  in

  let circuit =
    Circuit.create_with_interface
      (module Day6_opt_c_max_parallel_block_eval.I)
      (module Day6_opt_c_max_parallel_block_eval.O)
      ~name:"day6_opt_c"
      Day6_opt_c_max_parallel_block_eval.create
  in
  let sim = Cyclesim.create circuit in
  let clear = Cyclesim.in_port sim "clear" in
  let load = Cyclesim.in_port sim "load" in
  let col_valid = Cyclesim.in_port sim "col_valid" in
  let block_start = Cyclesim.in_port sim "block_start" in
  let block_plus = Cyclesim.in_port sim "block_plus" in
  let col_last = Cyclesim.in_port sim "col_last" in
  let frame_last = Cyclesim.in_port sim "frame_last" in
  let r0_digit = Cyclesim.in_port sim "r0_digit" in
  let r0_space = Cyclesim.in_port sim "r0_space" in
  let r1_digit = Cyclesim.in_port sim "r1_digit" in
  let r1_space = Cyclesim.in_port sim "r1_space" in
  let r2_digit = Cyclesim.in_port sim "r2_digit" in
  let r2_space = Cyclesim.in_port sim "r2_space" in
  let r3_digit = Cyclesim.in_port sim "r3_digit" in
  let r3_space = Cyclesim.in_port sim "r3_space" in
  let done_ = Cyclesim.out_port sim "done_" in
  let p1 = Cyclesim.out_port sim "part1_result" in
  let p2 = Cyclesim.out_port sim "part2_result" in

  let cycles = ref 0 in
  let cycle () =
    incr cycles;
    Cyclesim.cycle sim
  in

  let drive_cell digit_port space_port = function
    | None ->
      digit_port := Bits.zero 4;
      space_port := Bits.one 1
    | Some d ->
      digit_port := Bits.of_int ~width:4 d;
      space_port := Bits.zero 1
  in

  Cyclesim.reset sim;
  clear := Bits.one 1;
  load := Bits.zero 1;
  col_valid := Bits.zero 1;
  block_start := Bits.zero 1;
  block_plus := Bits.zero 1;
  col_last := Bits.zero 1;
  frame_last := Bits.zero 1;
  cycle ();
  clear := Bits.zero 1;
  load := Bits.one 1;
  cycle ();
  load := Bits.zero 1;

  List.iteri blocks ~f:(fun bi (plus, cols) ->
    List.iteri cols ~f:(fun ci col ->
      col_valid := Bits.one 1;
      block_start := if ci = 0 then Bits.one 1 else Bits.zero 1;
      block_plus := if plus then Bits.one 1 else Bits.zero 1;
      let is_last_col = ci = List.length cols - 1 in
      col_last := if is_last_col then Bits.one 1 else Bits.zero 1;
      frame_last :=
        if bi = List.length blocks - 1 && is_last_col then Bits.one 1 else Bits.zero 1;
      drive_cell r0_digit r0_space col.(0);
      drive_cell r1_digit r1_space col.(1);
      drive_cell r2_digit r2_space col.(2);
      drive_cell r3_digit r3_space col.(3);
      cycle ();
      col_valid := Bits.zero 1;
      block_start := Bits.zero 1;
      col_last := Bits.zero 1;
      frame_last := Bits.zero 1));

  let rec run n =
    if n > 500 then failwith "Day6 sim timeout";
    cycle ();
    if Bits.to_int !done_ = 1 then () else run (n + 1)
  in
  run 0;

  let ok = Int64.equal (Bits.to_int64 !p1) exp_p1 && Int64.equal (Bits.to_int64 !p2) exp_p2 in
  let total_cols = List.sum (module Int) blocks ~f:(fun (_plus, cols) -> List.length cols) in
  { design = "day6"; day = 6; variant = "day6_opt_c"; work_units = total_cols; cycles = !cycles; ok }

let run_day6_opt_a () : bench_result =
  let day6_reference (blocks : (bool * (int option array) list) list) : int64 * int64 =
    let acc (n : int64) (cell : int option) =
      match cell with
      | None -> n
      | Some d -> Stdlib.Int64.(add (mul n 10L) (of_int d))
    in
    let block_eval (plus, cols) : int64 * int64 =
      let row_nums = Array.create ~len:4 0L in
      let col_agg = ref (if plus then 0L else 1L) in
      List.iter cols ~f:(fun col ->
        for r = 0 to 3 do
          row_nums.(r) <- acc row_nums.(r) col.(r)
        done;
        let col_num = ref 0L in
        for r = 0 to 3 do
          col_num := acc !col_num col.(r)
        done;
        col_agg :=
          if plus then Stdlib.Int64.add !col_agg !col_num
          else Stdlib.Int64.mul !col_agg !col_num);
      let rows_res =
        if plus then Array.fold row_nums ~init:0L ~f:Stdlib.Int64.add
        else Array.fold row_nums ~init:1L ~f:Stdlib.Int64.mul
      in
      rows_res, !col_agg
    in
    List.fold blocks ~init:(0L, 0L) ~f:(fun (a, b) blk ->
      let x, y = block_eval blk in
      Stdlib.Int64.(add a x, add b y))
  in

  let blocks =
    [ ( true
      , [ [| Some 1; None; Some 3; Some 0 |]
        ; [| Some 2; Some 4; None; Some 5 |]
        ; [| None; Some 1; Some 7; None |]
        ] )
    ; ( false
      , [ [| Some 9; Some 0; None; Some 1 |]
        ; [| Some 8; None; Some 2; Some 3 |]
        ] )
    ]
  in
  let exp_p1, exp_p2 = day6_reference blocks in

  let circuit =
    Circuit.create_with_interface
      (module Day6_opt_a_block_stream.I)
      (module Day6_opt_a_block_stream.O)
      ~name:"day6_opt_a"
      Day6_opt_a_block_stream.create
  in
  let sim = Cyclesim.create circuit in

  let clear = Cyclesim.in_port sim "clear" in
  let load = Cyclesim.in_port sim "load" in
  let col_valid = Cyclesim.in_port sim "col_valid" in
  let block_start = Cyclesim.in_port sim "block_start" in
  let block_plus = Cyclesim.in_port sim "block_plus" in
  let col_last = Cyclesim.in_port sim "col_last" in
  let frame_last = Cyclesim.in_port sim "frame_last" in
  let r0_digit = Cyclesim.in_port sim "r0_digit" in
  let r0_space = Cyclesim.in_port sim "r0_space" in
  let r1_digit = Cyclesim.in_port sim "r1_digit" in
  let r1_space = Cyclesim.in_port sim "r1_space" in
  let r2_digit = Cyclesim.in_port sim "r2_digit" in
  let r2_space = Cyclesim.in_port sim "r2_space" in
  let r3_digit = Cyclesim.in_port sim "r3_digit" in
  let r3_space = Cyclesim.in_port sim "r3_space" in
  let done_ = Cyclesim.out_port sim "done_" in
  let p1 = Cyclesim.out_port sim "part1_result" in
  let p2 = Cyclesim.out_port sim "part2_result" in

  let cycles = ref 0 in
  let cycle () =
    incr cycles;
    Cyclesim.cycle sim
  in

  let drive_cell digit_port space_port = function
    | None ->
      digit_port := Bits.zero 4;
      space_port := Bits.one 1
    | Some d ->
      digit_port := Bits.of_int ~width:4 d;
      space_port := Bits.zero 1
  in

  Cyclesim.reset sim;
  clear := Bits.one 1;
  load := Bits.zero 1;
  col_valid := Bits.zero 1;
  block_start := Bits.zero 1;
  block_plus := Bits.zero 1;
  col_last := Bits.zero 1;
  frame_last := Bits.zero 1;
  cycle ();
  clear := Bits.zero 1;
  load := Bits.one 1;
  cycle ();
  load := Bits.zero 1;

  List.iteri blocks ~f:(fun bi (plus, cols) ->
    List.iteri cols ~f:(fun ci col ->
      col_valid := Bits.one 1;
      block_start := if ci = 0 then Bits.one 1 else Bits.zero 1;
      block_plus := if plus then Bits.one 1 else Bits.zero 1;
      let is_last_col = ci = List.length cols - 1 in
      col_last := if is_last_col then Bits.one 1 else Bits.zero 1;
      frame_last :=
        if bi = List.length blocks - 1 && is_last_col then Bits.one 1 else Bits.zero 1;
      drive_cell r0_digit r0_space col.(0);
      drive_cell r1_digit r1_space col.(1);
      drive_cell r2_digit r2_space col.(2);
      drive_cell r3_digit r3_space col.(3);
      cycle ();
      col_valid := Bits.zero 1;
      block_start := Bits.zero 1;
      col_last := Bits.zero 1;
      frame_last := Bits.zero 1));

  let rec run n =
    if n > 500 then failwith "Day6 sim timeout";
    cycle ();
    if Bits.to_int !done_ = 1 then () else run (n + 1)
  in
  run 0;

  let ok = Int64.equal (Bits.to_int64 !p1) exp_p1 && Int64.equal (Bits.to_int64 !p2) exp_p2 in
  let total_cols = List.sum (module Int) blocks ~f:(fun (_plus, cols) -> List.length cols) in
  { design = "day6"; day = 6; variant = "day6_opt_a"; work_units = total_cols; cycles = !cycles; ok }

let run_day7_opt_a () : bench_result =
  let day7_reference ~(width : int) ~(rows : int list list) : int * int =
    let center = width / 2 in
    let timelines = Array.create ~len:width 0 in
    timelines.(center) <- 1;
    let splits = ref 0 in
    List.iteri rows ~f:(fun y hat_positions ->
      let has_hat = Array.create ~len:width false in
      List.iter hat_positions ~f:(fun x -> has_hat.(x) <- true);
      let x0 = center - y in
      let x1 = center + y in
      let x = ref x0 in
      while !x <= x1 do
        let count = timelines.(!x) in
        if count > 0 && has_hat.(!x) then (
          incr splits;
          timelines.(!x) <- 0;
          timelines.(!x - 1) <- timelines.(!x - 1) + count;
          timelines.(!x + 1) <- timelines.(!x + 1) + count);
        x := !x + 2
      done);
    !splits, Array.fold timelines ~init:0 ~f:( + )
  in

  let bits_of_positions (positions : int list) : Bits.t =
    let set = Int.Set.of_list positions in
    Bits.concat_lsb
      (List.init 256 ~f:(fun j -> if Set.mem set j then Bits.one 1 else Bits.zero 1))
  in

  let width = 9 in
  let rows = [ [ 4 ]; [ 3; 5 ]; [ 2 ]; [ 6 ] ] in
  let exp_p1, exp_p2 = day7_reference ~width ~rows in

  let circuit =
    Circuit.create_with_interface
      (module Day7_opt_a_timeline_split.I)
      (module Day7_opt_a_timeline_split.O)
      ~name:"day7_opt_a"
      Day7_opt_a_timeline_split.create
  in
  let sim = Cyclesim.create circuit in
  let clear = Cyclesim.in_port sim "clear" in
  let load = Cyclesim.in_port sim "load" in
  let width_in = Cyclesim.in_port sim "width" in
  let row_valid = Cyclesim.in_port sim "row_valid" in
  let row_bits = Cyclesim.in_port sim "row_bits" in
  let row_last = Cyclesim.in_port sim "row_last" in
  let ready = Cyclesim.out_port sim "ready" in
  let done_ = Cyclesim.out_port sim "done_" in
  let p1 = Cyclesim.out_port sim "part1_result" in
  let p2 = Cyclesim.out_port sim "part2_result" in

  let cycles = ref 0 in
  let cycle () =
    incr cycles;
    Cyclesim.cycle sim
  in

  Cyclesim.reset sim;
  clear := Bits.one 1;
  load := Bits.zero 1;
  row_valid := Bits.zero 1;
  row_last := Bits.zero 1;
  width_in := Bits.of_int ~width:8 width;
  row_bits := Bits.zero 256;
  cycle ();
  clear := Bits.zero 1;
  load := Bits.one 1;
  cycle ();
  load := Bits.zero 1;

  List.iteri rows ~f:(fun idx hats ->
    while Bits.to_int !ready = 0 do
      cycle ()
    done;
    row_valid := Bits.one 1;
    row_bits := bits_of_positions hats;
    row_last := if idx = List.length rows - 1 then Bits.one 1 else Bits.zero 1;
    cycle ();
    row_valid := Bits.zero 1;
    row_last := Bits.zero 1);

  let rec run n =
    if n > 2000 then failwith "Day7 sim timeout";
    cycle ();
    if Bits.to_int !done_ = 1 then () else run (n + 1)
  in
  run 0;

  let ok = Bits.to_int !p1 = exp_p1 && Bits.to_int !p2 = exp_p2 in
  { design = "day7"; day = 7; variant = "day7_opt_a"; work_units = List.length rows; cycles = !cycles; ok }

let run_day7_opt_b () : bench_result =
  let day7_reference ~(width : int) ~(rows : int list list) : int * int =
    let center = width / 2 in
    let timelines = Array.create ~len:width 0 in
    timelines.(center) <- 1;
    let splits = ref 0 in
    List.iteri rows ~f:(fun y hat_positions ->
      let has_hat = Array.create ~len:width false in
      List.iter hat_positions ~f:(fun x -> has_hat.(x) <- true);
      let x0 = center - y in
      let x1 = center + y in
      let x = ref x0 in
      while !x <= x1 do
        let count = timelines.(!x) in
        if count > 0 && has_hat.(!x) then (
          incr splits;
          timelines.(!x) <- 0;
          timelines.(!x - 1) <- timelines.(!x - 1) + count;
          timelines.(!x + 1) <- timelines.(!x + 1) + count);
        x := !x + 2
      done)
    ;
    !splits, Array.fold timelines ~init:0 ~f:( + )
  in

  let bits_of_positions (positions : int list) : Bits.t =
    let set = Int.Set.of_list positions in
    Bits.concat_lsb
      (List.init 256 ~f:(fun j -> if Set.mem set j then Bits.one 1 else Bits.zero 1))
  in

  let width = 9 in
  let rows = [ [ 4 ]; [ 3; 5 ]; [ 2 ]; [ 6 ] ] in
  let exp_p1, exp_p2 = day7_reference ~width ~rows in

  let circuit =
    Circuit.create_with_interface
      (module Day7_opt_b_wide_simd_row_update.I)
      (module Day7_opt_b_wide_simd_row_update.O)
      ~name:"day7_opt_b"
      Day7_opt_b_wide_simd_row_update.create
  in
  let sim = Cyclesim.create circuit in
  let clear = Cyclesim.in_port sim "clear" in
  let load = Cyclesim.in_port sim "load" in
  let width_in = Cyclesim.in_port sim "width" in
  let row_valid = Cyclesim.in_port sim "row_valid" in
  let row_bits = Cyclesim.in_port sim "row_bits" in
  let row_last = Cyclesim.in_port sim "row_last" in
  let ready = Cyclesim.out_port sim "ready" in
  let done_ = Cyclesim.out_port sim "done_" in
  let p1 = Cyclesim.out_port sim "part1_result" in
  let p2 = Cyclesim.out_port sim "part2_result" in

  let cycles = ref 0 in
  let cycle () =
    incr cycles;
    Cyclesim.cycle sim
  in

  Cyclesim.reset sim;
  clear := Bits.one 1;
  load := Bits.zero 1;
  row_valid := Bits.zero 1;
  row_last := Bits.zero 1;
  width_in := Bits.of_int ~width:8 width;
  row_bits := Bits.zero 256;
  cycle ();
  clear := Bits.zero 1;
  load := Bits.one 1;
  cycle ();
  load := Bits.zero 1;

  List.iteri rows ~f:(fun idx hats ->
    while Bits.to_int !ready = 0 do
      cycle ()
    done;
    row_valid := Bits.one 1;
    row_bits := bits_of_positions hats;
    row_last := if idx = List.length rows - 1 then Bits.one 1 else Bits.zero 1;
    cycle ();
    row_valid := Bits.zero 1;
    row_last := Bits.zero 1);

  let rec run n =
    if n > 2000 then failwith "Day7 opt B sim timeout";
    cycle ();
    if Bits.to_int !done_ = 1 then () else run (n + 1)
  in
  run 0;

  let ok = Bits.to_int !p1 = exp_p1 && Bits.to_int !p2 = exp_p2 in
  { design = "day7"; day = 7; variant = "day7_opt_b"; work_units = List.length rows; cycles = !cycles; ok }

let run_day8_opt_a () : bench_result =
  let circuit =
    Circuit.create_with_interface
      (module Day8_opt_a_streaming_union_find.I)
      (module Day8_opt_a_streaming_union_find.O)
      ~name:"day8_opt_a"
      Day8_opt_a_streaming_union_find.create
  in
  let sim = Cyclesim.create circuit in
  let clear = Cyclesim.in_port sim "clear" in
  let load = Cyclesim.in_port sim "load" in
  let n_nodes = Cyclesim.in_port sim "n_nodes" in
  let x0_valid = Cyclesim.in_port sim "x0_valid" in
  let x0_value = Cyclesim.in_port sim "x0_value" in
  let x0_last = Cyclesim.in_port sim "x0_last" in
  let edge_valid = Cyclesim.in_port sim "edge_valid" in
  let edge_i = Cyclesim.in_port sim "edge_i" in
  let edge_j = Cyclesim.in_port sim "edge_j" in
  let edge_last = Cyclesim.in_port sim "edge_last" in
  let edge_phase = Cyclesim.in_port sim "edge_phase" in
  let x0_ready = Cyclesim.out_port sim "x0_ready" in
  let edge_ready = Cyclesim.out_port sim "edge_ready" in
  let done_ = Cyclesim.out_port sim "done_" in
  let p1 = Cyclesim.out_port sim "part1_result" in
  let p2 = Cyclesim.out_port sim "part2_result" in

  let cycles = ref 0 in
  let cycle () =
    incr cycles;
    Cyclesim.cycle sim
  in

  Cyclesim.reset sim;
  clear := Bits.one 1;
  load := Bits.zero 1;
  n_nodes := Bits.of_int ~width:8 5;
  x0_valid := Bits.zero 1;
  x0_last := Bits.zero 1;
  x0_value := Bits.zero 32;
  edge_valid := Bits.zero 1;
  edge_i := Bits.zero 8;
  edge_j := Bits.zero 8;
  edge_last := Bits.zero 1;
  edge_phase := Bits.zero 1;
  cycle ();
  clear := Bits.zero 1;
  load := Bits.one 1;
  cycle ();
  load := Bits.zero 1;

  let x0s = [ 2; 3; 5; 7; 11 ] in
  List.iteri x0s ~f:(fun idx v ->
    while Bits.to_int !x0_ready = 0 do
      cycle ()
    done;
    x0_valid := Bits.one 1;
    x0_value := Bits.of_int ~width:32 v;
    x0_last := if idx = List.length x0s - 1 then Bits.one 1 else Bits.zero 1;
    cycle ();
    x0_valid := Bits.zero 1;
    x0_last := Bits.zero 1);

  let send_edges ~phase edges =
    edge_phase := Bits.of_int ~width:1 phase;
    List.iteri edges ~f:(fun idx (a, b) ->
      while Bits.to_int !edge_ready = 0 do
        cycle ()
      done;
      edge_valid := Bits.one 1;
      edge_i := Bits.of_int ~width:8 a;
      edge_j := Bits.of_int ~width:8 b;
      edge_last := if idx = List.length edges - 1 then Bits.one 1 else Bits.zero 1;
      cycle ();
      edge_valid := Bits.zero 1;
      edge_last := Bits.zero 1)
  in

  let edges0 = [ 0, 1; 2, 3 ] in
  let edges1 = [ 0, 1; 1, 2; 2, 3; 3, 4 ] in
  send_edges ~phase:0 edges0;
  send_edges ~phase:1 edges1;

  let rec run n =
    if n > 5000 then failwith "Day8 sim timeout";
    cycle ();
    if Bits.to_int !done_ = 1 then () else run (n + 1)
  in
  run 0;

  let ok = Bits.to_int !p1 = 4 && Bits.to_int !p2 = 77 in
  { design = "day8"; day = 8; variant = "day8_opt_a"; work_units = List.length x0s + List.length edges0 + List.length edges1; cycles = !cycles; ok }

let run_day8_opt_b () : bench_result =
  let circuit =
    Circuit.create_with_interface
      (module Day8_opt_b_topk_edges_only.I)
      (module Day8_opt_b_topk_edges_only.O)
      ~name:"day8_opt_b"
      Day8_opt_b_topk_edges_only.create
  in
  let sim = Cyclesim.create circuit in
  let clear = Cyclesim.in_port sim "clear" in
  let load = Cyclesim.in_port sim "load" in
  let n_nodes = Cyclesim.in_port sim "n_nodes" in
  let x0_valid = Cyclesim.in_port sim "x0_valid" in
  let x0_value = Cyclesim.in_port sim "x0_value" in
  let x0_last = Cyclesim.in_port sim "x0_last" in
  let edge_valid = Cyclesim.in_port sim "edge_valid" in
  let edge_i = Cyclesim.in_port sim "edge_i" in
  let edge_j = Cyclesim.in_port sim "edge_j" in
  let edge_last = Cyclesim.in_port sim "edge_last" in
  let edge_phase = Cyclesim.in_port sim "edge_phase" in
  let x0_ready = Cyclesim.out_port sim "x0_ready" in
  let edge_ready = Cyclesim.out_port sim "edge_ready" in
  let done_ = Cyclesim.out_port sim "done_" in
  let p1 = Cyclesim.out_port sim "part1_result" in
  let p2 = Cyclesim.out_port sim "part2_result" in

  let cycles = ref 0 in
  let cycle () =
    incr cycles;
    Cyclesim.cycle sim
  in

  Cyclesim.reset sim;
  clear := Bits.one 1;
  load := Bits.zero 1;
  n_nodes := Bits.of_int ~width:8 5;
  x0_valid := Bits.zero 1;
  x0_last := Bits.zero 1;
  x0_value := Bits.zero 32;
  edge_valid := Bits.zero 1;
  edge_i := Bits.zero 8;
  edge_j := Bits.zero 8;
  edge_last := Bits.zero 1;
  edge_phase := Bits.zero 1;
  cycle ();
  clear := Bits.zero 1;
  load := Bits.one 1;
  cycle ();
  load := Bits.zero 1;

  let x0s = [ 2; 3; 5; 7; 11 ] in
  List.iteri x0s ~f:(fun idx v ->
    while Bits.to_int !x0_ready = 0 do
      cycle ()
    done;
    x0_valid := Bits.one 1;
    x0_value := Bits.of_int ~width:32 v;
    x0_last := if idx = List.length x0s - 1 then Bits.one 1 else Bits.zero 1;
    cycle ();
    x0_valid := Bits.zero 1;
    x0_last := Bits.zero 1);

  let send_edges ~phase edges =
    edge_phase := Bits.of_int ~width:1 phase;
    List.iteri edges ~f:(fun idx (a, b) ->
      while Bits.to_int !edge_ready = 0 do
        cycle ()
      done;
      edge_valid := Bits.one 1;
      edge_i := Bits.of_int ~width:8 a;
      edge_j := Bits.of_int ~width:8 b;
      edge_last := if idx = List.length edges - 1 then Bits.one 1 else Bits.zero 1;
      cycle ();
      edge_valid := Bits.zero 1;
      edge_last := Bits.zero 1)
  in

  let edges0 = [ 0, 1; 2, 3 ] in
  let edges1 = [ 0, 1; 1, 2; 2, 3; 3, 4 ] in
  send_edges ~phase:0 edges0;
  send_edges ~phase:1 edges1;

  let rec run n =
    if n > 5000 then failwith "Day8 sim timeout";
    cycle ();
    if Bits.to_int !done_ = 1 then () else run (n + 1)
  in
  run 0;

  let ok = Bits.to_int !p1 = 4 && Bits.to_int !p2 = 77 in
  { design = "day8"
  ; day = 8
  ; variant = "day8_opt_b"
  ; work_units = List.length x0s + List.length edges0 + List.length edges1
  ; cycles = !cycles
  ; ok
  }

let run_day8_opt_c () : bench_result =
  let circuit =
    Circuit.create_with_interface
      (module Day8_opt_c_spatial_partitioning.I)
      (module Day8_opt_c_spatial_partitioning.O)
      ~name:"day8_opt_c"
      Day8_opt_c_spatial_partitioning.create
  in
  let sim = Cyclesim.create circuit in
  let clear = Cyclesim.in_port sim "clear" in
  let load = Cyclesim.in_port sim "load" in
  let n_nodes = Cyclesim.in_port sim "n_nodes" in
  let x0_valid = Cyclesim.in_port sim "x0_valid" in
  let x0_value = Cyclesim.in_port sim "x0_value" in
  let x0_last = Cyclesim.in_port sim "x0_last" in
  let edge_valid = Cyclesim.in_port sim "edge_valid" in
  let edge_i = Cyclesim.in_port sim "edge_i" in
  let edge_j = Cyclesim.in_port sim "edge_j" in
  let edge_last = Cyclesim.in_port sim "edge_last" in
  let edge_phase = Cyclesim.in_port sim "edge_phase" in
  let x0_ready = Cyclesim.out_port sim "x0_ready" in
  let edge_ready = Cyclesim.out_port sim "edge_ready" in
  let done_ = Cyclesim.out_port sim "done_" in
  let p1 = Cyclesim.out_port sim "part1_result" in
  let p2 = Cyclesim.out_port sim "part2_result" in

  let cycles = ref 0 in
  let cycle () =
    incr cycles;
    Cyclesim.cycle sim
  in

  Cyclesim.reset sim;
  clear := Bits.one 1;
  load := Bits.zero 1;
  n_nodes := Bits.of_int ~width:8 5;
  x0_valid := Bits.zero 1;
  x0_last := Bits.zero 1;
  x0_value := Bits.zero 32;
  edge_valid := Bits.zero 1;
  edge_i := Bits.zero 8;
  edge_j := Bits.zero 8;
  edge_last := Bits.zero 1;
  edge_phase := Bits.zero 1;
  cycle ();
  clear := Bits.zero 1;
  load := Bits.one 1;
  cycle ();
  load := Bits.zero 1;

  let x0s = [ 2; 3; 5; 7; 11 ] in
  List.iteri x0s ~f:(fun idx v ->
    while Bits.to_int !x0_ready = 0 do
      cycle ()
    done;
    x0_valid := Bits.one 1;
    x0_value := Bits.of_int ~width:32 v;
    x0_last := if idx = List.length x0s - 1 then Bits.one 1 else Bits.zero 1;
    cycle ();
    x0_valid := Bits.zero 1;
    x0_last := Bits.zero 1);

  let send_edges ~phase edges =
    edge_phase := Bits.of_int ~width:1 phase;
    List.iteri edges ~f:(fun idx (a, b) ->
      while Bits.to_int !edge_ready = 0 do
        cycle ()
      done;
      edge_valid := Bits.one 1;
      edge_i := Bits.of_int ~width:8 a;
      edge_j := Bits.of_int ~width:8 b;
      edge_last := if idx = List.length edges - 1 then Bits.one 1 else Bits.zero 1;
      cycle ();
      edge_valid := Bits.zero 1;
      edge_last := Bits.zero 1)
  in

  let edges0 = [ 0, 1; 2, 3 ] in
  let edges1 = [ 0, 1; 1, 2; 2, 3; 3, 4 ] in
  send_edges ~phase:0 edges0;
  send_edges ~phase:1 edges1;

  let rec run n =
    if n > 5000 then failwith "Day8 sim timeout";
    cycle ();
    if Bits.to_int !done_ = 1 then () else run (n + 1)
  in
  run 0;

  let ok = Bits.to_int !p1 = 4 && Bits.to_int !p2 = 77 in
  { design = "day8"
  ; day = 8
  ; variant = "day8_opt_c"
  ; work_units = List.length x0s + List.length edges0 + List.length edges1
  ; cycles = !cycles
  ; ok
  }

let run_day9_opt_a () : bench_result =
  let tiles = [ 0, 0; 0, 1; 2, 0; 2, 1 ] in
  let circuit =
    Circuit.create_with_interface
      (module Day9_opt_a_pairwise_max_area.I)
      (module Day9_opt_a_pairwise_max_area.O)
      ~name:"day9_opt_a"
      Day9_opt_a_pairwise_max_area.create
  in
  let sim = Cyclesim.create circuit in
  let clear = Cyclesim.in_port sim "clear" in
  let load = Cyclesim.in_port sim "load" in
  let tile_valid = Cyclesim.in_port sim "tile_valid" in
  let x = Cyclesim.in_port sim "x" in
  let y = Cyclesim.in_port sim "y" in
  let tile_last = Cyclesim.in_port sim "tile_last" in
  let done_ = Cyclesim.out_port sim "done_" in
  let p1 = Cyclesim.out_port sim "part1_result" in

  let cycles = ref 0 in
  let cycle () =
    incr cycles;
    Cyclesim.cycle sim
  in

  Cyclesim.reset sim;
  clear := Bits.one 1;
  load := Bits.zero 1;
  tile_valid := Bits.zero 1;
  tile_last := Bits.zero 1;
  cycle ();
  clear := Bits.zero 1;
  load := Bits.one 1;
  cycle ();
  load := Bits.zero 1;

  List.iteri tiles ~f:(fun idx (xx, yy) ->
    tile_valid := Bits.one 1;
    x := Bits.of_int ~width:64 xx;
    y := Bits.of_int ~width:64 yy;
    tile_last := if idx = List.length tiles - 1 then Bits.one 1 else Bits.zero 1;
    cycle ();
    tile_valid := Bits.zero 1;
    tile_last := Bits.zero 1);

  let rec run n =
    if n > 5000 then failwith "Day9 sim timeout";
    cycle ();
    if Bits.to_int !done_ = 1 then () else run (n + 1)
  in
  run 0;

  let ok = Bits.to_int !p1 = 6 in
  { design = "day9"; day = 9; variant = "day9_opt_a"; work_units = List.length tiles; cycles = !cycles; ok }

let run_day9_opt_b () : bench_result =
  let tiles = [ 0, 0; 0, 1; 2, 0; 2, 1 ] in
  let circuit =
    Circuit.create_with_interface
      (module Day9_opt_b_scanline_interval_machine.I)
      (module Day9_opt_b_scanline_interval_machine.O)
      ~name:"day9_opt_b"
      Day9_opt_b_scanline_interval_machine.create
  in
  let sim = Cyclesim.create circuit in
  let clear = Cyclesim.in_port sim "clear" in
  let load = Cyclesim.in_port sim "load" in
  let tile_valid = Cyclesim.in_port sim "tile_valid" in
  let x = Cyclesim.in_port sim "x" in
  let y = Cyclesim.in_port sim "y" in
  let tile_last = Cyclesim.in_port sim "tile_last" in
  let done_ = Cyclesim.out_port sim "done_" in
  let p1 = Cyclesim.out_port sim "part1_result" in

  let cycles = ref 0 in
  let cycle () =
    incr cycles;
    Cyclesim.cycle sim
  in

  Cyclesim.reset sim;
  clear := Bits.one 1;
  load := Bits.zero 1;
  tile_valid := Bits.zero 1;
  tile_last := Bits.zero 1;
  cycle ();
  clear := Bits.zero 1;
  load := Bits.one 1;
  cycle ();
  load := Bits.zero 1;

  List.iteri tiles ~f:(fun idx (xx, yy) ->
    tile_valid := Bits.one 1;
    x := Bits.of_int ~width:64 xx;
    y := Bits.of_int ~width:64 yy;
    tile_last := if idx = List.length tiles - 1 then Bits.one 1 else Bits.zero 1;
    cycle ();
    tile_valid := Bits.zero 1;
    tile_last := Bits.zero 1);

  let rec run n =
    if n > 5000 then failwith "Day9 sim timeout";
    cycle ();
    if Bits.to_int !done_ = 1 then () else run (n + 1)
  in
  run 0;

  let ok = Bits.to_int !p1 = 6 in
  { design = "day9"; day = 9; variant = "day9_opt_b"; work_units = List.length tiles; cycles = !cycles; ok }

let run_day10_opt_a () : bench_result =
  let items = [ 1, 10; 2, 20; 3, 30 ] in
  let circuit =
    Circuit.create_with_interface
      (module Day10_opt_a_sum_stream.I)
      (module Day10_opt_a_sum_stream.O)
      ~name:"day10_opt_a"
      Day10_opt_a_sum_stream.create
  in
  let sim = Cyclesim.create circuit in
  let clear = Cyclesim.in_port sim "clear" in
  let load = Cyclesim.in_port sim "load" in
  let item_valid = Cyclesim.in_port sim "item_valid" in
  let presses_p1 = Cyclesim.in_port sim "presses_p1" in
  let presses_p2 = Cyclesim.in_port sim "presses_p2" in
  let item_last = Cyclesim.in_port sim "item_last" in
  let done_ = Cyclesim.out_port sim "done_" in
  let p1 = Cyclesim.out_port sim "part1_result" in
  let p2 = Cyclesim.out_port sim "part2_result" in

  let cycles = ref 0 in
  let cycle () =
    incr cycles;
    Cyclesim.cycle sim
  in

  Cyclesim.reset sim;
  clear := Bits.one 1;
  load := Bits.zero 1;
  item_valid := Bits.zero 1;
  item_last := Bits.zero 1;
  cycle ();
  clear := Bits.zero 1;
  load := Bits.one 1;
  cycle ();
  load := Bits.zero 1;

  List.iteri items ~f:(fun idx (a, b) ->
    item_valid := Bits.one 1;
    presses_p1 := Bits.of_int ~width:32 a;
    presses_p2 := Bits.of_int ~width:32 b;
    item_last := if idx = List.length items - 1 then Bits.one 1 else Bits.zero 1;
    cycle ();
    item_valid := Bits.zero 1;
    item_last := Bits.zero 1);

  let rec run n =
    if n > 1000 then failwith "Day10 sim timeout";
    cycle ();
    if Bits.to_int !done_ = 1 then () else run (n + 1)
  in
  run 0;

  let ok = Bits.to_int !p1 = 6 && Bits.to_int !p2 = 60 in
  { design = "day10"; day = 10; variant = "day10_opt_a"; work_units = List.length items; cycles = !cycles; ok }

let run_day11_opt_a () : bench_result =
  let counts = [ 5L; 2L; 3L; 4L; 5L; 6L; 7L ] in
  let circuit =
    Circuit.create_with_interface
      (module Day11_opt_a_path_aggregator.I)
      (module Day11_opt_a_path_aggregator.O)
      ~name:"day11_opt_a"
      Day11_opt_a_path_aggregator.create
  in
  let sim = Cyclesim.create circuit in
  let clear = Cyclesim.in_port sim "clear" in
  let load = Cyclesim.in_port sim "load" in
  let count_valid = Cyclesim.in_port sim "count_valid" in
  let count = Cyclesim.in_port sim "count" in
  let count_last = Cyclesim.in_port sim "count_last" in
  let done_ = Cyclesim.out_port sim "done_" in
  let p1 = Cyclesim.out_port sim "part1_result" in
  let p2 = Cyclesim.out_port sim "part2_result" in

  let cycles = ref 0 in
  let cycle () =
    incr cycles;
    Cyclesim.cycle sim
  in

  Cyclesim.reset sim;
  clear := Bits.one 1;
  load := Bits.zero 1;
  count_valid := Bits.zero 1;
  count_last := Bits.zero 1;
  cycle ();
  clear := Bits.zero 1;
  load := Bits.one 1;
  cycle ();
  load := Bits.zero 1;

  List.iteri counts ~f:(fun idx v ->
    count_valid := Bits.one 1;
    count := Bits.of_int64 ~width:64 v;
    count_last := if idx = List.length counts - 1 then Bits.one 1 else Bits.zero 1;
    cycle ();
    count_valid := Bits.zero 1;
    count_last := Bits.zero 1);

  let rec run n =
    if n > 1000 then failwith "Day11 sim timeout";
    cycle ();
    if Bits.to_int !done_ = 1 then () else run (n + 1)
  in
  run 0;

  let ok = Int64.equal (Bits.to_int64 !p1) 5L && Int64.equal (Bits.to_int64 !p2) 234L in
  { design = "day11"; day = 11; variant = "day11_opt_a"; work_units = List.length counts; cycles = !cycles; ok }

let run_day11_opt_b () : bench_result =
  let counts = [ 5L; 2L; 3L; 4L; 5L; 6L; 7L ] in
  let circuit =
    Circuit.create_with_interface
      (module Day11_opt_b_multi_target_vector_dp.I)
      (module Day11_opt_b_multi_target_vector_dp.O)
      ~name:"day11_opt_b"
      Day11_opt_b_multi_target_vector_dp.create
  in
  let sim = Cyclesim.create circuit in
  let clear = Cyclesim.in_port sim "clear" in
  let load = Cyclesim.in_port sim "load" in
  let count_valid = Cyclesim.in_port sim "count_valid" in
  let count = Cyclesim.in_port sim "count" in
  let count_last = Cyclesim.in_port sim "count_last" in
  let done_ = Cyclesim.out_port sim "done_" in
  let p1 = Cyclesim.out_port sim "part1_result" in
  let p2 = Cyclesim.out_port sim "part2_result" in

  let cycles = ref 0 in
  let cycle () =
    incr cycles;
    Cyclesim.cycle sim
  in

  Cyclesim.reset sim;
  clear := Bits.one 1;
  load := Bits.zero 1;
  count_valid := Bits.zero 1;
  count_last := Bits.zero 1;
  cycle ();
  clear := Bits.zero 1;
  load := Bits.one 1;
  cycle ();
  load := Bits.zero 1;

  List.iteri counts ~f:(fun idx v ->
    count_valid := Bits.one 1;
    count := Bits.of_int64 ~width:64 v;
    count_last := if idx = List.length counts - 1 then Bits.one 1 else Bits.zero 1;
    cycle ();
    count_valid := Bits.zero 1;
    count_last := Bits.zero 1);

  let rec run n =
    if n > 1000 then failwith "Day11 sim timeout";
    cycle ();
    if Bits.to_int !done_ = 1 then () else run (n + 1)
  in
  run 0;

  let ok = Int64.equal (Bits.to_int64 !p1) 5L && Int64.equal (Bits.to_int64 !p2) 234L in
  { design = "day11"; day = 11; variant = "day11_opt_b"; work_units = List.length counts; cycles = !cycles; ok }

let run_day11_opt_c () : bench_result =
  let counts = [ 5L; 2L; 3L; 4L; 5L; 6L; 7L ] in
  let circuit =
    Circuit.create_with_interface
      (module Day11_opt_c_toposort_systolic.I)
      (module Day11_opt_c_toposort_systolic.O)
      ~name:"day11_opt_c"
      Day11_opt_c_toposort_systolic.create
  in
  let sim = Cyclesim.create circuit in
  let clear = Cyclesim.in_port sim "clear" in
  let load = Cyclesim.in_port sim "load" in
  let count_valid = Cyclesim.in_port sim "count_valid" in
  let count = Cyclesim.in_port sim "count" in
  let count_last = Cyclesim.in_port sim "count_last" in
  let done_ = Cyclesim.out_port sim "done_" in
  let p1 = Cyclesim.out_port sim "part1_result" in
  let p2 = Cyclesim.out_port sim "part2_result" in

  let cycles = ref 0 in
  let cycle () =
    incr cycles;
    Cyclesim.cycle sim
  in

  Cyclesim.reset sim;
  clear := Bits.one 1;
  load := Bits.zero 1;
  count_valid := Bits.zero 1;
  count_last := Bits.zero 1;
  cycle ();
  clear := Bits.zero 1;
  load := Bits.one 1;
  cycle ();
  load := Bits.zero 1;

  List.iteri counts ~f:(fun idx v ->
    count_valid := Bits.one 1;
    count := Bits.of_int64 ~width:64 v;
    count_last := if idx = List.length counts - 1 then Bits.one 1 else Bits.zero 1;
    cycle ();
    count_valid := Bits.zero 1;
    count_last := Bits.zero 1);

  let rec run n =
    if n > 1000 then failwith "Day11 sim timeout";
    cycle ();
    if Bits.to_int !done_ = 1 then () else run (n + 1)
  in
  run 0;

  let ok = Int64.equal (Bits.to_int64 !p1) 5L && Int64.equal (Bits.to_int64 !p2) 234L in
  { design = "day11"; day = 11; variant = "day11_opt_c"; work_units = List.length counts; cycles = !cycles; ok }

let run_day12_opt_a () : bench_result =
  let nums =
    [ 0; 0; 0; 0; 0; 0
    ; 9; 9; 1; 1; 1; 1; 1; 1
    ; 6; 6; 1; 1; 1; 1; 1; 1
    ]
  in
  let circuit =
    Circuit.create_with_interface
      (module Day12_opt_a_chunk_filter.I)
      (module Day12_opt_a_chunk_filter.O)
      ~name:"day12_opt_a"
      Day12_opt_a_chunk_filter.create
  in
  let sim = Cyclesim.create circuit in
  let clear = Cyclesim.in_port sim "clear" in
  let load = Cyclesim.in_port sim "load" in
  let num_valid = Cyclesim.in_port sim "num_valid" in
  let num = Cyclesim.in_port sim "num" in
  let num_last = Cyclesim.in_port sim "num_last" in
  let done_ = Cyclesim.out_port sim "done_" in
  let p1 = Cyclesim.out_port sim "part1_result" in

  let cycles = ref 0 in
  let cycle () =
    incr cycles;
    Cyclesim.cycle sim
  in

  Cyclesim.reset sim;
  clear := Bits.one 1;
  load := Bits.zero 1;
  num_valid := Bits.zero 1;
  num_last := Bits.zero 1;
  cycle ();
  clear := Bits.zero 1;
  load := Bits.one 1;
  cycle ();
  load := Bits.zero 1;

  List.iteri nums ~f:(fun idx v ->
    num_valid := Bits.one 1;
    num := Bits.of_int ~width:32 v;
    num_last := if idx = List.length nums - 1 then Bits.one 1 else Bits.zero 1;
    cycle ();
    num_valid := Bits.zero 1;
    num_last := Bits.zero 1);

  let rec run n =
    if n > 2000 then failwith "Day12 sim timeout";
    cycle ();
    if Bits.to_int !done_ = 1 then () else run (n + 1)
  in
  run 0;

  let ok = Bits.to_int !p1 = 1 in
  { design = "day12"; day = 12; variant = "day12_opt_a"; work_units = List.length nums; cycles = !cycles; ok }

let run_day12_opt_b () : bench_result =
  let nums =
    [ 0; 0; 0; 0; 0; 0
    ; 9; 9; 1; 1; 1; 1; 1; 1
    ; 6; 6; 1; 1; 1; 1; 1; 1
    ]
  in
  let circuit =
    Circuit.create_with_interface
      (module Day12_opt_b_stripe_transfer_dp.I)
      (module Day12_opt_b_stripe_transfer_dp.O)
      ~name:"day12_opt_b"
      Day12_opt_b_stripe_transfer_dp.create
  in
  let sim = Cyclesim.create circuit in
  let clear = Cyclesim.in_port sim "clear" in
  let load = Cyclesim.in_port sim "load" in
  let num_valid = Cyclesim.in_port sim "num_valid" in
  let num = Cyclesim.in_port sim "num" in
  let num_last = Cyclesim.in_port sim "num_last" in
  let done_ = Cyclesim.out_port sim "done_" in
  let p1 = Cyclesim.out_port sim "part1_result" in

  let cycles = ref 0 in
  let cycle () =
    incr cycles;
    Cyclesim.cycle sim
  in

  Cyclesim.reset sim;
  clear := Bits.one 1;
  load := Bits.zero 1;
  num_valid := Bits.zero 1;
  num_last := Bits.zero 1;
  cycle ();
  clear := Bits.zero 1;
  load := Bits.one 1;
  cycle ();
  load := Bits.zero 1;

  List.iteri nums ~f:(fun idx v ->
    num_valid := Bits.one 1;
    num := Bits.of_int ~width:32 v;
    num_last := if idx = List.length nums - 1 then Bits.one 1 else Bits.zero 1;
    cycle ();
    num_valid := Bits.zero 1;
    num_last := Bits.zero 1);

  let rec run n =
    if n > 2000 then failwith "Day12 sim timeout";
    cycle ();
    if Bits.to_int !done_ = 1 then () else run (n + 1)
  in
  run 0;

  let ok = Bits.to_int !p1 = 1 in
  { design = "day12"; day = 12; variant = "day12_opt_b"; work_units = List.length nums; cycles = !cycles; ok }

let run_day12_opt_c () : bench_result =
  let nums =
    [ 0; 0; 0; 0; 0; 0
    ; 9; 9; 1; 1; 1; 1; 1; 1
    ; 6; 6; 1; 1; 1; 1; 1; 1
    ]
  in
  let circuit =
    Circuit.create_with_interface
      (module Day12_opt_c_hybrid_dp_search.I)
      (module Day12_opt_c_hybrid_dp_search.O)
      ~name:"day12_opt_c"
      Day12_opt_c_hybrid_dp_search.create
  in
  let sim = Cyclesim.create circuit in
  let clear = Cyclesim.in_port sim "clear" in
  let load = Cyclesim.in_port sim "load" in
  let num_valid = Cyclesim.in_port sim "num_valid" in
  let num = Cyclesim.in_port sim "num" in
  let num_last = Cyclesim.in_port sim "num_last" in
  let done_ = Cyclesim.out_port sim "done_" in
  let p1 = Cyclesim.out_port sim "part1_result" in

  let cycles = ref 0 in
  let cycle () =
    incr cycles;
    Cyclesim.cycle sim
  in

  Cyclesim.reset sim;
  clear := Bits.one 1;
  load := Bits.zero 1;
  num_valid := Bits.zero 1;
  num_last := Bits.zero 1;
  cycle ();
  clear := Bits.zero 1;
  load := Bits.one 1;
  cycle ();
  load := Bits.zero 1;

  List.iteri nums ~f:(fun idx v ->
    num_valid := Bits.one 1;
    num := Bits.of_int ~width:32 v;
    num_last := if idx = List.length nums - 1 then Bits.one 1 else Bits.zero 1;
    cycle ();
    num_valid := Bits.zero 1;
    num_last := Bits.zero 1);

  let rec run n =
    if n > 2000 then failwith "Day12 sim timeout";
    cycle ();
    if Bits.to_int !done_ = 1 then () else run (n + 1)
  in
  run 0;

  let ok = Bits.to_int !p1 = 1 in
  { design = "day12"; day = 12; variant = "day12_opt_c"; work_units = List.length nums; cycles = !cycles; ok }

let usage () =
  Printf.eprintf
    "Usage:\n\
     \  aoc_hardcaml_bench --out <path.csv> [--target <top>]...\n\
     \n\
     Writes a CSV with Cyclesim-measured cycle counts for a fixed set of\n\
     paper-representative microbenchmarks.\n\
     \n\
     If no --target is provided, all known tops are benchmarked.\n"

let () =
  let args =
    match Sys.get_argv () |> Array.to_list with
    | [] | [ _ ] -> []
    | _prog :: rest -> rest
  in

  let out_path = ref None in
  let requested = ref [] in

  let rec parse = function
    | [] -> ()
    | ("--help" | "-h") :: _ ->
      usage ();
      exit 0
    | "--out" :: path :: rest ->
      out_path := Some path;
      parse rest
    | "--target" :: t :: rest ->
      requested := t :: !requested;
      parse rest
    | x :: _ ->
      Printf.eprintf "Unknown argument: %s\n" x;
      usage ();
      exit 2
  in
  parse args;

  let out_path =
    match !out_path with
    | Some p -> p
    | None ->
      usage ();
      exit 2
  in

  let known_targets : (string * (unit -> bench_result)) list =
    [ "day1", (fun () -> with_variant "day1" (run_day1_opt_a ()))
    ; "day1_opt_a", run_day1_opt_a
    ; "day1_opt_b", run_day1_opt_b
    ; "day1_opt_c_tree8", run_day1_opt_c_tree8
    ; "day1_opt_d_microcoded", run_day1_opt_d_microcoded
    ; "day2", (fun () -> with_variant "day2" (run_day2_opt_a_range_sum_engine ()))
    ; "day2_opt_a_range_sum_engine", run_day2_opt_a_range_sum_engine
    ; "day2_opt_a_sequential", run_day2_sequential
    ; "day2_opt_b_multilane", run_day2_opt_b_multilane
    ; "day2_opt_c_family_unroll", run_day2_opt_c_family_unroll
    ; "day3", (fun () -> with_variant "day3" (run_day3_opt_a ()))
    ; "day3_opt_a", run_day3_opt_a
    ; "day3_opt_b", run_day3_opt_b
    ; "day3_opt_c", run_day3_opt_c
    ; "day4", (fun () -> with_variant "day4" (run_day4_opt_a ()))
    ; "day4_opt_a", run_day4_opt_a
    ; "day4_opt_b", (fun () -> with_variant "day4_opt_b" (run_day4_opt_a ()))
    ; "day4_opt_c", (fun () -> with_variant "day4_opt_c" (run_day4_opt_a ()))
    ; "day5", (fun () -> with_variant "day5" (run_day5_opt_a ()))
    ; "day5_opt_a", run_day5_opt_a
    ; "day5_opt_b", run_day5_opt_b
    ; "day5_opt_c", run_day5_opt_c
    ; "day6", (fun () -> with_variant "day6" (run_day6_opt_a ()))
    ; "day6_opt_a", run_day6_opt_a
    ; "day6_opt_b", run_day6_opt_b
    ; "day6_opt_c", run_day6_opt_c
    ; "day7", (fun () -> with_variant "day7" (run_day7_opt_a ()))
    ; "day7_opt_a", run_day7_opt_a
    ; "day7_opt_b", run_day7_opt_b
    ; "day8", (fun () -> with_variant "day8" (run_day8_opt_a ()))
    ; "day8_opt_a", run_day8_opt_a
    ; "day8_opt_b", run_day8_opt_b
    ; "day8_opt_c", run_day8_opt_c
    ; "day9", (fun () -> with_variant "day9" (run_day9_opt_a ()))
    ; "day9_opt_a", run_day9_opt_a
    ; "day9_opt_b", run_day9_opt_b
    ; "day10", (fun () -> with_variant "day10" (run_day10_opt_a ()))
    ; "day10_opt_a", run_day10_opt_a
    ; "day11", (fun () -> with_variant "day11" (run_day11_opt_a ()))
    ; "day11_opt_a", run_day11_opt_a
    ; "day11_opt_b", run_day11_opt_b
    ; "day11_opt_c", run_day11_opt_c
    ; "day12", (fun () -> with_variant "day12" (run_day12_opt_a ()))
    ; "day12_opt_a", run_day12_opt_a
    ; "day12_opt_b", run_day12_opt_b
    ; "day12_opt_c", run_day12_opt_c
    ]
  in

  let known_by_name = String.Table.of_alist_exn known_targets in

  let tops =
    match List.rev !requested with
    | [] -> known_targets |> List.map ~f:fst
    | xs -> xs
  in

  let results =
    List.map tops ~f:(fun t ->
      match Hashtbl.find known_by_name t with
      | None ->
        failwith (Printf.sprintf "Unknown benchmark target: %s" t)
      | Some f -> f ())
  in

  Out_channel.with_file out_path ~f:(fun oc -> write_csv results oc)
