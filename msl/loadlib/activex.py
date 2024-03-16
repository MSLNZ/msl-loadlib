"""
Helper module for loading an ActiveX library in an application window.
"""
from __future__ import annotations

import ctypes
from ctypes import wintypes as wt
from enum import IntEnum
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


class Background(IntEnum):
    """Background colours."""
    WHITE = 0
    LIGHT_GRAY = 1
    GRAY = 2
    DARK_GRAY = 3
    BLACK = 4


class ClassStyle(IntEnum):
    """Window class styles. See
    `window-class-styles <https://learn.microsoft.com/en-us/windows/win32/winmsg/window-class-styles#constants>`_
    for more details."""
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


class ExtendedWindowStyle(IntEnum):
    """Extended window styles. See
    `extended-window-styles <https://learn.microsoft.com/en-us/windows/win32/winmsg/extended-window-styles>`_
    for more details."""
    NONE = 0
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


class Icon(IntEnum):
    """Standard icons. See
    `about-icons <https://learn.microsoft.com/en-us/windows/win32/menurc/about-icons>`_
    for more details."""
    APPLICATION = 32512
    ERROR = 32513
    QUESTION = 32514
    WARNING = 32515
    INFORMATION = 32516
    WINLOGO = 32517
    SHIELD = 32518


class MenuFlag(IntEnum):
    """Menu item flags. See
    `append-menu <https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-appendmenuw>`_
    for more details."""
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


class MessageBoxOption(IntEnum):
    """Message box options. See
    `message-box <https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-messagebox>`_
    for more details."""
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


class PositionFlag(IntEnum):
    """Window position options. See
    `set-window-pos <https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowpos>`_
    for more details."""
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
    """Show window commands. See
    `show-window <https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindow>`_
    for more details."""
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


class WindowStyle(IntEnum):
    """Window styles. See
    `window-styles <https://learn.microsoft.com/en-us/windows/win32/winmsg/window-styles>`_
    for more details."""
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

    WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM)

    class WNDCLASSEXW(ctypes.Structure):
        _fields_ = [
            ('cbSize', wt.UINT),
            ('style', wt.UINT),
            ('lpfnWndProc', WNDPROC),
            ('cbClsExtra', ctypes.c_int),
            ('cbWndExtra', ctypes.c_int),
            ('hInstance', wt.HINSTANCE),
            ('hIcon', wt.HICON),
            ('hCursor', wt.HANDLE),
            ('hbrBackground', wt.HBRUSH),
            ('lpszMenuName', wt.LPCWSTR),
            ('lpszClassName', wt.LPCWSTR),
            ('hIconSm', wt.HICON),
        ]

    user32.CreateWindowExW.errcheck = _err_check
    user32.CreateWindowExW.restype = wt.HWND
    user32.CreateWindowExW.argtypes = [
        wt.DWORD,      # dwExStyle
        wt.LPCWSTR,    # lpClassName
        wt.LPCWSTR,    # lpWindowName
        wt.DWORD,      # dwStyle
        ctypes.c_int,  # X
        ctypes.c_int,  # Y
        ctypes.c_int,  # nWidth
        ctypes.c_int,  # nHeight
        wt.HWND,       # hWndParent
        wt.HMENU,      # hMenu
        wt.HINSTANCE,  # hInstance
        wt.LPVOID      # lpParam
    ]

    user32.SetWindowTextW.errcheck = _err_check
    user32.SetWindowTextW.restype = ctypes.c_bool
    user32.SetWindowTextW.argtypes = [wt.HWND, wt.LPCWSTR]

    user32.SetWindowPos.errcheck = _err_check
    user32.SetWindowPos.restype = ctypes.c_bool
    user32.SetWindowPos.argtypes = [
        wt.HWND,       # hWnd
        wt.HWND,       # hWndInsertAfter
        ctypes.c_int,  # X
        ctypes.c_int,  # Y
        ctypes.c_int,  # cx
        ctypes.c_int,  # cy
        wt.UINT        # uFlags
    ]

    user32.AppendMenuW.errcheck = _err_check
    user32.AppendMenuW.restype = ctypes.c_bool
    user32.AppendMenuW.argtypes = [wt.HMENU, wt.UINT, wt.UINT, wt.LPCWSTR]

    user32.CheckMenuItem.restype = ctypes.c_int
    user32.CheckMenuItem.argtypes = [wt.HMENU, wt.UINT, wt.UINT]

    user32.MessageBoxExW.restype = ctypes.c_int
    user32.MessageBoxExW.argtypes = [wt.HWND, wt.LPCWSTR, wt.LPCWSTR, wt.UINT, wt.WORD]

    user32.DefWindowProcW.restype = LRESULT
    user32.DefWindowProcW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]

    user32.DestroyMenu.restype = ctypes.c_bool
    user32.DestroyMenu.argtypes = [wt.HMENU]

    user32.RegisterClassExW.restype = wt.ATOM
    user32.RegisterClassExW.argtypes = [ctypes.POINTER(WNDCLASSEXW)]

    user32.UnregisterClassW.restype = ctypes.c_bool
    user32.UnregisterClassW.argtypes = [wt.LPCWSTR, wt.HINSTANCE]

