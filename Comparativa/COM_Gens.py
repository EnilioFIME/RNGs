import csv
import pandas as pd
import os

def parse_csv(filepath):
    data = {'NIST': {}, 'PE': {}}
    current_section = 'NIST'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row: continue
            
            if 'NOMBRE DE LA PRUEBA NIST' in row[0]:
                current_section = 'NIST'
                continue
            if 'NOMBRE DE LA PRUEBA PE' in row[0]:
                current_section = 'PE'
                continue
                
            if current_section == 'NIST':
                if row[0] in ['Pasados NIST', 'Tiempo NIST s', 'Totales']:
                    continue
                if len(row) >= 3 and row[2] in ['PASO', 'NO PASO']:
                    data['NIST'][row[0]] = row[2]
                    
            if current_section == 'PE':
                if row[0] in ['Pasados PE', 'Totales']:
                    pass
                elif len(row) >= 3 and row[2] in ['PASO', 'NO PASO']:
                    data['PE'][row[0]] = row[2]
                    
            if row[0].startswith('Entropia Bitstream'):
                data['Entropia'] = float(row[1])
            elif row[0].startswith('Distribucion 1s'):
                data['Distribucion 1s'] = float(row[1])
            elif row[0].startswith('Bitrate'):
                data['Bitrate'] = float(row[1])
                
    return data

def comparar_generadores(gen1_name, gen2_name):
    # Usamos os.path.join para evitar problemas de rutas entre Windows/Linux
    ruta_gen1 = os.path.join("Evaluacion", f"RES_EVL_NIST_EDT_BIN_{gen1_name}.csv")
    ruta_gen2 = os.path.join("Evaluacion", f"RES_EVL_NIST_EDT_BIN_{gen2_name}.csv")
    
    # Validar que los archivos existan antes de procesar
    if not os.path.exists(ruta_gen1) or not os.path.exists(ruta_gen2):
        print(f"Error: No se encontraron los archivos CSV para {gen1_name} y/o {gen2_name}.")
        print(f"Rutas buscadas:\n- {ruta_gen1}\n- {ruta_gen2}")
        return

    gen1_data = parse_csv(ruta_gen1)
    gen2_data = parse_csv(ruta_gen2)

    votes_gen1 = 0
    votes_gen2 = 0
    rows = []

    # Evaluar pruebas NIST
    nist_tests = sorted(list(set(list(gen1_data['NIST'].keys()) + list(gen2_data['NIST'].keys()))))
    for test in nist_tests:
        v1 = gen1_data['NIST'].get(test, 'N/A')
        v2 = gen2_data['NIST'].get(test, 'N/A')
        if v1 == 'PASO': votes_gen1 += 1
        if v2 == 'PASO': votes_gen2 += 1
        rows.append([f"NIST: {test}", v1, v2])

    # Evaluar pruebas PE
    pe_tests = sorted(list(set(list(gen1_data['PE'].keys()) + list(gen2_data['PE'].keys()))))
    for test in pe_tests:
        v1 = gen1_data['PE'].get(test, 'N/A')
        v2 = gen2_data['PE'].get(test, 'N/A')
        if v1 == 'PASO': votes_gen1 += 1
        if v2 == 'PASO': votes_gen2 += 1
        rows.append([f"PE: {test}", v1, v2])

    # Votación por Distribución de bits (más cercano a 0.5)
    dist1 = gen1_data.get('Distribucion 1s', 0)
    dist2 = gen2_data.get('Distribucion 1s', 0)
    diff1 = abs(0.5 - dist1)
    diff2 = abs(0.5 - dist2)
    if diff1 < diff2: votes_gen1 += 1
    elif diff2 < diff1: votes_gen2 += 1
    rows.append(["Distribucion de bits (unos)", dist1, dist2])

    # Votación por Entropía (más cercano a 8)
    ent1 = gen1_data.get('Entropia', 0)
    ent2 = gen2_data.get('Entropia', 0)
    diff_ent1 = abs(8.0 - ent1)
    diff_ent2 = abs(8.0 - ent2)
    if diff_ent1 < diff_ent2: votes_gen1 += 1
    elif diff_ent2 < diff_ent1: votes_gen2 += 1
    rows.append(["Entropia", ent1, ent2])

    # Votación por Bitrate (el más alto)
    bit1 = gen1_data.get('Bitrate', 0)
    bit2 = gen2_data.get('Bitrate', 0)
    if bit1 > bit2: votes_gen1 += 1
    elif bit2 > bit1: votes_gen2 += 1
    rows.append(["Bitrate (bits/s)", bit1, bit2])

    rows.append(["---", "---", "---"])
    rows.append(["TOTAL VOTOS", votes_gen1, votes_gen2])

    if votes_gen1 > votes_gen2: winner = f"{gen1_name}"
    elif votes_gen2 > votes_gen1: winner = f"{gen2_name}"
    else: winner = "Empate"
        
    rows.append(["GANADOR", winner, winner])

    df = pd.DataFrame(rows, columns=['Metrica', gen1_name, gen2_name])
    
    # Crear carpeta Comparativa si no existe y guardar
    os.makedirs('Comparativa', exist_ok=True)
    ruta_salida = os.path.join('Comparativa', f'Resumen_Comparativo_{gen1_name}_{gen2_name}.csv')
    df.to_csv(ruta_salida, index=False)

    print(f"\n--- Resultados de Comparativa: {gen1_name} vs {gen2_name} ---")
    print(df.to_string(index=False))
    print(f"\nResumen exportado exitosamente en: {ruta_salida}")