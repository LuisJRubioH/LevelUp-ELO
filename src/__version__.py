"""
src/__version__.py
==================
Versión semántica de LevelUp-ELO.

Convención: MAJOR.MINOR.PATCH
  MAJOR: cambios incompatibles de API o arquitectura (Streamlit → FastAPI en V2.0)
  MINOR: nuevas funcionalidades retrocompatibles (nuevos cursos, nuevos paneles)
  PATCH: bug fixes y mejoras menores

V2.0.0: migración a FastAPI + React + nuevas features (PWA, Examen, Logros, Notificaciones WS)
Ver ROADMAP_V2.md y CHANGELOG.md para el historial completo.
"""

__version__ = "2.0.0"
__version_info__ = (2, 0, 0)
