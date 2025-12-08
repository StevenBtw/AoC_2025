@group(0) @binding(0) var<storage, read> numbers: array<u32>;
@group(0) @binding(1) var<storage, read> operators: array<u32>;
@group(0) @binding(2) var<storage, read> counts: array<u32>;
@group(0) @binding(3) var<storage, read_write> results_lo: array<u32>;
@group(0) @binding(4) var<storage, read_write> results_hi: array<u32>;
@group(0) @binding(5) var<uniform> maxNums: u32;

fn mul64(a: u32, b: u32) -> vec2<u32> {
    let a_lo = a & 0xFFFFu; let a_hi = a >> 16u;
    let b_lo = b & 0xFFFFu; let b_hi = b >> 16u;
    let p0 = a_lo * b_lo; let p1 = a_lo * b_hi; let p2 = a_hi * b_lo; let p3 = a_hi * b_hi;
    let mid = p1 + p2;
    let lo = p0 + ((mid & 0xFFFFu) << 16u);
    let carry = select(0u, 1u, lo < p0);
    let hi = p3 + (mid >> 16u) + carry + select(0u, 0x10000u, mid < p1);
    return vec2<u32>(lo, hi);
}

fn mul64_inplace(lo: ptr<function, u32>, hi: ptr<function, u32>, n: u32) {
    let prod_lo = mul64(*lo, n); let prod_hi = mul64(*hi, n);
    *lo = prod_lo.x; *hi = prod_lo.y + prod_hi.x;
}

fn add64_inplace(lo: ptr<function, u32>, hi: ptr<function, u32>, n: u32) {
    let new_lo = *lo + n;
    *hi = *hi + select(0u, 1u, new_lo < *lo);
    *lo = new_lo;
}

@compute @workgroup_size(64)
fn main(@builtin(global_invocation_id) gid: vec3<u32>) {
    let idx = gid.x;
    if (idx >= arrayLength(&operators)) { return; }
    let base = idx * maxNums;
    let op = operators[idx];
    let count = counts[idx];
    var lo: u32; var hi: u32;
    if (op == 0u) {
        lo = 1u; hi = 0u;
        for (var i = 0u; i < count; i++) { mul64_inplace(&lo, &hi, numbers[base + i]); }
    } else {
        lo = 0u; hi = 0u;
        for (var i = 0u; i < count; i++) { add64_inplace(&lo, &hi, numbers[base + i]); }
    }
    results_lo[idx] = lo;
    results_hi[idx] = hi;
}
