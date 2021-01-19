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

    def __init__(self, host, port, **kwargs):
        """
        Example of a class that is a wrapper around a 32-bit .NET Framework library,
        :ref:`dotnet_lib32.dll <dotnet-lib>`. `Python for .NET <https://pythonnet.github.io/>`_
        can handle many native Python data types as input arguments.

        Parameters
        ----------
        host : :class:`str`
            The IP address of the server.
        port : :class:`int`
            The port to open on the server.

        Note
        ----
        Any class that is a subclass of :class:`~msl.loadlib.server32.Server32` **MUST**
        provide two arguments in its constructor: `host` and `port` (in that order)
        and `**kwargs`. Otherwise the ``server32`` executable, see
        :class:`~msl.loadlib.start_server32`, cannot create an instance of the
        :class:`~msl.loadlib.server32.Server32` subclass.
        """
        super(DotNet32, self).__init__(os.path.join(os.path.dirname(__file__), 'dotnet_lib32.dll'),
                                       'net', host, port)

        self.BasicMath = self.lib.DotNetMSL.BasicMath()
        self.ArrayManipulation = self.lib.DotNetMSL.ArrayManipulation()

    def get_class_names(self):
        """Returns the class names in the library.

        See the corresponding 64-bit :meth:`~.dotnet64.DotNet64.get_class_names` method.

        Returns
        -------
        :class:`list` of :class:`str`
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
        a : :class:`int`
            The first integer.
        b : :class:`int`
            The second integer.

        Returns
        -------
        :class:`int`
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
        a : :class:`float`
            The first number.
        b : :class:`float`
            The second number.

        Returns
        -------
        :class:`float`:
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
        a : :class:`float`
            The first number.
        b : :class:`float`
            The second number.

        Returns
        -------
        :class:`float`
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
        a : :class:`float`
            The first double-precision number.
        b : :class:`float`
            The second double-precision number.
        do_addition : :class:`bool`
            Whether to **add** the numbers.

        Returns
        -------
        :class:`float`
            Either `a` + `b` if `do_addition` is :data:`True` else `a` - `b`.
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
        a : :class:`float`
            The scalar value.
        xin : :class:`list` of :class:`float`
            The array to modify.

        Returns
        -------
        :class:`list` of :class:`float`
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

        Parameters
        ----------
        a1 : :class:`list` of :class:`list` of :class:`float`
            The first matrix.
        a2 : :class:`list` of :class:`list` of :class:`float`
            The second matrix.

        Returns
        -------
        :class:`list` of :class:`list` of :class:`float`
             The result of `a1` * `a2`.
        """
        nrows1 = len(a1)
        ncols1 = len(a1[0])

        nrows2 = len(a2)
        ncols2 = len(a2[0])

        if not ncols1 == nrows2:
            msg = "Cannot multiply a {}x{} matrix with a {}x{} matrix"
            raise ValueError(msg.format(nrows1, ncols1, nrows2, ncols2))

        m1 = self.lib.System.Array.CreateInstance(self.lib.System.Double, nrows1, ncols1)
        for r in range(nrows1):
            for c in range(ncols1):
                m1[r, c] = a1[r][c]

        m2 = self.lib.System.Array.CreateInstance(self.lib.System.Double, nrows2, ncols2)
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
        original : :class:`str`
            The original string.

        Returns
        -------
        :class:`str`
            The string reversed.
        """
        return self.lib.StringManipulation().reverse_string(original)

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
        a : :class:`int`
            An integer.
        b : :class:`int`
            An integer.
        c : :class:`int`
            An integer.
        d : :class:`int`
            An integer.
        e : :class:`int`
            An integer.

        Returns
        -------
        :class:`int`
            The sum of the input arguments.
        """
        return self.lib.StaticClass.add_multiple(a, b, c, d, e)

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
        a : :class:`str`
            A string.
        b : :class:`str`
            A string.
        c : :class:`str`
            A string.
        d : :class:`bool`
            Whether to include `e` in the concatenation.
        e : :class:`str`
            A string.

        Returns
        -------
        :class:`str`
            The strings concatenated together.
        """
        return self.lib.StaticClass.concatenate(a, b, c, d, e)