except AttributeError:
    kernel32 = user32 = atl = gdi32 = WNDCLASSEXW = None


CW_USEDEFAULT = 0x80000000


def _create_window(*,
                   ex_style: int = 0,
                   class_name: str = '',
                   window_name: str = '',
                   style: int = 0,
                   x: int = CW_USEDEFAULT,
                   y: int = CW_USEDEFAULT,
                   width: int = CW_USEDEFAULT,
                   height: int = CW_USEDEFAULT,
                   parent: int = None,
                   menu: int = None,
                   instance: int = None,
                   param: int = None) -> int:
    """Create a new Window and return the handle."""
    return user32.CreateWindowExW(ex_style, class_name, window_name,
                                  style, x, y, width, height, parent,
                                  menu, instance, param)


class MenuItem:

    def __init__(self, **kwargs) -> None:
        """A menu item that belongs to a popup menu."""
        self._hmenu: int = kwargs['hmenu']
        self._id: int = kwargs['id']
        self._text: str = kwargs['text']
        self._callback: Callback | None = kwargs['callback']
        self._flags: int = kwargs['flags']
        self._checked = False

        self.data: Any = kwargs['data']
        """User data associated with the menu item."""

    def __eq__(self, other: MenuItem) -> bool:
        return self.id == other.id

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} id={self._id} text={self._text!r}>'

    @property
    def callback(self) -> Callback | None:
        """The callback function to call when the menu item is clicked."""
        return self._callback

    @property
    def checked(self) -> bool:
        """Whether the menu item's check mark is shown."""
        return self._checked

    @checked.setter
    def checked(self, value: bool) -> None:
        """Set the checked state of the menu item."""
        # MF_CHECKED=8, MF_UNCHECKED=0
        state = 8 if value else 0
        previous = user32.CheckMenuItem(self._hmenu, self._id, state)
        if previous == -1:
            raise ctypes.WinError()
        self._checked = bool(value)

    @property
    def flags(self) -> int:
        """The flags that were used to create the menu item."""
        return self._flags

    @property
    def hmenu(self) -> int:
        """The handle to the popup menu that the menu item belongs to."""
        return self._hmenu

    @property
    def id(self) -> int:
        """The identifier of the menu item."""
        return self._id

    @property
    def text(self) -> str:
        """The content of the menu item."""
        return self._text


