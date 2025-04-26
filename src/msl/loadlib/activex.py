"""Load ActiveX controls in an application window.

The following classes are available to interact with ActiveX controls

* [Application][msl.loadlib.activex.Application]
* [Icon][msl.loadlib.activex.Icon]
* [Menu][msl.loadlib.activex.Menu]
* [MenuGroup][msl.loadlib.activex.MenuGroup]
* [MenuItem][msl.loadlib.activex.MenuItem]

and the following enumerations

* [Colour][msl.loadlib.activex.Colour]
* [ExtendedWindowStyle][msl.loadlib.activex.ExtendedWindowStyle]
* [MenuFlag][msl.loadlib.activex.MenuFlag]
* [MessageBoxOption][msl.loadlib.activex.MessageBoxOption]
* [ShowWindow][msl.loadlib.activex.ShowWindow]
* [WindowClassStyle][msl.loadlib.activex.WindowClassStyle]
* [WindowPosition][msl.loadlib.activex.WindowPosition]
* [WindowStyle][msl.loadlib.activex.WindowStyle]
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes as wt
from enum import IntEnum
from enum import IntFlag
from typing import Any
from typing import Callable
from typing import Iterator

try:
    import comtypes
    import comtypes.client as client
except ImportError:
    comtypes = client = None

LRESULT = wt.LPARAM

WM_COMMAND = 0x0111
WM_DESTROY = 0x0002


class Colour(IntEnum):
    """Background colour.

    Attributes:
        WHITE (int): 0
        LIGHT_GREY (int): 1
        GREY (int): 2
        DARK_GREY (int): 3
        BLACK (int): 4
    """

    WHITE = 0
    LIGHT_GREY = 1
    GREY = 2
    DARK_GREY = 3
    BLACK = 4


class WindowClassStyle(IntFlag):
    """[Window class style]{:target="_blank"} flags.

    [Window class style]: https://learn.microsoft.com/en-us/windows/win32/winmsg/window-class-styles#constants

    Attributes:
        NONE (int): 0x0000
        BYTEALIGNCLIENT (int): 0x1000
        BYTEALIGNWINDOW (int): 0x2000
        CLASSDC (int): 0x0040
        DBLCLKS (int): 0x0008
        DROPSHADOW (int): 0x00020000
        GLOBALCLASS (int): 0x4000
        HREDRAW (int): 0x0002
        NOCLOSE (int): 0x0200
        OWNDC (int): 0x0020
        PARENTDC (int): 0x0080
        SAVEBITS (int): 0x0800
        VREDRAW (int): 0x0001
    """

    NONE = 0
    BYTEALIGNCLIENT = 0x1000
    BYTEALIGNWINDOW = 0x2000
    CLASSDC = 0x0040
    DBLCLKS = 0x0008
    DROPSHADOW = 0x00020000
    GLOBALCLASS = 0x4000
    HREDRAW = 0x0002
    NOCLOSE = 0x0200
    OWNDC = 0x0020
    PARENTDC = 0x0080
    SAVEBITS = 0x0800
    VREDRAW = 0x0001


class ExtendedWindowStyle(IntFlag):
    """[Extended window style]{:target="_blank"} flags.

    [Extended window style]: https://learn.microsoft.com/en-us/windows/win32/winmsg/extended-window-styles

    Attributes:
        DLGMODALFRAME (int): 0x00000001
        NOPARENTNOTIFY (int): 0x00000004
        TOPMOST (int): 0x00000008
        ACCEPTFILES (int): 0x00000010
        TRANSPARENT (int): 0x00000020
        MDICHILD (int): 0x00000040
        TOOLWINDOW (int): 0x00000080
        WINDOWEDGE (int): 0x00000100
        CLIENTEDGE (int): 0x00000200
        CONTEXTHELP (int): 0x00000400
        RIGHT (int): 0x00001000
        LEFT (int): 0x00000000
        RTLREADING (int): 0x00002000
        LTRREADING (int): 0x00000000
        LEFTSCROLLBAR (int): 0x00004000
        RIGHTSCROLLBAR (int): 0x00000000
        CONTROLPARENT (int): 0x00010000
        STATICEDGE (int): 0x00020000
        APPWINDOW (int): 0x00040000
        LAYERED (int): 0x00080000
        NOINHERITLAYOUT (int): 0x00100000
        NOREDIRECTIONBITMAP (int): 0x00200000
        LAYOUTRTL (int): 0x00400000
        COMPOSITED (int): 0x02000000
        NOACTIVATE (int): 0x08000000
        OVERLAPPEDWINDOW (int): WINDOWEDGE | CLIENTEDGE
        PALETTEWINDOW (int): WINDOWEDGE | TOOLWINDOW | TOPMOST
    """

    DLGMODALFRAME = 0x00000001
    NOPARENTNOTIFY = 0x00000004
    TOPMOST = 0x00000008
    ACCEPTFILES = 0x00000010
    TRANSPARENT = 0x00000020
    MDICHILD = 0x00000040
    TOOLWINDOW = 0x00000080
    WINDOWEDGE = 0x00000100
    CLIENTEDGE = 0x00000200
    CONTEXTHELP = 0x00000400
    RIGHT = 0x00001000
    LEFT = 0x00000000
    RTLREADING = 0x00002000
    LTRREADING = 0x00000000
    LEFTSCROLLBAR = 0x00004000
    RIGHTSCROLLBAR = 0x00000000
    CONTROLPARENT = 0x00010000
    STATICEDGE = 0x00020000
    APPWINDOW = 0x00040000
    LAYERED = 0x00080000
    NOINHERITLAYOUT = 0x00100000
    NOREDIRECTIONBITMAP = 0x00200000
    LAYOUTRTL = 0x00400000
    COMPOSITED = 0x02000000
    NOACTIVATE = 0x08000000
    OVERLAPPEDWINDOW = WINDOWEDGE | CLIENTEDGE
    PALETTEWINDOW = WINDOWEDGE | TOOLWINDOW | TOPMOST


class MenuFlag(IntFlag):
    """[Menu]{:target="_blank"} item flags.

    [Menu]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-appendmenuw

    Attributes:
        BITMAP (int): 0x00000004
        CHECKED (int): 0x00000008
        DISABLED (int): 0x00000002
        ENABLED (int): 0x00000000
        GRAYED (int): 0x00000001
        MENUBARBREAK (int): 0x00000020
        MENUBREAK (int): 0x00000040
        OWNERDRAW (int): 0x00000100
        POPUP (int): 0x00000010
        SEPARATOR (int): 0x00000800
        STRING (int): 0x00000000
        UNCHECKED (int): 0x00000000
    """

    BITMAP = 0x00000004
    CHECKED = 0x00000008
    DISABLED = 0x00000002
    ENABLED = 0x00000000
    GRAYED = 0x00000001
    MENUBARBREAK = 0x00000020
    MENUBREAK = 0x00000040
    OWNERDRAW = 0x00000100
    POPUP = 0x00000010
    SEPARATOR = 0x00000800
    STRING = 0x00000000
    UNCHECKED = 0x00000000


class MessageBoxOption(IntFlag):
    """[Message box]{:target="_blank"} flags.

    [Message box]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-messagebox

    Attributes:
        ABORTRETRYIGNORE (int): 0x00000002
        CANCELTRYCONTINUE (int): 0x00000006
        HELP (int): 0x00004000
        OK (int): 0x00000000
        OKCANCEL (int): 0x00000001
        RETRYCANCEL (int): 0x00000005
        YESNO (int): 0x00000004
        YESNOCANCEL (int): 0x00000003
        ICONEXCLAMATION (int): 0x00000030
        ICONWARNING (int): 0x00000030
        ICONINFORMATION (int): 0x00000040
        ICONASTERISK (int): 0x00000040
        ICONQUESTION (int): 0x00000020
        ICONSTOP (int): 0x00000010
        ICONERROR (int): 0x00000010
        ICONHAND (int): 0x00000010
        DEFBUTTON1 (int): 0x00000000
        DEFBUTTON2 (int): 0x00000100
        DEFBUTTON3 (int): 0x00000200
        DEFBUTTON4 (int): 0x00000300
        APPLMODAL (int): 0x00000000
        SYSTEMMODAL (int): 0x00001000
        TASKMODAL (int): 0x00002000
        DEFAULT_DESKTOP_ONLY (int): 0x00020000
        RIGHT (int): 0x00080000
        RTLREADING (int): 0x00100000
        SETFOREGROUND (int): 0x00010000
        TOPMOST (int): 0x00040000
        SERVICE_NOTIFICATION (int): 0x00200000
    """

    ABORTRETRYIGNORE = 0x00000002
    CANCELTRYCONTINUE = 0x00000006
    HELP = 0x00004000
    OK = 0x00000000
    OKCANCEL = 0x00000001
    RETRYCANCEL = 0x00000005
    YESNO = 0x00000004
    YESNOCANCEL = 0x00000003
    ICONEXCLAMATION = 0x00000030
    ICONWARNING = 0x00000030
    ICONINFORMATION = 0x00000040
    ICONASTERISK = 0x00000040
    ICONQUESTION = 0x00000020
    ICONSTOP = 0x00000010
    ICONERROR = 0x00000010
    ICONHAND = 0x00000010
    DEFBUTTON1 = 0x00000000
    DEFBUTTON2 = 0x00000100
    DEFBUTTON3 = 0x00000200
    DEFBUTTON4 = 0x00000300
    APPLMODAL = 0x00000000
    SYSTEMMODAL = 0x00001000
    TASKMODAL = 0x00002000
    DEFAULT_DESKTOP_ONLY = 0x00020000
    RIGHT = 0x00080000
    RTLREADING = 0x00100000
    SETFOREGROUND = 0x00010000
    TOPMOST = 0x00040000
    SERVICE_NOTIFICATION = 0x00200000


class WindowPosition(IntFlag):
    """[Window position]{:target="_blank"} flags.

    [Window position]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowpos

    Attributes:
        NONE (int): 0x0000
        ASYNCWINDOWPOS (int): 0x4000
        DEFERERASE (int): 0x2000
        DRAWFRAME (int): 0x0020
        FRAMECHANGED (int): 0x0020
        HIDEWINDOW (int): 0x0080
        NOACTIVATE (int): 0x0010
        NOCOPYBITS (int): 0x0100
        NOMOVE (int): 0x0002
        NOOWNERZORDER (int): 0x0200
        NOREDRAW (int): 0x0008
        NOREPOSITION (int): 0x0200
        NOSENDCHANGING (int): 0x0400
        NOSIZE (int): 0x0001
        NOZORDER (int): 0x0004
        SHOWWINDOW (int): 0x0040
    """

    NONE = 0
    ASYNCWINDOWPOS = 0x4000
    DEFERERASE = 0x2000
    DRAWFRAME = 0x0020
    FRAMECHANGED = 0x0020
    HIDEWINDOW = 0x0080
    NOACTIVATE = 0x0010
    NOCOPYBITS = 0x0100
    NOMOVE = 0x0002
    NOOWNERZORDER = 0x0200
    NOREDRAW = 0x0008
    NOREPOSITION = 0x0200
    NOSENDCHANGING = 0x0400
    NOSIZE = 0x0001
    NOZORDER = 0x0004
    SHOWWINDOW = 0x0040


class ShowWindow(IntEnum):
    """[Show window]{:target="_blank"} options.

    [Show window]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindow

    Attributes:
        HIDE (int): 0
        SHOWNORMAL (int): 1
        NORMAL (int): 1
        SHOWMINIMIZED (int): 2
        SHOWMAXIMIZED (int): 3
        MAXIMIZE (int): 3
        SHOWNOACTIVATE (int): 4
        SHOW (int): 5
        MINIMIZE (int): 6
        SHOWMINNOACTIVE (int): 7
        SHOWNA (int): 8
        RESTORE (int): 9
        SHOWDEFAULT (int): 10
        FORCEMINIMIZE (int): 11
    """

    HIDE = 0
    SHOWNORMAL = 1
    NORMAL = 1
    SHOWMINIMIZED = 2
    SHOWMAXIMIZED = 3
    MAXIMIZE = 3
    SHOWNOACTIVATE = 4
    SHOW = 5
    MINIMIZE = 6
    SHOWMINNOACTIVE = 7
    SHOWNA = 8
    RESTORE = 9
    SHOWDEFAULT = 10
    FORCEMINIMIZE = 11


class WindowStyle(IntFlag):
    """[Window style]{:target="_blank"} flags.

    [Window styles]: https://learn.microsoft.com/en-us/windows/win32/winmsg/window-styles

    Attributes:
        OVERLAPPED (int): 0x00000000
        POPUP (int): 0x80000000
        CHILD (int): 0x40000000
        MINIMIZE (int): 0x20000000
        VISIBLE (int): 0x10000000
        DISABLED (int): 0x08000000
        CLIPSIBLINGS (int): 0x04000000
        CLIPCHILDREN (int): 0x02000000
        MAXIMIZE (int): 0x01000000
        CAPTION (int): 0x00C00000
        BORDER (int): 0x00800000
        DLGFRAME (int): 0x00400000
        VSCROLL (int): 0x00200000
        HSCROLL (int): 0x00100000
        SYSMENU (int): 0x00080000
        THICKFRAME (int): 0x00040000
        GROUP (int): 0x00020000
        TABSTOP (int): 0x00010000
        MINIMIZEBOX (int): 0x00020000
        MAXIMIZEBOX (int): 0x00010000
        TILED (int): OVERLAPPED
        ICONIC (int): MINIMIZE
        SIZEBOX (int): THICKFRAME
        OVERLAPPEDWINDOW (int): OVERLAPPED | CAPTION | SYSMENU | THICKFRAME | MINIMIZEBOX | MAXIMIZEBOX
        POPUPWINDOW (int): POPUP | BORDER | SYSMENU
        CHILDWINDOW (int): CHILD
        TILEDWINDOW (int): OVERLAPPEDWINDOW
    """

    OVERLAPPED = 0x00000000
    POPUP = 0x80000000
    CHILD = 0x40000000
    MINIMIZE = 0x20000000
    VISIBLE = 0x10000000
    DISABLED = 0x08000000
    CLIPSIBLINGS = 0x04000000
    CLIPCHILDREN = 0x02000000
    MAXIMIZE = 0x01000000
    CAPTION = 0x00C00000
    BORDER = 0x00800000
    DLGFRAME = 0x00400000
    VSCROLL = 0x00200000
    HSCROLL = 0x00100000
    SYSMENU = 0x00080000
    THICKFRAME = 0x00040000
    GROUP = 0x00020000
    TABSTOP = 0x00010000
    MINIMIZEBOX = 0x00020000
    MAXIMIZEBOX = 0x00010000
    TILED = OVERLAPPED
    ICONIC = MINIMIZE
    SIZEBOX = THICKFRAME
    OVERLAPPEDWINDOW = OVERLAPPED | CAPTION | SYSMENU | THICKFRAME | MINIMIZEBOX | MAXIMIZEBOX
    POPUPWINDOW = POPUP | BORDER | SYSMENU
    CHILDWINDOW = CHILD
    TILEDWINDOW = OVERLAPPEDWINDOW


def _err_check(result, func, arguments):  # noqa: func and arguments are not used
    if not result:
        raise ctypes.WinError()
    return result


try:
    kernel32 = ctypes.windll.kernel32
    gdi32 = ctypes.windll.gdi32
    atl = ctypes.windll.atl
    user32 = ctypes.windll.user32
    shell32 = ctypes.windll.shell32

    WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM)

    class WNDCLASSEXW(ctypes.Structure):
        """Contains window class information."""

        _fields_ = (
            ("cbSize", wt.UINT),
            ("style", wt.UINT),
            ("lpfnWndProc", WNDPROC),
            ("cbClsExtra", ctypes.c_int),
            ("cbWndExtra", ctypes.c_int),
            ("hInstance", wt.HINSTANCE),
            ("hIcon", wt.HICON),
            ("hCursor", wt.HANDLE),
            ("hbrBackground", wt.HBRUSH),
            ("lpszMenuName", wt.LPCWSTR),
            ("lpszClassName", wt.LPCWSTR),
            ("hIconSm", wt.HICON),
        )

    kernel32.GetModuleHandleW.restype = wt.HMODULE
    kernel32.GetModuleHandleW.argtypes = [wt.LPCWSTR]

    user32.CreateWindowExW.errcheck = _err_check
    user32.CreateWindowExW.restype = wt.HWND
    user32.CreateWindowExW.argtypes = [
        wt.DWORD,  # dwExStyle
        wt.LPCWSTR,  # lpClassName
        wt.LPCWSTR,  # lpWindowName
        wt.DWORD,  # dwStyle
        ctypes.c_int,  # X
        ctypes.c_int,  # Y
        ctypes.c_int,  # nWidth
        ctypes.c_int,  # nHeight
        wt.HWND,  # hWndParent
        wt.HMENU,  # hMenu
        wt.HINSTANCE,  # hInstance
        wt.LPVOID,  # lpParam
    ]

    user32.SetWindowTextW.errcheck = _err_check
    user32.SetWindowTextW.restype = wt.BOOL
    user32.SetWindowTextW.argtypes = [wt.HWND, wt.LPCWSTR]

    user32.SetWindowPos.errcheck = _err_check
    user32.SetWindowPos.restype = wt.BOOL
    user32.SetWindowPos.argtypes = [
        wt.HWND,  # hWnd
        wt.HWND,  # hWndInsertAfter
        ctypes.c_int,  # X
        ctypes.c_int,  # Y
        ctypes.c_int,  # cx
        ctypes.c_int,  # cy
        wt.UINT,  # uFlags
    ]

    user32.AppendMenuW.errcheck = _err_check
    user32.AppendMenuW.restype = wt.BOOL
    user32.AppendMenuW.argtypes = [wt.HMENU, wt.UINT, wt.UINT, wt.LPCWSTR]

    user32.CheckMenuItem.restype = wt.DWORD
    user32.CheckMenuItem.argtypes = [wt.HMENU, wt.UINT, wt.UINT]

    user32.MessageBoxExW.restype = ctypes.c_int
    user32.MessageBoxExW.argtypes = [wt.HWND, wt.LPCWSTR, wt.LPCWSTR, wt.UINT, wt.WORD]

    user32.DefWindowProcW.restype = LRESULT
    user32.DefWindowProcW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]

    user32.DestroyMenu.restype = wt.BOOL
    user32.DestroyMenu.argtypes = [wt.HMENU]

    user32.RegisterClassExW.restype = wt.ATOM
    user32.RegisterClassExW.argtypes = [ctypes.POINTER(WNDCLASSEXW)]

    user32.UnregisterClassW.restype = wt.BOOL
    user32.UnregisterClassW.argtypes = [wt.LPCWSTR, wt.HINSTANCE]

    user32.CreatePopupMenu.restype = wt.HMENU
    user32.CreatePopupMenu.argtypes = []

    user32.CreateMenu.errcheck = _err_check
    user32.CreateMenu.restype = wt.HMENU
    user32.CreateMenu.argtypes = []

    user32.LoadIconW.restype = wt.HICON
    user32.LoadIconW.argtypes = [wt.HINSTANCE, wt.LPCWSTR]

    user32.LoadCursorW.restype = wt.HANDLE
    user32.LoadCursorW.argtypes = [wt.HINSTANCE, wt.LPCWSTR]

    user32.DestroyIcon.restype = wt.BOOL
    user32.DestroyIcon.argtypes = [wt.HICON]

    user32.SetMenu.restype = wt.BOOL
    user32.SetMenu.argtypes = [wt.HWND, wt.HMENU]

    user32.ShowWindow.restype = wt.BOOL
    user32.ShowWindow.argtypes = [wt.HWND, ctypes.c_int]

    user32.UpdateWindow.restype = wt.BOOL
    user32.UpdateWindow.argtypes = [wt.HWND]

    user32.GetWindowThreadProcessId.restype = wt.DWORD
    user32.GetWindowThreadProcessId.argtypes = [wt.HWND, wt.LPDWORD]

    user32.PostQuitMessage.restype = ctypes.c_void_p
    user32.PostQuitMessage.argtypes = [ctypes.c_int]

    user32.PostMessageW.restype = wt.BOOL
    user32.PostMessageW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]

    user32.GetMessageW.restype = wt.BOOL
    user32.GetMessageW.argtypes = [wt.LPMSG, wt.HWND, wt.UINT, wt.UINT]

    user32.TranslateMessage.restype = wt.BOOL
    user32.TranslateMessage.argtypes = [ctypes.POINTER(wt.MSG)]

    user32.DispatchMessageW.restype = LRESULT
    user32.DispatchMessageW.argtypes = [ctypes.POINTER(wt.MSG)]

    gdi32.GetStockObject.restype = wt.HGDIOBJ
    gdi32.GetStockObject.argtypes = [ctypes.c_int]

    shell32.ExtractIconW.restype = wt.HICON
    shell32.ExtractIconW.argtypes = [wt.HINSTANCE, wt.LPCWSTR, wt.UINT]

    atl.AtlAxWinInit.restype = wt.BOOL
    atl.AtlAxWinInit.argtypes = []

    atl.AtlAxGetControl.restype = ctypes.HRESULT
    atl.AtlAxGetControl.argtypes = [wt.HWND, ctypes.c_void_p]

except AttributeError:
    kernel32 = user32 = atl = gdi32 = shell32 = WNDCLASSEXW = None


CW_USEDEFAULT = 0x80000000


def _create_window(
    *,
    ex_style: int = 0,
    class_name: str = "",
    window_name: str = "",
    style: int = 0,
    x: int = CW_USEDEFAULT,
    y: int = CW_USEDEFAULT,
    width: int = CW_USEDEFAULT,
    height: int = CW_USEDEFAULT,
    parent: int | None = None,
    menu: int | None = None,
    instance: int | None = None,
    param: int | None = None,
) -> int:
    """Create a new Window and return the handle."""
    return user32.CreateWindowExW(
        ex_style, class_name, window_name, style, x, y, width, height, parent, menu, instance, param
    )


class Icon:
    """Extract an icon from an executable file, DLL or icon file."""

    def __init__(self, file: str, *, index: int = 0, hinstance: int | None = None) -> None:
        """Extract an icon from an executable file, DLL or icon file.

        Args:
            file: The path to an executable file, DLL or icon file.
            index: The zero-based index of the icon to extract.
            hinstance: Handle to the instance of the calling application.
        """
        self._hicon: int | None = None

        if shell32 is None:
            msg = "Loading an icon is not supported on this platform"
            raise OSError(msg)

        if index < 0:
            msg = "A negative index is not supported"
            raise ValueError(msg)

        if hinstance is None:
            hinstance = kernel32.GetModuleHandleW(None)

        self._file = file
        self._index = index
        self._hicon = shell32.ExtractIconW(hinstance, file, index)

    def __repr__(self) -> str:
        """Returns the string representation."""
        return f"<Icon file={self._file!r} index={self._index}>"

    def __del__(self) -> None:
        """Destroys the icon and frees any memory the icon occupied."""
        self.destroy()

    @property
    def hicon(self) -> int | None:
        """[int][] | `None` &mdash; The handle to the icon or `None` an icon was not found in the `file`."""
        return self._hicon

    def destroy(self) -> None:
        """Destroys the icon and frees any memory the icon occupied."""
        if self._hicon is not None and self._hicon > 0:
            user32.DestroyIcon(self._hicon)
            self._hicon = None


class MenuItem:
    """A menu item that belongs to a popup menu."""

    def __init__(self, **kwargs) -> None:
        """A menu item that belongs to a popup menu.

        !!! warning
            Do not instantiate this class directly. Use
            [MenuGroup.append][msl.loadlib.activex.MenuGroup.append]
            or [Menu.append][msl.loadlib.activex.Menu.append]
            to create a new menu item.
        """
        self._hmenu: int = kwargs["hmenu"]
        self._id: int = kwargs["id"]
        self._text: str = kwargs["text"]
        self._callback: Callback | None = kwargs["callback"]
        self._flags: int = kwargs["flags"]
        self._checked: bool = False
        self._data: Any = kwargs["data"]

    def __eq__(self, other: MenuItem) -> bool:
        """Checks for equal id's."""
        try:
            return self.id == other.id
        except AttributeError:
            return False

    def __repr__(self) -> str:
        """Returns the string representation."""
        return f"<{self.__class__.__name__} id={self._id} text={self._text!r}>"

    @property
    def callback(self) -> Callback | None:
        """[Callback][] | `None` &mdash; The callback function to call when the menu item is clicked."""
        return self._callback

    @property
    def checked(self) -> bool:
        """[bool][] &mdash; Whether the menu item's check mark is shown."""
        return self._checked

    @checked.setter
    def checked(self, value: bool) -> None:
        """Set the checked state of the menu item."""
        if self._hmenu == -1:
            msg = "A MenuItem must first be added to a Menu before it can be checked"
            raise ValueError(msg)

        # MF_CHECKED=8, MF_UNCHECKED=0
        state = 8 if value else 0
        previous = user32.CheckMenuItem(self._hmenu, self._id, state)
        if previous == -1:
            raise ctypes.WinError()
        self._checked = bool(value)

    @property
    def data(self) -> Any:
        """[Any][typing.Any] &mdash; User-defined data associated with the menu item."""
        return self._data

    @data.setter
    def data(self, value: Any) -> None:
        """Set the user data."""
        if self._hmenu == -1:
            msg = "A MenuItem must first be added to a Menu before it can be checked"
            raise ValueError(msg)

        # MF_CHECKED=8, MF_UNCHECKED=0
        state = 8 if value else 0
        previous = user32.CheckMenuItem(self._hmenu, self._id, state)
        if previous == -1:
            raise ctypes.WinError()
        self._checked = bool(value)

    @property
    def flags(self) -> int:
        """[int][] &mdash; The flags that were used to create the menu item."""
        return self._flags

    @property
    def hmenu(self) -> int:
        """[int][] &mdash; The handle to the popup menu that the menu item belongs to."""
        return self._hmenu

    @property
    def id(self) -> int:
        """[int][] &mdash; The identifier of the menu item."""
        return self._id

    @property
    def text(self) -> str:
        """[str][] &mdash; The content of the menu item."""
        return self._text


