# pyright reports a reportUnknownMemberType warning for pytest.approx
# pyright: reportUnknownMemberType=false
from __future__ import annotations

import math
import os
import pathlib
from ctypes import (
    POINTER,
    byref,
    c_bool,
    c_char_p,
    c_double,
    c_float,
    c_int,
    c_int8,
    c_int16,
    c_int32,
    c_int64,
    c_void_p,
    create_string_buffer,
)

import pytest

from conftest import (
    HAS_32BIT_LABVIEW_RUNTIME,
    HAS_64BIT_LABVIEW_RUNTIME,
    IS_MAC,
    IS_MAC_ARM64,
    IS_WINDOWS,
    has_mono_runtime,
    skipif_no_comtypes,
    skipif_no_pythonnet,
    skipif_not_windows,
)
from msl.examples.loadlib import EXAMPLES_DIR, FourPoints, NPoints, Point
from msl.loadlib import IS_PYTHON_64BIT, LoadLibrary
from msl.loadlib._constants import default_extension
from msl.loadlib.utils import get_available_port, get_com_info

suffix = "arm64" if IS_MAC_ARM64 else "64" if IS_PYTHON_64BIT else "32"


def test_invalid_libtype() -> None:
    with pytest.raises(ValueError, match=r"Invalid libtype"):
        _ = LoadLibrary("does-not-matter", libtype="xxxxxxxx")  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]


@pytest.mark.parametrize("path", [None, ""])
def test_invalid_path(path: None | str) -> None:
    with pytest.raises(ValueError, match=r"Must specify a non-empty path"):
        _ = LoadLibrary(path)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]


@pytest.mark.skipif(IS_MAC, reason="the 32-bit libraries do not exist for macOS")
@pytest.mark.parametrize("filename", ["cpp_lib", "fortran_lib"])
def test_wrong_bitness(filename: str) -> None:
    suffix = "32" if IS_PYTHON_64BIT else "64"
    path = EXAMPLES_DIR / f"{filename}{suffix}{default_extension}"
    assert path.is_file()
    with pytest.raises(OSError):  # noqa: PT011
        _ = LoadLibrary(path)


@skipif_no_pythonnet
@skipif_not_windows
def test_wrong_bitness_dotnet() -> None:
    import System  # type: ignore[import-not-found] # pyright: ignore[reportMissingImports]  # noqa: PLC0415

    suffix = "32" if IS_PYTHON_64BIT else "64"
    path = EXAMPLES_DIR / f"dotnet_lib{suffix}.dll"
    assert path.is_file()
    with pytest.raises(System.BadImageFormatException):  # pyright: ignore[reportUnknownArgumentType]
        _ = LoadLibrary(path, libtype="net")


