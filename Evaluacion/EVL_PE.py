import math
import numpy as np
from collections import Counter

# ═══════════════════════════════════════════════════════════════════════════════
#  EVL_PE.py — Pruebas Estadísticas para Números Rectangulares
#  Basadas en el material del curso (Promedios, KS, Frecuencias,
#  Distancias, Series, Póker)
#
#  POR QUÉ NO SE APLICAN DIRECTO SOBRE 1,000,000 DE FLOTANTES
#  ────────────────────────────────────────────────────────────
#  Las pruebas del curso fueron diseñadas para muestras pequeñas (N ≈ 10-30).
#  El estadístico chi-cuadrada que usan Frecuencias, Distancias y Series
#  crece proporcionalmente a N:
#
#      X²o = (1/FE) · Σ(FOi - FEi)²   donde   FE = N/n
#
#  Con N=10  y n=4:  FE = 2.5    → diferencias de ±1 producen X²o ≈ 1.6
#  Con N=1M  y n=4:  FE = 250,000 → diferencias de ±100 producen X²o ≈ 1,000,000
#
#  Resultado: con N grande cualquier generador falla, incluso uno perfecto,
#  porque el test detecta desviaciones estadísticamente significativas pero
#  prácticamente irrelevantes (un sesgo de 0.001% ya es "significativo").
#
#  SOLUCIÓN: ESQUEMA DE MÚLTIPLES BLOQUES
#  ───────────────────────────────────────
#  Análogo a cómo NIST SP800-22 maneja secuencias largas:
#
#    1. Dividir los flotantes en K bloques de tamaño SAMPLE_SIZE.
#    2. Aplicar cada prueba a cada bloque de forma independiente.
#    3. Contar qué proporción de bloques pasa la prueba.
#    4. Criterio final: ACEPTADO si >= PASS_THRESHOLD de bloques pasan.
#
#  Con SAMPLE_SIZE=1000 y 1,000,000 flotantes → 1,000 bloques evaluados.
#  Cada bloque se evalúa con los mismos criterios del curso.
#  El resultado final es una proporción, no un único estadístico.
#
#  PARÁMETROS AJUSTABLES
#  ─────────────────────
SAMPLE_SIZE    = 1_000   # Tamaño de cada bloque (N del curso)
PASS_THRESHOLD = 0.90    # Proporción mínima de bloques que deben pasar
# ═══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
#  TABLAS DE VALORES CRÍTICOS
# ─────────────────────────────────────────────────────────────────────

_KS_TABLA = {
    1: 0.97500, 2: 0.84189, 3: 0.70760, 4: 0.62394, 5: 0.56328,
    6: 0.51926, 7: 0.48342, 8: 0.45427, 9: 0.43001, 10: 0.40925,
    11: 0.39122, 12: 0.37543, 13: 0.35143, 14: 0.34890, 15: 0.33760,
    16: 0.32733, 17: 0.31796, 18: 0.30936, 19: 0.30143, 20: 0.29408,
}

_CHI2_TABLA = {
    1: 3.84146, 2: 5.99147, 3: 7.81473, 4: 9.48773,
    5: 11.07050, 6: 12.59159, 7: 14.06714, 8: 15.50731,
}

_Z_TABLA = 1.96

# ─────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────

def _chi2_critico(gl: int) -> float:
    return _CHI2_TABLA.get(gl, 3.84146)

def _ks_critico(N: int, alpha: float = 0.05) -> float:
    if N in _KS_TABLA:
        return _KS_TABLA[N]
    if alpha == 0.10:
        return 1.22 / math.sqrt(N)
    if alpha == 0.01:
        return 1.63 / math.sqrt(N)
    return 1.36 / math.sqrt(N)

def _digitos_decimales(x: float, n: int = 5) -> list:
    s = f"{x:.{n}f}".replace("0.", "").replace(".", "")[:n]
    return [int(c) for c in s]

def _bloques(xi: np.ndarray, size: int) -> list:
    """Divide xi en bloques de tamaño size, descartando el residuo."""
    n_bloques = len(xi) // size
    return [xi[i * size:(i + 1) * size] for i in range(n_bloques)]

def _resultado_multibloque(nombre, fn_prueba, bloques, threshold, **kwargs):
    """
    Aplica fn_prueba a cada bloque y agrega resultados.
    Reporta proporción de bloques que pasan y veredicto final.
    """
    aprobados    = 0
    estadisticos = []

    for bloque in bloques:
        r = fn_prueba(bloque, **kwargs)
        estadisticos.append(r["estadistico"])
        if r["aprobado"]:
            aprobados += 1

    proporcion  = aprobados / len(bloques)
    aprobado    = proporcion >= threshold
    critico_ref = fn_prueba(bloques[0], **kwargs)["critico"]

    return {
        "prueba":      nombre,
        "N_total":     len(bloques) * len(bloques[0]),
        "n_bloques":   len(bloques),
        "sample_size": len(bloques[0]),
        "estadistico": float(np.mean(estadisticos)),
        "critico":     critico_ref,
        "aprobados":   aprobados,
        "proporcion":  proporcion,
        "threshold":   threshold,
        "aprobado":    aprobado,
    }

