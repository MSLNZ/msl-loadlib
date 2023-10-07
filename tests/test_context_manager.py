import logging
import os
from ctypes import CDLL

import pytest
from py4j.java_gateway import JVMView
from py4j.java_gateway import JavaGateway

from conftest import skipif_no_pythonnet
from conftest import skipif_no_server32
from msl.examples.loadlib import Cpp64
from msl.examples.loadlib import EXAMPLES_DIR
from msl.loadlib import LoadLibrary
from msl.loadlib.constants import DEFAULT_EXTENSION
from msl.loadlib.constants import IS_PYTHON_64BIT
from msl.loadlib.load_library import DotNet
from msl.loadlib.utils import logger

suffix = '64' if IS_PYTHON_64BIT else '32'


def test_raises():
    with pytest.raises(OSError, match=r'^Cannot find'):
        with LoadLibrary('doesnotexist'):
            pass

    path = os.path.join(EXAMPLES_DIR, 'Trig.class')
    with pytest.raises(ValueError, match=r'^Invalid libtype'):
        with LoadLibrary(path, libtype='invalid'):
            pass


def test_cpp():
    path = os.path.join(EXAMPLES_DIR, 'cpp_lib' + suffix + DEFAULT_EXTENSION)
    with LoadLibrary(path) as library:
        assert library.assembly is None
        assert library.gateway is None
        assert library.path == path
        assert isinstance(library.lib, CDLL)
        assert library.lib.add(1, 2) == 3
    assert library.path == path
    assert library.assembly is None
    assert library.gateway is None
    assert library.lib is None

    # can still call this (even multiple times)
    for _ in range(10):
        library.cleanup()

    assert 'libtype=NoneType' in str(library)
    assert 'libtype=NoneType' in repr(library)


@skipif_no_pythonnet
def test_dotnet():
    path = os.path.join(EXAMPLES_DIR, f'dotnet_lib{suffix}.dll')
    with LoadLibrary(path, libtype='net') as library:
        assert isinstance(library.assembly, library.lib.System.Reflection.Assembly)
        assert library.assembly is not None
        assert library.gateway is None
        assert library.path == path
        assert isinstance(library.lib, DotNet)
        assert library.lib.DotNetMSL.BasicMath().add_integers(1, 2) == 3
    assert library.path == path
    assert library.assembly is None
    assert library.gateway is None
    assert library.lib is None

    # can still call this (even multiple times)
    for _ in range(10):
        library.cleanup()

    assert 'libtype=NoneType' in str(library)
    assert 'libtype=NoneType' in repr(library)


def test_java(caplog):
    caplog.set_level(logging.DEBUG, logger.name)
    path = os.path.join(EXAMPLES_DIR, 'Trig.class')
    with LoadLibrary(path) as library:
        assert library.assembly is None
        assert isinstance(library.gateway, JavaGateway)
        assert library.path == path
        assert isinstance(library.lib, JVMView)
        assert library.lib.Trig.cos(0.0) == 1.0
    assert library.path == path
    assert library.assembly is None
    assert library.gateway is None
    assert library.lib is None

    record = caplog.records[0]
    assert record.levelname == 'DEBUG'
    assert record.msg == 'Loaded %s'

    record = caplog.records[1]
    assert record.levelname == 'DEBUG'
    assert record.msg == 'shutdown Py4J.GatewayServer'

    # can still call this (even multiple times)
    for _ in range(10):
        library.cleanup()

    assert 'libtype=NoneType' in str(library)
    assert 'libtype=NoneType' in repr(library)


@skipif_no_server32
def test_client():
    with Cpp64() as cpp:
        assert cpp.connection is not None
        assert cpp.add(1, -1) == 0
    assert cpp.connection is None

    # can still call this (even multiple times)
    for _ in range(10):
        out, err = cpp.shutdown_server32()
        assert out.closed
        assert err.closed

    with Cpp64() as cpp:
        out, err = cpp.shutdown_server32()
        assert not out.closed
        assert not err.closed
        assert out.read() == b''
        assert err.read() == b''
    out, err = cpp.shutdown_server32()
    assert out.closed
    assert err.closed

    assert 'lib=None address=None' in str(cpp)
    assert 'lib=None address=None' in repr(cpp)
