.. _install:

Install MSL-LoadLib
===================

To install **MSL-LoadLib** run::

   pip install msl-loadlib

Alternatively, using the `MSL Package Manager`_ run::

   msl install loadlib

.. _MSL Package Manager: http://msl-package-manager.readthedocs.io/en/latest/?badge=latest

Compatibility
-------------

* Tested with Python versions 2.7, 3.3+.
* The :mod:`~msl.loadlib.start_server32` module has been built in to a `frozen <http://www.pyinstaller.org/>`_
  Python application for Windows and Linux and works with the Python versions listed above. The 32-bit server
  is running on Python 3.6 and therefore all modules that run on the server must use Python 3 syntax.
* The 32-bit server can be `frozen <http://www.pyinstaller.org/>`_ for other operating systems by running
  the :mod:`~msl.loadlib.freeze_server32` module in the operating system of your choice using a 32-bit
  Python interpreter of your choice.

.. _prerequisites:

Prerequisites
-------------

Windows
+++++++
64-bit Windows already comes with `WoW64 <https://en.wikipedia.org/wiki/WoW64>`_ to run 32-bit software and
includes the .NET Framework and therefore no prerequisites are required to load ``__cdecl``, ``__stdcall``
or ``.NET`` libraries.

If you need to load a Java library, a ``.jar`` or ``.class`` file, then you must install a
`Java Runtime Environment`_ and ensure that the ``java`` executable is available on your ``PATH``.
For example, the following should return the version of Java that is installed::

   C:\>java -version
   java version "1.8.0_161"
   Java(TM) SE Runtime Environment (build 1.8.0_161-b12)
   Java HotSpot(TM) 64-Bit Server VM (build 25.161-b12, mixed mode)

When loading a shared library it is vital that all dependency's of the library are also available on your
computer and that the shared library knows where to locate the dependency. A helpful utility to use to
determine the dependencies of a shared library is `Dependency Walker <http://www.dependencywalker.com/>`_.
For finding the dependencies of a .NET library the
`DependencyWalker for .NET <https://github.com/isindicic/DependencyWalker.Net>`_ is also useful.

Linux
++++++
Before using **MSL-LoadLib** on Linux the following packages are required.

Install the packages that are needed to load C/C++ and FORTRAN libraries::

   sudo apt-get update
   sudo apt-get install software-properties-common build-essential g++ gcc-multilib g++-multilib gfortran libgfortran3:i386 zlib1g:i386

If you need to load a .NET Framework then you must install Mono_ (v4.8.0 is specified below)::

   sudo apt-get install libglib2.0-dev clang
   sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF
   echo "deb http://download.mono-project.com/repo/ubuntu wheezy/snapshots/4.8.0 main" | sudo tee /etc/apt/sources.list.d/mono-official.list
   sudo apt-get update
   sudo apt-get install mono-devel mono-complete -y

Also, `Python for .NET`_ is not automatically installed when **MSL-LoadLib** is installed on Linux.
You will have to run::

   pip install pythonnet

Installing `Python for .NET`_ v2.3.0 with Mono_ v4.8.0 installed on Ubuntu 16.04.3 has been confirmed to work::

   joe@msl:~$ lsb_release -a
   No LSB modules are available.
   Distributor ID: Ubuntu
   Description:    Ubuntu 16.04.3 LTS
   Release:        16.04
   Codename:       xenial

   joe@msl:~$ mono -V
   Mono JIT compiler version 4.8.0 (Stable 4.8.0.524/9d74414 Wed Apr  5 17:57:04 UTC 2017)
   Copyright (C) 2002-2014 Novell, Inc, Xamarin Inc and Contributors. www.mono-project.com
       TLS:           __thread
       SIGSEGV:       altstack
       Notifications: epoll
       Architecture:  amd64
       Disabled:      none
       Misc:          softdebug
       LLVM:          supported, not enabled.
       GC:            sgen

If you run in to problems installing `Python for .NET`_ then the best place to find help is on the
`issues <https://github.com/pythonnet/pythonnet/issues>`_ page of `Python for .NET`_\'s repository.

If you need to load a Java library, a ``.jar`` or ``.class`` file, then you must install a
`Java Runtime Environment`_::

   sudo apt-get install default-jre

and ensure that the ``java`` executable is available on your ``PATH``. For example, the following
should return the version of Java that is installed::

   joe@msl:~$ java -version
   openjdk version "1.8.0_131"
   OpenJDK Runtime Environment (build 1.8.0_131-8u131-b11-2ubuntu1.16.04.3-b11)
   OpenJDK 64-Bit Server VM (build 25.131-b11, mixed mode)

OSX
+++
The 32-bit server has not been created for OSX nor have the C++/FORTRAN example libraries been
compiled in OSX.

.. _Mono: http://www.mono-project.com/
.. _Python for .NET: http://pythonnet.github.io/
.. _Java Runtime Environment: http://www.oracle.com/technetwork/java/javase/downloads/index.html
