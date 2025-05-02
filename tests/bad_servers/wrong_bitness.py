import os

from msl.loadlib import Server32


class WrongBitness(Server32):
    def __init__(self, host: str, port: int, **kwargs: str) -> None:
        path = os.path.join(Server32.examples_dir(), "cpp_lib64")  # noqa: PTH118
        super().__init__(path, "cdll", host, port, **kwargs)