# ─────────────────────────────────────────────────────────────────────
#  PRUEBAS INDIVIDUALES (operan sobre un bloque de tamaño SAMPLE_SIZE)
# ─────────────────────────────────────────────────────────────────────

def _promedios_bloque(xi, alpha=0.05):
    N     = len(xi)
    x_bar = float(np.mean(xi))
    z0    = abs((x_bar - 0.5) * math.sqrt(N) / math.sqrt(1 / 12))
    return {"estadistico": z0, "critico": _Z_TABLA, "aprobado": z0 < _Z_TABLA}

def _ks_bloque(xi, alpha=0.05):
    N      = len(xi)
    xi_ord = np.sort(xi)
    D_max  = 0.0
    for i, x in enumerate(xi_ord, start=1):
        D_max = max(D_max, abs(x - i / N), abs(x - (i - 1) / N))
    critico = _ks_critico(N, alpha)
    return {"estadistico": D_max, "critico": critico, "aprobado": D_max < critico}

def _frecuencias_bloque(xi, n=4, alpha=0.05):
    N  = len(xi)
    FE = N / n
    FO = np.zeros(n, dtype=int)
    for x in xi:
        FO[min(int(x * n), n - 1)] += 1
    x2_0    = float((1 / FE) * np.sum((FO - FE) ** 2))
    critico = _chi2_critico(n - 1)
    return {"estadistico": x2_0, "critico": critico, "aprobado": x2_0 < critico}

def _distancias_bloque(xi, alpha=0.05):
    # 1. Encontrar los tamaños de los huecos (gaps) entre apariciones del evento.
    # Evento: el número cae en el intervalo [0.0, 0.1), que tiene probabilidad p = 0.1
    gaps = []
    current_gap = 0
    for x in xi:
        if x < 0.1:
            gaps.append(current_gap)
            current_gap = 0
        else:
            current_gap += 1
            
    N_gaps = len(gaps)
    
    # Seguridad: si el bloque no tuvo suficientes huecos para evaluar
    if N_gaps == 0:
        return {"estadistico": 0.0, "critico": _chi2_critico(1), "aprobado": True}
        
    # 2. Contar frecuencias observadas (FO)
    FO_dict = {}
    for g in gaps:
        FO_dict[g] = FO_dict.get(g, 0) + 1
        
    max_gap = max(FO_dict.keys())
    
    # 3. Calcular frecuencias esperadas (FE) según la distribución geométrica
    FE_dict = {}
    for i in range(max_gap + 1):
        if i < max_gap:
            FE_dict[i] = N_gaps * 0.1 * (0.9 ** i)
        else:
            FE_dict[i] = N_gaps * (0.9 ** i) # El acumulado de la cola
            
    # 4. Agrupar categorías para cumplir la condición FE >= 5
    g1 = [i for i in range(max_gap + 1) if FE_dict[i] < 5]
    g2 = [i for i in range(max_gap + 1) if FE_dict[i] >= 5]
    
    FE_g1 = sum(FE_dict[i] for i in g1)
    FO_g1 = sum(FO_dict.get(i, 0) for i in g1)
    FE_g2 = sum(FE_dict[i] for i in g2)
    FO_g2 = sum(FO_dict.get(i, 0) for i in g2)
    
    # 5. Calcular Chi-cuadrada
    t1 = ((FO_g1 - FE_g1) ** 2) / FE_g1 if FE_g1 > 0 else 0
    t2 = ((FO_g2 - FE_g2) ** 2) / FE_g2 if FE_g2 > 0 else 0
    x2_0 = t1 + t2
    
    critico = _chi2_critico(1)
    return {"estadistico": x2_0, "critico": critico, "aprobado": x2_0 < critico}

def _series_bloque(xi, n=2, alpha=0.05):
    N       = len(xi)
    n_pares = N - 1
    FE      = n_pares / (n ** 2)
    FO      = np.zeros((n, n), dtype=int)
    for k in range(n_pares):
        ci = min(int(xi[k] * n),     n - 1)
        cj = min(int(xi[k + 1] * n), n - 1)
        FO[ci, cj] += 1
    x2_0    = float((n ** 2 / n_pares) * np.sum((FO - FE) ** 2))
    critico = _chi2_critico(n ** 2 - 1)
    return {"estadistico": x2_0, "critico": critico, "aprobado": x2_0 < critico}

_POKER_CATEGORIAS = [
    ("Todos diferentes", 0.30240),
    ("Un par",           0.50400),
    ("Dos pares",        0.10800),
    ("Tercia",           0.07200),
    ("Full",             0.00900),
    ("Poker",            0.00450),
    ("Quintilla",        0.00010),
]

