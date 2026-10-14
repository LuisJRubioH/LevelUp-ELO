"""
api/config.py
=============
Configuración centralizada para la API FastAPI vía pydantic-settings.
Lee variables de entorno o del archivo .env en la raíz del repo.
"""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "development"

    # ── JWT ───────────────────────────────────────────────────────────────────
    jwt_secret_key: str = "CHANGE_ME_IN_PRODUCTION_USE_A_LONG_RANDOM_STRING"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    # Spec 004 E5 (FR-081): SameSite of the renewal cookie. "none" while the frontend calls the API
    # from another origin (today); "lax" once the API is reached through the frontend's own origin
    # (Vercel proxy, docs/transfer.md § 3.3). The cookie is always HttpOnly and Secure.
    auth_cookie_samesite: str = "none"

    # ── Base de datos ─────────────────────────────────────────────────────────
    database_url: str = ""  # vacío → SQLite local
    db_path: str = "data/elo_database.db"

    # ── CORS ─────────────────────────────────────────────────────────────────
    cors_origins: list[str] = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # React dev alternativo
        "https://luislevelupelo.vercel.app",  # frontend Vercel — producción
        "https://luislevelupelo-git-main-luisjrubiohs-projects.vercel.app",  # preview rama main
    ]

    # ── IA del sistema ─────────────────────────────────────────────────────────
    # Key general (fallback si no hay key específica por función)
    system_ai_api_key: str = ""  # gsk_, sk-ant-, sk-, AIzaSy… — cualquier proveedor
    system_ai_provider: str = ""  # groq, anthropic, openai, google (auto-detectado si vacío)

    # Keys opcionales por función — si vacías, usan system_ai_api_key
    ai_key_katia: str = ""  # chat socrático (KatIA)
    ai_key_procedure: str = ""  # revisión de procedimientos manuscritos
    ai_key_student_analysis: str = ""  # recomendaciones y análisis para el estudiante
    ai_key_teacher_analysis: str = ""  # análisis en dashboard del docente

    def get_ai_key(self, function: str = "", user_key: str = "") -> str:
        """Resuelve la API key por prioridad: usuario > función > general."""
        if user_key.strip():
            return user_key.strip()
        fn_map = {
            "katia": self.ai_key_katia,
            "procedure": self.ai_key_procedure,
            "student_analysis": self.ai_key_student_analysis,
            "teacher_analysis": self.ai_key_teacher_analysis,
        }
        specific = fn_map.get(function, "").strip()
        if specific:
            return specific
        return self.system_ai_api_key.strip()

    # ── Rate limiting (slowapi) ───────────────────────────────────────────────
    rate_limit_socratic: str = "10/minute"  # peticiones IA socrática por usuario
    rate_limit_review: str = "3/minute"  # revisión de procedimientos
    # Spec 004 E1: login is limited per account and overall, never per address (FR-006 … FR-009);
    # public sign-up, when open, has its own per-address limit (FR-004, decision N2: 20/minute).
    rate_limit_login_account: str = "10/minute"
    rate_limit_login_global: str = "300/minute"
    rate_limit_register: str = "20/minute"
    # Spec 004 FR-001/FR-002: public registration is closed unless this server setting opens it.
    public_registration_enabled: bool = False
    rate_limit_default: str = "60/minute"  # endpoints normales
    rate_limit_storage_uri: str = "memory://"  # producción: Redis compartido entre instancias
    # Spec 004 E6 (FR-090 … FR-095): if the shared store fails while the API runs, limits are
    # counted in memory; no call waits longer than these timeouts, and recovery is probed in the
    # background at most once per interval. The memory fallback holds at most this many counters.
    rate_limit_storage_connect_timeout: float = 0.5  # seconds
    rate_limit_storage_timeout: float = 0.5  # seconds, per operation
    rate_limit_storage_probe_interval: float = 10.0  # seconds
    rate_limit_fallback_max_keys: int = 50_000

    # ── Admin ─────────────────────────────────────────────────────────────────
    admin_user: str = "admin"
    admin_password: str = ""  # solo si se quiere seed automático

    # ── Concurrencia de procesos ──────────────────────────────────────────────
    # uvicorn y gunicorn leen WEB_CONCURRENCY como número de workers. PvP y las
    # notificaciones guardan su estado en memoria del proceso, así que con más
    # de uno los jugadores de procesos distintos no se emparejan y los eventos
    # solo llegan a los sockets locales. Ver validate_runtime() y AGENTS.md R18.
    web_concurrency: int = 1

    @field_validator("auth_cookie_samesite")
    @classmethod
    def _known_samesite(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in ("none", "lax", "strict"):
            raise ValueError("AUTH_COOKIE_SAMESITE debe ser none, lax o strict.")
        return value

    def validate_runtime(self) -> None:
        """Impide arrancar producción con defaults locales o secretos débiles."""
        if self.environment.lower() != "production":
            return
        if not self.database_url.strip():
            raise RuntimeError("DATABASE_URL es obligatoria en producción.")
        if (
            self.jwt_secret_key == "CHANGE_ME_IN_PRODUCTION_USE_A_LONG_RANDOM_STRING"
            or len(self.jwt_secret_key) < 32
        ):
            raise RuntimeError("JWT_SECRET_KEY debe ser un secreto de al menos 32 caracteres.")
        if not self.cors_origins or any(
            origin.startswith("http://localhost") for origin in self.cors_origins
        ):
            raise RuntimeError("CORS_ORIGINS de producción no puede incluir localhost.")
        if self.rate_limit_storage_uri.strip().lower() == "memory://":
            raise RuntimeError("RATE_LIMIT_STORAGE_URI compartida es obligatoria en producción.")
        if self.web_concurrency > 1:
            raise RuntimeError(
                "WEB_CONCURRENCY debe ser 1: el lobby de PvP y las salas de "
                "notificaciones viven en memoria del proceso. Con varios workers los "
                "jugadores de procesos distintos no se emparejan y los eventos solo "
                "llegan a los sockets locales, sin ningún error visible. Antes de "
                "subirlo hace falta coordinación compartida — ver AGENTS.md R18."
            )

    # ── Versión ───────────────────────────────────────────────────────────────
    @property
    def app_version(self) -> str:
        try:
            from src.__version__ import __version__

            return __version__
        except ImportError:
            return "2.0.0"


settings = Settings()
