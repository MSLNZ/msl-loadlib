.. _tutorial_labview:

==============================================
Load a 32-bit LabVIEW library in 64-bit Python
==============================================

.. attention::
   This example requires that the appropriate
   `LabVIEW Run-Time Engine <https://www.ni.com/download/labview-run-time-engine-2015/5507/en/>`_ is installed
   and that the operating system is Windows.

This example shows how to access a 32-bit LabVIEW library from a module that is run by a
64-bit Python interpreter by using `inter-process communication
<https://en.wikipedia.org/wiki/Inter-process_communication>`_.
:class:`~msl.examples.loadlib.labview32.Labview32` is the 32-bit server and
:class:`~msl.examples.loadlib.labview64.Labview64` is the 64-bit client. The source
code of the LabVIEW program is available :ref:`here <labview-lib>`.

Create a :class:`~msl.examples.loadlib.labview64.Labview64` client to communicate with the
32-bit :ref:`labview_lib32 <labview-lib>` library from 64-bit Python:

.. code-block:: pycon

   >>> from msl.examples.loadlib import Labview64
   >>> labview = Labview64()  # doctest: +SKIP
   >>> labview  # doctest: +SKIP
   <Labview64 lib=labview_lib32.dll address=127.0.0.1:49952>
   >>> labview.lib32_path  # doctest: +SKIP
   'D:\\msl\\examples\\loadlib\\labview_lib32.dll'

Calculate the mean and the *sample* variance and standard deviation of some data, see
:meth:`~msl.examples.loadlib.labview64.Labview64.stdev`:

.. code-block:: pycon

   >>> data = [1, 2, 3, 4, 5, 6, 7, 8, 9]
   >>> labview.stdev(data)  # doctest: +SKIP
   (5.0, 7.5, 2.7386127875258306)

Calculate the mean and the *population* variance and standard deviation of data:

.. code-block:: pycon

   >>> labview.stdev(data, 1)  # doctest: +SKIP
   (5.0, 6.666666666666667, 2.581988897471611)

Shutdown the server, see :meth:`~msl.loadlib.client64.Client64.shutdown_server32`:

.. code-block:: pycon

   >>> labview.shutdown_server32()  # doctest: +SKIP

.. note::
   When using a subclass of :class:`~msl.loadlib.client64.Client64` in a script, the
   :meth:`~msl.loadlib.client64.Client64.shutdown_server32` method gets called automatically
   when the instance of the subclass is about to be destroyed and therefore you do not have to call
   the :meth:`~msl.loadlib.client64.Client64.shutdown_server32` method to shutdown the server.
