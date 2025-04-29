# COM {: #direct-com }

To load a [Component Object Model]{:target="_blank"} (COM) library you pass in the library's Program or Class ID. To view the COM libraries that are available on your computer you can use the [get_com_info][msl.loadlib.utils.get_com_info] function.

!!! attention
    This example is only valid on Windows.

Here we load the [FileSystemObject]{:target="_blank"} and include the `"com"` argument to indicate that it is a COM library

<!-- invisible-code-block: pycon
>>> SKIP_IF_NOT_WINDOWS()

-->

```pycon
>>> from msl.loadlib import LoadLibrary
>>> com = LoadLibrary("Scripting.FileSystemObject", "com")
>>> com
<LoadLibrary libtype=POINTER(IFileSystem3) path=Scripting.FileSystemObject>

```

We can then use the library to create, edit and close a text file by using the [CreateTextFile]{:target="_blank"} method

```pycon
>>> fp = com.lib.CreateTextFile("a_new_file.txt")
>>> fp.Write("This is a test.")
0
>>> fp.Close()
0

```

Verify that the file exists and that the text is correct

```pycon
>>> com.lib.FileExists("a_new_file.txt")
True
>>> file = com.lib.OpenTextFile("a_new_file.txt")
>>> file.ReadAll()
'This is a test.'
>>> file.Close()
0

```

<!-- invisible-code-block: pycon
>>> import os
>>> os.remove("a_new_file.txt")

-->

[Component Object Model]: https://learn.microsoft.com/en-us/windows/win32/com/component-object-model--com--portal
[FileSystemObject]: https://learn.microsoft.com/en-us/office/vba/language/reference/user-interface-help/filesystemobject-object
[CreateTextFile]: https://learn.microsoft.com/en-us/office/vba/language/reference/user-interface-help/createtextfile-method
