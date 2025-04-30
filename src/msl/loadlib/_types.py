"""Custom types."""

from __future__ import annotations

import os
from typing import Literal

LibType = Literal["cdll", "windll", "oledll", "net", "clr", "java", "com", "activex"]
"""Supported library types."""

PathLike = str | bytes | os.PathLike[str] | os.PathLike[bytes]
"""A [path-like object][]{:target="_blank"}."""
