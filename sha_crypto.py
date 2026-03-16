import hashlib
import time
#import sys
#import os

def sha256_file(filepath):
    with open(filepath, "rb") as f:
        file = f.read()
    start = time.perf_counter()
    hashlib.sha256(file).digest()
    end = time.perf_counter()
    time_us = (end - start) * 1000000
    return time_us

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