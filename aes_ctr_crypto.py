import os
import timeit
import utils
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import matplotlib.pyplot as plot

# AI was used to better format the comments according to Google Style Docstring. All has been proofread.

def encrypt_ctr(key, plaintext):
    """Encrypts plaintext using AES in Counter mode. Adapted from the crytography library

    Args:
        key (bytes): The 256-bit AES key
        plaintext (bytes): The data to be encrypted

    Returns:
        tuple: A tuple containing the 16-byte nonce and the ciphertext
    """
    nonce = os.urandom(16)
    encryptor = Cipher(
        algorithms.AES(key),
        modes.CTR(nonce),
    ).encryptor()
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    return (nonce, ciphertext)

def decrypt_ctr(key, nonce, ciphertext):
    """Decrypts AES-CTR ciphertext. Adapted from the crytography library

    Args:
        key (bytes): The 256-bit AES key
        nonce (bytes): The 16-byte initial counter value used during encryption
        ciphertext (bytes): The encrypted data

    Returns:
        bytes: The decrypted plaintext
    """
    decryptor = Cipher(
        algorithms.AES(key),
        modes.CTR(nonce),
    ).decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()

################## Benchmarking ##################

def benchmark_aes(filename, iterations=100):
    """Measures encryption and decryption performance for the specific files generated previously

    Args:
        filename (str): Path to the binary file to read
        iterations (int): Number of independent timing repetitions

    Returns:
        tuple: Two lists containing encryption and decryption times in milliseconds
    """
    if not os.path.exists(filename):
        return [], []
    with open(filename, "rb") as f:
        data = f.read()
    key = os.urandom(32)
    enc_times = timeit.repeat(lambda: encrypt_ctr(key, data), repeat=iterations, number=1)
    enc_times_ms = [t * 1000 for t in enc_times]
    nonce, ciphertext = encrypt_ctr(key, data)
    dec_times = timeit.repeat(lambda: decrypt_ctr(key, nonce, ciphertext), repeat=iterations, number=1)
    dec_times_ms = [t * 1000 for t in dec_times]
    return enc_times_ms, dec_times_ms

def benchmark_aes_random(size, iterations=100):
    """Measures performance using randomly generated data

    Args:
        size (int): Number of bytes to generate for the test
        iterations (int): Number of independent timing repetitions

    Returns:
        tuple: Two lists containing encryption and decryption times in milliseconds
    """
    data = os.urandom(size)
    key = os.urandom(32)
    enc_times = timeit.repeat(lambda: encrypt_ctr(key, data), repeat=iterations, number=1)
    enc_times_ms = [t * 1000 for t in enc_times]
    nonce, ciphertext = encrypt_ctr(key, data)
    dec_times = timeit.repeat(lambda: decrypt_ctr(key, nonce, ciphertext), repeat=iterations, number=1)
    dec_times_ms = [t * 1000 for t in dec_times]
    return enc_times_ms, dec_times_ms

################## Execution ##################

# GRAPH GENERATION - (partly generated with Gemini)

def generate_plots(file_sizes, enc_avgs, enc_stds, dec_avgs, dec_stds):
    """Visualizes performance results using Linear and Log-Log scale plots

    Args:
        file_sizes (list): List of tested data sizes in bytes
        enc_avgs (list): Mean encryption times
        enc_stds (list): Standard deviation of encryption times
        dec_avgs (list): Mean decryption times
        dec_stds (list): Standard deviation of decryption times
    """
    fig, axes = plot.subplots(1, 2, figsize=(14, 6))
    axes[0].errorbar(file_sizes, enc_avgs, yerr=enc_stds, marker='o', linestyle='-', capsize=5, label='AES Encrypt')
    axes[0].errorbar(file_sizes, dec_avgs, yerr=dec_stds, marker='s', linestyle='-', capsize=5, label='AES Decrypt')
    axes[0].set_title("Linear Scale")
    axes[0].set_xlabel("File Size (B)")
    axes[0].set_ylabel("Time (Milliseconds)")
    axes[0].grid(True, ls="--", alpha=0.5)
    axes[0].legend()
    axes[1].errorbar(file_sizes, enc_avgs, yerr=enc_stds, marker='o', linestyle='-', capsize=5, label='AES Encrypt')
    axes[1].errorbar(file_sizes, dec_avgs, yerr=dec_stds, marker='s', linestyle='-', capsize=5, label='AES Decrypt')
    axes[1].set_title("Log-Log Scale")
    axes[1].set_xlabel("File Size (B)")
    axes[1].set_ylabel("Time (Milliseconds)")
    axes[1].set_xscale('log')
    axes[1].set_yscale('log')
    axes[1].grid(True, which="both", ls="--", alpha=0.5)
    axes[1].legend()
    plot.tight_layout()
    plot.savefig('aes_combined_plot_fixed.png', bbox_inches='tight', dpi=300) # Rename graph for every rerun
    plot.show()

