"""
tests/unit/application/test_repository_contracts.py
====================================================
Regresión del hallazgo P2 #9 de la auditoría de arquitectura (2026-09-05):
"el protocolo de estudiante declara métodos como `get_item` y
`get_available_items` que no están implementados con esos nombres, y omite
métodos consumidos como `get_items_from_db` y `get_answered_item_ids`".

Un protocolo que nadie comprueba no es un contrato, es un comentario con
sintaxis. Estas pruebas lo comprueban en las dos direcciones:

  1. Todo método declarado en un protocolo existe en AMBOS repositorios, con
     los mismos nombres de parámetro.
  2. Todo `self.repository.<algo>` que un servicio llama está declarado en su
     protocolo.

La (2) es la que atrapa el olvido normal: añadir una llamada al servicio y no
tocar el protocolo.
"""

import ast
import inspect
import pathlib

import pytest

from src.application.interfaces.repositories import (
    IAdminRepository,
    IRatingReadRepository,
    IStudentRepository,
    ITeacherRepository,
)
from src.infrastructure.persistence.postgres_repository import PostgresRepository
from src.infrastructure.persistence.sqlite_repository import SQLiteRepository

REPOS = [SQLiteRepository, PostgresRepository]
PROTOCOLS = [IStudentRepository, ITeacherRepository, IRatingReadRepository, IAdminRepository]

_SRC = pathlib.Path(__file__).resolve().parents[3] / "src"


def _protocol_methods(protocol) -> list[str]:
    return [
        name
        for name in dir(protocol)
        if not name.startswith("_") and callable(getattr(protocol, name, None))
    ]


def _params(func) -> list[str]:
    return [p for p in inspect.signature(func).parameters if p != "self"]


@pytest.mark.parametrize("protocol", PROTOCOLS, ids=lambda p: p.__name__)
@pytest.mark.parametrize("repo_cls", REPOS, ids=lambda c: c.__name__)
def test_every_declared_method_exists_in_both_engines(protocol, repo_cls):
    missing = [m for m in _protocol_methods(protocol) if not hasattr(repo_cls, m)]
    assert not missing, (
        f"{protocol.__name__} declara métodos que {repo_cls.__name__} no tiene: {missing}. "
        "O el repositorio los perdió, o el protocolo describe algo que no existe."
    )


@pytest.mark.parametrize("protocol", PROTOCOLS, ids=lambda p: p.__name__)
@pytest.mark.parametrize("repo_cls", REPOS, ids=lambda c: c.__name__)
def test_declared_signatures_match_the_implementation(protocol, repo_cls):
    """Los nombres de parámetro deben coincidir: los servicios llaman por keyword."""
    for name in _protocol_methods(protocol):
        declared = _params(getattr(protocol, name))
        actual = _params(getattr(repo_cls, name))
        assert declared == actual, (
            f"{protocol.__name__}.{name} declara {declared} pero "
            f"{repo_cls.__name__}.{name} recibe {actual}."
        )


def _repository_calls(service_path: pathlib.Path) -> set[str]:
    """Nombres en `self.repository.<algo>(...)` dentro de un servicio."""
    tree = ast.parse(service_path.read_text(encoding="utf-8"))
    found = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Attribute) or not isinstance(node.value, ast.Attribute):
            continue
        inner = node.value
        if (
            isinstance(inner.value, ast.Name)
            and inner.value.id == "self"
            and inner.attr == "repository"
        ):
            found.add(node.attr)
    return found


@pytest.mark.parametrize(
    "service_file, protocol",
    [
        ("application/services/student_service.py", IStudentRepository),
        ("application/services/teacher_service.py", ITeacherRepository),
        ("application/services/rating_read_service.py", IRatingReadRepository),
    ],
    ids=["student", "teacher", "rating_read"],
)
def test_everything_the_service_calls_is_declared(service_file, protocol):
    used = _repository_calls(_SRC / service_file)
    declared = set(_protocol_methods(protocol))
    undeclared = sorted(used - declared)
    assert not undeclared, (
        f"{service_file} llama a métodos ausentes de {protocol.__name__}: {undeclared}. "
        "Declararlos ahí — si no, el protocolo deja de describir al consumidor."
    )


@pytest.mark.parametrize("repo_cls", REPOS, ids=lambda c: c.__name__)
def test_repositories_satisfy_the_protocols_at_runtime(repo_cls):
    """isinstance() sobre un Protocol runtime_checkable: comprueba presencia."""
    fake = type("Fake", (), {m: (lambda self, *a, **k: None) for p in PROTOCOLS
                             for m in _protocol_methods(p)})()
    for protocol in PROTOCOLS:
        assert isinstance(fake, protocol)
        assert all(hasattr(repo_cls, m) for m in _protocol_methods(protocol))
