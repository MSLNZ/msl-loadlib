import os
import sys
from setuptools import setup, find_packages
from setuptools.command.install import install

from msl import loadlib

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), 'docs'))
import docs_commands


class CustomInstall(install):
    """
    Customized install command that creates the .NET config file
    after the package has been installed.
    """
    def run(self):
        install.run(self)

        # allow executing the server32-* file as a program, make it read only and create the config file
        if loadlib.IS_WINDOWS or loadlib.IS_LINUX:
            import site
            for path in site.getsitepackages():
                if path.endswith('site-packages'):
                    os.chmod(os.path.join(path, 'msl', 'loadlib', loadlib.SERVER_FILENAME), 365)
        loadlib.LoadLibrary.check_dot_net_config(sys.executable)

        sys.exit(0)


def read(filename):
    with open(filename) as fp:
        text = fp.read()
    return text

testing = {'test', 'tests', 'pytest'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if testing else []

needs_sphinx = {'doc', 'docs', 'apidoc', 'apidocs', 'build_sphinx'}.intersection(sys.argv)
sphinx = ['sphinx', 'sphinx_rtd_theme'] if needs_sphinx else []

# pycparser is needed to install pythonnet on a non-Windows OS
# it does not automatically get installed before pythonnet is installed
install_requires = ['pycparser'] if not loadlib.IS_WINDOWS else []
install_requires += read('requirements.txt').splitlines() if not testing else []

setup(
    name='msl-loadlib',
    version=loadlib.__version__,
    author=loadlib.__author__,
    author_email='joseph.borbely@callaghaninnovation.govt.nz',
    url='https://github.com/MSLNZ/msl-loadlib',
    description='Load a shared library (and access a 32-bit library from 64-bit Python)',
    long_description=read('README.rst'),
    license='MIT',
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Physics',
    ],
    setup_requires=sphinx + pytest_runner,
    tests_require=['pytest-cov', 'pytest'],
    install_requires=install_requires,
    cmdclass={
        'install': CustomInstall,
        'docs': docs_commands.BuildDocs,
        'apidocs': docs_commands.ApiDocs
    },
    packages=find_packages(include=('msl*',)),
    include_package_data=True,
)
