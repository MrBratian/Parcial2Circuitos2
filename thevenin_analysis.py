"""
Análisis de equivalentes Thévenin para circuitos con amplificadores operacionales.
"""
import numpy as np
import matplotlib.pyplot as plt
from utils import init_components, configure_plots

def calc_thevenin_entrada(R1, R2, C1, s):
    """Calcula el equivalente Thévenin desde la entrada."""
    Z_C1 = 1/(s*C1)
    Z_th = (R1 * (R2 + Z_C1))/(R1 + R2 + Z_C1)
    V_th = R2/(R1 + R2 + Z_C1)
    return V_th, Z_th

def calc_thevenin_salida(R5, R6, C2, s):
    """Calcula el equivalente Thévenin desde la salida."""
    Z_C2 = 1/(s*C2)
    Z_th = (R5 * (R6 + Z_C2))/(R5 + R6 + Z_C2)
    V_th = R6/(R5 + R6 + Z_C2)
    return V_th, Z_th

def plot_thevenin_analysis():
    """Realiza y grafica el análisis de Thévenin completo."""
    configure_plots()
    (R1, R2, R3, R4, R5, R6), (C1, C2), valores = init_components()
    
    # Análisis en frecuencia
    freq = np.logspace(0, 5, 1000)
    w = 2*np.pi*freq
    
    # Entrada
    Z_th_mag = []
    Z_th_phase = []
    for f in freq:
        V_th, Z_th = calc_thevenin_entrada(
            valores[R1], valores[R2], valores[C1], 2*np.pi*f*1j
        )
        Z_th_mag.append(abs(Z_th))
        Z_th_phase.append(np.angle(Z_th, deg=True))
    
    # Salida
    Z_th_salida_mag = []
    Z_th_salida_phase = []
    for f in freq:
        V_th, Z_th = calc_thevenin_salida(
            valores[R5], valores[R6], valores[C2], 2*np.pi*f*1j
        )
        Z_th_salida_mag.append(abs(Z_th))
        Z_th_salida_phase.append(np.angle(Z_th, deg=True))
    
    # Gráficas
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # Entrada
    ax1.semilogx(freq, Z_th_mag)
    ax1.set_title('Magnitud Z_th Entrada')
    ax1.set_xlabel('Frecuencia (Hz)')
    ax1.set_ylabel('|Z_th| (Ω)')
    ax1.grid(True)
    
    ax2.semilogx(freq, Z_th_phase)
    ax2.set_title('Fase Z_th Entrada')
    ax2.set_xlabel('Frecuencia (Hz)')
    ax2.set_ylabel('Fase (grados)')
    ax2.grid(True)
    
    # Salida
    ax3.semilogx(freq, Z_th_salida_mag)
    ax3.set_title('Magnitud Z_th Salida')
    ax3.set_xlabel('Frecuencia (Hz)')
    ax3.set_ylabel('|Z_th| (Ω)')
    ax3.grid(True)
    
    ax4.semilogx(freq, Z_th_salida_phase)
    ax4.set_title('Fase Z_th Salida')
    ax4.set_xlabel('Frecuencia (Hz)')
    ax4.set_ylabel('Fase (grados)')
    ax4.grid(True)
    
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    plot_thevenin_analysis()