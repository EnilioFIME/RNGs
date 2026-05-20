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

from Evaluacion.EVL_PE import aplicar_todas

sys.path.append( os.path.abspath( os.path.join(os.path.dirname(__file__), "..") ) )

def load_gens (module_name: str): 

    mod =importlib.import_module(module_name)

    if not hasattr(mod, "gen_bits"):

        raise AttributeError(f"el modulo '{module_name}' no tiene la funcion gen")
    
    return mod.gen_bits

def bytes_to_float (secuencia):

    bytes_seq = np.asarray(secuencia, dtype=np.uint8)

    n = (len(secuencia) //4 ) *4
    bytes_seq  = bytes_seq[:n]

    ints = np.frombuffer(bytes_seq.tobytes(), dtype = '>u4')

    return  ints /np.float32(2**32)

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
    
    os.makedirs("Evaluacion", exist_ok=True)
    base_name = os.path.basename(file).replace('.bin', '')
    route = os.path.join("Evaluacion", f"RES_EVL_NIST_EDT_{base_name}.csv")

    with open(file, "rb") as f:
        bytes_data = np.frombuffer(f.read(), dtype=np.uint8)

    bits_seq = np.unpackbits(bytes_data).astype(np.int8)
    floats = bytes_to_float(bytes_data)

    generate = load_gens (gen)

    print("=" * 20)
    print(f"... Calculando Entropia para: {file}")

    bitstream_entropy = entropy (bytes_data)

    print()
    print(f"... Calculando Distribucion 0 1 para: {file}")

    bitstream_dist = (np.mean(bits_seq))
    
    print()
    print(f"... Calculando Total de Bits para: {file}")

    bitstream_len = len(bits_seq)

    fmtted_seq = bits_seq.astype(np.int8)

    eligible_batt = check_eligibility_all_battery(
        fmtted_seq,
        SP800_22R1A_BATTERY
    )

    skip_tests = {
        "linear_complexity",
        "serial",
        "approximate_entropy",
        "random_excursion",
        "maurers_universal",
        "dft"
    }

    print()
    print(f"... Calculando Bitrate para: {file}")
    print(f"... Generando Bits para: {file}")

    t_start = time.perf_counter()
    px = generate(bits_n)
    t_gen = time.perf_counter() - t_start

    bitstream_len = len(bits_seq)

    bitrate = bitstream_len / t_gen if t_gen > 0 else float ("inf")
   
    print("=" * 70)
    print(f"... Iniciando NIST para: {file}")

    print(f"Pruebas NIST elegibles: {len(eligible_batt) - len(skip_tests)}")

    print("\nEjecutando pruebas... Aproximadamente 4 minutos...\n")

    results = []
    total_start = time.time()

    for i, (test_name, test_obj) in enumerate(eligible_batt.items()):

        if test_name in skip_tests:

            continue

        print(f"[ Ejecutando: {test_name} ]")

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

        print(f"\n{'NOMBRE DE LA PRUEBA':<35}  {'P-VALUE':<12}  {'RESULTADO'}")
        c.writerow(["NOMBRE DE LA PRUEBA NIST", "P-VALUE", "RESULTADO"])
        print("-" * 70)

        success = 0

        for result, test_name in results:

            status = "PASO" if result.passed else "NO PASO"

            if result.passed:
                success += 1

            print(f"{test_name:<35}  {result.score:<12.5f}  {status}")
            c.writerow([test_name, result.score, status])

        
        print(f"Resumen: Pasado {success} de {len(results)} pruebas NIST")
        c.writerow(["Pasados NIST", success, "Totales", len(results)])
        c.writerow(["Tiempo NIST s", round(total_elapsed, 2)])

        print("=" * 70)
        print(f"... Ejecutando Pruebas Estadisticas para: {file}")

        resultados_pe = aplicar_todas(floats)

        print(f"\n{'PRUEBA':<25} {'ESTADÍSTICO':>14} {'CRÍTICO':>10} {'RESULTADO':>10}")
        c.writerow(['NOMBRE DE LA PRUEBA PE', 'ESTADISTICO', 'RESULTADO'])
        print("-" * 65)

        pasados = 0
        for nombre, r in resultados_pe.items():
            estado = "PASO" if r["aprobado"] else "NO PASO"
            pasados += 1 if estado == "PASO" else 0
            print(f"{r['prueba']:<25} {r['estadistico']:>14.6f} {r['critico']:>10.5f} {estado:>10}")
            c.writerow([r['prueba'], r['estadistico'], estado])
            
        c.writerow(["Pasados PE", pasados, "Totales", len(resultados_pe)])
        print("=" * 70)

        print(f"Total bits: {bitstream_len}")

        print ("Entropia del Bitsream: " , bitstream_entropy )
        print("Distribucion de 1s: ", bitstream_dist)
        print("Distribucion de 0s: ", 1 - bitstream_dist)
        print("Tiempo de Generacion: ", t_gen)
        print("Bitrate: ", bitrate)
       
        c.writerow(["Entropia Bitstream", bitstream_entropy])
        c.writerow(["Distribucion 1s", bitstream_dist])
        c.writerow(["Distribucion 0s", 1 - bitstream_dist])
        c.writerow(["Total Bits", bitstream_len])
        c.writerow(["Tiempo de Generacion s", t_gen])
        c.writerow(["Bitrate bits/s", bitrate])

if __name__ == "__main__":
    print("Por favor, ejecuta las evaluaciones desde el menu principal (main.py).")