class MenuGroup:
    """A group of [MenuItem][msl.loadlib.activex.MenuItem]s."""

    def __init__(self, name: str = "") -> None:
        """A group of [MenuItem][msl.loadlib.activex.MenuItem]s.

        Only one item in the group may have a check mark to indicate
        that a particular item is selected.

        Args:
            name: A name to associate with the group.
        """
        self._name = name
        self._items: list[MenuItem] = []

    def __repr__(self) -> str:
        """Returns the string representation."""
        return f"<{self.__class__.__name__} name={self._name!r} size={len(self._items)}>"

    def __iter__(self) -> Iterator[MenuItem]:
        """Returns an iterator of the [MenuItem][msl.loadlib.activex.MenuItem]s."""
        return iter(self._items)

    def append(
        self, text: str, *, callback: Callback | None = None, data: Any = None, flags: MenuFlag = MenuFlag.STRING
    ) -> MenuItem:
        """Create a new [MenuItem][msl.loadlib.activex.MenuItem] and append it to the group.

        Args:
            text: The content of the new menu item.
            callback: A callable object that will be called when this menu item is selected.
                The callable object will receive the [MenuItem][msl.loadlib.activex.MenuItem]
                instance as an argument and the returned object is ignored.
            data: User data associated with the menu item.
            flags: Controls the appearance and behaviour of the new menu item. Can be any
                combination (bitwise OR) of [MenuFlag][msl.loadlib.activex.MenuFlag] values.

        Returns:
            The menu item that was appended to the group.
        """
        item = MenuItem(hmenu=-1, text=text, callback=callback, id=-1, flags=flags, data=data)
        self._items.append(item)
        return item

    def append_separator(self) -> None:
        """Append a horizontal dividing line to the group."""
        self._items.append(MenuItem(hmenu=-1, text=None, callback=None, id=-1, flags=MenuFlag.SEPARATOR, data=None))

    @property
    def checked(self) -> MenuItem | None:
        """[MenuItem][msl.loadlib.activex.MenuItem] | `None` &mdash; The menu item that is currently checked in the group."""
        for item in self:
            if item.checked:
                return item
        return None

    @checked.setter
    def checked(self, item: MenuItem | None) -> None:
        """Sets the menu item that is currently checked in the group."""
        for i in self:
            if i.hmenu == -1:
                msg = "A MenuGroup must first be added to a Menu before a MenuItem can be checked"
                raise ValueError(msg)
            i.checked = i == item

    @property
    def name(self) -> str:
        """[str][] &mdash; The name of the menu group."""
        return self._name


