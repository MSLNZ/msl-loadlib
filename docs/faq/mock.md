# Mocking the connection to the server {: #faq-mock }

You may mock the connection to the server by passing in `host=None` when you instantiate [Client64][]. Also, the [Server32][] may need to decide which library to load.

When the connection is mocked, both [Client64][] and [Server32][] instances will run in the same Python interpreter, therefore the server must load a library that is the same bitness as the Python interpreter that the client is running in. The [pickle][]{:target="_blank"} module is not used when the connection is mocked, so there is no overhead of using a file as a middle step to process requests and responses (which has a side effect that a mocked connection can return objects in a server's response that are not pickleable).

One reason that you may want to mock the connection is that you wrote a lot of code that had to load a 32-bit library but now a 64-bit version of the library is available. You may also need to support the 32-bit and 64-bit libraries at the same time. Instead of making a relatively large change to your code, or managing different code bases, you can simply specify a keyword argument when instantiating your client class to decide whether to use the 32-bit library or the 64-bit library and the client class behaves exactly the same.

Here is an example on how a client (running within 64-bit Python) can have a [Server32][] subclass load a 32-bit library or a 64-bit library.

```python
from msl.loadlib import Client64, Server32

class MockableServer(Server32):

    def __init__(self, host, port, **kwargs):
        # Decide which library to load on the server.
        # `host` is `None` when the connection is mocked.
        if host is None:
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
