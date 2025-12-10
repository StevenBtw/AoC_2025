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
    int threadId = threadIdx.x;

    // boundary check
    if (blockId >= N) return;

    // load problem parameters for this block
    int targetOffset = target_offsets[blockId];
    int numCounters = num_counters[blockId];
    int numButtons = buttons_per_machine[blockId];
    int buttonGroupOffset = button_group_offsets[blockId];
    int maxTarget = max_target_per_machine[blockId];

    /*
     * __shared__ : "Variables declared with __shared__ qualifier reside in
     * shared memory of a thread block"
     */
    __shared__ int sharedBestResult;

    // thread 0 initializes shared memory
    if (threadId == 0) {
        sharedBestResult = 99999;
    }

    // Synchronize to ensure shared memory is populated
    __syncthreads();

    /*
     * Local arrays stored in registers/local memory
     */
    int targetValues[32];
    int workingState[32];

    // copy target values from global memory to local memory
    for (int i = 0; i < numCounters; i++) {
        targetValues[i] = all_targets[targetOffset + i];
    }

    /*
     * Grid-stride loop pattern for work distribution
     */
    long long totalCombinations = 1;
    int base = maxTarget + 1;
    for (int b = 0; b < numButtons; b++) {
        totalCombinations *= base;
        if (totalCombinations > 100000000LL) {
            totalCombinations = 100000000LL;
            break;
        }
    }

    for (long long combination = threadId; combination < totalCombinations; combination += blockDim.x) {

        // initialize working state to all zeros
        for (int i = 0; i < numCounters; i++) {
            workingState[i] = 0;
        }

        // Count number of buttons pressed
        int buttonPressCount = 0;
        long long temp = combination;

        // iterate through each button
        for (int b = 0; b < numButtons; b++) {
            int presses = temp % base;
            temp /= base;
            buttonPressCount = buttonPressCount + presses;

            // get indices that this button toggles
            int buttonIndex = buttonGroupOffset + b;
            int indexOffset = button_index_offsets[buttonIndex];
            int indexCount = button_index_counts[buttonIndex];

            // toggle each position
            for (int j = 0; j < indexCount; j++) {
                int position = all_button_indices[indexOffset + j];
                workingState[position] += presses;
            }
        }

        int isMatch = 1;
        for (int i = 0; i < numCounters; i++) {
            if (workingState[i] != targetValues[i]) {
                isMatch = 0;
            }
        }

        // update best result if this combination also solves
        if (isMatch == 1) {
            atomicMin(&sharedBestResult, buttonPressCount);
        }
    }

    // synchronize before reading final result
    __syncthreads();

    // thread 0 writes the result to global memory
    if (threadId == 0) {
        if (sharedBestResult == 99999) {
            results[blockId] = 0;
        } else {
            results[blockId] = sharedBestResult;
        }
    }
}
