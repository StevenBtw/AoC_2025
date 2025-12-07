export {};

const part1Btn = document.getElementById('part1') as HTMLButtonElement
const part2Btn = document.getElementById('part2') as HTMLButtonElement
const startBtn = document.getElementById('startBtn') as HTMLButtonElement
const stopBtn = document.getElementById('stopBtn') as HTMLButtonElement
const timeEl = document.getElementById('time')!
const resultEl = document.getElementById('result')!
const statusEl = document.getElementById('status')!
const dataEl = document.getElementById('data')!

let currentPart = 1
let running = false
let startTime = 0
let timerInterval: number | null = null
let INPUT = ''
let problems: any[] = []
let problemsP2: any[] = []
let maxResult = 0

async function loadInput() {
    statusEl.textContent = 'Loading input.txt...'
    const resp = await fetch('input.txt')
    INPUT = await resp.text()
    problems = parse(INPUT, false)
    problemsP2 = parse(INPUT, true)
    statusEl.textContent = `Loaded ${problems.length} problems`
    renderData(currentPart === 1 ? problems : problemsP2)
}

function renderData(probs: any[], results?: number[]) {
    if (results) maxResult = Math.max(...results.map(Math.abs))

    const isPart2 = currentPart === 2
    let html = '<div class="problems-grid" id="grid">'

    if (isPart2 && probs[0]?.grid) {
        const maxRows = Math.max(...probs.map(p => p.grid?.length || 0))
        for (let row = 0; row < maxRows; row++) {
            html += '<div class="row">'
            probs.forEach((p, i) => {
                const hasResult = results !== undefined
                const result = results?.[i] ?? 0
                const intensity = hasResult ? Math.min(1, Math.log10(result + 1) / Math.log10(maxResult + 1)) : 0
                const isMultiply = p.operator === '*'
                const gridRow = p.grid?.[row] || ''
                for (let c = 0; c < (p.grid?.[0]?.length || 0); c++) {
                    const ch = gridRow[c] || ' '
                    let style = ''
                    if (hasResult && ch !== ' ') {
                        const r = isMultiply ? Math.floor(255 * intensity) : 50
                        const g = 50
                        const b = isMultiply ? 50 : Math.floor(255 * intensity)
                        style = `background: rgb(${r},${g},${b}); color: #fff;`
                    }
                    html += `<div class="cell char${hasResult ? ' done' : ''}" data-idx="${i}" style="${style}">${ch}</div>`
                }
                html += `<div class="cell spacer"></div>`
            })
            html += '</div>'
        }
    } else {
        const maxRows = Math.max(...probs.map(p => p.numbers.length))
        for (let row = 0; row < maxRows; row++) {
            html += '<div class="row">'
            probs.forEach((p, i) => {
                const num = p.numbers[row]
                const hasResult = results !== undefined
                const result = results?.[i] ?? 0
                const intensity = hasResult ? Math.min(1, Math.log10(result + 1) / Math.log10(maxResult + 1)) : 0
                const isMultiply = p.operator === '*'
                let style = ''
                if (hasResult && num !== undefined) {
                    const r = isMultiply ? Math.floor(255 * intensity) : 50
                    const g = 50
                    const b = isMultiply ? 50 : Math.floor(255 * intensity)
                    style = `background: rgb(${r},${g},${b}); color: #fff;`
                }
                html += `<div class="cell${hasResult ? ' done' : ''}" data-idx="${i}" style="${style}">${num !== undefined ? num : ''}</div>`
            })
            html += '</div>'
        }
    }

    html += '<div class="row ops">'
    probs.forEach((p, i) => {
        const isMultiply = p.operator === '*'
        const width = isPart2 && p.grid ? p.grid[0].length + 1 : 1
        html += `<div class="cell op ${isMultiply ? 'mul' : 'add'}" data-idx="${i}" style="min-width:${width * 12}px">${p.operator}</div>`
    })
    html += '</div>'

    if (results) {
        html += '<div class="row results">'
        results.forEach((r, i) => {
            const intensity = Math.min(1, Math.log10(r + 1) / Math.log10(maxResult + 1))
            const isMultiply = probs[i].operator === '*'
            const red = isMultiply ? Math.floor(200 * intensity) : 30
            const blue = isMultiply ? 30 : Math.floor(200 * intensity)
            const width = isPart2 && probs[i].grid ? probs[i].grid[0].length + 1 : 1
            html += `<div class="cell result" data-idx="${i}" style="background: rgb(${red},50,${blue}); min-width:${width * 12}px">${r}</div>`
        })
        html += '</div>'
    }
    html += '</div>'
    dataEl.innerHTML = html
}

