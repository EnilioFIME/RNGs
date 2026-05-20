import numpy as np
import os

SLOPE=np.float64(2.0)
REF_VOLTAGE=np.float64(1.0)
THRESHOLD=np.float64(0.0)

def _pwam_sc_stage(x_voltage):
    abs_v=np.float64(np.abs(x_voltage))
    return np.float64(np.float64(SLOPE*abs_v)-REF_VOLTAGE)

def _cmos_comparator(voltage):
    return 1 if voltage>=THRESHOLD else 0

def gen_bits(bits_n,seed=2043379):
    voltage_state=np.float64(seed/9999999)
    bits=np.zeros(bits_n,dtype=np.uint8)

    for i in range(bits_n):
        voltage_state=_pwam_sc_stage(voltage_state)
        raw_bit=_cmos_comparator(voltage_state)

        if i>0:
            bits[i]=raw_bit^bits[i-1]
        else:
            bits[i]=raw_bit

    return bits

if __name__=="__main__":
    target_bits=1_000_000
    os.makedirs("Generadores",exist_ok=True)
    bits=gen_bits(target_bits)
    packed=np.packbits(bits)
    output_path=rf"Generadores\BIN_PWAMMapp.bin"
    packed.tofile(output_path)
    print(f"Secuencia guardada en : {output_path}")