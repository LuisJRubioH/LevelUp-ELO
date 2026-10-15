"""The single rank scale and the display rule (spec 001, FR-031, FR-028h, FR-028i, FR-028j)."""

from decimal import ROUND_HALF_UP, Decimal

# (minimum rating, label), ascending. The only rank scale; served by GET /api/meta/ranks.
RANKS: tuple[tuple[int, str], ...] = (
    (0, "Aspirante"),
    (600, "Hierro"),
    (700, "Bronce II"),
    (800, "Bronce I"),
    (900, "Plata II"),
    (1000, "Plata I"),
    (1100, "Oro II"),
    (1200, "Oro I"),
    (1300, "Platino II"),
    (1400, "Platino I"),
    (1500, "Diamante II"),
    (1600, "Diamante I"),
    (1800, "Maestro"),
    (2000, "Gran Maestro"),
    (2200, "Leyenda"),
    (2500, "Leyenda Suprema"),
)

# Whole numbers: the one precision for comparing ratings in rankings and for showing a rating
# next to its rank label.
RATING_DISPLAY_DECIMALS = 0


def rank_for(rating: float | None) -> str | None:
    if rating is None:
        return None
    label = RANKS[0][1]
    for minimum, name in RANKS:
        if rating >= minimum:
            label = name
    return label


def round_for_display(rating: float) -> int:
    """Half up on the decimal value (1199.5 → 1200, 1200.5 → 1201); never Python's round().

    Only for a final derived value that is displayed or ranked — never for stored ratings or
    intermediate averages (FR-028i).
    """
    return int(Decimal(repr(rating)).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def rating_display(rating: float | None) -> dict:
    """The shown number and its label, both from the same rounded value (FR-028j)."""
    if rating is None:
        return {"display_rating": None, "rank_label": None}
    shown = round_for_display(rating)
    return {"display_rating": shown, "rank_label": rank_for(shown)}


def rank_competition(entries: list[dict]) -> list[dict]:
    """Competition ranking (1, 2, 2, 4) on rounded ratings (FR-028h).

    Each entry carries `user_id` and a full-precision `rating` (None = pending). Returns copies
    with `rating` rounded, `rank_label` from it and `rank`; user id only orders a tie for display;
    pending entries come last with `rank=None`. Other fields are carried through, never used.
    """
    rated, pending = [], []
    for entry in entries:
        shown = rating_display(entry["rating"])
        row = {**entry, "rating": shown["display_rating"], "rank_label": shown["rank_label"]}
        (pending if row["rating"] is None else rated).append(row)
    rated.sort(key=lambda e: (-e["rating"], e["user_id"]))
    for i, entry in enumerate(rated):
        tied_with_previous = i and entry["rating"] == rated[i - 1]["rating"]
        entry["rank"] = rated[i - 1]["rank"] if tied_with_previous else i + 1
    pending.sort(key=lambda e: e["user_id"])
    for entry in pending:
        entry["rank"] = None
    return rated + pending
