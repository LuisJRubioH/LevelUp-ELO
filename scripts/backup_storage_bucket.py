"""
scripts/backup_storage_bucket.py — download every object of a Supabase Storage bucket.

The Supabase dashboard has no bulk download. This lists the bucket recursively through the Storage
REST API, saves each object under --out with its relative path (AGENTS.md R9: the database stores
relative paths) and writes manifest.json (path, size, sha256). With --database-url it also checks
that every procedure_submissions.storage_url is in the backup.

    python scripts/backup_storage_bucket.py --out backup-procedimientos-YYYYMMDD \\
        [--bucket procedimientos] [--database-url "$MIGRATION_DATABASE_URL"]

Reads SUPABASE_URL and SUPABASE_KEY (the key the API already uses; it must be able to read the
private bucket) from the environment. Read-only on Supabase. The files are student work: keep
them out of the repository. Exit code 0 only if every object was saved (and, with
--database-url, every referenced path is present).
"""

import argparse
import hashlib
import json
import os
import sys
from urllib.parse import quote

import httpx

PAGE = 1000


def _list(client, bucket, prefix=""):
    """Every object path under prefix (folders are entries without an id)."""
    paths, offset = [], 0
    while True:
        res = client.post(
            f"/storage/v1/object/list/{bucket}",
            json={
                "prefix": prefix,
                "limit": PAGE,
                "offset": offset,
                "sortBy": {"column": "name", "order": "asc"},
            },
        )
        res.raise_for_status()
        entries = res.json()
        for entry in entries:
            path = f"{prefix}{entry['name']}"
            if entry.get("id") is None:
                paths.extend(_list(client, bucket, path + "/"))
            else:
                paths.append(path)
        if len(entries) < PAGE:
            return paths
        offset += PAGE


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", required=True, help="new, empty directory for the backup")
    ap.add_argument("--bucket", default="procedimientos")
    ap.add_argument("--database-url", help="check procedure_submissions.storage_url against it")
    ap.add_argument("--sslmode", default=os.environ.get("DATABASE_SSLMODE", "require"))
    args = ap.parse_args()

    url, key = os.environ.get("SUPABASE_URL", "").rstrip("/"), os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        sys.exit("Set SUPABASE_URL and SUPABASE_KEY in the environment.")
    if os.path.exists(args.out) and os.listdir(args.out):
        sys.exit(f"Refusing: {args.out} is not empty.")
    os.makedirs(args.out, exist_ok=True)

    client = httpx.Client(
        base_url=url,
        timeout=120,
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
    )
    paths = _list(client, args.bucket)
    print(f"{len(paths)} objects in bucket {args.bucket!r}")
    manifest, failed = [], []
    for path in paths:
        res = client.get(f"/storage/v1/object/{args.bucket}/{quote(path)}")
        if res.status_code != 200:
            failed.append(f"{path} ({res.status_code})")
            continue
        target = os.path.join(args.out, *path.split("/"))
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "wb") as fh:
            fh.write(res.content)
        manifest.append(
            {
                "path": path,
                "size": len(res.content),
                "sha256": hashlib.sha256(res.content).hexdigest(),
            }
        )
    with open(os.path.join(args.out, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump({"bucket": args.bucket, "objects": manifest}, fh, indent=1)
    total = sum(m["size"] for m in manifest)
    print(f"saved {len(manifest)} objects, {total:,} bytes; failed {len(failed)}")
    for f in failed[:20]:
        print(f"  FAILED {f}")

    missing = []
    if args.database_url:
        import psycopg2

        conn = psycopg2.connect(args.database_url, sslmode=args.sslmode)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT storage_url FROM procedure_submissions"
                    " WHERE storage_url IS NOT NULL AND storage_url <> ''"
                )
                referenced = {row[0] for row in cur.fetchall()}
        finally:
            conn.close()
        saved = {m["path"] for m in manifest}
        missing = sorted(referenced - saved)
        print(
            f"database references {len(referenced)} stored files; missing from backup:"
            f" {len(missing)}"
        )
        for m in missing[:20]:
            print(f"  MISSING {m}")

    ok = not failed and not missing
    print("RESULT: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