@skipif_no_pythonnet
@pytest.mark.skipif(not has_mono_runtime(), reason="requires mono runtime")
@pytest.mark.parametrize("filename", ["dotnet_lib32.dll", "dotnet_lib64.dll"])
def test_mono_bitness_independent(filename: str) -> None:
    path = EXAMPLES_DIR / filename
    net = LoadLibrary(path, libtype="clr")

    names = ";".join(str(name) for name in net.assembly.GetTypes()).split(";")
    assert len(names) == 4
    assert "StringManipulation" in names
    assert "DotNetMSL.BasicMath" in names
    assert "DotNetMSL.ArrayManipulation" in names
    assert "StaticClass" in names

    BasicMath = net.lib.DotNetMSL.BasicMath()  # noqa: N806
    assert BasicMath.add_integers(4, 5) == 9
    assert pytest.approx(BasicMath.divide_floats(4.0, 5.0)) == 0.8
    assert pytest.approx(BasicMath.multiply_doubles(872.24, 525.525)) == 458383.926
    assert pytest.approx(BasicMath.add_or_subtract(99.0, 9.0, True)) == 108.0  # noqa: FBT003
    assert pytest.approx(BasicMath.add_or_subtract(99.0, 9.0, False)) == 90.0  # noqa: FBT003

    ArrayManipulation = net.lib.DotNetMSL.ArrayManipulation()  # noqa: N806
    a = 7.13141
    values = [float(x) for x in range(1000)]
    net_values = ArrayManipulation.scalar_multiply(a, values)
    for i in range(len(values)):
        assert pytest.approx(net_values[i]) == a * values[i]

    a1 = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
    m1 = net.lib.System.Array.CreateInstance(net.lib.System.Double, 2, 3)
    for r in range(2):
        for c in range(3):
            m1[r, c] = a1[r][c]
    a2 = [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]
    m2 = net.lib.System.Array.CreateInstance(net.lib.System.Double, 3, 2)
    for r in range(3):
        for c in range(2):
            m2[r, c] = a2[r][c]
    out = ArrayManipulation.multiply_matrices(m1, m2)
    net_mat = [[out[r, c] for c in range(2)] for r in range(2)]
    assert pytest.approx(net_mat[0][0]) == 22.0
    assert pytest.approx(net_mat[0][1]) == 28.0
    assert pytest.approx(net_mat[1][0]) == 49.0
    assert pytest.approx(net_mat[1][1]) == 64.0

    assert net.lib.StringManipulation().reverse_string("New Zealand") == "dnalaeZ weN"
    assert net.lib.StaticClass.add_multiple(11, -22, 33, -44, 55) == 33
    assert net.lib.StaticClass.concatenate("a", "b", "c", False, "d") == "abc"  # noqa: FBT003
    assert net.lib.StaticClass.concatenate("a", "b", "c", True, "d") == "abcd"  # noqa: FBT003

    net.cleanup()


def test_cpp() -> None:
    path = EXAMPLES_DIR / f"cpp_lib{suffix}"
    cpp = LoadLibrary(path)

    lib = cpp.lib
    lib.add.argtypes = [c_int, c_int]
    lib.add.restype = c_int
    lib.subtract.argtypes = [c_float, c_float]
    lib.subtract.restype = c_float
    lib.add_or_subtract.argtypes = [c_double, c_double, c_bool]
    lib.add_or_subtract.restype = c_double
    lib.scalar_multiply.argtypes = [c_double, POINTER(c_double), c_int, POINTER(c_double)]
    lib.scalar_multiply.restype = None
    lib.reverse_string_v1.argtypes = [c_char_p, c_int, c_char_p]
    lib.reverse_string_v1.restype = None
    lib.reverse_string_v2.argtypes = [c_char_p, c_int]
    lib.reverse_string_v2.restype = c_char_p
    lib.distance_4_points.argtypes = [FourPoints]
    lib.distance_4_points.restype = c_double
    lib.distance_n_points.argtypes = [NPoints]
    lib.distance_n_points.restype = c_double

    assert lib.add(1, 2) == 3
    assert lib.add(-1000, -2) == -1002
    assert pytest.approx(lib.subtract(20.0, 10.0)) == 10.0
    assert pytest.approx(lib.subtract(90.0, 100.0)) == -10.0
    assert pytest.approx(lib.add_or_subtract(0.1234, -0.1234, True)) == 0.0  # noqa: FBT003
    assert pytest.approx(lib.add_or_subtract(123.456, 23.456, False)) == 100.0  # noqa: FBT003

    n = 100
    a = 3.1415926
    values = (c_double * n)(*tuple(x for x in range(n)))
    out = (c_double * n)()
    lib.scalar_multiply(a, values, n, out)
    for i in range(n):
        assert pytest.approx(out[i]) == a * values[i]

    str_in = "1234567890"
    str_out = create_string_buffer(len(str_in))
    lib.reverse_string_v1(create_string_buffer(str_in.encode()), len(str_in), str_out)
    assert str_out.raw.decode() == "0987654321"

    str_in = "&* 1 j z|x cba["
    str_out2 = lib.reverse_string_v2(create_string_buffer(str_in.encode()), len(str_in))
    # ignore testing for null termination on different platforms
    assert str_out2[: len(str_in)].decode() == "[abc x|z j 1 *&"

    fp = FourPoints(Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0))
    assert pytest.approx(4.0) == lib.distance_4_points(fp)

    n = 2**16
    theta = 0.0
    delta = (2.0 * math.pi) / float(n)
    pts = NPoints()
    pts.n = n
    pts.points = (Point * n)()
    for i in range(n):
        pts.points[i] = Point(math.cos(theta), math.sin(theta))
        theta += delta
    assert pytest.approx(2.0 * math.pi) == lib.distance_n_points(pts)


