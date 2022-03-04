.. _loadlib-install:

Install
=======

To install MSL-LoadLib run:

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
* The :mod:`~msl.loadlib.start_server32` module has been built into a
  frozen_ Python application for Windows and Linux and works with the
  Python versions listed above. The 32-bit server is running with a
  Python 3 interpreter and therefore all modules that run on the server
  must use Python 3 syntax.
* You can create a new 32-bit server. See :ref:`refreeze` for more details.

.. _loadlib-prerequisites:

Prerequisites
-------------

Windows
+++++++
64-bit Windows already comes with WoW64_ to run 32-bit software and therefore
no prerequisites are required to load ``__cdecl`` or ``__stdcall`` libraries.
However, the library might have its own dependencies, such as a particular
Visual C++ Redistributable, that may need to be installed.

If you need to load a Microsoft .NET library then you must install
`Python for .NET`_

.. code-block:: console

   pip install pythonnet

If you need to load a Java library (i.e., a ``.jar`` or ``.class`` file)
then you must install Py4J_

.. code-block:: console

   pip install py4j

and a `Java Runtime Environment`_ and ensure that the ``java`` executable
is available on your ``PATH``. For example, the following should return the
version of Java that is installed

.. code-block:: console

   C:\>java --version
   java 15.0.1 2020-10-20
   Java(TM) SE Runtime Environment (build 15.0.1+9-18)
   Java HotSpot(TM) 64-Bit Server VM (build 15.0.1+9-18, mixed mode, sharing)

If you need to load a `Component Object Model`_ library then you must
install comtypes_

.. code-block:: console

   pip install comtypes

.. tip::

   When loading a shared library it is vital that all dependencies of the
   library are also on your computer and that the directory of the dependency
   is also available on your ``PATH``. A helpful utility to use to determine
   the dependencies of a shared library is Dependencies_ (which is a modern
   `Dependency Walker`_). For finding the dependencies of a .NET library the
   `Dependency Walker for .NET`_ can also be helpful.

Linux
++++++
Before using MSL-LoadLib on Linux the following packages are required.

Install the packages that are required to load C/C++ and FORTRAN libraries

.. note::
   The following packages are required to run the examples that are included
   with MSL-LoadLib when it is installed. The dependencies for the C/C++ or
   FORTRAN library that you want to load may be different.

.. code-block:: console

   sudo apt update
   sudo apt install g++ gfortran libgfortran5 zlib1g:i386 libstdc++6:i386 libgfortran5:i386

The following ensures that the ``netstat`` command is available

.. code-block:: console

   sudo apt install net-tools

If you need to load a Microsoft .NET library then you must install Mono_.
The following illustrates how to install Mono_ v5.20 on Ubuntu 18.04.

.. attention::

   Mono_ v5.20 was installed when embedding pythonnet in the 32-bit server
   and therefore that version must also be installed in 64-bit Linux
   if you want to load a 32-bit library. You can :ref:`refreeze <refreeze>`
   the 32-bit server using a different Mono_ version; however, be sure to
   follow the status of `issue 1210`_. You can install any version of Mono_
   that is supported by `Python for .NET`_ in 64-bit Linux if you do not
   need to load a 32-bit .NET library.

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

Installing Mono_ v5.20.1.34 and `Python for .NET`_ v2.4.0 on Ubuntu 18.04 has
been confirmed to work. If you run in to problems installing `Python for .NET`_
then the best place to find help is on the issues_ page of `Python for .NET`_\'s
repository.

If you need to load a Java library (i.e., a ``.jar`` or ``.class`` file)
then you must install Py4J_

.. code-block:: console

   pip3 install py4j

and a `Java Runtime Environment`_

.. code-block:: console

   sudo apt install default-jre

and ensure that the ``java`` executable is available on your ``PATH``.
For example, the following should return the version of Java that is installed

.. code-block:: console

   $ java --version
   openjdk 11.0.9.1 2020-11-04
   OpenJDK Runtime Environment (build 11.0.9.1+1-Ubuntu-0ubuntu1.18.04)
   OpenJDK 64-Bit Server VM (build 11.0.9.1+1-Ubuntu-0ubuntu1.18.04, mixed mode, sharing)

macOS
+++++
The 32-bit server has not been created for macOS, however, the
:class:`~msl.loadlib.load_library.LoadLibrary` class can be used to load a
library that uses the ``__cdecl`` calling convention that is the same
bitness as the Python interpreter, a .NET library or a Java library.

The following assumes that you are using Homebrew_ as your package manager.

It is recommended to update Homebrew_ before installing packages

.. code-block:: console

   brew update

To load a C/C++ or FORTRAN library install gcc (which includes gfortran)

.. code-block:: console

   brew install gcc

If you need to load a Microsoft .NET library then you must install Mono_
and the prerequisites to build `Python for .NET`_ from source

.. code-block:: console

   brew install pkg-config glib mono
   pip3 install pycparser

and `Python for .NET`_

.. code-block:: console

   pip3 install pythonnet

If you run in to problems installing `Python for .NET`_ then the best place
to find help is on the issues_ page of `Python for .NET`_\'s repository.

If you need to load a Java library (i.e., a ``.jar`` or ``.class`` file)
then you must install Py4J_

.. code-block:: console

   pip3 install py4j

and a `Java Runtime Environment`_

.. code-block:: console

   brew cask install java

.. _MSL Package Manager: https://msl-package-manager.readthedocs.io/en/stable/
.. _Python for .NET: https://pythonnet.github.io/
.. _Py4J: https://www.py4j.org/
.. _comtypes: https://pythonhosted.org/comtypes/#
.. _frozen: https://www.pyinstaller.org/
.. _WoW64: https://en.wikipedia.org/wiki/WoW64
.. _Java Runtime Environment: https://www.oracle.com/technetwork/java/javase/downloads/index.html
.. _Component Object Model: https://en.wikipedia.org/wiki/Component_Object_Model
.. _Dependencies: https://github.com/lucasg/Dependencies
.. _Dependency Walker: http://www.dependencywalker.com/
.. _Dependency Walker for .NET: https://github.com/isindicic/DependencyWalker.Net
.. _Mono: https://www.mono-project.com/download/stable/
.. _issues: https://github.com/pythonnet/pythonnet/issues
.. _issue 1210: https://github.com/pythonnet/pythonnet/issues/1210
.. _Homebrew: https://brew.sh/
