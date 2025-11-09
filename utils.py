"""
Utilidades para el análisis de circuitos con amplificadores operacionales.
"""
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal
from sympy import symbols, solve, expand, simplify, limit, Poly
from sympy.abc import s
import control
from control import TransferFunction

def get_user_input(prompt, allow_zero=False):
    """Obtiene entrada del usuario con validación.

    - allow_zero: si True permite que el usuario ingrese 0 (útil para capacitores ausentes)
    """
    while True:
        try:
            value = float(input(prompt))
            if allow_zero:
                if value < 0:
                    print("El valor no puede ser negativo.")
                    continue
            else:
                if value <= 0:
                    print("El valor debe ser positivo.")
                    continue
            return value
        except ValueError:
            print("Por favor, ingrese un número válido.")

def get_yes_no(prompt):
    """Pregunta sí/no y devuelve True/False."""
    while True:
        resp = input(prompt + " (s/n): ").strip().lower()
        if resp in ('s', 'si'):
            return True
        if resp in ('n', 'no'):
            return False
        print("Por favor responda 's' o 'n'.")

def get_impedance_type(stage_name):
    """Obtiene el tipo de impedancia del amplificador."""
    while True:
        print(f"\nImpedancia de retroalimentación para {stage_name}:")
        print("1. Solo resistencia")
        print("2. Resistencia y capacitor")
        try:
            choice = int(input("Seleccione el tipo (1/2): "))
            if choice in [1, 2]:
                if choice == 1:
                    return {'type': 'R', 'config': None}
                else:
                    while True:
                        print("\nConfiguración R-C:")
                        print("1. Serie")
                        print("2. Paralelo")
                        rc_choice = int(input("Seleccione la configuración (1/2): "))
                        if rc_choice in [1, 2]:
                            return {'type': 'RC', 'config': rc_choice}
                        print("Por favor, seleccione 1 o 2.")
            else:
                print("Por favor, seleccione 1 o 2.")
        except ValueError:
            print("Por favor, ingrese un número válido.")

def init_components():
    """Inicializa los componentes del circuito interactivamente."""
    print("\n=== Configuración del Primer Amplificador Operacional ===")
    
    # Primer amplificador
    print("\nEntrada inversora:")
    R1_val = get_user_input("R1 (Ω, por ejemplo 10000 para 10k): ")
    has_C_input = get_yes_no("¿La entrada inversora tiene capacitor?")
    C_input_val = get_user_input("Valor del capacitor de entrada (F): ", allow_zero=False) if has_C_input else 0
    
    print("\nRetroalimentación:")
    config1 = get_impedance_type("Primer Amplificador")
    R2_val = get_user_input("R2 (Ω): ")
    C1_val = 0 if config1['type'] == 'R' else get_user_input("C1 (F, por ejemplo 1e-9): ", allow_zero=False)
    
    print("\n=== Configuración del Segundo Amplificador Operacional ===")
    
    # Segundo amplificador
    print("\nEntrada inversora:")
    R3_val = get_user_input("R3 (Ω): ")
    
    print("\nRetroalimentación:")
    config2 = get_impedance_type("Segundo Amplificador")
    R4_val = get_user_input("R4 (Ω): ")
    C2_val = 0 if config2['type'] == 'R' else get_user_input("C2 (F, por ejemplo 1e-9): ", allow_zero=False)
    
    # Definir símbolos
    R1, R2, R3, R4 = symbols('R1 R2 R3 R4')
    C1, C2, Ci = symbols('C1 C2 Ci')  # Ci para el capacitor de entrada
    
    valores = {
        R1: R1_val,
        R2: R2_val,
        R3: R3_val,
        R4: R4_val,
        C1: C1_val,
        C2: C2_val,
        Ci: C_input_val
    }
    
    print("\nValores configurados:")
    print(f"R1 = {R1_val/1e3:.2f} kΩ")
    if C_input_val > 0:
        print(f"Ci = {C_input_val*1e9:.2f} nF")
    print(f"R2 = {R2_val/1e3:.2f} kΩ")
    print(f"C1 = {C1_val*1e9:.2f} nF")
    print(f"R3 = {R3_val/1e3:.2f} kΩ")
    print(f"R4 = {R4_val/1e3:.2f} kΩ")
    print(f"C2 = {C2_val*1e9:.2f} nF")
    
    configs = {
        'config1': config1,
        'config2': config2
    }
    
    print("\nConfiguración completada.")
    return (R1, R2, R3, R4), (Ci, C1, C2), valores, configs

def configure_plots():
    """Configura el estilo de las gráficas."""
    plt.style.use('default')
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.linestyle'] = '--'
    plt.rcParams['grid.alpha'] = 0.5