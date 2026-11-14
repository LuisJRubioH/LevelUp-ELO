"""Run the QA API on loopback with an isolated SQLite file and no remote integrations.

    python scripts/qa/serve_flow_app.py

Stop the other API on port 8000 first. Never installs browsers or deletes an existing database.
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def main() -> int:
    if "DATABASE_URL" in os.environ:
        print("DATABASE_URL is defined: the local QA server refuses to start.")
        return 2
    # Explicit environment values also override .env settings and python-dotenv's fallback.
    # All writes stay in this local, disposable database, including upload fallback bytes.
    database = ROOT / "tmp" / "qa-flows" / "elo.db"
    database.parent.mkdir(parents=True, exist_ok=True)
    os.environ.update(
        {
            "DATABASE_URL": "",
            "DB_PATH": str(database),
            "ENVIRONMENT": "development",
            "WEB_CONCURRENCY": "1",
            "RUN_MIGRATIONS": "1",
            "ADMIN_PASSWORD": "testadmin123",
            "PUBLIC_REGISTRATION_ENABLED": "true",
            "SYSTEM_AI_API_KEY": "",
            "AI_KEY_KATIA": "",
            "AI_KEY_PROCEDURE": "",
            "AI_KEY_TEACHER_ANALYSIS": "",
            "SUPABASE_URL": "",
            "SUPABASE_KEY": "",
            "RATE_LIMIT_STORAGE_URI": "memory://",
        }
    )
    import uvicorn

    print(f"QA only: loopback API, SQLite {database}, no AI or Supabase Storage.")
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, workers=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
