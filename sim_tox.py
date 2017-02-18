"""
tox and conda currently do not "play nice" together
see: https://bitbucket.org/hpk42/tox/issues/273/support-conda-envs-when-using-miniconda

This script simulates tox by finding all conda envs and executing "setup.py test" for each environment

Usage:

Perform the tests using all conda envs
$ python sim_tox.py

Perform the tests using all conda envs that contain 'py' in the env name
$ python sim_tox.py -i py

Perform the tests using all conda envs except those that contain 'py33' in the env name
$ python sim_tox.py -e py33

Show the conda envs that would be used to test the code then exit
$ python sim_tox.py --show

Show the conda envs that contain 'py' in the env name then exit
$ python sim_tox.py --show -i py

Show the conda envs that contain 'py' in the env name AND exclude those with 'py33' in the name and then exit
$ python sim_tox.py --show -i py -e py33
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
temp_envs = envs[:]
for exclude in args.exclude:
    compiled = re.compile(exclude)
    for env in temp_envs:
        if compiled.search(os.path.basename(env)) is not None:
            envs.remove(env)

if args.show:
    print('================ Test with the following conda envs ================')
    for env in envs:
        print(env)
    sys.exit(0)

# run the tests
for env in envs:
    print('testing with ' + env)
    p = subprocess.Popen(os.path.join(env, 'python') + ' setup.py test', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = p.communicate()[0].decode()
    if 'FAILURES' in output:
        print(output)
        sys.exit(0)
    else:
        show = False
        for line in output.split('\n'):
            if 'test session starts' in line:
                show = True
            if show:
                print(line)

print('===================== Simulate-tox summary =====================')
for env in envs:
    print('All tests passed with {}'.format(env))
