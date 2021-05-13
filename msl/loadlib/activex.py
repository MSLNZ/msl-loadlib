"""
Helper module for loading an ActiveX library.

The module also defines all the `Window Styles`_ and `Extended Window Styles`_ constants.

.. _Window Styles: https://docs.microsoft.com/en-us/windows/win32/winmsg/window-styles
.. _Extended Window Styles: https://docs.microsoft.com/en-us/windows/win32/winmsg/extended-window-styles
"""
import ctypes

try:
    import clr
    import System
    clr.AddReference('System.Windows.Forms')
    import System.Windows.Forms as Forms
except:
    clr = None

    class Forms(object):
        Form = object

try:
    from comtypes import (
        IUnknown,
        GUID,
    )
    from comtypes.client import (
        GetEvents,
        GetBestInterface,
    )
except:
    GUID = None


CW_USEDEFAULT = 0x80000000

# Window Styles
WS_OVERLAPPED = 0x00000000
WS_POPUP = 0x80000000
WS_CHILD = 0x40000000
WS_MINIMIZE = 0x20000000
WS_VISIBLE = 0x10000000
WS_DISABLED = 0x08000000
WS_CLIPSIBLINGS = 0x04000000
WS_CLIPCHILDREN = 0x02000000
WS_MAXIMIZE = 0x01000000
WS_CAPTION = 0x00C00000
WS_BORDER = 0x00800000
WS_DLGFRAME = 0x00400000
WS_VSCROLL = 0x00200000
WS_HSCROLL = 0x00100000
WS_SYSMENU = 0x00080000
WS_THICKFRAME = 0x00040000
WS_GROUP = 0x00020000
WS_TABSTOP = 0x00010000
WS_MINIMIZEBOX = 0x00020000
WS_MAXIMIZEBOX = 0x00010000
WS_TILED = WS_OVERLAPPED
WS_ICONIC = WS_MINIMIZE
WS_SIZEBOX = WS_THICKFRAME
WS_OVERLAPPEDWINDOW = WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_THICKFRAME | WS_MINIMIZEBOX | WS_MAXIMIZEBOX
WS_POPUPWINDOW = WS_POPUP | WS_BORDER | WS_SYSMENU
WS_CHILDWINDOW = WS_CHILD
WS_TILEDWINDOW = WS_OVERLAPPEDWINDOW

# Extended Window Styles
WS_EX_DLGMODALFRAME = 0x00000001
WS_EX_NOPARENTNOTIFY = 0x00000004
WS_EX_TOPMOST = 0x00000008
WS_EX_ACCEPTFILES = 0x00000010
WS_EX_TRANSPARENT = 0x00000020
WS_EX_MDICHILD = 0x00000040
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_WINDOWEDGE = 0x00000100
WS_EX_CLIENTEDGE = 0x00000200
WS_EX_CONTEXTHELP = 0x00000400
WS_EX_RIGHT = 0x00001000
WS_EX_LEFT = 0x00000000
WS_EX_RTLREADING = 0x00002000
WS_EX_LTRREADING = 0x00000000
WS_EX_LEFTSCROLLBAR = 0x00004000
WS_EX_RIGHTSCROLLBAR = 0x00000000
WS_EX_CONTROLPARENT = 0x00010000
WS_EX_STATICEDGE = 0x00020000
WS_EX_APPWINDOW = 0x00040000
WS_EX_LAYERED = 0x00080000
WS_EX_NOINHERITLAYOUT = 0x00100000
WS_EX_NOREDIRECTIONBITMAP = 0x00200000
WS_EX_LAYOUTRTL = 0x00400000
WS_EX_COMPOSITED = 0x02000000
WS_EX_NOACTIVATE = 0x08000000
WS_EX_OVERLAPPEDWINDOW = WS_EX_WINDOWEDGE | WS_EX_CLIENTEDGE
WS_EX_PALETTEWINDOW = WS_EX_WINDOWEDGE | WS_EX_TOOLWINDOW | WS_EX_TOPMOST


