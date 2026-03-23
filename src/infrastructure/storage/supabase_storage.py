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
        url = os.environ.get('SUPABASE_URL')
        key = os.environ.get('SUPABASE_KEY')
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

    def upload_file(self, bucket: str, path: str, file_bytes: bytes,
                    mime_type: str = 'image/jpeg') -> str | None:
        """Upload *file_bytes* and return its public URL, or None on failure."""
        if not self.available:
            return None
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
            return storage.get_public_url(path)
        except Exception as exc:
            print(f"[SupabaseStorage] upload error: {exc}")
            return None

    def get_file(self, bucket: str, path: str) -> bytes | None:
        """Download and return file bytes, or None on failure."""
        if not self.available:
            return None
        try:
            storage = self._client.storage.from_(bucket)
            return storage.download(path)
        except Exception as exc:
            print(f"[SupabaseStorage] download error: {exc}")
            return None
