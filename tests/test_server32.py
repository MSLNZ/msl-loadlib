import math
import os
from typing import Optional

import pytest

from conftest import skipif_no_server32
from conftest import skipif_not_windows
from msl import loadlib
from msl.examples.loadlib import Cpp64
from msl.examples.loadlib import DotNet64
from msl.examples.loadlib import Echo64
from msl.examples.loadlib import Fortran64
from msl.examples.loadlib import FourPoints
from msl.examples.loadlib import Point
from msl.loadlib import ConnectionTimeoutError
from msl.loadlib.constants import IS_MAC
from msl.loadlib.constants import IS_WINDOWS

c: Optional[Cpp64] = None
f: Optional[Fortran64] = None
e: Optional[Echo64] = None
n: Optional[DotNet64] = None


def setup_module():
    global c, f, e, n
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


def teardown_module():
    if IS_MAC:  # the 32-bit server for macOS does not exist
        return
    c.shutdown_server32()
    f.shutdown_server32()
    e.shutdown_server32()
    if n is not None:
        n.shutdown_server32()


@skipif_no_server32
def test_unique_ports():
    for obj1 in [c, f, e, n]:
        for obj2 in [c, f, e, n]:
            if obj1 is None or obj2 is None or obj1 is obj2:
                continue
            assert obj1.port != obj2.port


@skipif_no_server32
def test_lib_name():
    def get_name(path):
        return os.path.basename(path).split(".")[0]

    assert "cpp_lib32" == get_name(c.lib32_path)
    assert "fortran_lib32" == get_name(f.lib32_path)
    if n is not None:
        assert "dotnet_lib32" == get_name(n.lib32_path)


@skipif_no_server32
def test_server_version():
    assert loadlib.Server32.version().startswith("Python")


@skipif_no_server32
def test_cpp():
    assert 3 == c.add(1, 2)
    assert -1002 == c.add(-1000, -2)
    assert 10.0 == pytest.approx(c.subtract(20.0, 10.0))
    assert -10.0 == pytest.approx(c.subtract(90.0, 100.0))
    assert 0.0 == pytest.approx(c.add_or_subtract(0.1234, -0.1234, True))
    assert 100.0 == pytest.approx(c.add_or_subtract(123.456, 23.456, False))

    a = 3.1415926
    values = [float(x) for x in range(100)]
    c_values = c.scalar_multiply(a, values)
    for i in range(len(values)):
        assert a * values[i] == pytest.approx(c_values[i])

    assert "0987654321" == c.reverse_string_v1("1234567890")
    assert "[abc x|z j 1 *&" == c.reverse_string_v2("&* 1 j z|x cba[")

    fp = FourPoints(Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0))
    assert c.distance_4_points(fp) == 4.0

    assert c.circumference(0.5, 0) == 0.0
    assert c.circumference(0.5, 2) == 2.0
    assert c.circumference(0.5, 2**16) == pytest.approx(math.pi)
    assert c.circumference(1.0, 2**16) == pytest.approx(2.0 * math.pi)


