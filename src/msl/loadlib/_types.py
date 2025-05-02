"""Custom types."""

from __future__ import annotations

import os
from socket import socket as _socket  # noqa: TC003
from typing import Literal, Protocol

LibType = Literal["cdll", "windll", "oledll", "net", "clr", "java", "com", "activex"]
"""Supported library types."""

PathLike = str | bytes | os.PathLike[str] | os.PathLike[bytes]
"""A [path-like object][]{:target="_blank"}."""


class Server32Subclass(Protocol):
    socket: _socket
    path: str

    def __init__(self, host: str | None, port: int, **kwargs: str) -> None: ...
    def serve_forever(self) -> None: ...
    def server_activate(self) -> None: ...
    def server_bind(self) -> None: ...
    def server_close(self) -> None: ...
    def shutdown(self) -> None: ...
    def shutdown_handler(self) -> None: ...
