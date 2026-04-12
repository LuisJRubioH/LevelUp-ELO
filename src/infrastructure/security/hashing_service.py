from passlib.context import CryptContext
import hashlib


class HashingService:
    """
    Servicio de infraestructura para la gestión de hashing de contraseñas.
    Encapsula Argon2id y soporte para hashes legados SHA-256.
    """

    def __init__(self):
        self.pwd_context = CryptContext(
            schemes=["argon2"],
            argon2__memory_cost=65536,
            argon2__parallelism=4,
            argon2__time_cost=2,
            deprecated="auto",
        )

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verifica una contraseña contra un hash (Argon2id)."""
        return self.pwd_context.verify(password, hashed)

    def verify_and_update(self, password: str, hashed: str):
        """Verifica y retorna un nuevo hash si el actual está deprecado."""
        return self.pwd_context.verify_and_update(password, hashed)

    def verify_legacy_sha256(self, password: str, stored_hash: str) -> bool:
        """Verifica contra SHA-256 plano (migración)."""
        legacy_hash = hashlib.sha256(password.encode()).hexdigest()
        return legacy_hash == stored_hash
