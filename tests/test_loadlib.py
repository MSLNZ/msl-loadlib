# -*- coding: utf-8 -*-
import os
import sys
import math
import pathlib
from ctypes import *

import pytest

from msl import loadlib
from msl.examples.loadlib import EXAMPLES_DIR, Point, FourPoints, NPoints


def test_invalid_libtype():
    with pytest.raises(ValueError, match=', '.join(loadlib.LoadLibrary.LIBTYPES)):
        loadlib.LoadLibrary('does-not-matter', libtype='xxxxxxxx')


def test_invalid_path():
    for item in [None, '']:
        with pytest.raises(ValueError, match=r'You must specify the path'):
            loadlib.LoadLibrary(item)


@pytest.mark.skipif(loadlib.IS_MAC, reason='the 32-bit library does not exist on macOS')
def test_load_failure_in_wrong_python_bitness():

    def check(path, libtype, exception):
        if libtype == 'net':
            path += '.dll'
        else:
            path += loadlib.DEFAULT_EXTENSION
        assert os.path.isfile(path)

        if loadlib.IS_WINDOWS or libtype != 'net':
            with pytest.raises(exception):
                loadlib.LoadLibrary(path, libtype=libtype)
        elif loadlib.IS_LINUX and libtype == 'net':
            # Mono can load a 32/64 bit library in 64/32 bit Python
            net = loadlib.LoadLibrary(path, libtype=libtype)
            bm = net.lib.DotNetMSL.BasicMath()
            assert 9 == bm.add_integers(4, 5)
        else:
            raise NotImplementedError

    suffix = '32' if loadlib.IS_PYTHON_64BIT else '64'
    check(os.path.join(EXAMPLES_DIR, 'cpp_lib'+suffix), 'cdll', OSError)
    check(os.path.join(EXAMPLES_DIR, 'fortran_lib'+suffix), 'cdll', OSError)
    if not loadlib.IS_LINUX and sys.version_info[:2] != (3, 8):  # mono encounters a fatal crash
        import clr
        check(
            os.path.join(EXAMPLES_DIR, 'dotnet_lib'+suffix),
            'net',
            (clr.System.IO.FileNotFoundException,  clr.System.BadImageFormatException)
        )


def test_cpp():
    bitness = '64' if loadlib.IS_PYTHON_64BIT else '32'
    path = os.path.join(EXAMPLES_DIR, 'cpp_lib' + bitness)
    cpp = loadlib.LoadLibrary(path)

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

    assert 3 == lib.add(1, 2)
    assert -1002 == lib.add(-1000, -2)
    assert 10.0 == pytest.approx(lib.subtract(20.0, 10.0))
    assert -10.0 == pytest.approx(lib.subtract(90.0, 100.0))
    assert 0.0 == pytest.approx(lib.add_or_subtract(0.1234, -0.1234, True))
    assert 100.0 == pytest.approx(lib.add_or_subtract(123.456, 23.456, False))

    n = 100
    a = 3.1415926
    values = (c_double * n)(*tuple(x for x in range(n)))
    out = (c_double * n)()
    lib.scalar_multiply(a, values, n, out)
    for i in range(n):
        assert a * values[i] == pytest.approx(out[i])

    str_in = '1234567890'
    str_out = create_string_buffer(len(str_in))
    lib.reverse_string_v1(create_string_buffer(str_in.encode()), len(str_in), str_out)
    assert '0987654321' == str_out.raw.decode()

    str_in = '&* 1 j z|x cba['
    str_out = lib.reverse_string_v2(create_string_buffer(str_in.encode()), len(str_in))
    # ignore testing for null termination on different platforms
    assert '[abc x|z j 1 *&' == str_out[:len(str_in)].decode()

    fp = FourPoints((0, 0), (0, 1), (1, 1), (1, 0))
    assert lib.distance_4_points(fp) == pytest.approx(4.0)

    n = 2**16
    theta = 0.0
    delta = (2.0 * math.pi) / float(n)
    pts = NPoints()
    pts.n = n
    pts.points = (Point * n)()
    for i in range(n):
        pts.points[i] = Point(math.cos(theta), math.sin(theta))
        theta += delta
    assert lib.distance_n_points(pts) == pytest.approx(2.0 * math.pi)


