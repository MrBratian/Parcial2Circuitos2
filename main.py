"""
Script principal para el análisis de circuitos con amplificadores operacionales.
"""
from thevenin_analysis import plot_thevenin_analysis
from transfer_function import plot_transfer_function_analysis
from responses import run_complete_analysis

def main():
    """Ejecuta el análisis completo del circuito."""
    print("=== Análisis de Equivalentes Thévenin ===")
    plot_thevenin_analysis()
    
    print("\n=== Análisis de Función de Transferencia y Estabilidad ===")
    plot_transfer_function_analysis()
    
    print("\n=== Análisis de Respuestas Temporales y en Frecuencia ===")
    run_complete_analysis()

if __name__ == '__main__':
    main()