# Day 6 Solution quickstart

## Run

```bash
npm install
npx esbuild solution.ts --outfile=solution.js --format=iife
npx serve
```

Open `http://localhost:3000/solution.html`

## Notes

- Needs a WebGPU-capable browser (Chrome/Edge)
- Uses u32x2 shaders (emulated 64-bit via two 32-bit integers)
- A `shader_f64.wgsl` is provided for GPUs with native f64 support. To use it, update `solution.ts`:

```typescript
// Replace line 20-23:
let SHADER_F64 = ''

async function loadInput() {
    SHADER_F64 = await fetch('shader_f64.wgsl').then(r => r.text())
```

And modify `run_gpu()` to use `Float64Array` buffers, a single result buffer, and request `shader-f64` feature.
