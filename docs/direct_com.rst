.. _direct_com:

COM
---
To load a `Component Object Model`_ (COM library) you pass in the library's
Program ID. To view the COM libraries that are available on your computer
you can run the :func:`~msl.loadlib.utils.get_com_info` function.

.. attention::

   This example is only valid on Windows.

Here we load the FileSystemObject_ and include the ``'com'`` argument
to indicate that it is a COM library

.. invisible-code-block: pycon

   >>> SKIP_IF_NOT_WINDOWS()

.. code-block:: pycon

   >>> from msl.loadlib import LoadLibrary
   >>> com = LoadLibrary('Scripting.FileSystemObject', 'com')
   >>> com
   <LoadLibrary libtype=POINTER(IFileSystem3) path=Scripting.FileSystemObject>

We can then use the library to create, edit and close a text file by using the
CreateTextFile_ method

.. code-block:: pycon

   >>> fp = com.lib.CreateTextFile('a_new_file.txt')
   >>> fp.Write('This is a test.')
   0
   >>> fp.Close()
   0

Verify that the file exists and that the text is correct

   >>> com.lib.FileExists('a_new_file.txt')
   True
   >>> file = com.lib.OpenTextFile('a_new_file.txt')
   >>> file.ReadAll()
   'This is a test.'
   >>> file.Close()
   0

.. invisible-code-block: pycon

   >>> import os
   >>> os.remove('a_new_file.txt')

.. _Component Object Model: https://en.wikipedia.org/wiki/Component_Object_Model
.. _FileSystemObject: https://docs.microsoft.com/en-us/office/vba/language/reference/user-interface-help/filesystemobject-object
.. _CreateTextFile: https://docs.microsoft.com/en-us/office/vba/language/reference/user-interface-help/createtextfile-method
