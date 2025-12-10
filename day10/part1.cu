/*
 * __global__ : Declaration specifier for kernel functions
 */
extern "C" __global__ void solve_machines(
    const char* all_patterns,
    const int* pattern_offsets,
    const int* pattern_lengths,
    const int* all_button_indices,
    const int* button_index_offsets,
    const int* button_index_counts,
    const int* buttons_per_machine,
    const int* button_group_offsets,
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
    int patternOffset = pattern_offsets[blockId];
    int patternLength = pattern_lengths[blockId];
    int numButtons = buttons_per_machine[blockId];
    int buttonGroupOffset = button_group_offsets[blockId];

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
    char targetPattern[32];
    char workingState[32];

    // copy target pattern from global memory to local memory
    for (int i = 0; i < patternLength; i++) {
        targetPattern[i] = all_patterns[patternOffset + i];
    }

    /*
     * Grid-stride loop pattern for work distribution
     */
    int totalCombinations = 1 << numButtons;

    for (int combination = threadId; combination < totalCombinations; combination += blockDim.x) {

        // initialize working state to all '.' characters
        for (int i = 0; i < patternLength; i++) {
            workingState[i] = '.';
        }

        // Count number of buttons pressed
        int buttonPressCount = 0;

        // iterate through each button
        for (int b = 0; b < numButtons; b++) {
            // check if bit b is set in combination
            if ((combination >> b) & 1) {
                buttonPressCount = buttonPressCount + 1;

                // get indices that this button toggles
                int buttonIndex = buttonGroupOffset + b;
                int indexOffset = button_index_offsets[buttonIndex];
                int indexCount = button_index_counts[buttonIndex];

                // toggle each position
                for (int j = 0; j < indexCount; j++) {
                    int position = all_button_indices[indexOffset + j];
                    if (workingState[position] == '.') {
                        workingState[position] = '#';
                    } else {
                        workingState[position] = '.';
                    }
                }
            }
        }

        int isMatch = 1;
        for (int i = 0; i < patternLength; i++) {
            if (workingState[i] != targetPattern[i]) {
                isMatch = 0;
                break;
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
