"""
tests/unit/test_architecture_layers.py
=======================================
R2 comprobado, no solo escrito. Del hallazgo P2 #9 de la auditoría
(2026-09-05): "los servicios importan el cliente de IA de infraestructura; el
dominio contiene carga de archivos pickle, entrenamiento y dependencias
numpy/sklearn".

Las capas solo son capas si algo las sostiene:

    domain/         → sin imports de capas superiores ni de librerías externas
    application/    → importa domain/, NO infrastructure/
    infrastructure/ → implementa lo que domain/ y application/ declaran
    interface/, api/→ pueden importar todo (son la composición)
"""

import ast
import pathlib
import re

import pytest

_SRC = pathlib.Path(__file__).resolve().parents[2] / "src"

# Librerías que no pueden aparecer en domain/: el dominio es aritmética y reglas,
# no I/O ni modelos entrenados. `pickle` salió de aquí con IsotonicCalibrator.
_FORBIDDEN_IN_DOMAIN = {"numpy", "sklearn", "pandas", "pickle", "psycopg2", "sqlite3", "requests"}


def _modules(layer: str) -> list[pathlib.Path]:
    return sorted((_SRC / layer).rglob("*.py"))


def _imported_names(path: pathlib.Path) -> set[str]:
    """Módulos importados, incluidos los locales dentro de funciones."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.add(node.module)
    return names


def _ids(paths):
    return [str(p.relative_to(_SRC)) for p in paths]


@pytest.mark.parametrize("path", _modules("application"), ids=_ids(_modules("application")))
def test_application_does_not_import_infrastructure(path):
    offenders = sorted(
        name for name in _imported_names(path) if name.startswith("src.infrastructure")
    )
    assert not offenders, (
        f"{path.name} importa infraestructura: {offenders}. La capa de aplicación declara lo "
        "que necesita y la composición (api/routers, streamlit/app.py) se lo inyecta."
    )


@pytest.mark.parametrize("path", _modules("domain"), ids=_ids(_modules("domain")))
def test_domain_does_not_import_upper_layers(path):
    offenders = sorted(
        name
        for name in _imported_names(path)
        if name.startswith(("src.application", "src.infrastructure", "src.interface", "api."))
    )
    assert not offenders, f"{path.name} importa capas superiores: {offenders}."


@pytest.mark.parametrize("path", _modules("domain"), ids=_ids(_modules("domain")))
def test_domain_stays_free_of_io_and_ml_dependencies(path):
    offenders = sorted(
        name for name in _imported_names(path) if name.split(".")[0] in _FORBIDDEN_IN_DOMAIN
    )
    assert not offenders, (
        f"{path.name} depende de {offenders}. Eso es infraestructura: va en "
        "src/infrastructure/ y se inyecta (así se movió IsotonicCalibrator)."
    )


# ── Spec 001 (T061): rating arithmetic lives in the domain, not in SQL or routers ──

_RATING_SQL = re.compile(
    r"AVG\(\s*[\w.]*(current_elo|elo_after)|ORDER BY[^\"\n]*\b(current_elo|elo_after)\b",
    re.IGNORECASE,
)


def test_spec001_no_rating_aggregation_in_repositories_or_routers():
    """Constitution III (supplementary to the behavioural tests): repositories return raw rows and
    participants; routers present what RatingReadService computed."""
    root = _SRC.parent
    files = sorted((_SRC / "infrastructure" / "persistence").glob("*_repository.py"))
    files += sorted((root / "api" / "routers").glob("*.py"))
    offenders = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        for match in _RATING_SQL.finditer(text):
            line = text[: match.start()].count("\n") + 1
            offenders.append(f"{path.name}:{line}: {match.group(0)[:60]}")
        imported = _imported_names(path)
        for module in ("src.domain.elo.aggregation", "src.domain.elo.ranks"):
            if module in imported:
                offenders.append(f"{path.name}: imports {module}")
    assert not offenders, "\n".join(offenders)
