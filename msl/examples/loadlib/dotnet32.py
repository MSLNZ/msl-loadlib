"""
A wrapper around a 32-bit .NET library, :ref:`dotnet_lib32 <dotnet-lib>`.

Example of a server that loads a 32-bit .NET library, :ref:`dotnet_lib32.dll <dotnet-lib>`
in a 32-bit Python interpreter to host the library. The corresponding :mod:`~.dotnet64`
module can be executed by a 64-bit Python interpreter and the :class:`~.dotnet64.DotNet64`
class can send a request to the :class:`~.dotnet32.DotNet32` class which calls the
32-bit library to execute the request and then return the response from the library.
"""
import os

from msl.loadlib import Server32


class DotNet32(Server32):
    """
    Example of a class that is a wrapper around a 32-bit .NET Framework library,
    :ref:`dotnet_lib32.dll <dotnet-lib>`. `Python for .NET <http://pythonnet.github.io/>`_
    can handle many native Python data types as input arguments.

    Parameters
    ----------
    host : :obj:`str`
        The IP address of the server.
    port : :obj:`int`
        The port to open on the server.
    quiet : :obj:`bool`
        Whether to hide :obj:`sys.stdout` messages from the server.

    Note
    ----
    Any class that is a subclass of :class:`~msl.loadlib.server32.Server32` **MUST**
    provide three arguments in its constructor: `host`, `port` and `quiet`
    (in that order) and `**kwargs`. Otherwise the ``server32`` executable, see
    :class:`~msl.loadlib.start_server32`, cannot create an instance of the
    :class:`~msl.loadlib.server32.Server32` subclass.
    """
    def __init__(self, host, port, quiet, **kwargs):
        Server32.__init__(self, os.path.join(os.path.dirname(__file__), 'dotnet_lib32.dll'),
                          'net', host, port, quiet)

        self.BasicMath = self.lib.DotNetMSL.BasicMath()
        self.ArrayManipulation = self.lib.DotNetMSL.ArrayManipulation()

    def get_class_names(self):
        """Returns the class names in the library.
        
        See the corresponding 64-bit :meth:`~.dotnet64.DotNet64.get_class_names` method.
        
        Returns
        -------
        :obj:`list` of :obj:`str`
            The names of the classes that are available in :ref:`dotnet_lib32.dll <dotnet-lib>`.        
        """
        return ';'.join(str(name) for name in self.assembly.GetTypes()).split(';')

    def add_integers(self, a, b):
        """Add two integers.

        The corresponding C# code is

        .. code-block:: csharp

            public int add_integers(int a, int b)
            {
                return a + b;
            }

        See the corresponding 64-bit :meth:`~.dotnet64.DotNet64.add_integers` method.

        Parameters
        ----------
        a : :obj:`int`
            The first integer.
        b : :obj:`int`
            The second integer.

        Returns
        -------
        :obj:`int`
            The sum of `a` and `b`.
        """
        return self.BasicMath.add_integers(a, b)

    def divide_floats(self, a, b):
        """Divide two C# floating-point numbers.

        The corresponding C# code is

        .. code-block:: csharp

            public float divide_floats(float a, float b)
            {
                return a / b;
            }

        See the corresponding 64-bit :meth:`~.dotnet64.DotNet64.divide_floats` method.

        Parameters
        ----------
        a : :obj:`float`
            The first number.
        b : :obj:`float`
            The second number.

        Returns
        -------
        :obj:`float`:
            The quotient of `a` / `b`.
        """
        return self.BasicMath.divide_floats(a, b)

    def multiply_doubles(self, a, b):
        """Multiply two C# double-precision numbers.

        The corresponding C# code is

        .. code-block:: csharp

            public double multiply_doubles(double a, double b)
            {
                return a * b;
            }

        See the corresponding 64-bit :meth:`~.dotnet64.DotNet64.multiply_doubles` method.

        Parameters
        ----------
        a : :obj:`float`
            The first number.
        b : :obj:`float`
            The second number.

        Returns
        -------
        :obj:`float`
            The product of `a` * `b`.
        """
        return self.BasicMath.multiply_doubles(a, b)

    def add_or_subtract(self, a, b, do_addition):
        """Add or subtract two C# double-precision numbers.

        The corresponding C# code is

        .. code-block:: csharp

            public double add_or_subtract(double a, double b, bool do_addition)
            {
                if (do_addition)
                {
                    return a + b;
                }
                else
                {
                    return a - b;
                }
            }

        See the corresponding 64-bit :meth:`~.dotnet64.DotNet64.add_or_subtract` method.

        Parameters
        ----------
        a : :obj:`float`
            The first double-precision number.
        b : :obj:`float`
            The second double-precision number.
        do_addition : :obj:`bool`
            Whether to **add** the numbers.

        Returns
        -------
        :obj:`float`
            Either `a` + `b` if `do_addition` is :obj:`True` else `a` - `b`.
        """
        return self.BasicMath.add_or_subtract(a, b, do_addition)

    def scalar_multiply(self, a, xin):
        """Multiply each element in an array by a number.

        The corresponding C# code is

        .. code-block:: csharp

            public double[] scalar_multiply(double a, double[] xin)
            {
                int n = xin.GetLength(0);
                double[] xout = new double[n];
                for (int i = 0; i < n; i++)
                {
                    xout[i] = a * xin[i];
                }
                return xout;
            }

        See the corresponding 64-bit :meth:`~.dotnet64.DotNet64.scalar_multiply` method.

        Parameters
        ----------
        a : :obj:`float`
            The scalar value.
        xin : :obj:`list` of :obj:`float`
            The array to modify.

        Returns
        -------
        :obj:`list` of :obj:`float`
            A new array with each element in `xin` multiplied by `a`.
        """
        ret = self.ArrayManipulation.scalar_multiply(a, xin)
        return [val for val in ret]

    def multiply_matrices(self, a1, a2):
        """Multiply two matrices.

        The corresponding C# code is

        .. code-block:: csharp

            public double[,] multiply_matrices(double[,] A, double[,] B)
            {
                int rA = A.GetLength(0);
                int cA = A.GetLength(1);
                int rB = B.GetLength(0);
                int cB = B.GetLength(1);
                double temp = 0;
                double[,] C = new double[rA, cB];
                if (cA != rB)
                {
                    Console.WriteLine("matrices can't be multiplied!");
                    return new double[0, 0];
                }
                else
                {
                    for (int i = 0; i < rA; i++)
                    {
                        for (int j = 0; j < cB; j++)
                        {
                            temp = 0;
                            for (int k = 0; k < cA; k++)
                            {
                                temp += A[i, k] * B[k, j];
                            }
                            C[i, j] = temp;
                        }
                    }
                    return C;
                }
            }

        See the corresponding 64-bit :meth:`~.dotnet64.DotNet64.multiply_matrices` method.

        Note
        ----
        The **CLR** package from `Python for .NET <http://pythonnet.github.io/>`_ contains
        the `System <https://msdn.microsoft.com/en-us/library/system(v=vs.110).aspx>`_
        namespace from the .NET Framework that is required to create and initialize a
        2D matrix.

        Parameters
        ----------
        a1 : :obj:`list` of :obj:`list` of :obj:`float`
            The first matrix.
        a2 : :obj:`list` of :obj:`list` of :obj:`float`
            The second matrix.

        Returns
        -------
        :obj:`list` of :obj:`list` of :obj:`float`
             The result of `a1` * `a2`.
        """
        # System is part of the clr package from Python for .NET.
        # Therefore, until "import clr" has been performed the System module cannot be imported.
        # The Server32 class imports clr and so we do not have to do it here.
        from System import Array, Double

        nrows1 = len(a1)
        ncols1 = len(a1[0])

        nrows2 = len(a2)
        ncols2 = len(a2[0])

        if not ncols1 == nrows2:
            msg = "Cannot multiply a {}x{} matrix with a {}x{} matrix"
            raise ValueError(msg.format(nrows1, ncols1, nrows2, ncols2))

        m1 = Array.CreateInstance(Double, nrows1, ncols1)
        for r in range(nrows1):
            for c in range(ncols1):
                m1[r, c] = a1[r][c]

        m2 = Array.CreateInstance(Double, nrows2, ncols2)
        for r in range(nrows2):
            for c in range(ncols2):
                m2[r, c] = a2[r][c]

        ret = self.ArrayManipulation.multiply_matrices(m1, m2)
        return [[ret[r, c] for c in range(ncols2)] for r in range(nrows1)]

    def reverse_string(self, original):
        """Reverse a string.

        The corresponding C# code is

        .. code-block:: csharp

            public string reverse_string(string original)
            {
                char[] charArray = original.ToCharArray();
                Array.Reverse(charArray);
                return new string(charArray);
            }

        See the corresponding 64-bit :meth:`~.dotnet64.DotNet64.reverse_string` method.

        Parameters
        ----------
        original : :obj:`str`
            The original string.

        Returns
        -------
        :obj:`str`
            The string reversed.
        """
        return self.lib.StringManipulation.reverse_string(original)

    def add_multiple(self, a, b, c, d, e):
        """Add multiple integers. *Calls a static method in a static class.*

        The corresponding C# code is

        .. code-block:: csharp

            public static int add_multiple(int a, int b, int c, int d, int e)
            {
                return a + b + c + d + e;
            }

        See the corresponding 64-bit :meth:`~.dotnet64.DotNet64.add_multiple` method.

        Parameters
        ----------
        a : :obj:`int`
            An integer.
        b : :obj:`int` 
            An integer.
        c : :obj:`int`
            An integer.
        d : :obj:`int`
            An integer.
        e : :obj:`int`
            An integer.

        Returns
        -------
        :obj:`int`
            The sum of the input arguments.
        """
        return self.lib.StaticClass.GetMethod('add_multiple').Invoke(None, [a, b, c, d, e])

    def concatenate(self, a, b, c, d, e):
        """Concatenate strings. *Calls a static method in a static class.*

        The corresponding C# code is

        .. code-block:: csharp

            public static string concatenate(string a, string b, string c, bool d, string e)
            {
                string res = a + b + c;
                if (d)
                {
                    res += e;
                }
                return res;

            }

        See the corresponding 64-bit :meth:`~.dotnet64.DotNet64.concatenate` method.

        Parameters
        ----------
        a : :obj:`str`
            A string.
        b : :obj:`str`
            A string.
        c : :obj:`str`
            A string.
        d : :obj:`bool`
            Whether to include `e` in the concatenation.
        e : :obj:`str`
            A string.

        Returns
        -------
        :obj:`str`
            The strings concatenated together.
        """
        return self.lib.StaticClass.GetMethod('concatenate').Invoke(None, [a, b, c, d, e])
