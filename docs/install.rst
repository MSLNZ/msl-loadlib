.. _loadlib-install:

Install
=======

To install msl-loadlib run

.. code-block:: console

   pip install msl-loadlib

Alternatively, using the `MSL Package Manager`_ run

.. code-block:: console

   msl install loadlib

Dependencies
------------
* Python 3.8+

Optional dependencies:

  * `Python for .NET`_
  * Py4J_
  * comtypes_

You can install msl-loadlib and `Python for .NET`_ using,

.. code-block:: console

   pip install msl-loadlib[clr]

msl-loadlib and Py4J_,

.. code-block:: console

   pip install msl-loadlib[java]

msl-loadlib and comtypes_,

.. code-block:: console

   pip install msl-loadlib[com]

or msl-loadlib and all optional dependencies

.. code-block:: console

   pip install msl-loadlib[all]

Compatibility
-------------
* The 32-bit server has been built into a frozen_ Python executable for Windows and Linux.
* You may create a new 32-bit server. See :ref:`refreeze` for more details.

.. _loadlib-prerequisites:

Prerequisites
-------------

Windows
+++++++
64-bit Windows already comes with WoW64_ to run 32-bit software and therefore
no prerequisites are required to load 32-bit libraries. However, the library
might have its own dependencies, such as a particular Visual C++ Redistributable,
that may need to be installed.

If you need to load a Microsoft .NET library, you must install `Python for .NET`_

.. code-block:: console

   pip install pythonnet

If you need to load a Java library (i.e., a ``.jar`` or ``.class`` file),
you must install Py4J_,

.. code-block:: console

   pip install py4j

a `Java Runtime Environment`_, and, ensure that the ``java`` executable is
available on the PATH_ variable. For example, the following should return the
version of Java that is installed

.. code-block:: console

   C:\Users\username>java --version
   java 22 2024-03-19
   Java(TM) SE Runtime Environment (build 22+36-2370)
   Java HotSpot(TM) 64-Bit Server VM (build 22+36-2370, mixed mode, sharing)

If you need to load a `Component Object Model`_ (or ActiveX_) library, you must install comtypes_

.. code-block:: console

   pip install comtypes

.. tip::

   When loading a shared library it is vital that all dependencies of the
   library are also on the computer and that the directory that the dependencies
   are located in is available on the PATH_ variable (and possibly you may need
   to add a directory with :func:`os.add_dll_directory`). A helpful utility to
   determine the dependencies of a shared library on Windows is Dependencies_
   (which is a modern `Dependency Walker`_). Microsoft also provides the
   DUMPBIN_ tool. For finding the dependencies of a .NET library the
   `Dependency Walker for .NET`_ may also be helpful.

Linux
+++++
Before using msl-loadlib on Debian-based Linux distributions, the following
packages are required. For other distributions, use the appropriate system
package manager (e.g., *yum*) and the equivalent command.

.. attention::

   The following packages are required to run the examples that are included
   with msl-loadlib when it is installed. The dependencies for the C/C++ or
   FORTRAN library that you want to load may be different.

Install the packages that are required to load 32-bit and 64-bit C/C++
and FORTRAN libraries

.. code-block:: console

   sudo dpkg --add-architecture i386
   sudo apt update
   sudo apt install g++ gfortran libgfortran5 zlib1g:i386 libstdc++6:i386 libgfortran5:i386

The following ensures that the ss_ command is available

.. code-block:: console

   sudo apt install iproute2

If you need to load a Microsoft .NET library then you must install Mono_
(see `here <Mono_>`_ for instructions) and `Python for .NET`_

.. code-block:: console

   pip3 install pythonnet

.. important::

   As of version 0.10.0 of msl-loadlib, pythonnet is no longer installed
   on the 32-bit server for Linux. Mono_ can load both 32-bit and 64-bit
   libraries on 64-bit Linux and therefore a 32-bit .NET library can be
   loaded directly via :class:`~msl.loadlib.load_library.LoadLibrary` on
   64-bit Linux.

If you need to load a Java library (i.e., a ``.jar`` or ``.class`` file),
you must install Py4J_,

.. code-block:: console

   pip3 install py4j

and a `Java Runtime Environment`_

.. code-block:: console

   sudo apt install default-jre

.. tip::

   When loading a shared library it is vital that all dependencies of the
   library are also on the computer and that the directory that the dependency
   is located in is available on the PATH_ variable. A helpful utility to
   determine the dependencies of a shared library on Unix is ldd_.

macOS
+++++
The 32-bit server has not been created for macOS; however, the
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

If you need to load a Microsoft .NET library, you must install Mono_,

.. code-block:: console

   brew install mono

and `Python for .NET`_

.. code-block:: console

   pip3 install pythonnet

If you need to load a Java library (i.e., a ``.jar`` or ``.class`` file),
you must install Py4J_,

.. code-block:: console

   pip3 install py4j

and a `Java Runtime Environment`_

.. code-block:: console

   brew cask install java

.. _MSL Package Manager: https://msl-package-manager.readthedocs.io/en/stable/
.. _Python for .NET: https://pythonnet.github.io/
.. _Py4J: https://www.py4j.org/
.. _comtypes: https://pythonhosted.org/comtypes/#
.. _frozen: https://pyinstaller.readthedocs.io/en/stable/
.. _WoW64: https://en.wikipedia.org/wiki/WoW64
.. _Java Runtime Environment: https://www.oracle.com/java/technologies/downloads/
.. _Component Object Model: https://en.wikipedia.org/wiki/Component_Object_Model
.. _Dependencies: https://github.com/lucasg/Dependencies
.. _Dependency Walker: https://www.dependencywalker.com/
.. _Dependency Walker for .NET: https://github.com/isindicic/DependencyWalker.Net
.. _Mono: https://www.mono-project.com/download/stable/
.. _issues: https://github.com/pythonnet/pythonnet/issues
.. _Homebrew: https://brew.sh/
.. _ss: https://man7.org/linux/man-pages/man8/ss.8.html
.. _ldd: https://man7.org/linux/man-pages/man1/ldd.1.html
.. _PATH: https://en.wikipedia.org/wiki/PATH_(variable)
.. _DUMPBIN: https://learn.microsoft.com/en-us/cpp/build/reference/dumpbin-reference?view=msvc-170
.. _ActiveX: https://en.wikipedia.org/wiki/ActiveX
