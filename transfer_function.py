"""
Análisis de la función de transferencia y estabilidad del circuito.
"""
import numpy as np
import matplotlib.pyplot as plt
from sympy import symbols, Poly
import control
from utils import init_components, configure_plots

def calc_impedance(R, C, s, config):
    """Calcula la impedancia según la configuración."""
    if config['type'] == 'R':
        return R
    else:  # type == 'RC'
        Z_C = 1/(s*C)
        if config['config'] == 1:  # Serie
            return R + Z_C
        else:  # Paralelo
            return (R * Z_C)/(R + Z_C)

def calc_individual_transfer_functions(R1, R2, R3, R4, Ci, C1, C2, s, configs):
    """Calcula las funciones de transferencia individuales y total."""
    # Primera etapa (primer amplificador)
    Z1 = calc_impedance(R2, C1, s, configs['config1'])
    if Ci > 0:  # Si hay capacitor en la entrada
        Z_in = (R1 * (1/(s*Ci)))/(R1 + 1/(s*Ci))  # R1 y Ci en paralelo
        H1 = -Z1/Z_in
    else:
        H1 = -Z1/R1
    
    # Segunda etapa (segundo amplificador)
    Z2 = calc_impedance(R4, C2, s, configs['config2'])
    H2 = -Z2/R3
    
    # Función de transferencia total
    H_total = H1 * H2
    
    return H1, H2, H_total

def calc_transfer_function(R1, R2, R3, R4, Ci, C1, C2, s, configs):
    """Calcula la función de transferencia del sistema."""
    _, _, H_total = calc_individual_transfer_functions(R1, R2, R3, R4, Ci, C1, C2, s, configs)
    return H_total
    
    # Segunda etapa (segundo amplificador)
    Z2 = calc_impedance(R4, C2, s, configs['config2'])
    H2 = -Z2/R3
    
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
    poles = control.poles(sys)
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
    (R1, R2, R3, R4), (Ci, C1, C2), valores, configs = init_components()
    s = symbols('s')

    # Calcular funciones de transferencia individuales y total
    H1, H2, H_total = calc_individual_transfer_functions(R1, R2, R3, R4, Ci, C1, C2, s, configs)
    
    print("\n=== Funciones de Transferencia ===")
    print("\nPrimer Amplificador Operacional:")
    print(f"H1(s) = {H1}")
    
    print("\nSegundo Amplificador Operacional:")
    print(f"H2(s) = {H2}")
    
    print("\nFunción de Transferencia Total:")
    print(f"H_total(s) = {H_total}")

    # Convertir a sistema numérico para análisis
    sys = get_numeric_tf(H_total, valores, s)
    
    # Análisis de polos y ceros
    zeros = control.zeros(sys)
    poles = control.poles(sys)
    
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