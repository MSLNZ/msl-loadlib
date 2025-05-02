import sys
from pathlib import Path
from subprocess import PIPE, Popen

import pytest

from conftest import skipif_no_pythonnet, skipif_not_windows
from msl.loadlib import LoadLibrary

config_path = Path(sys.base_prefix) / f"{Path(sys.executable).name}.config"


def teardown_module() -> None:
    config_path.unlink(missing_ok=True)


@skipif_not_windows
@skipif_no_pythonnet
def test_framework_v2() -> None:
    # The python.exe.config file must exist before the Python interpreter
    # starts in order for pythonnet to load a library from .NET <4.0. That
    # is why we must use subprocess for this test. The 'legacy_v2_runtime.py'
    # script must be run in a different Python process which depends on
    # whether python.exe.config exists before the subprocess runs.
    #
    # This test also requires that the .NET Framework 3.5 is installed.
    # If it is not, this test will fail with a missing-dependency error:
    #
    #   System.IO.FileLoadException: Could not load file or assembly
    #   'legacy_v2_runtime_x64.dll' or one of its dependencies.
    #

    root_dir = Path(__file__).parent / "dotnet_config"
    script = root_dir / "legacy_v2_runtime.py"

    assert script.is_file()

    config_path.unlink(missing_ok=True)

    # the python.exe.config file gets created
    assert not config_path.is_file()
    p = Popen([sys.executable, script], stdout=PIPE, stderr=PIPE)  # noqa: S603
    stdout, stderr = p.communicate()
    assert not stdout
    assert b"useLegacyV2RuntimeActivationPolicy property was added" in stderr
    assert config_path.is_file()

    # the script now runs without error
    p = Popen([sys.executable, script], stdout=PIPE, stderr=PIPE)  # noqa: S603
    stdout, stderr = p.communicate()
    assert not stderr
    assert stdout.rstrip() == b"SUCCESS"

    # the above tests also depend on LoadLibrary raising OSError
    # if the DLL file does not exist
    with pytest.raises(OSError, match=r"Cannot find '.*legacy_v2_runtime.dll' for libtype='clr'"):
        _ = LoadLibrary(root_dir / "legacy_v2_runtime.dll", libtype="clr")
