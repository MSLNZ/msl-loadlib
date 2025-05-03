# pyright reports a reportUnknownMemberType warning for pytest.approx
# pyright: reportUnknownMemberType=false
from __future__ import annotations

import math
import os
from pathlib import Path
from typing import Any, Callable

import pytest

from conftest import IS_MAC, IS_WINDOWS, skipif_no_server32, skipif_not_windows
from msl import loadlib
from msl.examples.loadlib import Cpp64, DotNet64, Echo64, Fortran64, FourPoints, Point
from msl.loadlib import ConnectionTimeoutError

c: Cpp64 | None = None
f: Fortran64 | None = None
e: Echo64 | None = None
n: DotNet64 | None = None


def setup_module() -> None:
    global c, f, e, n  # noqa: PLW0603
    if IS_MAC:  # the 32-bit server for macOS does not exist
        return
    c = Cpp64()
    f = Fortran64()
    e = Echo64()
    if IS_WINDOWS:
        # Stop testing on 64-bit linux because Mono can load both 32-bit and 64-bit libraries

        # This is flaky on GitHub Actions with Windows (connecting to the server sometimes times out)
        try:
            n = DotNet64()
        except ConnectionTimeoutError:
            pytest.xfail("flaky test with .NET, Windows and GA")


def teardown_module() -> None:
    if IS_MAC:  # the 32-bit server for macOS does not exist
        return
    assert c is not None
    assert f is not None
    assert e is not None
    _ = c.shutdown_server32()
    _ = f.shutdown_server32()
    _ = e.shutdown_server32()
    if n is not None:
        _ = n.shutdown_server32()


@skipif_no_server32
def test_unique_ports() -> None:
    for obj1 in [c, f, e, n]:
        for obj2 in [c, f, e, n]:
            if obj1 is None or obj2 is None or obj1 is obj2:
                continue
            assert obj1.port != obj2.port


@skipif_no_server32
def test_lib_name() -> None:
    def get_name(path: str) -> str:
        return Path(path).name.split(".")[0]

    assert c is not None
    assert f is not None
    assert get_name(c.lib32_path) == "cpp_lib32"
    assert get_name(f.lib32_path) == "fortran_lib32"
    if n is not None:
        assert get_name(n.lib32_path) == "dotnet_lib32"


@skipif_no_server32
def test_server_version() -> None:
    assert loadlib.Server32.version().startswith("Python")


@skipif_no_server32
def test_cpp() -> None:
    assert c is not None
    assert c.add(1, 2) == 3
    assert c.add(-1000, -2) == -1002
    assert pytest.approx(c.subtract(20.0, 10.0)) == 10.0
    assert pytest.approx(c.subtract(90.0, 100.0)) == -10.0
    assert pytest.approx(c.add_or_subtract(0.1234, -0.1234, do_addition=True)) == 0.0
    assert pytest.approx(c.add_or_subtract(123.456, 23.456, do_addition=False)) == 100.0

    a = 3.1415926
    values = [float(x) for x in range(100)]
    c_values = c.scalar_multiply(a, values)
    for i in range(len(values)):
        assert pytest.approx(c_values[i]) == a * values[i]

    assert c.reverse_string_v1("1234567890") == "0987654321"
    assert c.reverse_string_v2("&* 1 j z|x cba[") == "[abc x|z j 1 *&"

    fp = FourPoints(Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0))
    assert c.distance_4_points(fp) == 4.0

    assert c.circumference(0.5, 0) == 0.0
    assert c.circumference(0.5, 2) == 2.0
    assert c.circumference(0.5, 2**16) == pytest.approx(math.pi)
    assert c.circumference(1.0, 2**16) == pytest.approx(2.0 * math.pi)


