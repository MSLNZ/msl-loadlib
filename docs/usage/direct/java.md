# Java {: #direct-java }

Since Java byte code is executed in a [JVM]{:target="_blank"} it doesn't matter whether it was built with a 32- or 64-bit Java Development Kit. The Python interpreter does not load the Java byte code but communicates with the [JVM]{:target="_blank"} through a local network socket that is managed by [Py4J]{:target="_blank"}.

## Example (.jar)
Load the example [Java archive][java-lib], `java_lib.jar`

```pycon
>>> from msl.loadlib import LoadLibrary
>>> from msl.examples.loadlib import EXAMPLES_DIR
>>> jar = LoadLibrary(EXAMPLES_DIR / "java_lib.jar")
>>> jar
<LoadLibrary libtype=JVMView path=...java_lib.jar>
>>> jar.gateway
<py4j.java_gateway.JavaGateway object at ...>

```

The Java archive contains a `nz.msl.examples` package with two classes, `MathUtils` and `Matrix`

```pycon
>>> MathUtils = jar.lib.nz.msl.examples.MathUtils
>>> Matrix = jar.lib.nz.msl.examples.Matrix

```

Calculate the square root of a number using the `MathUtils` class

```pycon
>>> MathUtils.sqrt(32.4)
5.692099788303...

```

Solve a linear system of equations, `Ax=b`, using the `Matrix` library class and the `gateway` object to allocate memory for the `A` and `b` arrays

```pycon
>>> A = jar.gateway.new_array(jar.lib.Double, 3, 3)
>>> coefficients = [[3, 2, -1], [7, -2, 4], [-1, 5, 1]]
>>> for i in range(3):
...     for j in range(3):
...         A[i][j] = float(coefficients[i][j])
...
>>> b = jar.gateway.new_array(jar.lib.Double, 3)
>>> b[0] = 4.0
>>> b[1] = 15.0
>>> b[2] = 12.0
>>> x = Matrix.solve(Matrix(A), Matrix(b))
>>> print(x.toString())
+1.000000e+00
+2.000000e+00
+3.000000e+00

```

Verify that `x` is the solution

```pycon
>>> for i in range(3):
...     x_i = 0.0
...     for j in range(3):
...         x_i += coefficients[i][j] * x.getValue(j,0)
...     assert abs(x_i - b[i]) < 1e-12
...

```

Shutdown the connection to the [JVM]{:target="_blank"} when finished

```pycon
>>> jar.gateway.shutdown()

```

## Example (.class)

Load the example [Java byte code][java-lib], `Trig.class`

```pycon
>>> cls = LoadLibrary(EXAMPLES_DIR / "Trig.class")
>>> cls
<LoadLibrary libtype=JVMView path=...Trig.class>
>>> cls.lib
<py4j.java_gateway.JVMView object at ...>

```

The Java library contains a `Trig` class, which calculates various trigonometric quantities

```pycon
>>> Trig = cls.lib.Trig
>>> Trig
<py4j.java_gateway.JavaClass object at ...>
>>> Trig.cos(1.2)
0.3623577544766...
>>> Trig.asin(0.6)
0.6435011087932...
>>> Trig.tanh(1.3)
0.8617231593133...

```

Shutdown the connection to the [JVM]{:target="_blank"} when finished

```pycon
>>> cls.gateway.shutdown()

```

## Java Source Code {: #java-lib }

??? example "java_lib.jar"

    === "MathUtils.java"
        ```java
        --8<-- "src/msl/examples/loadlib/nz/msl/examples/MathUtils.java"
        ```

    === "Matrix.java"
        ```java
        --8<-- "src/msl/examples/loadlib/nz/msl/examples/Matrix.java"
        ```

??? example "Trig.class"
    ```java
    --8<-- "src/msl/examples/loadlib/Trig.java"
    ```

[JVM]: https://en.wikipedia.org/wiki/Java_virtual_machine
[Py4J]: https://www.py4j.org/
