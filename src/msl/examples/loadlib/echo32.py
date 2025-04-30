"""An example of a 32-bit *echo* server.

[Echo32][] is the 32-bit server class and [Echo64][] is the 64-bit client class.
These *Echo* classes do not actually communicate with a library. The point of these
*Echo* classes is to show that a Python data type in a 64-bit process appears as
the same data type in the 32-bit process and vice versa.
(*provided that the data type is [pickle][]{:target="_blank"}able.*)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from msl.loadlib import Server32


class Echo32(Server32):
    """Example that shows Python data types are preserved between [Echo32][] and [Echo64][]."""

    def __init__(self, host: str, port: int) -> None:
        """Example that shows Python data types are preserved between [Echo32][] and [Echo64][].

        Args:
            host: The IP address (or hostname) to use for the server.
            port: The port to open for the server.
        """
        # even though this is a *echo* class that does not call a library
        # we still need to provide a library file that exists. Use the C++ library.
        path = Path(__file__).parent / "cpp_lib32"
        super().__init__(path, "cdll", host, port)

    @staticmethod
    def received_data(*args: Any, **kwargs: Any) -> tuple[tuple[Any, ...], dict[str, Any]]:  # type: ignore[misc]
        """Process a request from the [Echo64.send_data][msl.examples.loadlib.echo64.Echo64.send_data] method.

        Args:
            args: The arguments.
            kwargs: The keyword arguments.

        Returns:
            The `args` and `kwargs` that were received.
        """
        return args, kwargs
