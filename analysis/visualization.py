# ======================================================
# analysis/visualization.py
# ======================================================
import matplotlib.pyplot as plt
import os

# Creamos una carpeta para los resultados si no existe
RESULTS_DIR = "results"
if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)

def plot_convergence(histories, filename="convergencia.png"):
    plt.figure(figsize=(10, 6))
    for h in histories:
        plt.plot(h, alpha=0.1, color='teal')
    plt.axhline(y=1000, color='r', linestyle='--', label="Media Inicial")
    plt.title("Convergencia del Sistema Adaptativo")
    plt.xlabel("Pasos")
    plt.ylabel("ELO Estimado")
    
    path = os.path.join(RESULTS_DIR, filename)
    plt.savefig(path)
    print(f"Gráfica guardada en: {path}")
    plt.close() # Importante cerrar la figura para liberar memoria

def plot_error_histogram(errors, filename="histograma_error.png"):
    plt.figure(figsize=(10, 6))
    plt.hist(errors, bins=20, color='skyblue', edgecolor='black')
    plt.title("Distribución del Error de Estimación")
    plt.xlabel("Error Absoluto (Real - Estimado)")
    plt.ylabel("Frecuencia")
    
    path = os.path.join(RESULTS_DIR, filename)
    plt.savefig(path)
    print(f"Histograma guardado en: {path}")
    plt.close()