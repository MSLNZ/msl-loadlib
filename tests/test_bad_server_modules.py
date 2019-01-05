import os
import sys
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from msl.loadlib import ConnectionTimeoutError

sys.path.append(os.path.join(os.path.dirname(__file__), 'servers'))
from client import Client


def _raises(module32):
    sys.stderr = open('stdout.txt', 'w+')
    with pytest.raises(ConnectionTimeoutError):
        Client(module32)
    sys.stderr.seek(0)
    lines = sys.stderr.readlines()
    sys.stderr.close()
    os.remove('stdout.txt')
    return lines


def test_no_server32_subclass():
    stderr_lines = _raises('no_server32_subclass')
    assert 'Module does not contain a class that is a subclass of Server32.' == stderr_lines[1].strip()


def test_no_init():
    stderr_lines = _raises('no_init')
    assert 'class NoInit(Server32):' == stderr_lines[3].strip()


def test_bad_init_args():
    stderr_lines = _raises('bad_init_args')
    assert 'class BadInitArgs(Server32):' == stderr_lines[3].strip()


def test_no_super():
    stderr_lines = _raises('no_super')
    assert 'class NoSuper(Server32):' == stderr_lines[3].strip()


def test_bad_super_init():
    stderr_lines = _raises('bad_super_init')
    assert 'class BadSuperInit(Server32):' == stderr_lines[3].strip()


def test_bad_lib_path():
    stderr_lines = _raises('bad_lib_path')
    assert 'Cannot find the shared library' in stderr_lines[0]


def test_bad_lib_type():
    stderr_lines = _raises('bad_lib_type')
    assert 'Cannot load libtype=invalid' in stderr_lines[0]


def test_unexpected_error():
    stderr_lines = _raises('unexpected_error')
    assert 'ZeroDivisionError' in stderr_lines[0]


def test_wrong_bitness():
    stderr_lines = _raises('wrong_bitness')
    assert 'Failed to load' in stderr_lines[0]
