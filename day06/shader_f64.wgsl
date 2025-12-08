enable f64;
@group(0) @binding(0) var<storage, read> numbers: array<f64>;
@group(0) @binding(1) var<storage, read> operators: array<u32>;
@group(0) @binding(2) var<storage, read> counts: array<u32>;
@group(0) @binding(3) var<storage, read_write> results: array<f64>;
@group(0) @binding(4) var<uniform> maxNums: u32;

@compute @workgroup_size(64)
fn main(@builtin(global_invocation_id) gid: vec3<u32>) {
    let idx = gid.x;
    if (idx >= arrayLength(&operators)) { return; }
    let base = idx * maxNums;
    let op = operators[idx];
    let count = counts[idx];
    var result: f64;
    if (op == 0u) {
        result = 1.0lf;
        for (var i = 0u; i < count; i++) { result = result * numbers[base + i]; }
    } else {
        result = 0.0lf;
        for (var i = 0u; i < count; i++) { result = result + numbers[base + i]; }
    }
    results[idx] = result;
}
