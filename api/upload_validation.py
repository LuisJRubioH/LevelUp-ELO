"""Lectura acotada y validación del contenido real de uploads."""

import io

from fastapi import HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 25_000_000
ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp", "application/pdf"}
_FORMAT_MIME = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}


async def read_validated_upload(file: UploadFile) -> tuple[bytes, str]:
    declared = file.content_type or ""
    if declared not in ALLOWED_MIME:
        raise HTTPException(status_code=415, detail="Tipo de archivo no soportado.")
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if not data:
        raise HTTPException(status_code=422, detail="El archivo está vacío.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="El archivo excede el límite de 10 MB.")
    if declared == "application/pdf":
        if not data.startswith(b"%PDF-"):
            raise HTTPException(status_code=415, detail="El contenido no es un PDF válido.")
        try:
            import fitz

            document = fitz.open(stream=data, filetype="pdf")
            page_count = document.page_count
            document.close()
            if page_count < 1 or page_count > 20:
                raise HTTPException(status_code=422, detail="El PDF debe tener entre 1 y 20 páginas.")
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=415, detail="El PDF no es válido.") from exc
        return data, declared
    try:
        with Image.open(io.BytesIO(data)) as image:
            actual = _FORMAT_MIME.get(image.format or "")
            if actual != declared:
                raise HTTPException(status_code=415, detail="El contenido no coincide con su MIME.")
            if image.width * image.height > MAX_IMAGE_PIXELS:
                raise HTTPException(status_code=413, detail="La imagen excede el límite de píxeles.")
            image.verify()
    except HTTPException:
        raise
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(status_code=415, detail="La imagen no es válida.") from exc
    return data, declared
