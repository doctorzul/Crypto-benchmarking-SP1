#!/usr/bin/env python3

import hashlib
import timeit
import math
import utils
import os
import math
from cryptography.hazmat.primitives.asymmetric import rsa
import matplotlib.pyplot as plot

R_LENGTH_BITS = 256

# key pair
generated_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = generated_key.public_key()

# number extraction
d = generated_key.private_numbers().d # secret key
n = public_key.public_numbers().n # product of two primes
e = public_key.public_numbers().e # public

def rsa_encrypt(m_int, e, n):
    """
    @brief Performs raw RSA encryption.
    """
    return pow(m_int, e, n)
#implement key generation, inversion, evaluation

def rsa_decrypt(c_int, d, n):
    """
    @brief Performs raw RSA decryption.
    """
    return pow(c_int, d, n)


def encrypt(message_bytes, e, n):
    """
    @brief Encrypts a message using a hybrid RSA/SHA-256 scheme.
    """
    # uniform value r, 256b
    r_bytes = os.urandom(32)

    # converts r for an integer for math - one time secret session key
    r_int = int.from_bytes(r_bytes, 'big')
    encrypted_r_int = rsa_encrypt(r_int, e, n)

    # convert back to bytes
    encrypted_r_bytes = encrypted_r_int.to_bytes(R_LENGTH_BITS, 'big')

    ciphertext_blocks = []
    l = 32 # Hash output size of the hash function in bytes
    message_len = len(message_bytes)
    total_blocks = math.ceil(message_len / l) # how many 32 byte chunks to split into
    
    # for every block
    for block_i in range(total_blocks):
        start_i = block_i * l
        end_i = start_i + l
        m_i = message_bytes[start_i:end_i] # the current block processed

        block_num_bytes = block_i.to_bytes(4, byteorder='big')
        hash_input = block_num_bytes + r_bytes # To measure against two same plaintexts - include index

        keystream_block = hashlib.sha256(hash_input).digest() # unique hash for every block

        hash_out_truncated = keystream_block[:len(m_i)]

        xor_result = []
        for byte_i in range(len(m_i)):
            keystream_b = hash_out_truncated[byte_i]
            message_b = m_i[byte_i]
            encrypted_b = keystream_b ^ message_b
            xor_result.append(encrypted_b)
        c_i = bytes(xor_result) 
        
        ciphertext_blocks.append(c_i)
    
    final_ciphertext = encrypted_r_bytes + b"".join(ciphertext_blocks) # combine to one final bytestring
    return final_ciphertext


def decrypt(message_cyphertext, d,n):
    """
    @brief Decrypts a message encrypted with the hybrid RSA/SHA-256 scheme.
    """
    bytes_encrypted_r = message_cyphertext[0:256] # 2048 bits
    ciphertext_message = message_cyphertext[256:]

    # RSA mathematical inversion on int
    encrypted_r = int.from_bytes(bytes_encrypted_r,byteorder='big')
    decrypted_r = rsa_decrypt(encrypted_r, d, n)
    r_bytes = decrypted_r.to_bytes(32, byteorder='big')

    l = 32 # because of sha-256 (32*8 = 256)
    plaintext_blocks = []
    message_len = len(ciphertext_message)
    total_blocks = math.ceil(message_len/32)

    for block_num in range(total_blocks):
        # isolate chunk
        start_index = block_num * l
        end_index = l + start_index

        c_index = ciphertext_message[start_index:end_index]
        index_bytes = block_num.to_bytes(4, 'big')

        hash_input = index_bytes + r_bytes 

        keystream_block = hashlib.sha256(hash_input).digest()

        # trim to match block size (mainlz for last block)
        keystream = keystream_block[:len(c_index)]

        # XOR to get back plaintext block
        xor_result = []
        #
        for byte_i in range(len(c_index)):
            keystream_b = keystream[byte_i]
            ciphertext_b = c_index[byte_i]
            decrypted_b = keystream_b ^ ciphertext_b
            xor_result.append(decrypted_b)
        plaintext_block = bytes(xor_result)
        plaintext_blocks.append(plaintext_block)
            
    final_plaintext = b"".join(plaintext_blocks)
    return final_plaintext

