import os
import sys
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from msl.loadlib import ConnectionTimeoutError

sys.path.append(os.path.join(os.path.dirname(__file__), 'servers'))
from client import Client


def test_no_server32_subclass():
    sys.stderr = open('stdout.txt', 'w+')
    with pytest.raises(ConnectionTimeoutError):
        Client('no_server32_subclass')
    sys.stderr.seek(0)
    assert 'Module does not contain a class that is a subclass of Server32.' == sys.stderr.readlines()[1].strip()
    sys.stderr.close()
    os.remove('stdout.txt')


def test_no_init():
    sys.stderr = open('stdout.txt', 'w+')
    with pytest.raises(ConnectionTimeoutError):
        Client('no_init')
    sys.stderr.seek(0)
    assert 'class NoInit(Server32):' == sys.stderr.readlines()[3].strip()
    sys.stderr.close()
    os.remove('stdout.txt')


def test_bad_init_args():
    sys.stderr = open('stdout.txt', 'w+')
    with pytest.raises(ConnectionTimeoutError):
        Client('bad_init_args')
    sys.stderr.seek(0)
    assert 'class BadInitArgs(Server32):' == sys.stderr.readlines()[3].strip()
    sys.stderr.close()
    os.remove('stdout.txt')


def test_bad_super_init():
    sys.stderr = open('stdout.txt', 'w+')
    with pytest.raises(ConnectionTimeoutError):
        Client('bad_super_init')
    sys.stderr.seek(0)
    assert 'class BadSuperArgs(Server32):' == sys.stderr.readlines()[3].strip()
    sys.stderr.close()
    os.remove('stdout.txt')


def test_bad_lib_path():
    sys.stderr = open('stdout.txt', 'w+')
    with pytest.raises(ConnectionTimeoutError):
        Client('bad_lib_path')
    sys.stderr.seek(0)
    assert 'Cannot find the shared library' in sys.stderr.readlines()[0]
    sys.stderr.close()
    os.remove('stdout.txt')


def test_bad_lib_type():
    sys.stderr = open('stdout.txt', 'w+')
    with pytest.raises(ConnectionTimeoutError):
        Client('bad_lib_type')
    sys.stderr.seek(0)
    assert 'Cannot load libtype=invalid' in sys.stderr.readlines()[0]
    sys.stderr.close()
    os.remove('stdout.txt')


def test_unexpected_error():
    sys.stderr = open('stdout.txt', 'w+')
    with pytest.raises(ConnectionTimeoutError):
        Client('unexpected_error')
    sys.stderr.seek(0)
    assert 'ZeroDivisionError' in sys.stderr.readlines()[0]
    sys.stderr.close()
    os.remove('stdout.txt')


def test_wrong_bitness():
    sys.stderr = open('stdout.txt', 'w+')
    with pytest.raises(ConnectionTimeoutError):
        Client('wrong_bitness')
    sys.stderr.seek(0)
    assert 'Failed to load' in sys.stderr.readlines()[0]
    sys.stderr.close()
    os.remove('stdout.txt')
