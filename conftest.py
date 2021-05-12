import os
import sys

import pytest

from msl import loadlib


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
        not_windows = lambda: pytest.skip('operating system is not Windows')
    else:
        not_windows = lambda: None

    if loadlib.IS_MAC:
        is_mac = lambda: pytest.skip('operating system is macOS')
    else:
        is_mac = lambda: None

    if loadlib.IS_PYTHON_64BIT:
        bit64 = lambda: pytest.skip('requires 32-bit Python')
        bit32 = lambda: None
    else:
        bit64 = lambda: None
        bit32 = lambda: pytest.skip('requires 64-bit Python')

    if loadlib.IS_PYTHON_64BIT and has_labview_runtime():
        no_labview64 = lambda: None
    else:
        no_labview64 = lambda: pytest.skip('requires 64-bit LabVIEW Run-Time Engine')

    no_labview32 = lambda: pytest.skip('requires 32-bit LabVIEW Run-Time Engine -- not even checking if installed')

    doctest_namespace['SKIP_IF_PYTHON_2'] = py2
    doctest_namespace['SKIP_IF_PYTHON_LESS_THAN_3_6'] = less_36
    doctest_namespace['SKIP_IF_NOT_WINDOWS'] = not_windows
    doctest_namespace['SKIP_IF_MACOS'] = is_mac
    doctest_namespace['SKIP_IF_64BIT'] = bit64
    doctest_namespace['SKIP_IF_32BIT'] = bit32
    doctest_namespace['SKIP_IF_LABVIEW64_NOT_INSTALLED'] = no_labview64
    doctest_namespace['SKIP_LABVIEW32'] = no_labview32
