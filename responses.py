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
    """Ejecuta el análisis numérico de respuestas temporales y en frecuencia para cada op-amp y el total."""
    if components is None:
        (R1, R2, R3, R4), (Ci1, Ci2, C1, C2), valores, configs = init_components()
    else:
        (R1, R2, R3, R4), (Ci1, Ci2, C1, C2), valores, configs = components
    s = symbols('s')

    # Obtener funciones de transferencia individuales y total
    from transfer_function import calc_individual_transfer_functions, get_numeric_tf
    H1, H2, H_total = calc_individual_transfer_functions(R1, R2, R3, R4, Ci1, Ci2, C1, C2, s, configs)
    
    sys1 = get_numeric_tf(H1, valores, s)
    sys2 = get_numeric_tf(H2, valores, s)
    sys_total = get_numeric_tf(H_total, valores, s)
    
    # Análisis del primer op-amp
    print("\n=== ANÁLISIS DE RESPUESTA: PRIMER AMPLIFICADOR OPERACIONAL ===")
    info1 = control.step_info(sys1)
    print("\nCaracterísticas de la respuesta al escalón:")
    for key, value in info1.items():
        print(f"{key}: {value:.3f}")

    # Análisis en frecuencia para el primer op-amp
    w = np.logspace(-1, 5, 1000)
    w, mag1, phase1 = control.bode(sys1, w, plot=False)
    freq = w/(2*np.pi)
    mag_db1 = 20 * np.log10(mag1 + 1e-10)  # Evitar log(0)
    
    try:
        cutoff_idx1 = np.abs(mag_db1 - (np.max(mag_db1) - 3)).argmin()
        cutoff_freq1 = freq[cutoff_idx1]
        print(f"\nFrecuencia de corte (-3dB): {cutoff_freq1:.2f} Hz")
    except:
        print("\nNo se pudo calcular la frecuencia de corte")
    
    # Análisis del segundo op-amp
    print("\n" + "="*60)
    print("\n=== ANÁLISIS DE RESPUESTA: SEGUNDO AMPLIFICADOR OPERACIONAL ===")
    info2 = control.step_info(sys2)
    print("\nCaracterísticas de la respuesta al escalón:")
    for key, value in info2.items():
        print(f"{key}: {value:.3f}")

    # Análisis en frecuencia para el segundo op-amp
    w, mag2, phase2 = control.bode(sys2, w, plot=False)
    mag_db2 = 20 * np.log10(mag2 + 1e-10)
    
    try:
        cutoff_idx2 = np.abs(mag_db2 - (np.max(mag_db2) - 3)).argmin()
        cutoff_freq2 = freq[cutoff_idx2]
        print(f"\nFrecuencia de corte (-3dB): {cutoff_freq2:.2f} Hz")
    except:
        print("\nNo se pudo calcular la frecuencia de corte")
    
    # Análisis del sistema total
    print("\n" + "="*60)
    print("\n=== ANÁLISIS DE RESPUESTA: SISTEMA TOTAL (AMBOS AMPLIFICADORES) ===")
    info_total = control.step_info(sys_total)
    print("\nCaracterísticas de la respuesta al escalón:")
    for key, value in info_total.items():
        print(f"{key}: {value:.3f}")

    # Análisis en frecuencia para el sistema total
    w, mag_total, phase_total = control.bode(sys_total, w, plot=False)
    mag_db_total = 20 * np.log10(mag_total + 1e-10)
    
    filter_type = determine_filter_type(mag_db_total, freq)
    print(f"\nTipo de filtro identificado: {filter_type}")
    
    try:
        cutoff_idx_total = np.abs(mag_db_total - (np.max(mag_db_total) - 3)).argmin()
        cutoff_freq_total = freq[cutoff_idx_total]
        print(f"Frecuencia de corte (-3dB): {cutoff_freq_total:.2f} Hz")
    except:
        print("No se pudo calcular la frecuencia de corte")

    return sys1, sys2, sys_total

