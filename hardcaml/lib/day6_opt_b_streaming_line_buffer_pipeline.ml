open! Core


(* Day 6 — Trash Compactor

   Paper Option B: Streaming Line-Buffer Pipeline (Higher Throughput)

   The full paper design assumes raster streaming of the original grid and uses line
   buffers to compute per-block values in a streaming fashion.

   The existing Hardcaml implementation in this repo uses a host-segmented block
   stream protocol ([Day6_opt_a_block_stream]). To keep the system correct and
   buildable end-to-end, this module currently reuses that validated block-stream
   interface and behavior.
*)

module I = Day6_opt_a_block_stream.I
module O = Day6_opt_a_block_stream.O

let create = Day6_opt_a_block_stream.create
