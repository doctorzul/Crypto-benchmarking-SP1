#!/usr/bin/env python3

"""
@file rsa_hybrid.py
@brief RSA-based hybrid encryption implementation for Security and Privacy course.
@details Implements a custom hybrid scheme using RSA-2048 for key encapsulation 
         and SHA-256 for data encapsulation via a stream cipher approach.
"""

import os
import math
import hashlib
import timeit
import math
from cryptography.hazmat.primitives.asymmetric import rsa

# key pair
generated_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = generated_key.public_key()

# number extraction
n = public_key.public_numbers().n # product of two primes
e = public_key.public_numbers().e # public
d = generated_key.private_numbers().d # secret key

def rsa_encrypt(m_int, e, n):
    """
    @brief Performs raw RSA encryption.
    @param m_int The plaintext message converted to an integer.
    @param e The public exponent.
    @param n The modulus.
    @return The resulting ciphertext as an integer (c = m^e mod n).
    """
    return pow(m_int, e, n)
#implement key generation, inversion, evaluation

def rsa_decrypt(c_int, d, n):
    """
    @brief Performs raw RSA decryption.
    @param c_int The ciphertext integer.
    @param d The private exponent.
    @param n The modulus.
    @return The resulting plaintext as an integer (m = c^d mod n).
    """
    return pow(c_int, d, n)


def encrypt(message_bytes, e, n):
    """
    @brief Encrypts a message using a hybrid RSA/SHA-256 scheme.
    @details Implements Enc(m; r) = (RSA(r), H(0, r) ^ m0, ..., H(n, r) ^ mn).
    @param message_bytes The raw plaintext data (bytes).
    @param e The RSA public exponent.
    @param n The RSA modulus.
    @return A byte string containing the 256-byte RSA-encrypted 'r' followed by the ciphertext blocks.
    """
    # uniform value r - 256b
    r_bytes = os.urandom(32)

    # converts r for an integer for math - one time secret session key
    r_int = int.from_bytes(r_bytes, byteorder='big')
    encrypted_r_int = rsa_encrypt(r_int, e, n)

    # convert back to bytes
    encrypted_r_bytes = encrypted_r_int.to_bytes(256, byteorder='big')

    l = 32 # Hash output size of the hash function in bytes
    message_length = len(message_bytes)
    total_blocks = math.ceil(message_length / l) # how many 32 byte chunks to split into
    
    ciphertext_blocks = []

    for block_num in range(total_blocks):
        start_index = block_num * l
        end_index = start_index + l
        m_i = message_bytes[start_index:end_index] # the current block processed

        i_bytes = block_num.to_bytes(4, byteorder='big')
        hash_input = i_bytes + r_bytes # Measure against two same plaintexts - include index

        h_out = hashlib.sha256(hash_input).digest() # unique hash for every block

        h_out_truncated = h_out[:len(m_i)]

        c_i = bytes(a ^ b for a,b in zip(h_out_truncated, m_i)) # resulting encrypted block - xoring pairs
        ciphertext_blocks.append(c_i)
    
    final_ciphertext = encrypted_r_bytes + b"".join(ciphertext_blocks) # combine to one final bytestring
    return final_ciphertext


def decrypt(message_cyphertext, d,n):
    """
    @brief Decrypts a message encrypted with the hybrid RSA/SHA-256 scheme.
    @param message_cyphertext The full ciphertext byte string (RSA(r) + data blocks).
    @param d The RSA private exponent.
    @param n The RSA modulus.
    @return The original plaintext byte string.
    """
    bytes_encrypted_r = message_cyphertext[:256] # 2048 bits
    ciphertext_message = message_cyphertext[256:]

    # RSA mathematical inversion on int
    encrypted_r = int.from_bytes(bytes_encrypted_r,byteorder='big')
    decrypted_r = rsa_decrypt(encrypted_r, d, n)
    r_bytes = decrypted_r.to_bytes(32, byteorder='big')

    l = 32 # because of sha-256
    message_len = len(ciphertext_message)
    total_blocks = math.ceil(message_len/32)

    plaintext_blocks = []

    for block_num in range(total_blocks):
        # isolate chunk
        start_index = block_num * l
        end_index = start_index + l

        c_index = ciphertext_message[start_index:end_index]
        index_bytes = block_num.to_bytes(4, byteorder='big')

        hash_input = index_bytes + r_bytes 

        h_out = hashlib.sha256(hash_input).digest()
        h_out_truncated = h_out[:len(c_index)] # trim last block if necessary

        m_i = bytes(a ^ b for a,b in zip(h_out_truncated, c_index))
        plaintext_blocks.append(m_i)
    
    final_plaintext = b"".join(plaintext_blocks)
    return final_plaintext


def benchmark_rsa(filename, repetitions):
    """
    @brief Benchmarks the encryption and decryption times for a specific file.
    @param filename The path to the file to be benchmarked.
    @param repetitions The number of times to run the benchmark for statistical significance.
    @return A tuple containing two lists - (encryption_times_us, decryption_times_us).
    """
    exec_times_encryption = []
    exec_times_decryption = []
    
    with open(filename, "rb") as f:
        plaintext = f.read()
        
    for i in range(repetitions):
        execution_time = timeit.timeit(lambda: encrypt(plaintext, e, n), number=1)
        # in microseconds 
        exec_times_encryption.append(execution_time * 1_000_000)
        
    valid_ciphertext = encrypt(plaintext, e, n)
    
   
    for i in range(repetitions):
        execution_time = timeit.timeit(lambda: decrypt(valid_ciphertext, d, n), number=1)
        exec_times_decryption.append(execution_time * 1_000_000)
        
    return exec_times_encryption, exec_times_decryption

