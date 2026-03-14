import hashlib
import time
import sys

def sha256_file(filepath):
    with open(filepath, "rb") as f:
        file = f.read()
    start = time.perf_counter()
    hashlib.sha256(file).digest()
    end = time.perf_counter()
    time_micros = (end - start) * 1000000
    return time_micros

if __name__ == "__main__":
    file = sys.argv[1]
    time_taken = sha256_file(file)
    print("SHA-256 hashing time:", round(time_taken, 2), "microseconds")