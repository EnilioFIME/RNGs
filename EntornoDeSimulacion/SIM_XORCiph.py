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
import csv

bitstream = "BIN_TentMapp"

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

with open (rf"Generadores\{bitstream}.bin"   , "rb")as f:
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

results = {

    "Entropia Original" : message_entropy,
    "Entropoia Cifrado" : cipher_entropy,
    "Correlacion": correlation,
    "Bytes Evaluados" : leng

}

print ("\n" + "=" * 40)
for text, value in results.items():

    print (f"{text:25}: {value}")
print ("=" * 40)

route = f"EntornoDeSimulacion\RES_SIM_XORCiph_{bitstream}.csv"

with open(route, "w", newline="", encoding="utf-8") as file:
    f = csv.writer(file)

    f.writerow(["Metrica", "Valor"])

    for text, value in results.items():

        f.writerow([text, value])
        
print(f"CSV GUARDADO EN: {route} ")