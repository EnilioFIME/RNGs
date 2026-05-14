# Referencias
'''
https://en.wikipedia.org/wiki/Tent_map
https://gist.github.com/kindageeky/5431524
https://www.numberanalytics.com/blog/ultimate-guide-tent-map-dynamical-systems
https://hypercode.alexisbouchez.com/chaos-theory/lessons/tent-map
https://ieeexplore.ieee.org/document/6828610
https://www.geeksforgeeks.org/digital-logic/linear-feedback-shift-registers-lfsr/
https://github.com/markagold1/LFSR-LAB/blob/master/python/lfsr.py
https://stackoverflow.com/questions/33975149/linear-feedback-shift-register

'''

import numpy as np
import matplotlib.pyplot as plt
import struct
import math as mt

def _tent_mapping (x, mu):

    if x < 0.5:

        return mu * x
    
    else:

        return mu * ( 1 - x )

def _function_seed (seed):

    return seed / 9999999

def _lfsr (bits_in): 

    lfsr_State = 0b11111111

    bits_out = np.zeros(len(bits_in), dtype=np.uint8)

    for i in range(len(bits_in)):
        bit = bits_in[i]

        #8 bit LFSR corrector x7 + x3 + x2 + x1
        bit7 = (lfsr_State >> 7) & 1
        bit3 = (lfsr_State >> 3) & 1
        bit2 = (lfsr_State >> 2) & 1
        bit1 = (lfsr_State >> 1) & 1

        new_bit = bit7 ^ bit3 ^ bit2 ^ bit1
        bit_lfsr = bit7

        lfsr_State = ((lfsr_State << 1) | new_bit) & 0xFF

        bits_out[i] = bit ^ bit_lfsr

    return bits_out

'''

"If μ equals 2 ...  so the map has become chaotic."
"For the parameter value r = 2, the tent map is exactly chaotic"

'''

# Params
mu = 2                                   # Parametro de crecimiento
seed = 2043379

def gen_bits (bits_n):

    x0 = _function_seed (seed)                # x inicial
    n  = bits_n                         # Iteraciones

    x = np.zeros(n)
    px = np.zeros(n, dtype=np.uint8)

    x [ 0 ] = x0

    for i in range(1,n):

        x [ i ] = _tent_mapping (x[ i - 1 ], mu) + 1e-15 # Agregar ruido microscopido
        x [ i ] %= 1.0                                  # Aegurarnos que no se "salga" del rango
        
    bits = ( x >= 0.5 ).astype (np.uint8)
    px = _lfsr (bits)

    return px

if __name__ == "__main__":

    import os

    target_bits = 1_000_000
    
    os.makedirs("Generadores", exist_ok=True)

    bits = gen_bits (target_bits)
    packed = np.packbits(bits)

    packed.tofile(r"Generadores\BIN_TentMapp.bin")
    print("Secuencia guardada en  : BIN_TentMapp.bin")