def test_fortran() -> None:  # noqa: PLR0915
    path = EXAMPLES_DIR / f"fortran_lib{suffix}"
    fortran = LoadLibrary(path)

    lib = fortran.lib
    lib.sum_8bit.argtypes = [POINTER(c_int8), POINTER(c_int8)]
    lib.sum_8bit.restype = c_int8
    lib.sum_16bit.argtypes = [POINTER(c_int16), POINTER(c_int16)]
    lib.sum_16bit.restype = c_int16
    lib.sum_32bit.argtypes = [POINTER(c_int32), POINTER(c_int32)]
    lib.sum_32bit.restype = c_int32
    lib.sum_64bit.argtypes = [POINTER(c_int64), POINTER(c_int64)]
    lib.sum_64bit.restype = c_int64
    lib.multiply_float32.argtypes = [POINTER(c_float), POINTER(c_float)]
    lib.multiply_float32.restype = c_float
    lib.multiply_float64.argtypes = [POINTER(c_double), POINTER(c_double)]
    lib.multiply_float64.restype = c_double
    lib.is_positive.argtypes = [POINTER(c_double)]
    lib.is_positive.restype = c_bool
    lib.add_or_subtract.argtypes = [POINTER(c_int32), POINTER(c_int32), POINTER(c_bool)]
    lib.add_or_subtract.restype = c_int32
    lib.factorial.argtypes = [POINTER(c_int8)]
    lib.factorial.restype = c_double
    lib.standard_deviation.argtypes = [POINTER(c_double), POINTER(c_int32)]
    lib.standard_deviation.restype = c_double
    lib.besselj0.argtypes = [POINTER(c_double)]
    lib.besselj0.restype = c_double
    lib.reverse_string.argtypes = [c_char_p, POINTER(c_int32), c_char_p]
    lib.reverse_string.restype = None
    lib.add_1d_arrays.argtypes = [POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_int32)]
    lib.add_1d_arrays.restype = None
    lib.matrix_multiply.argtypes = [
        c_void_p,
        c_void_p,
        POINTER(c_int32),
        POINTER(c_int32),
        c_void_p,
        POINTER(c_int32),
        POINTER(c_int32),
    ]
    lib.matrix_multiply.restype = None

    assert lib.sum_8bit(byref(c_int8(-(2**7))), byref(c_int8(1))) == -127
    assert lib.sum_16bit(byref(c_int16(2**15 - 1)), byref(c_int16(-1))) == 32766
    assert lib.sum_32bit(byref(c_int32(123456788)), byref(c_int32(1))) == 123456789
    assert lib.sum_64bit(byref(c_int64(-(2**63))), byref(c_int64(1))) == -9223372036854775807
    assert pytest.approx(lib.multiply_float32(byref(c_float(40.874)), byref(c_float(-1284.131)))) == -52487.570494
    assert pytest.approx(lib.multiply_float64(byref(c_double(1.1e100)), byref(c_double(2.1e200)))) == 2.31e300
    assert lib.is_positive(byref(c_double(1e-100)))
    assert not lib.is_positive(byref(c_double(-1e-100)))
    assert lib.add_or_subtract(byref(c_int32(1000)), byref(c_int32(2000)), byref(c_bool(True))) == 3000  # noqa: FBT003
    assert lib.add_or_subtract(byref(c_int32(1000)), byref(c_int32(2000)), byref(c_bool(False))) == -1000  # noqa: FBT003
    assert int(lib.factorial(byref(c_int8(0)))) == 1
    assert int(lib.factorial(byref(c_int8(1)))) == 1
    assert int(lib.factorial(byref(c_int8(5)))) == 120

    a = (c_double * 9)(*[float(val) for val in range(1, 10)])
    assert pytest.approx(lib.standard_deviation(a, byref(c_int32(9)))) == 2.73861278752583

    assert pytest.approx(lib.besselj0(byref(c_double(8.0)))) == 0.171650807137

    str_in = "hello world!"
    str_out = create_string_buffer(len(str_in))
    lib.reverse_string(create_string_buffer(str_in.encode()), byref(c_int32(len(str_in))), str_out)
    assert str_out.raw.decode() == "!dlrow olleh"

    in1 = (c_double * 999)(*[float(val) for val in range(1, 1000)])
    in2 = (c_double * 999)(*[3.0 * val for val in range(1, 1000)])
    assert len(in1) == len(in2)
    a = (c_double * len(in1))()
    lib.add_1d_arrays(a, in1, in2, byref(c_int32(len(in1))))
    for i in range(len(a)):
        assert pytest.approx(a[i]) == in1[i] + in2[i]

    m1 = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
    a1 = ((c_double * 2) * 3)()
    for r in range(2):
        for c in range(3):
            a1[c][r] = m1[r][c]
    m2 = [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]
    a2 = ((c_double * 3) * 2)()
    for r in range(3):
        for c in range(2):
            a2[c][r] = m2[r][c]
    aa = ((c_double * 2) * 2)()
    lib.matrix_multiply(aa, a1, byref(c_int32(2)), byref(c_int32(3)), a2, byref(c_int32(3)), byref(c_int32(2)))
    assert pytest.approx(aa[0][0]) == 22.0
    assert pytest.approx(aa[0][1]) == 49.0
    assert pytest.approx(aa[1][0]) == 28.0
    assert pytest.approx(aa[1][1]) == 64.0


