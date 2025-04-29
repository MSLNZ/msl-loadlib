# *Echo* {: #ipc-echo }

This example illustrates that Python data types are preserved when they are passed from the [Echo64][msl.examples.loadlib.echo64.Echo64] client to the [Echo32][msl.examples.loadlib.echo32.Echo32] server and back. The [Echo32.received_data][msl.examples.loadlib.echo32.Echo32.received_data] method simply returns a [tuple][]{:target="_blank"} of the `(args, kwargs)` that it received back to the [Echo64.send_data][msl.examples.loadlib.echo64.Echo64.send_data] method in the client.

Create an [Echo64][msl.examples.loadlib.echo64.Echo64] instance

<!-- invisible-code-block: pycon
>>> SKIP_IF_MACOS()

-->

```pycon
>>> from msl.examples.loadlib import Echo64
>>> echo = Echo64()

```

send a boolean as an argument

```pycon
>>> echo.send_data(True)
((True,), {})

```

send a boolean as a keyword argument

```pycon
>>> echo.send_data(boolean=True)
((), {'boolean': True})

```

send multiple data types as arguments and as keyword arguments

```pycon
>>> echo.send_data(1.2, {"my_list":[1, 2, 3]}, 0.2j, range(10), x=True, y="hello world!")
((1.2, {'my_list': [1, 2, 3]}, 0.2j, range(0, 10)), {'x': True, 'y': 'hello world!'})

```

You have access to the server's `stdout` and `stderr` streams when you shut down the server

```pycon
>>> stdout, stderr = echo.shutdown_server32()

```
