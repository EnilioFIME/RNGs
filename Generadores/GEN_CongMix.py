'''
https://stackoverflow.com/questions/19140589/linear-congruential-generator-in-python
https://www.quantstart.com/articles/linear-congruential-generators-in-python/
'''

'''
Generador Congruencial Mixto (Linear Congruential Generator - Mixed)
Relación de recurrencia: Xn+1 = (a * Xn + c) mod m

Referencias:
https://en.wikipedia.org/wiki/Linear_congruential_generator
https://numpy.org/doc/stable/reference/random/bit_generators/index.html

Parámetros seleccionados (sistema binario, m = 2^31):
m=2**31
a=1664525
c=1013904223
SEED=2043379

Período: completo (= m = 2^31)
'''
import numpy as np
import os

M=2**31
A=1664525
C=1013904223
SEED=2043379

def gen_bits(bits_n:int,seed:int=SEED)->np.ndarray:
    bits=np.empty(bits_n,dtype=np.uint8)
    x=seed
    for i in range(bits_n):
        x=(A*x+C)%M
        bits[i]=(x>>30)&1
    return bits

if __name__=="__main__":
    target_bits=1_000_000
    os.makedirs("Generadores",exist_ok=True)
    bits=gen_bits(target_bits)
    packed=np.packbits(bits)
    packed.tofile(rf"Generadores\BIN_CongMix.bin")
    print("Secuencia guardada en  : BIN_CongMix.bin")