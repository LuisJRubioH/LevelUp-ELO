"""Validación de archivos, antiplagio y procedencia verificable del análisis IA."""

import hashlib
import io
import uuid

from PIL import Image


def png_bytes(color=(20, 80, 140)) -> bytes:
    output = io.BytesIO()
    Image.new("RGB", (2, 2), color).save(output, format="PNG")
    return output.getvalue()


def test_rejects_declared_image_with_non_image_content(api_client, student_headers):
    response = api_client.post(
        "/api/student/procedure",
        headers=student_headers,
        data={"item_id": "invalid-content"},
        files={"file": ("fake.png", b"not an image", "image/png")},
    )
    assert response.status_code == 415


def test_client_cannot_forge_ai_score_but_signed_review_is_accepted(api_client, student_headers):
    import api.dependencies as dependencies

    profile = api_client.get("/api/auth/me", headers=student_headers).json()
    repo = dependencies.get_repository()
    image = png_bytes()
    item_id = "verified-ai-" + uuid.uuid4().hex

    forged = api_client.post(
        "/api/student/procedure",
        headers=student_headers,
        data={"item_id": item_id, "ai_proposed_score": "99", "ai_feedback": "forged"},
        files={"file": ("work.png", image, "image/png")},
    )
    assert forged.status_code == 200
    assert repo.get_student_submission(profile["user_id"], item_id)["ai_proposed_score"] is None

    token = dependencies.create_procedure_review_token(
        profile["user_id"], item_id, hashlib.sha256(image).hexdigest(), 84, "verified"
    )
    verified = api_client.post(
        "/api/student/procedure",
        headers=student_headers,
        data={"item_id": item_id, "analysis_token": token},
        files={"file": ("work.png", image, "image/png")},
    )
    assert verified.status_code == 200
    saved = repo.get_student_submission(profile["user_id"], item_id)
    assert saved["ai_proposed_score"] == 84
    assert saved["ai_feedback"] == "verified"


def test_duplicate_file_from_another_student_is_rejected(api_client, student_headers):
    import api.dependencies as dependencies

    repo = dependencies.get_repository()
    image = png_bytes((160, 40, 20))
    item_id = "plagiarism-" + uuid.uuid4().hex
    first = api_client.post(
        "/api/student/procedure",
        headers=student_headers,
        data={"item_id": item_id},
        files={"file": ("a.png", image, "image/png")},
    )
    assert first.status_code == 200

    username = "upload_other_" + uuid.uuid4().hex[:10]
    ok, _ = repo.register_user(username, "password123", "student")
    assert ok
    conn = repo.get_connection()
    try:
        other_id = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()[0]
    finally:
        conn.close()
    token = dependencies.create_access_token(other_id, username, "student")
    second = api_client.post(
        "/api/student/procedure",
        headers={"Authorization": f"Bearer {token}"},
        data={"item_id": item_id},
        files={"file": ("copy.png", image, "image/png")},
    )
    assert second.status_code == 409