def test_fortran():
    bitness = '64' if loadlib.IS_PYTHON_64BIT else '32'
    path = os.path.join(EXAMPLES_DIR, 'fortran_lib' + bitness)
    fortran = loadlib.LoadLibrary(path)

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
    lib.matrix_multiply.argtypes = [c_void_p, c_void_p, POINTER(c_int32), POINTER(c_int32), c_void_p, POINTER(c_int32),
                                    POINTER(c_int32)]
    lib.matrix_multiply.restype = None

    assert -127 == lib.sum_8bit(byref(c_int8(-2 ** 7)), byref(c_int8(1)))
    assert 32766 == lib.sum_16bit(byref(c_int16(2 ** 15 - 1)), byref(c_int16(-1)))
    assert 123456789 == lib.sum_32bit(byref(c_int32(123456788)), byref(c_int32(1)))
    assert -9223372036854775807 == lib.sum_64bit(byref(c_int64(-2 ** 63)), byref(c_int64(1)))
    assert -52487.570494 == pytest.approx(lib.multiply_float32(byref(c_float(40.874)), byref(c_float(-1284.131))))
    assert 2.31e300 == pytest.approx(lib.multiply_float64(byref(c_double(1.1e100)), byref(c_double(2.1e200))))
    assert lib.is_positive(byref(c_double(1e-100)))
    assert not lib.is_positive(byref(c_double(-1e-100)))
    assert 3000 == lib.add_or_subtract(byref(c_int32(1000)), byref(c_int32(2000)), byref(c_bool(True)))
    assert -1000 == lib.add_or_subtract(byref(c_int32(1000)), byref(c_int32(2000)), byref(c_bool(False)))
    assert 1 == int(lib.factorial(byref(c_int8(0))))
    assert 1 == int(lib.factorial(byref(c_int8(1))))
    assert 120 == int(lib.factorial(byref(c_int8(5))))

    a = (c_double * 9)(*[float(val) for val in range(1, 10)])
    assert 2.73861278752583 == pytest.approx(lib.standard_deviation(a, byref(c_int32(9))))

    assert 0.171650807137 == pytest.approx(lib.besselj0(byref(c_double(8.0))))

    str_in = 'hello world!'
    str_out = create_string_buffer(len(str_in))
    lib.reverse_string(create_string_buffer(str_in.encode()), byref(c_int32(len(str_in))), str_out)
    assert '!dlrow olleh' == str_out.raw.decode()

    in1 = (c_double * 999)(*[float(val) for val in range(1, 1000)])
    in2 = (c_double * 999)(*[3.0 * val for val in range(1, 1000)])
    assert len(in1) == len(in2)
    a = (c_double * len(in1))()
    lib.add_1d_arrays(a, in1, in2, byref(c_int32(len(in1))))
    for i in range(len(a)):
        assert in1[i] + in2[i] == pytest.approx(a[i])

    m1 = [[1., 2., 3.], [4., 5., 6.]]
    a1 = ((c_double * 2) * 3)()
    for r in range(2):
        for c in range(3):
            a1[c][r] = m1[r][c]
    m2 = [[1., 2.], [3., 4.], [5., 6.]]
    a2 = ((c_double * 3) * 2)()
    for r in range(3):
        for c in range(2):
            a2[c][r] = m2[r][c]
    a = ((c_double * 2) * 2)()
    lib.matrix_multiply(a, a1, byref(c_int32(2)), byref(c_int32(3)), a2, byref(c_int32(3)), byref(c_int32(2)))
    assert 22.0 == pytest.approx(a[0][0])
    assert 49.0 == pytest.approx(a[0][1])
    assert 28.0 == pytest.approx(a[1][0])
    assert 64.0 == pytest.approx(a[1][1])


