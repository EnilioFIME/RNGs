'''

https://numpy.org/doc/stable/reference/random/
https://numpy.org/doc/stable/reference/random/upgrading-pcg64.html
https://numpy.org/doc/stable/reference/random/bit_generators/index.html
https://en.wikipedia.org/wiki/Permuted_congruential_generator
https://www.pcg-random.org/

'''

import numpy as np
import os
import math as mt

def gen_bits(bits_n, seed = 2043379):
    rng = np.random.Generator(np.random.PCG64(seed))   
    bytes_n = bits_n // 8    
    random_bytes = rng.bytes(bytes_n)    
    return np.unpackbits(np.frombuffer(random_bytes, dtype=np.uint8))

if __name__ == "__main__":
    target_bits = 1_000_000   
    os.makedirs("Generadores", exist_ok=True)
    bits = gen_bits(target_bits)
    packed = np.packbits(bits)
    packed.tofile(rf"Generadores\BIN_PCG64.bin")
    print("Secuencia guardada en  : BIN_PCG64.bin")