class MenuGroup:

    def __init__(self, name: str = '') -> None:
        """A group of :class:`.MenuItem`\\'s where only one item may be selected at a time."""
        self._name = name
        self._items: list[MenuItem] = []

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} name={self._name!r} size={len(self._items)}>'

    def __iter__(self) -> Iterator[MenuItem]:
        return iter(self._items)

    def append(self,
               text: str,
               *,
               callback: Callback | None = None,
               data: Any = None,
               flags: int = MenuFlag.STRING) -> MenuItem:
        """Create a new :class:`.MenuItem` and append it to the group.

        :param text: The content of the new menu item.
        :param callback: A callable object that will be called when this menu
            item is selected. The callable object will receive the :class:`.MenuItem`
            instance as an argument and the returned object is ignored.
        :param data: User data associated with the menu item.
        :param flags: Controls the appearance and behaviour of the new menu item.

        :return: The menu item that was appended to the group.
        """
        item = MenuItem(hmenu=-1, text=text, callback=callback,
                        id=-1, flags=flags, data=data)
        self._items.append(item)
        return item

    @property
    def checked(self) -> MenuItem | None:
        """Returns the menu item that is currently checked in the group."""
        for item in self:
            if item.checked:
                return item

    @checked.setter
    def checked(self, item: MenuItem) -> None:
        """Sets the menu item that is currently checked in the group."""
        for i in self:
            i.checked = i == item

    @property
    def name(self) -> str:
        """Returns the name of the menu group."""
        return self._name


# TypeAlias
Callback = Callable[[MenuItem], None]


class Menu:

    def __init__(self) -> None:
        """A menu associated with the main application window."""
        self._id = 0
        self._items: dict[int, MenuItem] = {}
        self._hmenu: int = user32.CreateMenu()

    def __getitem__(self, item: int) -> MenuItem:
        return self._items[item]

    def append(self,
               hmenu: int,
               text: str,
               *,
               callback: Callback | None = None,
               data: Any = None,
               flags: int = MenuFlag.STRING) -> MenuItem:
        """Create and append a menu item to a popup menu.

        :param hmenu: The handle of a popup menu to append the new menu item to.
        :param text: The content of the new menu item.
        :param callback: A callable object that will be called when this menu
            item is selected. The callable object will receive the :class:`.MenuItem`
            instance as an argument and the returned object is ignored.
        :param data: User data associated with the menu item.
        :param flags: Controls the appearance and behaviour of the new menu item.

        :return: The menu item that was appended.
        """
        self._id += 1
        user32.AppendMenuW(hmenu, flags, self._id, text)
        item = MenuItem(hmenu=hmenu, text=text, callback=callback,
                        id=self._id, flags=flags, data=data)
        self._items[self._id] = item
        return item

    def append_group(self, hmenu: int, menu_group: MenuGroup) -> None:
        """Append a group of menu items to a popup menu.

        :param hmenu: The handle of a popup menu to append the group to.
        :param menu_group: A group of menu items.
        """
        for item in menu_group:
            self._id += 1
            item._hmenu = hmenu
            item._id = self._id
            user32.AppendMenuW(hmenu, item.flags, self._id, item.text)
            self._items[self._id] = item

    def append_separator(self, hmenu: int) -> None:
        """Append a horizontal dividing line to a popup menu.

        :param hmenu: The handle to a popup menu.
        """
        self._id += 1
        user32.AppendMenuW(hmenu, MenuFlag.SEPARATOR, self._id, None)

    def create(self, text: str) -> int:
        """Create a new popup menu and append it to the main menu.

        :param text: The text to display for the popup menu.

        :return: The handle to the popup menu that was created.
        """
        flags = MenuFlag.STRING | MenuFlag.POPUP
        h: int = user32.CreatePopupMenu()
        user32.AppendMenuW(self._hmenu, flags, h, text)
        return h

    @property
    def hmenu(self) -> int:
        """Returns the handle to the main menu."""
        return self._hmenu


