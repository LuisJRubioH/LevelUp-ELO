"""QA only: export server-side grading data to the Node driver, never to a browser.

Reads the domain and versioned bank; no database, network or AI access.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.domain.learning import prealgebra as lessons  # noqa: E402


def main() -> None:
    nodes = {}
    for node_id, lesson in lessons._LESSONS.items():
        rules = {}
        for interaction_id, rule in lessons._INTERACTION_RULES.items():
            if rule["node_id"] != node_id:
                continue
            expected = rule.get("expected")
            if expected is None:
                expected = sorted(rule["valid_options"])[0]
            if isinstance(expected, (set, list)):
                expected = ",".join(sorted(expected))
            rules[interaction_id] = str(expected)
        nodes[node_id] = {**lesson, "answers": rules}
    bank = {}
    for source in sorted((ROOT / "items" / "bank").rglob("*.json")):
        items = json.loads(source.read_text(encoding="utf-8"))
        if isinstance(items, list):
            for item in items:
                if "correct_option" in item:
                    bank[item["id"]] = item["correct_option"]
    json.dump({"nodes": nodes, "bank": bank}, sys.stdout, ensure_ascii=False, default=list)


if __name__ == "__main__":
    main()