async function animateThreads(probs: any[]) {
    const grid = document.getElementById('grid')
    if (!grid) return
    const cells = grid.querySelectorAll('.cell[data-idx]')
    const n = probs.length
    for (let batch = 0; batch < n; batch += 64) {
        const end = Math.min(batch + 64, n)
        cells.forEach((cell: HTMLElement) => {
            const idx = parseInt(cell.dataset.idx || '0')
            if (idx >= batch && idx < end) cell.classList.add('processing')
        })
        await new Promise(r => setTimeout(r, 5))
        cells.forEach((cell: HTMLElement) => {
            const idx = parseInt(cell.dataset.idx || '0')
            if (idx >= batch && idx < end) cell.classList.remove('processing')
        })
    }
}


part1Btn.onclick = () => { currentPart = 1; part1Btn.classList.add('active'); part2Btn.classList.remove('active'); renderData(problems) }
part2Btn.onclick = () => { currentPart = 2; part2Btn.classList.add('active'); part1Btn.classList.remove('active'); renderData(problemsP2) }

function parse(input: string, cephalopod: boolean) {
    const lines = input.replace(/\r/g, '').split('\n').filter(l => l.trim())
    const dataLines = lines.slice(0, -1)
    const operatorLine = lines[lines.length - 1]
    const width = Math.max(...lines.map(l => l.length))
    const paddedData = dataLines.map(l => l.padEnd(width))
    const paddedOps = operatorLine.padEnd(width)

    let problems = []
    let inProblem = false
    let problemStart = 0

    for (let col = 0; col <= width; col++) {
        const allSpace = col === width || (paddedData.every(line => line[col] === ' ') && paddedOps[col] === ' ')
        if (!allSpace && !inProblem) { inProblem = true; problemStart = col }
        else if (allSpace && inProblem) {
            inProblem = false
            const operator = paddedOps.slice(problemStart, col).trim()
            if (cephalopod) {
                const grid: string[] = paddedData.map(line => line.slice(problemStart, col))
                const blockWidth = col - problemStart
                const numbers: number[] = []
                for (let c = blockWidth - 1; c >= 0; c--) {
                    let digits = ''
                    for (let r = 0; r < grid.length; r++) {
                        const ch = grid[r][c]
                        if (ch && ch !== ' ') digits += ch
                    }
                    if (digits) numbers.push(parseInt(digits, 10))
                }
                if (numbers.length > 0) problems.push({ numbers, operator, grid })
            } else {
                let numbers = []
                for (const line of paddedData) {
                    const slice = line.slice(problemStart, col).trim()
                    if (slice) numbers.push(parseInt(slice, 10))
                }
                problems.push({ numbers, operator })
            }
        }
    }
    return problems
}

const SHADER_F64 = `
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
}`

const SHADER_U32X2 = `
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
}`

