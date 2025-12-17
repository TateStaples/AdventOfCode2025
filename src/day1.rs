const DIAL_SIZE: i32 = 100;

pub fn part1() {
    let input = include_str!("../inputs/1-1.txt");
    let lines = input.lines().collect::<Vec<&str>>();
    let password = count_0s(lines);
    println!("Number of 0s lock seq: {}", password);
}

fn count_0s(input: Vec<&str>) -> usize {
    input.into_iter().map(|s| {
        let dir: i32 = match s.chars().next() {
            Some('R') => 1,
            Some('L') => -1,
            None => panic!("Empty string"),
            _ => panic!("Invalid character"),
        };
        dir * s[1..].parse::<i32>().expect("Invalid number in back of string")
    }).fold((0, 50), |(mut count, mut pos), step| {
        pos += step;
        count += if pos % DIAL_SIZE == 0 { 1 } else { 0 };
        // println!("Step: {}, New Pos: {}, Count: {}", step, pos, count);
        (count, pos)
    }).0 as usize
}

pub fn part2() {
    let input = include_str!("../inputs/1-2.txt");
    let lines = input.lines().collect::<Vec<&str>>();
    let password = advanced_feature(lines);
    println!("Advanced feature count: {}", password);
}

pub fn advanced_feature(input: Vec<&str>) -> usize {
    input.into_iter().map(|s| {
        let dir: i32 = match s.chars().next() {
            Some('R') => 1,
            Some('L') => -1,
            None => panic!("Empty string"),
            _ => panic!("Invalid character"),
        };
        dir * s[1..].parse::<i32>().expect("Invalid number in back of string")
    }).fold((0, 0, 50), |(mut count, mut domain, mut pos), step| {
        let clicks = step / DIAL_SIZE;
        pos += step % DIAL_SIZE;
        let new_domain = pos / DIAL_SIZE;  // Doesn't work for landing exactly on boundary
        count += if new_domain != domain {
            (new_domain - domain).abs() as usize + pos
        } else {
            0
        };
        // println!("Step: {}, New Pos: {}, Count: {}", step, pos, count);
        (count, domain, pos)
    }).0 as usize
}