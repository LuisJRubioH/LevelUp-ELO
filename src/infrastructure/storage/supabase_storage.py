from dotenv import load_dotenv

load_dotenv()  # debe ser lo primero

import os

print(f"[STORAGE INIT] URL={os.environ.get('SUPABASE_URL', 'NO DEFINIDA')}")
print(f"[STORAGE INIT] KEY={'OK' if os.environ.get('SUPABASE_KEY') else 'NO DEFINIDA'}")

"""Supabase Storage client for file uploads (procedures, feedback images).

Degrades gracefully: if SUPABASE_URL / SUPABASE_KEY are not set, all
methods return None so callers can fall back to the legacy BYTEA path.
"""


class SupabaseStorage:
    """Thin wrapper around the Supabase Storage API."""

    def __init__(self):
        self._client = None
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if url and key:
            try:
                from supabase import create_client

                self._client = create_client(url, key)
            except Exception as exc:
                print(f"[SupabaseStorage] init failed: {exc}")

    @property
    def available(self) -> bool:
        return self._client is not None

    # ── public API ──────────────────────────────────────────────────────────

    def upload_file(
        self, bucket: str, path: str, file_bytes: bytes, mime_type: str = "image/jpeg"
    ) -> str | None:
        """Upload *file_bytes* and return the storage *path* (not a URL).

        Previous versions returned a public URL, but the bucket is private
        so public URLs don't work.  Now we store the path and generate
        signed URLs on demand via :meth:`create_signed_url`.
        """
        if not self.available:
            return None
        print(
            f"[STORAGE UPLOAD] bucket={bucket}, path={path}, size={len(file_bytes)} bytes, mime={mime_type}"
        )
        try:
            storage = self._client.storage.from_(bucket)
            # Remove existing file at same path (idempotent re-upload)
            try:
                storage.remove([path])
            except Exception:
                pass
            storage.upload(
                path,
                file_bytes,
                file_options={"content-type": mime_type, "upsert": "true"},
            )
            # Return the path — callers use create_signed_url() to display.
            return path
        except Exception as exc:
            print(f"[STORAGE UPLOAD ERROR] {exc}")
            return None

    @staticmethod
    def extract_path(storage_url: str, bucket: str) -> str:
        """Extract the storage path from a public URL or return as-is if already a path.

        Handles three cases:
        (a) Full URL: ``https://xxx.supabase.co/storage/v1/object/public/procedimientos/1/2/h.jpg``
            → ``1/2/h.jpg``
        (b) Plain path: ``1/2/h.jpg`` → ``1/2/h.jpg``
        (c) Path with bucket prefix: ``procedimientos/1/2/h.jpg`` → ``1/2/h.jpg``
        """
        # Case (a): full public URL
        marker = f"/object/public/{bucket}/"
        idx = storage_url.find(marker)
        if idx != -1:
            return storage_url[idx + len(marker) :]
        # Case (c): path starts with bucket name
        prefix = f"{bucket}/"
        if storage_url.startswith(prefix):
            return storage_url[len(prefix) :]
        # Case (b): already a plain path
        return storage_url

    def create_signed_url(self, bucket: str, path: str, expires_in: int = 3600) -> str | None:
        """Create a signed URL valid for *expires_in* seconds, or None."""
        if not self.available:
            return None
        try:
            storage = self._client.storage.from_(bucket)
            # extract_path handles legacy full-URL values
            clean_path = self.extract_path(path, bucket)
            resp = storage.create_signed_url(clean_path, expires_in)
            # supabase-py returns {'signedURL': '...'} or a dict with 'signedUrl'
            if isinstance(resp, dict):
                return resp.get("signedURL") or resp.get("signedUrl")
            return resp
        except Exception as exc:
            print(f"[SupabaseStorage] signed-url error: {exc}")
            return None

    def get_file(self, bucket: str, path: str) -> bytes | None:
        """Download and return file bytes, or None on failure."""
        if not self.available:
            print("[STORAGE GET] No disponible - SUPABASE_URL/KEY faltantes")
            return None
        try:
            print(f"[STORAGE GET] path_original={path}")
            clean_path = self.extract_path(path, bucket)
            print(f"[STORAGE GET] path_limpio={clean_path}")
            storage = self._client.storage.from_(bucket)
            data = storage.download(clean_path)
            print(f"[STORAGE GET] OK: {len(data)} bytes")
            return data
        except Exception as exc:
            print(f"[STORAGE GET ERROR] {type(exc).__name__}: {exc}")
            return None
