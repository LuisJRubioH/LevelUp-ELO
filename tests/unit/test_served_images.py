"""The pictures the frontend serves stay light, and every one the code names exists.

The lesson art was once ~3 MB a PNG (300 MB in `frontend/public/`); `scripts/optimize_images.py`
turned it into WebP. These tests keep it that way and catch a reference left pointing at the old
file, which the browser would show as a broken image.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import optimize_images  # noqa: E402

# A served picture's URL path in a string literal or a CSS url(): "/leccion/a/b.webp".
_REFERENCE = re.compile(r"""(?<=["'`(])/(?:[\w.-]+/)*[\w.-]+\.(?:png|webp|gif|jpe?g|svg|avif)""")

# Over this a single picture is a regression (the largest converted scene is about 0.85 MB).
_SERVED_MAX_BYTES = 1_000_000


def _referenced_paths():
    found = {}
    for path in optimize_images.reference_files():
        for url in _REFERENCE.findall(path.read_text(encoding="utf-8")):
            if url.startswith("/items/"):
                continue  # item figures are served by the API, not by the frontend
            found.setdefault(url, path.relative_to(ROOT).as_posix())
    return found


def test_no_served_picture_needs_converting():
    pending = [optimize_images.url_path(p) for p in optimize_images.pending()]
    assert pending == [], "run: python scripts/optimize_images.py --apply"


def test_no_served_picture_is_over_budget():
    heavy = {
        optimize_images.url_path(p): p.stat().st_size
        for p in optimize_images.PUBLIC.rglob("*")
        if p.is_file() and p.stat().st_size > _SERVED_MAX_BYTES
    }
    assert heavy == {}


def test_the_code_names_the_lesson_pictures():
    referenced = _referenced_paths()
    assert sum(url.startswith("/leccion/") for url in referenced) > 100


def test_every_picture_the_code_names_exists():
    missing = {
        url: where
        for url, where in _referenced_paths().items()
        if not (optimize_images.PUBLIC / url.lstrip("/")).is_file()
    }
    assert missing == {}
