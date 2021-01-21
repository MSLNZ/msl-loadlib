Strings
-------
In this example the memory for the reversed string is allocated in Python,
see :meth:`~msl.examples.loadlib.cpp64.Cpp64.reverse_string_v1`

.. invisible-code-block: pycon

   >>> SKIP_IF_MACOS()
   >>> from msl.examples.loadlib import Cpp64
   >>> cpp = Cpp64()

.. code-block:: pycon

   >>> cpp.reverse_string_v1('hello world!')
   '!dlrow olleh'

In this example the memory for the reversed string is allocated in C++,
see :meth:`~msl.examples.loadlib.cpp64.Cpp64.reverse_string_v2`

.. code-block:: pycon

   >>> cpp.reverse_string_v2('uncertainty')
   'ytniatrecnu'
