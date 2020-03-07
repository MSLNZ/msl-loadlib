namespace A
{
    namespace B
    {
        namespace C
        {
            public class Klass
            {
                public string Message()
                {
                    return "Hello from A.B.C.Klass().Message()";
                }
            }

            public enum ErrorCode : ushort
            {
                Unknown,
                ConnectionLost = 100,
                OutlierReading = 200
            }

            public class Subtracter
            {
                public int x;
                public int y;

                public Subtracter(int x, int y)
                {
                    this.x = x;
                    this.y = y;
                }

                public int Subtract()
                {
                    return x - y;
                }
            }

            public struct Point
            {
                public int X, Y;

                public Point(int x, int y)
                {
                    X = x;
                    Y = y;
                }

                public override string ToString() => $"Point<X={X}, Y={Y}>";
            }
        }
        public class Klass
        {
            public string Message()
            {
                return "Hello from A.B.Klass().Message()";
            }
        }
    }

    public class Klass
    {
        public string Message()
        {
            return "Hello from A.Klass().Message()";
        }
    }

}

public class Messenger
{
    public string Message()
    {
        return "Hello from Messenger.Message()";
    }
}

class Adder
{
    public int x;
    public int y;

    public Adder(int x, int y)
    {
        this.x = x;
        this.y = y;
    }

    public int Add()
    {
        return x + y;
    }

}

namespace Foo.Bar
{
    public class Baz
    {
        public string message;

        public Baz(string msg)
        {
            message = msg;
        }

        public string Message()
        {
            return message;
        }
    }
}

public enum Season
{
    Winter,
    Spring,
    Summer,
    Autumn    
}

public struct Point
{
 
    public Point(int x, int y)
    {
        X = x;
        Y = y;
    }

    public int X { get; }
    public int Y { get; }

}

public struct StructWithoutConstructor
{
    public int X;
    public int Y;
}
