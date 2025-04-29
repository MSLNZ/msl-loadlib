# Client-Server {: #client-server }

This section of the documentation shows examples for how a module running within a 64-bit Python interpreter can communicate with a 32-bit library by using [inter-process communication][]{:target="_blank"}. The method that is used to allow a 32-bit and a 64-bit process to exchange information is by use of a file. The [pickle][]{:target="_blank"} module is used to (de)serialize Python objects.

!!! attention
    See [Direct][direct] if you want to load a 64-bit library in 64-bit Python or a 32-bit library in 32-bit Python.

## Example Server

Suppose you want to call functions in a 32-bit C library, `my_lib.dll`, from a 64-bit Python interpreter. This C library is loaded by the following `MyServer` class, which is running within a 32-bit process. `MyServer` hosts the C library at a specified host address and port number. Any class that is a subclass of [Server32][] **must** provide two arguments in its constructor: `host` and `port`. Including keyword arguments in the constructor is optional.

!!! example "my_server.py"

    ```python
    from __future__ import annotations

    from msl.loadlib import Server32

    class MyServer(Server32):
        """Load a 32-bit C library 'my_lib.dll' that has an 'add' and a 'version' function."""

        def __init__(self, host: str, port: int, **kwargs: str) -> None:
            # The `host` and `port` arguments are mandatory.
            # All values in `kwargs` are of type string.
            # Calling super() loads the 'my_lib.dll' library using `ctypes.CDLL`.
            super().__init__("my_lib.dll", "cdll", host, port)

            # The Server32 class has a `lib` attribute that is a reference
            # to the ctypes.CDLL object.

            # The 'version' function in the library returns an int32_t.
            # Store the result as an attribute of 'MyServer'.
            self.version: int = self.lib.version()

        def add(self, a: int, b: int) -> int:
            # The 'add' function in the library takes two int32_t parameters
            # and returns the sum.
            return self.lib.add(a, b)
    ```

## Example Client

The following `MyClient` is a subclass of [Client64][] and it will communicate with `MyServer` to call functions in the C library. When an instance of `MyClient` is created, the server starts automatically so that `MyClient` can send requests to `MyServer` to call the `add` function in the C library and to get the value of the `version` attribute of `MyServer`. `MyServer` processes the request and sends the response back to `MyClient`.

!!! example "my_client.py"

    ```python
    from __future__ import annotations

    from msl.loadlib import Client64

    class MyClient(Client64):
        """Call a function in 'my_lib.dll' via the 'MyServer' wrapper."""

        def __init__(self, **kwargs) -> None:
            # Specify the name of the Python module to run on the 32-bit server (i.e., "my_server").
            # All user-defined keyword arguments will appear as `kwargs` in `MyServer.__init__`.
            super().__init__("my_server", **kwargs)

        def add(self, a: int, b: int) -> int:
            # The `Client64` class has a `request32` method to send a request to the 32-bit server.
            # Send the `a` and `b` arguments to the `MyServer.add` method.
            return self.request32("add", a, b)

        def version(self) -> int:
            # Get the 'version' attribute.
            return self.request32("version")
    ```

The `MyClient` class could then be used as follows

```python
from my_client import MyClient

c = MyClient()
x = c.add(1, 2)
v = c.version()
c.shutdown_server32()

# or as a context manager
with MyClient() as c:
    x = c.add(1, 2)
    v = c.version()
```

Keyword arguments, `kwargs`, that the [Server32][] subclass requires can be passed to the server from the [Client64][]; however, the data types for the values of the `kwargs` are not preserved (since they are ultimately parsed from the command line). All data types for the values of `kwargs` will be of type [str][]{:target="_blank"} at the `__init__` method of the [Server32][] subclass. These `kwargs` are the only values where the data type is not preserved for the client-server protocol. See the [Echo][ipc-echo] example which shows that data types are preserved between client-server method calls (provided that the value is [pickle][]{:target="_blank"}able).

??? tip "Simplifying the Client"

    If you find yourself repeatedly implementing each method in your [Client64][] subclass in the following way (i.e., you are essentially duplicating the code for each method)

    ```python
    from msl.loadlib import Client64

    class LinearAlgebra(Client64):

        def __init__(self):
            super().__init__("linear_algebra_32.py")

        def solve(self, matrix, vector):
            return self.request32("solve", matrix, vector)

        def eigenvalues(self, matrix):
            return self.request32("eigenvalues", matrix)

        def stdev(self, data, as_population=True)
            return self.request32("stdev", data, as_population=as_population)

        def determinant(self, matrix):
            return self.request32("determinant", matrix)

        def cross_product(self, vector1, vector2):
            return self.request32("cross_product", vector1, vector2)
    ```

    Then you can simplify the implementation by defining your [Client64][] subclass as

    ```python
    from msl.loadlib import Client64

    class LinearAlgebra(Client64):

        def __init__(self):
            super().__init__("linear_algebra_32.py")

        def __getattr__(self, name):
            def send(*args, **kwargs):
                return self.request32(name, *args, **kwargs)
            return send
    ```

    and you will get the same behaviour. If you call a method that does not exist on the [Server32][] subclass or if you specify the wrong number of arguments or keyword arguments then a [Server32Error][msl.loadlib.exceptions.Server32Error] will be raised.

    There are situations where you may want to explicitly write some (or all) of the methods in the [Client64][] subclass in addition to (or instead of) implementing the [`__getattr__`][object.__getattr__]{:target="_blank"} method, e.g.,

    * you are writing an API for others to use and you want features like autocomplete or docstrings to be available in the IDE that the person using your API is using

    * you want the [Client64][] subclass to do error checking on the `*args`, `**kwargs` and/or on the result from the [Server32][] subclass (this allows you to have control over the type of [Exception][bltin-exceptions]{:target="_blank"} that is raised because if the [Server32][] subclass raises an exception then it is a [Server32Error][msl.loadlib.exceptions.Server32Error])

    * you want to modify the returned object from a particular [Server32][] method, for example, a [list][]{:target="_blank"} is returned but you want the corresponding [Client64][] method to return a [numpy.ndarray][]{:target="_blank"}

## Runnable Examples

The following examples are included with `msl-loadlib` to demonstrate how to communicate with libraries that were compiled in different programming languages or using different calling conventions.

* [Echo][ipc-echo]
* [C++][ipc-cpp]
* [FORTRAN][ipc-fortran]
* [.NET][ipc-dotnet]
* [Windows __stdcall][ipc-stdcall]
* [LabVIEW][ipc-labview]

[inter-process communication]: https://en.wikipedia.org/wiki/Inter-process_communication
