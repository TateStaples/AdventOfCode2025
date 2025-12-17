// Solutions adapted from https://github.com/maneatingape/advent-of-code-rust/tree/main/src/year2025
// Copyright (c) 2025 maneatingape
mod util;
mod day1;
mod day2;
mod day3;
mod day4;
mod day5;
mod day6;
mod day7;
mod day8;
mod day9;
mod day10;
mod day11;
mod day12;

use std::fs::read_to_string;
use std::time::Instant;

macro_rules! run_day {
    ($day:expr, $mod:ident) => {
        let path = format!("inputs/{}-1.txt", $day);
        match read_to_string(&path) {
            Ok(input) => {
                let start = Instant::now();
                let parsed = $mod::parse(&input);
                let p1 = $mod::part1(&parsed);
                let p2 = $mod::part2(&parsed);
                let duration = start.elapsed();
                println!("Day {}:", $day);
                println!("  Part 1: {}", p1);
                println!("  Part 2: {}", p2);
                println!("  Time: {:?}", duration);
            }
            Err(_) => {
                println!("Day {}: Input file not found at {}", $day, path);
            }
        }
    };
}

fn main() {
    run_day!(1, day1);
    run_day!(2, day2);
    run_day!(3, day3);
    run_day!(4, day4);
    run_day!(5, day5);
    run_day!(6, day6);
    run_day!(7, day7);
    run_day!(8, day8);
    run_day!(9, day9);
    run_day!(10, day10);
    run_day!(11, day11);
    run_day!(12, day12);
}
