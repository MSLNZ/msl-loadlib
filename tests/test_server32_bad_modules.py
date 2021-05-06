import os
import sys

import pytest

from msl.loadlib import ConnectionTimeoutError, IS_MAC

sys.path.append(os.path.join(os.path.dirname(__file__), 'bad_servers'))
from client import Client

skipif_macos = pytest.mark.skipif(IS_MAC, reason='the 32-bit server for macOS does not exist')


@skipif_macos
def test_no_server32_subclass():
    with pytest.raises(ConnectionTimeoutError, match=r'Module does not contain a class that is a subclass of Server32'):
        Client('no_server32_subclass')


@skipif_macos
def test_no_init():
    with pytest.raises(ConnectionTimeoutError, match=r'class NoInit\(Server32\):'):
        Client('no_init')


@skipif_macos
def test_bad_init_args():
    with pytest.raises(ConnectionTimeoutError, match=r'class BadInitArgs\(Server32\):'):
        Client('bad_init_args')


@skipif_macos
def test_no_super():
    with pytest.raises(ConnectionTimeoutError, match=r'class NoSuper\(Server32\):'):
        Client('no_super')


@skipif_macos
def test_bad_super_init():
    with pytest.raises(ConnectionTimeoutError, match=r'class BadSuperInit\(Server32\):'):
        Client('bad_super_init')


@skipif_macos
def test_bad_lib_path():
    with pytest.raises(ConnectionTimeoutError, match=r"Cannot find 'doesnotexist' for libtype='cdll'"):
        Client('bad_lib_path')


@skipif_macos
def test_bad_lib_type():
    with pytest.raises(ConnectionTimeoutError, match=r"Cannot load libtype='invalid'"):
        Client('bad_lib_type')


@skipif_macos
def test_unexpected_error():
    with pytest.raises(ConnectionTimeoutError, match=r'ZeroDivisionError'):
        Client('unexpected_error')


@skipif_macos
def test_wrong_bitness():
    with pytest.raises(ConnectionTimeoutError, match=r'Failed to load'):
        Client('wrong_bitness')
