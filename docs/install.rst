Install MSL-LoadLib
===================

To install **MSL-LoadLib** run::

   pip install https://github.com/MSLNZ/msl-loadlib/archive/master.zip

Compatibility
-------------

* Tested with Python versions 2.7, 3.3 - 3.6.
* The :mod:`~msl.loadlib.start_server32` module has been built into a `frozen <http://www.pyinstaller.org/>`_
  Python application for Windows and Linux and works with the Python versions listed above. It can be
  `frozen <http://www.pyinstaller.org/>`_ for other operating systems running the :mod:`~msl.loadlib.freeze_server32`
  module in the operating system of your choice.

.. _prerequisites:

Prerequisites
-------------
The following commands should be executed so that you have the prerequisites install to be able to run the
examples on Linux.

To run the :ref:`C++ <tutorial_cpp>` and :ref:`FORTRAN <tutorial_fortran>` examples::

   sudo apt-get install build-essential g++ gcc-multilib g++-multilib gfortran libgfortran3:i386 zlib1g:i386

To run the .NET example::

   sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF
   echo "deb http://download.mono-project.com/repo/debian wheezy main" | sudo tee /etc/apt/sources.list.d/mono-xamarin.list
   sudo apt-get update
   sudo apt-get install mono-complete

Windows already comes with `WoW64 <https://en.wikipedia.org/wiki/WoW64>`_ to run 32-bit software on 64-bit
Windows and the .NET Framework.
