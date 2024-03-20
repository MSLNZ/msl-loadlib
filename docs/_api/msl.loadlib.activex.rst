msl.loadlib.activex module
==========================

.. automodule:: msl.loadlib.activex
   :exclude-members: WNDCLASSEXW, Background, ClassStyle, ExtendedWindowStyle, MenuFlag, MessageBoxOption, PositionFlag, ShowWindow, WindowStyle, Application, Icon, Menu, MenuItem, MenuGroup

Example usage,

.. code-block:: python

    import sys

    from msl.loadlib.activex import Application, Icon, MenuGroup, MenuItem

    def letter_clicked(item: MenuItem):
        print(item, item.data)
        if item.text == 'C':
            item.checked = not item.checked

    def group_clicked(item: MenuItem):
        group.checked = item
        print(item)

    # Create an application window
    app = Application(title='My ActiveX Control', icon=Icon(sys.executable))

    # Create a new 'Letters' menu
    letters = app.menu.create('Letters')

    # append items to the 'Letters' menu
    app.menu.append(letters, 'A')
    app.menu.append(letters, 'B', callback=letter_clicked, data=1)
    app.menu.append_separator(letters)
    app.menu.append(letters, 'C', callback=letter_clicked, data=[1, 2, 3])

    # Create a new menu group
    group = MenuGroup()
    group.append('Group 1', callback=group_clicked)
    group.append('Group 2', callback=group_clicked)
    group.append('Group 3', callback=group_clicked)

    # Create a new 'Numbers' menu
    numbers = app.menu.create('Numbers')
    # add the group to the 'Numbers' menu
    app.menu.append_group(numbers, group)
    # add a separator then another item
    app.menu.append_separator(numbers)
    app.menu.append(numbers, 'Not in Group')

    # Load an ActiveX control in the main application window
    # ocx = app.load('My.OCX.Application', width=300, height=300)

    app.set_window_size(300, 300)

    app.show()
    app.run()


.. _activex_classes:

Classes
-------
* :class:`~msl.loadlib.activex.Application`
* :class:`~msl.loadlib.activex.Icon`
* :class:`~msl.loadlib.activex.Menu`
* :class:`~msl.loadlib.activex.MenuItem`
* :class:`~msl.loadlib.activex.MenuGroup`

.. autoclass:: msl.loadlib.activex.Application
.. autoclass:: msl.loadlib.activex.Icon
.. autoclass:: msl.loadlib.activex.Menu
.. autoclass:: msl.loadlib.activex.MenuItem
.. autoclass:: msl.loadlib.activex.MenuGroup

.. _activex_enumerations:

Enumerations
------------
* :class:`~msl.loadlib.activex.Background`
* :class:`~msl.loadlib.activex.ClassStyle`
* :class:`~msl.loadlib.activex.ExtendedWindowStyle`
* :class:`~msl.loadlib.activex.MenuFlag`
* :class:`~msl.loadlib.activex.MessageBoxOption`
* :class:`~msl.loadlib.activex.PositionFlag`
* :class:`~msl.loadlib.activex.ShowWindow`
* :class:`~msl.loadlib.activex.WindowStyle`

.. autointenum:: msl.loadlib.activex.Background

.. autointenum:: msl.loadlib.activex.ClassStyle
   :hex: 5

.. autointenum:: msl.loadlib.activex.ExtendedWindowStyle
   :hex: 7

.. autointenum:: msl.loadlib.activex.MenuFlag
   :hex: 3

.. autointenum:: msl.loadlib.activex.MessageBoxOption
   :hex: 6

.. autointenum:: msl.loadlib.activex.PositionFlag
   :hex: 4

.. autointenum:: msl.loadlib.activex.ShowWindow

.. autointenum:: msl.loadlib.activex.WindowStyle
   :hex: 8
