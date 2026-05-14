'''

https://www.tutorialspoint.com/cryptography_with_python/cryptography_with_python_xor_process.htm
https://en.wikipedia.org/wiki/XOR_cipher
https://www.geeksforgeeks.org/dsa/xor-cipher/
https://stackoverflow.com/questions/20557999/xor-python-text-encryption-decryption
https://www.geeksforgeeks.org/machine-learning/entropy-in-information-theory/
https://stackoverflow.com/questions/15450192/fastest-way-to-compute-entropy-in-python
https://thehardcorecoder.com/2021/12/21/calculating-entropy-in-python/
https://www.geeksforgeeks.org/maths/pearson-correlation-coefficient/
https://numpy.org/doc/stable/reference/generated/numpy.corrcoef.html
https://www.tecnoloblog.com/que-es-la-entropia-de-shannon/
https://numpy.org/doc/stable/reference/generated/numpy.corrcoef.html
https://docs.python.org/3/library/zlib.html

'''

import numpy as np
import csv
import zlib
from scipy.stats import chisquare

bitstream = "BIN_LogiMapp"

def xor_strings(msg: bytes, key: bytes) -> bytes:
    return bytes([a ^ b for a, b in zip(msg, key)])

def entropy(datos) -> float:
    if not datos:
        return 0.0
    
    leng = len(datos)
    freq = [0] * 256

    for byte in datos:
        freq[byte] += 1

    entropia = 0.0

    for count in freq:
        if count > 0:
            P = count / leng
            entropia += - P * np.log2(P)

    return entropia

def simular_compresion(ciphertext: bytes) -> float:
    compressed = zlib.compress(ciphertext)
    return len(compressed) / len(ciphertext)

def simular_autocorrelacion(cipher_vec: np.ndarray) -> float:
    if len(cipher_vec) < 2:
        return 0.0
    
    corr = np.corrcoef(cipher_vec[:-1], cipher_vec[1:])[0, 1]
    
    if np.isnan(corr):
        return 0.0
        
    return float(corr)

def simular_chi_cuadrado(cipher_vec: np.ndarray) -> float:
    freqs, _ = np.histogram(cipher_vec, bins=256, range=(0, 256))
    expected = np.ones(256) * (len(cipher_vec) / 256.0)
    
    _, p_val = chisquare(f_obs=freqs, f_exp=expected)
    
    return float(p_val)


with open(rf"Generadores\{bitstream}.bin", "rb") as f:
    keystream = f.read()

with open(r"Simulacion\mensaje.txt", "rb") as f:
    message = f.read()

cipher = xor_strings(message, keystream)

cipher_entropy = entropy(cipher)
message_entropy = entropy(message)

cipher_vector = np.frombuffer(cipher, dtype=np.uint8)
message_vector = np.frombuffer(message, dtype=np.uint8)

leng = len(cipher)
clip_vector = message_vector[:leng]

correlation = np.corrcoef(clip_vector, cipher_vector)[0, 1]

ratio_compresion = simular_compresion(cipher)
autocorr_cifrado = simular_autocorrelacion(cipher_vector)
chi_p_val = simular_chi_cuadrado(cipher_vector)

results = {
    "Entropia Original bits/byte": message_entropy,
    "Entropoia Cifrado bits/byte": cipher_entropy,
    "Redundancia bits/byte": 8 - cipher_entropy,
    "Correlacion": correlation,
    "Bytes Evaluados n": leng,
    "Ratio Compresion ZLIB": ratio_compresion,
    "Autocorrelacion (d=1)": autocorr_cifrado,
    "Chi-Cuadrado P-Value": chi_p_val
}

for k, v in results.items():
    print(f"{k:<30}: {v}")
print ("=" * 40)

route = rf"Simulacion\RES_SIM_XORCiph_{bitstream}.csv"

with open(route, "w", newline="", encoding="utf-8") as file:
    f = csv.writer(file)

    f.writerow(["Metrica", "Valor"])

    for text, value in results.items():

        f.writerow([text, value])
        
print(f"CSV GUARDADO EN: {route} ")