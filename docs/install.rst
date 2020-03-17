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
   java 13.0.2 2020-01-14
   Java(TM) SE Runtime Environment (build 13.0.2+8)
   Java HotSpot(TM) 64-Bit Server VM (build 13.0.2+8, mixed mode, sharing)

If you need to load a `Component Object Model`_ library then you must install comtypes_

.. code-block:: console

   pip install comtypes

When loading a shared library it is vital that all dependencies of the library are also available on your
computer and that the directory of the dependency is also available on your ``PATH``. A helpful utility to use
to determine the dependencies of a shared library is Dependencies_ (which is a modern `Dependency Walker`_).
For finding the dependencies of a .NET library the `Dependency Walker for .NET`_ is also useful.

Linux
++++++
Before using **MSL-LoadLib** on Linux the following packages are required.

Install the packages that are needed to run a 32-bit binary on 64-bit Linux and to load C/C++ and FORTRAN libraries

.. code-block:: console

   sudo apt update
   sudo apt install software-properties-common build-essential g++ gcc-multilib g++-multilib gfortran libgfortran3 libgfortran3:i386 lib32gfortran3 libx32gfortran3 zlib1g:i386

The following ensures that the ``netstat`` command is available

.. code-block:: console

   sudo apt install net-tools

If you need to load a Microsoft .NET library then you must install Mono_. The following illustrates
how to install Mono_ v5.20 on Ubuntu 18.04. *(NOTE: v5.20 was used when embedding pythonnet in*
*the 32-bit server for Linux)*

.. code-block:: console

   sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF
   sudo apt install apt-transport-https ca-certificates
   echo "deb https://download.mono-project.com/repo/ubuntu stable-bionic/snapshots/5.20 main" | sudo tee /etc/apt/sources.list.d/mono-official-stable.list
   sudo apt update
   sudo apt install mono-complete

The prerequisites to build `Python for .NET`_ from source must also be installed

.. code-block:: console

   sudo apt install libglib2.0-dev clang python3-pip python3-dev
   pip3 install pycparser

and then install `Python for .NET`_

.. code-block:: console

   pip3 install pythonnet

Installing Mono_ v5.20.1.34 and `Python for .NET`_ v2.4.0 on Ubuntu 18.04 has been confirmed to work.
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

   $ java --version
   openjdk 11.0.6 2020-01-14
   OpenJDK Runtime Environment (build 11.0.6+10-post-Ubuntu-1ubuntu118.04.1)
   OpenJDK 64-Bit Server VM (build 11.0.6+10-post-Ubuntu-1ubuntu118.04.1, mixed mode, sharing)

macOS
+++++
The 32-bit server has not been created for macOS, however, the :class:`~msl.loadlib.load_library.LoadLibrary`
class can be used to load a library that uses the ``__cdecl`` calling convention that is the same
bitness as the Python interpreter, a .NET library or a Java library.

The following assumes that you are using Homebrew_ as your package manager.

It is recommended to update Homebrew_ before installing packages

.. code-block:: console

   brew update

To load a C/C++ or FORTRAN library install gcc (which includes gfortran)

.. code-block:: console

   brew install gcc

If you need to load a Microsoft .NET library then you must install Mono_ and the prerequisites
to build `Python for .NET`_ from source

.. code-block:: console

   brew install pkg-config glib mono
   pip3 install pycparser

and `Python for .NET`_

.. code-block:: console

   pip3 install pythonnet

If you run in to problems installing `Python for .NET`_ then the best place to find help is on the
`issues <https://github.com/pythonnet/pythonnet/issues>`_ page of `Python for .NET`_\'s repository.

If you need to load a Java library, a ``.jar`` or ``.class`` file, then you must install Py4J_

.. code-block:: console

   pip3 install py4j

and a `Java Runtime Environment`_

.. code-block:: console

   brew cask install java

.. _MSL Package Manager: https://msl-package-manager.readthedocs.io/en/latest/
.. _Mono: https://www.mono-project.com/download/stable/
.. _Python for .NET: https://pythonnet.github.io/
.. _Java Runtime Environment: https://www.oracle.com/technetwork/java/javase/downloads/index.html
.. _Py4J: https://www.py4j.org/
.. _comtypes: https://pythonhosted.org/comtypes/#
.. _Component Object Model: https://en.wikipedia.org/wiki/Component_Object_Model
.. _Dependencies: https://github.com/lucasg/Dependencies
.. _Dependency Walker: http://www.dependencywalker.com/
.. _Dependency Walker for .NET: https://github.com/isindicic/DependencyWalker.Net
.. _Homebrew: https://brew.sh/
