r"""Checks that running a script with pythonw.exe does not do the following.

1) create a new console
2) the console that pythonw.exe is executing in does not "flash"

If the script executes successfully, a new file \tests\check_pythonw.txt is created.

See Issue #31 https://github.com/MSLNZ/msl-loadlib/issues/31

Usage

  .\.venv\Scripts\pythonw.exe .\tests\check_pythonw.py

"""

import sys
from pathlib import Path

from msl.examples.loadlib import EXAMPLES_DIR, Cpp64
from msl.loadlib import LoadLibrary

if Path(sys.executable).name != "pythonw.exe":
    raise RuntimeError("Must run this script using,\n  pythonw.exe " + __file__)

sys.stdout = open(f"{__file__[:-3]}.txt", mode="w")  # noqa: PTH123, SIM115
sys.stderr = sys.stdout

with LoadLibrary(EXAMPLES_DIR / "Trig.class") as java:
    print(java)  # noqa: T201

with Cpp64() as cpp:
    print(cpp)  # noqa: T201

print("You should delete this file")  # noqa: T201
