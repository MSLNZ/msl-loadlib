.. _loadlib-install:

Install MSL-LoadLib
===================

To install **MSL-LoadLib** run:

.. code-block:: console

   pip install msl-loadlib

Alternatively, using the `MSL Package Manager`_ run:

.. code-block:: console

   msl install loadlib

Dependencies
------------
* Python 2.7, 3.5+

Optional dependencies:

  * `Python for .NET`_
  * Py4J_
  * comtypes_

You can install MSL-LoadLib and `Python for .NET`_ using:

.. code-block:: console

   pip install msl-loadlib[clr]

MSL-LoadLib and Py4J_:

.. code-block:: console

   pip install msl-loadlib[java]

MSL-LoadLib and comtypes_:

.. code-block:: console

   pip install msl-loadlib[com]

or MSL-LoadLib and all optional dependencies:

.. code-block:: console

   pip install msl-loadlib[all]


Compatibility
-------------
* The :mod:`~msl.loadlib.start_server32` module has been built in to a `frozen <https://www.pyinstaller.org/>`_
  Python application for Windows and Linux and works with the Python versions listed above. The 32-bit server
  is running on Python 3.7 and therefore all modules that run on the server must use Python 3 syntax.
* You can create a new 32-bit server. See :ref:`refreeze` for more details.

.. _loadlib-prerequisites:

Prerequisites
-------------

Windows
+++++++
64-bit Windows already comes with `WoW64 <https://en.wikipedia.org/wiki/WoW64>`_ to run 32-bit software and
therefore no prerequisites are required to load ``__cdecl`` or ``__stdcall`` libraries. However,
the library might have its own dependencies, such as a particular Visual C++ Redistributable, that may need
to be installed.

If you need to load a Microsoft .NET library then you must install `Python for .NET`_

.. code-block:: console

   pip install pythonnet

If you need to load a Java library, a ``.jar`` or ``.class`` file, then you must install Py4J_

.. code-block:: console

   pip install py4j

and a `Java Runtime Environment`_ and ensure that the ``java`` executable is available on your ``PATH``.
For example, the following should return the version of Java that is installed

.. code-block:: console

   C:\>java --version
   java 11.0.2 2019-01-15 LTS
   Java(TM) SE Runtime Environment 18.9 (build 11.0.2+9-LTS)
   Java HotSpot(TM) 64-Bit Server VM 18.9 (build 11.0.2+9-LTS, mixed mode)

If you need to load a `Component Object Model`_ library then you must install comtypes_

.. code-block:: console

   pip install comtypes

When loading a shared library it is vital that all dependencies of the library are also available on your
computer and that the directory of the dependency is also available on your ``PATH``. A helpful utility to use to
determine the dependencies of a shared library is `Dependency Walker <http://www.dependencywalker.com/>`_.
For finding the dependencies of a .NET library the
`Dependency Walker for .NET <https://github.com/isindicic/DependencyWalker.Net>`_ is also useful.

Linux
++++++
Before using **MSL-LoadLib** on Linux the following packages are required.

Install the packages that are needed to run a 32-bit binary on 64-bit Linux and to load C/C++ and FORTRAN libraries

.. code-block:: console

   sudo apt update
   sudo apt install software-properties-common build-essential g++ gcc-multilib g++-multilib gfortran libgfortran3:i386 zlib1g:i386

The following ensures that the ``netstat`` command is available

.. code-block:: console

   sudo apt install net-tools

If you need to load a Microsoft .NET library then you must install Mono_
*(NOTE: v5.20 was used when embedding pythonnet in the 32-bit server for Linux)*

.. code-block:: console

   sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF
   sudo apt install apt-transport-https ca-certificates
   echo "deb https://download.mono-project.com/repo/ubuntu stable-bionic/snapshots/5.20 main" | sudo tee /etc/apt/sources.list.d/mono-official-stable.list
   sudo apt update
   sudo apt install mono-complete

the prerequisites to build `Python for .NET`_ from source

.. code-block:: console

   sudo apt install libglib2.0-dev clang python3-pip python3-dev
   pip3 install pycparser

and `Python for .NET`_

.. code-block:: console

   pip3 install pythonnet

Installing Mono_ v5.20.1.34 and `Python for .NET`_ v2.4.0 on Ubuntu 18.04.2 has been confirmed to work

.. code-block:: console

   joe@msl:~$ lsb_release -a
   No LSB modules are available.
   Distributor ID: Ubuntu
   Description:    Ubuntu 18.04.2 LTS
   Release:        18.04
   Codename:       bionic

   joe@msl:~$ mono -V
   Mono JIT compiler version 5.20.1.34 (tarball Tue Jul 16 22:52:32 UTC 2019)
   Copyright (C) 2002-2014 Novell, Inc, Xamarin Inc and Contributors. www.mono-project.com
       TLS:           __thread
       SIGSEGV:       altstack
       Notifications: epoll
       Architecture:  amd64
       Disabled:      none
       Misc:          softdebug
       Interpreter:   yes
       LLVM:          yes(600)
       Suspend:       hybrid
       GC:            sgen (concurrent by default)

If you run in to problems installing `Python for .NET`_ then the best place to find help is on the
`issues <https://github.com/pythonnet/pythonnet/issues>`_ page of `Python for .NET`_\'s repository.

If you need to load a Java library, a ``.jar`` or ``.class`` file, then you must install Py4J_

.. code-block:: console

   pip3 install py4j

and a `Java Runtime Environment`_

.. code-block:: console

   sudo apt install default-jre

and ensure that the ``java`` executable is available on your ``PATH``. For example, the following
should return the version of Java that is installed

.. code-block:: console

   joe@msl:~$ java --version
   openjdk 11.0.2 2019-01-15
   OpenJDK Runtime Environment (build 11.0.2+9-Ubuntu-3ubuntu118.04.3)
   OpenJDK 64-Bit Server VM (build 11.0.2+9-Ubuntu-3ubuntu118.04.3, mixed mode, sharing)

OSX
+++
The 32-bit server has not been created for OSX nor have the example libraries been compiled in OSX.

.. _MSL Package Manager: https://msl-package-manager.readthedocs.io/en/latest/
.. _Mono: https://www.mono-project.com/download/stable/#download-lin
.. _Python for .NET: https://pythonnet.github.io/
.. _Java Runtime Environment: https://www.oracle.com/technetwork/java/javase/downloads/index.html
.. _Py4J: https://www.py4j.org/
.. _comtypes: https://pythonhosted.org/comtypes/#
.. _Component Object Model: https://en.wikipedia.org/wiki/Component_Object_Model
