"""
Exception classes.
"""
try:
    from httplib import HTTPException  # Python 2
except ImportError:
    from http.client import HTTPException

from . import IS_PYTHON2


class ConnectionTimeoutError(OSError):
    """Raised when the connection to the 32-bit server cannot be established."""

class ServerExit(Exception):
    '''
    Raised by the server thread to inform the HTTPServer it wants to stop.
    This is much cleaner then just calling terminate() (the server can do
    cleanup this way).
    '''
    pass

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