async function run_gpu(probs: any[]) {
    const n = probs.length
    const maxNums = Math.max(...probs.map(p => p.numbers.length))

    let numbersFlat = new Float64Array(n * maxNums)
    let operators = new Uint32Array(n)
    let counts = new Uint32Array(n)

    probs.forEach((p, i) => {
        const base = i * maxNums
        const identity = p.operator === '*' ? 1 : 0
        for (let j = 0; j < maxNums; j++) numbersFlat[base + j] = p.numbers[j] ?? identity
        operators[i] = p.operator === '*' ? 0 : 1
        counts[i] = p.numbers.length
    })

    const adapter = await navigator.gpu.requestAdapter()
    const features: GPUFeatureName[] = []
    if (adapter.features.has('shader-f64')) features.push('shader-f64')
    const device = await adapter.requestDevice({ requiredFeatures: features })
    const hasF64 = device.features.has('shader-f64')

    if (hasF64) {
        const inputData = numbersFlat
        const numBuf = device.createBuffer({ size: inputData.byteLength, usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST })
        const opBuf = device.createBuffer({ size: operators.byteLength, usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST })
        const countBuf = device.createBuffer({ size: counts.byteLength, usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST })
        const resBuf = device.createBuffer({ size: n * 8, usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_SRC })
        const stageBuf = device.createBuffer({ size: n * 8, usage: GPUBufferUsage.MAP_READ | GPUBufferUsage.COPY_DST })
        const uniformBuf = device.createBuffer({ size: 4, usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST })

        device.queue.writeBuffer(numBuf, 0, inputData)
        device.queue.writeBuffer(opBuf, 0, operators)
        device.queue.writeBuffer(countBuf, 0, counts)
        device.queue.writeBuffer(uniformBuf, 0, new Uint32Array([maxNums]))

        const shader = device.createShaderModule({ code: SHADER_F64 })
        const pipeline = device.createComputePipeline({ layout: 'auto', compute: { module: shader, entryPoint: 'main' } })
        const bindGroup = device.createBindGroup({
            layout: pipeline.getBindGroupLayout(0),
            entries: [
                { binding: 0, resource: { buffer: numBuf } },
                { binding: 1, resource: { buffer: opBuf } },
                { binding: 2, resource: { buffer: countBuf } },
                { binding: 3, resource: { buffer: resBuf } },
                { binding: 4, resource: { buffer: uniformBuf } },
            ]
        })

        const encoder = device.createCommandEncoder()
        const pass = encoder.beginComputePass()
        pass.setPipeline(pipeline)
        pass.setBindGroup(0, bindGroup)
        pass.dispatchWorkgroups(Math.ceil(n / 64))
        pass.end()
        encoder.copyBufferToBuffer(resBuf, 0, stageBuf, 0, n * 8)
        device.queue.submit([encoder.finish()])

        await stageBuf.mapAsync(GPUMapMode.READ)
        const results = new Float64Array(stageBuf.getMappedRange().slice(0))
        stageBuf.unmap()
        numBuf.destroy(); opBuf.destroy(); countBuf.destroy(); resBuf.destroy(); stageBuf.destroy(); uniformBuf.destroy()
        console.log('GPU f64:', n, maxNums)
        return Array.from(results)
    } else {
        const inputData = new Uint32Array(n * maxNums)
        probs.forEach((p, i) => {
            const base = i * maxNums
            const identity = p.operator === '*' ? 1 : 0
            for (let j = 0; j < maxNums; j++) inputData[base + j] = p.numbers[j] ?? identity
        })

        const numBuf = device.createBuffer({ size: inputData.byteLength, usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST })
        const opBuf = device.createBuffer({ size: operators.byteLength, usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST })
        const countBuf = device.createBuffer({ size: counts.byteLength, usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST })
        const resLoBuf = device.createBuffer({ size: n * 4, usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_SRC })
        const resHiBuf = device.createBuffer({ size: n * 4, usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_SRC })
        const stageLoBuf = device.createBuffer({ size: n * 4, usage: GPUBufferUsage.MAP_READ | GPUBufferUsage.COPY_DST })
        const stageHiBuf = device.createBuffer({ size: n * 4, usage: GPUBufferUsage.MAP_READ | GPUBufferUsage.COPY_DST })
        const uniformBuf = device.createBuffer({ size: 4, usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST })

        device.queue.writeBuffer(numBuf, 0, inputData)
        device.queue.writeBuffer(opBuf, 0, operators)
        device.queue.writeBuffer(countBuf, 0, counts)
        device.queue.writeBuffer(uniformBuf, 0, new Uint32Array([maxNums]))

        const shader = device.createShaderModule({ code: SHADER_U32X2 })
        const pipeline = device.createComputePipeline({ layout: 'auto', compute: { module: shader, entryPoint: 'main' } })
        const bindGroup = device.createBindGroup({
            layout: pipeline.getBindGroupLayout(0),
            entries: [
                { binding: 0, resource: { buffer: numBuf } },
                { binding: 1, resource: { buffer: opBuf } },
                { binding: 2, resource: { buffer: countBuf } },
                { binding: 3, resource: { buffer: resLoBuf } },
                { binding: 4, resource: { buffer: resHiBuf } },
                { binding: 5, resource: { buffer: uniformBuf } },
            ]
        })

        const encoder = device.createCommandEncoder()
        const pass = encoder.beginComputePass()
        pass.setPipeline(pipeline)
        pass.setBindGroup(0, bindGroup)
        pass.dispatchWorkgroups(Math.ceil(n / 64))
        pass.end()
        encoder.copyBufferToBuffer(resLoBuf, 0, stageLoBuf, 0, n * 4)
        encoder.copyBufferToBuffer(resHiBuf, 0, stageHiBuf, 0, n * 4)
        device.queue.submit([encoder.finish()])

        await Promise.all([stageLoBuf.mapAsync(GPUMapMode.READ), stageHiBuf.mapAsync(GPUMapMode.READ)])
        const loResults = new Uint32Array(stageLoBuf.getMappedRange().slice(0))
        const hiResults = new Uint32Array(stageHiBuf.getMappedRange().slice(0))
        stageLoBuf.unmap(); stageHiBuf.unmap()

        const results: number[] = []
        for (let i = 0; i < n; i++) results.push(hiResults[i] * 0x100000000 + loResults[i])

        numBuf.destroy(); opBuf.destroy(); countBuf.destroy(); resLoBuf.destroy(); resHiBuf.destroy()
        stageLoBuf.destroy(); stageHiBuf.destroy(); uniformBuf.destroy()
        console.log('GPU u32x2:', n, maxNums)
        return results
    }
}

