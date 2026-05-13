# Referencias
'''

Survey: 2.2.1 Logistic Mapping, Table 1
https://mikekipruto.substack.com/p/simulating-the-logistic-map-in-python
pdf gpu_nody  J. S. Teh 
https://www.geeksforgeeks.org/python/get-the-logical-xor-of-two-variables-in-python/
https://stackoverflow.com/questions/432842/how-do-you-get-the-logical-xor-of-two-variables-in-python
https://stackoverflow.com/questions/21341338/extract-lsb-bit-from-a-byte-in-python
https://stackoverflow.com/questions/32834963/most-significant-byte-calculation

'''

import numpy as np
import matplotlib.pyplot as plt
import struct
import math as mt

def logistic_mapping (x, mu):

    return mu * x * (1 - x)

def function_seed (seed):

    return seed / 9999999

def mu_change (x, mu):      # Funcion determinista reproducible

    y = 2
    tmp_list = []

    if x >= 0.5 :

        for _ in range(y): 
            x = logistic_mapping (x, mu)
        
        mu = 3.99
    
    else:

        for _ in range(y): 

            x = logistic_mapping (x, mu)
            tmp = 3.86 + (x * 0.14)
            tmp_list.append(tmp)

        mu = np.mean(tmp_list)

    return x, mu

def pointer_casting (x):

    return struct.unpack('Q', struct.pack('d', x))[0]

def unsigned_int (x1, x2):          #32 bit addition and XOR

    C1 = pointer_casting(x1)
    C2 = pointer_casting(x2)

    M1 =  C1        & 0xFFFFFFFF    #LSB C1
    M2 = (C1 >> 32) & 0xFFFFFFFF    #MSB C1
    M3 =  C2        & 0xFFFFFFFF    #LSB C2
    M4 = (C2 >> 32) & 0xFFFFFFFF    #MSB C2

    # v = ((M1 + M4) XOR M3) + M2 En 32 bits
    v = ((((M1 + M4) & 0xFFFFFFFF) ^ M3) + M2) & 0xFFFFFFFF

    return v



# Params
target_bits = 1_000_000
bits_per_val = 32

mu = 3.99                               # Parametro de crecimiento
x0 = function_seed (2043379)            # x inicial
n = mt.ceil(target_bits / bits_per_val) # Iteraciones

xtemp = x0
for _ in range (1000):

    xtemp, _ = mu_change (xtemp, mu)

x = np.zeros(n)
px = np.zeros(n, dtype=np.uint32)

x [0] = xtemp
px[0] = unsigned_int (x[0], x0)

for i in range(1,n):

    x [i], mu = mu_change (x[i - 1], mu)
    px[i] = unsigned_int  (x[i], x[i-1])

px.tofile(r"Generadores\BIN_LogiMapp.bin")
print("Secuencia guardada en  : BIN_LogiMapp.bin")
