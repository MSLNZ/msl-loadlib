# FAQ

Answers to frequently asked questions.

## Access `stdout` and `stderr` from the server {: #faq-streams }

You have access to the console output, `stdout` and `stderr`, of the 32-bit server once it has shut down. For example, suppose your 64-bit client class is called `MyClient`, you could do something like

```python
c = MyClient()
c.do_something()
c.do_something_else()
stdout, stderr = c.shutdown_server32()
print(stdout.read())
print(stderr.read())
```

If you want to be able to poll the console output in real time (while the server is running) you have two options:

1. Have the server write to a file and the client read from the file.

2. Implement a `polling` method on the server for the client to send requests to. The following is a runnable example

```python
import os

from msl.loadlib import Client64, Server32

class Polling32(Server32):

    def __init__(self, host, port):
        # Loading a "dummy" 32-bit library for this example
        path = os.path.join(Server32.examples_dir(), "cpp_lib32")
        super().__init__(path, "cdll", host, port)

        # Create a list to store 'print' messages in
        self._stdout = []

        # Use your own print method instead of calling the
        # builtin print() function
        self.print("Polling32 has been initiated")

    def say_hello(self, name):
        """Return a greeting."""
        self.print(f"say_hello was called with argument {name!r}")
        return f"Hello, {name}!"

    def poll(self):
        """Get the latest message."""
        try:
            return self._stdout[-1]
        except IndexError:
            return ""

    def flush(self):
        """Get all messages and clear the cache."""
        messages = "\n".join(self._stdout)
        self._stdout.clear()
        return messages

    def print(self, message):
        """Append a message."""
        self._stdout.append(message)

class Polling64(Client64):

    def __init__(self):
        super().__init__(__file__)

    def __getattr__(self, name):
        def send(*args, **kwargs):
            return self.request32(name, *args, **kwargs)
        return send

# Only execute this section of code on the 64-bit client
# (not on the 32-bit server). You may also prefer to write the
# Server32 class and the Client64 class in separate files.
if __name__ == "__main__":
    p = Polling64()
    print("poll ->", p.poll())
    print("say_hello ->", p.say_hello("world"))
    print("poll ->", p.poll())
    print("flush ->", repr(p.flush()))
    print("poll ->", repr(p.poll()))
    p.shutdown_server32()
```

Running the above script will output:

```console
poll -> Polling32 has been initiated
say_hello -> Hello, world!
poll -> say_hello was called with argument 'world'
flush -> "Polling32 has been initiated\nsay_hello was called with argument 'world'"
poll -> ''
```

## Freezing the `msl-loadlib` package {: #faq-freeze }

If you want to use [PyInstaller]{:target="_blank"} or [cx-Freeze]{:target="_blank"} to bundle MSL-LoadLib in a frozen application, the 32-bit server must be added as a data file.

For example, using [PyInstaller]{:target="_blank"} on Windows you would include an ``--add-data`` option

```console
pyinstaller --add-data "..\site-packages\msl\loadlib\server32-windows.exe:."
```

where you must replace the leading `..` prefix with the parent directories to the file (i.e., specify the absolute path to the file). On Linux, replace `server32-windows.exe:.` with `server32-linux:.`

If the server is loading a .NET library that was compiled with .NET < 4.0, you must also add the `server32-windows.exe.config` data file. Otherwise, you do not need to add this config file.

[cx-Freeze]{:target="_blank"} appears to automatically bundle the 32-bit server (tested with [cx-Freeze]{:target="_blank"} version 6.14.5) so there may not be anything you need to do. If the `server32` executable is not bundled, you can specify the absolute path to the `server32` executable as the `include_files` option for the `build_exe` command.

You may also wish to [refreeze][] the 32-bit server and add your custom server to your application.

## Mocking the connection to the server {: #faq-mock }

You may mock the connection to the server by passing in `host=None` when you instantiate [Client64][msl.loadlib.client64.Client64]. Also, the [Server32][msl.loadlib.server32.Server32] may need to decide which library to load.

When the connection is mocked, both [Client64][msl.loadlib.client64.Client64] and [Server32][msl.loadlib.server32.Server32] instances will run in the same Python interpreter, therefore the server must load a library that is the same bitness as the Python interpreter that the client is running in. The [pickle][]{:target="_blank"} module is not used when the connection is mocked, so there is no overhead of using a file as a middle step to process requests and responses (which has a side effect that a mocked connection can return objects in a server's response that are not pickleable).

One reason that you may want to mock the connection is that you wrote a lot of code that had to load a 32-bit library but now a 64-bit version of the library is available. You may also need to support the 32-bit and 64-bit libraries at the same time. Instead of making a relatively large change to your code, or
managing different code bases, you can simply specify a keyword argument when instantiating your client class to decide whether to use the 32-bit library or the 64-bit library and the client class behaves exactly the same.

Here is an example on how a client (running within 64-bit Python) can have a server load a 32-bit library or a 64-bit library.

```python
import sys

from msl.loadlib import Client64, Server32

class MockableServer(Server32):

    def __init__(self, host, port, **kwargs):
        # Decide which library to load on the server.
        # You could check if the server is running in a 32-bit
        # or a 64-bit version of Python (like is shown here) or
        # check "if host is None:", which is `True` when the
        # connection is mocked.
        if sys.maxsize > 2 ** 32:
            path = "path/to/64bit/c/library.so"
        else:
            path = "path/to/32bit/c/library.so"
        super().__init__(path, "cdll", host, port)

class MockableClient(Client64):

    def __init__(self, **kwargs):
        super().__init__(__file__, **kwargs)

if __name__ == "__main__":
    client_uses_32bit_library = MockableClient()
    client_uses_64bit_library = MockableClient(host=None)
```

[PyInstaller]: https://pyinstaller.org/en/stable/
[cx-Freeze]: https://cx-freeze.readthedocs.io/en/latest/index.html
