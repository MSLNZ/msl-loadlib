import pytest

from msl.loadlib import Client64, IS_MAC
from msl.examples.loadlib import Cpp64


@pytest.mark.skipif(IS_MAC, reason='the 32-bit server for macOS does not exist')
def test_unclosed_pipe_warning(recwarn):
    # recwarn is a built-in pytest fixture that records all warnings emitted by test functions

    # The following warnings should not be written to stderr for the unclosed subprocess PIPE's
    #   sys:1: ResourceWarning: unclosed file <_io.BufferedReader name=3>
    #   sys:1: ResourceWarning: unclosed file <_io.BufferedReader name=4>

    Cpp64()
    assert recwarn.list == []


def test_unraisable_exception_warning():
    # The point of this test is to verify that the PytestUnraisableExceptionWarning
    # does not get written to the terminal at the end of this test.
    #
    # This test will always pass (so it is deceptive) but what the user must
    # pay attention to is whether a warning message similar to the following
    # is displayed in the "warnings summary" of pytest:
    #
    # Exception ignored in: <function Client64.__del__ at 0x000001BFBD402B80>
    # Traceback (most recent call last):
    #   File "...client64.py", line 368, in __del__
    #     if self._conn is not None:
    # AttributeError: 'DivZero' object has no attribute '_conn'
    #
    # For more details see:
    # https://docs.pytest.org/en/stable/usage.html#warning-about-unraisable-exceptions-and-unhandled-thread-exceptions

    class DivZero(Client64):
        def __init__(self):
            1/0

    with pytest.raises(ZeroDivisionError):
        DivZero()