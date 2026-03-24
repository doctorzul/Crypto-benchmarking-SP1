import hashlib
import timeit
import statistics

def sha256_file(filepath, runs=100):
    with open(filepath, "rb") as f:
        data = f.read()

    timer = timeit.Timer(lambda: hashlib.sha256(data).digest())

    # Warm-up
    timer.timeit(number=10)

    raw_times = timer.repeat(repeat=runs, number=1)

    return [t * 1000000 for t in raw_times]

if __name__ == "__main__":
    files = [
        "file_8.bin",
        "file_64.bin",
        "file_512.bin",
        "file_4096.bin",
        "file_32768.bin",
        "file_262144.bin",
        "file_2097152.bin"
    ]

    for f in files:
        times = sha256_file(f, runs=100)

        print(f"{f}:")
        print(f"  mean   = {statistics.mean(times):.2f} µs")
        print(f"  median = {statistics.median(times):.2f} µs")
        print(f"  stddev = {statistics.stdev(times):.2f} µs")