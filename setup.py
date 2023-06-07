import os
import re
import sys
from subprocess import check_output

from setuptools import Command
from setuptools import find_packages
from setuptools import setup


class ApiDocs(Command):
    """
    A custom command that calls sphinx-apidoc
    see: https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html
    """
    description = 'builds the api documentation using sphinx-apidoc'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        command = [
            None,  # in Sphinx < 1.7.0 the first command-line argument was parsed, in 1.7.0 it became argv[1:]
            '--force',  # overwrite existing files
            '--module-first',  # put module documentation before submodule documentation
            '--separate',  # put documentation for each module on its own page
            '-o', './docs/_autosummary',  # where to save the output files
            'msl',  # the path to the Python package to document
        ]

        import sphinx
        if sphinx.version_info[:2] < (1, 7):
            from sphinx.apidoc import main
        else:
            from sphinx.ext.apidoc import main
            command.pop(0)

        main(command)


class BuildDocs(Command):
    """
    A custom command that calls sphinx-build
    see: https://www.sphinx-doc.org/en/master/man/sphinx-build.html
    """
    description = 'builds the documentation using sphinx-build'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        command = [
            None,  # in Sphinx < 1.7.0 the first command-line argument was parsed, in 1.7.0 it became argv[1:]
            '-b', 'html',  # the builder to use, e.g., create a HTML version of the documentation
            '-a',  # generate output for all files
            '-E',  # ignore cached files, forces to re-read all source files from disk
            'docs',  # the source directory where the documentation files are located
            './docs/_build/html',  # where to save the output files
        ]

        import sphinx
        if sphinx.version_info[:2] < (1, 7):
            from sphinx import build_main
        else:
            from sphinx.cmd.build import build_main
            command.pop(0)

        build_main(command)


def read(filename):
    with open(filename) as fp:
        return fp.read()


def fetch_init(key):
    # open the __init__.py file to determine a value instead of importing the package
    return re.search(r'{}\s*=\s*(.+)'.format(key), read(init_original)).group(1).strip('\'\"')


def get_version():
    init_version = fetch_init('__version__')
    if 'dev' not in init_version or testing:
        return init_version

    if 'develop' in sys.argv:
        # then installing in editable (develop) mode
        #   python setup.py develop
        #   pip install -e .
        # following PEP-440, the local version identifier starts with '+'
        return init_version + '+editable'

    # append the commit hash to __version__
    setup_dir = os.path.dirname(os.path.realpath(__file__))
    try:
        # write all error messages from git to devnull
        with open(os.devnull, mode='w') as devnull:
            out = check_output(['git', 'rev-parse', 'HEAD'], cwd=setup_dir, stderr=devnull)
            sha1 = out.strip().decode()
    except:
        # the git executable is not available, manually parse .git directory
        try:
            git_dir = os.path.join(setup_dir, '.git')
            with open(os.path.join(git_dir, 'HEAD'), mode='rt') as fp1:
                line = fp1.readline().strip()
                if line.startswith('ref:'):
                    _, ref_path = line.split()
                    with open(os.path.join(git_dir, ref_path), mode='rt') as fp2:
                        sha1 = fp2.readline().strip()
                else:  # detached HEAD
                    sha1 = line
        except:
            return init_version

    suffix = sha1[:7]
    if not suffix or init_version.endswith(suffix):
        return init_version

    # following PEP-440, the local version identifier starts with '+'
    dev_version = init_version + '+' + suffix

    with open(init_original) as fp:
        init_source = fp.read()

    if os.path.isfile(init_backup):
        os.remove(init_backup)
    os.rename(init_original, init_backup)

    with open(init_original, mode='wt') as fp:
        fp.write(re.sub(
            r'__version__\s*=.+',
            "__version__ = '{}'".format(dev_version),
            init_source
        ))

    return dev_version


# auto generate the MANIFEST.in file depending on the distribution that is being built
if 'bdist_wheel' in sys.argv and 'sdist' in sys.argv:
    raise ValueError(
        'cannot specify bdist_wheel and sdist in the same command, '
        'run one option at a time'
    )
