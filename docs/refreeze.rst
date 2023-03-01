.. _refreeze:

==============================
Re-freezing the 32-bit server
==============================

If you want to make your own 32-bit server you will need

1) a 32-bit version of Python 2.7 or 3.5+ (whatever version you want)
2) `PyInstaller <https://www.pyinstaller.org/>`_

Using pip from the 32-bit Python interpreter run

.. code-block:: console

   pip install msl-loadlib pyinstaller

.. note::

   If you want to include additional packages, for example,
   pythonnet, comtypes, numpy, etc. run

    .. code-block:: console

       pip install pythonnet comtypes numpy

You have two options to create the 32-bit server

1) :ref:`refreeze-api`

2) :ref:`refreeze-cli`

and you have two options to use the newly-created server

1. Copy the ``server32-*`` file to the ``../site-packages/msl/loadlib`` directory
where you have MSL-LoadLib installed in your 64-bit version of Python to replace
the existing server file.

2. Specify the directory where the ``server32-*`` file is located as the value
of the ``server32_dir`` keyword argument in :class:`~msl.loadlib.client64.Client64`.

.. _refreeze-api:

Using the API
-------------
Launch an Interactive Console using the 32-bit Python interpreter

.. code-block:: console

   python

and enter

.. code-block:: pycon

   >>> from msl.loadlib import freeze_server32
   >>> freeze_server32.main()  # doctest: +SKIP
   ... PyInstaller logging messages ...
   Server saved to ...

Specify the appropriate keyword arguments to the
:func:`~msl.loadlib.freeze_server32.main` function.

.. _refreeze-cli:

Using the CLI
-------------
In this example, the GitHub repository is cloned and the server is created from
the command line. Make sure that invoking `python` on your terminal uses the
32-bit Python interpreter or specify the full path to the 32-bit Python interpreter
that you want to use.

.. code-block:: console

   git clone https://github.com/MSLNZ/msl-loadlib.git
   cd msl-loadlib/msl/loadlib
   python freeze_server32.py

To see the help for the `freeze_server32.py` module run

.. code-block:: console

   python freeze_server32.py --help

For example, if you wanted to bypass the error that pythonnet is not installed run

.. code-block:: console

   python freeze_server32.py --ignore-pythonnet