@skipif_no_server32
def test_fortran():
    assert -127 == f.sum_8bit(-(2**7), 1)
    assert 32766 == f.sum_16bit(2**15 - 1, -1)
    assert 123456789 == f.sum_32bit(123456788, 1)
    assert -9223372036854775807 == f.sum_64bit(-(2**63), 1)
    assert -52487.570494 == pytest.approx(f.multiply_float32(40.874, -1284.131))
    assert 2.31e300 == pytest.approx(f.multiply_float64(1.1e100, 2.1e200))
    assert f.is_positive(1e-100)
    assert not f.is_positive(-1e-100)
    assert 3000 == f.add_or_subtract(1000, 2000, True)
    assert -1000 == f.add_or_subtract(1000, 2000, False)
    assert 1 == int(f.factorial(0))
    assert 1 == int(f.factorial(1))
    assert 120 == int(f.factorial(5))
    assert 2.73861278752583 == pytest.approx(f.standard_deviation([float(val) for val in range(1, 10)]))
    assert 0.171650807137 == pytest.approx(f.besselJ0(8.0))
    assert "!dlrow olleh" == f.reverse_string("hello world!")

    a = [float(val) for val in range(1, 1000)]
    b = [3.0 * val for val in range(1, 1000)]
    f_values = f.add_1d_arrays(a, b)
    for i in range(len(a)):
        assert a[i] + b[i] == pytest.approx(f_values[i])

    f_mat = f.matrix_multiply([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    assert 22.0 == pytest.approx(f_mat[0][0])
    assert 28.0 == pytest.approx(f_mat[0][1])
    assert 49.0 == pytest.approx(f_mat[1][0])
    assert 64.0 == pytest.approx(f_mat[1][1])


@skipif_no_server32
def test_echo():
    args, kwargs = e.send_data(True)
    assert args[0]
    assert isinstance(args[0], bool)
    assert not kwargs

    args, kwargs = e.send_data(x=1.0)
    assert not args
    assert kwargs == {"x": 1.0}

    x = [val for val in range(100)]
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
def test_dotnet():
    names = n.get_class_names()
    assert len(names) == 4
    assert "StringManipulation" in names
    assert "DotNetMSL.BasicMath" in names
    assert "DotNetMSL.ArrayManipulation" in names
    assert "StaticClass" in names

    assert 9 == n.add_integers(4, 5)
    assert 0.8 == pytest.approx(n.divide_floats(4.0, 5.0))
    assert 458383.926 == pytest.approx(n.multiply_doubles(872.24, 525.525))
    assert 108.0 == pytest.approx(n.add_or_subtract(99.0, 9.0, True))
    assert 90.0 == pytest.approx(n.add_or_subtract(99.0, 9.0, False))

    a = 7.13141
    values = [float(x) for x in range(1000)]
    net_values = n.scalar_multiply(a, values)
    for i in range(len(values)):
        assert a * values[i] == pytest.approx(net_values[i])

    assert n.reverse_string("New Zealand") == "dnalaeZ weN"

    net_mat = n.multiply_matrices([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    assert 22.0 == pytest.approx(net_mat[0][0])
    assert 28.0 == pytest.approx(net_mat[0][1])
    assert 49.0 == pytest.approx(net_mat[1][0])
    assert 64.0 == pytest.approx(net_mat[1][1])

    assert 33 == n.add_multiple(11, -22, 33, -44, 55)
    assert "the experiment worked " == n.concatenate("the ", "experiment ", "worked ", False, "temporarily")
    assert "the experiment worked temporarily" == n.concatenate("the ", "experiment ", "worked ", True, "temporarily")


@skipif_no_server32
def test_unicode_path():
    class Cpp64Encoding(loadlib.Client64):
        def __init__(self):
            dir_name = os.path.dirname(__file__)
            super().__init__(
                module32="cpp32unicode",
                append_sys_path=f"{dir_name}/uñicödé",
                append_environ_path=f"{dir_name}/uñicödé",
            )

        def add(self, a, b):
            return self.request32("add", a, b)

    c2 = Cpp64Encoding()
    assert c2.add(-5, 3) == -2

    with pytest.raises(loadlib.Server32Error):
        c2.add("hello", "world")

    try:
        c2.add("hello", "world")
    except loadlib.Server32Error as err:
        print(err)  # must not raise an error

    c2.shutdown_server32()


@skipif_no_server32
def test_server32_error():
    try:
        c.add("hello", "world")
    except loadlib.Server32Error as err:
        assert err.name == "ArgumentError"
        assert "argument 1: TypeError:" in err.value
        assert err.traceback.endswith("return self.lib.add(a, b)")


@skipif_not_windows
def test_comtypes_ctypes_union_error():
    # Changes to ctypes in Python 3.7.6 and 3.8.1 caused the following exception
    #   TypeError: item 1 in _argtypes_ passes a union by value, which is unsupported.
    # when loading some COM objects, see https://bugs.python.org/issue16575
    #
    # Want to make sure that the Python interpreter that the server32-windows.exe
    # is running on does not raise this TypeError

    class FileSystemObjectClient(loadlib.Client64):
        def __init__(self):
            super().__init__(
                module32="ctypes_union_error",
                append_sys_path=os.path.join(os.path.dirname(__file__), "server32_comtypes"),
            )

        def __getattr__(self, name):
            def send(*args, **kwargs):
                return self.request32(name, *args, **kwargs)

            return send

    file_system = FileSystemObjectClient()
    file_system.create_and_write("foo<bar<baz>>")
    temp_file = file_system.get_temp_file()

    with open(temp_file, mode="rt") as fp:
        source = fp.read().strip()

    assert source == "foo<bar<baz>>"

    os.remove(temp_file)
    file_system.shutdown_server32()


@skipif_not_windows
def test_comtypes_shell32():
    class Shell64(loadlib.Client64):
        def __init__(self):
            super().__init__(
                module32="shell32.py",
                append_sys_path=os.path.join(os.path.dirname(__file__), "server32_comtypes"),
            )

        def environ(self, key):
            return self.request32("environ", key)

    shell = Shell64()

    for name in ["PROCESSOR_IDENTIFIER", "NUMBER_OF_PROCESSORS"]:
        assert shell.environ(name) == os.environ[name]

    shell.shutdown_server32()


@skipif_not_windows
def test_activex():
    class ActiveX(loadlib.Client64):
        def __init__(self):
            super().__init__(
                module32="activex_media_player.py",
                append_sys_path=os.path.join(os.path.dirname(__file__), "server32_comtypes"),
                timeout=30,
            )

        def this(self):
            return self.request32("this")

        def reload(self):
            return self.request32("reload")

        def load_library(self):
            return self.request32("load_library")

        def error1(self):
            return self.request32("error1")

        def error2(self):
            return self.request32("error2")

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
