"""
A wrapper around a 32-bit LabVIEW library, :ref:`labview_lib32 <labview-lib>`.

.. attention::
   This example requires that the appropriate
   `LabVIEW Run-Time Engine <https://www.ni.com/download/labview-run-time-engine-2015/5507/en/>`_ is installed
   and that the operating system is Windows.

Example of a server that loads a 32-bit shared library, :ref:`labview_lib <labview-lib>`,
in a 32-bit Python interpreter to host the library. The corresponding :mod:`~.labview64` module
can be executed by a 64-bit Python interpreter and the :class:`~.labview64.Labview64` class can send
a request to the :class:`~.labview32.Labview32` class which calls the 32-bit library to execute the
request and then return the response from the library.
"""
import os
from ctypes import c_double, byref

from msl.loadlib import Server32


class Labview32(Server32):

    def __init__(self, host, port, **kwargs):
        """A wrapper around the 32-bit LabVIEW library, :ref:`labview_lib32 <labview-lib>`.

        Parameters
        ----------
        host : :class:`str`
            The IP address of the server.
        port : :class:`int`
            The port to open on the server.

        Note
        ----
        Any class that is a subclass of :class:`~msl.loadlib.server32.Server32` **MUST**
        provide two arguments in its constructor: `host` and `port` (in that order)
        and `**kwargs`. Otherwise the ``server32`` executable, see
        :class:`~msl.loadlib.start_server32`, cannot create an instance of the
        :class:`~msl.loadlib.server32.Server32` subclass.
        """
        super(Labview32, self).__init__(os.path.join(os.path.dirname(__file__), 'labview_lib32.dll'),
                                        'cdll', host, port)

    def stdev(self, x, weighting=0):
        """Calculates the mean, variance and standard deviation of the values in the input `x`.

        See the corresponding 64-bit :meth:`~.labview64.Labview64.stdev` method.

        Parameters
        ----------
        x : :class:`list` of :class:`float`
            The data to calculate the mean, variance and standard deviation of.
        weighting : :class:`int`, optional
            Whether to calculate the **sample**, ``weighting = 0``, or the **population**,
            ``weighting = 1``, standard deviation and variance.

        Returns
        -------
        :class:`float`
            The mean.
        :class:`float`
            The variance.
        :class:`float`
            The standard deviation.
        """
        data = (c_double * len(x))(*x)
        mean, variance, std = c_double(), c_double(), c_double()
        self.lib.stdev(data, len(x), weighting, byref(mean), byref(variance), byref(std))
        return mean.value, variance.value, std.value