# --- Benchmarking & Plotting ---
def benchmark_rsa(filename, repetitions):
    """
    @brief Benchmarks the encryption and decryption times for a specific file.
    """
    if not os.path.exists(filename):
        return [], []

    with open(filename, "rb") as f:
        plaintext = f.read()

    # Measure encryption time in micro seconds (number=1: independent samples)
    enc_times = timeit.repeat(lambda: encrypt(plaintext, e, n), repeat=repetitions, number=1)
    exec_times_encryption = [t * 1000 * 1000 for t in enc_times]
        
    valid_ciphertext = encrypt(plaintext, e, n)
    
    # Measure decryption time
    dec_times = timeit.repeat(lambda: decrypt(valid_ciphertext, d, n), repeat=repetitions, number=1)
    exec_times_decryption = [t * 1000 * 1000 for t in dec_times]
        
    return exec_times_encryption, exec_times_decryption

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
                     linestyle='-', capsize=5, label='RSA Encrypt')
    axes[0].errorbar(file_sizes, dec_avgs, yerr=dec_stds, marker='s', 
                     linestyle='-', capsize=5, label='RSA Decrypt')
    
    axes[0].set_title("Linear Scale")
    axes[0].set_xlabel("File Size (B)")
    axes[0].set_ylabel("Time (Microseconds)") 
    axes[0].grid(True, ls="--", alpha=0.5)
    axes[0].legend()

    # --- RIGHT SIDE: Log plot ---
    axes[1].errorbar(file_sizes, enc_avgs, yerr=enc_stds, marker='o', 
                     linestyle='-', capsize=5, label='RSA Encrypt')
    axes[1].errorbar(file_sizes, dec_avgs, yerr=dec_stds, marker='s', 
                     linestyle='-', capsize=5, label='RSA Decrypt')
    
    axes[1].set_title("Log-Log Scale")
    axes[1].set_xlabel("File Size (B)")
    axes[1].set_ylabel("Time (Microseconds)")
    axes[1].set_xscale('log') 
    axes[1].set_yscale('log')
    axes[1].grid(True, which="both", ls="--", alpha=0.5)
    axes[1].legend()

    # Apply tight layout and save/show the result
    plot.tight_layout()
    plot.savefig('rsa_public_combined_plot.png', bbox_inches='tight', dpi=300)
    plot.show()

    
def run_performance_test():
    """
    @brief Prepares the performance benchmarking for RSA hybrid encryption.
    """
    file_names = ["file_8.bin", "file_64.bin", "file_512.bin", "file_4096.bin", 
                  "file_32768.bin", "file_262144.bin", "file_2097152.bin"]
    file_sizes = [8, 64, 512, 4096, 32768, 262144, 2097152]
    
    iterations = 100 

    # Lists to store the final statistical data for the graphs
    all_enc_avgs, all_enc_stds = [], []
    all_dec_avgs, all_dec_stds = [], []

    # Header 
    print(f"{'File Name':<20} | {'Mean (μs)':<12} | {'StdDev':<10} | {'95% CI'}")
    print("-" * 75)

    for filename in file_names:
        enc_list, dec_list = benchmark_rsa(filename, iterations)
        
        if not enc_list:
            print(f"Skipping {filename}: File not found.")
            # Pad lists with zeros so the graph doesn't crash if a file is missing
            all_enc_avgs.append(0); all_enc_stds.append(0)
            all_dec_avgs.append(0); all_dec_stds.append(0)
            continue

        # Process the raw data using the shared utils module
        enc_stats = utils.calculate_statistics(enc_list)
        dec_stats = utils.calculate_statistics(dec_list)

        # Append to our plotting lists
        all_enc_avgs.append(enc_stats['mean'])
        all_enc_stds.append(enc_stats['stdev'])
        all_dec_avgs.append(dec_stats['mean'])
        all_dec_stds.append(dec_stats['stdev'])

        # Output formatted statistical results
        print(f"{filename:<20} | {enc_stats['mean']:<12.4f} | {enc_stats['stdev']:<10.4f} | [{enc_stats['ci_low']:.4f}, {enc_stats['ci_high']:.4f}] (Enc)")
        print(f"{'':<20} | {dec_stats['mean']:<12.4f} | {dec_stats['stdev']:<10.4f} | [{dec_stats['ci_low']:.4f}, {dec_stats['ci_high']:.4f}] (Dec)")
        
    # Trigger the plot generation using the collected data
    generate_plots(file_sizes, all_enc_avgs, all_enc_stds, all_dec_avgs, all_dec_stds)

if __name__ == "__main__":
    run_performance_test()

# End of file: rsa_crypto.py