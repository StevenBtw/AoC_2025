import random
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

SHAPES = [
    [(0,0), (0,1), (1,0), (1,1), (2,0), (2,1)],
    [(0,0), (0,1), (0,2), (1,0), (1,1), (1,2)], 
    [(0,0), (0,1), (1,0), (1,1), (2,1)], 
    [(0,1), (1,0), (1,1), (1,2), (2,1)],
    [(0,0), (0,1), (0,2), (1,0), (2,0), (2,1), (2,2)], 
    [(0,0), (0,2), (1,0), (1,1), (1,2), (2,0), (2,2)], 
]

SHAPE_CELLS = [len(s) for s in SHAPES]

DENSE_CLUSTERS = [
    [3, 3, 2, 1, 1, 1],
    [2, 2, 2, 1, 1, 1],
]

SPARSE_CLUSTERS = [
    [1, 1, 1, 3, 3, 3],
    [1, 1, 1, 4, 1, 1], 
    [1, 1, 1, 1, 4, 1],
]

def shape_to_str(shape):
    max_x = max(x for x, y in shape)
    max_y = max(y for x, y in shape)
    grid = [['.' for _ in range(max_y + 1)] for _ in range(max_x + 1)]
    for x, y in shape:
        grid[x][y] = '#'
    return '\n'.join(''.join(row) for row in grid)

def calculate_counts(W, H, ratio, target_fill):
    area = W * H
    target_cells = int(area * target_fill)
    ratio_cells = sum(r * c for r, c in zip(ratio, SHAPE_CELLS))
    scale = target_cells / ratio_cells
    counts = [max(3, int(r * scale + random.uniform(-0.5, 0.5))) for r in ratio]
    return counts

def generate_region(fits):
    W = random.randint(36, 50)
    H = random.randint(36, 50)

    if fits:
        ratio = random.choice(DENSE_CLUSTERS)
        target_fill = random.uniform(0.82, 0.87)
    else:
        ratio = random.choice(SPARSE_CLUSTERS)
        target_fill = random.uniform(0.82, 0.87)

    counts = calculate_counts(W, H, ratio, target_fill)
    actual_cells = sum(c * s for c, s in zip(counts, SHAPE_CELLS))
    actual_fill = actual_cells / (W * H)

    return W, H, counts, actual_fill

def main():
    regions = []
    num_fit = random.randint(300, 700)
    num_nofit = 1000 - num_fit

    for _ in range(num_fit):
        W, H, counts, fill = generate_region(fits=True)
        regions.append((W, H, counts, True, fill))

    for _ in range(num_nofit):
        W, H, counts, fill = generate_region(fits=False)
        regions.append((W, H, counts, False, fill))

    random.shuffle(regions)
    answer = sum(1 for r in regions if r[3])
    
    #fit_fills = [r[4] for r in regions if r[3]]
    #nofit_fills = [r[4] for r in regions if not r[3]]
    #print(f"Generated {len(regions)} regions")
    #print(f"  Fit: {len(fit_fills)}, fill: {min(fit_fills):.3f} - {max(fit_fills):.3f}")
    #print(f"  No-fit: {len(nofit_fills)}, fill: {min(nofit_fills):.3f} - {max(nofit_fills):.3f}")
    #print(f"  OVERLAP: fit max={max(fit_fills):.3f}, nofit min={min(nofit_fills):.3f}")
    #print(f"Answer: {answer}")

    with open(SCRIPT_DIR / "better_input.txt", "w") as f:
        for i, shape in enumerate(SHAPES):
            f.write(f"{i}:\n{shape_to_str(shape)}\n\n")
        for W, H, counts, fits, fill in regions:
            f.write(f"{W}x{H}: {' '.join(map(str, counts))}\n")

    message = "Success!"
    encoded = bytes(ord(c) ^ (answer % 256) for c in message)
    with open(SCRIPT_DIR / "solution.txt", "wb") as f:
        f.write(encoded)

    print(f"\nWrote better_input.txt and solution.txt to {SCRIPT_DIR}")

if __name__ == "__main__":
    main()