def _clasificar_poker(digitos):
    freqs = sorted(Counter(digitos).values(), reverse=True)
    if freqs[0] == 5: return "Quintilla"
    if freqs[0] == 4: return "Poker"
    if freqs[0] == 3 and len(freqs) > 1 and freqs[1] == 2: return "Full"
    if freqs[0] == 3: return "Tercia"
    if freqs[0] == 2 and len(freqs) > 1 and freqs[1] == 2: return "Dos pares"
    if freqs[0] == 2: return "Un par"
    return "Todos diferentes"

def _poker_bloque(xi, alpha=0.05):
    N       = len(xi)
    FO_dict = {cat: 0 for cat, _ in _POKER_CATEGORIAS}
    for x in xi:
        FO_dict[_clasificar_poker(_digitos_decimales(x, 5))] += 1
    FE_dict = {cat: p * N for cat, p in _POKER_CATEGORIAS}

    g1 = [(cat, p) for cat, p in _POKER_CATEGORIAS
          if FO_dict[cat] > 0 and FE_dict[cat] < 5]
    g2 = [(cat, p) for cat, p in _POKER_CATEGORIAS
          if FE_dict[cat] >= 5]

    FE_g1 = sum(FE_dict[cat] for cat, _ in g1)
    FO_g1 = sum(FO_dict[cat] for cat, _ in g1)
    FE_g2 = sum(FE_dict[cat] for cat, _ in g2)
    FO_g2 = sum(FO_dict[cat] for cat, _ in g2)

    t1   = (FO_g1 - FE_g1) ** 2 / FE_g1 if FE_g1 > 0 else 0
    t2   = (FO_g2 - FE_g2) ** 2 / FE_g2 if FE_g2 > 0 else 0
    x2_0 = t1 + t2
    critico = _chi2_critico(1)
    return {"estadistico": x2_0, "critico": critico, "aprobado": x2_0 < critico}

# ─────────────────────────────────────────────────────────────────────
#  API PÚBLICA — misma firma que antes, compatible con EVL_NIST_EDT.py
# ─────────────────────────────────────────────────────────────────────

def aplicar_todas(xi,
                  alpha=0.05,
                  n_frecuencias=4,
                  n_series=2,
                  sample_size=SAMPLE_SIZE,
                  pass_threshold=PASS_THRESHOLD) -> dict:
    """
    Aplica las 6 pruebas estadísticas del curso a xi usando bloques.
    Compatible con EVL_NIST_EDT.py — misma firma que la versión anterior.

    Parámetros
    ----------
    xi              : array de flotantes en [0, 1]
    alpha           : nivel de significancia (default 0.05)
    n_frecuencias   : intervalos para Frecuencias (default 4)
    n_series        : divisiones por eje para Series (default 2)
    sample_size     : tamaño de cada bloque (default 1,000)
    pass_threshold  : fracción mínima de bloques que deben pasar (default 0.90)
    """
    xi    = np.asarray(xi, dtype=float)
    bloques_grandes = _bloques(xi, 1000)  # Para Promedios y KS
    bloques_medios  = _bloques(xi, 100)   # Para Frecuencias y Series
    bloques_chicos  = _bloques(xi, 10)    # Para Distancias y Poker

    return {
        "promedios":   _resultado_multibloque(
                           "Promedios", _promedios_bloque, bloques_grandes,
                           pass_threshold, alpha=alpha),
        "ks":          _resultado_multibloque(
                           "Kolmogorov-Smirnov", _ks_bloque, bloques_grandes,
                           pass_threshold, alpha=alpha),
        "frecuencias": _resultado_multibloque(
                           "Frecuencias", _frecuencias_bloque, bloques_medios,
                           pass_threshold, n=n_frecuencias, alpha=alpha),
        "distancias":  _resultado_multibloque(
                           "Distancias", _distancias_bloque, bloques_chicos,
                           pass_threshold, alpha=alpha),
        "series":      _resultado_multibloque(
                           "Series", _series_bloque, bloques_medios,
                           pass_threshold, n=n_series, alpha=alpha),
        "poker":       _resultado_multibloque(
                           "Poker", _poker_bloque, bloques_chicos,
                           pass_threshold, alpha=alpha),
    }


# ─────────────────────────────────────────────────────────────────────
#  EJEMPLO
# ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    rng = np.random.default_rng(42)
    xi  = rng.uniform(0, 1, size=1_000_000)

    resultados = aplicar_todas(xi)

    print(f"\n{'PRUEBA':<25} {'PROM.ESTAD.':>12} {'CRÍTICO':>9} "
          f"{'APROBADOS':>11} {'PROPORCIÓN':>11} {'RESULTADO':>12}")
    print("─" * 85)
    for r in resultados.values():
        estado = "ACEPTADO" if r["aprobado"] else "RECHAZADO"
        print(f"{r['prueba']:<25} {r['estadistico']:>12.5f} {r['critico']:>9.5f} "
              f"  {r['aprobados']:>4}/{r['n_bloques']:<5} "
              f"{r['proporcion']:>10.1%}   {estado}")