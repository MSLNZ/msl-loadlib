# .NET {: #direct-dotnet }

Load a 64-bit C# library (a .NET Framework) in 64-bit Python. Include the `"net"` argument to indicate that the `.dll` file is for the .NET Framework. *To load the 32-bit library in 32-bit Python use `"dotnet_lib32.dll"` as the filename.*

## Example

Load the example [.NET library][dotnet-lib]

!!! tip
    `"clr"` is an alias for `"net"` and can also be used as the value of `libtype` when instantiating [LoadLibrary][msl.loadlib.load_library.LoadLibrary].

<!-- invisible-code-block: pycon
>>> SKIP_IF_32BIT() or SKIP_IF_NO_PYTHONNET()

-->

```pycon
>>> from msl.loadlib import LoadLibrary
>>> from msl.examples.loadlib import EXAMPLES_DIR
>>> net = LoadLibrary(EXAMPLES_DIR / "dotnet_lib64.dll", "net")

```

The library contains a reference to the `DotNetMSL` module (which is a C# namespace), the `StaticClass` class, the `StringManipulation` class and the [System]{:target="_blank"} namespace.

Create an instance of the `BasicMath` class in the `DotNetMSL` namespace and call the `multiply_doubles` method

```pycon
>>> bm = net.lib.DotNetMSL.BasicMath()
>>> bm.multiply_doubles(2.3, 5.6)
12.879999...

```

Create an instance of the `ArrayManipulation` class in the `DotNetMSL` namespace and call the `scalar_multiply` method

```pycon
>>> am = net.lib.DotNetMSL.ArrayManipulation()
>>> values = am.scalar_multiply(2., [1., 2., 3., 4., 5.])
>>> values
<System.Double[] object at ...>
>>> [val for val in values]
[2.0, 4.0, 6.0, 8.0, 10.0]

```

Call the `reverse_string` method in the `StringManipulation` class to reverse a string

```pycon
>>> net.lib.StringManipulation().reverse_string("abcdefghijklmnopqrstuvwxyz")
'zyxwvutsrqponmlkjihgfedcba'

```

Call the static `add_multiple` method in the `StaticClass` class to add five integers

```pycon
>>> net.lib.StaticClass.add_multiple(1, 2, 3, 4, 5)
15

```

One can create objects from the [System]{:target="_blank"} namespace,

```pycon
>>> System = net.lib.System

```

for example, to create a 32-bit signed integer,

```pycon
>>> System.Int32(9)
<System.Int32 object at ...>

```

or, a one-dimensional [Array]{:target="_blank"} of the specified [Type]{:target="_blank"}

```pycon
>>> array = System.Array[int](list(range(10)))
>>> array
<System.Int32[] object at ...>
>>> list(array)
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
>>> array[0] = -1
>>> list(array)
[-1, 1, 2, 3, 4, 5, 6, 7, 8, 9]

```

<!-- invisible-code-block: pycon
# https://github.com/pythonnet/pythonnet/issues/1683
>>> net.cleanup()

-->

## Configure a .NET runtime {: #config-runtime }

By default, `pythonnet` uses the .NET Framework runtime on Windows and the Mono runtime on Linux/macOS. To configure `pythonnet` to use the non-default runtime, such as the .NET Core runtime, you must either run

```python
from pythonnet import load
load("coreclr")
```

or define a `PYTHONNET_RUNTIME=coreclr` environment variable, e.g.,

```python
import os
os.environ["PYTHONNET_RUNTIME"] = "coreclr"
```

before [LoadLibrary][msl.loadlib.load_library.LoadLibrary] is called. To explicitly use the Mono runtime, replace `"coreclr"` with `"mono"` or to use the .NET Framework runtime on Windows use `"netfx"`.

## .NET Source Code {: #dotnet-lib }

??? example "dotnet_lib.cs"
    ```csharp
    --8<-- "src/msl/examples/loadlib/dotnet_lib.cs"
    ```

[System]: https://docs.microsoft.com/en-us/dotnet/api/system
[Array]: https://docs.microsoft.com/en-us/dotnet/api/system.array
[Type]: https://docs.microsoft.com/en-us/dotnet/api/system.type
