"""
src/domain/pvp/match_items.py
=============================
Spec 007 delivery M (FR-032; owner decision O-M8). Pure — no I/O; the randomness is the
`random.Random` the caller passes (tests seed it).

1. Candidates: the items no player saw (`seen`, O-M9) within ±`band` of the mean of the two
   ratings, the band widened by `band_step` at a time until there are at least `n` or it covers
   the whole course.
2. `n` of them drawn at random.
3. When the whole course holds fewer than `n` unseen items, all of them are taken and the rest is
   filled with seen ones, nearest difficulty to the mean first.

The same list, in the same order, goes to both players.
"""

import random
from typing import Collection, Sequence


def choose_match_items(
    items: Sequence[dict],
    mean: float,
    seen: Collection[str],
    n: int,
    rng: random.Random,
    band: float = 200,
    band_step: float = 100,
) -> list[dict]:
    def gap(item: dict) -> float:
        return abs(float(item["difficulty"]) - mean)

    unseen = [item for item in items if item["id"] not in seen]
    if len(unseen) < n:
        nearest_seen = sorted(
            (item for item in items if item["id"] in seen), key=lambda i: (gap(i), str(i["id"]))
        )
        chosen = unseen + nearest_seen[: n - len(unseen)]
        rng.shuffle(chosen)
        return chosen

    width = band
    candidates = [item for item in unseen if gap(item) <= width]
    while len(candidates) < n and band_step > 0:
        width += band_step
        candidates = [item for item in unseen if gap(item) <= width]
    if len(candidates) < n:  # no step to widen by: the whole course
        candidates = unseen
    return rng.sample(candidates, n)
