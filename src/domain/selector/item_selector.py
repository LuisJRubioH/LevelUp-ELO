# ======================================================
# selector/item_selector.py
# ======================================================
from typing import List
from src.domain.elo.model import Item, expected_score
from src.domain.elo.zdp import zdp_interval


class AdaptiveItemSelector:
    """
    Selector experto basado en la Zona de Desarrollo Próximo (ZDP).
    
    LÓGICA MATEMÁTICA:
    1. Probabilidad Esperada (P): Se utiliza el modelo logístico de ELO/IRT:
       P = 1 / (1 + 10^((Dificultad - Rating) / 400))
    2. Rango de Aprendizaje Óptimo: Se seleccionan ítems donde 0.4 <= P <= 0.75.
       - P > 0.75: Demasiado fácil (Boredom).
       - P < 0.4: Demasiado difícil (Frustration).
    3. Información de Fisher: Entre candidatos válidos, se maximiza I(P) = P * (1-P).
       Esto asegura una convergencia más rápida del ELO al elegir ítems cerca de P=0.5.
    4. Expansión Progresiva: Si el banco es limitado, se relajan los límites de P 
       progresivamente (±0.05) hasta encontrar un ítem.
    """
    def __init__(self, target_low: float = 0.4, target_high: float = 0.75):
        self.target_low = target_low
        self.target_high = target_high

    def information(self, p: float) -> float:
        """Información de Fisher: p(1-p). Máxima en p=0.5."""
        return p * (1 - p)

    def select_optimal_item(self, student_rating: float, items: List[Item]) -> Item:
        """
        Selecciona el ítem estadísticamente más informativo dentro del rango de probabilidad.
        Pre-filtra por ventana ZDP en espacio de rating antes del filtro de probabilidad.
        """
        if not items:
            return None

        # Pre-filtro por ventana ZDP en espacio de rating [rating-250, rating+250]
        zdp_low, zdp_high = zdp_interval(student_rating, delta=250)
        zdp_pool = [i for i in items if zdp_low <= i.difficulty <= zdp_high]
        pool = zdp_pool if zdp_pool else items  # fallback al pool completo

        p_low = self.target_low
        p_high = self.target_high
        steps = 0
        max_expansion_steps = 10

        candidates = []

        while not candidates and steps < max_expansion_steps:
            for item in pool:
                p = expected_score(student_rating, item.difficulty)
                if p_low <= p <= p_high:
                    candidates.append((item, p))

            if not candidates:
                # Expansión sutil del rango de probabilidad ±5%
                p_low = max(0.01, p_low - 0.05)
                p_high = min(0.99, p_high + 0.05)
                steps += 1

        if not candidates:
            candidates = [(i, expected_score(student_rating, i.difficulty)) for i in pool]

        # Priorizar por máxima información (Fisher Information) y peso del ítem
        return max(
            candidates,
            key=lambda c: self.information(c[1]) * getattr(c[0], 'weight', 1.0)
        )[0]