elif 'bdist_wheel' in sys.argv or 'install' in sys.argv:
    if sys.platform == 'win32':
        server32_suffix, extn = 'windows.exe', '.dll'
        if 'bdist_wheel' in sys.argv:
            if sys.maxsize > 2 ** 32:
                sys.argv.extend(['--universal', '--plat-name', 'win_amd64'])
            else:
                sys.argv.extend(['--universal', '--plat-name', 'win32'])
    elif sys.platform.startswith('linux'):
        server32_suffix, extn = 'linux', '.so'
        if 'bdist_wheel' in sys.argv:
            if sys.maxsize > 2 ** 32:
                sys.argv.extend(['--universal', '--plat-name', 'manylinux1_x86_64'])
            else:
                sys.argv.extend(['--universal', '--plat-name', 'manylinux1_i686'])
    elif sys.platform == 'darwin':
        server32_suffix, extn = None, '.dylib'
        if 'bdist_wheel' in sys.argv:
            sys.argv.append('--universal')
    else:
        server32_suffix, extn = None, None

    with open('MANIFEST.in', mode='wt') as f:
        f.write('# This file is automatically generated. Do not modify.\n')
        f.write('recursive-include msl/examples/loadlib *.jar *.class\n')
        f.write('include msl/loadlib/py4j-wrapper.jar\n')
        f.write('include msl/examples/loadlib/dotnet_lib32.dll\n')
        f.write('include msl/examples/loadlib/dotnet_lib64.dll\n')
        if server32_suffix is not None:
            f.write('recursive-include msl/loadlib server32-{}*\n'.format(server32_suffix))
        if extn is not None:
            f.write('recursive-include msl/examples/loadlib *{}\n'.format(extn))
elif 'sdist' in sys.argv:
    with open('MANIFEST.in', mode='wt') as f:
        f.write('# This file is automatically generated. Do not modify.\n')
        f.write('recursive-include msl *.cpp *.h *.cs *.f90 *.java *.jar *.class *.so *.dll *.txt *.dylib\n')
        f.write('exclude msl/loadlib/server32-*\n')

install_requires = []

tests_require = [
    'pytest>=4.4',  # >=4.4 to support the "-p conftest" option
    'pytest-cov',
    'py4j',
    'numpy',  # needed for [doctest] tutorials_cpp_array.rst
    'pythonnet',
    'pathlib;python_version<"3.0"',
    'comtypes;sys_platform=="win32"',
]

docs_require = ['sphinx', 'sphinx-rtd-theme']

testing = {'test', 'tests', 'pytest'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if testing else []

needs_sphinx = {'doc', 'docs', 'apidoc', 'apidocs', 'build_sphinx'}.intersection(sys.argv)
sphinx = docs_require + install_requires if needs_sphinx else []

init_original = 'msl/loadlib/__init__.py'
init_backup = init_original + '.backup'
version = get_version()

setup(
    name='msl-loadlib',
    version=version,
    author=fetch_init('__author__'),
    author_email='info@measurement.govt.nz',
    url='https://github.com/MSLNZ/msl-loadlib',
    description='Load a shared library (and access a 32-bit library from 64-bit Python)',
    long_description=read('README.rst'),
    license='MIT',
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development',
        'Topic :: Scientific/Engineering',
    ],
    setup_requires=sphinx + pytest_runner,
    tests_require=tests_require,
    install_requires=install_requires,
    extras_require={
        'clr': ['pythonnet'],
        'java': ['py4j'],
        'com': ['comtypes'],
        'all': ['pythonnet', 'py4j', 'comtypes'],
        'tests': tests_require,
        'docs': docs_require,
        'dev': tests_require + docs_require,
    },
    cmdclass={'docs': BuildDocs, 'apidocs': ApiDocs},
    packages=find_packages(include=('msl*',)),
    include_package_data=True,
)

if os.path.isfile(init_backup):
    os.remove(init_original)
    os.rename(init_backup, init_original)
