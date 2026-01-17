from simulation.mass_simulation import run_simulation
from analysis.metrics import mean_absolute_error
from analysis.visualization import plot_convergence, plot_error_histogram
from graph.content_graph import ContentGraph, Concept # Importación necesaria


import csv
import os
import time
# ... tus otras importaciones ...

def save_to_csv(data, timestamp):
    results_dir = "results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    # 1. Guardar Resumen de Estudiantes
    summary_path = os.path.join(results_dir, f"resumen_{timestamp}.csv")
    with open(summary_path, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['student_id', 'true_skill', 'estimated_elo', 'abs_error'])
        for d in data:
            writer.writerow([
                d['student_id'], 
                round(d['true'], 2), 
                round(d['estimated'], 2), 
                round(abs(d['true'] - d['estimated']), 2)
            ])

    # 2. Guardar Detalle de cada Paso (Log de interacciones)
    detail_path = os.path.join(results_dir, f"detalles_{timestamp}.csv")
    with open(detail_path, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['student_id', 'step', 'elo_before', 'item_diff', 'result'])
        for d in data:
            for step in d['steps']:
                writer.writerow([
                    step['student_id'], 
                    step['step'], 
                    round(step['current_elo'], 2), 
                    step['item_difficulty'], 
                    step['result']
                ])
    
    print(f"Archivos CSV guardados en la carpeta '{results_dir}'")

def main():
    # Inicializa tu grafo aquí si es necesario
    graph = ContentGraph() 
    # ... logic ...
    data = run_simulation(graph, n_students=200, n_steps=40)
    
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    save_to_csv(data, timestamp)
    plot_convergence([d['history'] for d in data], f"conv_{timestamp}.png")
    print("Simulación y análisis completados.")

if __name__ == "__main__":
    main()