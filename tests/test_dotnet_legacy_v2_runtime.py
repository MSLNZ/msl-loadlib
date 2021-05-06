import os
import sys
from subprocess import (
    Popen,
    PIPE,
)

import pytest

from msl.loadlib import (
    LoadLibrary,
    IS_WINDOWS,
)

config_path = sys.executable + '.config'


def teardown_module():
    # clean up
    if os.path.isfile(config_path):
        os.remove(config_path)


@pytest.mark.skipif(not IS_WINDOWS, reason='only valid on Windows')
def test_framework_3_5():
    # The python.exe.config file must exist before the Python interpreter
    # starts in order for pythonnet to load a library from .NET <4.0. That
    # is why we must use subprocess for this test. The 'legacy_v2_runtime.py'
    # script must be run in a different Python process which depends on
    # whether python.exe.config exists before the subprocess runs.

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

    # the above tests also depend on LoadLibrary raising IOError
    # if the DLL file does not exist
    with pytest.raises(IOError, match=r"Cannot find '.*legacy_v2_runtime.dll' for libtype='cdll'"):
        LoadLibrary(os.path.join(root_dir, 'legacy_v2_runtime.dll'))
