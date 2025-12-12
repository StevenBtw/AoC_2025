"""Day 12: Animated visualization for shape packing puzzles."""

import argparse
import time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from run_inference import get_valid_placements
from pathlib import Path
from run_inference import parse_input, compile_model, load_metadata
from create_model import main as create_model

matplotlib.use('Agg')
plt.style.use('dark_background')

COLORS = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
    '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
    '#E74C3C', '#3498DB', '#2ECC71', '#9B59B6', '#F39C12',
]

script_dir = Path(__file__).parent
BUILDUP_FRAMES = 70
TOTAL_FRAMES = 110

def sample_buildup(placements, max_frames=BUILDUP_FRAMES):
    n = len(placements)
    if n <= max_frames:
        return [placements[:i] for i in range(1, n + 1)]
    indices = [int(i * n / max_frames) for i in range(1, max_frames + 1)]
    return [placements[:i] for i in indices]


def solve_with_history(region, shapes_data, request, kernels_by_shape, timeout=30, skip=1):
    w, h = region['width'], region['height']
    board = np.ones((h, w), dtype=np.float32)

    shapes_to_place = []
    for sid, cnt in sorted(region['shape_counts'].items(), key=lambda x: len(kernels_by_shape[x[0]])):
        shapes_to_place.extend([sid] * cnt)

    history, placements = [], []
    max_depth, dead_end_count = [0], [0]
    start_time, timed_out, first_dead_end = [time.time()], [False], [True]

    def backtrack(idx):
        if timed_out[0] or idx >= len(shapes_to_place):
            return idx >= len(shapes_to_place)

        if time.time() - start_time[0] > timeout:
            timed_out[0] = True
            return False

        sid = shapes_to_place[idx]
        valid = get_valid_placements(request, board, sid, kernels_by_shape)
        valid.sort(key=lambda x: (x[1], x[2]))

        if not valid and placements:
            dead_end_count[0] += 1
            if first_dead_end[0]:
                for snapshot in sample_buildup(placements):
                    history.append(('place', snapshot))
                history.append(('dead_end', list(placements)))
                first_dead_end[0] = False
            elif dead_end_count[0] % skip == 0:
                history.append(('dead_end', list(placements)))

        for var, row, col, vh, vw in valid:
            variant = shapes_data[sid][var]
            mask = variant > 0
            board[row:row+vh, col:col+vw][mask] = 0
            placements.append((sid, var, row, col))
            max_depth[0] = max(max_depth[0], len(placements))

            if backtrack(idx + 1):
                return True

            placements.pop()
            board[row:row+vh, col:col+vw][mask] = 1
        return False

    success = backtrack(0)

    if success:
        history = [('start', [])]
        for snapshot in sample_buildup(placements):
            history.append(('place', snapshot))
        history.append(('solved', list(placements)))

    return history, shapes_data, (h, w), success


def create_frame(ax, placements, shapes_data, board_size):
    ax.clear()
    h, w = board_size
    colored = np.ones((h, w, 3)) * 0.1

    for shape_id, var_idx, row, col in placements:
        variant = shapes_data[shape_id][var_idx]
        color = tuple(int(COLORS[shape_id % len(COLORS)][i:i+2], 16) / 255 for i in (1, 3, 5))
        for r in range(variant.shape[0]):
            for c in range(variant.shape[1]):
                if variant[r, c] > 0:
                    colored[row + r, col + c] = color

    ax.imshow(colored, aspect='equal', interpolation='nearest')
    for i in range(h + 1):
        ax.axhline(i - 0.5, color='#333', linewidth=0.5)
    for j in range(w + 1):
        ax.axvline(j - 0.5, color='#333', linewidth=0.5)
    ax.set_xlim(-0.5, w - 0.5)
    ax.set_ylim(h - 0.5, -0.5)
    ax.axis('off')


def create_animation(history, shapes_data, board_size, output_path, fps=8, solved=True):
    if len(history) > TOTAL_FRAMES:
        step = len(history) // TOTAL_FRAMES
        history = [history[0]] + history[1:-1:step] + [history[-1]]

    hold_frames = max(0, TOTAL_FRAMES - len(history))
    fig, ax = plt.subplots(figsize=(8, 8))

    def update(frame_idx):
        if frame_idx >= len(history):
            action, placements = history[-1]
        else:
            action, placements = history[frame_idx]

        create_frame(ax, placements, shapes_data, board_size)

        if frame_idx >= len(history) or action == 'solved':
            text, color = ('FIT', '#2ECC71') if solved else ('NO FIT', '#E74C3C')
            ax.text(0.5, 0.5, text, transform=ax.transAxes, fontsize=48, fontweight='bold',
                    color=color, ha='center', va='center', alpha=0.9,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='#111', edgecolor=color, lw=3))
        elif action == 'dead_end':
            ax.set_title(f'Dead end ({len(placements)} pieces)', color='#E74C3C', fontsize=14)
        elif action == 'place':
            ax.set_title(f'Placing piece {len(placements)}', fontsize=14)

    anim = FuncAnimation(fig, update, frames=len(history) + hold_frames, interval=1000//fps)
    anim.save(output_path, writer=PillowWriter(fps=fps))
    plt.close()
    print(f"Saved {output_path} ({TOTAL_FRAMES} frames)")


def main():
    parser = argparse.ArgumentParser(description='Day 12 visualization')
    parser.add_argument('input', nargs='?', default='input.txt')
    parser.add_argument('-r', '--region', type=int, default=0)
    parser.add_argument('-t', '--timeout', type=int, default=130)
    parser.add_argument('-s', '--skip', type=int, default=30000)
    parser.add_argument('--fps', type=int, default=8)
    args = parser.parse_args()

    model_path = script_dir / "shape_detector.xml"
    if not model_path.exists():
        create_model(args.input, str(script_dir))

    shapes_data, regions = parse_input(args.input)
    kernels = load_metadata(str(script_dir / "kernel_metadata.json"))
    request = compile_model(str(model_path))

    if args.region >= len(regions):
        print(f"Region {args.region} not found (0-{len(regions)-1})")
        return

    region = regions[args.region]
    print(f"Solving region {args.region}: {region['width']}x{region['height']}")

    history, shapes_data, board_size, solved = solve_with_history(
        region, shapes_data, request, kernels, args.timeout, args.skip
    )

    output_path = script_dir.parent / "images" / f"d12{'fit' if solved else 'nofit'}.gif"
    print(f"  {'Solved' if solved else 'No solution'} ({len(history)} steps)")
    create_animation(history, shapes_data, board_size, output_path, args.fps, solved)

if __name__ == "__main__":
    main()
