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

def calc_individual_transfer_functions(R1, R2, R3, R4, Ci1, Ci2, C1, C2, s, configs):
    """Calcula las funciones de transferencia individuales y total."""
    # Primera etapa (primer amplificador)
    Z1 = calc_impedance(R2, C1, s, configs['config1'])
    input1_cfg = configs.get('input1', {'type': 'R', 'config': None})
    if input1_cfg['type'] == 'R' or Ci1 == 0:
        Z_in1 = R1
    else:
        Zc1 = 1/(s*Ci1)
        if input1_cfg['config'] == 1:  # Serie
            Z_in1 = R1 + Zc1
        else:  # Paralelo
            Z_in1 = (R1 * Zc1) / (R1 + Zc1)
    H1 = -Z1 / Z_in1
    
    # Segunda etapa (segundo amplificador)
    Z2 = calc_impedance(R4, C2, s, configs['config2'])
    input2_cfg = configs.get('input2', {'type': 'R', 'config': None})
    if input2_cfg['type'] == 'R' or Ci2 == 0:
        Z_in2 = R3
    else:
        Zc2 = 1/(s*Ci2)
        if input2_cfg['config'] == 1:
            Z_in2 = R3 + Zc2
        else:
            Z_in2 = (R3 * Zc2) / (R3 + Zc2)
    H2 = -Z2 / Z_in2
    
    # Función de transferencia total
    H_total = H1 * H2
    
    return H1, H2, H_total

def calc_transfer_function(R1, R2, R3, R4, Ci1, Ci2, C1, C2, s, configs):
    """Calcula la función de transferencia del sistema."""
    _, _, H_total = calc_individual_transfer_functions(R1, R2, R3, R4, Ci1, Ci2, C1, C2, s, configs)
    return H_total

def get_numeric_tf(H, valores, s):
    """Convierte la función de transferencia simbólica a numérica y normaliza los coeficientes."""
    H_num = H.subs(valores)
    num, den = H_num.as_numer_denom()
    
    # Obtener coeficientes
    num_coeff = [complex(x).real for x in Poly(num, s).all_coeffs()]
    den_coeff = [complex(x).real for x in Poly(den, s).all_coeffs()]
    
    # Normalizar coeficientes para evitar problemas numéricos
    max_num = max(abs(np.array(num_coeff)))
    max_den = max(abs(np.array(den_coeff)))
    
    if max_num > 0:
        num_coeff = [n/max_num for n in num_coeff]
    if max_den > 0:
        den_coeff = [d/max_den for d in den_coeff]
    
    # Eliminar coeficientes muy pequeños que pueden causar problemas numéricos
    num_coeff = np.array(num_coeff)
    den_coeff = np.array(den_coeff)
    num_coeff[abs(num_coeff) < 1e-10] = 0
    den_coeff[abs(den_coeff) < 1e-10] = 0
    
    return control.TransferFunction(num_coeff, den_coeff)

def analyze_stability(sys):
    """Analiza la estabilidad del sistema y proporciona información detallada."""
    # Analizar polos
    poles = control.poles(sys)
    stable = all(pole.real < 0 for pole in poles)
    
    print("\nAnálisis de estabilidad:")
    print(f"Estado: Sistema {'estable' if stable else 'inestable'}")
    
    # Mostrar detalles de los polos
    print("\nPolos del sistema y su efecto en la estabilidad:")
    for i, pole in enumerate(poles, 1):
        print(f"Polo {i}: {pole:.3f}")
        if pole.real < 0:
            print(f"  - Estable: parte real negativa ({pole.real:.3f})")
        else:
            print(f"  - Inestable: parte real positiva ({pole.real:.3f})")
        
        if abs(pole.imag) > 0:
            freq_nat = abs(pole)
            damping = -pole.real/freq_nat
            print(f"  - Frecuencia natural: {freq_nat:.2f} rad/s")
            print(f"  - Coeficiente de amortiguamiento: {damping:.3f}")
    
    # Intentar calcular márgenes de estabilidad
    try:
        gm, pm, wg, wp = control.margin(sys)
        print("\nMárgenes de estabilidad:")
        if np.isfinite(gm):
            print(f"Margen de ganancia: {gm:.2f} dB a {wg:.2f} rad/s")
        else:
            print("Margen de ganancia: No cruza por -180°")
            
        if np.isfinite(pm):
            print(f"Margen de fase: {pm:.2f} grados a {wp:.2f} rad/s")
        else:
            print("Margen de fase: No cruza por 0dB")
            
    except Exception as e:
        print("\nNo se pudieron calcular los márgenes de estabilidad")
        print("Esto puede ocurrir si el sistema:")
        print("- No tiene cruces de fase o ganancia")
        print("- Tiene una respuesta en frecuencia compleja")
    
    # Recomendaciones para estabilización si es inestable
    if not stable:
        print("\nRecomendaciones para estabilización:")
        print("1. Revisar las ganancias del sistema (valores de R)")
        print("2. Considerar agregar compensación de fase")
        print("3. Verificar los valores de los componentes RC")
        print("4. Evaluar la posibilidad de realimentación adicional")
    
    return stable

