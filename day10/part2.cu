/*
 * __global__ : Declaration specifier for kernel functions
 */
extern "C" __global__ void solve_machines(
    const int* all_targets,
    const int* target_offsets,
    const int* num_counters,
    const int* all_button_indices,
    const int* button_index_offsets,
    const int* button_index_counts,
    const int* buttons_per_machine,
    const int* button_group_offsets,
    const int* max_target_per_machine,
    int* results,
    int N)
{
    /*
     * Built-in variables
     * - blockIdx.x : "index of the block within the grid"
     * - threadIdx.x : "index of the thread within the block"
     * - blockDim.x : "number of threads per block"
     */
    int blockId = blockIdx.x;
    // boundary check
    if (blockId >= N) return;

    // load problem parameters for this block
    int targetOffset = target_offsets[blockId];
    int numCounters = num_counters[blockId];
    int numButtons = buttons_per_machine[blockId];
    int buttonGroupOffset = button_group_offsets[blockId];
    int maxTarget = max_target_per_machine[blockId];

    __shared__ long long matrix[16][20];
    __shared__ int pivotCol[16];
    __shared__ int freeVars[16];
    __shared__ int numFree;
    __shared__ int bestResult;

    int threadId = threadIdx.x;
    int numCols = numButtons + 1;

    if (threadId == 0) {
        bestResult = 999999999;
        numFree = 0;

        for (int i = 0; i < numCounters; i++) {
            for (int j = 0; j < numCols; j++) {
                matrix[i][j] = 0;
            }
            pivotCol[i] = -1;
        }

        for (int b = 0; b < numButtons; b++) {
            int buttonIndex = buttonGroupOffset + b;
            int indexOffset = button_index_offsets[buttonIndex];
            int indexCount = button_index_counts[buttonIndex];

            for (int k = 0; k < indexCount; k++) {
                int counter = all_button_indices[indexOffset + k];
                if (counter < numCounters) {
                    matrix[counter][b] = 1;
                }
            }
        }

        for (int i = 0; i < numCounters; i++) {
            matrix[i][numButtons] = all_targets[targetOffset + i];
        }

        int h = 0;
        int k = 0;

        while (h < numCounters && k < numButtons) {
            int i_max = h;
            long long maxVal = 0;
            for (int i = h; i < numCounters; i++) {
                long long v = matrix[i][k];
                if (v < 0) v = -v;
                if (v > maxVal) {
                    maxVal = v;
                    i_max = i;
                }
            }

            if (maxVal == 0) {
                k++;
            } else {
                for (int j = 0; j < numCols; j++) {
                    long long tmp = matrix[h][j];
                    matrix[h][j] = matrix[i_max][j];
                    matrix[i_max][j] = tmp;
                }

                pivotCol[h] = k;

                for (int i = 0; i < numCounters; i++) {
                    if (i == h) continue;

                    long long num = matrix[i][k];
                    long long denom = matrix[h][k];

                    if (num != 0) {
                        int needScale = 0;
                        for (int j = k + 1; j < numCols; j++) {
                            long long product = num * matrix[h][j];
                            long long absProd = product < 0 ? -product : product;
                            long long absDenom = denom < 0 ? -denom : denom;
                            if (absProd % absDenom != 0) {
                                needScale = 1;
                                break;
                            }
                        }

                        if (needScale) {
                            long long absDenom = denom < 0 ? -denom : denom;
                            for (int j = 0; j < numCols; j++) {
                                matrix[i][j] *= absDenom;
                            }
                            denom = denom < 0 ? -1 : 1;
                        }

                        for (int j = k + 1; j < numCols; j++) {
                            matrix[i][j] -= matrix[h][j] * num / denom;
                        }
                        matrix[i][k] = 0;
                    }
                }

                h++;
                k++;
            }
        }

        for (int col = 0; col < numButtons; col++) {
            int hasPivot = 0;
            for (int row = 0; row < numCounters; row++) {
                if (pivotCol[row] == col) {
                    hasPivot = 1;
                    break;
                }
            }
            if (!hasPivot) {
                freeVars[numFree++] = col;
            }
        }
    }

    __syncthreads();

    int effectiveRows = numCounters;
    while (effectiveRows > 0) {
        int allZero = 1;
        for (int j = 0; j < numCols; j++) {
            if (matrix[effectiveRows - 1][j] != 0) {
                allZero = 0;
                break;
            }
        }
        if (allZero) effectiveRows--;
        else break;
    }

    if (numFree == 0) {
        if (threadId == 0) {
            int ans = 0;
            int valid = 1;
            for (int row = 0; row < effectiveRows; row++) {
                int col = pivotCol[row];
                if (col < 0) continue;

                long long num = matrix[row][numButtons];
                long long denom = matrix[row][col];

                if (denom == 0) { valid = 0; break; }

                long long absNum = num < 0 ? -num : num;
                long long absDenom = denom < 0 ? -denom : denom;
                if (absNum % absDenom != 0) { valid = 0; break; }

                long long val = num / denom;
                if (val < 0) { valid = 0; break; }

                ans += (int)val;
            }
            if (valid) {
                bestResult = ans;
            }
        }
    } else {
        long long maxVal = maxTarget + 1;
        long long totalCombos = 1;
        for (int f = 0; f < numFree && f < 4; f++) {
            totalCombos *= maxVal;
            if (totalCombos > 100000000LL) {
                totalCombos = 100000000LL;
                break;
            }
        }

        for (long long combo = threadId; combo < totalCombos; combo += blockDim.x) {
            int freeVals[4] = {0, 0, 0, 0};
            long long temp = combo;

            int sumFree = 0;
            for (int f = 0; f < numFree && f < 4; f++) {
                freeVals[f] = (int)(temp % maxVal);
                temp /= maxVal;
                sumFree += freeVals[f];
            }

            int valid = 1;
            int ans = sumFree;

            for (int row = effectiveRows - 1; row >= 0; row--) {
                int col = pivotCol[row];
                if (col < 0) continue;

                long long rhs = matrix[row][numButtons];

                for (int f = 0; f < numFree && f < 4; f++) {
                    rhs -= matrix[row][freeVars[f]] * freeVals[f];
                }

                long long denom = matrix[row][col];
                if (denom == 0) { valid = 0; break; }

                long long absRhs = rhs < 0 ? -rhs : rhs;
                long long absDenom = denom < 0 ? -denom : denom;
                if (absRhs % absDenom != 0) { valid = 0; break; }

                long long val = rhs / denom;
                if (val < 0) { valid = 0; break; }

                ans += (int)val;
            }

            if (valid) {
                atomicMin(&bestResult, ans);
            }
        }
    }

    __syncthreads();

    if (threadId == 0) {
        results[blockId] = (bestResult == 999999999) ? 0 : bestResult;
    }
}
