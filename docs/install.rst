Install MSL-LoadLib
===================

To install **MSL-LoadLib** run::

   $ pip install git+https://github.com/mslnz/msl-loadlib

*Note: To run the above command, pip requires that* git_ *is installed and for the* **git** *command to be available on your path.*

Compatibility
-------------

* Tested with Python versions 2.7, 3.3 - 3.6.
* The :mod:`~msl.loadlib.start_server32` module has only been built into a `frozen <http://www.pyinstaller.org/>`_
  Python application for Windows and works with the Python versions listed above. It can be
  `frozen <http://www.pyinstaller.org/>`_ for other operating systems and Python versions by running the
  :mod:`~msl.loadlib.freeze_server32` module in the operating system and Python version of your choice.
