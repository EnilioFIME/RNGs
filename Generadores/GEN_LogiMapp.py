'''
Survey: 2.2.1 Logistic Mapping, Table 1
https://mikekipruto.substack.com/p/simulating-the-logistic-map-in-python
pdf gpu_nody  J. S. Teh 
https://www.geeksforgeeks.org/python/get-the-logical-xor-of-two-variables-in-python/
https://stackoverflow.com/questions/432842/how-do-you-get-the-logical-xor-of-two-variables-in-python
https://stackoverflow.com/questions/21341338/extract-lsb-bit-from-a-byte-in-python
https://stackoverflow.com/questions/32834963/most-significant-byte-calculation
'''

import numpy as np
import struct
import math as mt
import os

def _logistic_mapping(x,mu):
    return mu*x*(1-x)

def _function_seed(seed):
    return seed/9999999

def _mu_change(x,mu):
    y=2
    tmp_list=[]
    if x>=0.5:
        for _ in range(y):
            x=_logistic_mapping(x,mu)
        mu=3.99
    else:
        for _ in range(y):
            x=_logistic_mapping(x,mu)
            tmp=3.86+(x*0.14)
            tmp_list.append(tmp)
        mu=np.mean(tmp_list)
    return x,mu

def _pointer_casting(x):
    return struct.unpack('Q',struct.pack('d',x))[0]

def _unsigned_int(x1,x2):
    C1=_pointer_casting(x1)
    C2=_pointer_casting(x2)
    M1=C1&0xFFFFFFFF
    M2=(C1>>32)&0xFFFFFFFF
    M3=C2&0xFFFFFFFF
    M4=(C2>>32)&0xFFFFFFFF
    v=((((M1+M4)&0xFFFFFFFF)^M3)+M2)&0xFFFFFFFF
    v^=(v>>13)
    v^=(v<<17)&0xFFFFFFFF
    v^=(v>>5)
    return v

def gen_bits(bits_n,seed=2043379):
    mu_init=3.99
    x0=_function_seed(seed)
    words_n=mt.ceil(bits_n/32)
    mu=mu_init
    xtemp=x0

    for _ in range(1000):
        xtemp,_=_mu_change(xtemp,mu)

    x=np.zeros(words_n)
    px=np.zeros(words_n,dtype=np.uint32)

    x[0]=xtemp

    for i in range(1,words_n):
        x[i],mu=_mu_change(x[i-1],mu)

    for i in range(words_n):
        x2=(i+33)%words_n
        px[i]=_unsigned_int(x[i],x[x2])

    px_bytes=px.astype('>u4').view(np.uint8)
    bits_array=np.unpackbits(px_bytes)

    return bits_array[:bits_n]

if __name__=="__main__":
    target_bits=1_000_000
    os.makedirs("Generadores",exist_ok=True)
    bits=gen_bits(target_bits)
    packed=np.packbits(bits)
    packed.tofile(rf"Generadores\BIN_LogiMapp.bin")
    print("Secuencia guardada en  : BIN_LogiMapp.bin")