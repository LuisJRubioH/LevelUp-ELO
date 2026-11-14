"""QA only: open every lesson of the learning path for three local test students.

The automated lesson sweep (`scripts/qa/lesson_sweep.js`) needs every node open and one student
per presentation band. This writes straight into the LOCAL SQLite database and refuses to run
when `DATABASE_URL` is set, so it can never touch Supabase.

    python scripts/qa/seed_lesson_access.py

Students (seeded test users, `is_test_user=1`):
    estudiante_colegio_1 → basico (diagnostic 30 %)
    estudiante_colegio_2 → intermedio (65 %)
    estudiante_colegio_3 → avanzado (90 %)
"""

import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.domain.learning.prealgebra import PREALGEBRA_COURSE_ID, curriculum_map_rows  # noqa: E402

BANDS = {
    "estudiante_colegio_1": 30.0,
    "estudiante_colegio_2": 65.0,
    "estudiante_colegio_3": 90.0,
}


def main() -> int:
    if os.environ.get("DATABASE_URL"):
        print("DATABASE_URL is set: this script only writes the local SQLite database.")
        return 1
    db = ROOT / "data" / "elo_database.db"
    if not db.exists():
        print(f"{db} does not exist: start the API once so it bootstraps the database.")
        return 1
    node_ids = [row["node_id"] for row in curriculum_map_rows(lambda _n: "completed")]
    conn = sqlite3.connect(db)
    try:
        for username, score in BANDS.items():
            row = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            if not row:
                print(f"{username}: not found, skipped")
                continue
            user_id = row[0]
            conn.execute(
                "INSERT OR REPLACE INTO diagnostics (user_id, course_id, initial_elo, score_pct)"
                " VALUES (?, ?, 1000, ?)",
                (user_id, PREALGEBRA_COURSE_ID, score),
            )
            conn.executemany(
                "INSERT OR REPLACE INTO lesson_progress (user_id, course_id, node_id, state,"
                " completed_at) VALUES (?, ?, ?, 'completed', CURRENT_TIMESTAMP)",
                [(user_id, PREALGEBRA_COURSE_ID, node_id) for node_id in node_ids],
            )
            print(f"{username}: {len(node_ids)} nodes open, diagnostic {score:.0f} %")
        conn.commit()
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
