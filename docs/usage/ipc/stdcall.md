# Windows __stdcall {: #ipc-stdcall }

This example shows how to access the 32-bit Windows [kernel32]{:target="_blank"} library from 64-bit Python. [Kernel32][msl.examples.loadlib.kernel32.Kernel32] is the 32-bit server and [Kernel64][msl.examples.loadlib.kernel64.Kernel64] is the 64-bit client.

Create a [Kernel64][msl.examples.loadlib.kernel64.Kernel64] client to communicate with the 32-bit [kernel32]{:target="_blank"} library

<!-- invisible-code-block: pycon
>>> SKIP_IF_NOT_WINDOWS()

-->

```pycon
>>> from msl.examples.loadlib import Kernel64
>>> k = Kernel64()
>>> k.lib32_path
'C:\\Windows\\SysWOW64\\kernel32.dll'

```

Call the library to get the current date and time by populating the [SYSTEMTIME]{:target="_blank"} structure, see [Kernel64.get_local_time][msl.examples.loadlib.kernel64.Kernel64.get_local_time]

```pycon
>>> now = k.get_local_time()

```

<!-- invisible-code-block: pycon
>>> from datetime import datetime
>>> assert isinstance(now, datetime)

-->

You have access to the server's `stdout` and `stderr` streams when you shut down the server

```pycon
>>> stdout, stderr = k.shutdown_server32()

```

[kernel32]: https://www.geoffchappell.com/studies/windows/win32/kernel32/api/
[SYSTEMTIME]: https://docs.microsoft.com/en-us/windows/win32/api/minwinbase/ns-minwinbase-systemtime
