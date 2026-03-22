import sha_crypto
import statistics

iterations = 50
sizes = [8, 64, 512, 4096, 32768, 262144, 2097152]
print_flag = False

sha_plot_data = {}

for size in sizes:

    filename = f"file_{size}.bin"
    times = []

    print(f"\nSIZE    : {size} bytes")

    for i in range(iterations):
        time_us = sha_crypto.sha256_file(filename)
        times.append(time_us)

        if print_flag:
            i = i + 1
            print(f"iteration {i}: {time_us:.2f} us")

    average = statistics.mean(times)
    median = statistics.median(times)
    std_dev = statistics.stdev(times)

    sha_plot_data[size] = {
        "times": times,
        "average": average,
        "median": median,
        "std_dev": std_dev
    }

    print("average :", round(average, 2), "us")
    print("median  :", round(median, 2), "us")
    print("std dev :", round(std_dev, 2), "us")

# === PLOTTING STARTS HERE (ChatGPT) ===
import matplotlib.pyplot as plt

file_sizes = list(sha_plot_data.keys())
average_times = [sha_plot_data[size]["average"] for size in file_sizes]
std_devs = [sha_plot_data[size]["std_dev"] for size in file_sizes]

plt.figure(figsize=(8,5))
plt.errorbar(file_sizes, average_times, yerr=std_devs, fmt='o-', capsize=5, label='SHA-256')

plt.xlabel("File Size (bytes)")
plt.ylabel("Time (microseconds)")
plt.title("SHA-256 Hashing Time vs File Size")
plt.xscale('log')
plt.yscale('log')
plt.grid(True, which="both", ls="--")
plt.legend()
plt.tight_layout()
plt.show()