import sys

import pytest

from conftest import IS_WINDOWS, skipif_not_windows
from msl.loadlib import activex


def test_menu_item() -> None:
    mi = activex.MenuItem(hmenu=-1, text="hello world", callback=None, flags=1, data=[-1, 0, 1])
    assert mi.id >= 0
    assert mi.checked is False

    assert mi.hmenu == -1
    assert mi.text == "hello world"
    assert mi.callback is None
    assert mi.flags == 1
    assert mi == mi  # noqa: PLR0124
    assert mi is mi  # noqa: PLR0124
    assert mi.data == [-1, 0, 1]
    mi.data = 8
    assert mi.data == 8
    assert str(mi) == "<MenuItem id=0, text='hello world', checked=False, data=8>"
    assert hash(mi) == hash(mi.id)

    mi2 = activex.MenuItem(hmenu=-1, text="hello world", callback=None, flags=1, data=8)
    assert mi2.id == mi.id + 1
    assert mi != mi2  # IDs do not match

    mi3 = activex.MenuItem(hmenu=-1, text="a", callback=None, flags=0, data=None)
    assert mi3.id == mi.id + 2
    assert mi != mi3  # IDs do not match
    with pytest.raises(ValueError, match=r"A MenuItem must first be added to a Menu"):
        mi3.checked = True


def test_menu_group() -> None:
    mg = activex.MenuGroup()
    assert mg.name == ""
    assert mg.checked is None
    assert str(mg) == "<MenuGroup name='' (0 items)>"

    mg = activex.MenuGroup("click")
    a = mg.append("a")
    assert isinstance(a, activex.MenuItem)
    assert str(mg) == "<MenuGroup name='click' (1 item)>"
    b = mg.append("b", data=8, flags=activex.MenuFlag.POPUP)
    mg.append_separator()
    mg.append_separator()
    c = mg.append("c", callback=None)
    assert mg.name == "click"
    assert mg.checked is None

    # separator's are not considered as items
    assert str(mg) == "<MenuGroup name='click' (3 items)>"
    assert len(mg) == 3

    for item in mg:
        assert isinstance(item, activex.MenuItem)
        assert item.checked is False
        assert item.flags != activex.MenuFlag.SEPARATOR

    assert mg[0] == a
    assert mg[1] == b
    assert mg[2] == c

    with pytest.raises(ValueError, match=r"A MenuGroup must first be added to a Menu"):
        mg.checked = None

    with pytest.raises(ValueError, match=r"A MenuGroup must first be added to a Menu"):
        mg.checked = a

    with pytest.raises(IndexError):
        _ = mg[3]


@skipif_not_windows
def test_menu() -> None:  # noqa: PLR0915
    m = activex.Menu()
    assert m.hmenu > 0

    h_file = m.create("File")
    assert h_file > 0

    new = m.append(h_file, "New", data=-1)
    assert isinstance(new, activex.MenuItem)
    assert new.text == "New"
    assert new.flags == activex.MenuFlag.STRING
    assert new.callback is None
    assert new.data == -1
    assert new.checked is False

    m.append_separator(h_file)

    h_settings = m.create("Settings")
    assert h_settings > 0

    group = activex.MenuGroup("Alphabet")
    a = group.append("A", data="a")
    assert isinstance(a, activex.MenuItem)
    b = group.append("B")
    group.append_separator()
    c = group.append("C")

    with pytest.raises(ValueError, match=r"A MenuItem must first be added to a Menu"):
        c.checked = True
    with pytest.raises(ValueError, match=r"A MenuGroup must first be added to a Menu"):
        group.checked = c

    m.append_group(h_settings, group)

    assert a.text == "A"
    assert a.flags == activex.MenuFlag.STRING
    assert a.callback is None
    assert a.data == "a"
    assert a.checked is False

    assert b.text == "B"
    assert b.data is None

    assert c.text == "C"

    assert group.checked is None
    assert a.checked is False
    assert b.checked is False
    assert c.checked is False

    group.checked = a
    assert group.checked is a
    assert a.checked is True
    assert b.checked is False  # type: ignore[unreachable]
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


@skipif_not_windows
def test_application() -> None:
    app = activex.Application()
    assert app.hwnd > 0
    assert app.thread_id > 0
    assert isinstance(app.menu, activex.Menu)
    app.set_window_position(10, 0, 100, 250)
    app.set_window_size(100, 100)
    app.set_window_title("new title")
    app.unhandle_events()

    with pytest.raises(AttributeError, match=r"disconnect"):
        app.unhandle_events(None)

    # ok to call close() multiple times
    app.close()
    app.close()
    app.close()
    app.close()


@pytest.mark.skipif(IS_WINDOWS, reason="do not test on Windows")
def test_application_raises() -> None:
    with pytest.raises(OSError, match="not supported on this platform"):
        _ = activex.Application()


@skipif_not_windows
def test_icon() -> None:
    icon = activex.Icon("does not exist")
    assert str(icon) == "<Icon file='does not exist', index=0>"
    assert icon.hicon is None

    # ok to call destroy() multiple times
    icon.destroy()
    icon.destroy()
    icon.destroy()
    icon.destroy()

    with pytest.raises(ValueError, match="negative index"):
        _ = activex.Icon("", index=-1)

    icon = activex.Icon(sys.executable)
    assert icon.hicon is not None
    assert icon.hicon > 0
    icon.destroy()


def test_menu_group_added_early() -> None:
    mg = activex.MenuGroup()
    first = mg.append("first", data=1)
    assert mg.hmenu == -1
    assert first.hmenu == -1

    menu = activex.Menu()
    handle = menu.create("Text")
    assert handle > 0

    with pytest.raises(ValueError, match=r"A MenuItem must first be added to a Menu"):
        first.checked = True
    with pytest.raises(ValueError, match=r"A MenuGroup must first be added to a Menu"):
        mg.checked = first

    menu.append_group(handle, mg)
    assert mg.hmenu == handle

    assert mg.checked is None

    second = mg.append("second", data=2)
    assert second.hmenu == handle

    mg.checked = first
    assert mg.checked is first
    assert first.checked
    assert not second.checked
