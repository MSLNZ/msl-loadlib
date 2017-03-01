import os
import sys
from setuptools import setup, find_packages
from setuptools.command.install import install

from msl import loadlib

here = os.path.abspath(os.path.dirname(__file__))

sys.path.insert(0, os.path.join(here, 'docs'))
import docs_commands


class CustomInstall(install):
    """
    Customized install command that creates the .NET config file
    after the package has been installed.
    """
    def run(self):
        install.run(self)
        loadlib.LoadLibrary.check_dot_net_config(sys.executable)

        # allow executing the server32-* file as a program and make it read only
        if loadlib.IS_WINDOWS or loadlib.IS_LINUX:
            import stat
            f = os.path.join(here, 'msl', 'loadlib', loadlib.SERVER_FILENAME)
            os.chmod(f, stat.S_IRUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

        sys.exit(0)


def read(filename):
    with open(filename) as fp:
        text = fp.read()
    return text

testing = {'test', 'tests', 'pytest'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if testing else []

needs_sphinx = {'doc', 'docs', 'apidoc', 'apidocs', 'build_sphinx'}.intersection(sys.argv)
sphinx = ['sphinx', 'sphinx_rtd_theme'] if needs_sphinx else []

setup(
    name='msl-loadlib',
    version=loadlib.__version__,
    author=loadlib.__author__,
    author_email='joseph.borbely@callaghaninnovation.govt.nz',
    url='https://github.com/MSLNZ/msl-loadlib',
    description='Load a shared library (access a 32-bit library from 64-bit Python)',
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
    install_requires=read('requirements.txt').split() if not testing else [],
    cmdclass={
        'install': CustomInstall,
        'docs': docs_commands.BuildDocs,
        'apidocs': docs_commands.ApiDocs
    },
    packages=find_packages(include=('msl*',)),
    include_package_data=True,
)
