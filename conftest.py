import os
import platform
import sys

import pytest

try:
    import clr
except (ImportError, RuntimeError):
    clr = None

from msl.loadlib.constants import *

# Using the --doctest-modules option with pytest for an implicit
# namespace package does not work properly, see
#   https://github.com/pytest-dev/pytest/issues/1927
#   https://github.com/pytest-dev/pytest/issues/2371
#   https://github.com/pytest-dev/pytest/issues/5147
#   https://github.com/pytest-dev/pytest/issues/6966
# Consider using the hack in msl-nlf (where a hack with Sybil is used)
# instead of the following hack that adds loadlib to sys.modules
from msl import loadlib
sys.modules['loadlib'] = loadlib


def add_py4j_in_eggs():
    # if py4j is located in the .eggs directory and not in the site-packages directory
    # then the py4j*.jar file cannot be found, so we need to create a PY4J_JAR env variable
    import py4j
    os.environ['PY4J_JAR'] = os.path.join(
        '.eggs',
        f'py4j-{py4j.__version__}-py{sys.version_info.major}.{sys.version_info.minor}.egg',
        'share',
        'py4j',
        f'py4j{py4j.__version__}.jar'
    )


def has_labview_runtime():
    if IS_PYTHON_64BIT:
        root = r'C:\Program Files\National Instruments\Shared\LabVIEW Run-Time'
    else:
        root = r'C:\Program Files (x86)\National Instruments\Shared\LabVIEW Run-Time'

    if not os.path.isdir(root):
        return False

    for item in os.listdir(root):
        path = os.path.join(root, item, 'lvrt.dll')
        if os.path.isfile(path):
            return True

    return False


@pytest.fixture(autouse=True)
def doctest_skipif(doctest_namespace):

    if not IS_WINDOWS:
        not_windows = lambda: pytest.skip('not Windows')
        readme_com = lambda: pytest.skip('skipped at COM test')
    else:
        not_windows = lambda: None
        readme_com = lambda: None

    if IS_MAC:
        is_mac = lambda: pytest.skip('is macOS')
    else:
        is_mac = lambda: None

    if IS_PYTHON_64BIT:
        bit64 = lambda: pytest.skip('requires 32-bit Python')
        bit32 = lambda: None
    else:
        bit64 = lambda: None
        bit32 = lambda: pytest.skip('requires 64-bit Python')

    if not IS_PYTHON_64BIT or (sys.platform == 'darwin' and platform.machine() == 'arm64'):
        readme_all = lambda: pytest.skip('skipped all tests')
    else:
        readme_all = lambda: None

    if IS_PYTHON_64BIT and has_labview_runtime():
        no_labview64 = lambda: None
    else:
        no_labview64 = lambda: pytest.skip('requires 64-bit LabVIEW Run-Time Engine')

    no_labview32 = lambda: pytest.skip('not checking if 32-bit LabVIEW is installed')

    if clr is None:
        readme_dotnet = lambda: pytest.skip('skipped at .NET test')
        no_pythonnet = lambda: pytest.skip('pythonnet is not installed')
    else:
        readme_dotnet = lambda: None
        no_pythonnet = lambda: None

    if IS_WINDOWS and os.getenv('GITHUB_ACTIONS') == 'true':
        win32_github_actions = lambda: pytest.skip('flaky test on Windows and GA')
    else:
        win32_github_actions = lambda: None

    doctest_namespace['SKIP_IF_WINDOWS_GITHUB_ACTIONS'] = win32_github_actions
    doctest_namespace['SKIP_IF_NOT_WINDOWS'] = not_windows
    doctest_namespace['SKIP_IF_MACOS'] = is_mac
    doctest_namespace['SKIP_IF_64BIT'] = bit64
    doctest_namespace['SKIP_IF_32BIT'] = bit32
    doctest_namespace['SKIP_IF_LABVIEW64_NOT_INSTALLED'] = no_labview64
    doctest_namespace['SKIP_LABVIEW32'] = no_labview32
    doctest_namespace['SKIP_README_DOTNET'] = readme_dotnet
    doctest_namespace['SKIP_README_COM'] = readme_com
    doctest_namespace['SKIP_README_ALL'] = readme_all
    doctest_namespace['SKIP_IF_NO_PYTHONNET'] = no_pythonnet


skipif_no_comtypes = pytest.mark.skipif(
    not IS_WINDOWS,
    reason='comtypes is only supported on Windows'
)
skipif_no_labview_runtime = pytest.mark.skipif(
    not has_labview_runtime(),
    reason='requires LabVIEW Run-Time Engine'
)
skipif_no_pythonnet = pytest.mark.skipif(
    clr is None,
    reason='pythonnet is not installed'
)
skipif_no_server32 = pytest.mark.skipif(
    IS_MAC,
    reason='32-bit server does not exist'
)
skipif_not_windows = pytest.mark.skipif(
    not IS_WINDOWS,
    reason='not Windows'
)

xfail_windows_ga = pytest.mark.xfail(
    IS_WINDOWS and os.getenv('GITHUB_ACTIONS') == 'true',
    reason='flaky test on Windows and GA'
)
