Structs
-------
It is possible to :mod:`pickle` a :class:`ctypes.Structure` and pass the
*struct* object between :class:`~msl.examples.loadlib.cpp64.Cpp64` and
:class:`~msl.examples.loadlib.cpp32.Cpp32` provided that the *struct* is
a **fixed size** in memory (i.e., the *struct* does not contain any pointers).
If the *struct* contains pointers then you must create the *struct* within
:class:`~msl.examples.loadlib.cpp32.Cpp32` and you can only pass the
**values** of the *struct* back to :class:`~msl.examples.loadlib.cpp64.Cpp64`.

.. attention::

   The following will only work if :class:`~msl.examples.loadlib.cpp64.Cpp64`
   is run using Python 3 because :class:`~msl.examples.loadlib.cpp32.Cpp32`
   is running on Python 3 and there are issues with :mod:`ctypes` and :mod:`pickle`
   when mixing Python 2 (client) and Python 3 (server).

The :ref:`cpp_lib32 <cpp-lib>` library contains the following structs

.. code-block:: cpp

    struct Point {
        double x;
        double y;
    };

    struct FourPoints {
        Point points[4];
    };

    struct NPoints {
        int n;
        Point *points;
    };

The :meth:`~msl.examples.loadlib.cpp64.Cpp64.distance_4_points` method uses the
:class:`~msl.examples.loadlib.cpp32.FourPoints` struct to calculate the total
distance connecting 4 :class:`~msl.examples.loadlib.cpp32.Point` structs. Since
the :class:`~msl.examples.loadlib.cpp32.FourPoints` struct is a **fixed size** it
can be created in 64-bit Python, *pickled* and then *unpickled* in
:class:`~msl.examples.loadlib.cpp32.Cpp32`

.. invisible-code-block: pycon

   >>> SKIP_IF_MACOS()
   >>> from msl.examples.loadlib import Cpp64
   >>> cpp = Cpp64()

.. code-block:: pycon

   >>> from msl.examples.loadlib import FourPoints
   >>> fp = FourPoints((0, 0), (0, 1), (1, 1), (1, 0))
   >>> cpp.distance_4_points(fp)
   4.0

The :meth:`Cpp32.circumference <msl.examples.loadlib.cpp32.Cpp32.circumference>`
method uses the :class:`~msl.examples.loadlib.cpp32.NPoints` struct to calculate
the circumference of a circle using *n* :class:`~msl.examples.loadlib.cpp32.Point`
structs. Since the :class:`~msl.examples.loadlib.cpp32.NPoints` struct is
**not a fixed size** it must be created in the
:meth:`Cpp32.circumference <msl.examples.loadlib.cpp32.Cpp32.circumference>` method.
The :meth:`Cpp64.circumference <msl.examples.loadlib.cpp64.Cpp64.circumference>`
method takes the values of the *radius* and *n* as input arguments to pass to the
:meth:`Cpp32.circumference <msl.examples.loadlib.cpp32.Cpp32.circumference>` method.

.. code-block:: pycon

   >>> for i in range(16):
   ...     print(cpp.circumference(0.5, 2**i))
   ...
   0.0
   2.0
   2.828427124746...
   3.061467458920...
   3.121445152258...
   3.136548490545...
   3.140331156954...
   3.141277250932...
   3.141513801144...
   3.141572940367...
   3.141587725277...
   3.141591421511...
   3.141592345569...
   3.141592576584...
   3.141592634337...
   3.141592648775...
