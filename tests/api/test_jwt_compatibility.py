"""JWT wire compatibility and rejection rules when replacing python-jose with PyJWT."""

import base64
import hashlib
import hmac
import json
import time

import pytest
from fastapi import HTTPException

from api import dependencies


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _wire_token(payload, key, algorithm="HS256"):
    """Build the standard HS256 wire format independently of either JWT library."""
    header = _b64(json.dumps({"alg": algorithm, "typ": "JWT"}).encode())
    body = _b64(json.dumps(payload).encode())
    message = f"{header}.{body}"
    digest = hmac.new(key.encode(), message.encode(), hashlib.sha256).digest()
    return f"{message}.{_b64(digest)}"


@pytest.fixture(autouse=True)
def jwt_settings(monkeypatch):
    monkeypatch.setattr(
        dependencies.settings, "jwt_secret_key", "jwt-compatibility-test-key-32bytes"
    )
    monkeypatch.setattr(dependencies.settings, "jwt_algorithm", "HS256")


@pytest.mark.parametrize("token_type", ["access", "refresh", "procedure_review"])
def test_existing_hs256_tokens_remain_valid(token_type):
    payload = {"sub": "42", "type": token_type, "exp": int(time.time()) + 300}
    token = _wire_token(payload, dependencies.settings.jwt_secret_key)
    assert dependencies.decode_token(token) == payload


@pytest.mark.parametrize("token_type", ["access", "refresh", "procedure_review"])
def test_new_tokens_preserve_standard_signature_and_claims(token_type):
    if token_type == "access":
        token = dependencies.create_access_token(42, "student", "student")
    elif token_type == "refresh":
        token = dependencies.create_refresh_token(42)
    else:
        token = dependencies.create_procedure_review_token(42, "item", "hash", 80, "feedback")
    header, body, signature = token.split(".")
    expected = hmac.new(
        dependencies.settings.jwt_secret_key.encode(),
        f"{header}.{body}".encode(),
        hashlib.sha256,
    ).digest()
    assert hmac.compare_digest(signature, _b64(expected))
    claims = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
    assert claims["sub"] == "42"
    assert claims["type"] == token_type
    assert claims["exp"] > time.time()
    assert dependencies.decode_token(token) == claims


@pytest.mark.parametrize("invalid_case", ["expired", "wrong_key", "wrong_algorithm", "malformed"])
def test_invalid_tokens_still_return_401(invalid_case):
    payload = {"sub": "42", "type": "access", "exp": int(time.time()) + 300}
    key = dependencies.settings.jwt_secret_key
    algorithm = "HS256"
    if invalid_case == "expired":
        payload["exp"] = int(time.time()) - 60
    elif invalid_case == "wrong_key":
        key = "different-jwt-compatibility-test-key"
    elif invalid_case == "wrong_algorithm":
        algorithm = "none"
    token = "malformed" if invalid_case == "malformed" else _wire_token(payload, key, algorithm)
    with pytest.raises(HTTPException) as error:
        dependencies.decode_token(token)
    assert error.value.status_code == 401
    assert error.value.headers == {"WWW-Authenticate": "Bearer"}
