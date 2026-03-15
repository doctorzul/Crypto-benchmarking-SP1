import os
import timeit
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

def run_performance_test():
    file_sizes = [8, 64, 512, 4096, 32768, 262144, 2097152]
    # 256 bites key
    key = os.urandom(32)

    print(f"{'File Name':<20} | {'Encryption Time (ms)':<15} | {'Decryption Time (ms)':<15}")
    print("-" * 55)

    for size in file_sizes:
        filename = f"file_{size}.bin"

        with open(filename, "rb") as f:
            data = f.read()

        iterations = 1000
        
        # Measure Encryption
        t_enc = timeit.timeit(lambda: encrypt_ctr(key, data), number=iterations) / iterations
        
        # Prepare for Decryption measurement
        nonce, ciphertext = encrypt_ctr(key, data)
        
        # Measure Decryption
        t_dec = timeit.timeit(lambda: decrypt_ctr(key, nonce, ciphertext), number=iterations) / iterations

        print(f"{filename:<20} | {t_enc*1000:<15.6f} | {t_dec*1000:<15.6f}")

if __name__ == "__main__":
    run_performance_test()