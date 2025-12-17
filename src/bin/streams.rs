#[path = "../util/mod.rs"]
mod util;

#[path = "../day10.rs"]
mod day10;

use std::env;
use std::fs::read_to_string;

fn usage() -> ! {
    eprintln!("Usage: cargo run --quiet --bin streams -- --day <N> [--input <path>]\n\nCurrently supported stream exports:\n  --day 10: per-machine presses (part1, part2)");
    std::process::exit(2);
}

fn parse_args() -> (u32, Option<String>) {
    let mut args = env::args().skip(1);
    let mut day: Option<u32> = None;
    let mut input: Option<String> = None;

    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--day" | "-d" => {
                let value = args.next().unwrap_or_else(|| usage());
                day = Some(value.parse::<u32>().unwrap_or_else(|_| usage()));
            }
            "--input" | "-i" => {
                let value = args.next().unwrap_or_else(|| usage());
                input = Some(value);
            }
            "--help" | "-h" => usage(),
            _ => {}
        }
    }

    let Some(day) = day else { usage() };
    (day, input)
}

fn main() {
    let (day, input_path) = parse_args();
    let path = input_path.unwrap_or_else(|| format!("inputs/{}-1.txt", day));
    let input = read_to_string(&path).unwrap_or_else(|e| {
        eprintln!("Failed to read {}: {}", path, e);
        std::process::exit(1);
    });

    match day {
        10 => {
            let (presses_p1, presses_p2) = day10::parse(&input);
            if presses_p1.len() != presses_p2.len() {
                eprintln!("Day10 parse returned mismatched vector lengths");
                std::process::exit(1);
            }

            for (idx, (p1, p2)) in presses_p1.iter().zip(presses_p2.iter()).enumerate() {
                let last = idx + 1 == presses_p1.len();
                println!("presses_p1={} presses_p2={} last={}", p1, p2, if last { 1 } else { 0 });
            }
        }
        _ => {
            eprintln!("Unsupported day {}", day);
            std::process::exit(2);
        }
    }
}
