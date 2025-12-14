# Better Input for Day 12

The original input had a dirty secret: all solvable regions were at ~68% fill, all unsolvable at ~100%. A simple area check beats the puzzle. No backtracking required. Mildly disappointing.

This generator creates input where the lazy solution doesn't work anymore.

## How it works

New shapes, but still 6 and the regions are the same size also, the distribution is now different, and just looking at the fill ratio is not gonna cut it anymore. 

## Usage

```bash
uv run python create_better_input.py
```

Generates `better_input.txt`  and `solution.txt` (encoded answer).

## Verify your answer

```bash
uv run python check_solution.py <your_answer>
```

If you see "Success!", you solved it. If you see garbage, you didn't.