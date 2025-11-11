"""
Análisis de equivalentes Thévenin para circuitos con amplificadores operacionales.
"""
import numpy as np
import matplotlib.pyplot as plt
from utils import init_components, configure_plots

def calc_thevenin_entrada(R1, R2, C1, Ci, s, config, input_config):
    """Calcula el equivalente Thévenin desde la entrada.

    config: dict con keys 'type' ('R' o 'RC') y 'config' (1=serie,2=paralelo) para la red de
    retroalimentación (R2/C1).
    input_config: dict similar para la combinación R1/Ci en la entrada.
    """
    # Impedancia de la red de retroalimentación (carga vista desde el nodo de entrada)
    if config['type'] == 'R' or C1 == 0:
        Z_load = R2
    else:
        Zc1 = 1/(s*C1)
        if config['config'] == 1:  # Serie
            Z_load = R2 + Zc1
        else:  # Paralelo
            Z_load = (R2 * Zc1) / (R2 + Zc1)

    # Impedancia de la red de entrada R1/Ci
    if input_config is None or input_config['type'] == 'R' or Ci == 0:
        Z_input = R1
    else:
        Zci = 1/(s*Ci)
        if input_config['config'] == 1:  # Serie
            Z_input = R1 + Zci
        else:  # Paralelo
            Z_input = (R1 * Zci) / (R1 + Zci)

    # Voltaje Thévenin y resistencia equivalente (divisor entre Z_input y Z_load)
    V_th = Z_load / (Z_input + Z_load)
    Z_th = (Z_input * Z_load) / (Z_input + Z_load)
    return V_th, Z_th

def calc_thevenin_salida(R3, R4, C2, s, config):
    """Calcula el equivalente Thévenin desde la salida.

    config: dict con keys 'type' ('R' o 'RC') y 'config' (1=serie,2=paralelo) cuando aplica.
    """
    if config['type'] == 'R' or C2 == 0:
        V_th = R4/(R3 + R4)
        Z_th = (R3 * R4)/(R3 + R4)
        return V_th, Z_th

    Z_C2 = 1/(s*C2)
    if config['config'] == 1:  # Serie
        Z_eq = R4 + Z_C2
        Z_th = (R3 * Z_eq)/(R3 + Z_eq)
        V_th = Z_eq/(R3 + Z_eq)
    else:  # Paralelo
        Z_RC = (R4 * Z_C2)/(R4 + Z_C2)
        Z_th = (R3 * Z_RC)/(R3 + Z_RC)
        V_th = R4/(R3 + R4 + Z_C2)
    return V_th, Z_th

def plot_thevenin_analysis(components=None, show_plots=False):
    """Realiza el análisis de Thévenin básico para cada op-amp y el sistema total."""
    if components is None:
        (R1, R2, R3, R4), (Ci1, Ci2, C1, C2), valores, configs = init_components()
    else:
        (R1, R2, R3, R4), (Ci1, Ci2, C1, C2), valores, configs = components
    
    print("\n=== PRIMER AMPLIFICADOR OPERACIONAL ===")
    print("Equivalente th entrada: Z1")
    print(f"Equivalente th salida: (Z2/Z1)*Vi1")
    
    print("\n=== SEGUNDO AMPLIFICADOR OPERACIONAL ===")
    print("Equivalente th entrada: Z3")
    print(f"Equivalente th salida: (Z4/Z3)*Vi2")
    
    print("\n=== SISTEMA TOTAL ===")
    print("Cascada de dos etapas:")
    print("- Salida op-amp 1 = (Z2/Z1)*Vi1")
    print("- Entrada op-amp 2 = Salida op-amp 1")
    print("- Salida op-amp 2 = (Z4/Z3)*Salida op-amp 1 = (Z4/Z3)*(Z2/Z1)*Vi1")
    
    print("\nDonde:")
    print("Z1: Impedancia de entrada del primer op amp")
    print("Z2: Impedancia de retroalimentación del primer op amp")
    print("Z3: Impedancia de entrada del segundo op amp")
    print("Z4: Impedancia de retroalimentación del segundo op amp")
    print("Vi1: Voltaje de entrada del primer op amp")

if __name__ == '__main__':
    plot_thevenin_analysis()