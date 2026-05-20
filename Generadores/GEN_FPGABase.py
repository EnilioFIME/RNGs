import numpy as np
import os

A=np.float32(2.8)
B=np.float32(0.2)
C=np.float32(1.4)
D=np.float32(1.0)
E=np.float32(10.0)
F=np.float32(2.0)

H=np.float32(0.04)
HALF=np.float32(0.5)
ONE_SIXTH=np.float32(1.0/6.0)
TWO=np.float32(2.0)

def _chaotic_system(state):
    x,y,z=state
    dx=np.float32(np.float32(A*y)-x+np.float32(z*y))
    dy=np.float32(np.float32(np.float32(-B*x)*z)-np.float32(C*x)+np.float32(y*z)+D)
    dz=np.float32(E-np.float32(np.float32(F*x)*y)-np.float32(x*x))
    return np.array([dx,dy,dz],dtype=np.float32)

def _rk4_step(state):
    k1=_chaotic_system(state)
    k2=_chaotic_system(state+np.float32(np.float32(HALF*H)*k1))
    k3=_chaotic_system(state+np.float32(np.float32(HALF*H)*k2))
    k4=_chaotic_system(state+np.float32(H*k3))

    sum_k=np.float32(k1+np.float32(TWO*k2))
    sum_k=np.float32(sum_k+np.float32(TWO*k3))
    sum_k=np.float32(sum_k+k4)

    return state+np.float32(np.float32(H*ONE_SIXTH)*sum_k)

def gen_bits(bits_n,seed=2043379):
    np.random.seed(seed)

    state=np.array([
        np.random.uniform(-0.001,0.001),
        np.random.uniform(-0.001,0.001),
        np.random.uniform(-0.001,0.001)
    ],dtype=np.float32)

    bits=np.zeros(bits_n,dtype=np.uint8)

    for i in range(bits_n):
        state=_rk4_step(state)
        bus=state.view(np.int32)
        bx=bus[0]&1
        by=bus[1]&1
        bz=bus[2]&1
        bits[i]=bx^by^bz

    return bits

if __name__=="__main__":
    target_bits=1_000_000
    os.makedirs("Generadores",exist_ok=True)
    bits=gen_bits(target_bits)
    packed=np.packbits(bits)
    output_path=rf"Generadores\BIN_FPGABase.bin"
    packed.tofile(output_path)
    print(f"Secuencia guardada en : {output_path}")