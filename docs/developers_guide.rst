================
Developers Guide
================
This guide shows you how to:

* `Install Python, Git and PyCharm`_
* `Commit changes to the repository`_
* `Execute setup.py commands`_
* `Edit the code using the style guide`_

If you are familiar with setting up a Python environment and cloning a repository then you can access
the **MSL-LoadLib** repository `here <repo_>`_.

.. _Install Python, Git and PyCharm:

Install Python, Git and PyCharm
-------------------------------
This section describes *one way* to set up a Python environment in order to contribute to **MSL-LoadLib** [#f1]_.

.. note::
   The following instructions are only valid for a Windows x64 operating system.

1. Download a 64-bit version of Miniconda_.

2. Install Miniconda_ in a folder of your choice, but make sure to **Add** and **Register** Anaconda.

   .. image:: _static/anaconda_setup.png

3. Open a `Windows Command Prompt`_ and update all Miniconda_ packages::

   $ conda update --yes --all

4. It is usually best to create a new `virtual environment`_ for each Python project that you are working on to avoid
   possible conflicts between the packages that are required for each Python project or to test the code against
   different versions of Python (i.e., it solves the "Project X depends on version 1.x but Project Y depends on
   version 4.x" dilemma).

   Create a new **msl** `virtual environment`_ (you can pick another name, **msl** is just an example of a name) and
   install the latest Python interpreter in this environment::

      $ conda create --yes --name msl python

   You may also want to create a new `virtual environment`_ so that you can test the code against another Python
   version. For example, here is an example of how to create a Python 2.7 `virtual environment`_::

      $ conda create --yes --name msl27 python=2.7

5. Create a GitHub_ account *(if you do not already have one)*.

6. Download and install git_ *(accept the default settings)*. This program is used as the `version control system`_.

7. Download and install the `Community Edition of PyCharm`_ to use as an IDE_. This IDE_ is free to use and it provides
   a lot of the features that one expects from an IDE_. When asked to **Create associations** check the **.py** checkbox
   *(you can accept the default settings for everything else that you are asked during the installation)*.

   .. image:: _static/pycharm_installation1.png

8. Run PyCharm and perform the following:

   a) Do not import settings from a previous version of PyCharm *(unless you have a settings file that you want to use)*.

      .. image:: _static/pycharm_installation2.png

   b) You can keep the default editor theme *(or select the one that you like; note: you can change the theme later)*.
    
      .. image:: _static/pycharm_installation3.png

   c) Select the **GitHub** option from **Check out from Version Control**.

      .. image:: _static/pycharm_github_checkout.png

   d) Enter your GitHub_ account information *(see step 5 above)* and click **Login**.

      .. image:: _static/pycharm_github_login.png

   e) Clone the **MSL-LoadLib** `repository <repo_>`_. You will have to change the path of the **Parent Directory**
      and you can choose the **Directory Name** to be any text that you want.

      .. image:: _static/pycharm_github_clone.png

   f) Open the `repository <repo_>`_ in PyCharm.

      .. image:: _static/pycharm_github_open.png

9. Specify the Python executable in the **msl** `virtual environment`_ as the **Project Interpreter**.
   
   a) Press **CTRL + ALT + S** to open the **Settings** window.
   
   b) Go to **Project Interpreter** and click on the button in the top-right corner. 

      .. image:: _static/pycharm_interpreter1.png
   
   c) Select **Add Local**
    
      .. image:: _static/pycharm_interpreter2.png
      
   d) Navigate to the folder where the **msl** `virtual environment`_ is located (e.g., path\\to\\Miniconda\\envs\\msl),
      select the **python.exe** file and then click **OK**.
   
      .. image:: _static/pycharm_interpreter3.png

   e) Click **Apply** then **OK**.

   f) If you created a **msl27** `virtual environment`_ then repeat *step (d)* to add the Python 2.7 executable.

10. The **MSL-LoadLib** project is now shown in the **Project** window and you can begin to modify the code.

.. _Commit changes to the repository:

Commit changes to the repository
--------------------------------
The following is only a very basic example of how to upload changes to the source code to the `repository <repo_>`_
by using PyCharm. See `this link <githelp_>`_ for a much more detailed tutorial on how to use git.

.. note::
   This section assumes that you followed the instructions from `Install Python, Git and PyCharm`_.

1. Make sure that the git **Branch** you are working on is up to date by performing a **Pull**.

   a) Click on the :abbr:`VCS (Version Control Software)` *downward-arrow button* in the top-right corner.

      .. image:: _static/pycharm_github_pull_1.png

   b) Select the options for how you want to update the project *(the default options are usually okay)* and click
      **OK**.

      .. image:: _static/pycharm_github_pull_2.png

2. Make changes to the code ...

