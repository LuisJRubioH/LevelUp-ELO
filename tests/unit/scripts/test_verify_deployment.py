"""verify_deployment.py: the preview check must not fail on its own rounding."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from verify_deployment import matches_preview  # noqa: E402


def _reported(exact):
    """What `/answer` reports (0.01) and what `/next-question` previewed (0.1)."""
    return round(exact, 2), round(exact, 1)


@pytest.mark.parametrize("exact", [5.4466, -12.4649, 6.0, 0.04999, -0.0451, 31.95, 1.25])
def test_the_applied_change_matches_its_own_preview(exact):
    assert matches_preview(*_reported(exact))


@pytest.mark.parametrize("delta,preview", [(5.6, 5.4), (5.46, 5.3), (-12.4, -12.6), (6.0, -6.0)])
def test_a_different_change_does_not_match(delta, preview):
    assert not matches_preview(delta, preview)
