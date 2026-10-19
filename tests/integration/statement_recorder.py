"""
Spec 002 D1 (task T001): record every statement a repository issues, on both engines.

`record_statements(monkeypatch, repository_class)` wraps the connections the class hands out
(`get_connection`) in thin proxies; each `execute` is logged with the row count the driver
reports. Nothing else changes: the proxies delegate every other attribute, so a repository
built while recording behaves as it does in production.

    recorded = record_statements(monkeypatch, SQLiteRepository)
    SQLiteRepository(db_name=path)
    assert recorded.ddl() == [] and recorded.writes() == []
"""

import re

_DDL = re.compile(r"^\s*(CREATE|ALTER|DROP)\b", re.IGNORECASE)
_DML = re.compile(r"^\s*(INSERT|UPDATE|DELETE)\b", re.IGNORECASE)


def _text(statement) -> str:
    return statement.decode() if isinstance(statement, bytes) else str(statement)


class Recorded:
    def __init__(self):
        self.statements: list[tuple[str, int]] = []

    def ddl(self) -> list[str]:
        """Every CREATE, ALTER or DROP issued, whether or not it changed the schema."""
        return [sql for sql, _ in self.statements if _DDL.match(sql)]

    def writes(self) -> list[tuple[str, int]]:
        """Every INSERT, UPDATE or DELETE that changed at least one row."""
        return [(sql, n) for sql, n in self.statements if _DML.match(sql) and n > 0]

    def matching(self, pattern: str) -> list[str]:
        return [sql for sql, _ in self.statements if re.search(pattern, sql, re.IGNORECASE)]


class _Cursor:
    def __init__(self, inner, recorded):
        object.__setattr__(self, "_inner", inner)
        object.__setattr__(self, "_recorded", recorded)

    def execute(self, statement, *params):
        result = self._inner.execute(statement, *params)
        self._recorded.statements.append((_text(statement), self._inner.rowcount))
        # sqlite3 returns the cursor (chained .fetchone()); psycopg2 returns None.
        return self if result is self._inner else result

    def executemany(self, statement, rows):
        result = self._inner.executemany(statement, rows)
        self._recorded.statements.append((_text(statement), self._inner.rowcount))
        return self if result is self._inner else result

    def __iter__(self):
        return iter(self._inner)

    def __enter__(self):
        self._inner.__enter__()
        return self

    def __exit__(self, *exc):
        return self._inner.__exit__(*exc)

    def __getattr__(self, name):
        return getattr(self._inner, name)

    def __setattr__(self, name, value):
        setattr(self._inner, name, value)


class _Connection:
    def __init__(self, inner, recorded):
        object.__setattr__(self, "_inner", inner)
        object.__setattr__(self, "_recorded", recorded)

    def cursor(self, *args, **kwargs):
        return _Cursor(self._inner.cursor(*args, **kwargs), self._recorded)

    def execute(self, statement, *params):  # sqlite3 shortcut
        return self.cursor().execute(statement, *params)

    def executemany(self, statement, rows):  # sqlite3 shortcut
        return self.cursor().executemany(statement, rows)

    def __enter__(self):
        self._inner.__enter__()
        return self

    def __exit__(self, *exc):
        return self._inner.__exit__(*exc)

    def __getattr__(self, name):
        return getattr(self._inner, name)

    def __setattr__(self, name, value):
        setattr(self._inner, name, value)


def record_statements(monkeypatch, repository_class) -> Recorded:
    """Record every statement issued through `repository_class` connections from now on."""
    recorded = Recorded()
    original_get = repository_class.get_connection

    def get_connection(self, *args, **kwargs):
        return _Connection(original_get(self, *args, **kwargs), recorded)

    monkeypatch.setattr(repository_class, "get_connection", get_connection)
    original_put = getattr(repository_class, "put_connection", None)
    if original_put is not None:  # PostgreSQL: the pool must get its own connection back

        def put_connection(self, conn):
            original_put(self, conn._inner if isinstance(conn, _Connection) else conn)

        monkeypatch.setattr(repository_class, "put_connection", put_connection)
    return recorded
