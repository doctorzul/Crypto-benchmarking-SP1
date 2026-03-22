import os
import timeit
import utils
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# Cryptography documentation example modified by removing GCM extra authentication steps

def encrypt_ctr(key, plaintext):
    # 128 bites block, minimum required by the library for the initial counter value
    nonce = os.urandom(16)

    encryptor = Cipher(
        algorithms.AES(key),
        modes.CTR(nonce),
    ).encryptor()

    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    return (nonce, ciphertext)

def decrypt_ctr(key, nonce, ciphertext):
    decryptor = Cipher(
        algorithms.AES(key),
        modes.CTR(nonce),
    ).decryptor()

    return decryptor.update(ciphertext) + decryptor.finalize()

################## Benchmarking ##################

def benchmark_aes(filename, iterations=100):
    # Benchmarks AES-CTR
    # Returns a tuple of two lists: (encryption_times_ms, decryption_times_ms)
    
    if not os.path.exists(filename):
        return [], []

    with open(filename, "rb") as f:
        data = f.read()
    
    key = os.urandom(32)

    # Measure Encryption
    enc_times = timeit.repeat(lambda: encrypt_ctr(key, data), repeat=iterations, number=1)
    enc_times_ms = [t * 1000 for t in enc_times] # Convert to ms

    # Measure Decryption
    nonce, ciphertext = encrypt_ctr(key, data)
    dec_times = timeit.repeat(lambda: decrypt_ctr(key, nonce, ciphertext), repeat=iterations, number=1)
    dec_times_ms = [t * 1000 for t in dec_times]

    return enc_times_ms, dec_times_ms

def benchmark_aes_random(size, iterations=100):
    # Benchmarks AES-CTR using randomly generated data
    # Returns a tuple of two lists: (encryption_times_ms, decryption_times_ms)
    
    # Generate random bytes in memory
    data = os.urandom(size)
    key = os.urandom(32)

    # Measure Encryption
    enc_times = timeit.repeat(lambda: encrypt_ctr(key, data), repeat=iterations, number=1)
    enc_times_ms = [t * 1000 for t in enc_times]

    # Measure Decryption
    nonce, ciphertext = encrypt_ctr(key, data)
    dec_times = timeit.repeat(lambda: decrypt_ctr(key, nonce, ciphertext), repeat=iterations, number=1)
    dec_times_ms = [t * 1000 for t in dec_times]

    return enc_times_ms, dec_times_ms

################## Execution ##################

def run_performance_test():
    file_names = ["file_8.bin", "file_64.bin", "file_512.bin", "file_4096.bin", 
                  "file_32768.bin", "file_262144.bin", "file_2097152.bin"]
    
    iterations = 100 

    print(f"{'File Name':<20} | {'Mean (ms)':<10} | {'StdDev':<10} | {'95% CI'}")
    print("-" * 75)

    for filename in file_names:
        # Get raw data from benchmark
        enc_list, dec_list = benchmark_aes(filename, iterations)
        
        if not enc_list:
            print(f"Skipping {filename}: File not found.")
            continue

        # Use utils to calculate statistics
        enc_stats = utils.calculate_statistics(enc_list)
        dec_stats = utils.calculate_statistics(dec_list)

        # Print Results
        print(f"{filename:<20} | {enc_stats['mean']:<10.4f} | {enc_stats['stdev']:<10.4f} | [{enc_stats['ci_low']:.4f}, {enc_stats['ci_high']:.4f}] (Enc)")
        print(f"{'':<20} | {dec_stats['mean']:<10.4f} | {dec_stats['stdev']:<10.4f} | [{dec_stats['ci_low']:.4f}, {dec_stats['ci_high']:.4f}] (Dec)")

def run_performance_test_random():
    sizes = [8, 64, 512, 4096, 32768, 262144, 2097152]
    iterations = 100

    print(f"{'Size (Bytes)':<15} | {'Mean (ms)':<10} | {'StdDev':<10} | {'95% CI'}")
    print("-" * 75)

    for size in sizes:
        # Get raw data
        enc_list, dec_list = benchmark_aes_random(size, iterations)
        
        # Use utils to calculate statistics
        enc_stats = utils.calculate_statistics(enc_list)
        dec_stats = utils.calculate_statistics(dec_list)

        # Print Results
        print(f"{size:<15} | {enc_stats['mean']:<10.4f} | {enc_stats['stdev']:<10.4f} | [{enc_stats['ci_low']:.4f}, {enc_stats['ci_high']:.4f}] (Enc)")
        print(f"{'':<15} | {dec_stats['mean']:<10.4f} | {dec_stats['stdev']:<10.4f} | [{dec_stats['ci_low']:.4f}, {dec_stats['ci_high']:.4f}] (Dec)")

if __name__ == "__main__":
    run_performance_test_random()