@skipif_no_pythonnet
def test_dotnet() -> None:
    bitness = "64" if IS_PYTHON_64BIT else "32"
    path = EXAMPLES_DIR / f"dotnet_lib{bitness}.dll"
    net = LoadLibrary(path, "clr")

    names = ";".join(str(name) for name in net.assembly.GetTypes()).split(";")
    assert len(names) == 4
    assert "StringManipulation" in names
    assert "DotNetMSL.BasicMath" in names
    assert "DotNetMSL.ArrayManipulation" in names
    assert "StaticClass" in names

    BasicMath = net.lib.DotNetMSL.BasicMath()  # noqa: N806
    assert BasicMath.add_integers(4, 5) == 9
    assert pytest.approx(BasicMath.divide_floats(4.0, 5.0)) == 0.8
    assert pytest.approx(BasicMath.multiply_doubles(872.24, 525.525)) == 458383.926
    assert pytest.approx(BasicMath.add_or_subtract(99.0, 9.0, True)) == 108.0  # noqa: FBT003
    assert pytest.approx(BasicMath.add_or_subtract(99.0, 9.0, False)) == 90.0  # noqa: FBT003

    ArrayManipulation = net.lib.DotNetMSL.ArrayManipulation()  # noqa: N806
    a = 7.13141
    values = [float(x) for x in range(1000)]
    net_values = ArrayManipulation.scalar_multiply(a, values)
    for i in range(len(values)):
        assert pytest.approx(net_values[i]) == a * values[i]

    a1 = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
    m1 = net.lib.System.Array.CreateInstance(net.lib.System.Double, 2, 3)
    for r in range(2):
        for c in range(3):
            m1[r, c] = a1[r][c]
    a2 = [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]
    m2 = net.lib.System.Array.CreateInstance(net.lib.System.Double, 3, 2)
    for r in range(3):
        for c in range(2):
            m2[r, c] = a2[r][c]
    out = ArrayManipulation.multiply_matrices(m1, m2)
    net_mat = [[out[r, c] for c in range(2)] for r in range(2)]
    assert pytest.approx(net_mat[0][0]) == 22.0
    assert pytest.approx(net_mat[0][1]) == 28.0
    assert pytest.approx(net_mat[1][0]) == 49.0
    assert pytest.approx(net_mat[1][1]) == 64.0

    assert net.lib.StringManipulation().reverse_string("New Zealand") == "dnalaeZ weN"
    assert net.lib.StaticClass.add_multiple(11, -22, 33, -44, 55) == 33
    assert net.lib.StaticClass.concatenate("a", "b", "c", False, "d") == "abc"  # noqa: FBT003
    assert net.lib.StaticClass.concatenate("a", "b", "c", True, "d") == "abcd"  # noqa: FBT003

    net.cleanup()


