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

from __future__ import annotations

import os
from ctypes import byref
from ctypes import c_double
from typing import Sequence

from msl.loadlib import Server32


class Labview32(Server32):
    def __init__(self, host: str, port: int, **kwargs: str) -> None:
        """A wrapper around the 32-bit LabVIEW library, :ref:`labview_lib32 <labview-lib>`.

        :param host: The IP address (or hostname) to use for the server.
        :param port: The port to open for the server.
        :param kwargs: Optional keyword arguments. The keys and values are of type :class:`str`.
        """
        path = os.path.join(os.path.dirname(__file__), "labview_lib32.dll")
        super().__init__(path, "cdll", host, port)

    def stdev(self, x: Sequence[float], weighting: int = 0) -> tuple[float, float, float]:
        """Calculates the mean, variance and standard deviation of the values in the input `x`.

        See the corresponding 64-bit :meth:`~.labview64.Labview64.stdev` method.

        :param x: The data to calculate the mean, variance and standard deviation of.
        :param weighting: Whether to calculate the sample (`weighting` = 0) or the
            population (`weighting` = 1) standard deviation and variance.
        :return: The mean, variance and standard deviation.
        """
        data = (c_double * len(x))(*x)
        mean, variance, std = c_double(), c_double(), c_double()
        self.lib.stdev(data, len(x), weighting, byref(mean), byref(variance), byref(std))
        return mean.value, variance.value, std.value
