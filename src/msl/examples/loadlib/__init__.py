"""Examples showing how to load a 32-bit library in 64-bit Python."""

from __future__ import annotations

from pathlib import Path

from .cpp32 import Cpp32, FourPoints, NPoints, Point
from .cpp64 import Cpp64
from .dotnet32 import DotNet32
from .dotnet64 import DotNet64
from .echo32 import Echo32
from .echo64 import Echo64
from .fortran32 import Fortran32
from .fortran64 import Fortran64
from .kernel32 import Kernel32
from .kernel64 import Kernel64
from .labview32 import Labview32
from .labview64 import Labview64

EXAMPLES_DIR: Path = Path(__file__).parent

__all__: list[str] = [
    "Cpp32",
    "Cpp64",
    "DotNet32",
    "DotNet64",
    "Echo32",
    "Echo64",
    "Fortran32",
    "Fortran64",
    "FourPoints",
    "Kernel32",
    "Kernel64",
    "Labview32",
    "Labview64",
    "NPoints",
    "Point",
]
