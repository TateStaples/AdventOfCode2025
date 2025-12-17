open Hardcaml
open Signal

(* Simple unsigned div/mod via restoring division (combinational, unrolled).

   Note: This is intended primarily for small widths or constant divisors.
   It is still synthesizable for larger widths, but can be expensive.
*)

let udivmod ~numerator ~denominator =
  let w = width numerator in
  if w = 0 then zero 0, zero 0
  else (
    let denom = uresize denominator w in
    let rem = ref (zero w) in
    let quot = ref (zero w) in
    for k = w - 1 downto 0 do
      let bring = bit numerator k in
      let rem_shift =
        if w = 1 then bring
        else concat_msb [ select !rem (w - 2) 0; bring ]
      in
      let ge = rem_shift >=: denom in
      let rem_next = mux2 ge (rem_shift -: denom) rem_shift in
      let quot_next =
        if w = 1 then ge
        else concat_msb [ select !quot (w - 2) 0; ge ]
      in
      rem := rem_next;
      quot := quot_next
    done;
    !quot, !rem)

let udiv ~numerator ~denominator = fst (udivmod ~numerator ~denominator)
let umod ~numerator ~denominator = snd (udivmod ~numerator ~denominator)
