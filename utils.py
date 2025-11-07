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

def init_components():
    """Inicializa los componentes del circuito."""
    R1, R2, R3, R4, R5, R6 = symbols('R1 R2 R3 R4 R5 R6')
    C1, C2 = symbols('C1 C2')
    
    valores = {
        R1: 10e3,  # 10 kΩ
        R2: 20e3,  # 20 kΩ
        R3: 15e3,  # 15 kΩ
        R4: 30e3,  # 30 kΩ
        R5: 25e3,  # 25 kΩ
        R6: 40e3,  # 40 kΩ
        C1: 100e-9,  # 100 nF
        C2: 47e-9   # 47 nF
    }
    
    return (R1, R2, R3, R4, R5, R6), (C1, C2), valores

def configure_plots():
    """Configura el estilo de las gráficas."""
    plt.style.use('seaborn-darkgrid')