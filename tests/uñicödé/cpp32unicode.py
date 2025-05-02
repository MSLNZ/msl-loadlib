import ctypes

from msl.loadlib import Server32


class Cpp32(Server32):
    def __init__(self, host: str, port: int) -> None:
        super().__init__("cpp_lib32-uñicödé", "cdll", host, port)

    def add(self, a: int, b: int) -> int:
        result: int = self.lib.add(ctypes.c_int32(a), ctypes.c_int32(b))
        return result
