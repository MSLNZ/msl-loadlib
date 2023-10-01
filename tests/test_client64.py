import gc

import pytest

from conftest import skipif_no_server32
from msl.examples.loadlib import Cpp64
from msl.loadlib import Client64
from msl.loadlib.constants import SERVER_FILENAME


@skipif_no_server32
def test_unclosed_warnings_1(recwarn):
    # recwarn is a built-in pytest fixture that records all warnings emitted by test functions

    # The following warnings should not be written to stderr for the unclosed subprocess PIPE's
    #   sys:1: ResourceWarning: unclosed file <_io.BufferedReader name=3>
    #   sys:1: ResourceWarning: unclosed file <_io.BufferedReader name=4>
    # nor for unclosed sockets
    #   ResourceWarning: unclosed <socket.socket ...>

    Cpp64()
    gc.collect()
    assert len(recwarn) == 0


@skipif_no_server32
def test_unclosed_warnings_2(recwarn):
    for _ in range(3):
        cpp = Cpp64()
        out, err = cpp.shutdown_server32()
        for _ in range(10):
            out.close()
            err.close()
        del cpp
    gc.collect()
    assert len(recwarn) == 0


def test_bad_del():
    # Make sure that the following exception is not raised in Client64.__del__
    #   AttributeError: 'BadDel' object has no attribute '_conn'

    class BadDel(Client64):
        def __init__(self):
            pass

    b = BadDel()
    b.__del__()
    del b

    with BadDel():
        pass

    # this should raise AttributeError because super() was not called in BadDel
    with pytest.raises(AttributeError, match='_conn'):
        BadDel().request32('request')


def test_invalid_server32_dir():
    with pytest.raises(OSError, match=rf'^Cannot find {SERVER_FILENAME}$'):
        Client64(__file__, server32_dir='')
