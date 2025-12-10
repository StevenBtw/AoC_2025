import re
import cupy as cp
from pathlib import Path

def parse_input(filename="input.txt"):
    machines = []
    for line in open(filename):
        if m := re.search(r'\[([.#]+)\]', line):
            btns = [list(map(int, b.split(','))) for b in re.findall(r'\(([^)]+)\)', line)]
            machines.append((m[1], btns))
    return machines

def explode_data(machines):
    all_patterns = []
    pattern_offsets = []
    pattern_lengths = []

    all_button_indices = []
    button_index_offsets = []
    button_index_counts = []
    buttons_per_machine = []
    button_group_offsets = []

    current_pat_offset = 0
    current_btn_offset = 0
    current_idx_offset = 0

    for pattern, buttons in machines:
        all_patterns.extend([ord(c) for c in pattern])
        pattern_offsets.append(current_pat_offset)
        pattern_lengths.append(len(pattern))
        current_pat_offset += len(pattern)

        buttons_per_machine.append(len(buttons))
        button_group_offsets.append(current_btn_offset)
        current_btn_offset += len(buttons)

        for btn in buttons:
            all_button_indices.extend(btn)
            button_index_offsets.append(current_idx_offset)
            button_index_counts.append(len(btn))
            current_idx_offset += len(btn)

    return {
        'patterns': all_patterns,
        'pat_offsets': pattern_offsets,
        'pat_lengths': pattern_lengths,
        'btn_indices': all_button_indices,
        'btn_idx_offsets': button_index_offsets,
        'btn_idx_counts': button_index_counts,
        'btns_per_machine': buttons_per_machine,
        'btn_grp_offsets': button_group_offsets,
    }

def copy_to_gpu(data, num_machines):
    return {
        'd_patterns': cp.array(data['patterns'], dtype=cp.int8),
        'd_pat_offsets': cp.array(data['pat_offsets'], dtype=cp.int32),
        'd_pat_lengths': cp.array(data['pat_lengths'], dtype=cp.int32),
        'd_btn_indices': cp.array(data['btn_indices'], dtype=cp.int32),
        'd_btn_idx_offsets': cp.array(data['btn_idx_offsets'], dtype=cp.int32),
        'd_btn_idx_counts': cp.array(data['btn_idx_counts'], dtype=cp.int32),
        'd_btns_per_machine': cp.array(data['btns_per_machine'], dtype=cp.int32),
        'd_btn_grp_offsets': cp.array(data['btn_grp_offsets'], dtype=cp.int32),
        'd_results': cp.zeros(num_machines, dtype=cp.int32),
    }

def load_kernel():
    cuda_file = Path(__file__).parent / "part1.cu"
    cuda_code = cuda_file.read_text()
    return cp.RawKernel(cuda_code, 'solve_machines')

def run_kernel(kernel, gpu_data, num_machines):
    threads_per_block = 256
    kernel(
        (num_machines,),
        (threads_per_block,),
        (
            gpu_data['d_patterns'],
            gpu_data['d_pat_offsets'],
            gpu_data['d_pat_lengths'],
            gpu_data['d_btn_indices'],
            gpu_data['d_btn_idx_offsets'],
            gpu_data['d_btn_idx_counts'],
            gpu_data['d_btns_per_machine'],
            gpu_data['d_btn_grp_offsets'],
            gpu_data['d_results'],
            num_machines
        )
    )
    return gpu_data['d_results']

def solve(machines):
    exploded_data = explode_data(machines)
    gpu_data = copy_to_gpu(exploded_data, len(machines))
    kernel = load_kernel()
    results = run_kernel(kernel, gpu_data, len(machines))
    return int(cp.sum(results))

machines = parse_input()
print(solve(machines))