open! Core
open Hardcaml
open Aoc_hardcaml

let simulate_day1_basic () =
	let circuit =
		Circuit.create_with_interface
			(module Day1_hardware.I)
			(module Day1_hardware.O)
			~name:"day1"
			Day1_hardware.create
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

	let cycle () = Cyclesim.cycle sim in

	let expect ~p1 ~p2 ~pos =
		let got_p1 = Bits.to_int !part1 in
		let got_p2 = Bits.to_int !part2 in
		let got_pos = Bits.to_int !position in
		if got_p1 <> p1 || got_p2 <> p2 || got_pos <> pos then
			failwith
				(Printf.sprintf
					 "Day1 mismatch: expected (p1=%d,p2=%d,pos=%d) got (p1=%d,p2=%d,pos=%d)"
					 p1
					 p2
					 pos
					 got_p1
					 got_p2
					 got_pos)
	in

	(* Reset state: position=50, p1=0, p2=0 *)
	cycle ();
	clear := Bits.zero 1;
	expect ~p1:0 ~p2:0 ~pos:50;

	(* Right 50: pos=0, crosses 1, and hits zero exactly *)
	set_instr ~valid:true ~dir:1 ~mag:50;
	cycle ();
	set_instr ~valid:false ~dir:1 ~mag:0;
	expect ~p1:1 ~p2:1 ~pos:0;

	(* Right 1: pos=1, crosses 0 *)
	set_instr ~valid:true ~dir:1 ~mag:1;
	cycle ();
	set_instr ~valid:false ~dir:1 ~mag:0;
	expect ~p1:1 ~p2:1 ~pos:1;

	(* Left 2 from pos=1: pos=99, crosses 1 zero (wrap) *)
	set_instr ~valid:true ~dir:0 ~mag:2;
	cycle ();
	set_instr ~valid:false ~dir:1 ~mag:0;
	expect ~p1:1 ~p2:2 ~pos:99;

	(* Right 1 from pos=99: pos=0, crosses 1, hits zero *)
	set_instr ~valid:true ~dir:1 ~mag:1;
	cycle ();
	set_instr ~valid:false ~dir:1 ~mag:0;
	expect ~p1:2 ~p2:3 ~pos:0

