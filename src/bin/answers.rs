#[path = "../util/mod.rs"]
mod util;

#[path = "../day1.rs"]
mod day1;
#[path = "../day2.rs"]
mod day2;
#[path = "../day3.rs"]
mod day3;
#[path = "../day4.rs"]
mod day4;
#[path = "../day5.rs"]
mod day5;
#[path = "../day6.rs"]
mod day6;
#[path = "../day7.rs"]
mod day7;
#[path = "../day8.rs"]
mod day8;
#[path = "../day9.rs"]
mod day9;
#[path = "../day10.rs"]
mod day10;
#[path = "../day11.rs"]
mod day11;
#[path = "../day12.rs"]
mod day12;

use std::env;
use std::fs::read_to_string;

fn usage() -> ! {
    eprintln!("Usage: cargo run --quiet --bin answers -- --day <N> [--input <path>]");
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

    let (p1, p2) = match day {
        1 => {
            let parsed = day1::parse(&input);
            (day1::part1(&parsed).to_string(), day1::part2(&parsed).to_string())
        }
        2 => {
            let parsed = day2::parse(&input);
            (day2::part1(&parsed).to_string(), day2::part2(&parsed).to_string())
        }
        3 => {
            let parsed = day3::parse(&input);
            (day3::part1(&parsed).to_string(), day3::part2(&parsed).to_string())
        }
        4 => {
            let parsed = day4::parse(&input);
            (day4::part1(&parsed).to_string(), day4::part2(&parsed).to_string())
        }
        5 => {
            let parsed = day5::parse(&input);
            (day5::part1(&parsed).to_string(), day5::part2(&parsed).to_string())
        }
        6 => {
            let parsed = day6::parse(&input);
            (day6::part1(&parsed).to_string(), day6::part2(&parsed).to_string())
        }
        7 => {
            let parsed = day7::parse(&input);
            (day7::part1(&parsed).to_string(), day7::part2(&parsed).to_string())
        }
        8 => {
            let parsed = day8::parse(&input);
            (day8::part1(&parsed).to_string(), day8::part2(&parsed).to_string())
        }
        9 => {
            let parsed = day9::parse(&input);
            (day9::part1(&parsed).to_string(), day9::part2(&parsed).to_string())
        }
        10 => {
            let parsed = day10::parse(&input);
            (day10::part1(&parsed).to_string(), day10::part2(&parsed).to_string())
        }
        11 => {
            let parsed = day11::parse(&input);
            (day11::part1(&parsed).to_string(), day11::part2(&parsed).to_string())
        }
        12 => {
            let parsed = day12::parse(&input);
            (day12::part1(&parsed).to_string(), day12::part2(&parsed).to_string())
        }
        _ => {
            eprintln!("Unsupported day {}", day);
            std::process::exit(2);
        }
    };

    // Machine-readable, single-line output.
    println!("day={} p1={} p2={}", day, p1, p2);
}
