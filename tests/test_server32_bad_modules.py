import os
import sys
try:
    ConnectionRefusedError
except NameError:  # Python 2
    import socket
    ConnectionRefusedError = socket.error

import pytest

from msl.loadlib import ConnectionTimeoutError

from conftest import skipif_no_server32

sys.path.append(os.path.join(os.path.dirname(__file__), 'bad_servers'))
from client import Client


def check(module_name, match):
    # This test module is a bit buggy.
    # Sometimes we get a ConnectionRefusedError that we want to ignore.
    attempts = 1

    # Set max_attempts to 1 to see if calling server_bind() and server_activate()
    # immediately before serve_forever() fixed the ConnectionRefusedError
    max_attempts = 1
    while True:
        try:
            with pytest.raises(ConnectionTimeoutError, match=match):
                Client(module_name)
        except ConnectionRefusedError:
            if attempts == max_attempts:
                raise
            attempts += 1
        else:
            break  # then this test was successful


@skipif_no_server32
def test_no_module():
    check('', r'specify a Python module')


@skipif_no_server32
def test_relative_import():
    check('.relative', r'Cannot perform relative imports')


@skipif_no_server32
def test_import_error():
    check('doesnotexist', r'module must be in sys.path')


@skipif_no_server32
def test_no_server32_subclass():
    check('no_server32_subclass', r'Module does not contain a class that is a subclass of Server32')


@skipif_no_server32
def test_no_init():
    check('no_init', r'class NoInit\(Server32\):')


@skipif_no_server32
def test_bad_init_args():
    check('bad_init_args', r'class BadInitArgs\(Server32\):')


@skipif_no_server32
def test_no_super():
    check('no_super', r'class NoSuper\(Server32\):')


@skipif_no_server32
def test_bad_super_init():
    check('bad_super_init', r'class BadSuperInit\(Server32\):')


@skipif_no_server32
def test_bad_lib_path():
    check('bad_lib_path', r"Cannot find 'doesnotexist' for libtype='cdll'")


@skipif_no_server32
def test_bad_lib_type():
    check('bad_lib_type', r"Cannot load libtype='invalid'")


@skipif_no_server32
def test_unexpected_error():
    check('unexpected_error', r'ZeroDivisionError')


@skipif_no_server32
def test_wrong_bitness():
    check('wrong_bitness', r'Failed to load')
