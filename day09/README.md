# Day 9 Visualization

## Run

```bash
uv sync
uv run python visualize.py
```

Open `http://localhost:5000`

## Notes

- Uses OR-Tools CP-SAT solver to find the largest rectangle
- Toggle Part 1/Part 2 to see different constraints
- Shows traces of previous solutions and part 2 shows the green polygon edges (valid tile boundary)
