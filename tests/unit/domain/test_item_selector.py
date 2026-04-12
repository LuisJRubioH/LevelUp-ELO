"""
tests/unit/domain/test_item_selector.py
========================================
Pruebas del AdaptiveItemSelector (ZDP + Fisher Information).

API real:
  AdaptiveItemSelector(target_low=0.4, target_high=0.75)
  selector.select_optimal_item(student_rating, items: List[Item]) -> Item | None
  selector.information(p) -> float

Nota: select_optimal_item recibe objetos Item(difficulty=...), no dicts.
"""
import pytest
from src.domain.elo.model import Item, expected_score
from src.domain.selector.item_selector import AdaptiveItemSelector


@pytest.fixture
def selector() -> AdaptiveItemSelector:
    return AdaptiveItemSelector()


def _make_items(*difficulties) -> list:
    """Crea una lista de Item dataclasses a partir de valores de dificultad."""
    return [Item(difficulty=d) for d in difficulties]


class TestZDPSelection:
    def test_selects_item_in_zdp_range(self, selector, item_pool_objs):
        """El selector elige ítems en la zona de desarrollo próximo."""
        result = selector.select_optimal_item(1000.0, item_pool_objs)
        assert result is not None

    def test_returns_none_for_empty_pool(self, selector):
        """Pool vacío → retorna None, no levanta excepción."""
        result = selector.select_optimal_item(1000.0, [])
        assert result is None

    def test_returns_item_object(self, selector, item_pool_objs):
        """El resultado es un objeto Item (no un dict)."""
        result = selector.select_optimal_item(1000.0, item_pool_objs)
        assert isinstance(result, Item)

    def test_expands_range_when_no_zdp_candidates(self, selector):
        """Si no hay ítems en rango ZDP, expande hasta encontrar uno."""
        # Todos los ítems son muy fáciles para un estudiante con rating 2000
        very_easy = _make_items(100, 120, 150, 180, 200)
        result = selector.select_optimal_item(2000.0, very_easy)
        # Debe encontrar algún ítem expandiendo el rango
        assert result is not None

    def test_single_item_pool_always_returns_it(self, selector):
        """Con un solo ítem, siempre lo retorna (sin importar la dificultad)."""
        items = _make_items(1800.0)
        result = selector.select_optimal_item(500.0, items)
        assert result is not None
        assert result.difficulty == 1800.0


class TestFisherInformation:
    def test_information_maximum_at_50_percent(self, selector):
        """Información de Fisher I(p) = p*(1-p) es máxima en p=0.5."""
        i_50 = selector.information(0.5)
        i_30 = selector.information(0.3)
        i_70 = selector.information(0.7)
        assert i_50 > i_30
        assert i_50 > i_70

    def test_prefers_item_closest_to_50_percent_success(self, selector):
        """Entre dos ítems válidos, prefiere el que maximiza P*(1-P)."""
        # Para rating=1000:
        # - item difficulty=1000 → P=0.5 → Fisher máximo
        # - item difficulty=800  → P≈0.76 → más fácil, menor Fisher
        item_near_50 = Item(difficulty=1000.0)
        item_at_76 = Item(difficulty=800.0)
        result = selector.select_optimal_item(1000.0, [item_at_76, item_near_50])
        assert result is not None
        assert result.difficulty == 1000.0

    def test_information_is_zero_at_extremes(self, selector):
        """I(0) = 0 e I(1) = 0 — probabilidades extremas no son informativas."""
        assert selector.information(0.0) == pytest.approx(0.0)
        assert selector.information(1.0) == pytest.approx(0.0)

    def test_information_is_symmetric(self, selector):
        """I(p) == I(1-p) — la información es simétrica alrededor de 0.5."""
        for p in [0.1, 0.2, 0.3, 0.4]:
            assert selector.information(p) == pytest.approx(selector.information(1 - p), abs=1e-9)


class TestZDPPreFiltering:
    def test_zdp_window_filters_extreme_difficulties(self, selector):
        """El filtro ZDP ±250 alrededor del rating excluye dificultades extremas."""
        # Rating 1000 → ZDP [750, 1250]
        items = _make_items(200.0, 300.0, 1000.0, 1700.0, 1900.0)
        result = selector.select_optimal_item(1000.0, items)
        assert result is not None
        # El ítem seleccionado debe estar en la ventana ZDP o ser el fallback
        # (en este caso, difficulty=1000 está en [750, 1250])
        assert result.difficulty == pytest.approx(1000.0, abs=1.0)
