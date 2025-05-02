from msl.loadlib import Server32


class BadLibPath(Server32):
    def __init__(self, host: str, port: int, **kwargs: str) -> None:
        super().__init__("doesnotexist", "cdll", host, port, **kwargs)
