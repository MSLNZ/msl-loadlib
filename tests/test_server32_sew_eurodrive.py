from pathlib import Path

from conftest import skipif_not_windows, xfail_windows_ga
from msl.loadlib import Client64


@xfail_windows_ga
@skipif_not_windows
def test_sew_eurodrive() -> None:
    """The reason for creating this test case was discussed through email.

    The LoadLibrary class has been modified so that clr.AddReference is
    called before clr.System.Reflection.Assembly.LoadFile is called.
    The order of execution was important for the example .NET DLL
    provided by an engineer at SEW-EURODRIVE.
    """

    class SEWEuroDrive64(Client64):
        def __init__(self) -> None:
            super().__init__(Path(__file__).parent / "sew_eurodrive" / "sew32.py")

        def do_something(self, value: float) -> float:
            result: float = self.request32("do_something", value)
            return result

    with SEWEuroDrive64() as sew:
        assert sew.do_something(600) == 100.0
