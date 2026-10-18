"""Fills attempts.prob_failure where it is NULL (spec 002 FR-018).

From the rating reconstructed in chronological order per student and topic — approximate, display
only; it never moves a rating (AGENTS R15): `python scripts/repairs/backfill_prob_failure.py [--apply]`.
"""

from _repair import run

if __name__ == "__main__":
    run("repair_prob_failure", "attempts given a prob_failure", __doc__)
