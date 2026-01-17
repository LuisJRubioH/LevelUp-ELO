class ELODiagnostics:
    def __init__(self):
        self.errors = [] #

    def record(self, result: float, expected: float):
        self.errors.append(result - expected) #

    def variance(self) -> float:
        if len(self.errors) < 2:
            return float('inf') #
        mean = sum(self.errors) / len(self.errors)
        return sum((e - mean) ** 2 for e in self.errors) / (len(self.errors) - 1) #

    def converged(self, epsilon: float) -> bool:
        return self.variance() < epsilon #

    # Nueva funcionalidad: Verificación de Dominio
    def is_mastered(self, current_rating: float, required_elo: float, epsilon: float = 0.05) -> bool:
        """
        Determina si el concepto ha sido dominado.
        Requiere que el rating sea suficiente y que el error sea estable.
        """
        return current_rating >= required_elo and self.converged(epsilon)