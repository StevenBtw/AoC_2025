import json
import numpy as np
import openvino as ov
from pathlib import Path

def load_metadata(path):
    metadata = json.load(open(path))
    kernels_by_shape = {}
    for idx, k in enumerate(metadata['kernels']):
        info = {'idx': idx, 'var': k['variant_idx'], 'h': k['height'],
                'w': k['width'], 'cells': k['cell_count']}
        kernels_by_shape.setdefault(k['shape_id'], []).append(info)
    return kernels_by_shape

def compile_model(path):
    core = ov.Core()
    model = core.read_model(path)
    compiled = core.compile_model(model, "CPU")
    return compiled.create_infer_request()

def infer(request, board):
    tensor = board.reshape(1, 1, *board.shape).astype(np.float32)
    request.infer({0: tensor})
    return request.get_output_tensor(0).data[0]

def get_valid_placements(request, board, shape_id, kernels_by_shape):
    scores = infer(request, board)
    valid = []
    for k in kernels_by_shape[shape_id]:
        positions = np.argwhere(np.abs(scores[k['idx']] - k['cells']) < 0.5)
        for pos in positions:
            valid.append((k['var'], int(pos[0]), int(pos[1]), k['h'], k['w']))
    return valid

def solve_region(region, shapes_data, request, kernels_by_shape):
    w, h, counts = region['width'], region['height'], region['shape_counts']
    board = np.ones((h, w), dtype=np.float32)

    shapes_to_place = []
    for sid, cnt in sorted(counts.items(), key=lambda x: len(kernels_by_shape[x[0]])):
        shapes_to_place.extend([sid] * cnt)

    total_cells = sum(kernels_by_shape[sid][0]['cells'] * cnt for sid, cnt in counts.items())
    if total_cells > w * h:
        return None

    placements = []

    def backtrack(idx):
        if idx >= len(shapes_to_place):
            return True
        sid = shapes_to_place[idx]
        valid = get_valid_placements(request, board, sid, kernels_by_shape)
        valid.sort(key=lambda x: (x[1], x[2]))

        for var, row, col, vh, vw in valid:
            variant = shapes_data[sid][var]
            mask = variant > 0
            board[row:row+vh, col:col+vw][mask] = 0
            placements.append((sid, var, row, col))
            if backtrack(idx + 1):
                return True
            placements.pop()
            board[row:row+vh, col:col+vw][mask] = 1
        return False

    return placements if backtrack(0) else None

def parse_input(filename="input.txt"):
    from create_model import parse_shapes, get_rotations_and_flips
    shapes_raw = parse_shapes(filename)
    shapes_data = {sid: get_rotations_and_flips(s) for sid, s in shapes_raw.items()}

    regions = []
    for line in open(filename):
        line = line.strip()
        if line and 'x' in line and ':' in line:
            parts = line.split(':')
            dims = parts[0].strip()
            if not dims[0].isdigit():
                continue
            w, h = map(int, dims.split('x'))
            counts = list(map(int, parts[1].strip().split()))
            regions.append({'width': w, 'height': h,
                           'shape_counts': {i: c for i, c in enumerate(counts) if c > 0}})
    return shapes_data, regions

def solve(filename="input.txt"):
    model_dir = Path(__file__).parent
    model_path = model_dir / "shape_detector.xml"
    metadata_path = model_dir / "kernel_metadata.json"

    if not model_path.exists():
        from create_model import main as create_main
        create_main(filename, str(model_dir))

    kernels_by_shape = load_metadata(str(metadata_path))
    request = compile_model(str(model_path))
    shapes_data, regions = parse_input(filename)

    solvable = sum(1 for r in regions if solve_region(r, shapes_data, request, kernels_by_shape))
    return solvable

if __name__ == "__main__":
    import sys
    filename = sys.argv[1] if len(sys.argv) > 1 else "input.txt"
    print(solve(filename))
