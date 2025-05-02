from msl.loadlib import Server32


class BadLibType(Server32):
    def __init__(self, host: str, port: int, **kwargs: str) -> None:
        super().__init__("does_not_matter", "invalid", host, port, **kwargs)  # type: ignore[arg-type]  # pyright: ignore[reportArgumentType]