class Application:

    def __init__(self,
                 *,
                 background: int = Background.WHITE,
                 class_style: int = ClassStyle.NONE,
                 icon: int = Icon.APPLICATION,
                 style: int = WindowStyle.OVERLAPPEDWINDOW,
                 title: str = 'ActiveX') -> None:
        """Create the main application window to display ActiveX controls.

        :param background: The background colour of the main window.
        :param class_style: The class style(s). Can be any combination (bitwise OR)
            of the :class:`.ClassStyle` values.
        :param icon: The application icon.
        :param style: The window style(s). Can be any combination (bitwise OR)
            of the :class:`.WindowStyle` values.
        :param title: The text to display in the titlebar (if one is visible).
        """
        super().__init__()
        self._atom = None
        self._event_connections = []
        self._msg_handlers: list[Callable[[int, int, int, int], None]] = []

        if WNDCLASSEXW is None:
            raise OSError('An ActiveX application is not supported on this platform')

        self._window = WNDCLASSEXW()
        self._window.cbSize = ctypes.sizeof(WNDCLASSEXW)
        self._window.style = class_style
        self._window.lpfnWndProc = WNDPROC(self._window_procedure)
        self._window.cbClsExtra = 0
        self._window.cbWndExtra = 0
        self._window.hInstance = kernel32.GetModuleHandleW(None)
        self._window.hIcon = user32.LoadIconW(None, wt.LPCWSTR(icon))
        self._window.hCursor = user32.LoadCursorW(None, wt.LPCWSTR(32512))  # IDC_ARROW
        self._window.hbrBackground = gdi32.GetStockObject(background)
        self._window.lpszMenuName = f'ActiveXMenu{id(self._window)}'  # make the name unique
        self._window.lpszClassName = f'ActiveXClass{id(self._window)}'
        self._window.hIconSm = user32.LoadIconW(None, wt.LPCWSTR(icon))

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
            raise OSError('Cannot register the "AtlAxWin" window class')

    def __del__(self) -> None:
        for ec in self._event_connections:
            ec.disconnect()
        self._event_connections.clear()

        if self._atom is not None:
            user32.UnregisterClassW(self._window.lpszClassName, self._window.hInstance)
            self._atom = None

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

        :param handler: A function that processes messages sent to a window.
            The function must accept four positional arguments (all integer
            values) and the returned object is ignored. See
            `window-procedure <https://learn.microsoft.com/en-us/windows/win32/learnwin32/writing-the-window-procedure>`_
            for more details about the input arguments to the `handler`.
        """
        self._msg_handlers.append(handler)

    def close(self) -> None:
        """Close the application."""
        user32.PostMessageW(self._hwnd, WM_DESTROY, 0, 0)

    def handle_events(self,
                      source: Any,
                      sink: Callable[..., Any] = None,
                      *,
                      interface: Any = None):
        """Handle events from an ActiveX object.

        :param source: An ActiveX object that emits events.
        :param sink: The object that handles the events. The `sink` must
            define methods with the same names as the ActiveX event names. If not
            specified, the :class:`.Application` instance is used as the `sink`.
        :param interface: The interface to use.

        :return: The advise-connection object.
        """
        cxn = client.GetEvents(source, sink or self, interface=interface)
        self._event_connections.append(cxn)
        return cxn

    @property
    def hwnd(self) -> int:
        """Returns the handle to the main application window."""
        return self._hwnd

    def load(self,
             activex_id: str,
             *,
             parent: int = None,
             x: int = 0,
             y: int = 0,
             width: int = 0,
             height: int = 0,
             style: int = WindowStyle.VISIBLE | WindowStyle.CHILD,
             ex_style: int = ExtendedWindowStyle.NONE) -> ctypes.POINTER:
        """Load an ActiveX library.

        :param activex_id: ProgID or CLSID of the ActiveX object.
        :param parent: The handle to the parent window that the ActiveX object
            will belong to.
        :param x: Horizontal position of the ActiveX object in the parent window.
        :param y: Vertical position of the ActiveX object in the parent window.
        :param width: Width (in pixels) of the ActiveX object.
        :param height: Height (in pixels) of the ActiveX object.
        :param style: Style of the window that is created to contain the ActiveX
            object. A combination (bitwise OR) of :class:`.WindowStyle` values.
        :param ex_style: Extended style of the window that is created to contain
            the ActiveX object. A combination (bitwise OR) of
            :class:`.ExtendedWindowStyle` values.

        :return: The interface pointer to the ActiveX library.
        """
        if comtypes is None:
            raise OSError('comtypes must be installed to load an ActiveX library')

        if parent is None:
            parent = self._hwnd

        try:
            window_name = str(comtypes.GUID.from_progid(activex_id))
        except (TypeError, OSError):
            window_name = None

        if not window_name:
            raise OSError(f'Cannot find an ActiveX library with ID {activex_id!r}')

        hwnd = _create_window(
            class_name='AtlAxWin',
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
            raise OSError(f'AtlAxGetControl {ctypes.WinError()}')
        return client.GetBestInterface(unknown)

    @property
    def menu(self) -> Menu:
        """Returns the menu instance."""
        return self._menu

    @staticmethod
    def message_box(*,
                    hwnd: int = None,
                    language_id: int = 0,
                    options: int = MessageBoxOption.OK,
                    text: str = '',
                    title: str = '') -> int:
        """Displays a modal dialog box.

        :param hwnd: A handle to the owner window of the message box to be created.
        :param language_id: The language for the text displayed in the message box
            button(s).
        :param options: The contents and behavior of the dialog box. A combination
            (bitwise OR) of :class:`.MessageBoxOption` values.
        :param text: The message to be displayed.
        :param title: The dialog box title.

        :return: An indication of how the message box was closed.
        """
        return user32.MessageBoxExW(hwnd, text, title, options, language_id)

    @staticmethod
    def run() -> None:
        """Run the application.

        This is a blocking call. Create and run the application in a separate
        thread if you want to execute other code while the application is running.
        """
        byref = ctypes.byref
        msg = wt.MSG()
        try:
            while user32.GetMessageW(byref(msg), None, 0, 0) != 0:
                user32.TranslateMessage(byref(msg))
                user32.DispatchMessageW(byref(msg))
        except KeyboardInterrupt:
            pass

    def set_window_position(self,
                            x: int,
                            y: int,
                            width: int,
                            height: int,
                            *,
                            flags: int = PositionFlag.NONE) -> None:
        """Set the position of the main window.

        :param x: The new position of the left side of the window.
        :param y: The new position of the top of the window.
        :param width: The new width of the window (in pixels).
        :param height: The new height of the window (in pixels).
        :param flags: The window sizing and positioning flags. A combination
            (bitwise OR) of :class:`.PositionFlag` values.
        """
        user32.SetWindowPos(self._hwnd, None, x, y, width, height, flags)

    def set_window_size(self, width: int, height: int) -> None:
        """Set the size of the main window.

        :param width: The new width of the window (in pixels).
        :param height: The new height of the window (in pixels).
        """
        # SWP_NOMOVE = 0x0002  Retains the current position (ignores X and Y parameters)
        self.set_window_position(0, 0, width, height, flags=0x0002)

    def set_window_title(self, title: str) -> None:
        """Set the text to display in the window's title bar."""
        user32.SetWindowTextW(self._hwnd, title)

    def show(self, command: int = ShowWindow.NORMAL) -> None:
        """Show the main application window.

        :param command: Controls how the window is shown
            (a :class:`.ShowWindow` value).
        """
        user32.SetMenu(self._hwnd, self._menu.hmenu)
        user32.ShowWindow(self._hwnd, command)
        user32.UpdateWindow(self._hwnd)

    @property
    def thread_id(self) -> int:
        """Returns the identifier of the thread that created the
        main application window."""
        return self._thread_id
