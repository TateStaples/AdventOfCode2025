open! Core

module Family = struct
  type t =
    { digits : int
    ; size : int
    }
  [@@deriving sexp_of]

  let step t : Int64.t =
    let digits_power = Int64.of_int (Int.pow 10 t.digits) in
    let size_power = Int64.of_int (Int.pow 10 t.size) in
    Int64.((digits_power - 1L) / (size_power - 1L))

  let start t : Int64.t =
    let step = step t in
    let size_power = Int64.of_int (Int.pow 10 t.size) in
    Int64.(step * (size_power / 10L))

  let stop t : Int64.t =
    let step = step t in
    let size_power = Int64.of_int (Int.pow 10 t.size) in
    Int64.(step * (size_power - 1L))
end

let first : Family.t list =
  [ { digits = 2; size = 1 }
  ; { digits = 4; size = 2 }
  ; { digits = 6; size = 3 }
  ; { digits = 8; size = 4 }
  ; { digits = 10; size = 5 }
  ]

let second : Family.t list =
  [ { digits = 3; size = 1 }
  ; { digits = 5; size = 1 }
  ; { digits = 6; size = 2 }
  ; { digits = 7; size = 1 }
  ; { digits = 9; size = 3 }
  ; { digits = 10; size = 2 }
  ]

let third : Family.t list =
  [ { digits = 6; size = 1 }
  ; { digits = 10; size = 1 }
  ]
