from thevenin_analysis import plot_thevenin_analysis
from transfer_function import plot_transfer_function_analysis
from responses import run_complete_analysis

def main():
    # Análisis de Equivalentes Thévenin (ahora primero)
    print("\n================================================")
    print("=== ANÁLISIS DE EQUIVALENTES THÉVENIN ===")
    print("================================================")
    plot_thevenin_analysis()
    
    # Análisis de Funciones de Transferencia
    print("\n================================================")
    print("=== ANÁLISIS DE FUNCIONES DE TRANSFERENCIA ===")
    print("================================================")
    plot_transfer_function_analysis()
    
    # Análisis de Respuestas
    print("\n================================================")
    print("=== ANÁLISIS DE RESPUESTAS DEL SISTEMA ===")
    print("================================================")
    run_complete_analysis()

if __name__ == '__main__':
    main()