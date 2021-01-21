.. _direct:

Load a library
==============
If you are loading a 64-bit library in 64-bit Python (or a 32-bit library in
32-bit Python) then you can directly load the library using
:class:`~msl.loadlib.load_library.LoadLibrary`.

.. important::
   If you want to load a 32-bit library in 64-bit Python then
   `inter-process communication`_ is used to communicate with the 32-bit library.
   See :ref:`inter-process-communication` for more details.

All of the shared libraries in the following examples are included with the
MSL-LoadLib package. The :ref:`C++ <cpp-lib>` and :ref:`FORTRAN <fortran-lib>`
libraries have been compiled in 32- and 64-bit Windows and Linux and in 64-bit
macOS. The :ref:`.NET <dotnet-lib>` library was complied in 32- and 64-bit using
Microsoft Visual Studio 2017. The kernel32_ library is a 32-bit library and it
is only valid on Windows (since it uses the ``__stdcall`` calling convention).
The :ref:`LabVIEW <labview-lib>` library was built using 32- and 64-bit LabVIEW
on Windows. The :ref:`Java <java-lib>` libraries are platform and bitness
independent since they run in the JVM_.

.. tip::
   If the file extension is not specified then a default extension,
   ``.dll`` (Windows), ``.so`` (Linux) or ``.dylib`` (macOS) is used.

.. toctree::

   C++ <direct_cpp>
   FORTRAN <direct_fortran>
   Microsoft .NET Framework <direct_dotnet>
   Java <direct_java>
   COM <direct_com>
   Windows __stdcall <direct_stdcall>
   LabVIEW <direct_labview>

.. _inter-process communication: https://en.wikipedia.org/wiki/Inter-process_communication
.. _kernel32: https://www.geoffchappell.com/studies/windows/win32/kernel32/api/
.. _JVM: https://en.wikipedia.org/wiki/Java_virtual_machine