@pytest.mark.skipif(not IS_WINDOWS, reason="not Windows")
@pytest.mark.skipif(IS_PYTHON_64BIT and not HAS_64BIT_LABVIEW_RUNTIME, reason="no 64-bit LabVIEW Run-Time Engine")
@pytest.mark.skipif(not IS_PYTHON_64BIT and not HAS_32BIT_LABVIEW_RUNTIME, reason="no 32-bit LabVIEW Run-Time Engine")
def test_labview() -> None:
    bit = "64" if IS_PYTHON_64BIT else "32"
    path = EXAMPLES_DIR / f"labview_lib{bit}.dll"
    labview = LoadLibrary(path)

    data = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    x = (c_double * len(data))(*data)

    mean, variance, stdev = c_double(), c_double(), c_double()

    # weighting to use: 0 -> sample, 1-> population

    labview.lib.stdev(x, len(data), 0, byref(mean), byref(variance), byref(stdev))
    assert pytest.approx(5.0) == mean.value
    assert pytest.approx(7.5) == variance.value
    assert pytest.approx(2.73861278752583) == stdev.value

    labview.lib.stdev(x, len(data), 1, byref(mean), byref(variance), byref(stdev))
    assert pytest.approx(5.0) == mean.value
    assert pytest.approx(6.66666666666667) == variance.value
    assert pytest.approx(2.58198889747161) == stdev.value


