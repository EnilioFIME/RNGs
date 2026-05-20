'''
PDF CHUAS A new Chua’s circuit with monolithic Chua’s diode and its -- Moqadasi, H_; Ghaznavi-Ghoushchi, M_ B_ -- Analog Integrated Circuits and Signal
https://en.wikipedia.org/wiki/Chua's_circuit
https://stackoverflow.com/questions/61127919/chuas-circuit-using-python-and-graphing
https://github.com/Paramveersingh-S/Chua-s-circuit-simulation/blob/main/README.md
'''
import numpy as np
import os
from scipy.integrate import odeint
import time

ALPHA=15.6
BETA=28.0
M0=-1.143
M1=-0.714

def _chua_diode(x):
    return M1*x+0.5*(M0-M1)*(np.abs(x+1)-np.abs(x-1))

def _chua_system(state,t):
    x,y,z=state
    dxdt=ALPHA*(y-x-_chua_diode(x))
    dydt=x-y+z
    dzdt=-BETA*y
    return [dxdt,dydt,dzdt]

def _lfsr_6_bits(bits_in):
    lfsr_state=0b111111
    bits_out=np.zeros(len(bits_in),dtype=np.uint8)
    for i in range(len(bits_in)):
        bit_entrada=bits_in[i]
        b0=(lfsr_state>>0)&1
        b1=(lfsr_state>>1)&1
        new_bit=b0^b1
        bit_lfsr=(lfsr_state>>5)&1
        lfsr_state=((lfsr_state>>1)|(new_bit<<5))&0x3F
        bits_out[i]=bit_entrada^bit_lfsr
    return bits_out

def gen_bits(bits_n,seed=2043379):
    np.random.seed(seed)
    estado_inicial=0.7+np.random.uniform(-0.01,0.01)
    initial_state=[estado_inicial,0.0,0.0]
    t=np.linspace(0,bits_n*0.1,bits_n)
    sol=odeint(_chua_system,initial_state,t)
    x_signal=sol[:,0]
    bits=(x_signal>0).astype(np.uint8)
    px=_lfsr_6_bits(bits)
    return px

if __name__=="__main__":
    target_bits=1_000_000
    os.makedirs("Generadores",exist_ok=True)
    time_s=time.perf_counter()
    bits=gen_bits(target_bits)
    packed=np.packbits(bits)
    output_file=rf"Generadores\BIN_ChuaSys.bin"
    packed.tofile(output_file)
    print(f"Secuencia guardada en : {output_file}")