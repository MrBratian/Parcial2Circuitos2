"""
Análisis de respuestas temporales y en frecuencia.
"""
import numpy as np
import matplotlib.pyplot as plt
import control
from utils import init_components, configure_plots
from transfer_function import calc_transfer_function, get_numeric_tf
from sympy import symbols

def plot_time_responses(sys):
    """Grafica las respuestas temporales del sistema."""
    t = np.linspace(0, 0.01, 1000)
    
    # Calcular respuestas
    t_natural, y_natural = control.initial_response(sys, t)
    t_step, y_step = control.step_response(sys, t)
    t_impulse, y_impulse = control.impulse_response(sys, t)
    
    # Graficar
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12))
    
    ax1.plot(t_natural, y_natural)
    ax1.set_title('Respuesta Natural')
    ax1.set_xlabel('Tiempo (s)')
    ax1.set_ylabel('Amplitud')
    ax1.grid(True)
    
    ax2.plot(t_step, y_step)
    ax2.set_title('Respuesta al Escalón')
    ax2.set_xlabel('Tiempo (s)')
    ax2.set_ylabel('Amplitud')
    ax2.grid(True)
    
    ax3.plot(t_impulse, y_impulse)
    ax3.set_title('Respuesta al Impulso')
    ax3.set_xlabel('Tiempo (s)')
    ax3.set_ylabel('Amplitud')
    ax3.grid(True)
    
    plt.tight_layout()
    plt.show()
    
    # Características de la respuesta al escalón
    info = control.step_info(sys)
    print("\nCaracterísticas de la respuesta al escalón:")
    for key, value in info.items():
        print(f"{key}: {value:.3f}")

def analyze_forced_responses(sys):
    """Analiza las respuestas forzadas del sistema."""
    # Ganancia DC
    dc_gain = control.dcgain(sys)
    print(f"Ganancia DC: {dc_gain:.2f} dB")
    
    # Análisis AC
    w = np.logspace(-1, 5, 1000)
    mag, phase, _ = control.bode(sys, w, plot=False)
    mag_db = 20 * np.log10(mag)
    
    print("\nGanancia AC a frecuencias específicas:")
    freqs = [1, 10, 100, 1000, 10000]  # Hz
    for f in freqs:
        idx = np.abs(w - 2*np.pi*f).argmin()
        print(f"A {f} Hz: {mag_db[idx]:.2f} dB, Fase: {phase[idx]:.2f} grados")

def determine_filter_type(mag_db, freq):
    """Determina el tipo de filtro basado en su respuesta en frecuencia."""
    high_freq_slope = np.mean(np.diff(mag_db[-100:]))/np.mean(np.diff(np.log10(freq[-100:])))
    low_freq_gain = mag_db[0]
    high_freq_gain = mag_db[-1]
    
    if abs(high_freq_slope) < 10:
        return "Pasa todo"
    elif high_freq_gain > low_freq_gain:
        return "Pasa altas"
    elif high_freq_gain < low_freq_gain:
        if abs(high_freq_slope) < 30:
            return "Pasa bajas"
        else:
            return "Pasa bajas de orden superior"
    else:
        return "Pasa banda"

def analyze_frequency_response(sys):
    """Realiza el análisis en frecuencia del sistema."""
    w = np.logspace(-1, 5, 1000)
    w, mag, phase = control.bode(sys, w, plot=False)
    
    freq = w/(2*np.pi)
    mag_db = 20 * np.log10(mag)
    
    # Encontrar frecuencia de corte
    cutoff_idx = np.abs(mag_db - (max(mag_db) - 3)).argmin()
    cutoff_freq = freq[cutoff_idx]
    
    # Determinar tipo de filtro
    filter_type = determine_filter_type(mag_db, freq)
    
    # Graficar
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    ax1.semilogx(freq, mag_db)
    ax1.axvline(cutoff_freq, color='r', linestyle='--', alpha=0.5)
    ax1.axhline(-3, color='g', linestyle='--', alpha=0.5)
    ax1.set_title(f'Diagrama de Bode - Magnitud\nTipo de Filtro: {filter_type}')
    ax1.set_xlabel('Frecuencia (Hz)')
    ax1.set_ylabel('Magnitud (dB)')
    ax1.grid(True)
    
    ax2.semilogx(freq, phase)
    ax2.set_title('Diagrama de Bode - Fase')
    ax2.set_xlabel('Frecuencia (Hz)')
    ax2.set_ylabel('Fase (grados)')
    ax2.grid(True)
    
    plt.tight_layout()
    plt.show()
    
    # Imprimir características
    print(f"\nTipo de filtro identificado: {filter_type}")
    print(f"Frecuencia de corte (-3dB): {cutoff_freq:.2f} Hz")
    
    slope_high_freq = np.mean(np.diff(mag_db[-100:]))/np.mean(np.diff(np.log10(freq[-100:])))
    approx_order = abs(slope_high_freq/20)
    print(f"Orden aproximado del filtro: {approx_order:.1f}")
    
    print("\nCaracterísticas del filtro:")
    print(f"Ganancia en bajas frecuencias: {mag_db[0]:.2f} dB")
    print(f"Ganancia en altas frecuencias: {mag_db[-1]:.2f} dB")
    print(f"Pendiente en la banda de transición: {slope_high_freq:.2f} dB/década")

def analyze_responses_no_plots(components=None):
    """Ejecuta el análisis numérico de respuestas temporales y en frecuencia."""
    if components is None:
        (R1, R2, R3, R4), (Ci1, Ci2, C1, C2), valores, configs = init_components()
    else:
        (R1, R2, R3, R4), (Ci1, Ci2, C1, C2), valores, configs = components
    s = symbols('s')

    # Obtener función de transferencia
    H = calc_transfer_function(R1, R2, R3, R4, Ci1, Ci2, C1, C2, s, configs)
    sys = get_numeric_tf(H, valores, s)
    
    # Calcular características sin mostrar gráficas
    t = np.linspace(0, 0.01, 1000)
    info = control.step_info(sys)
    print("\nCaracterísticas de la respuesta al escalón:")
    for key, value in info.items():
        print(f"{key}: {value:.3f}")

    # Análisis forzado
    analyze_forced_responses(sys)

    # Análisis en frecuencia básico (sin gráficas)
    w = np.logspace(-1, 5, 1000)
    w, mag, phase = control.bode(sys, w, plot=False)
    freq = w/(2*np.pi)
    mag_db = 20 * np.log10(mag)
    
    # Encontrar frecuencia de corte
    cutoff_idx = np.abs(mag_db - (max(mag_db) - 3)).argmin()
    cutoff_freq = freq[cutoff_idx]
    
    # Determinar tipo de filtro
    filter_type = determine_filter_type(mag_db, freq)
    
    print(f"\nTipo de filtro identificado: {filter_type}")
    print(f"Frecuencia de corte (-3dB): {cutoff_freq:.2f} Hz")
    
    return sys

def run_complete_analysis(components=None, show_plots=False):
    """Ejecuta el análisis completo de respuestas temporales y en frecuencia."""
    configure_plots()
    sys = analyze_responses_no_plots(components)
    
    if show_plots:
        # Realizar análisis con gráficas
        plot_time_responses(sys)
        analyze_frequency_response(sys)

if __name__ == '__main__':
    run_complete_analysis()