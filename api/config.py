"""
api/config.py
=============
Configuración centralizada para la API FastAPI vía pydantic-settings.
Lee variables de entorno o del archivo .env en la raíz del repo.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # ── JWT ───────────────────────────────────────────────────────────────────
    jwt_secret_key: str = "CHANGE_ME_IN_PRODUCTION_USE_A_LONG_RANDOM_STRING"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # ── Base de datos ─────────────────────────────────────────────────────────
    database_url: str = ""  # vacío → SQLite local
    db_path: str = "data/elo_database.db"

    # ── CORS ─────────────────────────────────────────────────────────────────
    cors_origins: list[str] = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # React dev alternativo
        "https://levelup-elo.vercel.app",  # frontend en Vercel (producción)
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
    rate_limit_default: str = "60/minute"  # endpoints normales

    # ── Admin ─────────────────────────────────────────────────────────────────
    admin_user: str = "admin"
    admin_password: str = ""  # solo si se quiere seed automático

    # ── Versión ───────────────────────────────────────────────────────────────
    @property
    def app_version(self) -> str:
        try:
            from src.__version__ import __version__

            return __version__
        except ImportError:
            return "2.0.0"


settings = Settings()
