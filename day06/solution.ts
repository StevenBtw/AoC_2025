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
let SHADER_U32X2 = ''

async function loadInput() {
    SHADER_U32X2 = await fetch('shader_u32x2.wgsl').then(r => r.text())
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

    probs.forEach((p, i) => {
        const hasResult = results !== undefined
        const result = results?.[i] ?? 0
        const intensity = hasResult ? Math.min(1, Math.log10(result + 1) / Math.log10(maxResult + 1)) : 0
        const isMultiply = p.operator === '*'

        html += `<div class="problem-col" data-idx="${i}">`

        if (isPart2 && p.grid) {
            for (let row = 0; row < p.grid.length; row++) {
                html += '<div class="char-row">'
                for (let c = 0; c < p.grid[0].length; c++) {
                    const ch = p.grid[row][c] || ' '
                    let style = ''
                    if (hasResult && ch !== ' ') {
                        const r = isMultiply ? Math.floor(255 * intensity) : 50
                        const g = 50
                        const b = isMultiply ? 50 : Math.floor(255 * intensity)
                        style = `background: rgb(${r},${g},${b}); color: #fff;`
                    }
                    html += `<div class="cell char${hasResult ? ' done' : ''}" style="${style}">${ch}</div>`
                }
                html += '</div>'
            }
        } else {
            for (const num of p.numbers) {
                let style = ''
                if (hasResult) {
                    const r = isMultiply ? Math.floor(255 * intensity) : 50
                    const g = 50
                    const b = isMultiply ? 50 : Math.floor(255 * intensity)
                    style = `background: rgb(${r},${g},${b}); color: #fff;`
                }
                html += `<div class="cell${hasResult ? ' done' : ''}" style="${style}">${num}</div>`
            }
        }

        html += `<div class="cell op ${isMultiply ? 'mul' : 'add'}">${p.operator}</div>`

        if (hasResult) {
            const red = isMultiply ? Math.floor(200 * intensity) : 30
            const blue = isMultiply ? 30 : Math.floor(200 * intensity)
            html += `<div class="cell result" style="background: rgb(${red},50,${blue})">${result}</div>`
        }

        html += '</div>'
    })

    html += '</div>'
    dataEl.innerHTML = html
}

async function animateThreads(probs: any[]) {
    const grid = document.getElementById('grid')
    if (!grid) return
    const cols = grid.querySelectorAll('.problem-col') as NodeListOf<HTMLElement>
    const n = probs.length
    for (let batch = 0; batch < n; batch += 64) {
        const end = Math.min(batch + 64, n)
        cols.forEach(col => {
            const idx = parseInt(col.dataset.idx || '0')
            if (idx >= batch && idx < end) col.querySelectorAll('.cell').forEach(c => c.classList.add('processing'))
        })
        await new Promise(r => setTimeout(r, 5))
        cols.forEach(col => {
            const idx = parseInt(col.dataset.idx || '0')
            if (idx >= batch && idx < end) col.querySelectorAll('.cell').forEach(c => c.classList.remove('processing'))
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

async function run_gpu(probs: any[]) {
    const n = probs.length
    const maxNums = Math.max(...probs.map(p => p.numbers.length))

    let numbersFlat = new Uint32Array(n * maxNums)
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
    const device = await adapter!.requestDevice()

    const numBuf = device.createBuffer({ size: numbersFlat.byteLength, usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST })
    const opBuf = device.createBuffer({ size: operators.byteLength, usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST })
    const countBuf = device.createBuffer({ size: counts.byteLength, usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST })
    const resLoBuf = device.createBuffer({ size: n * 4, usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_SRC })
    const resHiBuf = device.createBuffer({ size: n * 4, usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_SRC })
    const stageLoBuf = device.createBuffer({ size: n * 4, usage: GPUBufferUsage.MAP_READ | GPUBufferUsage.COPY_DST })
    const stageHiBuf = device.createBuffer({ size: n * 4, usage: GPUBufferUsage.MAP_READ | GPUBufferUsage.COPY_DST })
    const uniformBuf = device.createBuffer({ size: 4, usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST })

    device.queue.writeBuffer(numBuf, 0, numbersFlat)
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
    const lo = new Uint32Array(stageLoBuf.getMappedRange().slice(0))
    const hi = new Uint32Array(stageHiBuf.getMappedRange().slice(0))
    stageLoBuf.unmap(); stageHiBuf.unmap()
    numBuf.destroy(); opBuf.destroy(); countBuf.destroy(); resLoBuf.destroy(); resHiBuf.destroy(); stageLoBuf.destroy(); stageHiBuf.destroy(); uniformBuf.destroy()
    return Array.from(lo).map((l, i) => l + hi[i] * 0x100000000)
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
