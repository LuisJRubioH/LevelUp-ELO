"""QA only: print every eleven-block node's CONTENT as JSON, for `scripts/qa/math_check.js`.

    python scripts/qa/dump_lesson_content.py > lessons.json

Reads the node modules; touches no database.
"""

import importlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.domain.learning.nodes import NODE_MODULES  # noqa: E402


def main() -> None:
    nodes = {}
    for entry in NODE_MODULES:
        module = importlib.import_module(entry) if isinstance(entry, str) else entry
        content = getattr(module, "CONTENT", None)
        if content is not None:
            nodes[content.get("node_id") or module.__name__.rsplit(".", 1)[-1]] = content
    json.dump(nodes, sys.stdout, ensure_ascii=False, default=list)


if __name__ == "__main__":
    main()
