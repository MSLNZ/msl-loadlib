"""
Communicates with :ref:`labview_lib32 <labview-lib>` via the :class:`~.labview32.Labview32` class.

.. attention::
   This example requires that the appropriate
   `LabVIEW Run-Time Engine <https://www.ni.com/download/labview-run-time-engine-2015/5507/en/>`_ is installed
   and that the operating system is Windows.

Example of a module that can be executed within a 64-bit Python interpreter which can
communicate with a 32-bit library, :ref:`labview_lib32 <labview-lib>`, that is hosted
by a 32-bit Python server, :mod:`.labview32`. A 64-bit process cannot load a
32-bit library and therefore `inter-process communication <ipc_>`_ is used to
interact with a 32-bit library from a 64-bit process.

:class:`~.labview64.Labview64` is the 64-bit client and :class:`~.labview32.Labview32`
is the 32-bit server for `inter-process communication <ipc_>`_.

.. _ipc: https://en.wikipedia.org/wiki/Inter-process_communication
"""
from __future__ import annotations

import os
from typing import Sequence

from msl.loadlib import Client64


class Labview64(Client64):

    def __init__(self) -> None:
        """Communicates with a 32-bit LabVIEW library, :ref:`labview_lib32 <labview-lib>`.

        This class demonstrates how to communicate with a 32-bit LabVIEW library if an
        instance of this class is created within a 64-bit Python interpreter.
        """
        # specify the name of the corresponding 32-bit server module, labview32, which hosts
        # the 32-bit LabVIEW library -- labview_lib32.dll
        super().__init__(module32='labview32', append_sys_path=os.path.dirname(__file__))

    def stdev(self, x: Sequence[float], weighting: int = 0) -> tuple[float, float, float]:
        """Calculates the mean, variance and standard deviation of the values in the input `x`.

        See the corresponding 32-bit :meth:`~.labview32.Labview32.stdev` method.

        :param x: The data to calculate the mean, variance and standard deviation of.
        :param weighting: Whether to calculate the sample (`weighting` = 0) or the
            population (`weighting` = 1) standard deviation and variance.
        :return: The mean, variance and standard deviation.
        """
        if weighting == 0 or weighting == 1:
            return self.request32('stdev', x, weighting)
        raise ValueError(f'The weighting must be either 0 or 1, got {weighting}')
