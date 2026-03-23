import hashlib
import timeit
import statistics

def sha256_file(filepath, runs=100):
    with open(filepath, "rb") as f:
        data = f.read()

    timer = timeit.Timer(lambda: hashlib.sha256(data).digest())

    # Warm-up
    timer.timeit(number=10)

    total_time = timer.timeit(number=runs)
    return (total_time / runs) * 1_000_000  # microseconds

def sha256_file_stats(filepath, runs=100):
    with open(filepath, "rb") as f:
        data = f.read()

    timer = timeit.Timer(lambda: hashlib.sha256(data).digest())
    raw_times = timer.repeat(repeat=runs, number=1)

    return [t * 1_000_000 for t in raw_times]

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
        avg = sha256_file(f)
        stats = sha256_file_stats(f)

        print(f"{f}: {avg:.2f} µs (avg)")
        print(f"{f}: min={min(stats):.2f} µs, max={max(stats):.2f} µs, mean={statistics.mean(stats):.2f} µs")