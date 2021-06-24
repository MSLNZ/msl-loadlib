import os
import sys
import random

import clr

path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
sys.path.insert(0, path)

from msl.loadlib import (
    IS_PYTHON_64BIT,
    LoadLibrary,
)

bitness = 'x64' if IS_PYTHON_64BIT else 'x86'
filename = 'legacy_v2_runtime_{}.dll'.format(bitness)
path = os.path.abspath(os.path.join(os.path.dirname(__file__), filename))

# this is not necessary, just wanted to randomly select
# one of the supported .NET libtype's
libtype = 'clr' if random.random() > 0.5 else 'net'

net = LoadLibrary(path, libtype)

# pythonnet 3.0+ disabled implicit conversion from C# enums to Python int and back.
# One must now either use enum members (e.g. MyEnum.Option), or use enum constructor
# (e.g. MyEnum(42) or MyEnum(42, True) when MyEnum does not have a member with value 42).

if int(clr.__version__.split('.')[0]) < 3:
    if net.lib.SpelNetLib.SpelAxis.X != 1:
        sys.exit('error accessing enum "net.lib.SpelNetLib.SpelAxis.X"')
else:
    if net.lib.SpelNetLib.SpelAxis.X != net.lib.SpelNetLib.SpelAxis(1):
        sys.exit('error accessing enum "net.lib.SpelNetLib.SpelAxis.X"')

print('SUCCESS')
