'''

https://arxiv.org/pdf/1907.03251v3
https://prng.di.unimi.it/
https://bashtage.github.io/ng-numpy-randomstate/doc/xorshift128.html#id5
https://en.wikipedia.org/wiki/Xorshift
http://vigna.di.unimi.it/ftp/papers/xorshiftplus.pdf
https://numpy.org/doc/stable/reference/random/bit_generators/index.html

'''

import numpy as np
import os

SEED=2043379
MASK64=0xFFFFFFFFFFFFFFFF

def splitmix64(x):
    x=(x+0x9E3779B97F4A7C15)&MASK64
    z=x
    z=(z^(z>>30))*0xBF58476D1CE4E5B9&MASK64
    z=(z^(z>>27))*0x94D049BB133111EB&MASK64
    return (z^(z>>31))&MASK64

def xorshift128plus(state):
    s1=state[0]
    s0=state[1]
    state[0]=s0

    s1^=(s1<<23)&MASK64
    s1^=(s1>>17)&MASK64
    s1^=s0
    s1^=(s0>>26)&MASK64

    state[1]=s1
    return (state[1]+s0)&MASK64

def gen_bits(bits_n,seed=SEED):
    bits=np.empty(bits_n,dtype=np.uint8)

    sm_state=seed&MASK64
    s0=splitmix64(sm_state)
    sm_state=s0
    s1=splitmix64(sm_state)

    if s0==0 and s1==0:
        s1=1

    state=[s0,s1]

    for i in range(bits_n):
        x=xorshift128plus(state)
        bits[i]=(x>>63)&1

    return bits

if __name__=="__main__":
    target_bits=1_000_000
    os.makedirs("Generadores",exist_ok=True)
    bits=gen_bits(target_bits)
    packed=np.packbits(bits)
    packed.tofile(rf"Generadores\BIN_XORShif128.bin")
    print("Secuencia guardada en  : BIN_XorShift128Plus.bin")
    