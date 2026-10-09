"""Storage keys and local file names built from free text (AGENTS R9)."""

import re

_UNSAFE_PATH_CHARS = re.compile(r"[^A-Za-z0-9_-]+")


def safe_path_component(value) -> str:
    """One segment of a Storage key or a local file name, built from free text.

    A procedure's exercise id is typed by the student (`taller_3_p5`). Letters, digits, `_` and
    `-` are kept; any other run of characters becomes `_`, so no `/`, `\\` or `..` can leave the
    student's folder. The submission row still stores the id as typed.
    """
    segment = _UNSAFE_PATH_CHARS.sub("_", str(value or ""))[:80]
    return segment or "item"
