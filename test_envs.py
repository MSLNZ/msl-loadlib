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
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--show', action='store_true', help='show the conda envs to use then exit')
parser.add_argument('-i', '--include', default='', nargs='+', help='the conda envs to include')
parser.add_argument('-e', '--exclude', default='', nargs='+', help='the conda envs to exclude')
args = parser.parse_args()

# get a list of all conda envs
p = subprocess.Popen(['conda', 'info', '--envs'], stdout=subprocess.PIPE)
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
for env in envs:
    print('testing with ' + env)
    p = subprocess.Popen([os.path.join(env, path, 'python'), 'setup.py', 'test'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    comm = p.communicate()
    output = comm[0].decode()
    error = comm[1].decode()
    if not output:
        # if there were any "import issues" and pytest could not start properly then the output will be empty
        print('The following error occurred:')
        print(error)
        sys.exit()
    if 'FAILURES' in output or 'FAILED' in output:
        print(output)
        sys.exit()
    else:
        show = False
        for line in output.split('\n'):
            if 'test session starts' in line:
                show = True
            if show:
                print(line)

print('===================== conda envs summary =====================')
for env in envs:
    print('All tests passed with ' + env)
