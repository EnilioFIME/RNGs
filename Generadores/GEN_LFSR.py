'''

https://github.com/ArminZahedani/LFSR/blob/master/LFSR.py

'''

import numpy as np
import os

def gen_bits(bits_n):
    
    seed = 2043379

    taps = [24, 23, 22, 17]
    
    state = [(seed >> i) & 1 for i in range(23, -1, -1)]
    
    bits = np.zeros(bits_n, dtype=np.uint8)

    for i in range(bits_n):
        output_bit = state[-1]
        bits[i] = output_bit
        
        feedback = 0
        for tap in taps:
            feedback ^= state[tap - 1]
            
        state = [feedback] + state[:-1]
        
    return bits

if __name__ == "__main__":
    target_bits = 1_000_000
    
    os.makedirs("Generadores", exist_ok=True)

    bits = gen_bits(target_bits)

    packed = np.packbits(bits)

    output_path = r"Generadores\BIN_LFSR.bin"
    packed.tofile(output_path)

    print(f"Secuencia LFSR guardada en: {output_path}")