def run_complete_analysis(components=None, show_plots=False):
    """Ejecuta el análisis completo de respuestas temporales y en frecuencia."""
    configure_plots()
    sys1, sys2, sys_total = analyze_responses_no_plots(components)
    
    t = np.linspace(0, 0.01, 1000)
    
    if show_plots == 'escalon':
        t_step1, y_step1 = control.step_response(sys1, t)
        t_step2, y_step2 = control.step_response(sys2, t)
        t_step_total, y_step_total = control.step_response(sys_total, t)
        
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10))
        
        ax1.plot(t_step1, y_step1, 'b-', linewidth=2)
        ax1.set_title('Respuesta al Escalón - Primer Op-Amp')
        ax1.set_ylabel('Amplitud')
        ax1.grid(True)
        
        ax2.plot(t_step2, y_step2, 'r-', linewidth=2)
        ax2.set_title('Respuesta al Escalón - Segundo Op-Amp')
        ax2.set_ylabel('Amplitud')
        ax2.grid(True)
        
        ax3.plot(t_step_total, y_step_total, 'g-', linewidth=2)
        ax3.set_title('Respuesta al Escalón - Sistema Total')
        ax3.set_xlabel('Tiempo (s)')
        ax3.set_ylabel('Amplitud')
        ax3.grid(True)
        
        plt.tight_layout()
        plt.show()
        
    elif show_plots == 'impulso':
        t_impulse1, y_impulse1 = control.impulse_response(sys1, t)
        t_impulse2, y_impulse2 = control.impulse_response(sys2, t)
        t_impulse_total, y_impulse_total = control.impulse_response(sys_total, t)
        
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10))
        
        ax1.plot(t_impulse1, y_impulse1, 'b-', linewidth=2)
        ax1.set_title('Respuesta al Impulso - Primer Op-Amp')
        ax1.set_ylabel('Amplitud')
        ax1.grid(True)
        
        ax2.plot(t_impulse2, y_impulse2, 'r-', linewidth=2)
        ax2.set_title('Respuesta al Impulso - Segundo Op-Amp')
        ax2.set_ylabel('Amplitud')
        ax2.grid(True)
        
        ax3.plot(t_impulse_total, y_impulse_total, 'g-', linewidth=2)
        ax3.set_title('Respuesta al Impulso - Sistema Total')
        ax3.set_xlabel('Tiempo (s)')
        ax3.set_ylabel('Amplitud')
        ax3.grid(True)
        
        plt.tight_layout()
        plt.show()
        
    elif show_plots == 'bode':
        w = np.logspace(-1, 5, 1000)
        
        mag1, phase1, _ = control.bode(sys1, w, plot=False)
        mag2, phase2, _ = control.bode(sys2, w, plot=False)
        mag_total, phase_total, _ = control.bode(sys_total, w, plot=False)
        
        freq = w/(2*np.pi)
        mag_db1 = 20 * np.log10(mag1 + 1e-10)
        mag_db2 = 20 * np.log10(mag2 + 1e-10)
        mag_db_total = 20 * np.log10(mag_total + 1e-10)
        
        fig = plt.figure(figsize=(14, 12))
        
        # Primer op-amp
        ax1 = plt.subplot(3, 2, 1)
        ax1.semilogx(freq, mag_db1, 'b-', linewidth=2)
        ax1.set_title('Diagrama de Bode - Magnitud (Primer Op-Amp)')
        ax1.set_ylabel('Magnitud (dB)')
        ax1.grid(True)
        
        ax2 = plt.subplot(3, 2, 2)
        ax2.semilogx(freq, phase1, 'b-', linewidth=2)
        ax2.set_title('Diagrama de Bode - Fase (Primer Op-Amp)')
        ax2.set_ylabel('Fase (grados)')
        ax2.grid(True)
        
        # Segundo op-amp
        ax3 = plt.subplot(3, 2, 3)
        ax3.semilogx(freq, mag_db2, 'r-', linewidth=2)
        ax3.set_title('Diagrama de Bode - Magnitud (Segundo Op-Amp)')
        ax3.set_ylabel('Magnitud (dB)')
        ax3.grid(True)
        
        ax4 = plt.subplot(3, 2, 4)
        ax4.semilogx(freq, phase2, 'r-', linewidth=2)
        ax4.set_title('Diagrama de Bode - Fase (Segundo Op-Amp)')
        ax4.set_ylabel('Fase (grados)')
        ax4.grid(True)
        
        # Sistema total
        ax5 = plt.subplot(3, 2, 5)
        ax5.semilogx(freq, mag_db_total, 'g-', linewidth=2)
        ax5.set_title('Diagrama de Bode - Magnitud (Sistema Total)')
        ax5.set_xlabel('Frecuencia (Hz)')
        ax5.set_ylabel('Magnitud (dB)')
        ax5.grid(True)
        
        ax6 = plt.subplot(3, 2, 6)
        ax6.semilogx(freq, phase_total, 'g-', linewidth=2)
        ax6.set_title('Diagrama de Bode - Fase (Sistema Total)')
        ax6.set_xlabel('Frecuencia (Hz)')
        ax6.set_ylabel('Fase (grados)')
        ax6.grid(True)
        
        plt.tight_layout()
        plt.show()

if __name__ == '__main__':
    run_complete_analysis()