"""
Exception classes.
"""
try:
    from http.client import HTTPException
except ImportError:  # then Python 2
    from httplib import HTTPException

from . import IS_PYTHON2


class ConnectionTimeoutError(OSError):

    def __init__(self, *args, **kwargs):
        """Raised when the connection to the 32-bit server cannot be established."""
        self.timeout_message = args[0] if args else 'Timeout'
        self.reason = ''
        super(ConnectionTimeoutError, self).__init__(*args, **kwargs)

    def __str__(self):
        return self.timeout_message + '\n' + self.reason


class Server32Error(HTTPException):

    def __init__(self, value, name=None, traceback=None):
        """Raised when an exception occurs on the 32-bit server.

        .. versionadded:: 0.5

        Parameters
        ----------
        value : :class:`str`
            The error message.
        name : :class:`str`, optional
            The name of the exception.
        traceback : :class:`str`, optional
            The exception traceback.
        """
        msg = u'\n{}\n{}: {}'.format(traceback, name, value) if name else value
        if IS_PYTHON2:
            msg = msg.encode('utf-8')
        super(Server32Error, self).__init__(msg)
        self._name = name
        self._value = value
        self._traceback = traceback

    @property
    def name(self):
        """:class:`str`: The name of the exception from the 32-bit server."""
        return self._name

    @property
    def traceback(self):
        """:class:`str`: The exception traceback from the 32-bit server."""
        return self._traceback

    @property
    def value(self):
        """:class:`str`: The error message from the 32-bit server."""
        return self._value


class ResponseTimeoutError(OSError):
    """Raised when a timeout occurs while waiting for a response from the 32-bit server.

    .. versionadded:: 0.6
    """
