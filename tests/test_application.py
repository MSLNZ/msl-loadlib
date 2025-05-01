import sys

from msl.loadlib import activex

import pytest

from conftest import skipif_not_windows, IS_WINDOWS


def test_menu_item():
    mi = activex.MenuItem(hmenu=123, id=7, text="hello world", callback=None, flags=1, data=[-1, 0, 1])
    assert mi.hmenu == 123
    assert mi.id == 7
    assert mi.checked is False
    assert mi.text == "hello world"
    assert mi.callback is None
    assert mi.flags == 1
    assert mi == mi
    assert mi is mi
    assert str(mi) == "<MenuItem id=7 text='hello world'>"
    assert mi.data == [-1, 0, 1]

    mi2 = activex.MenuItem(hmenu=123, id=8, text="hello world", callback=None, flags=1, data=[-1, 0, 1])
    assert mi != mi2  # IDs do not match

    mi3 = activex.MenuItem(hmenu=-1, id=1, text="a", callback=None, flags=0, data=None)

    with pytest.raises(ValueError, match="A MenuItem must first be added to a Menu"):
        mi3.checked = True


def test_menu_group():
    mg = activex.MenuGroup()
    assert mg.name == ""
    assert mg.checked is None
    assert str(mg) == "<MenuGroup name='' size=0>"

    mg = activex.MenuGroup("click")
    a = mg.append("a")
    assert isinstance(a, activex.MenuItem)
    mg.append("b", data=8, flags=activex.MenuFlag.POPUP)
    mg.append_separator()
    mg.append("c", callback=None)
    assert mg.name == "click"
    assert mg.checked is None
    assert str(mg) == "<MenuGroup name='click' size=4>"

    for item in mg:
        assert isinstance(item, activex.MenuItem)
        assert item.checked is False

    for item in [a, None]:
        with pytest.raises(ValueError, match="A MenuGroup must first be added to a Menu"):
            mg.checked = item


@skipif_not_windows
def test_menu():
    m = activex.Menu()
    assert m.hmenu > 0

    h_file = m.create("File")
    assert h_file > 0

    new = m.append(h_file, "New", data=-1)
    assert isinstance(new, activex.MenuItem)
    assert m[new.id] is new
    assert new.id == 1
    assert new.text == "New"
    assert new.flags == activex.MenuFlag.STRING
    assert new.callback is None
    assert new.data == -1
    assert new.checked is False

    m.append_separator(h_file)

    h_settings = m.create("Settings")

    group = activex.MenuGroup("Alphabet")
    a = group.append("A", data="a")
    assert isinstance(a, activex.MenuItem)
    b = group.append("B")
    group.append_separator()
    c = group.append("C")

    m.append_group(h_settings, group)

    assert m[a.id] is a
    assert a.id == 3  # adding a separator (before creating 'Settings') increments the ID counter
    assert a.text == "A"
    assert a.flags == activex.MenuFlag.STRING
    assert a.callback is None
    assert a.data == "a"
    assert a.checked is False

    assert m[b.id] is b
    assert b.id == 4
    assert b.text == "B"
    assert b.data is None

    assert m[c.id] is c
    assert c.id == 6  # adding a separator (in the group) increments the ID counter
    assert c.text == "C"

    with pytest.raises(KeyError):
        _ = m[c.id + 1]

    assert group.checked is None
    assert a.checked is False
    assert b.checked is False
    assert c.checked is False

    group.checked = a
    assert group.checked is a
    assert a.checked is True
    assert b.checked is False
    assert c.checked is False

    group.checked = b
    assert group.checked is b
    assert a.checked is False
    assert b.checked is True
    assert c.checked is False

    group.checked = c
    assert group.checked is c
    assert a.checked is False
    assert b.checked is False
    assert c.checked is True

    group.checked = None
    assert group.checked is None
    assert a.checked is False
    assert b.checked is False
    assert c.checked is False


@pytest.mark.filterwarnings(pytest.PytestUnhandledThreadExceptionWarning)
@skipif_not_windows
def test_application():
    app = activex.Application()
    assert app.hwnd > 0
    assert app.thread_id > 0
    assert isinstance(app.menu, activex.Menu)
    app.set_window_position(10, 0, 100, 250)
    app.set_window_size(100, 100)
    app.set_window_title("new title")

    # ok to call close() multiple times
    app.close()
    app.close()
    app.close()
    app.close()


@pytest.mark.skipif(IS_WINDOWS, reason="do not test on Windows")
def test_application_raises():
    with pytest.raises(OSError, match="not supported on this platform"):
        activex.Application()


@skipif_not_windows
def test_icon():
    icon = activex.Icon("does not exist")
    assert str(icon) == "<Icon file='does not exist' index=0>"
    assert icon.hicon is None

    # ok to call destroy() multiple times
    icon.destroy()
    icon.destroy()
    icon.destroy()
    icon.destroy()

    with pytest.raises(ValueError, match="negative index"):
        activex.Icon("", index=-1)

    icon = activex.Icon(sys.executable)
    assert icon.hicon > 0
    icon.destroy()
