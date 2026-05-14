import numpy as np
import os

# --- Emulación de Registros Constantes de 32 bits (IEEE 754-1985) ---
A = np.float32(2.8)
B = np.float32(0.2)
C = np.float32(1.4)
D = np.float32(1.0)
E = np.float32(10.0)
F = np.float32(2.0)

# Parámetros de RK4 casteados a 32 bits
H = np.float32(0.04)
HALF = np.float32(0.5)
ONE_SIXTH = np.float32(1.0 / 6.0)
TWO = np.float32(2.0)

def _chaotic_system(state):
    """
    Ecuaciones de estado del sistema caótico.
    Cada operación emula la salida de un bloque multiplicador/sumador de 32-bits en la FPGA.
    """
    x, y, z = state
    
    # Ecuación dx: a*y - x + z*y
    dx = np.float32(np.float32(A * y) - x + np.float32(z * y))
    
    # Ecuación dy: -b*x*z - c*x + y*z + d
    dy = np.float32(np.float32(np.float32(-B * x) * z) - np.float32(C * x) + np.float32(y * z) + D)
    
    # Ecuación dz: e - f*x*y - x^2
    dz = np.float32(E - np.float32(np.float32(F * x) * y) - np.float32(x * x))
    
    return np.array([dx, dy, dz], dtype=np.float32)

def _rk4_step(state):
    """
    Algoritmo Runge-Kutta de 4to orden estricto a 32-bits.
    """
    k1 = _chaotic_system(state)
    k2 = _chaotic_system(state + np.float32(np.float32(HALF * H) * k1))
    k3 = _chaotic_system(state + np.float32(np.float32(HALF * H) * k2))
    k4 = _chaotic_system(state + np.float32(H * k3))

    # Acumulación iterativa truncando a 32 bits en cada suma
    sum_k = np.float32(k1 + np.float32(TWO * k2))
    sum_k = np.float32(sum_k + np.float32(TWO * k3))
    sum_k = np.float32(sum_k + k4)
    
    return state + np.float32(np.float32(H * ONE_SIXTH) * sum_k)

def gen_bits(bits_n):
    """Generación de bits emulando el pipeline de la FPGA"""
    # Condiciones iniciales en registro de 32 bits
    state = np.array([0.0, 0.0, 0.0], dtype=np.float32)
    
    bits = np.zeros(bits_n, dtype=np.uint8)
    
    print(f"Calculando {bits_n} bits (Advertencia: Los casteos constantes a 32-bit hacen la simulación más lenta pero determinística...)")
    
    for i in range(bits_n):
        state = _rk4_step(state)
        
        # Emulación del ruteo de hardware: leemos la memoria de 32 bits directamente
        # En una FPGA, se toma el LSB de la mantisa directamente del bus (cable 0)
        hardware_bus = state.view(np.int32)
        
        # Extracción del bit menos significativo de cada variable
        bx = hardware_bus[0] & 1
        by = hardware_bus[1] & 1
        bz = hardware_bus[2] & 1
        
        # Post-procesamiento XOR como bloque lógico final
        bits[i] = bx ^ by ^ bz
        
    return bits

if __name__ == "__main__":
    target_bits = 1_000_000
    os.makedirs("Generadores", exist_ok=True)

    # Generar secuencia
    bits = gen_bits(target_bits)
    
    # Empaquetado
    packed = np.packbits(bits)
    
    output_path = r"Generadores\BIN_FPGABase.bin"
    packed.tofile(output_path)
    
    print(f"Secuencia guardada en : {output_path}")