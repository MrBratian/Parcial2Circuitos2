from thevenin_analysis import plot_thevenin_analysis
from transfer_function import analyze_transfer_function_no_plots
from responses import run_complete_analysis, analyze_responses_no_plots
from utils import init_components

def show_menu():
    print("\n=== MENÚ DE GRÁFICAS ===")
    print("1. Respuesta al escalón")
    print("2. Respuesta al impulso")
    print("3. Diagrama de Bode (respuesta en frecuencia)")
    print("4. Salir")
    while True:
        try:
            choice = int(input("\nSeleccione la gráfica que desea ver (1-4): "))
            if 1 <= choice <= 4:
                return choice
            print("Por favor, seleccione un número entre 1 y 4.")
        except ValueError:
            print("Por favor, ingrese un número válido.")

def main():
    # Obtener todos los datos una sola vez
    components = init_components()

    # Mostrar todos los análisis numéricos primero
    print("\n================================================")
    print("=== ANÁLISIS DE EQUIVALENTES THÉVENIN ===")
    print("================================================")
    plot_thevenin_analysis(components)
    
    print("\n================================================")
    print("=== ANÁLISIS DE FUNCIONES DE TRANSFERENCIA ===")
    print("================================================")
    analyze_transfer_function_no_plots(components)
    
    print("\n================================================")
    print("=== ANÁLISIS DE RESPUESTAS DEL SISTEMA ===")
    print("================================================")
    analyze_responses_no_plots(components)
    
    # Menú para seleccionar gráficas
    while True:
        choice = show_menu()
        if choice == 1:
            run_complete_analysis(components, show_plots='escalon')
        elif choice == 2:
            run_complete_analysis(components, show_plots='impulso')
        elif choice == 3:
            run_complete_analysis(components, show_plots='bode')
        else:  # choice == 4
            print("\n¡Gracias por usar el programa!")
            break

if __name__ == '__main__':
    main()