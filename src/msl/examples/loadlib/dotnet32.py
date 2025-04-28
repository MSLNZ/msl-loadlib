"""Wrapper around a 32-bit .NET library.

Example of a server that loads a 32-bit library, [dotnet_lib32.dll][dotnet-lib],
in a 32-bit Python interpreter to host the library. The corresponding [DotNet64][] class
is created in a 64-bit Python interpreter and the [DotNet64][] class sends requests
to the [DotNet32][] class which calls the 32-bit library to execute the request and
then returns the response from the library.
"""

from __future__ import annotations

import os
from typing import Sequence

from msl.loadlib import Server32


class DotNet32(Server32):
    """Wrapper around a 32-bit .NET library."""

    def __init__(self, host: str, port: int) -> None:
        """Wrapper around a 32-bit .NET library.

        [Python for .NET](https://pythonnet.github.io/){:target="_blank"}
        can handle many native Python data types as input arguments.

        Args:
            host: The IP address (or hostname) to use for the server.
            port: The port to open for the server.
        """
        path = os.path.join(os.path.dirname(__file__), "dotnet_lib32.dll")
        super().__init__(path, "net", host, port)

        self.BasicMath = self.lib.DotNetMSL.BasicMath()
        self.ArrayManipulation = self.lib.DotNetMSL.ArrayManipulation()

    def get_class_names(self) -> list[str]:
        """Gets the class names in the library.

        Calls [GetTypes](https://learn.microsoft.com/en-us/dotnet/api/system.reflection.assembly.gettypes){:target="_blank"}
        using the [assembly][msl.loadlib.load_library.LoadLibrary.assembly] property.

        See the corresponding [DotNet64.get_class_names][msl.examples.loadlib.dotnet64.DotNet64.get_class_names] method.

        Returns:
            The names of the classes that are available in [dotnet_lib32.dll][dotnet-lib].
        """
        return ";".join(str(name) for name in self.assembly.GetTypes()).split(";")

    def add_integers(self, a: int, b: int) -> int:
        """Add two integers.

        The corresponding C# code is

        ```csharp
        public int add_integers(int a, int b)
        {
            return a + b;
        }
        ```

        See the corresponding [DotNet64.add_integers][msl.examples.loadlib.dotnet64.DotNet64.add_integers] method.

        Args:
            a: First integer.
            b: Second integer.

        Returns:
            The sum, `a + b`.
        """
        return self.BasicMath.add_integers(a, b)

    def divide_floats(self, a: float, b: float) -> float:
        """Divide two C# floating-point numbers.

        The corresponding C# code is

        ```csharp
        public float divide_floats(float a, float b)
        {
            return a / b;
        }
        ```

        See the corresponding [DotNet64.divide_floats][msl.examples.loadlib.dotnet64.DotNet64.divide_floats] method.

        Args:
            a: The numerator.
            b: The denominator.

        Returns:
            The quotient, `a / b`.
        """
        return self.BasicMath.divide_floats(a, b)

    def multiply_doubles(self, a: float, b: float) -> float:
        """Multiply two C# double-precision numbers.

        The corresponding C# code is

        ```csharp
        public double multiply_doubles(double a, double b)
        {
            return a * b;
        }
        ```

        See the corresponding [DotNet64.multiply_doubles][msl.examples.loadlib.dotnet64.DotNet64.multiply_doubles]
        method.

        Args:
            a: First double-precision number.
            b: Second double-precision number.

        Returns:
            The product, `a * b`.
        """
        return self.BasicMath.multiply_doubles(a, b)

    def add_or_subtract(self, a: float, b: float, do_addition: bool) -> float:
        """Add or subtract two C# double-precision numbers.

        The corresponding C# code is

        ```csharp
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
        ```

        See the corresponding [DotNet64.add_or_subtract][msl.examples.loadlib.dotnet64.DotNet64.add_or_subtract] method.

        Args:
            a: First double-precision number.
            b: Second double-precision number.
            do_addition: Whether to add or subtract the numbers.

        Returns:
            `a + b` if `do_addition` is `True` else `a - b`.
        """
        return self.BasicMath.add_or_subtract(a, b, do_addition)

    def scalar_multiply(self, a: float, xin: Sequence[float]) -> list[float]:
        """Multiply each element in an array by a number.

        The corresponding C# code is

        ```csharp
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
        ```

        See the corresponding [DotNet64.scalar_multiply][msl.examples.loadlib.dotnet64.DotNet64.scalar_multiply] method.

        Args:
            a: Scalar value.
            xin: Array to modify.

        Returns:
            A new array with each element in `xin` multiplied by `a`.
        """
        ret = self.ArrayManipulation.scalar_multiply(a, xin)
        return [val for val in ret]

    def multiply_matrices(self, a1: Sequence[Sequence[float]], a2: Sequence[Sequence[float]]) -> list[list[float]]:
        """Multiply two matrices.

        The corresponding C# code is

        ```csharp
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
        ```

        See the corresponding [DotNet64.multiply_matrices][msl.examples.loadlib.dotnet64.DotNet64.multiply_matrices]
        method.

        Args:
            a1: First matrix.
            a2: Second matrix.

        Returns:
            The result, `a1 @ a2`.
        """
        n_rows1 = len(a1)
        n_cols1 = len(a1[0])

        n_rows2 = len(a2)
        n_cols2 = len(a2[0])

        if n_cols1 != n_rows2:
            msg = f"Cannot multiply a {n_rows1}x{n_cols1} matrix with a {n_rows2}x{n_cols2} matrix"
            raise ValueError(msg)

        m1 = self.lib.System.Array.CreateInstance(self.lib.System.Double, n_rows1, n_cols1)
        for r in range(n_rows1):
            for c in range(n_cols1):
                m1[r, c] = a1[r][c]

        m2 = self.lib.System.Array.CreateInstance(self.lib.System.Double, n_rows2, n_cols2)
        for r in range(n_rows2):
            for c in range(n_cols2):
                m2[r, c] = a2[r][c]

        ret = self.ArrayManipulation.multiply_matrices(m1, m2)
        return [[ret[r, c] for c in range(n_cols2)] for r in range(n_rows1)]

    def reverse_string(self, original: str) -> str:
        """Reverse a string.

        The corresponding C# code is

        ```csharp
        public string reverse_string(string original)
        {
            char[] charArray = original.ToCharArray();
            Array.Reverse(charArray);
            return new string(charArray);
        }
        ```

        See the corresponding [DotNet64.reverse_string][msl.examples.loadlib.dotnet64.DotNet64.reverse_string] method.

        Args:
            original: The original string.

        Returns:
            The string reversed.
        """
        return self.lib.StringManipulation().reverse_string(original)

    def add_multiple(self, a: int, b: int, c: int, d: int, e: int) -> int:
        """Add multiple integers.

        Calls a static method in a static class.

        The corresponding C# code is

        ```csharp
        public static int add_multiple(int a, int b, int c, int d, int e)
        {
            return a + b + c + d + e;
        }
        ```

        See the corresponding [DotNet64.add_multiple][msl.examples.loadlib.dotnet64.DotNet64.add_multiple] method.

        Args:
            a: First integer.
            b: Second integer.
            c: Third integer.
            d: Fourth integer.
            e: Fifth integer.

        Returns:
            The sum of the input arguments.
        """
        return self.lib.StaticClass.add_multiple(a, b, c, d, e)

    def concatenate(self, a: str, b: str, c: str, d: bool, e: str) -> str:
        """Concatenate strings.

        Calls a static method in a static class.

        The corresponding C# code is

        ```csharp
        public static string concatenate(string a, string b, string c, bool d, string e)
        {
            string res = a + b + c;
            if (d)
            {
                res += e;
            }
            return res;
        }
        ```

        See the corresponding [DotNet64.concatenate][msl.examples.loadlib.dotnet64.DotNet64.concatenate] method.

        Args:
            a: First string.
            b: Second string.
            c: Third string.
            d: Whether to include `e` in the concatenation.
            e: Fourth string.

        Returns:
            The strings concatenated together.
        """
        return self.lib.StaticClass.concatenate(a, b, c, d, e)
