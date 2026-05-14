import time
import numpy as np
import csv
import os
import importlib
import sys

from nistrng import (
    check_eligibility_all_battery,
    SP800_22R1A_BATTERY
)

GEN = "FPGABase"
generator = f"GEN_{GEN}"
bitstream = f"BIN_{GEN}"

target_bits = 1_000_000

sys.path.append( os.path.abspath( os.path.join(os.path.dirname(__file__), "..") ) )

os.makedirs("Evaluacion", exist_ok=True)

route = rf"Evaluacion\RES_EVL_NIST_EDT_{bitstream}.csv"

def load_gens (module_name: str): 

    mod =importlib.import_module(module_name)

    if not hasattr(mod, "gen_bits"):

        raise AttributeError(f"el modulo '{module_name}' no tiene la funcion gen")
    
    return mod.gen_bits

def entropy (datos) -> bytes:

    if len(datos) == 0:

        return 0.0
    
    leng = len(datos)
    freq = [0] * 256

    for byte in datos:

        freq[byte] += 1

    entropia = 0.0

    for count in freq:

        if count > 0:

            P = count / leng

            entropia += - P * np.log2(P)

    return entropia

def nist_evals(file, gen, bits_n):

    with open(file, "rb") as f:
        bytes_data = np.frombuffer(f.read(), dtype=np.uint8)

    generate = load_gens (gen)

    print("=" * 20)
    print(f"... Calculando Entropia para: {file}")

    bitstream_entropy = entropy (bytes_data)
    print ("Entropia del Bitsream: " , bitstream_entropy )

    bits_seq = np.unpackbits(bytes_data).astype(np.int8)

    print()
    print(f"... Calculando Distribucion 0 1 para: {file}")

    bitstream_dist = (np.mean(bits_seq))
    print("Distribucion de 1s: ", bitstream_dist)
    print("Distribucion de 0s: ", 1 - bitstream_dist)

    print()
    print(f"... Calculando Total de Bits para: {file}")

    bitstream_len = len(bits_seq)

    print(f"Total bits: {bitstream_len}")

    fmtted_seq = bits_seq.astype(np.int8)

    eligible_batt = check_eligibility_all_battery(
        fmtted_seq,
        SP800_22R1A_BATTERY
    )

    skip_tests = {
        "linear_complexity",
        "serial",
        "approximate_entropy"
    }

    print()
    print(f"... Calculando Bitrate para: {file}")
    print(f"... Generando Bits para: {file}")

    t_start = time.perf_counter()
    px = generate(bits_n)
    t_gen = time.perf_counter() - t_start

    bitstream_len = len(bits_seq)

    bitrate = bitstream_len / t_gen if t_gen > 0 else float ("inf")

    print("Bitrate: ", bitrate)
    print("Tiempo de Generacion: ", t_gen)

    print("=" * 20)
    print(f"... Iniciando NIST para: {file}")

    print(f"Pruebas NIST elegibles: {len(eligible_batt) - len(skip_tests)}")

    print("\nEjecutando pruebas... Aproximadamente 12 minutos...\n")

    results = []
    total_start = time.time()

    for i, (test_name, test_obj) in enumerate(eligible_batt.items()):

        if test_name in skip_tests:

            continue

        print(f"[{i+1}/{len(eligible_batt) - len(skip_tests)}] Ejecutando: {test_name}")

        start = time.time()

        try:

            result, elapsed_time = test_obj.run(fmtted_seq)

            elapsed = time.time() - start

            print(f"   -> terminado en {elapsed:.2f} s")

            results.append((result, test_name))

        except Exception as e:

            elapsed = time.time() - start

            print(f"   -> ERROR despues de {elapsed:.2f} s")
            print(f"      {e}")

    total_elapsed = time.time() - total_start

    with open(route, "w", newline="", encoding="utf-8") as csv_file:

        c = csv.writer(csv_file)

        print(f"\nTiempo Pruebas Nist: {total_elapsed:.2f} s")

        print(f"\n{'NOMBRE DE LA PRUEBA':<35} | {'P-VALUE':<12} | {'RESULTADO'}")
        c.writerow(["NOMBRE DE LA PRUEBA", "P-VALUE", "RESULTADO"])
        print("-" * 70)

        success = 0

        for result, test_name in results:

            status = "PASO" if result.passed else "NO PASO"

            if result.passed:
                success += 1

            print(f"{test_name:<35} | {result.score:<12.5f} | {status}")
            c.writerow([test_name, result.score, status])

        print("-" * 70)
        print(f"Resumen: Pasado {success} de {len(results)} pruebas")
        c.writerow(["Pasados", success, "Totales", len(results)])
        c.writerow(["Tiempo NIST s", round(total_elapsed, 2)])
        c.writerow(["Entropia Bitstream", bitstream_entropy])
        c.writerow(["Distribucion 1s", bitstream_dist])
        c.writerow(["Distribucion 0s", 1 - bitstream_dist])
        c.writerow(["Total Bits", bitstream_len])
        c.writerow(["Tiempo de Generacion s", t_gen])
        c.writerow(["Bitrate bits/s", bitrate])

# Ejecución
if __name__ == "__main__":

    nist_evals(rf"Generadores\{bitstream}.bin", rf"Generadores.{generator}", target_bits)