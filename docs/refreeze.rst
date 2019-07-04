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
   Server saved to: ...
   >>> exit()  # doctest: +SKIP

Specify the appropriate keyword arguments to the :func:`~msl.loadlib.freeze_server32.main` function.

Copy the ``server32-*`` file to the folder where you have MSL-LoadLib installed
in your 64-bit version of Python and replace the existing server file.

.. tip::

   You could also use pip to install MSL-LoadLib from the master branch of GitHub

   .. code-block:: console

      pip install https://github.com/MSLNZ/msl-loadlib/archive/master.zip

   This may require you to update your version of pip. Only install MSL-LoadLib in this
   way if you are creating a new server. The servers that are on GitHub are not necessarily
   synced with the rest of the code that is on GitHub. The updated servers are only uploaded
   to GitHub when a release is published.

Using the CLI
-------------

In this example we will clone the GitHub repository and create the server from the command line.
Make sure that invoking `python` on your terminal uses the 32-bit Python interpreter or specify
the full path to the 32-bit Python interpreter that you want to use.

.. code-block:: console

   git clone https://github.com/MSLNZ/msl-loadlib.git
   cd msl-loadlib/msl/loadlib
   python freeze_server32.py

Copy the ``server32-*`` file to the folder where you have MSL-LoadLib installed
in your 64-bit version of Python and replace the existing server file.

To see the help for the `freeze_server32.py` module run

.. code-block:: console

   python freeze_server32.py --help

For example, if you wanted to bypass the error that pythonnet is not installed run

.. code-block:: console

   python freeze_server32.py --ignore-pythonnet
