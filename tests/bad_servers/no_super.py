from msl.loadlib import Server32


class NoSuper(Server32):
    def __init__(self, host: str, port: int, **kwargs: str) -> None:  # pyright: ignore[reportMissingSuperCall]
        pass
