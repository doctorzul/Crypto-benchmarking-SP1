import sha_crypto
# import hashlib
# import timeit
import os
import statistics
import matplotlib.pyplot as plt
import pandas as pd
import math

file_sizes = [8, 64, 512, 4096, 32768, 262144, 2097152]
results = []

print("File Size       | Average Time | Median Time  | Std Dev    | CI (95%)")

for size in file_sizes:
    temp_path = f"test_{size}.bin"
    with open(temp_path, "wb") as f:
        f.write(os.urandom(size))
    
    all_times = sha_crypto.sha256_file_stats(
        temp_path, 
        # runs=1000 if size <= 10240 else 500
        runs=500
    )
    
    avg_time = statistics.mean(all_times)
    med_time = statistics.median(all_times)
    std_dev = statistics.stdev(all_times)
    
    n = len(all_times)
    ci_95 = 1.96 * (std_dev / math.sqrt(n))
    
    print(f"{size:<15} | {avg_time:<12.2f} | {med_time:<12.2f} | {std_dev:<10.2f} | ±{ci_95:.2f}")
    
    results.append({
        "Size": size, 
        "Mean": avg_time, 
        "StdDev": std_dev,
        "CI": ci_95
    })
    
    os.remove(temp_path)

# === Plotting the results (Gemini) ===

df = pd.DataFrame(results)

plt.figure(figsize=(10, 6))

plt.errorbar(
    df["Size"], 
    df["Mean"], 
    yerr=df["CI"], 
    marker='o',
    linestyle='-',
    capsize=5
)

plt.title("SHA-256 Generation Time vs. File Size (with 95% CI)")
plt.xlabel("File Size (Bytes)")
plt.ylabel("Time (Microseconds)")
plt.xscale('log')
plt.yscale('log')
plt.grid(True, which="both", ls="--", alpha=0.5)

plt.show()

# Questions To Be Answered:
# 1.- What does it mean to assess performance?
# 2.- Why are the comparisons meaningful?
# 3.- What conclusions can be derived?