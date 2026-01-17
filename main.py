from elo.model import Item, StudentELO, expected_score, update_elo
from elo.diagnostics import ELODiagnostics
from simulation.student import SimulatedStudent


if __name__ == '__main__':
    student = StudentELO()
    diagnostics = ELODiagnostics()

    items = [Item(difficulty=d) for d in range(800, 1200, 50)]
    sim = SimulatedStudent(true_skill=1050)

    for item in items:
        exp = expected_score(student.rating, item.difficulty)
        res = sim.attempt(item)
        update_elo(student, item, res)
        diagnostics.record(res, exp)
        print(f"Item {item.difficulty} | Resultado {res} | ELO {student.rating:.2f}")

    print("Varianza final:", diagnostics.variance())