let () =
	simulate_day1_basic ();
	let is_repeat_exactly_twice (n : int) =
		let s = Int.to_string n in
		let len = String.length s in
		if len mod 2 <> 0 then false
		else
			let half = len / 2 in
			String.(sub s ~pos:0 ~len:half = sub s ~pos:half ~len:half)
	in

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
	in

	let brute_force_sums ~(ranges : (int * int) list) =
		List.fold ranges ~init:(0, 0) ~f:(fun (acc1, acc2) (a, b) ->
			let sum1 = ref acc1 in
			let sum2 = ref acc2 in
			for x = a to b do
				if is_repeat_exactly_twice x then sum1 := !sum1 + x;
				if is_repeat_k_ge_2 x then sum2 := !sum2 + x
			done;
			!sum1, !sum2)
	in

	let simulate_day2_option_a ~(ranges : (int * int) list) =
		let circuit =
			Circuit.create_with_interface
				(module Day2_opt_a_sequential.I)
				(module Day2_opt_a_sequential.O)
				~name:"day2_opt_a"
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

		let cycle () = Cyclesim.cycle sim in

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
			(* wait ready *)
			while Bits.to_int !ready = 0 do
				cycle ()
			done;
			let is_last = idx = List.length ranges - 1 in
			set_pair ~valid:true ~a ~b ~is_last;
			cycle ();
			set_pair ~valid:false ~a:0 ~b:0 ~is_last:false;
			(* wait either ready (for non-last) or done (for last) *)
			if is_last then (
				while Bits.to_int !done_ = 0 do
					cycle ()
				done
			) else (
				while Bits.to_int !ready = 0 do
					cycle ()
				done
			));

		Bits.to_int !sum_p1, Bits.to_int !sum_p2
	in

	let simulate_day2_option_c_single ~(a : int) ~(b : int) =
		let circuit =
			Circuit.create_with_interface
				(module Day2_opt_c_family_unroll.I)
				(module Day2_opt_c_family_unroll.O)
				~name:"day2_opt_c"
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
		Bits.to_int !sum_p1, Bits.to_int !sum_p2
	in

	(* Day 2 sanity: use small, non-overlapping ranges *)
	let ranges = [ 10, 250; 300, 450 ] in
	let exp1, exp2 = brute_force_sums ~ranges in
	let got1, got2 = simulate_day2_option_a ~ranges in
	if got1 <> exp1 || got2 <> exp2 then
		failwith
			(Printf.sprintf
				 "Day2 opt A mismatch: expected (p1=%d,p2=%d) got (p1=%d,p2=%d)"
				 exp1
				 exp2
				 got1
				 got2);

	let a, b = 10, 500 in
	let exp1c, exp2c = brute_force_sums ~ranges:[ a, b ] in
	let got1c, got2c = simulate_day2_option_c_single ~a ~b in
	if got1c <> exp1c || got2c <> exp2c then
		failwith
			(Printf.sprintf
				 "Day2 opt C mismatch: expected (p1=%d,p2=%d) got (p1=%d,p2=%d)"
				 exp1c
				 exp2c
				 got1c
				 got2c);

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
	in

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
	in

	let simulate_day3_option_a ~(k : int) (bank : string) : int =
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
		Cyclesim.cycle sim;
		start := Bits.zero 1;
		let rec run cycles =
			if cycles > 300 then failwith "Day3 sim timeout";
			Cyclesim.cycle sim;
			if Bits.to_int !done_ = 1 then Bits.to_int !result else run (cycles + 1)
		in
		run 0
	in

	let banks =
		[ "987654321111111"
		; "811111111111119"
		; "234234234234278"
		; "818181911112111"
		; "12345"
		; "111111111111"
		]
	in
	List.iter banks ~f:(fun bank ->
		let exp2 = lobby_reference ~k:2 bank in
		let got2 = simulate_day3_option_a ~k:2 bank in
		if got2 <> exp2 then
			failwith
				(Printf.sprintf "Day3 opt A mismatch k=2 bank=%s expected=%d got=%d" bank exp2 got2));
	List.iter banks ~f:(fun bank ->
		if String.length bank >= 12 then (
			let exp12 = lobby_reference ~k:12 bank in
			let got12 = simulate_day3_option_a ~k:12 bank in
			if got12 <> exp12 then
				failwith
					(Printf.sprintf
						 "Day3 opt A mismatch k=12 bank=%s expected=%d got=%d"
						 bank
						 exp12
						 got12)));

	let day4_reference (lines : string list) : int * int =
		let h = List.length lines in
		let w =
			match lines with
			| [] -> 0
			| hd :: _ -> String.length hd
		in
		let dirs =
			[ -1, -1
			; -1, 0
			; -1, 1
			; 0, -1
			; 0, 1
			; 1, -1
			; 1, 0
			; 1, 1
			]
		in
		let is_at r c =
			if r < 0 || r >= h || c < 0 || c >= w then false
			else Char.equal (String.get (List.nth_exn lines r) c) '@'
		in
		(* padded grid with u8::MAX for non-roll cells *)
		let pw = w + 2 in
		let ph = h + 2 in
		let idx r c = (r * pw) + c in
		let padded = Array.create ~len:(pw * ph) 255 in
		let todo = ref [] in
		for r = 0 to h - 1 do
			for c = 0 to w - 1 do
				if is_at r c then (
					let count =
						List.count dirs ~f:(fun (dr, dc) -> is_at (r + dr) (c + dc))
					in
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

	let simulate_day4_opt_a ~(lines : string list) : int * int =
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
		Cyclesim.reset sim;
		clear := Bits.one 1;
		start := Bits.zero 1;
		grid_in := Bits.zero (139 * 139);
		Cyclesim.cycle sim;
		clear := Bits.zero 1;
		start := Bits.one 1;
		grid_in := bits_of_day4_lines_139 lines;
		Cyclesim.cycle sim;
		start := Bits.zero 1;
		let rec run cycles =
			if cycles > 600 then failwith "Day4 sim timeout";
			Cyclesim.cycle sim;
			if Bits.to_int !done_ = 1 then Bits.to_int !part1, Bits.to_int !part2
			else run (cycles + 1)
		in
		run 0
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
	let exp4_p1, exp4_p2 = day4_reference day4_lines in
	let got4_p1, got4_p2 = simulate_day4_opt_a ~lines:day4_lines in
	if got4_p1 <> exp4_p1 || got4_p2 <> exp4_p2 then
		failwith
			(Printf.sprintf
				 "Day4 opt A mismatch: expected (p1=%d,p2=%d) got (p1=%d,p2=%d)"
				 exp4_p1
				 exp4_p2
				 got4_p1
				 got4_p2);

	let day5_reference ~(ranges : (int * int) list) ~(ids : int list) : int * int =
		let ranges = List.sort ranges ~compare:(fun (a1, b1) (a2, b2) ->
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
		(* two-pointer membership count *)
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

	let simulate_day5_opt_a ~(ranges : (int * int) list) ~(ids : int list) : int * int =
		let circuit =
			Circuit.create_with_interface
				(module Day5_hardware.I)
				(module Day5_hardware.O)
				~name:"day5_opt_a"
				Day5_hardware.create
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

		let cycle () = Cyclesim.cycle sim in

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
		(* pulse load *)
		load := Bits.one 1;
		cycle ();
		load := Bits.zero 1;

		let ranges = List.sort ranges ~compare:(fun (a1, b1) (a2, b2) ->
															match Int.compare a1 a2 with
															| 0 -> Int.compare b1 b2
															| x -> x)
		in
		let ids = List.sort ids ~compare:Int.compare in

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

		let rec run cycles =
			if cycles > 2000 then failwith "Day5 sim timeout";
			cycle ();
			if Bits.to_int !done_ = 1 then Bits.to_int !part1, Bits.to_int !part2
			else run (cycles + 1)
		in
		run 0
	in

	let day5_ranges = [ 10, 20; 15, 30; 40, 40; 41, 42; 100, 105 ] in
	let day5_ids = [ 9; 10; 15; 20; 21; 30; 31; 40; 41; 42; 43; 104; 200 ] in
	let exp5_p1, exp5_p2 = day5_reference ~ranges:day5_ranges ~ids:day5_ids in
	let got5_p1, got5_p2 = simulate_day5_opt_a ~ranges:day5_ranges ~ids:day5_ids in
	if got5_p1 <> exp5_p1 || got5_p2 <> exp5_p2 then
		failwith
			(Printf.sprintf
				 "Day5 opt A mismatch: expected (p1=%d,p2=%d) got (p1=%d,p2=%d)"
				 exp5_p1
				 exp5_p2
				 got5_p1
				 got5_p2);

	(* ---------------- Day 6 ---------------- *)
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

	let simulate_day6 (blocks : (bool * (int option array) list) list) : int64 * int64 =
		let circuit =
			Circuit.create_with_interface
				(module Day6_hardware.I)
				(module Day6_hardware.O)
				~name:"day6"
				Day6_hardware.create
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
		let cycle () = Cyclesim.cycle sim in

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
					if bi = List.length blocks - 1 && is_last_col then Bits.one 1
					else Bits.zero 1;
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
			if Bits.to_int !done_ = 1 then Bits.to_int64 !p1, Bits.to_int64 !p2 else run (n + 1)
		in
		run 0
	in

	let day6_blocks =
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
	let exp6_p1, exp6_p2 = day6_reference day6_blocks in
	let got6_p1, got6_p2 = simulate_day6 day6_blocks in
	if not (Int64.equal exp6_p1 got6_p1 && Int64.equal exp6_p2 got6_p2) then
		failwith
			(Printf.sprintf
				 "Day6 mismatch: expected (p1=%Ld,p2=%Ld) got (p1=%Ld,p2=%Ld)"
				 exp6_p1
				 exp6_p2
				 got6_p1
				 got6_p2);

	(* ---------------- Day 7 ---------------- *)
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

	let simulate_day7 ~(width : int) ~(rows : int list list) : int * int =
		let circuit =
			Circuit.create_with_interface
				(module Day7_hardware.I)
				(module Day7_hardware.O)
				~name:"day7"
				Day7_hardware.create
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
		let cycle () = Cyclesim.cycle sim in

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
			if Bits.to_int !done_ = 1 then Bits.to_int !p1, Bits.to_int !p2 else run (n + 1)
		in
		run 0
	in

	let day7_width = 9 in
	let day7_rows = [ [ 4 ]; [ 3; 5 ]; [ 2 ]; [ 6 ] ] in
	let exp7_p1, exp7_p2 = day7_reference ~width:day7_width ~rows:day7_rows in
	let got7_p1, got7_p2 = simulate_day7 ~width:day7_width ~rows:day7_rows in
	if got7_p1 <> exp7_p1 || got7_p2 <> exp7_p2 then
		failwith
			(Printf.sprintf
				 "Day7 mismatch: expected (p1=%d,p2=%d) got (p1=%d,p2=%d)"
				 exp7_p1
				 exp7_p2
				 got7_p1
				 got7_p2);

	(* ---------------- Day 8 ---------------- *)
	let simulate_day8 () : int * int =
		let circuit =
			Circuit.create_with_interface
				(module Day8_hardware.I)
				(module Day8_hardware.O)
				~name:"day8"
				Day8_hardware.create
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
		let cycle () = Cyclesim.cycle sim in

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

		send_edges ~phase:0 [ 0, 1; 2, 3 ];
		send_edges ~phase:1 [ 0, 1; 1, 2; 2, 3; 3, 4 ];

		let rec run n =
			if n > 5000 then failwith "Day8 sim timeout";
			cycle ();
			if Bits.to_int !done_ = 1 then Bits.to_int !p1, Bits.to_int !p2 else run (n + 1)
		in
		run 0
	in

	let got8_p1, got8_p2 = simulate_day8 () in
	if got8_p1 <> 4 || got8_p2 <> 77 then
		failwith (Printf.sprintf "Day8 mismatch: expected (p1=4,p2=77) got (p1=%d,p2=%d)" got8_p1 got8_p2);

	(* ---------------- Day 9 ---------------- *)
	let simulate_day9 ~(tiles : (int * int) list) : int =
		let circuit =
			Circuit.create_with_interface
				(module Day9_hardware.I)
				(module Day9_hardware.O)
				~name:"day9"
				Day9_hardware.create
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
		let cycle () = Cyclesim.cycle sim in
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
			if Bits.to_int !done_ = 1 then Bits.to_int !p1 else run (n + 1)
		in
		run 0
	in

	let got9 = simulate_day9 ~tiles:[ 0, 0; 0, 1; 2, 0; 2, 1 ] in
	if got9 <> 6 then failwith (Printf.sprintf "Day9 mismatch: expected 6 got %d" got9);

	(* ---------------- Day 10 ---------------- *)
	let simulate_day10 ~(items : (int * int) list) : int * int =
		let circuit =
			Circuit.create_with_interface
				(module Day10_hardware.I)
				(module Day10_hardware.O)
				~name:"day10"
				Day10_hardware.create
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
		let cycle () = Cyclesim.cycle sim in
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
			if Bits.to_int !done_ = 1 then Bits.to_int !p1, Bits.to_int !p2 else run (n + 1)
		in
		run 0
	in

	let got10_p1, got10_p2 = simulate_day10 ~items:[ 1, 10; 2, 20; 3, 30 ] in
	if got10_p1 <> 6 || got10_p2 <> 60 then
		failwith (Printf.sprintf "Day10 mismatch: expected (6,60) got (%d,%d)" got10_p1 got10_p2);

	(* ---------------- Day 11 ---------------- *)
	let simulate_day11 ~(counts : int64 list) : int64 * int64 =
		let circuit =
			Circuit.create_with_interface
				(module Day11_hardware.I)
				(module Day11_hardware.O)
				~name:"day11"
				Day11_hardware.create
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
		let cycle () = Cyclesim.cycle sim in
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
			if Bits.to_int !done_ = 1 then Bits.to_int64 !p1, Bits.to_int64 !p2 else run (n + 1)
		in
		run 0
	in

	let got11_p1, got11_p2 = simulate_day11 ~counts:[ 5L; 2L; 3L; 4L; 5L; 6L; 7L ] in
	if not (Int64.equal got11_p1 5L && Int64.equal got11_p2 234L) then
		failwith
			(Printf.sprintf "Day11 mismatch: expected (5,234) got (%Ld,%Ld)" got11_p1 got11_p2);

	(* ---------------- Day 12 ---------------- *)
	let simulate_day12 ~(nums : int list) : int =
		let circuit =
			Circuit.create_with_interface
				(module Day12_hardware.I)
				(module Day12_hardware.O)
				~name:"day12"
				Day12_hardware.create
		in
		let sim = Cyclesim.create circuit in
		let clear = Cyclesim.in_port sim "clear" in
		let load = Cyclesim.in_port sim "load" in
		let num_valid = Cyclesim.in_port sim "num_valid" in
		let num = Cyclesim.in_port sim "num" in
		let num_last = Cyclesim.in_port sim "num_last" in
		let done_ = Cyclesim.out_port sim "done_" in
		let p1 = Cyclesim.out_port sim "part1_result" in
		let cycle () = Cyclesim.cycle sim in
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
			if Bits.to_int !done_ = 1 then Bits.to_int !p1 else run (n + 1)
		in
		run 0
	in

	let nums12 =
		[ 0; 0; 0; 0; 0; 0
		; 9; 9; 1; 1; 1; 1; 1; 1
		; 6; 6; 1; 1; 1; 1; 1; 1
		]
	in
	let got12 = simulate_day12 ~nums:nums12 in
	if got12 <> 1 then failwith (Printf.sprintf "Day12 mismatch: expected 1 got %d" got12);

	print_endline "HardCaml tests passed"
