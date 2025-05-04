"""Wrapper around a 32-bit LabVIEW library.

Example of a server that loads a 32-bit LabVIEW library, [labview_lib][labview-lib],
in a 32-bit Python interpreter to host the library. The corresponding [Labview64][] class
is created in a 64-bit Python interpreter and the [Labview64][] class sends requests
to the [Labview32][] class which calls the 32-bit library to execute the request and
then returns the response from the library.

!!! attention
    This example requires that a 32-bit
    [LabVIEW Run-Time Engine](https://www.ni.com/en/support/downloads/software-products/download.labview-runtime.html){:target="_blank"}
    &ge; 2017 is installed and that the operating system is Windows.
"""

from __future__ import annotations

from ctypes import byref, c_double
from pathlib import Path
from typing import TYPE_CHECKING

from msl.loadlib import Server32

if TYPE_CHECKING:
    from collections.abc import Sequence


class Labview32(Server32):
    """Wrapper around the 32-bit LabVIEW library, [labview_lib][labview-lib]."""

    def __init__(self, host: str, port: int) -> None:
        """Wrapper around the 32-bit LabVIEW library, [labview_lib][labview-lib].

        Args:
            host: The IP address (or hostname) to use for the server.
            port: The port to open for the server.
        """
        path = Path(__file__).parent / "labview_lib32.dll"
        super().__init__(path, "cdll", host, port)

    def stdev(self, x: Sequence[float], weighting: int = 0) -> tuple[float, float, float]:
        """Calculates the mean, variance and standard deviation of the values in the input `x`.

        See the corresponding [Labview64.stdev][msl.examples.loadlib.labview64.Labview64.stdev] method.

        Args:
            x: The data to calculate the mean, variance and standard deviation of.
            weighting: Whether to calculate the sample (`weighting = 0`) or the
                population (`weighting = 1`) standard deviation and variance.

        Returns:
            The mean, variance and standard deviation.
        """
        data = (c_double * len(x))(*x)
        mean, variance, std = c_double(), c_double(), c_double()
        self.lib.stdev(data, len(x), weighting, byref(mean), byref(variance), byref(std))
        return mean.value, variance.value, std.value
