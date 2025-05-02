from msl.loadlib import Server32


class BadSuperInit(Server32):
    def __init__(self, host: str, port: int, **kwargs: str) -> None:  # noqa: ARG002
        super().__init__()  # type: ignore[call-arg] # pyright: ignore[reportCallIssue]
