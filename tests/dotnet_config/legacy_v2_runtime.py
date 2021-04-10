import os
import sys
import random

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

if net.lib.SpelNetLib.SpelAxis.X != 1:
    sys.exit('SpelAxis.X != 1')

print('SUCCESS')
