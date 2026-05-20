'''
Generador Congruencial Multiplicativo (Multiplicative Congruential Generator)
Relación de recurrencia: Xn+1 = a * Xn mod m

Referencias:
https://en.wikipedia.org/wiki/Lehmer_random_number_generator
https://numpy.org/doc/stable/reference/random/bit_generators/index.html
'''
import numpy as np
import os

M=2**31-1
A=16807
SEED=2043379

def gen_bits(bits_n:int,seed:int=SEED)->np.ndarray:
    bits=np.empty(bits_n,dtype=np.uint8)
    x=seed
    for i in range(bits_n):
        x=(A*x)%M
        bits[i]=(x>>30)&1
    return bits

if __name__=="__main__":
    target_bits=1_000_000
    os.makedirs("Generadores",exist_ok=True)
    bits=gen_bits(target_bits)
    packed=np.packbits(bits)
    packed.tofile(rf"Generadores\BIN_CongMult.bin")
    print("Secuencia guardada en  : Generadores\BIN_CongMult.bin")