class Menu:
    """A menu associated with the main application window."""

    def __init__(self) -> None:
        """A menu associated with the main application window.

        !!! warning
            Do not instantiate directly. Use the
            [Application.menu][msl.loadlib.activex.Application.menu]
            property to access the menu instance.
        """
        self._id = 0
        self._items: dict[int, MenuItem] = {}
        self._hmenu: int = user32.CreateMenu()

    def __getitem__(self, item: int) -> MenuItem:
        """Get a [MenuItem][msl.loadlib.activex.MenuItem]."""
        return self._items[item]

    def append(
        self,
        hmenu: int,
        text: str,
        *,
        callback: Callback | None = None,
        data: Any = None,
        flags: MenuFlag = MenuFlag.STRING,
    ) -> MenuItem:
        """Create a new [MenuItem][msl.loadlib.activex.MenuItem] and append it to a popup menu.

        Args:
            hmenu: The handle of a popup menu to append the new menu item to.
            text: The content of the new menu item.
            callback: A callable object that will be called when this menu item is selected.
                The callable object will receive the [MenuItem][msl.loadlib.activex.MenuItem]
                instance as an argument and the returned object is ignored.
            data: User data associated with the menu item.
            flags: Controls the appearance and behaviour of the new menu item. Can be any
                combination (bitwise OR) of [MenuFlag][msl.loadlib.activex.MenuFlag] values.

        Returns:
            The menu item that was appended.
        """
        self._id += 1
        user32.AppendMenuW(hmenu, flags, self._id, text)
        item = MenuItem(hmenu=hmenu, text=text, callback=callback, id=self._id, flags=flags, data=data)
        self._items[self._id] = item
        return item

    def append_group(self, hmenu: int, menu_group: MenuGroup) -> None:
        """Append a group of menu items to a popup menu.

        Args:
            hmenu: The handle of a popup menu to append the group to.
            menu_group: A group of menu items.
        """
        for item in menu_group:
            self._id += 1
            item._hmenu = hmenu
            item._id = self._id
            user32.AppendMenuW(hmenu, item.flags, self._id, item.text)
            self._items[self._id] = item

    def append_separator(self, hmenu: int) -> None:
        """Append a horizontal dividing line to a popup menu.

        Args:
            hmenu: The handle to a popup menu.
        """
        self._id += 1
        user32.AppendMenuW(hmenu, MenuFlag.SEPARATOR, self._id, None)

    def create(self, text: str) -> int:
        """Create a new popup menu and append it to the main menu.

        Args:
            text: The text to display for the popup menu.

        Returns:
            The handle to the popup menu that was created.
        """
        flags = MenuFlag.STRING | MenuFlag.POPUP
        h: int = user32.CreatePopupMenu()
        user32.AppendMenuW(self._hmenu, flags, h, text)
        return h

    @property
    def hmenu(self) -> int:
        """[int][] &mdash; The handle to the main menu."""
        return self._hmenu


