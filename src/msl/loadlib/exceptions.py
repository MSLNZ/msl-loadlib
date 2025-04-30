"""Exception classes for msl-loadlib IPC server communication."""

from __future__ import annotations

from http.client import HTTPException


class ConnectionTimeoutError(OSError):
    """Raised when the connection to the 32-bit server cannot be established."""

    def __init__(self, message: str) -> None:
        """
        Args:
            message: The error message describing why the connection failed.
        """
        super().__init__(message)
        self.timeout_message: str = message
        self.reason: str = ""

    def __str__(self) -> str:
        """Returns the full error message, including any additional reason."""
        if self.reason:
            return f"{self.timeout_message}\nReason: {self.reason}"
        return self.timeout_message


class Server32Error(HTTPException):
    """Raised when an exception occurs on the 32-bit server."""

    def __init__(self, value: str, *, name: str = "", traceback: str = "") -> None:
        """
        Args:
            value: The error message from the server.
            name: The name of the exception type raised server-side.
            traceback: The full server-side traceback.
        """
        msg = f"\n{traceback}\n{name}: {value}" if name else value
        super().__init__(msg)
        self._value: str = value
        self._name: str = name
        self._traceback: str = traceback

    @property
    def name(self) -> str:
        """The name of the exception type raised on the server."""
        return self._name

    @property
    def traceback(self) -> str:
        """The server-side traceback."""
        return self._traceback

    @property
    def value(self) -> str:
        """The error message from the server."""
        return self._value


class ResponseTimeoutError(OSError):
    """Raised when waiting for a response from the 32-bit server times out."""

    def __init__(self, message: str, timeout: float | None = None) -> None:
        """
        Args:
            message: The error message describing the timeout.
            timeout: The number of seconds waited before timing out (if known).
        """
        super().__init__(message)
        self.message: str = message
        self.timeout: float | None = timeout

    def __str__(self) -> str:
        """Return the timeout message, including the timeout duration if available."""
        if self.timeout is not None:
            return f"{self.message} (after {self.timeout:.1f}s)"
        return self.message
