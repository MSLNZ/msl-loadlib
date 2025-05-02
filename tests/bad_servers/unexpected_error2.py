from msl.loadlib import Server32


class UnexpectedError(Server32):
    def __init__(self, host: str, port: int, **kwargs: str) -> None:  # pyright: ignore[reportMissingSuperCall] # noqa: ARG002
        _ = 1 + "hello"  # type: ignore[operator] # pyright: ignore[reportOperatorIssue,reportUnknownVariableType]
