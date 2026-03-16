import hashlib
import timeit

def sha256_file(filepath, runs=50):
    with open(filepath, "rb") as f:
        data = f.read()

    def hash_operation():
        hashlib.sha256(data).digest()

    total_time = timeit.timeit(hash_operation, number=runs)
    avg_time = (total_time / runs) * 1_000_000

    return avg_time

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
        t = sha256_file(f)
        print(f"{f}: {round(t, 2)} microseconds")