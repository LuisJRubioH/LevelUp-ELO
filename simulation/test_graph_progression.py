from elo.model import Item, expected_score
from elo.vector_elo import VectorELO, aggregate_global_elo
from elo.diagnostics import ELODiagnostics
from graph.content_graph import ContentGraph, Concept
from simulation.student import SimulatedStudent
from selector.item_selector import AdaptiveItemSelector

def run_progression_demo():
    # 1. Configuración del Grafo
    graph = ContentGraph()
    c1 = Concept("aritmetica", min_elo=0.0)
    c2 = Concept("algebra", min_elo=1100.0) # Requiere un nivel más alto
    graph.add_concept(c1)
    graph.add_concept(c2)
    graph.add_prerequisite("algebra", "aritmetica")

    # 2. Inicialización del Estudiante (Habilidad real alta: 1200)
    sim = SimulatedStudent(true_skill=1200)
    vector = VectorELO()
    selector = AdaptiveItemSelector(delta=100)
    
    # Diagnósticos por concepto
    diagnostics = { "aritmetica": ELODiagnostics(), "algebra": ELODiagnostics() }
    mastered = set()
    
    # Items disponibles por concepto
    items_db = {
        "aritmetica": [Item(d) for d in range(800, 1101, 50)],
        "algebra": [Item(d) for d in range(1100, 1401, 50)]
    }

    print(f"--- Iniciando Simulación de Progresión ---")
    
    for step in range(1, 31):
        global_elo = aggregate_global_elo(vector)
        
        # Consultar conceptos disponibles
        # Nota: Aquí usamos la lógica de elo mínimo definida en tu código
        available = graph.available_concepts(global_elo)
        
        # Priorizar el concepto más avanzado disponible que no esté dominado
        current_concept = available[-1] if available else c1
        
        # Selección e interacción
        pool = items_db[current_concept.id]
        item = selector.select(vector.get(current_concept.id), pool)
        
        exp = expected_score(vector.get(current_concept.id), item.difficulty)
        res = sim.attempt(item)
        
        # Actualización
        vector.update(current_concept.id, item.difficulty, res, 24)
        diagnostics[current_concept.id].record(res, exp)
        
        current_elo = vector.get(current_concept.id)
        
        # Verificar Maestría (Umbral de convergencia: 0.05)
        if current_concept.id not in mastered:
            # Usamos la nueva lógica: Rating suficiente + Varianza baja
            if current_elo >= 1050 and diagnostics[current_concept.id].converged(0.05):
                mastered.add(current_concept.id)
                print(f"¡LOGRO! Concepto '{current_concept.id}' dominado en el paso {step}.")

        if step % 5 == 0 or current_concept.id == "algebra":
            print(f"Paso {step:02d} | Concepto: {current_concept.id} | Elo: {current_elo:.1f}")

if __name__ == "__main__":
    run_progression_demo()