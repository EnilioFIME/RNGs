import numpy as np
import os
import time

SEED=2043379
V_DD=1.0
V_TH=V_DD/2

GAIN_SRO=12.0
GAIN_FRO=18.0
TG_STRENGTH_1=0.08
TG_STRENGTH_2=0.11
NOISE_STD=5e-4

def _inverter(v_in,gain):
    v_clipped=np.clip(v_in,0.0,V_DD)
    return V_DD/(1.0+np.exp(gain*(v_clipped-V_TH)))

def _ring_step(ring,gain,noise,rng):
    thermal=rng.normal(0,noise,len(ring))
    rolled=np.roll(ring,1)
    nxt=np.array([_inverter(v,gain) for v in rolled])+thermal
    return np.clip(nxt,0.0,V_DD)

def _mnr_coupling(v_fro_out,v_sro,gain_sro,noise_std,rng):
    v_gs=np.clip(v_fro_out-V_TH,0.0,V_DD)
    g_mnr=v_gs**2
    pull_down=g_mnr*0.15*V_DD
    sro_mod=v_sro.copy()
    sro_mod[0]=np.clip(v_sro[0]-pull_down,0.0,V_DD)
    return sro_mod

def _tg_coupling(ring_a,ring_b,tg_strength):
    delta=ring_b[0]-ring_a[0]
    ring_a_new=ring_a.copy()
    ring_b_new=ring_b.copy()
    ring_a_new[0]=np.clip(ring_a[0]+tg_strength*delta,0.0,V_DD)
    ring_b_new[0]=np.clip(ring_b[0]-tg_strength*delta,0.0,V_DD)
    return ring_a_new,ring_b_new

def _simulate_crng(target_bits,sro_init,fro_init,tg_strength,rng):
    sro=sro_init.copy()
    fro=fro_init.copy()
    f_high=rng.integers(0,2,size=target_bits,dtype=np.uint8)
    bits=np.empty(target_bits,dtype=np.uint8)

    for i in range(target_bits):
        sro=_ring_step(sro,GAIN_SRO,NOISE_STD,rng)
        fro=_ring_step(fro,GAIN_FRO,NOISE_STD,rng)
        sro=_mnr_coupling(fro[0],sro,GAIN_SRO,NOISE_STD,rng)
        sro,fro=_tg_coupling(sro,fro,tg_strength)
        bits[i]=f_high[i] if sro[0]>V_TH else 1-f_high[i]

    return bits

def gen_bits(target_bits,seed=2043379):
    rng=np.random.Generator(np.random.MT19937(seed))

    sro_init_1=np.array([0.1,0.9,0.5,0.3,0.7],dtype=np.float64)
    fro_init_1=np.array([0.8,0.2,0.6],dtype=np.float64)

    sro_init_2=np.array([0.9,0.1,0.6,0.4,0.2],dtype=np.float64)
    fro_init_2=np.array([0.3,0.7,0.4],dtype=np.float64)

    bits_1=_simulate_crng(target_bits,sro_init_1,fro_init_1,TG_STRENGTH_1,rng)

    bits_2=_simulate_crng(target_bits,sro_init_2,fro_init_2,TG_STRENGTH_2,rng)

    return np.bitwise_xor(bits_1,bits_2)

if __name__=="__main__":
    target_bits=1_000_000
    os.makedirs("Generadores",exist_ok=True)
    bits=gen_bits(target_bits)
    packed=np.packbits(bits)
    output_path=os.path.join("Generadores","BIN_DiscTimeOsc.bin")
    packed.tofile(output_path)
    print(f"Secuencia guardada en: {output_path}")