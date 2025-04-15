"""
Exception classes.
"""
from __future__ import annotations

from http.client import HTTPException


class ConnectionTimeoutError(OSError):

    def __init__(self, message: str) -> None:
        """Raised when the connection to the 32-bit server cannot be established.

        :param message: The error message.
        """
        super().__init__(message)
        self.timeout_message: str = message
        self.reason: str = ""

    def __str__(self) -> str:
        if self.reason:
            return f"{self.timeout_message}\n{self.reason}"
        return self.timeout_message


class Server32Error(HTTPException):

    def __init__(self,
                 value: str,
                 *,
                 name: str = "",
                 traceback: str = "") -> None:
        """Raised when an exception occurs on the 32-bit server.

        .. versionadded:: 0.5

        :param value: The error message.
        :param name: The name of the exception type.
        :param traceback: The exception traceback.
        """
        super().__init__(f"\n{traceback}\n{name}: {value}" if name else value)
        self._value: str = value
        self._name: str = name
        self._traceback: str = traceback

    @property
    def name(self) -> str:
        """The name of the exception type."""
        return self._name

    @property
    def traceback(self) -> str:
        """The exception traceback."""
        return self._traceback

    @property
    def value(self) -> str:
        """The error message."""
        return self._value


class ResponseTimeoutError(OSError):
    """Raised when a timeout occurs while waiting for a response from the 32-bit server.

    .. versionadded:: 0.6
    """
