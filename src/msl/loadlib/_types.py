"""Custom types."""

from __future__ import annotations

import os
import sys
from typing import Literal

LibType = Literal["cdll", "windll", "oledll", "net", "clr", "java", "com", "activex"]
"""Supported library types."""

if sys.version_info[:2] > (3, 9):
    PathLike = str | bytes | os.PathLike[str] | os.PathLike[bytes]
    """A [path-like object][]{:target="_blank"}."""
else:
    from typing import Union  # pyright: ignore[reportDeprecated]
    PathLike = Union[str, bytes, os.PathLike]  # pyright: ignore[reportMissingTypeArgument, reportDeprecated]
