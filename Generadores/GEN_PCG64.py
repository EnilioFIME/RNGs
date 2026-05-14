'''

https://numpy.org/doc/stable/reference/random/
https://numpy.org/doc/stable/reference/random/upgrading-pcg64.html
https://numpy.org/doc/stable/reference/random/bit_generators/index.html

'''

import numpy as np
import os
import math as mt

def gen_bits(bits_n):
    
    seed = 2043379

    bit_gen = np.random.PCG64(seed)
    rng = np.random.Generator(bit_gen)

    return rng.integers(0, 2, bits_n, dtype=np.uint8)

if __name__ == "__main__":

    target_bits = 1_000_000
    
    os.makedirs("Generadores", exist_ok=True)

    bits = gen_bits(target_bits)

    packed = np.packbits(bits)

    packed.tofile(r"Generadores\BIN_PCG64.bin")

    print("Secuencia guardada en  : BIN_PCG64.bin")