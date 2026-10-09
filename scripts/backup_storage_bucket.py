"""
scripts/backup_storage_bucket.py — download every object of a Supabase Storage bucket.

The Supabase dashboard has no bulk download. This lists the bucket recursively through the Storage
REST API, saves each object under <out>/objects/ with its relative path (AGENTS.md R9: the
database stores relative paths) and writes <out>/manifest.json (path, size, sha256).
scripts/restore_storage_bucket.py puts such a backup back.

With --database-url it also proves the backup is complete, against two lists read from the
database in a READ ONLY transaction:
  - storage.objects for the bucket: Supabase's own catalogue of every stored file. A key that
    cannot list the private bucket gets an empty listing, not an error; this check catches it.
  - procedure_submissions.storage_url: every file the application references.
With --strict-catalog an unreadable storage.objects is a failure instead of a warning.

    python scripts/backup_storage_bucket.py --out backup-procedimientos-YYYYMMDD \\
        [--bucket procedimientos] [--database-url "$MIGRATION_DATABASE_URL"] [--strict-catalog]

Reads SUPABASE_URL and SUPABASE_KEY (the key the API already uses; it must be able to read the
private bucket) from the environment. Read-only on Supabase. Standard output carries counts only;
object paths (student work) go to <out>/backup-report.json, inside the backup. Keep the backup out
of the repository. Exit code 0 only if every object was saved and nothing known is missing.
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


def _expected(database_url, sslmode, bucket):
    """(catalogue paths or None if unreadable, referenced paths) — read-only."""
    import psycopg2

    conn = psycopg2.connect(database_url, sslmode=sslmode)
    conn.set_session(readonly=True)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT storage_url FROM procedure_submissions"
                " WHERE storage_url IS NOT NULL AND storage_url <> ''"
            )
            referenced = {row[0] for row in cur.fetchall()}
        conn.commit()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT name FROM storage.objects WHERE bucket_id = %s", (bucket,))
                catalogue = {row[0] for row in cur.fetchall()}
            conn.commit()
        except psycopg2.Error:
            conn.rollback()
            catalogue = None
    finally:
        conn.close()
    return catalogue, referenced


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", required=True, help="new, empty directory for the backup")
    ap.add_argument("--bucket", default="procedimientos")
    ap.add_argument("--database-url", help="check completeness against the database")
    ap.add_argument(
        "--strict-catalog", action="store_true", help="fail if storage.objects cannot be read"
    )
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
    print(f"listed {len(paths)} objects in bucket {args.bucket!r}")
    manifest, failed = [], []
    for path in paths:
        res = client.get(f"/storage/v1/object/{args.bucket}/{quote(path)}")
        if res.status_code != 200:
            failed.append({"path": path, "status": res.status_code})
            continue
        target = os.path.join(args.out, "objects", *path.split("/"))
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
    print(f"saved {len(manifest)} objects, {total:,} bytes; failed downloads {len(failed)}")

    report = {"listed": len(paths), "saved": len(manifest), "failed": failed}
    missing_catalogue, missing_referenced, catalogue_ok = [], [], True
    if args.database_url:
        catalogue, referenced = _expected(args.database_url, args.sslmode, args.bucket)
        saved = {m["path"] for m in manifest}
        missing_referenced = sorted(referenced - saved)
        print(
            f"database references {len(referenced)} stored files;"
            f" missing from backup: {len(missing_referenced)}"
        )
        if catalogue is None:
            catalogue_ok = not args.strict_catalog
            print(
                ("FAIL" if args.strict_catalog else "WARN")
                + ": storage.objects is not readable; completeness unproven"
            )
        else:
            missing_catalogue = sorted(catalogue - saved)
            print(
                f"storage catalogue lists {len(catalogue)} objects;"
                f" missing from backup: {len(missing_catalogue)}"
            )
        report.update(
            {
                "referenced": len(referenced),
                "missing_referenced": missing_referenced,
                "catalogue": None if catalogue is None else len(catalogue),
                "missing_catalogue": missing_catalogue,
            }
        )
    with open(os.path.join(args.out, "backup-report.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=1)

    ok = not failed and not missing_referenced and not missing_catalogue and catalogue_ok
    print("RESULT: " + ("PASS" if ok else "FAIL") + " (details in backup-report.json)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
