import numpy as np
import os
import time
import random
from numba import njit

SEED=2043379
DT=0.01
STEPS_PER_BIT=10
NOISE_STD=1e-5

@njit(fastmath=True)
def _f_i(u):
    return 5.0*(abs(u+0.11)-abs(u+0.09)+abs(u-0.09)-abs(u-0.11))

@njit(fastmath=True)
def _f_4(w):
    return 1.25*(abs(w+0.11)-abs(w+0.09)+abs(w-0.09)-abs(w-0.11))

@njit(fastmath=True)
def _rk4_step(x,y,z,w,dt,noise_std):
    dx1=2.0*(w-_f_4(w))
    dy1=1.0*w+1.0*(x-_f_i(x))
    dz1=1.5*w-1.0*(z-_f_i(z))
    dw1=-1.0*w-1.0*(y-_f_i(y))

    x2,y2,z2,w2=x+0.5*dt*dx1,y+0.5*dt*dy1,z+0.5*dt*dz1,w+0.5*dt*dw1
    dx2=2.0*(w2-_f_4(w2))
    dy2=1.0*w2+1.0*(x2-_f_i(x2))
    dz2=1.5*w2-1.0*(z2-_f_i(z2))
    dw2=-1.0*w2-1.0*(y2-_f_i(y2))

    x3,y3,z3,w3=x+0.5*dt*dx2,y+0.5*dt*dy2,z+0.5*dt*dz2,w+0.5*dt*dw2
    dx3=2.0*(w3-_f_4(w3))
    dy3=1.0*w3+1.0*(x3-_f_i(x3))
    dz3=1.5*w3-1.0*(z3-_f_i(z3))
    dw3=-1.0*w3-1.0*(y3-_f_i(y3))

    x4,y4,z4,w4=x+dt*dx3,y+dt*dy3,z+dt*dz3,w+dt*dw3
    dx4=2.0*(w4-_f_4(w4))
    dy4=1.0*w4+1.0*(x4-_f_i(x4))
    dz4=1.5*w4-1.0*(z4-_f_i(z4))
    dw4=-1.0*w4-1.0*(y4-_f_i(y4))

    nx=x+(dt/6.0)*(dx1+2*dx2+2*dx3+dx4)+random.uniform(-noise_std,noise_std)
    ny=y+(dt/6.0)*(dy1+2*dy2+2*dy3+dy4)+random.uniform(-noise_std,noise_std)
    nz=z+(dt/6.0)*(dz1+2*dz2+2*dz3+dz4)+random.uniform(-noise_std,noise_std)
    nw=w+(dt/6.0)*(dw1+2*dw2+2*dw3+dw4)+random.uniform(-noise_std,noise_std)

    return nx,ny,nz,nw

@njit(fastmath=True)
def gen_bits(target_bits,seed=2043379):
    random.seed(seed)
    x=y=z=w=0.01
    bits=np.empty(target_bits,dtype=np.uint8)

    for _ in range(500):
        x,y,z,w=_rk4_step(x,y,z,w,DT,NOISE_STD)

    for i in range(target_bits):
        for _ in range(STEPS_PER_BIT):
            x,y,z,w=_rk4_step(x,y,z,w,DT,NOISE_STD)
        bits[i]=1 if (x>y)^(z>w) else 0

    return bits

if __name__=="__main__":
    target_bits=1_000_000
    os.makedirs("Generadores",exist_ok=True)
    bits=gen_bits(target_bits)
    packed=np.packbits(bits)
    output_path=os.path.join("Generadores","BIN_CurrModeChao.bin")
    packed.tofile(output_path)
    print(f"Secuencia cruda guardada en: {output_path}")