async function solve(part: number) {
    const probs = part === 1 ? problems : problemsP2
    renderData(probs)
    const results = await run_gpu(probs)
    await animateThreads(probs)
    renderData(probs, results)
    return results.reduce((a, b) => a + b, 0)
}

function updateTimer() {
    const elapsed = (performance.now() - startTime) / 1000
    timeEl.textContent = elapsed.toFixed(3)
}

startBtn.onclick = async () => {
    if (running) return
    running = true
    startBtn.disabled = true
    stopBtn.disabled = false
    resultEl.textContent = '-'
    statusEl.textContent = 'Running...'
    statusEl.className = 'status'
    startTime = performance.now()
    timerInterval = setInterval(updateTimer, 10)
    try {
        const result = await solve(currentPart)
        if (running) {
            clearInterval(timerInterval!)
            updateTimer()
            resultEl.textContent = String(result)
            statusEl.textContent = 'Done!'
        }
    } catch (e) {
        if (running) {
            clearInterval(timerInterval!)
            resultEl.textContent = 'Error'
            statusEl.textContent = String(e)
            statusEl.className = 'status error'
        }
    }
    running = false
    startBtn.disabled = false
    stopBtn.disabled = true
}

stopBtn.onclick = () => {
    running = false
    if (timerInterval) clearInterval(timerInterval)
    statusEl.textContent = 'Stopped'
    startBtn.disabled = false
    stopBtn.disabled = true
}

loadInput()
