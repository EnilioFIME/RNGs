import numpy as np
import os

SEED=2043379

def _make_entropy_source():
    bit_gen=np.random.MT19937(SEED)
    return np.random.Generator(bit_gen)

def _bernoulli_loop(bits_n,entropy_1,entropy_2,x1_init,x2_init,mu=2.0):
    bits=np.empty(bits_n,dtype=np.uint8)
    x1=x1_init
    x2=x2_init
    jitter_1=entropy_1.uniform(-1e-10,1e-10,size=bits_n)
    jitter_2=entropy_2.uniform(-1e-10,1e-10,size=bits_n)
    for i in range(bits_n):
        x1=mu*x1 if x1<=0.5 else mu*x1-1.0
        x1=(x1+jitter_1[i])%1.0
        if x1==0.0:x1=1e-9
        x2=mu*x2 if x2<=0.5 else mu*x2-1.0
        x2=(x2+jitter_2[i])%1.0
        if x2==0.0:x2=1e-9
        bits[i]=1 if x2<x1 else 0
    return bits

def gen_bits(bits_n,seed=SEED):
    rng_1=_make_entropy_source()
    rng_2=np.random.Generator(np.random.MT19937(SEED+1))
    bits=_bernoulli_loop(bits_n,rng_1,rng_2,SEED/999999,1-SEED/999999)
    return bits

if __name__=="__main__":
    import time
    target_bits=1_000_000
    os.makedirs("Generadores",exist_ok=True)
    t0=time.perf_counter()
    bits=gen_bits(target_bits)
    packed=np.packbits(bits)
    output_path=os.path.join("Generadores","BIN_BernMapp.bin")
    packed.tofile(output_path)
    print(f"Secuencia guardada en: {output_path}")