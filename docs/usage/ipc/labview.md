# LabVIEW {: #ipc-labview }

This example shows how to access a 32-bit LabVIEW library from 64-bit Python. [Labview32][msl.examples.loadlib.labview32.Labview32] is the 32-bit server and [Labview64][msl.examples.loadlib.labview64.Labview64] is the 64-bit client. The source code of the LabVIEW program is available [here][labview-lib].

!!! attention
    This example requires that a 32-bit [LabVIEW Run-Time Engine]{:target="_blank"} is installed and that the operating system is Windows.

Create a [Labview64][msl.examples.loadlib.labview64.Labview64] client to communicate with the 32-bit [labview_lib32][labview-lib] library

<!-- invisible-code-block: pycon
>>> SKIP_LABVIEW32()
-->

```pycon
>>> from msl.examples.loadlib import Labview64
>>> labview = Labview64()

```

Calculate the mean, the *sample* variance and the standard deviation of some data, see [Labview64.stdev][msl.examples.loadlib.labview64.Labview64.stdev]

```pycon
>>> data = [1, 2, 3, 4, 5, 6, 7, 8, 9]
>>> labview.stdev(data)
(5.0, 7.5, 2.7386127875258306)

```

Calculate the mean, the *population* variance and the standard deviation of `data`

```pycon
>>> labview.stdev(data, 1)
(5.0, 6.666666666666667, 2.581988897471611)

```

You have access to the server's `stdout` and `stderr` streams when you shut down the server

```pycon
>>> stdout, stderr = labview.shutdown_server32()

```

[LabVIEW Run-Time Engine]: https://www.ni.com/en/support/downloads/software-products/download.labview-runtime.html
[SYSTEMTIME]: https://docs.microsoft.com/en-us/windows/win32/api/minwinbase/ns-minwinbase-systemtime
