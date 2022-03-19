import os
import sys
from subprocess import (
    Popen,
    PIPE,
)

import pytest
from conftest import (
    skipif_not_windows,
    skipif_no_pythonnet,
)

from msl.loadlib import LoadLibrary

config_path = sys.executable + '.config'


def teardown_module():
    if os.path.isfile(config_path):
        os.remove(config_path)


@skipif_not_windows
@skipif_no_pythonnet
def test_framework_v2():
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

    root_dir = os.path.join(os.path.dirname(__file__), 'dotnet_config')
    script = os.path.join(root_dir, 'legacy_v2_runtime.py')

    assert os.path.isfile(script)

    if os.path.isfile(config_path):
        os.remove(config_path)

    # the python.exe.config file gets created
    assert not os.path.isfile(config_path)
    p = Popen([sys.executable, script], stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    assert not stdout
    assert b'useLegacyV2RuntimeActivationPolicy property was added' in stderr

    # the script now runs without error
    p = Popen([sys.executable, script], stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    assert not stderr
    assert stdout.rstrip() == b'SUCCESS'

    # the above tests also depend on LoadLibrary raising OSError
    # if the DLL file does not exist
    with pytest.raises(OSError, match=r"Cannot find '.*legacy_v2_runtime.dll' for libtype='clr'"):
        LoadLibrary(os.path.join(root_dir, 'legacy_v2_runtime.dll'), libtype='clr')