def test_java() -> None:  # noqa: PLR0915
    jar = LoadLibrary(f"{EXAMPLES_DIR}/java_lib.jar")

    Math = jar.lib.nz.msl.examples.MathUtils  # noqa: N806
    Matrix = jar.lib.nz.msl.examples.Matrix  # noqa: N806

    assert 0.0 <= Math.random() < 1.0
    assert pytest.approx(5.69209978830308) == Math.sqrt(32.4)

    #
    # check LU decomposition
    #

    n = 14
    m1 = Matrix(n, n, 2.0, 8.0)
    L = m1.getL()  # noqa: N806
    U = m1.getU()  # noqa: N806
    LU = m1.multiply(L, U)  # noqa: N806
    for i in range(n):
        for j in range(n):
            assert pytest.approx(LU.getValue(i, j)) == m1.getValue(i, j)

    #
    # check QR decomposition
    #

    n = 8
    m2 = Matrix(n, n, -100.0, 100.0)
    Q = m2.getQ()  # noqa: N806
    R = m2.getR()  # noqa: N806
    QR = m2.multiply(Q, R)  # noqa: N806
    for i in range(n):
        for j in range(n):
            assert pytest.approx(QR.getValue(i, j)) == m2.getValue(i, j)

    #
    # solve Ax=b
    #
    m3 = jar.gateway.new_array(jar.lib.Double, 3, 3)
    m3[0][0] = 3.0
    m3[0][1] = 2.0
    m3[0][2] = -1.0
    m3[1][0] = 2.0
    m3[1][1] = -2.0
    m3[1][2] = 4.0
    m3[2][0] = -1.0
    m3[2][1] = 0.5
    m3[2][2] = 1.0

    m4 = jar.gateway.new_array(jar.lib.Double, 3)
    m4[0] = 1.0
    m4[1] = -2.0
    m4[2] = 0.0

    A = Matrix(m3)  # noqa: N806
    x = Matrix.solve(A, Matrix(m4))

    b_prime = Matrix.multiply(A, x)
    for i in range(3):
        assert pytest.approx(m4[i]) == b_prime.getValue(i, 0)

    #
    # Check inverse
    #
    n = 30
    m5 = Matrix(n, n, 0.0, 100.0)
    m6 = m5.getInverse()
    m7 = Matrix.multiply(m5, m6)
    identity = Matrix(n)
    for i in range(n):
        for j in range(n):
            assert pytest.approx(m7.getValue(i, j), abs=1e-8) == identity.getValue(i, j)

    #
    # Check determinant
    #
    a = [[6, 1, 1], [4, -2, 5], [2, 8, 7]]
    ja = jar.gateway.new_array(jar.lib.Double, 3, 3)
    for i in range(3):
        for j in range(3):
            ja[i][j] = float(a[i][j])
    m8 = Matrix(ja)
    assert pytest.approx(-306) == m8.getDeterminant()

    jar.gateway.shutdown()

    cls = LoadLibrary(f"{EXAMPLES_DIR}/Trig.class")
    Trig = cls.lib.Trig  # noqa: N806

    x = 0.123456

    assert pytest.approx(math.cos(x)) == Trig.cos(x)
    assert pytest.approx(math.cosh(x)) == Trig.cosh(x)
    assert pytest.approx(math.acos(x)) == Trig.acos(x)
    assert pytest.approx(math.sin(x)) == Trig.sin(x)
    assert pytest.approx(math.sinh(x)) == Trig.sinh(x)
    assert pytest.approx(math.asin(x)) == Trig.asin(x)
    assert pytest.approx(math.tan(x)) == Trig.tan(x)
    assert pytest.approx(math.tanh(x)) == Trig.tanh(x)
    assert pytest.approx(math.atan(x)) == Trig.atan(x)
    assert pytest.approx(math.atan2(-4.321, x)) == Trig.atan2(-4.321, x)


def test_java_gateway_parameters() -> None:
    from py4j.java_gateway import (  # type: ignore[import-untyped] # pyright: ignore[reportMissingTypeStubs]  # noqa: PLC0415
        GatewayParameters,  # pyright: ignore[reportUnknownVariableType]
    )

    port = get_available_port()
    gp = GatewayParameters(port=port)  # pyright: ignore[reportUnknownVariableType]

    with LoadLibrary(f"{EXAMPLES_DIR}/java_lib.jar", gateway_parameters=gp) as jar:
        assert 0.0 <= jar.lib.nz.msl.examples.MathUtils.random() < 1.0
        assert jar.gateway.gateway_parameters.port == port


@skipif_no_comtypes
def test_comtypes() -> None:
    progid = "Scripting.FileSystemObject"

    with LoadLibrary(progid, "com") as obj:
        assert obj.lib.BuildPath("root", "filename") == r"root\filename"

    with pytest.raises(OSError, match=r"Cannot find 'ABC.def.GHI' for libtype='com'"):
        _ = LoadLibrary("ABC.def.GHI", "com")

    info = get_com_info()
    assert info

    # load by CLSID
    found_it = False
    for key, value in info.items():
        if value["ProgID"] == progid:
            with LoadLibrary(key, "com") as obj:
                assert obj.lib.BuildPath("root", "filename") == r"root\filename"
                found_it = True
                break

    assert found_it, f"did not find {progid!r} in utils.get_com_info() dict"


@skipif_no_comtypes
def test_activex_raises() -> None:
    with pytest.raises(OSError, match=r"Cannot find an ActiveX library with ID 'ABC'"):
        _ = LoadLibrary("ABC", "activex")

    progid = "MediaPlayer.MediaPlayer.1"

    with pytest.raises(OSError, match=r"Cannot create a top-level child window"):
        _ = LoadLibrary(progid, "activex", parent=0)

    with pytest.raises(OSError, match=r"Invalid window handle"):
        _ = LoadLibrary(progid, "activex", parent="xxx")


