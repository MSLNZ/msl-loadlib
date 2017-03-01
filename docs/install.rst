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
  module in the operating system of your choice using a 32-bit Python interpreter.

.. _prerequisites:

Prerequisites
-------------
Before installing **MSL-LoadLib** on Linux you should create the following script and run it to install
the prerequisites::

   #!/bin/bash

   sudo apt-get update

   sudo apt-get -y install software-properties-common libglib2.0-dev clang build-essential g++ gcc-multilib g++-multilib gfortran libgfortran3:i386 zlib1g:i386

   sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF

   echo "deb http://download.mono-project.com/repo/debian wheezy main" | sudo tee /etc/apt/sources.list.d/mono-xamarin.list

   sudo apt-get update

   sudo DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confnew" install mono-devel mono-complete referenceassemblies-pcl ca-certificates-mono nunit-console

The above script was tested on a clean installation of Ubuntu 16.04.1 LTS (xenial).

64-bit Windows already comes with `WoW64 <https://en.wikipedia.org/wiki/WoW64>`_ to run 32-bit software and
includes the .NET Framework and therefore no prerequisites are required.