class Application(Forms.Form):

    def __init__(self):
        """Create the main application window to display ActiveX controls.

        Creating an application requires pythonnet_ to be installed.

        See Form_ for more details.

        .. _Form: https://docs.microsoft.com/en-us/dotnet/api/system.windows.forms.form
        .. _pythonnet: https://pypi.org/project/pythonnet/

        .. invisible-code-block: pycon

           >>> SKIP_IF_NOT_WINDOWS()

        Examples
        --------
        >>> from msl.loadlib.activex import Application
        >>> app = Application()
        >>> app.create_panel()
        <System.Windows.Forms.Panel object at ...>
        """
        super(Application, self).__init__()

        if clr is None:
            raise RuntimeError(
                'Creating an ActiveX application requires pythonnet to be installed.\n'
                'Run: pip install pythonnet'
            )

        self._event_connections = []

    def handle_events(self, source, sink=None, interface=None):
        """Handle events from an ActiveX object.

        Parameters
        ----------
        source
            The ActiveX object that emits events.
        sink
            The object that handles the events. The `sink` must
            define methods with the same names as the ActiveX event names.
            If not specified then uses the calling application instance
            as the `sink`.
        interface
            The interface to use.

        Returns
        -------
        The connection object.
        """
        cxn = GetEvents(source, sink or self, interface=interface)
        self._event_connections.append(cxn)
        return cxn

    @staticmethod
    def create_panel():
        """Create a new `Panel <https://docs.microsoft.com/en-us/dotnet/api/system.windows.forms.panel>`_."""
        return Forms.Panel()

    @staticmethod
    def load(activex_id, parent=None, x=0, y=0, width=0, height=0, style=0, ex_style=0):
        """Load an ActiveX library.

        Additional information about the keyword arguments are described by the
        CreateWindowExA_ object.

        Loading an ActiveX library requires comtypes_ to be installed.

        .. _comtypes: https://pypi.org/project/comtypes/
        .. _CreateWindowExA: https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-createwindowexa
        .. _System.Windows.Forms: https://docs.microsoft.com/en-us/dotnet/api/system.windows.forms

        Parameters
        ----------
        activex_id : :class:`str`
            The ProgID or CLSID of the ActiveX object.
        parent
            The parent or owner window of the window being created.
            The parent is typically an object from the System.Windows.Forms_
            namespace that has a ``Handle`` property.
        x : :class:`int`, optional
            The initial horizontal position of the window.
        y : :class:`int`, optional
            The initial vertical position of the window.
        width : :class:`int`, optional
            The width of the window.
        height : :class:`int`, optional
            The height of the window.
        style : :class:`int`, optional
            The style of the window being created. This argument can be a
            combination of the `Window Styles`_ constants, e.g.,
            ``style = WS_CHILD | WS_VISIBLE``.
        ex_style : :class:`int`, optional
            The extended window style of the window being created. This argument can be a
            combination of the `Extended Window Styles`_ constants, e.g.,
            ``ex_style = WS_EX_APPWINDOW | WS_EX_CONTEXTHELP``.

        Returns
        -------
        The interface pointer to the ActiveX library.

        Raises
        ------
        OSError
            If the library cannot be loaded.
        """
        if GUID is None:
            raise OSError(
                'Cannot load an ActiveX library because comtypes is not installed.\n'
                'Run: pip install comtypes'
            )

        try:
            clsid = GUID.from_progid(activex_id)
        except (TypeError, OSError):
            clsid = None

        if clsid is None:
            raise OSError("Cannot find '{}' for libtype='activex'".format(activex_id))

        if parent is not None:
            try:
                parent_handle = parent.Handle.ToInt32()
            except AttributeError:
                parent_handle = None

            if parent_handle is None:
                raise OSError('Cannot create a Handle from the parent {}'.format(type(parent)))
        else:
            parent_handle = None

        # calling AtlAxWinInit initializes ATL's control hosting code
        # by registering the "AtlAxWin" window class so that this window
        # class is available to the CreateWindowExA function
        h_result = ctypes.windll.atl.AtlAxWinInit()
        if not h_result:
            raise OSError('Cannot register the "AtlAxWin" window class')

        # create a new window
        h_instance = ctypes.windll.kernel32.GetModuleHandleA(None)
        hwnd = ctypes.windll.user32.CreateWindowExA(
            ex_style,             # dwExStyle
            b'AtlAxWin',          # lpClassName
            str(clsid).encode(),  # lpWindowName
            style,                # dwStyle
            x,                    # X
            y,                    # Y
            width,                # nWidth
            height,               # nHeight
            parent_handle,        # hWndParent
            None,                 # hMenu
            h_instance,           # hInstance
            0                     # lpParam
        )

        if hwnd == 0:
            raise OSError('CreateWindowExA {}'.format(ctypes.WinError()))

        # get the interface to the ActiveX control
        unknown = ctypes.POINTER(IUnknown)()
        ret = ctypes.windll.atl.AtlAxGetControl(hwnd, ctypes.byref(unknown))
        if ret != 0:
            raise OSError('AtlAxGetControl {}'.format(ctypes.WinError()))

        return GetBestInterface(unknown)
