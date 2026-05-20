import os
import time
import numpy as np
import importlib
import sys
import os
from COM_Gens import comparar_generadores

# Sube un nivel en los directorios para que Python detecte la carpeta "Evaluacion"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Hardcodeamos la lista de generadores disponibles
GENERADORES = [
    "GEN_ChuaSys",
    "GEN_JerkSys",
    "GEN_BoolChaoOsc",
    "GEN_CoupChaoOsc",
    "GEN_CurrModeChao",
    "GEN_FPGABase",
    "GEN_BernMapp",
    "GEN_LogiMapp",
    "GEN_TentMapp",
    "GEN_PWAMMapp",
    "GEN_DiscTimeOsc",
    "GEN_MersTwis",
    "GEN_PCG64",
    "GEN_CongMix",
    "GEN_CongMult",
    "GEN_LFSR",
    "GEN_XORShif128",
    # Agrega más aquí conforme los vayas creando, ej: "GEN_Rossler", "GEN_Lorenz"
]

COMPARAR_GENS = [
    {"gen1" : "ChuaSys"     , "gen2":"MersTwis" },
    {"gen1" : "JerkSys"     , "gen2":"PCG64"    },
    {"gen1" : "BoolChaoOsc" , "gen2":"CongMix"  },
    {"gen1" : "CoupChaoOsc" , "gen2":"CongMult" },
    {"gen1" : "CurrModeChao", "gen2":"LFSR"     },
    {"gen1" : "FPGABase"    , "gen2":"XORShif128"},
    {"gen1" : "BernMapp"    , "gen2":"MersTwis" },
    {"gen1" : "LogiMapp"    , "gen2":"PCG64"    },
    {"gen1" : "TentMapp"    , "gen2":"CongMix"  },
    {"gen1" : "PWAMMapp"    , "gen2":"CongMult" },
    {"gen1" : "DiscTimeOsc" , "gen2":"LFSR"     },
    
]

CARPETA_GENERADORES = "Generadores"

def menu_comparar():
    while True:
        print("=" * 70)
        print("COMPARATIVA DE GENERADORES")
        print("=" * 70)
        
        if not COMPARAR_GENS:
            print("La lista de comparaciones (COMPARAR_GENS) está vacía.")
            input("\nPresiona Enter para regresar...")
            break

        for i, par in enumerate(COMPARAR_GENS):
            print(f"{i + 1}. {par['gen1']} \t vs \t {par['gen2']}")
            
        opcion_regresar = len(COMPARAR_GENS) + 1
        print(f"{opcion_regresar}. Regresar al Menu Principal")
        print("=" * 70)
        
        opcion = input("Selecciona un par para comparar: ")
        
        try:
            opcion = int(opcion)
        except ValueError:
            print("Entrada no valida.")
            continue
            
        if 1 <= opcion <= len(COMPARAR_GENS):
            seleccion = COMPARAR_GENS[opcion - 1]
            print("=" * 70)
            print(f"Iniciando comparativa entre {seleccion['gen1']} y {seleccion['gen2']}...")
            
            # Mandamos a llamar a la función modularizada
            comparar_generadores(seleccion["gen1"], seleccion["gen2"])
            
            input("\nPresiona Enter para continuar...")
        elif opcion == opcion_regresar:
            break
        else:
            print("Opcion fuera de rango.")

def generar_y_guardar(generador_nombre, target_bits, semilla):
    os.makedirs(CARPETA_GENERADORES, exist_ok=True)
    print("=" * 70)
    print(f"Cargando generador: {generador_nombre}...")
    
    # Importación dinámica del módulo
    try:
        # Intenta importar como si estuviera dentro de la carpeta Generadores
        mod = importlib.import_module(f"{CARPETA_GENERADORES}.{generador_nombre}")
    except ModuleNotFoundError:
        try:
            # Fallback por si los scripts están en la misma carpeta que main.py
            mod = importlib.import_module(generador_nombre)
        except ModuleNotFoundError:
            print(f"Error: No se encontró el módulo '{generador_nombre}'.")
            return

    if not hasattr(mod, "gen_bits"):
        print(f"Error: El módulo {generador_nombre} no tiene la función 'gen_bits'.")
        return

    generate = mod.gen_bits

    print(f"Iniciando generacion con seed: {semilla} y {target_bits:,} bits...")
    t0 = time.perf_counter()
    bits = generate(target_bits, seed=semilla)
    elapsed = time.perf_counter() - t0

    ceros = int(np.sum(bits == 0))
    unos  = int(np.sum(bits == 1))
    
    print(f"Resultados: {ceros} Ceros ({ceros/target_bits*100:.2f}%) | {unos} Unos ({unos/target_bits*100:.2f}%)")
    print(f"Tiempo: {elapsed:.4f} s")
    
    packed = np.packbits(bits)
    # Formateo del nombre: BIN_CurrModeChao_seedXXXX.bin
    nombre_limpio = generador_nombre.replace("GEN_", "")
    nombre_archivo = f"BIN_{nombre_limpio}.bin"
    output_path = os.path.join(CARPETA_GENERADORES, nombre_archivo)
    
    packed.tofile(output_path)
    print(f"Secuencia guardada exitosamente en: {output_path}")

