import sha_crypto
import statistics
import matplotlib.pyplot as plt
import pandas as pd
import math

results = []

print("File Size (B) | Throughput (B/µs) | 95% CI (µs) ")
print("--------------+-------------------+-------------")

files = [
    (8, "file_8.bin"),
    (64, "file_64.bin"),
    (512, "file_512.bin"),
    (4096, "file_4096.bin"),
    (32768, "file_32768.bin"),
    (262144, "file_262144.bin"),
    (2097152, "file_2097152.bin")
]

for size, f in files:

    runs = 100 if size > 512 else 500

    all_times = sha_crypto.sha256_file(f, runs=runs)

    avg_time = statistics.mean(all_times)
    std_dev = statistics.stdev(all_times)

    throughput = size / avg_time

    n = len(all_times)
    ci = 1.96 * (std_dev / math.sqrt(n))

    ci_rel = ci / avg_time

    print(f"{size:<13} | {throughput:<17.6f} | ±{ci_rel:.4f}")

    results.append({
        "Size": size,
        "MeanTime": avg_time,
        "CI": ci,
    })

# === Plotting the results (Gemini) ===

df = pd.DataFrame(results)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

axes[0].errorbar(
    df["Size"],
    df["MeanTime"],
    yerr=df["CI"],
    marker='o',
    linestyle='-',
    capsize=5
)
axes[0].set_title("Linear Scale")
axes[0].set_xlabel("File Size (Bytes)")
axes[0].set_ylabel("Time (Microseconds)")
axes[0].grid(True, ls="--", alpha=0.5)

axes[1].errorbar(
    df["Size"],
    df["MeanTime"],
    yerr=df["CI"],
    marker='o',
    linestyle='-',
    capsize=5
)
axes[1].set_title("Log-Log Scale")
axes[1].set_xlabel("File Size (Bytes)")
axes[1].set_ylabel("Time (Microseconds)")
axes[1].set_xscale('log')
axes[1].set_yscale('log')
axes[1].grid(True, which="both", ls="--", alpha=0.5)

plt.tight_layout()
# plt.show()
plt.savefig("sha256_benchmark.png")

# Questions To Be Answered:
# 1.- What does it mean to assess performance?
# 2.- Why are the comparisons meaningful?
# 3.- What conclusions can be derived?