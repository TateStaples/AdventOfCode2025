(** Main entry point for AoC 2025 HardCaml solutions *)

open Core
open Hardcaml
open Aoc_hardcaml

let print_verilog circuit = Rtl.print Verilog circuit

type target =
  { name : string
  ; create_circuit : unit -> Circuit.t
  }

let targets : target list =
  [ { name = "day1"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day1_hardware.I)
            (module Day1_hardware.O)
            ~name:"day1"
            Day1_hardware.create)
    }
  ; { name = "day1_opt_a"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day1_opt_a_minimal_streaming.I)
            (module Day1_opt_a_minimal_streaming.O)
            ~name:"day1_opt_a"
            Day1_opt_a_minimal_streaming.create)
    }
  ; { name = "day1_opt_b"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day1_opt_b_pipelined.I)
            (module Day1_opt_b_pipelined.O)
            ~name:"day1_opt_b"
            Day1_opt_b_pipelined.create)
    }
  ; { name = "day1_opt_c_tree8"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day1_opt_c_tree8.I)
            (module Day1_opt_c_tree8.O)
            ~name:"day1_opt_c_tree8"
            Day1_opt_c_tree8.create)
    }
  ; { name = "day1_opt_d_microcoded"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day1_opt_d_microcoded_div100.I)
            (module Day1_opt_d_microcoded_div100.O)
            ~name:"day1_opt_d_microcoded"
            Day1_opt_d_microcoded_div100.create)
    }
  ; { name = "day2"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day2_hardware.I)
            (module Day2_hardware.O)
            ~name:"day2"
            Day2_hardware.create)
    }
  ; { name = "day2_opt_a_sequential"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day2_opt_a_sequential.I)
            (module Day2_opt_a_sequential.O)
            ~name:"day2_opt_a_sequential"
            Day2_opt_a_sequential.create)
    }
  ; { name = "day2_opt_b_multilane"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day2_opt_b_multilane.I)
            (module Day2_opt_b_multilane.O)
            ~name:"day2_opt_b_multilane"
            Day2_opt_b_multilane.create)
    }
  ; { name = "day2_opt_c_family_unroll"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day2_opt_c_family_unroll.I)
            (module Day2_opt_c_family_unroll.O)
            ~name:"day2_opt_c_family_unroll"
            Day2_opt_c_family_unroll.create)
    }
  ; { name = "day2_opt_a_range_sum_engine"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day2_opt_a_range_sum_engine.I)
            (module Day2_opt_a_range_sum_engine.O)
            ~name:"day2_opt_a_range_sum_engine"
            Day2_opt_a_range_sum_engine.create)
    }
  ; { name = "day3"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day3_hardware.I)
            (module Day3_hardware.O)
            ~name:"day3"
            Day3_hardware.create)
    }
  ; { name = "day3_opt_a"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day3_opt_a_streaming_selector.I)
            (module Day3_opt_a_streaming_selector.O)
            ~name:"day3_opt_a"
            Day3_opt_a_streaming_selector.create)
    }
  ; { name = "day3_opt_b"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day3_opt_b_monotone_stack.I)
            (module Day3_opt_b_monotone_stack.O)
            ~name:"day3_opt_b"
            Day3_opt_b_monotone_stack.create)
    }
  ; { name = "day3_opt_c"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day3_opt_c_unrolled_compare_network.I)
            (module Day3_opt_c_unrolled_compare_network.O)
            ~name:"day3_opt_c"
            Day3_opt_c_unrolled_compare_network.create)
    }
  ; { name = "day4"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day4_hardware.I)
            (module Day4_hardware.O)
            ~name:"day4"
            Day4_hardware.create)
    }
  ; { name = "day4_opt_a"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day4_opt_a_dense_ca.I)
            (module Day4_opt_a_dense_ca.O)
            ~name:"day4_opt_a"
            Day4_opt_a_dense_ca.create)
    }
  ; { name = "day4_opt_b"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day4_opt_b_event_queue_peeling.I)
            (module Day4_opt_b_event_queue_peeling.O)
            ~name:"day4_opt_b"
            Day4_opt_b_event_queue_peeling.create)
    }
  ; { name = "day4_opt_c"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day4_opt_c_hybrid_block_queue.I)
            (module Day4_opt_c_hybrid_block_queue.O)
            ~name:"day4_opt_c"
            Day4_opt_c_hybrid_block_queue.create)
    }
  ; { name = "day5"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day5_hardware.I)
            (module Day5_hardware.O)
            ~name:"day5"
            Day5_hardware.create)
    }
  ; { name = "day5_opt_a"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day5_opt_a_interval_union_engine.I)
            (module Day5_opt_a_interval_union_engine.O)
            ~name:"day5_opt_a"
            Day5_opt_a_interval_union_engine.create)
    }
  ; { name = "day5_opt_b"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day5_opt_b_multilane_counter.I)
            (module Day5_opt_b_multilane_counter.O)
            ~name:"day5_opt_b"
            Day5_opt_b_multilane_counter.create)
    }
  ; { name = "day5_opt_c"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day5_opt_c_max_parallel_coverage.I)
            (module Day5_opt_c_max_parallel_coverage.O)
            ~name:"day5_opt_c"
            Day5_opt_c_max_parallel_coverage.create)
    }
  ; { name = "day6"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day6_hardware.I)
            (module Day6_hardware.O)
            ~name:"day6"
            Day6_hardware.create)
    }
  ; { name = "day6_opt_a"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day6_opt_a_block_stream.I)
            (module Day6_opt_a_block_stream.O)
            ~name:"day6_opt_a"
            Day6_opt_a_block_stream.create)
    }
  ; { name = "day6_opt_b"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day6_opt_b_streaming_line_buffer_pipeline.I)
            (module Day6_opt_b_streaming_line_buffer_pipeline.O)
            ~name:"day6_opt_b"
            Day6_opt_b_streaming_line_buffer_pipeline.create)
    }
  ; { name = "day6_opt_c"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day6_opt_c_max_parallel_block_eval.I)
            (module Day6_opt_c_max_parallel_block_eval.O)
            ~name:"day6_opt_c"
            Day6_opt_c_max_parallel_block_eval.create)
    }
  ; { name = "day7"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day7_hardware.I)
            (module Day7_hardware.O)
            ~name:"day7"
            Day7_hardware.create)
    }
  ; { name = "day7_opt_a"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day7_opt_a_timeline_split.I)
            (module Day7_opt_a_timeline_split.O)
            ~name:"day7_opt_a"
            Day7_opt_a_timeline_split.create)
    }
  ; { name = "day7_opt_b"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day7_opt_b_wide_simd_row_update.I)
            (module Day7_opt_b_wide_simd_row_update.O)
            ~name:"day7_opt_b"
            Day7_opt_b_wide_simd_row_update.create)
    }
  ; { name = "day8"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day8_hardware.I)
            (module Day8_hardware.O)
            ~name:"day8"
            Day8_hardware.create)
    }
  ; { name = "day8_opt_a"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day8_opt_a_streaming_union_find.I)
            (module Day8_opt_a_streaming_union_find.O)
            ~name:"day8_opt_a"
            Day8_opt_a_streaming_union_find.create)
    }
  ; { name = "day8_opt_b"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day8_opt_b_topk_edges_only.I)
            (module Day8_opt_b_topk_edges_only.O)
            ~name:"day8_opt_b"
            Day8_opt_b_topk_edges_only.create)
    }
  ; { name = "day8_opt_c"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day8_opt_c_spatial_partitioning.I)
            (module Day8_opt_c_spatial_partitioning.O)
            ~name:"day8_opt_c"
            Day8_opt_c_spatial_partitioning.create)
    }
  ; { name = "day9"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day9_hardware.I)
            (module Day9_hardware.O)
            ~name:"day9"
            Day9_hardware.create)
    }
  ; { name = "day9_opt_a"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day9_opt_a_pairwise_max_area.I)
            (module Day9_opt_a_pairwise_max_area.O)
            ~name:"day9_opt_a"
            Day9_opt_a_pairwise_max_area.create)
    }
  ; { name = "day9_opt_b"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day9_opt_b_scanline_interval_machine.I)
            (module Day9_opt_b_scanline_interval_machine.O)
            ~name:"day9_opt_b"
            Day9_opt_b_scanline_interval_machine.create)
    }
  ; { name = "day10"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day10_hardware.I)
            (module Day10_hardware.O)
            ~name:"day10"
            Day10_hardware.create)
    }
  ; { name = "day10_opt_a"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day10_opt_a_sum_stream.I)
            (module Day10_opt_a_sum_stream.O)
            ~name:"day10_opt_a"
            Day10_opt_a_sum_stream.create)
    }
  ; { name = "day11"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day11_hardware.I)
            (module Day11_hardware.O)
            ~name:"day11"
            Day11_hardware.create)
    }
  ; { name = "day11_opt_a"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day11_opt_a_path_aggregator.I)
            (module Day11_opt_a_path_aggregator.O)
            ~name:"day11_opt_a"
            Day11_opt_a_path_aggregator.create)
    }
  ; { name = "day11_opt_b"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day11_opt_b_multi_target_vector_dp.I)
            (module Day11_opt_b_multi_target_vector_dp.O)
            ~name:"day11_opt_b"
            Day11_opt_b_multi_target_vector_dp.create)
    }
  ; { name = "day11_opt_c"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day11_opt_c_toposort_systolic.I)
            (module Day11_opt_c_toposort_systolic.O)
            ~name:"day11_opt_c"
            Day11_opt_c_toposort_systolic.create)
    }
  ; { name = "day12"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day12_hardware.I)
            (module Day12_hardware.O)
            ~name:"day12"
            Day12_hardware.create)
    }
  ; { name = "day12_opt_a"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day12_opt_a_chunk_filter.I)
            (module Day12_opt_a_chunk_filter.O)
            ~name:"day12_opt_a"
            Day12_opt_a_chunk_filter.create)
    }
  ; { name = "day12_opt_b"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day12_opt_b_stripe_transfer_dp.I)
            (module Day12_opt_b_stripe_transfer_dp.O)
            ~name:"day12_opt_b"
            Day12_opt_b_stripe_transfer_dp.create)
    }
  ; { name = "day12_opt_c"
    ; create_circuit =
        (fun () ->
          Circuit.create_with_interface
            (module Day12_opt_c_hybrid_dp_search.I)
            (module Day12_opt_c_hybrid_dp_search.O)
            ~name:"day12_opt_c"
            Day12_opt_c_hybrid_dp_search.create)
    }
  ]

let usage () =
  Printf.eprintf
    "Usage:\n\
     \  aoc_hardcaml --list-verilog\n\
     \  aoc_hardcaml --verilog <target>\n\
     \n\
     Examples:\n\
     \  aoc_hardcaml --verilog day6 > day6.v\n\
     \  aoc_hardcaml --verilog day1_opt_c_tree8 > day1_opt_c_tree8.v\n\
     \n\
     Notes:\n\
    \  - For batch export, run: hardcaml/scripts/export_verilog.sh\n"

let find_target (name : string) =
  let key = String.lowercase name in
  List.find targets ~f:(fun t -> String.(lowercase t.name = key))

let () =
  match Sys.get_argv () |> Array.to_list with
  | _prog :: ("--help" | "-h") :: _ -> usage ()
  | _prog :: "--list-verilog" :: _ ->
    List.iter targets ~f:(fun t -> print_endline t.name)
  | _prog :: "--verilog" :: name :: _ ->
    (match find_target name with
    | None ->
      Printf.eprintf "Unknown verilog target: %s\n" name;
      usage ();
      exit 2
    | Some t -> print_verilog (t.create_circuit ()))
  | _ ->
    usage ();
    exit 2
