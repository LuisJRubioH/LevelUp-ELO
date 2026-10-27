"""
Spec 007 delivery M (US3; FR-032): the items of a match (O-M8).

`choose_match_items` takes the course's items, the mean of the two ratings, the ids either player
saw this week and a seeded `random.Random`: unseen items within ±200 of the mean, widened by 100
until there are 10; 10 drawn at random; fewer than 10 unseen in the whole course → all of them,
then the nearest seen ones.
"""

import random

from src.domain.pvp.match_items import choose_match_items


def _items(*difficulties):
    return [{"id": f"i{n}", "difficulty": d} for n, d in enumerate(difficulties)]


def _choose(items, mean, seen=(), seed=7):
    return choose_match_items(
        items, mean, set(seen), n=10, rng=random.Random(seed), band=200, band_step=100
    )


def test_spec007_match_items_are_near_the_mean():
    """FR-032: with 12 items within ±200 of the mean and 8 far away, the 10 come from the band —
    for any draw; the draw is random among the band, not the 10 nearest."""
    near = _items(*([1000, 1100, 1150, 1199, 851, 1250] * 2))  # 851 … 1250, all within ±200
    far = [{"id": f"f{n}", "difficulty": d} for n, d in enumerate([600, 700] * 2 + [1500] * 4)]
    for seed in range(20):
        chosen = _choose(near + far, 1050, seed=seed)
        assert len(chosen) == 10
        assert all(abs(item["difficulty"] - 1050) <= 200 for item in chosen)
        assert len({item["id"] for item in chosen}) == 10
    draws = {tuple(sorted(i["id"] for i in _choose(near + far, 1050, seed=s))) for s in range(20)}
    assert len(draws) > 1

    # Too few in ±200: widened by 100 at a time — ±300 holds enough, so nothing at ±400 enters.
    sparse = _items(*([1050] * 6 + [1340] * 4 + [1440] * 5))
    chosen = _choose(sparse, 1050)
    assert sorted(i["difficulty"] for i in chosen) == [1050] * 6 + [1340] * 4


def test_spec007_match_items_skip_items_seen_this_week():
    """FR-032: an item either player saw is not chosen while enough unseen ones exist — the band
    widens before a seen item enters."""
    items = _items(*([1000] * 12 + [1350] * 4))
    seen = {"i0", "i1", "i2", "i3", "i4"}  # 7 unseen in ±200, so ±300, ±400 → + the 1350s
    for seed in range(10):
        chosen = _choose(items, 1000, seen, seed=seed)
        assert len(chosen) == 10
        assert not {i["id"] for i in chosen} & seen


def test_spec007_match_items_fill_with_seen_items_when_too_few_remain():
    """FR-032 "when enough remain": 6 unseen in the whole course → all 6, then the 4 seen items
    nearest the mean; a course with fewer than 10 items gives all it has."""
    items = _items(1000, 1010, 1020, 1030, 1040, 1050, 900, 1300, 1600, 1800, 2000, 400)
    seen = {"i0", "i1", "i2", "i3", "i4", "i5"}
    chosen = {i["id"] for i in _choose(items, 1000, seen)}
    assert chosen == {"i6", "i7", "i8", "i9", "i10", "i11", "i0", "i1", "i2", "i3"}

    small = _items(1000, 1200, 800)
    assert {i["id"] for i in _choose(small, 1000, {"i1"})} == {"i0", "i1", "i2"}
    assert _choose([], 1000) == []
