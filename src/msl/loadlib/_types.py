"""Custom types."""

import os
import sys
from typing import Literal, TypeVar

LibType = Literal["cdll", "windll", "oledll", "net", "clr", "java", "com", "activex"]
"""Supported library types."""


if sys.version_info[:2] > (3, 8):
    PathLike = TypeVar("PathLike", str, bytes, os.PathLike[str], os.PathLike[bytes])
    """A [path-like object][]{:target="_blank"}."""
else:
    PathLike = TypeVar("PathLike", str, bytes, os.PathLike)  # pyright: ignore[reportMissingTypeArgument]
