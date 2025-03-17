import numpy as np
import numba
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

@numba.jit(nopython=True, parallel=True)
def fast_monte_carlo(S0, K, T, r, sigma, paths, steps, option_type=1):
    dt = T / steps
    result = np.zeros(paths)
    
    for i in numba.prange(paths):
        S = S0
        for j in range(steps):
            z = np.random.normal(0, 1)
            S = S * np.exp((r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z)
        
        if option_type == 1:  # Call
            result[i] = max(0, S - K)
        else:  # Put
            result[i] = max(0, K - S)
    
    return np.exp(-r * T) * np.mean(result)

def parallel_monte_carlo(S0, K, T, r, sigma, total_paths, steps, option_type='call', num_processes=None):
    if num_processes is None:
        num_processes = multiprocessing.cpu_count()
    
    paths_per_process = total_paths // num_processes
    
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        futures = [
            executor.submit(
                fast_monte_carlo, 
                S0, K, T, r, sigma, 
                paths_per_process, 
                steps, 
                1 if option_type.lower() == 'call' else 0
            )
            for _ in range(num_processes)
        ]
        
        results = [future.result() for future in futures]
    
    return np.mean(results) 