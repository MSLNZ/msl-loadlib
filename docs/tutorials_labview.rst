.. _tutorial_labview:

==============================================
Load a 32-bit LabVIEW library in 64-bit Python
==============================================

This example shows how to access a 32-bit LabVIEW library from 64-bit Python.
:class:`~msl.examples.loadlib.labview32.Labview32` is the 32-bit server and
:class:`~msl.examples.loadlib.labview64.Labview64` is the 64-bit client.
The source code of the LabVIEW program is available :ref:`here <labview-lib>`.

.. attention::
   This example requires that a 32-bit `LabVIEW Run-Time Engine`_
   is installed and that the operating system is Windows.

Create a :class:`~msl.examples.loadlib.labview64.Labview64` client to communicate
with the 32-bit :ref:`labview_lib32 <labview-lib>` library

.. invisible-code-block: pycon

   >>> SKIP_LABVIEW32()

.. code-block:: pycon

   >>> from msl.examples.loadlib import Labview64
   >>> labview = Labview64()

Calculate the mean and the *sample* variance and standard deviation of some data, see
:meth:`~msl.examples.loadlib.labview64.Labview64.stdev`

.. code-block:: pycon

   >>> data = [1, 2, 3, 4, 5, 6, 7, 8, 9]
   >>> labview.stdev(data)
   (5.0, 7.5, 2.7386127875258306)

Calculate the mean and the *population* variance and standard deviation of data

.. code-block:: pycon

   >>> labview.stdev(data, 1)
   (5.0, 6.666666666666667, 2.581988897471611)

Shutdown the 32-bit server when you are done communicating with the 32-bit library

.. code-block:: pycon

   >>> stdout, stderr = labview.shutdown_server32()

.. _LabVIEW Run-Time Engine: https://www.ni.com/en-nz/support/downloads/software-products/download.labview.html#369481
