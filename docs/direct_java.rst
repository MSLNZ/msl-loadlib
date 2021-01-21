.. _direct_java:

Java
----
Since Java byte code is executed in a JVM_ it doesn't matter whether it was
built with a 32- or 64-bit Java Development Kit. The Python interpreter
does not load the Java byte code but communicates with the JVM_ through a
local network socket that is created by Py4J_.

Load a Java archive (view the :ref:`.jar source code <java-lib-jar>`)

.. code-block:: pycon

   >>> from msl.loadlib import LoadLibrary
   >>> from msl.examples.loadlib import EXAMPLES_DIR
   >>> jar = LoadLibrary(EXAMPLES_DIR + '/java_lib.jar')
   >>> jar
   <LoadLibrary libtype=JVMView path=...java_lib.jar>
   >>> jar.gateway
   <py4j.java_gateway.JavaGateway object at ...>

The Java archive contains a ``nz.msl.examples`` package with two classes,
``MathUtils`` and ``Matrix``

.. code-block:: pycon

   >>> MathUtils = jar.lib.nz.msl.examples.MathUtils
   >>> Matrix = jar.lib.nz.msl.examples.Matrix

Calculate the square root of a number using the ``MathUtils`` class

.. code-block:: pycon

   >>> MathUtils.sqrt(32.4)
   5.692099788303...

Solve a linear system of equations, Ax=b

.. code-block:: pycon

   >>> A = jar.gateway.new_array(jar.lib.Double, 3, 3)
   >>> coeff = [[3, 2, -1], [7, -2, 4], [-1, 5, 1]]
   >>> for i in range(3):
   ...     for j in range(3):
   ...         A[i][j] = float(coeff[i][j])
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

Verify that `x` is the solution

.. code-block:: pycon

   >>> for i in range(3):
   ...     x_i = 0.0
   ...     for j in range(3):
   ...         x_i += coeff[i][j] * x.getValue(j,0)
   ...     assert abs(x_i - b[i]) < 1e-12
   ...

Shutdown the connection to the JVM_ when you are finished

.. code-block:: pycon

   >>> jar.gateway.shutdown()

Load Java byte code (view the :ref:`.class source code <java-lib-class>`)

.. code-block:: pycon

   >>> cls = LoadLibrary(EXAMPLES_DIR + '/Trig.class')
   >>> cls
   <LoadLibrary libtype=JVMView path=...Trig.class>
   >>> cls.lib
   <py4j.java_gateway.JVMView object at ...>

The Java library contains a ``Trig`` class, which calculates various
trigonometric quantities

.. code-block:: pycon

   >>> Trig = cls.lib.Trig
   >>> Trig
   <py4j.java_gateway.JavaClass object at ...>
   >>> Trig.cos(1.2)
   0.3623577544766...
   >>> Trig.asin(0.6)
   0.6435011087932...
   >>> Trig.tanh(1.3)
   0.8617231593133...

Once again, shutdown the connection to the JVM_ when you are finished

.. code-block:: pycon

   >>> cls.gateway.shutdown()

.. _JVM: https://en.wikipedia.org/wiki/Java_virtual_machine
.. _Py4J: https://www.py4j.org/
