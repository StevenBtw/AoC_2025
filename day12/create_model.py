import json
import numpy as np
import openvino as ov
from openvino import Type, PartialShape, Dimension
from openvino.runtime import opset13 as ops
from pathlib import Path

MAX_BOARD_HEIGHT = 50
MAX_BOARD_WIDTH = 50

def parse_shapes(filename="input.txt"):
    shapes = {}
    lines = open(filename).read().strip().split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line and ':' in line:
            parts = line.split(':')
            first_part = parts[0].strip()
            if 'x' in first_part:
                break

            shape_id = int(first_part)
            shape_lines = []
            i += 1

            while i < len(lines) and lines[i].strip() and ':' not in lines[i]:
                shape_lines.append(lines[i])
                i += 1

            max_width = max(len(row) for row in shape_lines)
            shape = np.zeros((len(shape_lines), max_width), dtype=np.float32)
            for row_idx, row in enumerate(shape_lines):
                for col_idx, char in enumerate(row):
                    if char == '#':
                        shape[row_idx, col_idx] = 1.0
            shapes[shape_id] = shape
        else:
            i += 1
    return shapes

def get_rotations_and_flips(shape):
    variants = []
    seen = set()
    current = shape.copy()

    for _ in range(4):
        for flip in [False, True]:
            variant = np.fliplr(current) if flip else current.copy()
            rows = np.any(variant, axis=1)
            cols = np.any(variant, axis=0)
            variant = variant[rows][:, cols]

            key = tuple(variant.flatten()) + variant.shape
            if key not in seen:
                seen.add(key)
                variants.append(variant.astype(np.float32))
        current = np.rot90(current)
    return variants

def create_openvino_model(shapes):
    all_variants = []
    kernel_info = []

    for shape_id in sorted(shapes.keys()):
        shape = shapes[shape_id]
        cell_count = int(np.sum(shape))
        variants = get_rotations_and_flips(shape)

        for var_idx, variant in enumerate(variants):
            h, w = variant.shape
            all_variants.append(variant)
            kernel_info.append((shape_id, var_idx, h, w, cell_count))

    max_h = max(v.shape[0] for v in all_variants)
    max_w = max(v.shape[1] for v in all_variants)

    kernels = np.zeros((len(all_variants), 1, max_h, max_w), dtype=np.float32)
    for i, variant in enumerate(all_variants):
        h, w = variant.shape
        kernels[i, 0, :h, :w] = variant

    input_shape = PartialShape([
        Dimension(1), Dimension(1),
        Dimension(1, MAX_BOARD_HEIGHT), Dimension(1, MAX_BOARD_WIDTH)
    ])
    board_param = ops.parameter(input_shape, Type.f32, name="board")
    weights_const = ops.constant(kernels, Type.f32)
    conv = ops.convolution(board_param, weights_const,
                           strides=[1, 1], pads_begin=[0, 0],
                           pads_end=[0, 0], dilations=[1, 1])
    result = ops.result(conv, name="valid_placements")
    model = ov.Model([result], [board_param], "shape_placement_detector")

    return model, kernel_info, (max_h, max_w)

def save_metadata(kernel_info, kernel_size, output_path):
    metadata = {
        'kernel_size': list(kernel_size),
        'max_board_size': [MAX_BOARD_HEIGHT, MAX_BOARD_WIDTH],
        'kernels': [
            {'shape_id': info[0], 'variant_idx': info[1],
             'height': info[2], 'width': info[3], 'cell_count': info[4]}
            for info in kernel_info
        ]
    }
    with open(output_path, 'w') as f:
        json.dump(metadata, f, indent=2)

def main(input_file="input.txt", output_dir="."):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    shapes = parse_shapes(input_file)
    model, kernel_info, kernel_size = create_openvino_model(shapes)

    ov.save_model(model, str(output_dir / "shape_detector.xml"))
    save_metadata(kernel_info, kernel_size, str(output_dir / "kernel_metadata.json"))
    print("model created!")
    
if __name__ == "__main__":
    main()
