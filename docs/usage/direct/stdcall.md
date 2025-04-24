# Windows __stdcall {: #direct-stdcall }

Load a 32-bit Windows `__stdcall` library in 32-bit Python, see [kernel32]{:target="_blank"}. Include the `"windll"` argument to specify that the calling convention is `__stdcall`.

<!-- invisible-code-block: pycon
>>> SKIP_IF_NOT_WINDOWS() or SKIP_IF_64BIT()

-->

```pycon
>>> from msl.loadlib import LoadLibrary
>>> kernel = LoadLibrary(r"C:\Windows\SysWOW64\kernel32.dll", "windll")
>>> kernel
<LoadLibrary libtype=WinDLL path=C:\Windows\SysWOW64\kernel32.dll>
>>> kernel.lib
<WinDLL 'C:\Windows\SysWOW64\kernel32.dll', handle ... at ...>

```

Create an instance of the [SYSTEMTIME]{:target="_blank"} structure

```pycon
>>> from ctypes import pointer
>>> from msl.examples.loadlib.kernel32 import SystemTime
>>> st = SystemTime()
>>> time = kernel.lib.GetLocalTime(pointer(st))

```

Now that we have a [SYSTEMTIME]{:target="_blank"} structure we can access its attributes and compare the values to the builtin [datetime.datetime][]{:target="_blank"} module

```pycon
>>> from datetime import datetime
>>> today = datetime.today()
>>> st.wYear == today.year
True
>>> st.wMonth == today.month
True
>>> st.wDay == today.day
True

```

See [here][ipc-stdcall] for an example on how to communicate with [kernel32]{:target="_blank"} from 64-bit Python.

[kernel32]: https://www.geoffchappell.com/studies/windows/win32/kernel32/api/
[SYSTEMTIME]: https://docs.microsoft.com/en-us/windows/win32/api/minwinbase/ns-minwinbase-systemtime