class Application:
    """Create the main application window to display ActiveX controls."""

    def __init__(
        self,
        *,
        background: Colour = Colour.WHITE,
        class_style: WindowClassStyle = WindowClassStyle.NONE,
        icon: Icon | None = None,
        style: WindowStyle = WindowStyle.OVERLAPPEDWINDOW,
        title: str = "ActiveX",
    ) -> None:
        """Create the main application window to display ActiveX controls.

        Args:
            background: The background colour of the main window.
            class_style: The class style(s). Can be any combination (bitwise OR)
                of [WindowClassStyle][msl.loadlib.activex.WindowClassStyle] values.
            icon: The application icon.
            style: The window style(s). Can be any combination (bitwise OR)
                of [WindowStyle][msl.loadlib.activex.WindowStyle] values.
            title: The text to display in the titlebar (if one is visible).
        """
        super().__init__()
        self._atom = None
        self._icon = icon  # prevent an icon from being garbage collected
        self._event_connections = []
        self._msg_handlers: list[Callable[[int, int, int, int], None]] = []

        if WNDCLASSEXW is None:
            msg = "An ActiveX application is not supported on this platform"
            raise OSError(msg)

        if isinstance(icon, Icon):
            h_icon = icon.hicon
        else:
            h_icon = user32.LoadIconW(None, wt.LPCWSTR(32512))  # IDI_APPLICATION

        self._window = WNDCLASSEXW()
        self._window.cbSize = ctypes.sizeof(WNDCLASSEXW)
        self._window.style = class_style
        self._window.lpfnWndProc = WNDPROC(self._window_procedure)
        self._window.cbClsExtra = 0
        self._window.cbWndExtra = 0
        self._window.hInstance = kernel32.GetModuleHandleW(None)
        self._window.hIcon = h_icon
        self._window.hCursor = user32.LoadCursorW(None, wt.LPCWSTR(32512))  # IDC_ARROW
        self._window.hbrBackground = gdi32.GetStockObject(background)
        self._window.lpszMenuName = f"ActiveXMenu{id(self._window)}"  # make the name unique
        self._window.lpszClassName = f"ActiveXClass{id(self._window)}"
        self._window.hIconSm = h_icon

        self._atom = user32.RegisterClassExW(self._window)

        self._menu = Menu()

        self._hwnd = _create_window(
            class_name=self._window.lpszClassName,
            window_name=title,
            style=style,
            instance=self._window.hInstance,
        )

        self._thread_id = user32.GetWindowThreadProcessId(self._hwnd, None)

        # calling AtlAxWinInit initializes ATL's control hosting code
        # by registering the "AtlAxWin" window class so that this window
        # class is available to the CreateWindowExW function
        if not atl.AtlAxWinInit():
            msg = "Cannot register the 'AtlAxWin' window class"
            raise OSError(msg)

    def __del__(self) -> None:
        """Destroy all event handlers and unregister the window."""
        for ec in self._event_connections:
            ec.disconnect()
        self._event_connections.clear()

        if self._atom is not None:
            user32.UnregisterClassW(self._window.lpszClassName, self._window.hInstance)
            self._atom = None

        self._icon = None

    def _window_procedure(self, hwnd: int, message: int, w_param: int, l_param: int) -> int:
        for handler in self._msg_handlers:
            handler(hwnd, message, w_param, l_param)

        if message == WM_COMMAND:
            item = self._menu[w_param]
            if item.callback is not None:
                item.callback(item)
        elif message == WM_DESTROY:
            user32.PostQuitMessage(0)
            return 0

        return user32.DefWindowProcW(hwnd, message, w_param, l_param)

    def add_message_handler(self, handler: Callable[[int, int, int, int], None]) -> None:
        """Add a custom handler for processing window messages.

        Messages correspond to events from the user and from the operating system.

        Args:
            handler: A function that processes messages sent to the main window.
                The function must accept four positional arguments (all integer values)
                and the returned object is ignored. See
                [WindowProc](https://learn.microsoft.com/en-us/windows/win32/learnwin32/writing-the-window-procedure){:target="_blank"}
                for more details about the input arguments to the `handler`.
        """
        self._msg_handlers.append(handler)

    def close(self) -> None:
        """Close the application."""
        user32.PostMessageW(self._hwnd, WM_DESTROY, 0, 0)

    def handle_events(self, source: Any, sink: Callable[..., Any] | None = None, *, interface: Any = None) -> Any:
        """Handle events from an ActiveX object.

        Args:
            source: An ActiveX object that emits events.
            sink: The object that handles the events. The `sink` must
                define methods with the same names as the ActiveX event names. If not
                specified, the [Application][msl.loadlib.activex.Application] instance
                is used as the `sink`.
            interface: The COM interface to use.

        Returns:
            An `_AdviseConnection` object from `comtypes`.
        """
        cxn = client.GetEvents(source, sink or self, interface=interface)
        self._event_connections.append(cxn)
        return cxn

    @property
    def hwnd(self) -> int:
        """[int][] &mdash; The handle to the main application window."""
        return self._hwnd

    def load(
        self,
        activex_id: str,
        *,
        parent: int | None = None,
        x: int = 0,
        y: int = 0,
        width: int = 0,
        height: int = 0,
        style: WindowStyle = WindowStyle.VISIBLE | WindowStyle.CHILD,
        ex_style: ExtendedWindowStyle = ExtendedWindowStyle.LEFT,
    ) -> Any:
        """Load an ActiveX library.

        Args:
            activex_id: ProgID or CLSID of the ActiveX object.
            parent: The handle to the parent window that the ActiveX object
                will belong to. Default is the main application window.
            x: Horizontal position of the ActiveX object in the parent window.
            y: Vertical position of the ActiveX object in the parent window.
            width: Width (in pixels) of the ActiveX object.
            height: Height (in pixels) of the ActiveX object.
            style: Style of the window that is created to contain the ActiveX
                object. Can be any combination (bitwise OR) of
                [WindowStyle][msl.loadlib.activex.WindowStyle] values.
            ex_style: Extended style of the window that is created to contain
                the ActiveX object. Can be any combination (bitwise OR) of
                [ExtendedWindowStyle][msl.loadlib.activex.ExtendedWindowStyle] values.

        Returns:
            The interface pointer to the ActiveX library.
        """
        if comtypes is None:
            msg = "comtypes must be installed to load an ActiveX library"
            raise OSError(msg)

        try:
            window_name = str(comtypes.GUID.from_progid(activex_id))
        except (TypeError, OSError):
            window_name = None

        if not window_name:
            msg = f"Cannot find an ActiveX library with ID {activex_id!r}"
            raise OSError(msg)

        if parent is None:
            parent = self._hwnd

        hwnd = _create_window(
            class_name="AtlAxWin",
            window_name=window_name,
            style=style,
            ex_style=ex_style,
            x=x,
            y=y,
            width=width,
            height=height,
            parent=parent,
            instance=kernel32.GetModuleHandleW(None),
        )

        unknown = ctypes.POINTER(comtypes.IUnknown)()
        ret = atl.AtlAxGetControl(hwnd, ctypes.byref(unknown))
        if ret != 0:
            msg = f"AtlAxGetControl {ctypes.WinError()}"
            raise OSError(msg)
        return client.GetBestInterface(unknown)

    @property
    def menu(self) -> Menu:
        """[Menu][msl.loadlib.activex.Menu] &mdash; The menu instance."""
        return self._menu

    @staticmethod
    def message_box(
        *,
        hwnd: int | None = None,
        language_id: int = 0,
        options: MessageBoxOption = MessageBoxOption.OK,
        text: str = "",
        title: str = "",
    ) -> int:
        """Display a modal dialog box.

        Args:
            hwnd: A handle to the owner window of the message box to be created.
            language_id: The language for the text displayed in the message box button(s).
            options: The contents and behaviour of the dialog box. Can be any combination
                (bitwise OR) of [MessageBoxOption][msl.loadlib.activex.MessageBoxOption] values.
            text: The message to be displayed.
            title: The dialog box title.

        Returns:
            An indication of how the message box was closed.
        """
        return user32.MessageBoxExW(hwnd, text, title, options, language_id)

    @staticmethod
    def run() -> None:
        """Run the application.

        This is a blocking call. Create and run the application in a separate
        thread if you want to execute other code while the application is running.
        """
        msg = wt.MSG()
        try:
            while user32.GetMessageW(msg, None, 0, 0) != 0:
                user32.TranslateMessage(msg)
                user32.DispatchMessageW(msg)
        except KeyboardInterrupt:
            pass

    def set_window_position(
        self, x: int, y: int, width: int, height: int, *, flags: WindowPosition = WindowPosition.NONE
    ) -> None:
        """Set the position of the main window.

        Args:
            x: The new position of the left side of the window.
            y: The new position of the top of the window.
            width: The new width (in pixels) of the window.
            height: The new height (in pixels) of the window.
            flags: The window sizing and positioning flags. Can be any combination
                (bitwise OR) of [WindowPosition][msl.loadlib.activex.WindowPosition] values.
        """
        user32.SetWindowPos(self._hwnd, None, x, y, width, height, flags)

    def set_window_size(self, width: int, height: int) -> None:
        """Set the size of the main window.

        Args:
            width: The new width (in pixels) of the window.
            height: The new height (in pixels) of the window.
        """
        # SWP_NOMOVE = 0x0002  Retains the current position (ignores X and Y parameters)
        self.set_window_position(0, 0, width, height, flags=0x0002)

    def set_window_title(self, title: str) -> None:
        """Set the text to display in the window's title bar.

        Args:
            title: The title bar text.
        """
        user32.SetWindowTextW(self._hwnd, title)

    def show(self, command: ShowWindow = ShowWindow.NORMAL) -> None:
        """Show the main application window.

        Args:
            command: Controls how the window is shown.
        """
        user32.SetMenu(self._hwnd, self._menu.hmenu)
        user32.ShowWindow(self._hwnd, command)
        user32.UpdateWindow(self._hwnd)

    @property
    def thread_id(self) -> int:
        """[int][] &mdash; The identifier of the thread that created the main application window."""
        return self._thread_id


# TypeAlias
Callback = Callable[[MenuItem], None]
"""[TypeAlias][typing.TypeAlias] for a callable object to handle a [MenuItem][msl.loadlib.activex.MenuItem] callback."""
