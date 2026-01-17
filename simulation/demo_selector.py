# ======================================================
# simulation/demo_selector.py
# ======================================================
from elo.model import StudentELO, update_elo, Item
from selector.item_selector import AdaptiveItemSelector
from simulation.student import SimulatedStudent


def run_demo():
    student = StudentELO()
    selector = AdaptiveItemSelector(delta=120)


    items = [Item(difficulty=d) for d in range(700, 1300, 25)]
    sim = SimulatedStudent(true_skill=1050)


    for step in range(20):
        item = selector.select(student.rating, items)
        result = sim.attempt(item)
        update_elo(student, item, result)
        print(
        f"Paso {step+1:02d} | Ítem {item.difficulty} | "
        f"Resultado {result} | ELO {student.rating:.1f}"
        )




if __name__ == '__main__':
    run_demo()