@pytest.mark.skipif(
    (loadlib.IS_LINUX or loadlib.IS_MAC) and sys.version_info[:2] == (3, 8),
    reason='get fatal crash with mono & Python 3.8 when importing pythonnet'
)
def test_dotnet():
    bitness = '64' if loadlib.IS_PYTHON_64BIT else '32'
    path = os.path.join(EXAMPLES_DIR, 'dotnet_lib' + bitness + '.dll')
    net = loadlib.LoadLibrary(path, 'clr')

    names = ';'.join(str(name) for name in net.assembly.GetTypes()).split(';')
    assert len(names) == 4
    assert 'StringManipulation' in names
    assert 'DotNetMSL.BasicMath' in names
    assert 'DotNetMSL.ArrayManipulation' in names
    assert 'StaticClass' in names

    BasicMath = net.lib.DotNetMSL.BasicMath()
    assert 9 == BasicMath.add_integers(4, 5)
    assert 0.8 == pytest.approx(BasicMath.divide_floats(4., 5.))
    assert 458383.926 == pytest.approx(BasicMath.multiply_doubles(872.24, 525.525))
    assert 108.0 == pytest.approx(BasicMath.add_or_subtract(99., 9., True))
    assert 90.0 == pytest.approx(BasicMath.add_or_subtract(99., 9., False))

    ArrayManipulation = net.lib.DotNetMSL.ArrayManipulation()
    a = 7.13141
    values = [float(x) for x in range(1000)]
    net_values = ArrayManipulation.scalar_multiply(a, values)
    for i in range(len(values)):
        assert a * values[i] == pytest.approx(net_values[i])

    a1 = [[1., 2., 3.], [4., 5., 6.]]
    m1 = net.lib.System.Array.CreateInstance(net.lib.System.Double, 2, 3)
    for r in range(2):
        for c in range(3):
            m1[r, c] = a1[r][c]
    a2 = [[1., 2.], [3., 4.], [5., 6.]]
    m2 = net.lib.System.Array.CreateInstance(net.lib.System.Double, 3, 2)
    for r in range(3):
        for c in range(2):
            m2[r, c] = a2[r][c]
    out = ArrayManipulation.multiply_matrices(m1, m2)
    net_mat = [[out[r, c] for c in range(2)] for r in range(2)]
    assert 22.0 == pytest.approx(net_mat[0][0])
    assert 28.0 == pytest.approx(net_mat[0][1])
    assert 49.0 == pytest.approx(net_mat[1][0])
    assert 64.0 == pytest.approx(net_mat[1][1])

    assert 'dnalaeZ weN' == net.lib.StringManipulation().reverse_string('New Zealand')
    assert net.lib.StaticClass.add_multiple(11, -22, 33, -44, 55) == 33
    assert net.lib.StaticClass.concatenate('a', 'b', 'c', False, 'd') == 'abc'
    assert net.lib.StaticClass.concatenate('a', 'b', 'c', True, 'd') == 'abcd'


@pytest.mark.skipif(
    not any([
        os.path.isdir(r'C:\Program Files\National Instruments\Shared\LabVIEW Run-Time'),
        os.path.isdir(r'C:\Program Files (x86)\National Instruments\Shared\LabVIEW Run-Time'),
    ]),
    reason='requires labview runtime'
)
def test_labview():

    from ctypes import c_double, byref

    if loadlib.IS_PYTHON_64BIT:
        path = EXAMPLES_DIR + '/labview_lib64.dll'
    else:
        path = EXAMPLES_DIR + '/labview_lib32.dll'

    labview = loadlib.LoadLibrary(path)

    data = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    x = (c_double * len(data))(*data)

    mean, variance, stdev = c_double(), c_double(), c_double()

    # weighting to use: 0 -> sample, 1-> population

    labview.lib.stdev(x, len(data), 0, byref(mean), byref(variance), byref(stdev))
    assert mean.value == pytest.approx(5.0)
    assert variance.value == pytest.approx(7.5)
    assert stdev.value == pytest.approx(2.73861278752583)

    labview.lib.stdev(x, len(data), 1, byref(mean), byref(variance), byref(stdev))
    assert mean.value == pytest.approx(5.0)
    assert variance.value == pytest.approx(6.66666666666667)
    assert stdev.value == pytest.approx(2.58198889747161)


