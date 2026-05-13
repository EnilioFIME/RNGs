import time
import numpy as np
from nistrng import (
    pack_sequence,
    check_eligibility_all_battery,
    SP800_22R1A_BATTERY
)

def nist_eval(file):

    print("=" * 20)
    print(f"... Iniciando NIST para: {file}")

    with open(file, "rb") as f:
        bytes_data = np.frombuffer(f.read(), dtype=np.uint8)

    bits_seq = np.unpackbits(bytes_data)

    print(f"Total bits: {len(bits_seq)}")
    print(f"Promedio de bits: {np.mean(bits_seq):.6f}")

    fmtted_seq = pack_sequence(bits_seq)

    eligible_batt = check_eligibility_all_battery(
        fmtted_seq,
        SP800_22R1A_BATTERY
    )

    print(f"Pruebas elegibles: {len(eligible_batt)}")

    print("\nEjecutando pruebas...\n")

    results = []
    total_start = time.time()

    for i, (test_name, test_obj) in enumerate(eligible_batt.items()):

        print(f"[{i+1}/{len(eligible_batt)}] Ejecutando: {test_name}")

        start = time.time()

        try:
            # Usamos el objeto (test_obj) para ejecutar la matemática
            result, elapsed_time = test_obj.run(fmtted_seq)

            elapsed = time.time() - start

            print(f"   -> terminado en {elapsed:.2f} s")

            # Guardamos el resultado y el nombre de la prueba en la lista
            results.append((result, test_name))

        except Exception as e:

            elapsed = time.time() - start

            print(f"   -> ERROR despues de {elapsed:.2f} s")
            print(f"      {e}")

    total_elapsed = time.time() - total_start

    print(f"\nTiempo total: {total_elapsed:.2f} s")

    print(f"\n{'NOMBRE DE LA PRUEBA':<35} | {'P-VALUE':<12} | {'RESULTADO'}")
    print("-" * 70)

    success = 0

    for result, test_name in results:

        status = "PASÓ" if result.passed else "NO PASÓ"

        if result.passed:
            success += 1

        print(f"{test_name:<35} | {result.score:<12.5f} | {status}")

    print("-" * 70)
    print(f"Resumen: Pasado {success} de {len(results)} pruebas")


# Ejecución
nist_eval(r"Generadores\BIN_TentMapp.bin")