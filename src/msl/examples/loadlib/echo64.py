"""An example of a 64-bit *echo* client.

[Echo32][] is the 32-bit server class and [Echo64][] is the 64-bit client class.
These *Echo* classes do not actually communicate with a library. The point of these
*Echo* classes is to show that a Python data type in a 64-bit process appears as
the same data type in the 32-bit process and vice versa
(*provided that the data type is [pickle][]{:target="_blank"}able.*)
"""

from __future__ import annotations

import os
from typing import Any

from msl.loadlib import Client64


class Echo64(Client64):
    """Example that shows Python data types are preserved between [Echo32][] and [Echo64][]."""

    def __init__(self) -> None:
        """Example that shows Python data types are preserved between [Echo32][] and [Echo64][]."""
        super().__init__(module32="echo32", append_sys_path=os.path.dirname(__file__))

    def send_data(self, *args: Any, **kwargs: Any) -> tuple[tuple[Any, ...], dict[str, Any]]:
        """Send a request to [Echo32.received_data][msl.examples.loadlib.echo32.Echo32.received_data].

        Args:
            args: The arguments to send.
            kwargs: The keyword arguments to send.

        Returns:
            The `args` and `kwargs` that were sent.
        """
        return self.request32("received_data", *args, **kwargs)
