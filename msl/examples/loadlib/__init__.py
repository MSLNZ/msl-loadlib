"""
Example modules showing how to load a 32-bit shared library in 64-bit Python.
"""
import os

from .cpp32 import (
    Cpp32,
    Point,
    FourPoints,
    NPoints,
)
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

EXAMPLES_DIR = os.path.abspath(os.path.dirname(__file__))