def test_unicode_path_java() -> None:
    cls = LoadLibrary("./tests/uñicödé/Trig.class")
    x = 0.123456
    assert pytest.approx(math.cos(x)) == cls.lib.Trig.cos(x)
    assert isinstance(repr(cls), str)
    assert isinstance(str(cls), str)
    cls.gateway.shutdown()


@skipif_no_pythonnet
def test_unicode_path_dotnet() -> None:
    net = LoadLibrary("./tests/uñicödé/Namespace.With.Dots-uñicödé.dll", "net")
    checker = net.lib.Namespace.With.Dots.Checker()
    assert checker.IsSuccess()
    assert isinstance(repr(net), str)
    assert isinstance(str(net), str)
    net.cleanup()


def test_unicode_path_cpp() -> None:
    cpp = LoadLibrary(f"./tests/uñicödé/cpp_lib{suffix}-uñicödé")
    assert cpp.lib.add(1, 2) == 3
    assert isinstance(repr(cpp), str)
    assert isinstance(str(cpp), str)


@skipif_no_pythonnet
def test_issue7() -> None:
    # checks that Issue #7 is fixed
    net = LoadLibrary("./tests/namespace_with_dots/Namespace.With.Dots.dll", "net")
    checker = net.lib.Namespace.With.Dots.Checker()
    assert checker.IsSuccess()
    assert isinstance(repr(net), str)
    assert isinstance(str(net), str)
    net.cleanup()


def test_issue8() -> None:
    # checks that Issue #8 is fixed
    with LoadLibrary(pathlib.Path(os.path.join(EXAMPLES_DIR, f"cpp_lib{suffix}"))):  # noqa: PTH118
        pass


def test_path_attrib() -> None:
    path = os.path.join(EXAMPLES_DIR, f"cpp_lib{suffix}")  # noqa: PTH118
    expected = path + default_extension
    assert LoadLibrary(path).path == expected
    assert LoadLibrary(path.encode()).path == expected
    assert LoadLibrary(pathlib.Path(path)).path == expected


