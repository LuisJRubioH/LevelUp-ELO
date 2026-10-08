"""
scripts/restore_storage_bucket.py — put a bucket backup made by backup_storage_bucket.py back.

Verifies every file of <backup>/objects/ against <backup>/manifest.json (SHA-256) before touching
Supabase, then uploads with x-upsert: false: an object that already exists is left as it is and
counted, never overwritten; nothing is ever deleted. Without --apply it only verifies and reports.

    python scripts/restore_storage_bucket.py --backup backup-procedimientos-YYYYMMDD [--apply]

Reads SUPABASE_URL and SUPABASE_KEY (a key allowed to write the private bucket). Standard output
carries counts only. Exit code 0 only if the backup verifies and every object is present after the
run (uploaded now or already there).
"""

import argparse
import hashlib
import json
import mimetypes
import os
import sys
from urllib.parse import quote

import httpx


def _exists_response(res):
    if res.status_code == 409:
        return True
    return res.status_code == 400 and ("Duplicate" in res.text or "already exists" in res.text)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--backup", required=True, help="directory made by backup_storage_bucket.py")
    ap.add_argument("--bucket", help="target bucket (default: the one in the manifest)")
    ap.add_argument("--apply", action="store_true", help="upload; without it, verify only")
    args = ap.parse_args()

    with open(os.path.join(args.backup, "manifest.json"), encoding="utf-8") as fh:
        manifest = json.load(fh)
    bucket = args.bucket or manifest["bucket"]
    objects = manifest["objects"]

    corrupt = []
    for obj in objects:
        path = os.path.join(args.backup, "objects", *obj["path"].split("/"))
        try:
            with open(path, "rb") as fh:
                data = fh.read()
        except OSError:
            corrupt.append(obj["path"])
            continue
        if hashlib.sha256(data).hexdigest() != obj["sha256"] or len(data) != obj["size"]:
            corrupt.append(obj["path"])
    print(f"backup lists {len(objects)} objects; missing or altered files: {len(corrupt)}")
    if corrupt:
        print("RESULT: FAIL (the backup does not verify; nothing was uploaded)")
        return 1
    if not args.apply:
        print(f"RESULT: PASS (verified only; re-run with --apply to upload into {bucket!r})")
        return 0

    url, key = os.environ.get("SUPABASE_URL", "").rstrip("/"), os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        sys.exit("Set SUPABASE_URL and SUPABASE_KEY in the environment.")
    client = httpx.Client(
        base_url=url,
        timeout=120,
        headers={"apikey": key, "Authorization": f"Bearer {key}", "x-upsert": "false"},
    )
    uploaded, existing, failed = 0, 0, 0
    for obj in objects:
        path = os.path.join(args.backup, "objects", *obj["path"].split("/"))
        with open(path, "rb") as fh:
            data = fh.read()
        mime = mimetypes.guess_type(obj["path"])[0] or "application/octet-stream"
        res = client.post(
            f"/storage/v1/object/{bucket}/{quote(obj['path'])}",
            content=data,
            headers={"Content-Type": mime},
        )
        if res.status_code == 200:
            uploaded += 1
        elif _exists_response(res):
            existing += 1
        else:
            failed += 1
    print(f"uploaded {uploaded}; already present (left untouched) {existing}; failed {failed}")
    print("RESULT: " + ("PASS" if not failed else "FAIL"))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
