"""
Análisis de la función de transferencia y estabilidad del circuito.
"""
import numpy as np
import matplotlib.pyplot as plt
from sympy import symbols, Poly
import control
from utils import init_components, configure_plots

def calc_transfer_function(R1, R2, R5, R6, C1, C2, s):
    """Calcula la función de transferencia del sistema."""
    # Primera etapa
    Z_C1 = 1/(s*C1)
    H1 = -R2/R1 * (1/(1 + s*R2*C1))
    
    # Segunda etapa
    Z_C2 = 1/(s*C2)
    H2 = -R6/R5 * (1/(1 + s*R6*C2))
    
    return H1 * H2

def get_numeric_tf(H, valores, s):
    """Convierte la función de transferencia simbólica a numérica."""
    H_num = H.subs(valores)
    num, den = H_num.as_numer_denom()
    num_coeff = [complex(x).real for x in Poly(num, s).all_coeffs()]
    den_coeff = [complex(x).real for x in Poly(den, s).all_coeffs()]
    return control.TransferFunction(num_coeff, den_coeff)

def analyze_stability(sys):
    """Analiza la estabilidad del sistema."""
    poles = control.pole(sys)
    stable = all(pole.real < 0 for pole in poles)
    gm, pm, wg, wp = control.margin(sys)
    
    print("Análisis de estabilidad:")
    print(f"Sistema {'estable' if stable else 'inestable'}")
    print(f"Margen de ganancia: {gm:.2f} dB")
    print(f"Margen de fase: {pm:.2f} grados")
    print(f"Frecuencia de cruce de ganancia: {wg:.2f} rad/s")
    print(f"Frecuencia de cruce de fase: {wp:.2f} rad/s")
    
    return stable, gm, pm, wg, wp

def plot_transfer_function_analysis():
    """Realiza y grafica el análisis completo de la función de transferencia."""
    configure_plots()
    (R1, R2, R3, R4, R5, R6), (C1, C2), valores = init_components()
    s = symbols('s')
    
    # Calcular función de transferencia
    H = calc_transfer_function(R1, R2, R5, R6, C1, C2, s)
    sys = get_numeric_tf(H, valores, s)
    
    # Análisis de polos y ceros
    zeros = control.zero(sys)
    poles = control.pole(sys)
    
    print("Ceros del sistema:")
    for i, zero in enumerate(zeros, 1):
        print(f"z{i} = {zero:.2f}")
    
    print("\nPolos del sistema:")
    for i, pole in enumerate(poles, 1):
        print(f"p{i} = {pole:.2f}")
    
    # Gráficas
    plt.figure(figsize=(15, 5))
    
    plt.subplot(121)
    control.pzmap(sys, plot=True)
    plt.title('Diagrama de Polos y Ceros')
    plt.grid(True)
    
    plt.subplot(122)
    control.bode(sys, plot=True)
    plt.title('Diagrama de Bode')
    
    plt.tight_layout()
    plt.show()
    
    # Análisis de estabilidad
    analyze_stability(sys)

if __name__ == '__main__':
    plot_transfer_function_analysis()