def analyze_transfer_function_no_plots(components=None):
    """Realiza el análisis de la función de transferencia sin mostrar gráficas."""
    if components is None:
        (R1, R2, R3, R4), (Ci1, Ci2, C1, C2), valores, configs = init_components()
    else:
        (R1, R2, R3, R4), (Ci1, Ci2, C1, C2), valores, configs = components
    s = symbols('s')

    # Calcular funciones de transferencia individuales y total
    H1, H2, H_total = calc_individual_transfer_functions(R1, R2, R3, R4, Ci1, Ci2, C1, C2, s, configs)
    
    print("\n=== ANÁLISIS INDIVIDUAL: PRIMER AMPLIFICADOR OPERACIONAL ===")
    print(f"H1(s) = {H1}")
    
    # Sistema individual del primer op-amp
    sys1 = get_numeric_tf(H1, valores, s)
    zeros1 = control.zeros(sys1)
    poles1 = control.poles(sys1)
    
    print("\nCeros:")
    for i, zero in enumerate(zeros1, 1):
        print(f"  z{i} = {zero:.2f}")
    
    print("\nPolos:")
    for i, pole in enumerate(poles1, 1):
        print(f"  p{i} = {pole:.2f}")
    
    print("\nAnálisis de estabilidad:")
    analyze_stability(sys1)
    
    print("\n" + "="*60)
    print("\n=== ANÁLISIS INDIVIDUAL: SEGUNDO AMPLIFICADOR OPERACIONAL ===")
    print(f"H2(s) = {H2}")
    
    # Sistema individual del segundo op-amp
    sys2 = get_numeric_tf(H2, valores, s)
    zeros2 = control.zeros(sys2)
    poles2 = control.poles(sys2)
    
    print("\nCeros:")
    for i, zero in enumerate(zeros2, 1):
        print(f"  z{i} = {zero:.2f}")
    
    print("\nPolos:")
    for i, pole in enumerate(poles2, 1):
        print(f"  p{i} = {pole:.2f}")
    
    print("\nAnálisis de estabilidad:")
    analyze_stability(sys2)
    
    print("\n" + "="*60)
    print("\n=== FUNCIÓN DE TRANSFERENCIA TOTAL (AMBOS AMPLIFICADORES) ===")
    print(f"H_total(s) = {H_total}")

    # Convertir a sistema numérico para análisis
    sys_total = get_numeric_tf(H_total, valores, s)
    
    # Análisis de polos y ceros
    zeros_total = control.zeros(sys_total)
    poles_total = control.poles(sys_total)
    
    print("\nCeros:")
    for i, zero in enumerate(zeros_total, 1):
        print(f"  z{i} = {zero:.2f}")
    
    print("\nPolos:")
    for i, pole in enumerate(poles_total, 1):
        print(f"  p{i} = {pole:.2f}")
    
    # Análisis de estabilidad
    print("\nAnálisis de estabilidad:")
    analyze_stability(sys_total)
    
    return sys1, sys2, sys_total  # Retornamos los tres sistemas para usarlos en las gráficas

def plot_transfer_function_analysis(components=None, show_plots=False):
    """Realiza y grafica el análisis completo de la función de transferencia."""
    # Esta función ya no genera gráficas
    pass

if __name__ == '__main__':
    plot_transfer_function_analysis()