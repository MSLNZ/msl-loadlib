"""Communicates with the [labview_lib][labview-lib] library via the [Labview32][] class that is running on a server.

!!! attention
    This example requires that the appropriate
    [LabVIEW Run-Time Engine](https://www.ni.com/en/support/downloads/software-products/download.labview-runtime.html){:target="_blank"}
    is installed and that the operating system is Windows.
"""

from __future__ import annotations

import os
from typing import Sequence

from msl.loadlib import Client64


class Labview64(Client64):
    """Communicates with a 32-bit LabVIEW library, [labview_lib][labview-lib]."""

    def __init__(self) -> None:
        """Communicates with a 32-bit LabVIEW library, [labview_lib][labview-lib].

        This class demonstrates how to communicate with a 32-bit LabVIEW library if an
        instance of this class is created within a 64-bit Python interpreter.
        """
        # specify the name of the corresponding 32-bit server module, labview32, which hosts
        # the 32-bit LabVIEW library -- labview_lib32.dll
        super().__init__(module32="labview32", append_sys_path=os.path.dirname(__file__))

    def stdev(self, x: Sequence[float], weighting: int = 0) -> tuple[float, float, float]:
        """Calculates the mean, variance and standard deviation of the values in the input `x`.

        See the corresponding [Labview32.stdev][msl.examples.loadlib.labview32.Labview32.stdev] method.

        Args:
            x: The data to calculate the mean, variance and standard deviation of.
            weighting: Whether to calculate the sample (`weighting = 0`) or the
                population (`weighting = 1`) standard deviation and variance.

        Returns:
            The mean, variance and standard deviation.
        """
        if weighting not in {0, 1}:
            msg = f"The weighting must be either 0 or 1, got {weighting}"
            raise ValueError(msg)

        return self.request32("stdev", x, weighting)
