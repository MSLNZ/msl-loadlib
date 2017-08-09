Install MSL-LoadLib
===================

To install **MSL-LoadLib** run::

   pip install https://github.com/MSLNZ/msl-loadlib/archive/master.zip

Alternatively, using the `MSL Package Manager`_ run::

   msl install loadlib

.. _MSL Package Manager: http://msl-package-manager.readthedocs.io/en/latest/?badge=latest

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
Before installing **MSL-LoadLib** on Linux (Debian/Ubuntu) you should save the following script on your computer and run
it to install the prerequisites *(or execute each command individually if you prefer to not create the script)*.

This script installs 32-bit packages needed to load 32-bit C/C++ and FORTRAN libraries in 64-bit Debian/Ubuntu and it
installs `Mono <http://www.mono-project.com/>`_ for loading .NET Framework assemblies. For other Linux distributions
you will need to edit the commands appropriately::

   #!/bin/bash

   sudo apt-get update

   sudo apt-get -y install software-properties-common libglib2.0-dev clang build-essential g++ gcc-multilib g++-multilib gfortran libgfortran3:i386 zlib1g:i386

   sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF

   echo "deb http://download.mono-project.com/repo/debian wheezy main" | sudo tee /etc/apt/sources.list.d/mono-xamarin.list

   sudo apt-get update

   sudo DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confnew" install mono-devel mono-complete referenceassemblies-pcl ca-certificates-mono nunit-console

You should then be able to run::

   pip install https://github.com/MSLNZ/msl-loadlib/archive/master.zip

The above script was tested on a clean installation of Ubuntu 16.04.1 LTS (xenial).

64-bit Windows already comes with `WoW64 <https://en.wikipedia.org/wiki/WoW64>`_ to run 32-bit software and
includes the .NET Framework and therefore no prerequisites are required.
