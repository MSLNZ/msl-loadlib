from pathlib import Path

import pytest

from conftest import skipif_no_server32
from msl.loadlib import Client64, ConnectionTimeoutError


class Client(Client64):
    def __init__(self, module32: str) -> None:
        super().__init__(module32, append_sys_path=Path(__file__).parent / "bad_servers", timeout=5)


def check(module_name: str, match: str) -> None:
    # This test module is a bit buggy.
    # Sometimes we get a ConnectionRefusedError that we want to ignore.
    attempts = 1

    max_attempts = 3
    while True:
        try:
            with pytest.raises(ConnectionTimeoutError, match=match):
                _ = Client(module_name)
        except ConnectionRefusedError:  # noqa: PERF203
            if attempts == max_attempts:
                raise
            attempts += 1
        else:
            break  # then this test was successful


@skipif_no_server32
def test_no_module() -> None:
    check("", r"specify a Python module")


@skipif_no_server32
def test_relative_import() -> None:
    check(".relative", r"Cannot perform relative imports")


@skipif_no_server32
def test_import_error() -> None:
    # the module import_error.py exists, but the module imports a package that does not exist
    check("import_error", r"No module named 'missing'")


@skipif_no_server32
def test_import_error2() -> None:
    check("doesnotexist", r"module must be in sys.path")


@skipif_no_server32
def test_no_server32_subclass() -> None:
    check("no_server32_subclass", r"Module does not contain a class that is a subclass of Server32")


@skipif_no_server32
def test_no_init() -> None:
    check("no_init", r"class NoInit\(Server32\):")


@skipif_no_server32
def test_bad_init_args() -> None:
    check("bad_init_args", r"class BadInitArgs\(Server32\):")


@skipif_no_server32
def test_bad_init_args2() -> None:
    check("bad_init_args2", r"missing 1 required positional argument: 'extra'")


@skipif_no_server32
def test_no_super() -> None:
    check("no_super", r"class NoSuper\(Server32\):")


@skipif_no_server32
def test_bad_super_init() -> None:
    check("bad_super_init", r"class BadSuperInit\(Server32\):")


@skipif_no_server32
def test_bad_lib_path() -> None:
    check("bad_lib_path", r"Cannot find 'doesnotexist' for libtype='cdll'")


@skipif_no_server32
def test_bad_lib_type() -> None:
    check("bad_lib_type", r"ValueError: Invalid libtype 'invalid'")


@skipif_no_server32
def test_unexpected_error() -> None:
    check("unexpected_error", r"ZeroDivisionError")


@skipif_no_server32
def test_unexpected_error2() -> None:
    check("unexpected_error2", r"TypeError: unsupported operand")


@skipif_no_server32
def test_unexpected_error3() -> None:
    check("unexpected_error3", r"NameError: name 'y' is not defined")


@skipif_no_server32
def test_wrong_bitness() -> None:
    check("wrong_bitness", r"Failed to load")
