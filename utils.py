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
    """Inicializa los componentes del circuito interactivamente.

    Solicita las configuraciones de las cuatro impedancias (entrada y retroalimentación
    de cada op amp) en un flujo compacto:
      - Para cada impedancia: preguntar si es 'Solo resistencia' o 'Resistencia y capacitor'
      - Si es RC: preguntar si está en serie o paralelo con la resistencia
      - Luego pedir los valores (R y opcionalmente C)

    Devuelve símbolos, tupla de capacitores/símbolos, diccionario de valores y configs.
    """
    print("\n=== Configuración de los Amplificadores Operacionales ===")

    # Preparar estructuras donde guardaremos los datos
    op = {}

    for i in (1, 2):
        print(f"\n--- Amplificador Operacional {i} ---")
        # Entrada inversora
        print("\nEntrada inversora:")
        inp_type = None
        while inp_type not in (1, 2):
            try:
                print("1. Solo resistencia")
                print("2. Resistencia y capacitor")
                inp_type = int(input("Seleccione el tipo (1/2): "))
            except ValueError:
                print("Por favor ingrese 1 o 2.")
        if inp_type == 1:
            inp_cfg = {'type': 'R', 'config': None}
            R_in = get_user_input("R (Ω): ")
            C_in = 0
        else:
            # RC
            rc_cfg = None
            while rc_cfg not in (1, 2):
                try:
                    print("\nConfiguración R-C:")
                    print("1. Serie")
                    print("2. Paralelo")
                    rc_cfg = int(input("Seleccione la configuración (1/2): "))
                except ValueError:
                    print("Por favor ingrese 1 o 2.")
            inp_cfg = {'type': 'RC', 'config': rc_cfg}
            R_in = get_user_input("R (Ω): ")
            C_in = get_user_input("C (F, por ejemplo 1e-9): ", allow_zero=False)

        # Retroalimentación
        print("\nRetroalimentación:")
        fb_type = None
        while fb_type not in (1, 2):
            try:
                print("1. Solo resistencia")
                print("2. Resistencia y capacitor")
                fb_type = int(input("Seleccione el tipo (1/2): "))
            except ValueError:
                print("Por favor ingrese 1 o 2.")
        if fb_type == 1:
            fb_cfg = {'type': 'R', 'config': None}
            R_fb = get_user_input("R (Ω): ")
            C_fb = 0
        else:
            fb_rc = None
            while fb_rc not in (1, 2):
                try:
                    print("\nConfiguración R-C:")
                    print("1. Serie")
                    print("2. Paralelo")
                    fb_rc = int(input("Seleccione la configuración (1/2): "))
                except ValueError:
                    print("Por favor ingrese 1 o 2.")
            fb_cfg = {'type': 'RC', 'config': fb_rc}
            R_fb = get_user_input("R (Ω): ")
            C_fb = get_user_input("C (F, por ejemplo 1e-9): ", allow_zero=False)

        op[i] = {
            'input': {'cfg': inp_cfg, 'R': R_in, 'C': C_in},
            'fb': {'cfg': fb_cfg, 'R': R_fb, 'C': C_fb}
        }

    # Definir símbolos (mantener compatibilidad con el resto del código)
    R1, R2, R3, R4 = symbols('R1 R2 R3 R4')
    C1, C2, Ci1, Ci2 = symbols('C1 C2 Ci1 Ci2')

    # Mapear valores a símbolos
    valores = {
        R1: op[1]['input']['R'],
        R2: op[1]['fb']['R'],
        R3: op[2]['input']['R'],
        R4: op[2]['fb']['R'],
        C1: op[1]['fb']['C'],
        C2: op[2]['fb']['C'],
        Ci1: op[1]['input']['C'],
        Ci2: op[2]['input']['C']
    }

    configs = {
        'config1': op[1]['fb']['cfg'],
        'config2': op[2]['fb']['cfg'],
        'input1': op[1]['input']['cfg'],
        'input2': op[2]['input']['cfg']
    }

    print("\nValores configurados:")
    print(f"R1 = {valores[R1]/1e3:.2f} kΩ")
    print(f"R2 = {valores[R2]/1e3:.2f} kΩ")
    print(f"C1 = {valores[C1]*1e9:.2f} nF")
    print(f"R3 = {valores[R3]/1e3:.2f} kΩ")
    print(f"R4 = {valores[R4]/1e3:.2f} kΩ")
    print(f"C2 = {valores[C2]*1e9:.2f} nF")
    if valores[Ci1] > 0:
        print(f"Ci1 = {valores[Ci1]*1e9:.2f} nF")
    if valores[Ci2] > 0:
        print(f"Ci2 = {valores[Ci2]*1e9:.2f} nF")

    print("\nConfiguración completada.")
    return (R1, R2, R3, R4), (Ci1, Ci2, C1, C2), valores, configs


def configure_plots():
    """Configura el estilo de las gráficas."""
    plt.style.use('default')
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.linestyle'] = '--'
    plt.rcParams['grid.alpha'] = 0.5