def test_java():
    try:
        jar = loadlib.LoadLibrary(EXAMPLES_DIR + '/java_lib.jar')
    except (IOError, OSError) as e:
        # if py4j is located in the .eggs directory and not in the site-packages directory
        # then the py4j*.jar file cannot be found so we need to create a PY4J_JAR env variable
        msg = str(e)
        if 'Create a PY4J_JAR environment variable' not in msg:
            raise

        import py4j
        os.environ['PY4J_JAR'] = os.path.join(
            '.eggs',
            'py4j-{}-py{}.{}.egg'.format(py4j.__version__, sys.version_info.major, sys.version_info.minor),
            'share',
            'py4j',
            'py4j{}.jar'.format(py4j.__version__)
        )
        jar = loadlib.LoadLibrary(EXAMPLES_DIR + '/java_lib.jar')

    Math = jar.lib.nz.msl.examples.MathUtils
    Matrix = jar.lib.nz.msl.examples.Matrix

    assert 0.0 <= Math.random() < 1.0
    assert Math.sqrt(32.4) == pytest.approx(5.69209978830308)

    #
    # check LU decomposition
    #

    n = 14
    m1 = Matrix(n, n, 2.0, 8.0)
    L = m1.getL()
    U = m1.getU()
    LU = m1.multiply(L, U)
    for i in range(n):
        for j in range(n):
            assert m1.getValue(i, j) == pytest.approx(LU.getValue(i, j))

    #
    # check QR decomposition
    #

    n = 8
    m2 = Matrix(n, n, -100.0, 100.0)
    Q = m2.getQ()
    R = m2.getR()
    QR = m2.multiply(Q, R)
    for i in range(n):
        for j in range(n):
            assert m2.getValue(i, j) == pytest.approx(QR.getValue(i, j))

    #
    # solve Ax=b
    #
    m3 = jar.gateway.new_array(jar.lib.Double, 3, 3)
    m3[0][0] = 3.
    m3[0][1] = 2.
    m3[0][2] = -1.
    m3[1][0] = 2.
    m3[1][1] = -2.
    m3[1][2] = 4.
    m3[2][0] = -1.0
    m3[2][1] = 0.5
    m3[2][2] = 1.0

    m4 = jar.gateway.new_array(jar.lib.Double, 3)
    m4[0] = 1.0
    m4[1] = -2.0
    m4[2] = 0.0

    A = Matrix(m3)
    x = Matrix.solve(A, Matrix(m4))

    bprime = Matrix.multiply(A, x)
    for i in range(3):
        assert bprime.getValue(i, 0) == pytest.approx(m4[i])

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
            assert identity.getValue(i, j) == pytest.approx(m7.getValue(i, j), abs=1e-9)

    #
    # Check determinant
    #
    a = [[6, 1, 1], [4, -2, 5], [2, 8, 7]]
    ja = jar.gateway.new_array(jar.lib.Double, 3, 3)
    for i in range(3):
        for j in range(3):
            ja[i][j] = float(a[i][j])
    m8 = Matrix(ja)
    assert m8.getDeterminant() == pytest.approx(-306)

    jar.gateway.shutdown()

    import math

    cls = loadlib.LoadLibrary(EXAMPLES_DIR + '/Trig.class')
    Trig = cls.lib.Trig

    x = 0.123456

    assert Trig.cos(x) == pytest.approx(math.cos(x))
    assert Trig.cosh(x) == pytest.approx(math.cosh(x))
    assert Trig.acos(x) == pytest.approx(math.acos(x))
    assert Trig.sin(x) == pytest.approx(math.sin(x))
    assert Trig.sinh(x) == pytest.approx(math.sinh(x))
    assert Trig.asin(x) == pytest.approx(math.asin(x))
    assert Trig.tan(x) == pytest.approx(math.tan(x))
    assert Trig.tanh(x) == pytest.approx(math.tanh(x))
    assert Trig.atan(x) == pytest.approx(math.atan(x))
    assert Trig.atan2(-4.321, x) == pytest.approx(math.atan2(-4.321, x))

    cls.gateway.shutdown()


@pytest.mark.skipif(not loadlib.IS_WINDOWS, reason='comtypes is only supported on Windows')
def test_comtypes():
    # changes to ctypes in Python 3.7.6 and 3.8.1 caused the following exception
    #  TypeError: item 1 in _argtypes_ passes a union by value, which is unsupported.
    # when loading some COM objects, see https://bugs.python.org/issue16575
    #
    # The 'MediaPlayer.MediaPlayer.1' object does not appear to raise this exception
    # and the goal of this test function is not to test the internals of comtypes
    # but LoadLibrary calling the underlying comtypes wrapper properly

    progid = 'MediaPlayer.MediaPlayer.1'

    obj = loadlib.LoadLibrary(progid, 'com')
    # don't care whether it is enabled, just that a boolean is returned
    assert isinstance(obj.lib.IsSoundCardEnabled(), bool)

    with pytest.raises(OSError):
        loadlib.LoadLibrary('ABC.def.GHI', 'com')

    info = loadlib.utils.get_com_info()
    assert info, 'utils.get_com_info() returned an empty dict'

    found_it = False
    for key, value in info.items():
        if value['ProgID'] == progid:
            # don't need to specify libtype='com' since the `key`
            # startswith "{" and endswith "}" which is unique to a COM library
            obj = loadlib.LoadLibrary(key)
            assert isinstance(obj.lib.IsSoundCardEnabled(), bool)
            found_it = True
            break

    assert found_it, 'did not find %s in utils.get_com_info() dict' % progid


