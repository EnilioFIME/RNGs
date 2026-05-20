'''

https://numpy.org/doc/stable/reference/random/generated/numpy.random.randint.html
https://numpy.org/doc/stable/reference/random/bit_generators/index.html
https://numpy.org/doc/stable/reference/random/legacy.html
https://numpy.org/doc/stable/reference/random/bit_generators/mt19937.html#numpy.random.MT19937
https://en.wikipedia.org/wiki/Mersenne_Twister

'''

import numpy as np
import os
import math as mt

def gen_bits(bits_n, seed = 2043379):
    bit_gen = np.random.MT19937(seed)
    rng = np.random.Generator(bit_gen)
    bytes_n = bits_n // 8
    random_bytes = rng.bytes(bytes_n)
    return np.unpackbits(np.frombuffer(random_bytes, dtype=np.uint8))

if __name__ == "__main__":
    target_bits = 1_000_000
    os.makedirs("Generadores", exist_ok=True)
    bits = gen_bits(target_bits)
    packed = np.packbits(bits)
    packed.tofile(r"Generadores\BIN_MersTwis.bin")
    print("Secuencia guardada en  : BIN_MersTwis.bin")