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
.. _conda: https://conda.readthedocs.io/en/latest/
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
    def get_index_length(string):
        return line.find(string), len(string)

    if has_colorama:
        if 'SKIPPED' in line:
            i, n = get_index_length('SKIPPED')
            print(line[:i] + colorama.Fore.YELLOW + 'SKIPPED' + colorama.Fore.CYAN + line[i+n:])
        elif 'PASSED' in line:
            i, n = get_index_length('PASSED')
            print(line[:i] + colorama.Fore.GREEN + 'PASSED' + colorama.Fore.CYAN + line[i+n:])
        elif 'FAILED' in line:
            i, n = get_index_length('FAILED')
            print(line[:i] + colorama.Fore.RED + 'FAILED' + colorama.Fore.CYAN + line[i+n:])
        elif 'ERROR' in line:
            i, n = get_index_length('ERROR')
            print(line[:i] + colorama.Fore.RED + 'ERROR' + colorama.Fore.CYAN + line[i+n:])
        elif 'FAILURES' in line:
            print(colorama.Fore.RED + colorama.Style.BRIGHT + line)
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
        elif line.startswith('Install'):
            print(colorama.Fore.CYAN + colorama.Style.BRIGHT + line)
        elif line.startswith('***** '):
            print(colorama.Fore.YELLOW + line)
        else:
            print(line)
    else:
        print(line)


parser = argparse.ArgumentParser()
parser.add_argument('-s', '--show', action='store_true', help='show the conda envs to use then exit')
parser.add_argument('-i', '--include', default='', nargs='+', help='the conda envs to include')
parser.add_argument('-e', '--exclude', default='', nargs='+', help='the conda envs to exclude')
args = parser.parse_args()

# get a list of all conda envs
p = Popen(['conda', 'info', '--envs'], stdout=PIPE)
all_envs = [item.decode('utf-8') for item in p.communicate()[0].split() if 'envs' in item.decode('utf-8')]

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
        if compiled.search(os.path.basename(env)) is not None and env in envs:
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
    color_print('***** Testing with {} *****'.format(py_exe))

    proc = Popen([py_exe, 'setup.py', 'test'], stdout=PIPE, stderr=PIPE)

    show = False
    summary = ''
    while True:
        stdout = proc.stdout.readline().decode('utf-8').strip()
        if stdout.startswith('Reading'):
            color_print('Installing egg for' + stdout.split('Reading')[1])
            continue
        if stdout.startswith('Installed'):
            color_print(stdout)
            continue
        if not stdout and proc.poll() is not None:
            break
        if stdout.startswith('collect') and 'error' in stdout:  # errors during the "collecting..."
            summary += stdout
            success = False
            break
        if 'FAILURES' in summary:
            summary += stdout
            success = False
            break
        if stdout.startswith('='):
            show = True
        if show:
            summary += stdout
            color_print(stdout)
        if ' seconds =' in stdout:
            show = False  # once the test is finished a bunch of blank lines can be printed -- ignore these lines

    stdout = proc.stdout.read().decode('utf-8').strip()
    for item in stdout.split('\n'):
        color_print(item)

    summary += stdout
    if 'FAILURES' in summary or 'ERROR' in summary or 'FAILED' in summary or 'failed' in summary:
        success = False

    if not success:
        break
    else:
        print('\n')

if success:
    print('===================== conda envs summary =====================')
    for env in envs:
        color_print('All tests passed with ' + env)