def menu_generar(seed_actual):
    while True:
        print("=" * 70)
        print(f"GENERADORES - SEED ACTUAL = {seed_actual}")
        print("=" * 70)
        
        for i, gen in enumerate(GENERADORES):
            print(f"{i + 1}. {gen}")
            
        opcion_cambiar_seed = len(GENERADORES) + 1
        opcion_regresar = len(GENERADORES) + 2
        
        print(f"{opcion_cambiar_seed}. Cambiar Seed")
        print(f"{opcion_regresar}. Regresar al Menu Principal")
        print("=" * 70)
        
        opcion = input("Selecciona una opcion: ")
        
        try:
            opcion = int(opcion)
        except ValueError:
            print("Entrada no valida.")
            continue
            
        if 1 <= opcion <= len(GENERADORES):
            bits_input = input("Cantidad de bits a generar (Enter para 1,000,000): ")
            bits = int(bits_input) if bits_input.strip() else 1_000_000
            generar_y_guardar(GENERADORES[opcion - 1], bits, seed_actual)
            input("\nPresiona Enter para continuar...")
            
        elif opcion == opcion_cambiar_seed:
            nueva_seed = input("Introduce la nueva seed: ")
            try:
                seed_actual = int(nueva_seed)
                print(f"Seed actualizada a: {seed_actual}")
            except ValueError:
                print("Seed no valida. Debe ser un numero entero.")
                
        elif opcion == opcion_regresar:
            break
        else:
            print("Opcion fuera de rango.")
            
    return seed_actual

def menu_evaluar():
    while True:
        print("=" * 70)
        print("EVALUACION - SECUENCIAS DISPONIBLES")
        print("=" * 70)
        
        os.makedirs(CARPETA_GENERADORES, exist_ok=True)
        # Escaneo dinámico de los archivos binarios en la carpeta
        archivos_bin = [f for f in os.listdir(CARPETA_GENERADORES) if f.endswith('.bin')]
        
        if not archivos_bin:
            print("No hay secuencias generadas en la carpeta.")
            print("=" * 70)
            input("Presiona Enter para regresar...")
            break
            
        for i, archivo in enumerate(archivos_bin):
            print(f"{i + 1}. {archivo}")
            
        opcion_regresar = len(archivos_bin) + 1
        print(f"{opcion_regresar}. Regresar al Menu Principal")
        print("=" * 70)
        
        opcion = input("Selecciona una secuencia para evaluar: ")
        
        try:
            opcion = int(opcion)
        except ValueError:
            print("Entrada no valida.")
            continue
            
        if 1 <= opcion <= len(archivos_bin):
            archivo_seleccionado = archivos_bin[opcion - 1]
            ruta_archivo = os.path.join(CARPETA_GENERADORES, archivo_seleccionado)
            
            # Deducir el nombre del generador a partir del nombre del archivo
            # Ej: de "BIN_CurrModeChao_seed123.bin" extrae "CurrModeChao" y forma "GEN_CurrModeChao"
            archivo_sin_ext = archivo_seleccionado.replace('.bin', '')
            partes = archivo_sin_ext.split("_")
            gen_nombre = f"GEN_{partes[1]}" if len(partes) > 1 else GENERADORES[0]
            
            bits_input = input("Cantidad de bits a evaluar (Enter para 1,000,000): ")
            bits = int(bits_input) if bits_input.strip() else 1_000_000
            
            print("=" * 70)
            print(f"Iniciando evaluacion para {archivo_seleccionado}...")
            
            try:
                from Evaluacion.EVL_NIST_EDT import nist_evals
                
                # Le agregamos el nombre de la carpeta para que importlib sepa dónde buscar
                modulo_generador = f"{CARPETA_GENERADORES}.{gen_nombre}"
                
                nist_evals(ruta_archivo, modulo_generador, bits)
            
            except Exception as e:
                print(f"Error al ejecutar la evaluacion: {e}")
                print("Asegurate de que el archivo EVL_NIST_EDT.py este dentro de la carpeta 'Evaluacion'.")
                
            input("\nPresiona Enter para continuar...")
            
        elif opcion == opcion_regresar:
            break
        else:
            print("Opcion fuera de rango.")

def main():
    seed_actual = 2043379  # Seed predeterminada al arrancar el programa
    
    while True:
        print("=" * 70)
        print("MENU PRINCIPAL")
        print("=" * 70)
        print("1. Generar")
        print("2. Evaluar")
        print("3. Comparar")
        print("4. Salir")
        print("=" * 70)
        
        opcion = input("Selecciona una opcion: ")
        
        if opcion == "1":
            seed_actual = menu_generar(seed_actual)
        elif opcion == "2":
            menu_evaluar()
        elif opcion == "3":
            
            menu_comparar() # Reemplaza el bloque en construcción por esta llamada
        elif opcion == "4":
            print("Saliendo del programa...")
            break
        else:
            print("Opcion no valida. Intenta de nuevo.")

if __name__ == "__main__":
    main()