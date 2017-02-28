"""
At the time of writing this script, tox_ and conda_ did not "play nice" together, see here_,
and so this script provided a way around this issue. This script simulates tox_ by finding all conda_
environment_\'s (ignores the **root** env) and runs the unit tests with each environment_.

Usage:

Run the unit tests using all conda envs::

   $ python test_envs.py

Run the unit tests using all conda envs that include **py** in the env name::

   $ python test_envs.py -i py

Run the unit tests using all conda envs excluding those that contain **py26** and **py32** in the env name::

   $ python test_envs.py -e py26 py33

Show all the conda envs that are available and then exit::

   $ python test_envs.py -s

Show the conda envs that include **py** in the env name then exit::

   $ python test_envs.py -i py -s

Show the conda envs that include **py** in the env name *and* exclude those with **py33** in the name and then exit::

   $ python test_envs.py -i py -e py33 -s

.. _here: https://bitbucket.org/hpk42/tox/issues/273/support-conda-envs-when-using-miniconda
.. _tox: https://tox.readthedocs.io/en/latest/
.. _conda: http://conda.readthedocs.io/en/latest/
.. _environment: https://conda.io/docs/using/envs.html
"""
import re
import os
import sys
import argparse
from subprocess import Popen, PIPE

try:
    import colorama
    colorama.init(autoreset=True)
    has_colorama = True
except ImportError:
    has_colorama = False


def color_print(line):
    if has_colorama:
        if line.endswith('SKIPPED'):
            print(line[:-7] + colorama.Fore.YELLOW + 'SKIPPED')
        elif line.endswith('PASSED'):
            print(line[:-6] + colorama.Fore.GREEN + 'PASSED')
        elif line.endswith('FAILED'):
            print(line[:-6] + colorama.Fore.RED + 'FAILED')
        elif line.endswith('ERROR'):
            print(line[:-5] + colorama.Fore.RED + 'ERROR')
        elif line.startswith('___'):
            print(colorama.Fore.RED + colorama.Style.BRIGHT + line)
        elif line.startswith('E '):
            print(colorama.Fore.RED + colorama.Style.BRIGHT + line)
        elif line.startswith('=') and 'failed' in line:
            print(colorama.Fore.RED + colorama.Style.BRIGHT + line)
        elif line.startswith('=') and 'passed' in line:
            print(colorama.Fore.GREEN + colorama.Style.BRIGHT + line)
        elif line.startswith('=') and 'starts' in line:
            print(colorama.Style.BRIGHT + line)
        elif line.startswith('=') and 'summary' in line:
            print(colorama.Fore.GREEN + colorama.Style.BRIGHT + line)
        elif line.startswith('All tests passed'):
            print(colorama.Fore.GREEN + colorama.Style.BRIGHT + line)
        else:
            print(line)
    else:
        print(line)

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--show', action='store_true', help='show the conda envs to use then exit')
parser.add_argument('-i', '--include', default='', nargs='+', help='the conda envs to include')
parser.add_argument('-e', '--exclude', default='', nargs='+', help='the conda envs to exclude')
parser.add_argument('-t', '--timeout', default=10.0, help='abort after a timeout [default is 10 sec]')
args = parser.parse_args()

# get a list of all conda envs
p = Popen(['conda', 'info', '--envs'], stdout=PIPE)
all_envs = [item.decode() for item in p.communicate()[0].split() if 'envs' in item.decode()]

# perform the include filter
envs = [] if args.include else all_envs
for include in args.include:
    compiled = re.compile(include)
    for env in all_envs:
        if compiled.search(os.path.basename(env)) is not None:
            envs.append(env)

# perform the exclude filter
copy_envs = envs[:]
for exclude in args.exclude:
    compiled = re.compile(exclude)
    for env in copy_envs:
        if compiled.search(os.path.basename(env)) is not None:
            envs.remove(env)

if args.show:
    print('================ test with the following conda envs ================')
    for env in envs:
        print(env)
    sys.exit()

path = 'bin' if sys.platform.startswith('linux') or sys.platform == 'darwin' else ''

# run the tests
success = True
for env in envs:

    py_exe = os.path.join(env, path, 'python')
    print('Testing with ' + py_exe)

    proc = Popen([py_exe, 'setup.py', 'test'], stdout=PIPE, stderr=PIPE)

    show = False
    summary = ''
    while True:
        stdout = proc.stdout.readline().decode().strip()
        if stdout == '' and proc.poll() is not None:
            break
        if not stdout:
            # if there were any "import exceptions" and pytest could not
            # start properly then the output will be empty
            stderr = proc.stderr.read().decode()
            if stderr.startswith('Traceback'):
                print(stderr)
                success = False
                break
        if stdout.startswith('='):
            show = True
        if show:
            summary += stdout
            color_print(stdout)
        if ' seconds ===' in stdout:
            show = False  # once the test is finished a bunch of blank lines can be printed -- ignore these lines

    stdout = proc.stdout.read().decode().strip()
    for item in stdout.split('\n'):
        color_print(item)

    summary += stdout
    if 'FAILURES' in summary or 'ERRORS' in summary or 'FAILED' in summary or 'ERROR' in summary:
        success = False

    if not success:
        break
    else:
        print('\n')

if success:
    color_print('===================== conda envs summary =====================')
    for env in envs:
        color_print('All tests passed with ' + env)
