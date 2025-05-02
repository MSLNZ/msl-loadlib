from msl.loadlib import Server32


class BadInitArgs(Server32):
    def __init__(self) -> None:  # pyright: ignore[reportMissingSuperCall]
        pass
