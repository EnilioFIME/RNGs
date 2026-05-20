import numpy as np
import os

C1=1.4
C2=1.2
V_MIN=0.0
V_MAX=4.2

def _make_entropy_source(seed):
    return np.random.Generator(np.random.MT19937(None))

def _threshold_circuit(x_t,c1,c2):
    x1=np.where(x_t<=c1,1,0).astype(np.uint8)
    x2=np.where(x_t<=c2,1,0).astype(np.uint8)
    return x1,x2

def _bit_generator(x1,x2):
    rising_edges=np.where((x1[:-1]==0)&(x1[1:]==1))[0]+1
    bits=x2[rising_edges]
    return bits

def gen_bits(target_bits,seed=2043379):
    rng=_make_entropy_source(seed)
    bits_collected=[]
    total=0
    batch_size=target_bits*10
    while total<target_bits:
        x_t=rng.uniform(V_MIN,V_MAX,size=batch_size)
        x1,x2=_threshold_circuit(x_t,C1,C2)
        new_bits=_bit_generator(x1,x2)
        bits_collected.append(new_bits)
        total+=len(new_bits)
    all_bits=np.concatenate(bits_collected)[:target_bits]
    return all_bits.astype(np.uint8)

if __name__=="__main__":
    import time
    target_bits=1_000_000
    os.makedirs("Generadores",exist_ok=True)
    bits=gen_bits(target_bits)
    packed=np.packbits(bits)
    output_path=os.path.join("Generadores","BIN_BoolChaoOsc.bin")
    packed.tofile(output_path)
    print(f"Secuencia guardada en: {output_path}")