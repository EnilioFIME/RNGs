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

'''

import numpy as np

def xor_strings (msg: bytes, key: bytes) -> bytes:

    return bytes([a ^ b for a, b in zip (msg, key)])

def entropy (datos) -> bytes:

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

with open (r"Generadores\BIN_LogiMapp.bin"   , "rb")as f:
    keystream   = f.read()

with open (r"EntornoDeSimulacion\mensaje.txt", "rb")as f:
    message     = f.read()

cipher   = xor_strings(message, keystream)

cipher_entropy  = entropy (cipher)
message_entropy = entropy (message)

cipher_vector  = np.frombuffer(cipher , dtype= np.uint8)
message_vector = np.frombuffer(message, dtype= np.uint8)

leng = len(cipher)
clip_vector = message_vector[:leng]

correlation = np.corrcoef(clip_vector, cipher_vector) [0,1]

print ("\n======== Entropia =========================================")
print ("Entropia del Mensaje Original: \t\t", message_entropy)
print ("Entropia del Mensaje Cifrado:  \t\t", cipher_entropy)

print ("\n====== Correlacion ========================================")
print ("Correlacion del Mensaje Cifrado:  \t", correlation)

print ("\n===== Bytes Evaluados =====================================")
print ("Bytes Evaluados:  \t\t\t", leng)