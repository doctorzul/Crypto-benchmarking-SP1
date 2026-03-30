import os
import timeit
import utils
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import matplotlib.pyplot as plot
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

# GRAPH GENERATION - (partly generated with Gemini)
def generate_plots(file_sizes, enc_avgs, enc_stds, dec_avgs, dec_stds):
    """
    @brief Generates side-by-side combined plots (Linear and Log-Log).
    """
    print("\nGenerating formatted plots...")

    # Create the 1x2 side-by-side layout
    fig, axes = plot.subplots(1, 2, figsize=(14, 6))

    # --- LEFT SIDE: Linear plot ---
    axes[0].errorbar(file_sizes, enc_avgs, yerr=enc_stds, marker='o', 
                     linestyle='-', capsize=5, label='AES Encrypt')
    axes[0].errorbar(file_sizes, dec_avgs, yerr=dec_stds, marker='s', 
                     linestyle='-', capsize=5, label='AES Decrypt')
    
    axes[0].set_title("Linear Scale")
    axes[0].set_xlabel("File Size (B)")
    axes[0].set_ylabel("Time (Milliseconds)") 
    axes[0].grid(True, ls="--", alpha=0.5)
    axes[0].legend()

    # --- RIGHT SIDE: Log plot ---
    axes[1].errorbar(file_sizes, enc_avgs, yerr=enc_stds, marker='o', 
                     linestyle='-', capsize=5, label='AES Encrypt')
    axes[1].errorbar(file_sizes, dec_avgs, yerr=dec_stds, marker='s', 
                     linestyle='-', capsize=5, label='AES Decrypt')
    
    axes[1].set_title("Log-Log Scale")
    axes[1].set_xlabel("File Size (B)")
    axes[1].set_ylabel("Time (Milliseconds)")
    axes[1].set_xscale('log') 
    axes[1].set_yscale('log')
    axes[1].grid(True, which="both", ls="--", alpha=0.5)
    axes[1].legend()

    # Apply tight layout and save/show the result
    plot.tight_layout()
    plot.savefig('aes_combined_plot_fixed.png', bbox_inches='tight', dpi=300)
    plot.show()

def run_performance_test():
    file_names = ["file_8.bin", "file_64.bin", "file_512.bin", "file_4096.bin", 
                  "file_32768.bin", "file_262144.bin", "file_2097152.bin"]
    
    file_sizes = [8, 64, 512, 4096, 32768, 262144, 2097152]
    
    iterations = 100 

    # Lists to store the final statistical data for the graphs
    all_enc_avgs, all_enc_stds = [], []
    all_dec_avgs, all_dec_stds = [], []

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

        # Append to our plotting lists
        all_enc_avgs.append(enc_stats['mean'])
        all_enc_stds.append(enc_stats['stdev'])
        all_dec_avgs.append(dec_stats['mean'])
        all_dec_stds.append(dec_stats['stdev'])

        # Print Results
        print(f"{filename:<20} | {enc_stats['mean']:<10.4f} | {enc_stats['stdev']:<10.4f} | [{enc_stats['ci_low']:.4f}, {enc_stats['ci_high']:.4f}] (Enc)")
        print(f"{'':<20} | {dec_stats['mean']:<10.4f} | {dec_stats['stdev']:<10.4f} | [{dec_stats['ci_low']:.4f}, {dec_stats['ci_high']:.4f}] (Dec)")
    
    generate_plots(file_sizes, all_enc_avgs, all_enc_stds, all_dec_avgs, all_dec_stds)

def run_performance_test_random():
    file_sizes = [8, 64, 512, 4096, 32768, 262144, 2097152]
    iterations = 100

    # Lists to store the final statistical data for the graphs
    all_enc_avgs, all_enc_stds = [], []
    all_dec_avgs, all_dec_stds = [], []    

    print(f"{'Size (Bytes)':<15} | {'Mean (ms)':<10} | {'StdDev':<10} | {'95% CI'}")
    print("-" * 75)

    for size in file_sizes:
        # Get raw data
        enc_list, dec_list = benchmark_aes_random(size, iterations)
        
        # Use utils to calculate statistics
        enc_stats = utils.calculate_statistics(enc_list)
        dec_stats = utils.calculate_statistics(dec_list)

        # Append to our plotting lists
        all_enc_avgs.append(enc_stats['mean'])
        all_enc_stds.append(enc_stats['stdev'])
        all_dec_avgs.append(dec_stats['mean'])
        all_dec_stds.append(dec_stats['stdev'])

        # Print Results
        print(f"{size:<15} | {enc_stats['mean']:<10.4f} | {enc_stats['stdev']:<10.4f} | [{enc_stats['ci_low']:.4f}, {enc_stats['ci_high']:.4f}] (Enc)")
        print(f"{'':<15} | {dec_stats['mean']:<10.4f} | {dec_stats['stdev']:<10.4f} | [{dec_stats['ci_low']:.4f}, {dec_stats['ci_high']:.4f}] (Dec)")
    
    generate_plots(file_sizes, all_enc_avgs, all_enc_stds, all_dec_avgs, all_dec_stds)

if __name__ == "__main__":
    run_performance_test()