3. When you are happy with the changes that you have made you should **Push** the changes to the `repository <repo_>`_.

   a) Click on the :abbr:`VCS (Version Control Software)` *upward-arrow button* in the top-right corner.
   
      .. image:: _static/pycharm_github_commit1.png

   b) Select the file(s) that you want to upload to the `repository <repo_>`_, add a useful message for the commit and
      then select **Commit and Push**.

      .. image:: _static/pycharm_github_commit2.png

   c) Finally, **Push** the changes to the `repository <repo_>`_.
   
      .. image:: _static/pycharm_github_commit3.png

.. _Execute setup.py commands:

Execute setup.py commands
-------------------------
The **setup.py** file should be run with various arguments in order to perform unittests, to create the documentation,
to distribute the **MSL-LoadLib** package or to install the **MSL-LoadLib** package. **MSL-LoadLib** uses pytest_ for
testing the source code and sphinx_ for creating the documentation.

.. note::
   The Python packages (e.g., pytest_ and sphinx_) that are required to execute the following commands are automatically
   installed (into the **.eggs** folder) if they are not already installed in the **msl** `virtual environment`_.
   Therefore, the first time that you run the **docs** or **tests** command it will take longer to finish executing the
   command because these packages (and their own dependencies) need to be downloaded then installed.

The following command will run all the tests in the **tests** folder as well as testing all the example code that is
located within the docstrings of the source code. A coverage_ report is generated in the **htmlcov/index.html** file.
This report provides an overview of which classes/functions/methods are being tested::

   $ python setup.py test

To build the documentation, which can be viewed by opening the **docs/_build/html/index.html** file, run::

   $ python setup.py docs

To automatically create the API documentation from the docstrings in the source code (uses sphinx-apidoc_), run::

   $ python setup.py apidoc

*NOTE: By default, the* **docs/_autosummary** *folder that is created by running the* **apidoc** *command is
automatically generated (it will overwrite existing files). As such, it is excluded from the repository (i.e., this
folder is specified in the* **.gitignore** *file). If you want to keep the files located in* **docs/_autosummary** *you
can rename the folder to be, for example,* **docs/_api** *and then the changes made to the files in the* **docs/_api**
*folder will be kept and will be included in the repository.*

.. _Edit the code using the style guide:

Edit the code using the style guide
-----------------------------------
Please follow the following style guides when contributing to **MSL-LoadLib**:

* Follow the :pep:`8` style guide when possible *(by default, PyCharm will notify you if you do not)*.
* Docstrings must be provided for all public classes, methods, and functions.
* For the docstrings use the `Google Style`_ format.

  * Press **CTRL + ALT + S** to open the **Settings** window and navigate to **Tools > Python Integrated Tools** to
    select the **Google** docstring format and then click **Apply** then **OK**.

    .. image:: _static/pycharm_google_style.png

* Do not use :func:`print` statements to notify the end-user of the status of a program. Use :mod:`logging` instead.
  This has the advantage that you can use different `logging levels`_ to decide what message types are displayed and
  which are ignored and you can also easily redirect all messages, for example, to a GUI widget or to a file.

.. _Miniconda: http://conda.pydata.org/miniconda.html
.. _Windows Command Prompt: http://www.computerhope.com/issues/chusedos.htm
.. _virtual environment: http://conda.pydata.org/docs/using/envs.html
.. _repo: https://github.com/MSLNZ/msl-loadlib
.. _git: https://git-scm.com/downloads
.. _GitHub: https://github.com/join?source=header-home
.. _githelp: https://www.atlassian.com/git/tutorials/
.. _version control system: https://en.wikipedia.org/wiki/Version_control
.. _Community Edition of PyCharm: https://www.jetbrains.com/pycharm/download/#section=windows
.. _IDE: https://en.wikipedia.org/wiki/Integrated_development_environment
.. _pytest: http://doc.pytest.org/en/latest/
.. _sphinx: http://www.sphinx-doc.org/en/latest/#
.. _sphinx-apidoc: http://www.sphinx-doc.org/en/stable/man/sphinx-apidoc.html
.. _wheel: http://pythonwheels.com/
.. _coverage: http://coverage.readthedocs.io/en/latest/index.html
.. _build_sphinx: http://www.sphinx-doc.org/en/latest/invocation.html#invocation-of-sphinx-build
.. _Google Style: http://www.sphinx-doc.org/en/latest/ext/example_google.html
.. _logging levels: https://docs.python.org/3/library/logging.html#logging-levels

.. [#f1] Software is identified in this guide in order to specify the installation and configuration procedure
         adequately. Such identification is not intended to imply recommendation or endorsement by the Measurement
         Standards Laboratory of New Zealand, nor is it intended to imply that the software identified are
         necessarily the best available for the purpose.
