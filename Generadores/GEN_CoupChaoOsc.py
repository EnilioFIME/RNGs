import numpy as np
from numba import njit
import random
import time
import os

SEED=2043379
DT=0.02
NOISE_STD=1e-4
BASE_STEPS=10

@njit
def derivatives(x,y,z,w):
    dx=y-x
    dy=x*(2.8-z)-y
    dz=x*y-0.2*z
    dw=-w+x
    return dx,dy,dz,dw

@njit
def rk4_step(x,y,z,w,dt):
    k1_x,k1_y,k1_z,k1_w=derivatives(x,y,z,w)
    hx,hy,hz,hw=x+0.5*dt*k1_x,y+0.5*dt*k1_y,z+0.5*dt*k1_z,w+0.5*dt*k1_w
    k2_x,k2_y,k2_z,k2_w=derivatives(hx,hy,hz,hw)
    hx,hy,hz,hw=x+0.5*dt*k2_x,y+0.5*dt*k2_y,z+0.5*dt*k2_z,w+0.5*dt*k2_w
    k3_x,k3_y,k3_z,k3_w=derivatives(hx,hy,hz,hw)
    hx,hy,hz,hw=x+dt*k3_x,y+dt*k3_y,z+dt*k3_z,w+dt*k3_w
    k4_x,k4_y,k4_z,k4_w=derivatives(hx,hy,hz,hw)
    nx=x+(dt/6.0)*(k1_x+2*k2_x+2*k3_x+k4_x)
    ny=x+(dt/6.0)*(k1_y+2*k2_y+2*k3_y+k4_y)
    nz=x+(dt/6.0)*(k1_z+2*k2_z+2*k3_z+k4_z)
    nw=x+(dt/6.0)*(k1_w+2*k2_w+2*k3_w+k4_w)
    return nx,ny,nz,nw

@njit
def generate_raw_bits(target_raw,x,y,z,w):
    bits=np.empty(target_raw,dtype=np.uint8)
    for i in range(target_raw):
        modulator=abs(x+z)
        dynamic_steps=min(max(BASE_STEPS+int(modulator*3),5),30)
        for _ in range(dynamic_steps):
            x,y,z,w=rk4_step(x,y,z,w,DT)
            x+=random.gauss(0.0,NOISE_STD)
            y+=random.gauss(0.0,NOISE_STD)
            z+=random.gauss(0.0,NOISE_STD)
            w+=random.gauss(0.0,NOISE_STD)
        bit_a=1 if x>y else 0
        bit_b=1 if z>w else 0
        bits[i]=bit_a^bit_b
    return bits,x,y,z,w

@njit
def apply_von_neumann(raw_bits):
    n=len(raw_bits)//2
    output=np.empty(n,dtype=np.uint8)
    out_idx=0
    for i in range(0,n*2,2):
        b1=raw_bits[i]
        b2=raw_bits[i+1]
        if b1!=b2:
            output[out_idx]=b2
            out_idx+=1
    return output[:out_idx]

@njit
def warmup(x,y,z,w,steps,seed):
    random.seed(seed)
    np.random.seed(seed)
    for _ in range(steps):
        x,y,z,w=rk4_step(x,y,z,w,DT)
    return x,y,z,w

def gen_bits(target_bits,seed=2043379):
    clean_bits=np.empty(target_bits,dtype=np.uint8)
    filled=0
    x,y,z,w=0.1,0.1,0.1,0.1
    x,y,z,w=warmup(x,y,z,w,2000,seed)
    while filled<target_bits:
        needed=target_bits-filled
        raw_needed=needed*5
        raw,x,y,z,w=generate_raw_bits(raw_needed,x,y,z,w)
        extracted=apply_von_neumann(raw)
        take=min(len(extracted),needed)
        clean_bits[filled:filled+take]=extracted[:take]
        filled+=take
    return clean_bits

if __name__=="__main__":
    target_bits=1_000_000
    os.makedirs("Generadores",exist_ok=True)
    bits=gen_bits(target_bits)
    packed=np.packbits(bits)
    output_path=os.path.join("Generadores","BIN_CoupChaoOsc.bin")
    packed.tofile(output_path)
    print(f"Guardado en: {output_path}")