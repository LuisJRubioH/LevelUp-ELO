"""
src/infrastructure/logging_config.py
=====================================
Configuración centralizada de logging para LevelUp-ELO.

Uso desde app.py:
    from src.infrastructure.logging_config import configure_logging
    configure_logging()

Uso desde cualquier módulo:
    from src.infrastructure.logging_config import get_logger
    logger = get_logger(__name__)
    logger.info("Mensaje informativo")
    logger.warning("Advertencia con contexto")
    logger.error("Error con traceback", exc_info=True)
"""
import logging
import os
import sys


def configure_logging(
    level: str = "INFO",
    log_file: str = None,
) -> None:
    """
    Configura el sistema de logging de la aplicación.
    Llamar una sola vez al inicio de app.py.

    Args:
        level: Nivel de log. "DEBUG" | "INFO" | "WARNING" | "ERROR".
               Por defecto "INFO". Override con env var LOG_LEVEL.
        log_file: Ruta a archivo de log adicional (None = solo consola).
    """
    # Respetar override por variable de entorno
    effective_level = os.getenv("LOG_LEVEL", level).upper()
    numeric_level = getattr(logging, effective_level, logging.INFO)

    fmt = "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S"

    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

    logging.basicConfig(
        level=numeric_level,
        format=fmt,
        datefmt=date_fmt,
        handlers=handlers,
        force=True,  # Reemplaza configuración previa de Streamlit
    )

    # Silenciar librerías externas ruidosas
    for noisy_lib in ["httpx", "httpcore", "urllib3", "anthropic._base_client"]:
        logging.getLogger(noisy_lib).setLevel(logging.WARNING)

    app_logger = logging.getLogger("levelup")
    app_logger.info(
        "Logging configurado — nivel: %s%s",
        effective_level,
        f" | archivo: {log_file}" if log_file else "",
    )


def get_logger(name: str) -> logging.Logger:
    """
    Retorna un logger prefijado con 'levelup.' para identificar
    fácilmente los logs de la aplicación vs. librerías externas.

    Args:
        name: Nombre del módulo, típicamente __name__.
    """
    clean_name = name.replace("src.", "").replace(".", "/")
    return logging.getLogger(f"levelup.{clean_name}")
