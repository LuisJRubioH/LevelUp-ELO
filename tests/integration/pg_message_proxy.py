"""
Spec 002 D2 (task T001): a TCP proxy that counts the queries a client sends to PostgreSQL.

psycopg2 speaks the simple-query protocol: every statement it sends — the query itself, and the
`BEGIN` and `ROLLBACK` it adds around a transaction — is one `Q` message, one round trip. The
proxy parses the client→server stream (startup packet, then `type byte + int32 length` frames)
and counts the `Q` frames; it forwards every byte unchanged. Local only: the tests point it at
POSTGRES_TEST_DATABASE_URL with sslmode=disable, so the stream is plain.

    with MessageProxy("localhost", 5432) as proxy:
        url = proxy.url_for(database_url)
        ...
        proxy.queries.clear(); repo.get_user_by_id(1); assert len(proxy.queries) == 1
"""

import socket
import struct
import threading
from urllib.parse import urlsplit, urlunsplit


class MessageProxy:
    def __init__(self, host: str, port: int):
        self.target = (host, port)
        self.queries: list[str] = []
        self._lock = threading.Lock()
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.bind(("127.0.0.1", 0))
        self._server.listen(16)
        self.port = self._server.getsockname()[1]
        self._closed = False

    def url_for(self, database_url: str) -> str:
        parts = urlsplit(database_url)
        auth = parts.netloc.rsplit("@", 1)[0] + "@" if "@" in parts.netloc else ""
        return urlunsplit(parts._replace(netloc=f"{auth}127.0.0.1:{self.port}"))

    def __enter__(self):
        threading.Thread(target=self._accept, daemon=True).start()
        return self

    def __exit__(self, *exc):
        self._closed = True
        self._server.close()

    def _accept(self):
        while not self._closed:
            try:
                client, _ = self._server.accept()
            except OSError:
                return
            upstream = socket.create_connection(self.target)
            threading.Thread(
                target=self._client_to_server, args=(client, upstream), daemon=True
            ).start()
            threading.Thread(target=self._pipe, args=(upstream, client), daemon=True).start()

    @staticmethod
    def _pipe(source, sink):
        try:
            while data := source.recv(65536):
                sink.sendall(data)
        except OSError:
            pass
        finally:
            for s in (source, sink):
                try:
                    s.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass

    def _client_to_server(self, client, upstream):
        buffer = b""
        started = False
        try:
            while data := client.recv(65536):
                upstream.sendall(data)
                buffer += data
                while True:
                    if not started:  # startup packet: int32 length, no type byte
                        if len(buffer) < 4:
                            break
                        (length,) = struct.unpack("!I", buffer[:4])
                        if len(buffer) < length:
                            break
                        buffer, started = buffer[length:], True
                        continue
                    if len(buffer) < 5:
                        break
                    kind = buffer[:1]
                    (length,) = struct.unpack("!I", buffer[1:5])
                    if len(buffer) < 1 + length:
                        break
                    if kind == b"Q":
                        text = buffer[5 : 1 + length].rstrip(b"\0").decode("utf-8", "replace")
                        with self._lock:
                            self.queries.append(text)
                    buffer = buffer[1 + length :]
        except OSError:
            pass
        finally:
            for s in (client, upstream):
                try:
                    s.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
