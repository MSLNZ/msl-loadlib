# ActiveX {: #direct-activex }

The following runnable example shows how to create a main window that (could) contain [ActiveX]{:target="_blank"} controls and how to create a menubar in the application to handle callbacks. This example is only valid on Windows and requires [comtypes]{:target="_blank"} to be installed.

```python
from __future__ import annotations

import sys

from msl.loadlib.activex import Application, Icon, MenuGroup, MenuItem


def letter_clicked(item: MenuItem) -> None:
    """A callback function. You could interact with the `ocx` object."""
    print(item, item.data)
    if item.text == "C":
        item.checked = not item.checked


def group_clicked(item: MenuItem) -> None:
    """A callback function. You could interact with the `ocx` object."""
    print(item)
    group.checked = item


# Create an application window
app = Application(title="My ActiveX Control", icon=Icon(sys.executable))

# Create a new 'Letters' menu
letters = app.menu.create("Letters")

# Append items to the 'Letters' menu
app.menu.append(letters, "A")
app.menu.append(letters, "B", callback=letter_clicked, data=1)
app.menu.append_separator(letters)
app.menu.append(letters, "C", callback=letter_clicked, data=[1, 2, 3])

# Create a new menu group
group = MenuGroup()
group.append("Group 1", callback=group_clicked)
group.append("Group 2", callback=group_clicked)
group.append("Group 3", callback=group_clicked)

# Create a new 'Numbers' menu
numbers = app.menu.create("Numbers")
# Add the group to the 'Numbers' menu
app.menu.append_group(numbers, group)
# Add a separator then another item
app.menu.append_separator(numbers)
app.menu.append(numbers, "Not in Group")

# Define the size of the main application window
width = 300
height = 300

# Uncomment the next line to load an ActiveX control in the main application window
# ocx = app.load("My.OCX.Application", width=width, height=height)

app.set_window_size(width, height)
app.show()

# Calling `app.run` is a blocking call. You may not want to call it yet
# (or at all) and interact with the `ocx` object. It is shown here to keep
# the window open until it is manually closed.
app.run()
```

[ActiveX]: https://learn.microsoft.com/en-us/windows/win32/com/activex-controls
[comtypes]: https://comtypes.readthedocs.io/en/stable/index.html
