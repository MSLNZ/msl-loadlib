import os
import sys

import pytest

from msl.loadlib import ConnectionTimeoutError, IS_MAC

sys.path.append(os.path.join(os.path.dirname(__file__), 'bad_servers'))
from client import Client

skipif_macos = pytest.mark.skipif(IS_MAC, reason='the 32-bit server for macOS does not exist')


def check(module_name, match):
    # This test module is a bit buggy.
    # Sometimes we get a ConnectionRefusedError that we want to ignore.
    attempts = 1
    max_attempts = 3
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


@skipif_macos
def test_no_server32_subclass():
    check('no_server32_subclass', r'Module does not contain a class that is a subclass of Server32')


@skipif_macos
def test_no_init():
    check('no_init', r'class NoInit\(Server32\):')


@skipif_macos
def test_bad_init_args():
    check('bad_init_args', r'class BadInitArgs\(Server32\):')


@skipif_macos
def test_no_super():
    check('no_super', r'class NoSuper\(Server32\):')


@skipif_macos
def test_bad_super_init():
    check('bad_super_init', r'class BadSuperInit\(Server32\):')


@skipif_macos
def test_bad_lib_path():
    check('bad_lib_path', r"Cannot find 'doesnotexist' for libtype='cdll'")


@skipif_macos
def test_bad_lib_type():
    check('bad_lib_type', r"Cannot load libtype='invalid'")


@skipif_macos
def test_unexpected_error():
    check('unexpected_error', r'ZeroDivisionError')


@skipif_macos
def test_wrong_bitness():
    check('wrong_bitness', r'Failed to load')
