import os
import sys

import pytest
try:
    import clr
except ImportError:
    clr = None


from msl import loadlib


def add_py4j_in_eggs():
    # if py4j is located in the .eggs directory and not in the site-packages directory
    # then the py4j*.jar file cannot be found, so we need to create a PY4J_JAR env variable
    import py4j
    os.environ['PY4J_JAR'] = os.path.join(
        '.eggs',
        'py4j-{}-py{}.{}.egg'.format(py4j.__version__, sys.version_info.major, sys.version_info.minor),
        'share',
        'py4j',
        'py4j{}.jar'.format(py4j.__version__)
    )


def has_labview_runtime():
    if loadlib.IS_PYTHON_64BIT:
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

    if loadlib.IS_PYTHON2:
        py2 = lambda: pytest.skip('requires Python 3')
    else:
        py2 = lambda: None

    if sys.version_info[:2] < (3, 6):
        less_36 = lambda: pytest.skip('ignore Python <3.6 since dict does not preserve insertion order')
    else:
        less_36 = lambda: None

    if not loadlib.IS_WINDOWS:
        not_windows = lambda: pytest.skip('not Windows')
        readme_com = lambda: pytest.skip('skipped at COM test')
    else:
        not_windows = lambda: None
        readme_com = lambda: None

    if loadlib.IS_MAC:
        is_mac = lambda: pytest.skip('is macOS')
    else:
        is_mac = lambda: None

    if loadlib.IS_PYTHON_64BIT:
        bit64 = lambda: pytest.skip('requires 32-bit Python')
        bit32 = lambda: None
        readme_all = lambda: None
    else:
        bit64 = lambda: None
        bit32 = lambda: pytest.skip('requires 64-bit Python')
        readme_all = lambda: pytest.skip('skipped all tests')

    if loadlib.IS_PYTHON_64BIT and has_labview_runtime():
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

    doctest_namespace['SKIP_IF_PYTHON_2'] = py2
    doctest_namespace['SKIP_IF_PYTHON_LESS_THAN_3_6'] = less_36
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
    not loadlib.IS_WINDOWS,
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
    loadlib.IS_MAC,
    reason='32-bit server does not exist'
)
skipif_not_windows = pytest.mark.skipif(
    not loadlib.IS_WINDOWS,
    reason='not Windows'
)