@skipif_no_pythonnet
def test_dotnet_nested_namespace() -> None:  # noqa: PLR0915
    net = LoadLibrary("./tests/nested_namespaces/nested_namespaces.dll", "clr")
    lib = net.lib

    assert pytest.approx(math.pi) == lib.System.Math.PI

    assert lib.A.B.C.Klass().Message() == "Hello from A.B.C.Klass().Message()"
    assert lib.A.B.Klass().Message() == "Hello from A.B.Klass().Message()"
    assert lib.A.Klass().Message() == "Hello from A.Klass().Message()"

    assert lib.Messenger().Message() == "Hello from Messenger.Message()"

    assert lib.Foo.Bar.Baz("my custom message!").Message() == "my custom message!"
    assert lib.Foo.Bar.Baz("abc 123").message == "abc 123"

    # pythonnet 3.0+ disabled implicit conversion from C# enums to Python int and back.
    # One must now either use enum members (e.g. MyEnum.Option), or use enum constructor
    # (e.g. MyEnum(42) or MyEnum(42, True) when MyEnum does not have a member with value 42).
    import clr  # type: ignore[import-untyped] # pyright: ignore[reportMissingTypeStubs]  # noqa: PLC0415

    if int(clr.__version__.split(".")[0]) < 3:  # pyright: ignore[reportUnknownArgumentType]
        # an enum in a namespace
        assert lib.A.B.C.ErrorCode.Unknown == 0
        assert lib.A.B.C.ErrorCode.ConnectionLost == 100
        assert lib.A.B.C.ErrorCode.OutlierReading == 200

        # an enum not in a namespace
        assert lib.Season.Winter == 0
        assert lib.Season.Spring == 1
        assert lib.Season.Summer == 2
        assert lib.Season.Autumn == 3
    else:
        # an enum in a namespace
        assert lib.A.B.C.ErrorCode.Unknown == lib.A.B.C.ErrorCode(0)
        assert lib.A.B.C.ErrorCode.ConnectionLost == lib.A.B.C.ErrorCode(100)
        assert lib.A.B.C.ErrorCode.OutlierReading == lib.A.B.C.ErrorCode(200)

        # an enum not in a namespace
        assert lib.Season.Winter == lib.Season(0)
        assert lib.Season.Spring == lib.Season(1)
        assert lib.Season.Summer == lib.Season(2)
        assert lib.Season.Autumn == lib.Season(3)

    Subtracter = lib.A.B.C.Subtracter(8, 9)  # noqa: N806
    assert Subtracter.x == 8
    assert Subtracter.y == 9
    assert Subtracter.Subtract() == -1

    # Adder is not defined as a public class but can still be created
    Adder = lib.System.Activator.CreateInstance(lib.Adder, lib.System.Int32(82), lib.System.Int32(-27))  # noqa: N806
    assert Adder.Add() == 55
    assert Adder.x == 82
    assert Adder.y == -27

    # a struct in a nested namespace
    point = lib.A.B.C.Point(0, 0)
    assert point.X == 0
    assert point.Y == 0
    assert point.ToString() == "Point<X=0, Y=0>"
    point.X = 73
    point.Y = -21
    assert point.ToString() == "Point<X=73, Y=-21>"

    point = lib.A.B.C.Point(-3, 54)
    assert point.X == -3
    assert point.Y == 54
    assert point.ToString() == "Point<X=-3, Y=54>"

    # a struct not in a namespace
    point = lib.Point(123, 456)
    assert point.X == 123
    assert point.Y == 456

    # still need to create the instance in Python
    StructWithoutConstructor = lib.StructWithoutConstructor()  # noqa: N806
    assert StructWithoutConstructor.X == 0
    assert StructWithoutConstructor.Y == 0
    StructWithoutConstructor.X = 1
    StructWithoutConstructor.Y = -1
    assert StructWithoutConstructor.X == 1
    assert StructWithoutConstructor.Y == -1

    net.cleanup()


def test_py4j_jar_environment_variable() -> None:
    original = os.environ.get("PY4J_JAR", "")

    # the file does not exist
    os.environ["PY4J_JAR"] = f"{__file__}abc"
    with pytest.raises(OSError, match=r"the full path to py4j[\d.]+.jar is invalid"):
        _ = LoadLibrary(f"{EXAMPLES_DIR}/java_lib.jar")

    # a valid folder, but expect a path to the py4j<version>.jar file
    os.environ["PY4J_JAR"] = os.path.dirname(__file__)  # noqa: PTH120
    with pytest.raises(OSError, match=r"the full path to py4j[\d.]+.jar is invalid"):
        _ = LoadLibrary(f"{EXAMPLES_DIR}/java_lib.jar")

    # a valid file but not a py4j<version>.jar file
    os.environ["PY4J_JAR"] = __file__
    with pytest.raises(OSError, match=r"the full path to py4j[\d.]+.jar is invalid"):
        _ = LoadLibrary(f"{EXAMPLES_DIR}/java_lib.jar")

    os.environ["PY4J_JAR"] = original
    java = LoadLibrary(f"{EXAMPLES_DIR}/java_lib.jar")
    assert 0.0 <= java.lib.nz.msl.examples.MathUtils.random() < 1.0
    java.gateway.shutdown()


def test_bad_del() -> None:
    # Make sure that the following exception is not raised in LoadLibrary.__del__
    #   AttributeError: 'BadDel' object has no attribute '_gateway'

    class BadDel(LoadLibrary):
        def __init__(self) -> None:  # pyright: ignore[reportMissingSuperCall]
            pass

    b = BadDel()
    b.__del__()
    del b

    # the following will raise the error because the
    # LoadLibrary class was not instantiated

    with pytest.raises(AttributeError, match="_gateway"):
        _ = BadDel().gateway

    with pytest.raises(AttributeError, match="_gateway"):  # noqa: SIM117
        with BadDel():
            pass
