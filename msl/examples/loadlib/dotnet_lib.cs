// dotnet_lib.cs
// Examples that show how to pass various data types between Python and a C# library.
//
using System;

// The DotNetMSL namespace contains two classes: BasicMath, ArrayManipulation
namespace DotNetMSL
{
    // A class that is part of the DotNetMSL namespace
    public class BasicMath
    {

        public int add_integers(int a, int b)
        {
            return a + b;
        }

        public float divide_floats(float a, float b)
        {
            return a / b;
        }

        public double multiply_doubles(double a, double b)
        {
            return a * b;
        }

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

    }

    // A class that is part of the DotNetMSL namespace
    public class ArrayManipulation
    {

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

    }
}

// A class that is not part of the DotNetMSL namespace
public class StringManipulation
{

    public string reverse_string(string original)
    {
        char[] charArray = original.ToCharArray();
        Array.Reverse(charArray);
        return new string(charArray);
    }

}

// A static class
public static class StaticClass
{

    public static int add_multiple(int a, int b, int c, int d, int e)
    {
        return a + b + c + d + e;
    }

    public static string concatenate(string a, string b, string c, bool d, string e)
    {
        string res = a + b + c;
        if (d)
        {
            res += e;
        }
        return res;

    }

}
