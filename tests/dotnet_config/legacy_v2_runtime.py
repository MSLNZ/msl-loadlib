import os
import random
import sys

import clr

# make sure 'msl.loadlib' is available on PATH before importing it
path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
sys.path.insert(0, path)

from msl.loadlib import LoadLibrary
from msl.loadlib.constants import IS_PYTHON_64BIT

bitness = 'x64' if IS_PYTHON_64BIT else 'x86'
filename = f'legacy_v2_runtime_{bitness}.dll'
path = os.path.join(os.path.dirname(__file__), 'legacy_v2_runtime', filename)

# this is not necessary, just wanted to randomly select
# one of the supported .NET libtype's
libtype = 'clr' if random.random() > 0.5 else 'net'

net = LoadLibrary(path, libtype=libtype)

expected = 'Microsoft Visual Studio 2005 (Version 8.0.50727.42); Microsoft .NET Framework (Version 2.0.50727)'
environment = net.lib.legacy.Build().Environment()
if environment != expected:
    sys.exit(f'{environment!r} != {expected!r}')

print('SUCCESS')
