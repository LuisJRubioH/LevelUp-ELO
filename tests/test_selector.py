# ======================================================
# tests/test_selector.py
# ======================================================
from selector.item_selector import AdaptiveItemSelector
from elo.model import Item

def test_selector_returns_item():
    selector = AdaptiveItemSelector(delta=100)
    items = [Item(difficulty=d) for d in range(800, 1201, 100)]
    item = selector.select(1000, items)
    assert item in items