def test_unicode_path():
    cls = loadlib.LoadLibrary(u'./tests/uñicödé/Trig.class')
    import math
    x = 0.123456
    assert cls.lib.Trig.cos(x) == pytest.approx(math.cos(x))
    repr(cls)  # this should not raise an exception
    str(cls)  # this should not raise an exception
    cls.gateway.shutdown()

    if (loadlib.IS_MAC or loadlib.IS_LINUX) and sys.version_info[:2] == (3, 8):
        # get fatal crash on MacOS & Python 3.8 when importing pythonnet
        pass
    else:
        net = loadlib.LoadLibrary(u'./tests/uñicödé/Namespace.With.Dots-uñicödé.dll', 'net')
        checker = net.lib.Namespace.With.Dots.Checker()
        assert checker.IsSuccess()
        repr(net)  # this should not raise an exception
        str(net)  # this should not raise an exception

    bitness = u'64' if loadlib.IS_PYTHON_64BIT else u'32'
    cpp = loadlib.LoadLibrary(u'cpp_lib' + bitness + u'-uñicödé')
    assert cpp.lib.add(1, 2) == 3
    repr(cpp)  # this should not raise an exception
    str(cpp)  # this should not raise an exception


@pytest.mark.skipif(
    (loadlib.IS_MAC or loadlib.IS_LINUX) and sys.version_info[:2] == (3, 8),
    reason='get fatal crash with mono and Python 3.8 when importing pythonnet'
)
def test_issue7():
    # checks that Issue #7 is fixed
    net = loadlib.LoadLibrary('./tests/namespace_with_dots/Namespace.With.Dots.dll', 'net')
    checker = net.lib.Namespace.With.Dots.Checker()
    assert checker.IsSuccess()
    repr(net)  # test that the __repr__ and __str__ methods don't raise an exception
    str(net)


def test_issue8():
    # checks that Issue #8 is fixed
    bitness = '64' if loadlib.IS_PYTHON_64BIT else '32'
    loadlib.LoadLibrary(pathlib.Path(os.path.join(EXAMPLES_DIR, 'cpp_lib' + bitness)))


@pytest.mark.skipif(
    (loadlib.IS_MAC or loadlib.IS_LINUX) and sys.version_info[:2] == (3, 8),
    reason='get fatal crash with mono and Python 3.8 when importing pythonnet'
)
def test_dotnet_nested_namespace():
    lib = loadlib.LoadLibrary('./tests/nested_namespaces/nested_namespaces.dll', 'clr').lib

    from math import pi
    assert lib.System.Math.PI == pytest.approx(pi)

    assert lib.A.B.C.Klass().Message() == 'Hello from A.B.C.Klass().Message()'
    assert lib.A.B.Klass().Message() == 'Hello from A.B.Klass().Message()'
    assert lib.A.Klass().Message() == 'Hello from A.Klass().Message()'

    assert lib.Messenger().Message() == 'Hello from Messenger.Message()'

    assert lib.Foo.Bar.Baz('my custom message!').Message() == 'my custom message!'
    assert lib.Foo.Bar.Baz('abc 123').message == 'abc 123'

    # an enum in a namespace
    assert lib.A.B.C.ErrorCode.Unknown == 0
    assert lib.A.B.C.ErrorCode.ConnectionLost == 100
    assert lib.A.B.C.ErrorCode.OutlierReading == 200

    # an enum not in a namespace
    assert lib.Season.Winter == 0
    assert lib.Season.Spring == 1
    assert lib.Season.Summer == 2
    assert lib.Season.Autumn == 3

    Subtracter = lib.A.B.C.Subtracter(8, 9)
    assert Subtracter.x == 8
    assert Subtracter.y == 9
    assert Subtracter.Subtract() == -1

    # Adder is not defined as a public class but can still be created
    Adder = lib.System.Activator.CreateInstance(lib.Adder, 82, -27)
    assert Adder.Add() == 55
    assert Adder.x == 82
    assert Adder.y == -27

    # a struct in a nested namespace
    point = lib.A.B.C.Point()
    assert point.X == 0
    assert point.Y == 0
    assert point.ToString() == 'Point<X=0, Y=0>'
    point.X = 73
    point.Y = -21
    assert point.ToString() == 'Point<X=73, Y=-21>'

    point = lib.A.B.C.Point(-3, 54)
    assert point.X == -3
    assert point.Y == 54
    assert point.ToString() == 'Point<X=-3, Y=54>'

    # a struct not in a namespace
    point = lib.Point()
    assert point.X == 0
    assert point.Y == 0

    point = lib.Point(123, 456)
    assert point.X == 123
    assert point.Y == 456

    # still need to create the instance in Python
    StructWithoutConstructor = lib.StructWithoutConstructor()
    assert StructWithoutConstructor.X == 0
    assert StructWithoutConstructor.Y == 0
    StructWithoutConstructor.X = 1
    StructWithoutConstructor.Y = -1
    assert StructWithoutConstructor.X == 1
    assert StructWithoutConstructor.Y == -1
