'''

https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.welch.html
https://docs.python.org/3/library/zlib.html


'''

import numpy as np
import csv
import zlib
from scipy.signal import welch

GEN = "ChuaSys"
bitstream = f"BIN_{GEN}"

def calcular_entropia_espectral(senal: np.ndarray) -> float:
    _, psd = welch(senal)
    psd_norm = psd / np.sum(psd)
    return -np.sum(psd_norm * np.log2(psd_norm + 1e-12))

def calcular_compresion(senal: np.ndarray) -> float:
    bytes_senal = senal.astype(np.float32).tobytes()
    compressed = zlib.compress(bytes_senal)
    return len(compressed) / len(bytes_senal)

def calcular_autocorrelacion(senal: np.ndarray, lag: int) -> float:
    if len(senal) <= lag:
        return 0.0
    corr = np.corrcoef(senal[:-lag], senal[lag:])[0, 1]
    return float(corr) if not np.isnan(corr) else 0.0

def calcular_informacion_mutua(senal: np.ndarray, lag: int, bins: int = 64) -> float:
    c_xy, _, _ = np.histogram2d(senal[:-lag], senal[lag:], bins=bins)
    p_xy = c_xy / np.sum(c_xy)
    p_x = np.sum(p_xy, axis=1)
    p_y = np.sum(p_xy, axis=0)
    
    p_x_p_y = p_x[:, None] * p_y[None, :]
    nz = p_xy > 0
    mi = np.sum(p_xy[nz] * np.log2(p_xy[nz] / p_x_p_y[nz]))
    return float(mi)

def calcular_dimension_higuchi(senal: np.ndarray, k_max: int = 10) -> float:
    n = len(senal)
    l_m_k = np.zeros((k_max, k_max))
    for k in range(1, k_max + 1):
        for m in range(k):
            indices = np.arange(m, n, k)
            if len(indices) > 1:
                diff = np.abs(np.diff(senal[indices]))
                l_m_k[m, k - 1] = (np.sum(diff) * (n - 1)) / (len(indices) * k)
    
    l_k = np.zeros(k_max)
    for k in range(1, k_max + 1):
        l_k[k - 1] = np.sum(l_m_k[:k, k - 1]) / k
        
    x = np.log(1.0 / np.arange(1, k_max + 1))
    y = np.log(l_k)
    poly = np.polyfit(x, y, 1)
    return float(poly[0])

with open(rf"Generadores\{bitstream}.bin", "rb") as f:
    keystream = f.read()

ruido_uint8 = np.frombuffer(keystream, dtype=np.uint8)
muestras = len(ruido_uint8)
t = np.arange(muestras)
frecuencia_senoide = 0.01

# 1. Generar la senoide flotante original
senoide_flotante = np.sin(2 * np.pi * frecuencia_senoide * t)

# 2. Cuantizar la senoide a enteros de 8 bits [0, 255] para igualar el RNG
senoide_uint8 = np.uint8((senoide_flotante + 1.0) * 127.5)

# 3. Enmascaramiento total: usar XOR para que cada bit del ruido mute la senoide
senal_mixta_uint8 = np.bitwise_xor(senoide_uint8, ruido_uint8)

# 4. Normalizar de vuelta a flotante [-1.0, 1.0] para que las métricas (HFD, Autocorr) funcionen igual
senal_mixta = (senal_mixta_uint8.astype(float) - 127.5) / 127.5

# Opcional pero estricto: Normalizar la senoide cuantizada para la métrica de "Correlacion vs Senoide"
senoide = (senoide_uint8.astype(float) - 127.5) / 127.5

entropia_espectral = calcular_entropia_espectral(senal_mixta)
ratio_comp = calcular_compresion(senal_mixta)
autocorr_1 = calcular_autocorrelacion(senal_mixta, 1)
autocorr_2 = calcular_autocorrelacion(senal_mixta, 2)
info_mutua = calcular_informacion_mutua(senal_mixta, 1)
higuchi_fd = calcular_dimension_higuchi(senal_mixta, 10)
correlacion_base = float(np.corrcoef(senoide, senal_mixta)[0, 1])

results = {
    "Entropia Espectral bits": entropia_espectral,
    "Ratio Compresion ZLIB": ratio_comp,
    "Autocorrelacion (d=1)": autocorr_1,
    "Autocorrelacion (d=2)": autocorr_2,
    "Informacion Mutua (lag=1) bits": info_mutua,
    "Dimension Higuchi": higuchi_fd,
    "Correlacion vs Senoide": correlacion_base,
    "Muestras Evaluadas n": muestras
}

for k, v in results.items():
    print(f"{k:<30}: {v}")
print("=" * 40)

route = rf"Simulacion\RES_SIM_sinSig_{bitstream}.csv"

with open(route, "w", newline="", encoding="utf-8") as file:
    f = csv.writer(file)

    f.writerow(["Metrica", "Valor"])

    for text, value in results.items():
        f.writerow([text, value])
        
print(f"CSV GUARDADO EN: {route} ")