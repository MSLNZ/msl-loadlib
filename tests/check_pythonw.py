"""
Checks that running a script with pythonw.exe does not
1) create a new console
2) the console that pythonw.exe is executing on does not "flash"
"""
import os
import sys

# make sure that msl.loadlib is importable
path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, path)

from msl.loadlib import LoadLibrary
from msl.examples.loadlib import (
    EXAMPLES_DIR,
    Cpp64,
)

if os.path.basename(sys.executable) != 'pythonw.exe':
    raise RuntimeError(
        'Must run this script using,\n'
        '  pythonw.exe ' + __file__
    )

with LoadLibrary(os.path.join(EXAMPLES_DIR, 'Trig.class')) as java:
    pass

with Cpp64():
    pass
