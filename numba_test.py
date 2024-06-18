from numba import cuda
import numpy as np
import time

@cuda.jit
def gpu_add(a, b, c):
    i = cuda.grid(1)
    if i < a.size:
        c[i] = a[i] + b[i]

# Function for CPU addition for comparison
def cpu_add(a, b, c):
    for i in range(a.size):
        c[i] = a[i] + b[i]

n = 1000000
a = np.random.rand(n)
b = np.random.rand(n)
c_gpu = np.empty(n)
c_cpu = np.empty(n)

# Define GPU threads and blocks
threads_per_block = 256
blocks_per_grid = (a.size + (threads_per_block - 1)) // threads_per_block

# Measure GPU execution time
start_time = time.time()
gpu_add[blocks_per_grid, threads_per_block](a, b, c_gpu)
cuda.synchronize()  # Ensure GPU computation is finished
gpu_time = time.time() - start_time

# Measure CPU execution time
start_time = time.time()
cpu_add(a, b, c_cpu)
cpu_time = time.time() - start_time

# Print results
print(f"GPU result: {c_gpu[:10]}")  # Print first 10 elements for brevity
print(f"CPU result: {c_cpu[:10]}")  # Print first 10 elements for brevity
print(f"Execution time on GPU: {gpu_time:.6f} seconds")
print(f"Execution time on CPU: {cpu_time:.6f} seconds")
