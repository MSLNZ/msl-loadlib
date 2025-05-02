from msl.loadlib import Server32


class BadInitArgs2(Server32):
    def __init__(self, host: str, port: int, extra: int, **kwargs: str) -> None:  # pyright: ignore[reportMissingSuperCall]
        pass
