# Access `stdout` and `stderr` from the server {: #faq-streams }

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
