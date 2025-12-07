use std::collections::HashSet;
use std::fs;

fn parse(input_str: &str) -> Vec<Vec<char>> {
    input_str.lines().map(|line| line.chars().collect()).collect()
}

fn part1(input_str: &str) -> usize {
    let grid = parse(input_str);

    let start_col = grid[0].iter().position(|&c| c == 'S').unwrap();
    let mut beams: HashSet<usize> = HashSet::from([start_col]);

    let mut splits = 0;
    for row in grid.iter().step_by(2) {
        for (col, &c) in row.iter().enumerate() {
            if c == '^' && beams.contains(&col) {
                splits += 1;
                beams.remove(&col);
                beams.insert(col + 1);
                beams.insert(col.wrapping_sub(1));
            }
        }
    }

    splits
}

fn part2(input_str: &str) -> usize {
    let grid = parse(input_str);
    let width = grid[0].len();

    let start_col = grid[0].iter().position(|&c| c == 'S').unwrap();
    let mut timelines = vec![0usize; width];
    timelines[start_col] = 1;

    for row in grid.iter().step_by(2) {
        let mut next = timelines.clone();
        for (col, &c) in row.iter().enumerate() {
            if c == '^' && timelines[col] > 0 {
                let count = timelines[col];
                next[col] = 0;
                next[col + 1] += count;
                next[col - 1] += count;
            }
        }
        timelines = next;
    }

    timelines.iter().sum()
}

fn main() {
    let input_str = fs::read_to_string("input.txt").expect("Epic fail!");

    let solution = part1(&input_str);
    println!("part1:{}", solution);

    let solution = part2(&input_str);
    println!("part2:{}", solution);
}
