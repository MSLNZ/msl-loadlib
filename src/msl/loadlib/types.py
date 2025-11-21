"""Custom types."""

from __future__ import annotations

import os
from socket import socket as _socket  # noqa: TC003
from typing import Literal, Protocol, Union  # pyright: ignore[reportDeprecated]

LibType = Literal["cdll", "windll", "oledll", "net", "clr", "java", "com", "activex"]
"""Supported library types."""

PathLike = Union[str, bytes, os.PathLike[str], os.PathLike[bytes]]  # pyright: ignore[reportDeprecated]
"""A [path-like object][]{:target="_blank"}."""


class Server32Subclass(Protocol):
    """An subclass of [Server32][msl.loadlib.server32.Server32]."""

    socket: _socket
    path: str

    def __init__(self, host: str | None, port: int, **kwargs: str) -> None:
        """Base class for loading a 32-bit library in 32-bit Python."""

    def serve_forever(self) -> None:
        """Handle one request at a time until [shutdown][msl.loadlib.types.Server32Subclass.shutdown]."""

    def server_activate(self) -> None:
        """Called by constructor to activate the server."""

    def server_bind(self) -> None:
        """Called by constructor to bind the socket."""

    def server_close(self) -> None:
        """Called to clean-up the server."""

    def shutdown(self) -> None:
        """Stops the [serve_forever][msl.loadlib.types.Server32Subclass.serve_forever] loop."""

    def shutdown_handler(self) -> None:
        """Called just before the server shuts down."""
