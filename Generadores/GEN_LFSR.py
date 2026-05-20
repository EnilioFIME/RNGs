'''

https://github.com/ArminZahedani/LFSR/blob/master/LFSR.py
https://github.com/Vikasar24/Pseudo-Random-Bit-Generator-using-LFSR/blob/main/README.md
https://www.analog.com/en/resources/design-notes/random-number-generation-using-lfsr.html
S. Hussain, A. K. Chaudhary and S. Verma, "Design of Secured Lightweight PRNG Circuit using LFSR for Portable IoT Devices," 2022 Third International Conference on Intelligent Computing Instrumentation and Control Technologies (ICICICT), Kannur, India, 2022, pp. 1588-1592, doi: 10.1109/ICICICT54557.2022.9917644. keywords: {Power demand;Linear feedback shift registers;Instruments;Generators;Complexity theory;Cryptography;Internet of Things;LFSR;PRNG;Inequality;Comparator;Cryptography},    

'''

import numpy as np
import os

def gen_bits(bits_n,seed=2043379):
    taps=[24,23,22,17]
    state=[(seed>>i)&1 for i in range(23,-1,-1)]
    bits=np.zeros(bits_n,dtype=np.uint8)

    for i in range(bits_n):
        bits[i]=state[-1]
        feedback=0
        for t in taps:
            feedback^=state[t-1]
        state=[feedback]+state[:-1]

    return bits

if __name__=="__main__":
    target_bits=1_000_000
    os.makedirs("Generadores",exist_ok=True)
    bits=gen_bits(target_bits)
    packed=np.packbits(bits)
    output_path=rf"Generadores\BIN_LFSR.bin"
    packed.tofile(output_path)
    print(f"Secuencia LFSR guardada en: {output_path}")