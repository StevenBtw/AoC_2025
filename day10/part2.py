import re
import cupy as cp
from pathlib import Path

def parse_input(filename="input.txt"):
    machines = []
    for line in open(filename):
        if m := re.search(r'\[([.#]+)\]', line):
            btns = [list(map(int, b.split(','))) for b in re.findall(r'\(([^)]+)\)', line)]
            joltage = list(map(int, re.search(r'\{([^}]+)\}', line)[1].split(',')))
            machines.append((btns, joltage))
    return machines

def explode_data(machines):
    all_targets = []
    target_offsets = []
    num_counters = []
    max_target_per_machine = []

    all_button_indices = []
    button_index_offsets = []
    button_index_counts = []
    buttons_per_machine = []
    button_group_offsets = []

    current_target_offset = 0
    current_btn_offset = 0
    current_idx_offset = 0

    for buttons, joltage in machines:
        all_targets.extend(joltage)
        target_offsets.append(current_target_offset)
        num_counters.append(len(joltage))
        max_target_per_machine.append(max(joltage))
        current_target_offset += len(joltage)

        buttons_per_machine.append(len(buttons))
        button_group_offsets.append(current_btn_offset)
        current_btn_offset += len(buttons)

        for btn in buttons:
            all_button_indices.extend(btn)
            button_index_offsets.append(current_idx_offset)
            button_index_counts.append(len(btn))
            current_idx_offset += len(btn)

    return {
        'targets': all_targets,
        'target_offsets': target_offsets,
        'num_counters': num_counters,
        'max_target': max_target_per_machine,
        'btn_indices': all_button_indices,
        'btn_idx_offsets': button_index_offsets,
        'btn_idx_counts': button_index_counts,
        'btns_per_machine': buttons_per_machine,
        'btn_grp_offsets': button_group_offsets,
    }

def copy_to_gpu(data, num_machines):
    return {
        'd_targets': cp.array(data['targets'], dtype=cp.int32),
        'd_target_offsets': cp.array(data['target_offsets'], dtype=cp.int32),
        'd_num_counters': cp.array(data['num_counters'], dtype=cp.int32),
        'd_btn_indices': cp.array(data['btn_indices'], dtype=cp.int32),
        'd_btn_idx_offsets': cp.array(data['btn_idx_offsets'], dtype=cp.int32),
        'd_btn_idx_counts': cp.array(data['btn_idx_counts'], dtype=cp.int32),
        'd_btns_per_machine': cp.array(data['btns_per_machine'], dtype=cp.int32),
        'd_btn_grp_offsets': cp.array(data['btn_grp_offsets'], dtype=cp.int32),
        'd_max_target': cp.array(data['max_target'], dtype=cp.int32),
        'd_results': cp.zeros(num_machines, dtype=cp.int32),
    }

def load_kernel():
    cuda_file = Path(__file__).parent / "part2.cu"
    cuda_code = cuda_file.read_text()
    return cp.RawKernel(cuda_code, 'solve_machines')

def run_kernel(kernel, gpu_data, num_machines):
    threads_per_block = 256
    kernel(
        (num_machines,),
        (threads_per_block,),
        (
            gpu_data['d_targets'],
            gpu_data['d_target_offsets'],
            gpu_data['d_num_counters'],
            gpu_data['d_btn_indices'],
            gpu_data['d_btn_idx_offsets'],
            gpu_data['d_btn_idx_counts'],
            gpu_data['d_btns_per_machine'],
            gpu_data['d_btn_grp_offsets'],
            gpu_data['d_max_target'],
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