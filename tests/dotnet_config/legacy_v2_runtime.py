import sys
from pathlib import Path

import clr  # type: ignore[import-untyped] # pyright: ignore[reportUnusedImport,reportMissingTypeStubs] # noqa: F401

from msl.loadlib import IS_PYTHON_64BIT, LoadLibrary

bitness = "x64" if IS_PYTHON_64BIT else "x86"
filename = f"legacy_v2_runtime_{bitness}.dll"
path = Path(__file__).parent / "legacy_v2_runtime" / filename

net = LoadLibrary(path, libtype="net")

expected = "Microsoft Visual Studio 2005 (Version 8.0.50727.42); Microsoft .NET Framework (Version 2.0.50727)"
environment = net.lib.legacy.Build().Environment()
if environment != expected:
    sys.exit(f"{environment!r} != {expected!r}")

print("SUCCESS")  # noqa: T201
