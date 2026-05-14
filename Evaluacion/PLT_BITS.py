import numpy as np
import matplotlib.pyplot as plt


GEN = "LFSR"
bitstream = f"BIN_{GEN}"
route = rf"Generadores\{bitstream}.bin"

# Leer archivo binario
with open(route, "rb") as f:
    data = np.frombuffer(f.read(), dtype=np.uint8)

# Desempaquetar bytes -> bits
bits = np.unpackbits(data)

print("Cantidad de bits:", len(bits))
print(bits[:20])  # primeros 20 bits

# Graficar
plt.figure(figsize=(15, 4))
plt.plot(bits[-1000:], linewidth=1)  # solo primeros 1000 para visualizar
plt.ylim(-0.2, 1.2)
plt.xlabel("Índice")
plt.ylabel("Bit")
plt.title("Secuencia binaria")
plt.grid(True)

plt.show()