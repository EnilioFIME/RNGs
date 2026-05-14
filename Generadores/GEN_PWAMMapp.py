import numpy as np
import os

# --- Emulación de Parámetros de Hardware SC (Switched-Capacitor) a 32-bits ---
# Utilizamos un mapa PWAM clásico simétrico: M(x) = 2|x| - 1
# Este mapa expande el espacio y genera caos iterativo.
SLOPE = np.float32(2.0)
REF_VOLTAGE = np.float32(1.0)
THRESHOLD = np.float32(0.0)

def _pwam_sc_stage(x_voltage):
    """
    Emula la etapa de capacitores conmutados del circuito CMOS.
    Ejecuta el mapa PWAM (Piecewise-Affine Markov) en un ciclo de reloj.
    Todo forzado a 32-bits para emular las pérdidas de precisión.
    """
    # M(x) = 2 * |x| - 1
    # Representa la ganancia del amplificador operacional y la inyección de carga.
    abs_v = np.float32(np.abs(x_voltage))
    next_voltage = np.float32(np.float32(SLOPE * abs_v) - REF_VOLTAGE)
    return next_voltage

def _cmos_comparator(voltage):
    """
    Emula el comparador de alta velocidad a la salida del circuito.
    Retorna 1 si el voltaje supera el umbral, 0 en caso contrario.
    """
    return 1 if voltage >= THRESHOLD else 0

def gen_bits(bits_n):
    """Generación de bits emulando el pipeline CMOS del artículo"""
    
    # Voltaje inicial atrapado en el capacitor (Semilla)
    voltage_state = np.float32(0.1234567) 
    
    bits = np.zeros(bits_n, dtype=np.uint8)
    
    print(f"Iterando circuito PWAM discreto para {bits_n} bits...")
    
    for i in range(bits_n):
        # 1. Ciclo de reloj: El voltaje salta al siguiente estado discreto
        voltage_state = _pwam_sc_stage(voltage_state)
        
        # 2. El comparador evalúa el voltaje actual
        raw_bit = _cmos_comparator(voltage_state)
        
        # 3. Post-procesamiento Digital (Mitigación de Bias)
        # En la salida del chip, se aplica un XOR entre el bit actual 
        # y el bit del ciclo de reloj anterior para balancear posibles offsets 
        # analógicos del comparador.
        if i > 0:
            bits[i] = raw_bit ^ bits[i-1]
        else:
            bits[i] = raw_bit
            
    return bits

if __name__ == "__main__":
    target_bits = 1_000_000
    os.makedirs("Generadores", exist_ok=True)

    # Generar secuencia de bits
    bits = gen_bits(target_bits)
    
    # Empaquetado de bits a bytes (8 bits -> 1 byte real)
    packed = np.packbits(bits)
    
    output_path = r"Generadores\BIN_PWAMMapp.bin"
    packed.tofile(output_path)
    
    print(f"Secuencia guardada en : {output_path}")
    print("Metodología: Mapa PWAM discreto (32-bit) + Comparador Analógico + Corrección XOR Diferencial")