def run_performance_test():
    """Executes the benchmark on previously generated files and provides statistical reports/plots
    """
    file_names = ["file_8.bin", "file_64.bin", "file_512.bin", "file_4096.bin", 
                  "file_32768.bin", "file_262144.bin", "file_2097152.bin"]
    file_sizes = [8, 64, 512, 4096, 32768, 262144, 2097152]
    iterations = 100 
    all_enc_avgs, all_enc_stds = [], []
    all_dec_avgs, all_dec_stds = [], []

    print(f"{'File Name':<20} | {'Mean (ms)':<10} | {'StdDev':<10} | {'95% CI'}")
    print("-" * 75)

    for filename in file_names:
        enc_list, dec_list = benchmark_aes(filename, iterations)
        if not enc_list:
            print(f"Skipping {filename}: File not found.")
            continue
        enc_stats = utils.calculate_statistics(enc_list)
        dec_stats = utils.calculate_statistics(dec_list)
        all_enc_avgs.append(enc_stats['mean'])
        all_enc_stds.append(enc_stats['stdev'])
        all_dec_avgs.append(dec_stats['mean'])
        all_dec_stds.append(dec_stats['stdev'])

        print(f"{filename:<20} | {enc_stats['mean']:<10.4f} | {enc_stats['stdev']:<10.4f} | [{enc_stats['ci_low']:.4f}, {enc_stats['ci_high']:.4f}] (Enc)")
        print(f"{'':<20} | {dec_stats['mean']:<10.4f} | {dec_stats['stdev']:<10.4f} | [{dec_stats['ci_low']:.4f}, {dec_stats['ci_high']:.4f}] (Dec)")

    generate_plots(file_sizes, all_enc_avgs, all_enc_stds, all_dec_avgs, all_dec_stds)

def run_performance_test_random():
    """Executes the benchmark on random data and generates statistical reports/plots
    """
    file_sizes = [8, 64, 512, 4096, 32768, 262144, 2097152]
    iterations = 100
    all_enc_avgs, all_enc_stds = [], []
    all_dec_avgs, all_dec_stds = [], []    

    print(f"{'Size (Bytes)':<15} | {'Mean (ms)':<10} | {'StdDev':<10} | {'95% CI'}")
    print("-" * 75)

    for size in file_sizes:
        enc_list, dec_list = benchmark_aes_random(size, iterations)
        enc_stats = utils.calculate_statistics(enc_list)
        dec_stats = utils.calculate_statistics(dec_list)
        all_enc_avgs.append(enc_stats['mean'])
        all_enc_stds.append(enc_stats['stdev'])
        all_dec_avgs.append(dec_stats['mean'])
        all_dec_stds.append(dec_stats['stdev'])

        print(f"{size:<15} | {enc_stats['mean']:<10.4f} | {enc_stats['stdev']:<10.4f} | [{enc_stats['ci_low']:.4f}, {enc_stats['ci_high']:.4f}] (Enc)")
        print(f"{'':<15} | {dec_stats['mean']:<10.4f} | {dec_stats['stdev']:<10.4f} | [{dec_stats['ci_low']:.4f}, {dec_stats['ci_high']:.4f}] (Dec)")

    generate_plots(file_sizes, all_enc_avgs, all_enc_stds, all_dec_avgs, all_dec_stds)

if __name__ == "__main__":
    run_performance_test() # Alternate between run_performance_test() and run_performance_test_random()