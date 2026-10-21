"""
api/single_process.py
=====================
Spec 007 FR-052 (AGENTS.md R18): one API process per host in production, whatever starts it.

`uvicorn --workers N` and gunicorn start N processes, each running the lifespan, and none of them
sees `WEB_CONCURRENCY`. Each process takes an exclusive, non-blocking lock on one host file and
keeps it for its whole life: the first gets it, any other fails and refuses to start. The lock
belongs to the open file, so it dies with the process — a restart never meets a stale lock. It
cannot see a second machine (decision O-L2): `render.yaml` runs one instance.
"""

import os

SECOND_PROCESS = (
    "Ya hay otro proceso de la API en este servidor: PvP y las notificaciones viven en la "
    "memoria de UN proceso, y con dos los jugadores de procesos distintos no se emparejan. "
    "Arranca un solo worker (sin --workers, WEB_CONCURRENCY=1) — ver AGENTS.md R18."
)


def hold_single_process_lock(path: str):
    """Take the host lock at `path` and return its open file, which must stay referenced for the
    life of the process. Raises RuntimeError when another process holds it. POSIX only, like
    the production host; `fcntl` does not exist on Windows."""
    import fcntl

    handle = open(path, "a+")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        handle.close()
        raise RuntimeError(SECOND_PROCESS) from None
    handle.seek(0)
    handle.truncate()
    handle.write(str(os.getpid()))
    handle.flush()
    return handle
