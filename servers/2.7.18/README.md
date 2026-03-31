This 32-bit server is bundled with the following versions:

* Python 2.7.18
* msl-loadlib 0.10.0
* pythonnet 2.5.2
* comtypes 1.2.1

You can use this 32-bit server with your 64-bit application by using the following templates as a starting point, with `my_client.py`, `my_server.py` and `server32-windows.exe` saved in the same directory (`server32-windows.exe.config` is only required if you are loading a 32-bit .NET library that was built with .NET Framework version < 4.0). You can install the latest version of `msl-loadlib` in your 64-bit Python interpreter.

```python
# my_client.py
from msl.loadlib import Client64

class MyClient(Client64):

    def __init__(self) -> None:
        super().__init__("my_server", server32_dir=".", protocol=2)
```

The code in `my_server.py` must be valid for running in a Python 2.7 interpreter.

```python
# my_server.py
from msl.loadlib import Server32

class MyServer(Server32):

    def __init__(self, host, port, **kwargs):
        Server32.__init__(self, r"path\to\library.dll", "cdll", host, port)
```
