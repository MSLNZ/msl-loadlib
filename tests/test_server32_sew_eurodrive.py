import os

import pytest

from msl.loadlib import IS_MAC, IS_LINUX, Client64


@pytest.mark.skipif(IS_MAC or IS_LINUX, reason='only valid on Windows')
def test_sew_eurodrive():
    """
    The reason for creating this test case was discussed through email.
    The LoadLibrary class has been modified so that clr.AddReference is
    called before clr.System.Reflection.Assembly.LoadFile is called.
    The order of execution was important for the example .NET DLL
    provided by an engineer at SEW-EURODRIVE.
    """

    class SEWEuroDrive64(Client64):

        def __init__(self):
            super(SEWEuroDrive64, self).__init__(
                os.path.join(os.path.dirname(__file__), 'sew_eurodrive', 'sew32.py')
            )

        def do_something(self, value):
            return self.request32('do_something', value)

    sew = SEWEuroDrive64()
    assert sew.do_something(600) == 100
