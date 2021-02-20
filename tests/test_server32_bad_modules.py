import os
import sys

import pytest

from msl.loadlib import ConnectionTimeoutError, IS_MAC

sys.path.append(os.path.join(os.path.dirname(__file__), 'bad_servers'))
from client import Client


@pytest.mark.skipif(IS_MAC, reason='the 32-bit server for macOS does not exist')
def test_no_server32_subclass():
    with pytest.raises(ConnectionTimeoutError, match=r'Module does not contain a class that is a subclass of Server32'):
        Client('no_server32_subclass')


@pytest.mark.skipif(IS_MAC, reason='the 32-bit server for macOS does not exist')
def test_no_init():
    with pytest.raises(ConnectionTimeoutError, match=r'class NoInit\(Server32\):'):
        Client('no_init')


@pytest.mark.skipif(IS_MAC, reason='the 32-bit server for macOS does not exist')
def test_bad_init_args():
    with pytest.raises(ConnectionTimeoutError, match=r'class BadInitArgs\(Server32\):'):
        Client('bad_init_args')


@pytest.mark.skipif(IS_MAC, reason='the 32-bit server for macOS does not exist')
def test_no_super():
    with pytest.raises(ConnectionTimeoutError, match=r'class NoSuper\(Server32\):'):
        Client('no_super')


@pytest.mark.skipif(IS_MAC, reason='the 32-bit server for macOS does not exist')
def test_bad_super_init():
    with pytest.raises(ConnectionTimeoutError, match=r'class BadSuperInit\(Server32\):'):
        Client('bad_super_init')


@pytest.mark.skipif(IS_MAC, reason='the 32-bit server for macOS does not exist')
def test_bad_lib_path():
    with pytest.raises(ConnectionTimeoutError, match=r'Cannot find the shared library'):
        Client('bad_lib_path')


@pytest.mark.skipif(IS_MAC, reason='the 32-bit server for macOS does not exist')
def test_bad_lib_type():
    with pytest.raises(ConnectionTimeoutError, match=r'Cannot load libtype=invalid'):
        Client('bad_lib_type')


@pytest.mark.skipif(IS_MAC, reason='the 32-bit server for macOS does not exist')
def test_unexpected_error():
    with pytest.raises(ConnectionTimeoutError, match=r'ZeroDivisionError'):
        Client('unexpected_error')


@pytest.mark.skipif(IS_MAC, reason='the 32-bit server for macOS does not exist')
def test_wrong_bitness():
    with pytest.raises(ConnectionTimeoutError, match=r'Failed to load'):
        Client('wrong_bitness')
