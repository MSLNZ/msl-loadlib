.. _direct_cpp:

C++
---
Load a 64-bit C++ library in 64-bit Python (view the :ref:`C++ source code <cpp-lib>`).
*To load the 32-bit library in 32-bit Python use* ``'/cpp_lib32'``.

.. invisible-code-block: pycon

   >>> SKIP_IF_32BIT() or SKIP_IF_MACOS_ARM64()

.. code-block:: pycon

   >>> from msl.loadlib import LoadLibrary
   >>> from msl.examples.loadlib import EXAMPLES_DIR
   >>> cpp = LoadLibrary(EXAMPLES_DIR + '/cpp_lib64')

Call the ``add`` function to calculate the sum of two integers

.. code-block:: pycon

   >>> cpp.lib.add(1, 2)
   3
