import random
from elo.vector_elo import VectorELO, aggregate_global_elo
from elo.model import Item
from simulation.student import SimulatedStudent
from selector.item_selector import AdaptiveItemSelector
# from graph.content_graph import ContentGraph 
import pandas as pd # Necesitarás instalarlo: pip install pandas

def run_simulation(graph, n_students=100, n_steps=40):
    selector = AdaptiveItemSelector()
    items = [Item(difficulty=d) for d in range(700, 1401, 20)]
    results = []

    for s_id in range(n_students):
        if s_id % 50 == 0:
            print(f"Simulando estudiante {s_id}...", flush=True)

        true_skill = random.gauss(1000, 100)
        student = SimulatedStudent(true_skill)
        vector = VectorELO()
        
        history = []
        step_details = [] 

        for step in range(n_steps):
            global_elo = aggregate_global_elo(vector)
            item = selector.select(global_elo, items)
            result = student.attempt(item)
            
            step_details.append({
                'student_id': s_id,
                'step': step + 1,
                'current_elo': global_elo,
                'item_difficulty': item.difficulty,
                'result': result
            })
            
            vector.update('global', item.difficulty, result, 24)
            history.append(global_elo)

        results.append({
            'student_id': s_id,
            'true': true_skill, 
            'estimated': aggregate_global_elo(vector), 
            'history': history,
            'steps': step_details 
        })

    return results

# ESTO ES LO QUE FALTA PARA QUE "OCURRA ALGO":
# ... (todo tu código anterior igual) ...

# ESTO ES LO QUE DEBES AJUSTAR AL FINAL:
if __name__ == "__main__":
    print("--- Iniciando Simulación ---")
    
    # 1. Guardamos el retorno de la función en una variable
    resultados_finales = run_simulation(None, n_students=150, n_steps=10)
    
    print("\n--- Resumen de Resultados (Primeros 5 estudiantes) ---")
    # 2. Imprimimos una pequeña muestra para verificar que funcionó
    for res in resultados_finales[:5]:
        print(f"Estudiante {res['student_id']}: True Skill: {res['true']:.2f} | Estimated ELO: {res['estimated']:.2f}")

    print(f"\nProceso finalizado con éxito. Total: {len(resultados_finales)} estudiantes.")

   

    # Convertimos los detalles de cada paso a una tabla plana
    all_steps = []
    for res in resultados_finales:
        all_steps.extend(res['steps'])
    
    df = pd.DataFrame(all_steps)
    df.to_csv("resultados_simulacion.csv", index=False)
    print("\nArchivo 'resultados_simulacion.csv' guardado.")