@skipif_no_server32
def test_fortran() -> None:
    assert f is not None
    assert f.sum_8bit(-(2**7), 1) == -127
    assert f.sum_16bit(2**15 - 1, -1) == 32766
    assert f.sum_32bit(123456788, 1) == 123456789
    assert f.sum_64bit(-(2**63), 1) == -9223372036854775807
    assert pytest.approx(f.multiply_float32(40.874, -1284.131)) == -52487.570494
    assert pytest.approx(f.multiply_float64(1.1e100, 2.1e200)) == 2.31e300
    assert f.is_positive(1e-100)
    assert not f.is_positive(-1e-100)
    assert f.add_or_subtract(1000, 2000, do_addition=True) == 3000
    assert f.add_or_subtract(1000, 2000, do_addition=False) == -1000
    assert int(f.factorial(0)) == 1
    assert int(f.factorial(1)) == 1
    assert int(f.factorial(5)) == 120
    assert pytest.approx(f.standard_deviation([float(val) for val in range(1, 10)])) == 2.73861278752583
    assert pytest.approx(f.besselJ0(8.0)) == 0.171650807137
    assert f.reverse_string("hello world!") == "!dlrow olleh"

    a = [float(val) for val in range(1, 1000)]
    b = [3.0 * val for val in range(1, 1000)]
    f_values = f.add_1d_arrays(a, b)
    for i in range(len(a)):
        assert pytest.approx(f_values[i]) == a[i] + b[i]

    f_mat = f.matrix_multiply([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    assert pytest.approx(f_mat[0][0]) == 22.0
    assert pytest.approx(f_mat[0][1]) == 28.0
    assert pytest.approx(f_mat[1][0]) == 49.0
    assert pytest.approx(f_mat[1][1]) == 64.0


@skipif_no_server32
def test_echo() -> None:
    assert e is not None
    args, kwargs = e.send_data(True)  # noqa: FBT003
    assert args[0]
    assert isinstance(args[0], bool)
    assert not kwargs

    args, kwargs = e.send_data(x=1.0)
    assert not args
    assert kwargs == {"x": 1.0}

    x = list(range(100))
    y = range(9999)
    my_dict = {"x": x, "y": y, "text": "abcd 1234 wxyz"}  # cSpell: ignore wxyz
    args, kwargs = e.send_data(111, 2.3, complex(-1.2, 2.30), (1, 2), x=x, y=y, my_dict=my_dict)
    assert args[0] == 111
    assert args[1] == 2.3
    assert args[2] == complex(-1.2, 2.30)
    assert args[3] == (1, 2)
    assert kwargs["x"] == x
    assert kwargs["y"] == y
    assert kwargs["my_dict"] == my_dict


@skipif_not_windows
def test_dotnet() -> None:
    assert n is not None
    names = n.get_class_names()
    assert len(names) == 4
    assert "StringManipulation" in names
    assert "DotNetMSL.BasicMath" in names
    assert "DotNetMSL.ArrayManipulation" in names
    assert "StaticClass" in names

    assert n.add_integers(4, 5) == 9
    assert pytest.approx(n.divide_floats(4.0, 5.0)) == 0.8
    assert pytest.approx(n.multiply_doubles(872.24, 525.525)) == 458383.926
    assert pytest.approx(n.add_or_subtract(99.0, 9.0, do_addition=True)) == 108.0
    assert pytest.approx(n.add_or_subtract(99.0, 9.0, do_addition=False)) == 90.0

    a = 7.13141
    values = [float(x) for x in range(1000)]
    net_values = n.scalar_multiply(a, values)
    for i in range(len(values)):
        assert pytest.approx(net_values[i]) == a * values[i]

    assert n.reverse_string("New Zealand") == "dnalaeZ weN"

    net_mat = n.multiply_matrices([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    assert pytest.approx(net_mat[0][0]) == 22.0
    assert pytest.approx(net_mat[0][1]) == 28.0
    assert pytest.approx(net_mat[1][0]) == 49.0
    assert pytest.approx(net_mat[1][1]) == 64.0

    assert n.add_multiple(11, -22, 33, -44, 55) == 33
    assert n.concatenate("the ", "experiment ", "worked ", False, "temporarily") == "the experiment worked "  # noqa: FBT003
    assert n.concatenate("the ", "experiment ", "worked ", True, "temporarily") == "the experiment worked temporarily"  # noqa: FBT003


@skipif_no_server32
def test_unicode_path() -> None:
    class Cpp64Encoding(loadlib.Client64):
        def __init__(self) -> None:
            dir_name = Path(__file__).parent
            super().__init__(
                "cpp32unicode",
                append_sys_path=f"{dir_name}/uñicödé",
                append_environ_path=f"{dir_name}/uñicödé",
            )

        def add(self, a: int, b: int) -> int:
            out: int = self.request32("add", a, b)
            return out

    c2 = Cpp64Encoding()
    assert c2.add(-5, 3) == -2

    with pytest.raises(loadlib.Server32Error):
        _ = c2.add("hello", "world")  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]

    try:
        _ = c2.add("hello", "world")  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
    except loadlib.Server32Error as err:
        assert isinstance(str(err), str)  # noqa: PT017

    _ = c2.shutdown_server32()


@skipif_no_server32
def test_server32_error() -> None:
    assert c is not None
    try:
        _ = c.add("hello", "world")  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
    except loadlib.Server32Error as err:
        assert err.name == "ArgumentError"  # noqa: PT017
        assert "argument 1: TypeError:" in err.value  # noqa: PT017
        assert err.traceback.endswith("result: int = self.lib.add(a, b)")  # noqa: PT017


@skipif_not_windows
def test_comtypes_ctypes_union_error() -> None:
    # Changes to ctypes in Python 3.7.6 and 3.8.1 caused the following exception
    #   TypeError: item 1 in _argtypes_ passes a union by value, which is unsupported.
    # when loading some COM objects, see https://bugs.python.org/issue16575
    #
    # Want to make sure that the Python interpreter that the server32-windows.exe
    # is running on does not raise this TypeError

    class FileSystemObjectClient(loadlib.Client64):
        def __init__(self) -> None:
            super().__init__(
                "ctypes_union_error",
                append_sys_path=Path(__file__).parent / "server32_comtypes",
            )

        def __getattr__(self, name: str) -> Callable[..., Any]:
            def send(*args: Any, **kwargs: Any) -> Any:
                return self.request32(name, *args, **kwargs)

            return send

    file_system = FileSystemObjectClient()
    file_system.create_and_write("foo<bar<baz>>")

    temp_file = Path(file_system.get_temp_file())
    source = temp_file.read_text().strip()
    assert source == "foo<bar<baz>>"
    temp_file.unlink()

    _ = file_system.shutdown_server32()


@skipif_not_windows
def test_comtypes_shell32() -> None:
    class Shell64(loadlib.Client64):
        def __init__(self) -> None:
            super().__init__(
                "shell32.py",
                append_sys_path=Path(__file__).parent / "server32_comtypes",
            )

        def environ(self, key: str) -> str:
            value: str = self.request32("environ", key)
            return value

    shell = Shell64()

    for name in ["PROCESSOR_IDENTIFIER", "NUMBER_OF_PROCESSORS"]:
        assert shell.environ(name) == os.environ[name]

    _ = shell.shutdown_server32()


@skipif_not_windows
def test_activex() -> None:
    class ActiveX(loadlib.Client64):
        def __init__(self) -> None:
            super().__init__(
                "activex_media_player.py",
                append_sys_path=Path(__file__).parent / "server32_comtypes",
                timeout=30,
            )

        def this(self) -> bool:
            reply: bool = self.request32("this")
            return reply

        def reload(self) -> bool:
            reply: bool = self.request32("reload")
            return reply

        def load_library(self) -> bool:
            reply: bool = self.request32("load_library")
            return reply

        def error1(self) -> str:
            reply: str = self.request32("error1")
            return reply

        def error2(self) -> str:
            reply: str = self.request32("error2")
            return reply

    ax = ActiveX()

    # don't care whether the value is True or False only that it is a boolean
    assert isinstance(ax.this(), bool)
    assert isinstance(ax.reload(), bool)
    assert isinstance(ax.load_library(), bool)
    assert ax.error1().endswith("Cannot find an ActiveX library with ID 'ABC.DEF.GHI'")
    assert ax.error2().endswith("Cannot find an ActiveX library with ID 'ABC.DEF.GHI'")

    # no numpy warnings from comtypes
    out, err = ax.shutdown_server32()
    assert not out.read()
    assert not err.read()
    out.close()
    err.close()
