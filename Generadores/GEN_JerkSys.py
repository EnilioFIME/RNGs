import numpy as np
import time
import os

SEED=2043379
NOISE_STD=np.float32(1e-4)
DITHER_STD=np.float32(1e-3)
H=np.float32(0.001)
OVERSAMPLING=3

A=np.float32(0.5)
B=np.float32(1.0)
B1=np.float32(500.0)
B2=np.float32(15.0)
C=np.float32(0.9)

V_RAIL=np.float32(2.5)
SCRAMBLE_RATIO=np.float32(0.15)

def gen_bits(target_bits,seed=2043379):
    rng=np.random.default_rng(seed)
    bits=np.empty(target_bits,dtype=np.uint8)

    x=np.float32(0.1)
    y=np.float32(0.0)
    z=np.float32(0.0)

    int1=np.float32(0.0)
    int2=np.float32(0.0)

    collected=0

    while collected<target_bits:
        for _ in range(OVERSAMPLING):
            n0,n1,n2=rng.normal(0,NOISE_STD,3).astype(np.float32)

            dx=y+n0
            dy=z+n1

            nonlinear=B*(np.tanh(B1*x)*B2-C)

            dz=-A*z-y+nonlinear+n2

            x+=H*dx
            y+=H*dy
            z+=H*dz

            x=np.clip(x,-V_RAIL,V_RAIL)
            y=np.clip(y,-V_RAIL,V_RAIL)
            z=np.clip(z,-V_RAIL,V_RAIL)

        analog_mix=(x+y-z)*SCRAMBLE_RATIO
        dither=rng.normal(0,DITHER_STD)

        bit=1 if (int2+dither)>=0 else 0
        dac=1.0 if bit else -1.0

        int1_prev=int1
        int1+=analog_mix-dac
        int2+=int1_prev-dac

        bits[collected]=bit
        collected+=1

    return bits

if __name__=="__main__":
    bits=gen_bits(1_000_000)
    packed=np.packbits(bits)
    output_path=os.path.join("Generadores","BIN_JerkSys.bin")
    packed.tofile(output_path)
    print(f"Secuencia guardada en: {output_path}")