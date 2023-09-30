.. _refreeze:

=============================
Create a custom 32-bit server
=============================

If you want to create a custom 32-bit server, you will need

* a 32-bit version of Python (version 3.8 or later) installed
* `PyInstaller`_ installed in the 32-bit Python environment (ideally, you would
  use a :PEP:`virtual environment <405>` to install the necessary packages to
  create the server)

Some reasons why you may want to create a custom 32-bit server are that you want to

* run the server on a different version of Python,
* install a different version of comtypes or pythonnet (on Windows),
* install additional packages on the server (e.g., numpy, my_custom_package),
* embed your own data files in the frozen server

Using pip from a 32-bit Python interpreter, run

.. code-block:: console

   pip install msl-loadlib pyinstaller

You may want to install additional packages as well.

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
Create a script that calls the :func:`freeze_server32.main() <msl.loadlib.freeze_server32.main>`
function with the appropriate keyword arguments, for example,

.. code-block:: python

    from msl.loadlib import freeze_server32
    freeze_server32.main(packages='numpy')

and run your script using the 32-bit Python interpreter.

.. _refreeze-cli:

Using the CLI
-------------
When MSL-LoadLib is installed, a console script is included (named `freeze32`) that
may be executed from the command line to create a new frozen 32-bit server.

To see the help for `freeze32`, run

.. code-block:: console

   freeze32 --help

For example, if you want to include you own package and data files, you would run

.. code-block:: console

   freeze32 --packages my_package --data ./mydata/lib32.dll

.. _PyInstaller: https://www.pyinstaller.org/
