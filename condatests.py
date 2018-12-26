"""
Run the tests in conda environments.

For more information see:
  https://msl-package-manager.readthedocs.io/en/latest/new_package_readme.html#create-readme-condatests
"""
import os
import re
import sys
import json
import argparse
import subprocess
import collections
try:
    import configparser
except ImportError:
    import ConfigParser as configparser  # Python 2

if sys.platform in {'win32', 'cygwin'}:
    BIN, EXT = '', '.exe'
else:
    BIN, EXT = 'bin', ''

EXECUTABLES = {'python', 'pypy', 'pypy3'}


def get_conda_envs():
    p = subprocess.Popen(['conda', 'info', '--json'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if err:
        sys.exit(err)
    info = json.loads(out.decode('utf-8'))
    environs = dict()
    for env in info['envs']:
        if env == info['root_prefix']:
            key = 'base'
        else:
            key = re.sub(r'python', 'py', os.path.basename(env), flags=re.IGNORECASE)  # analogous with tox
        environs[key] = env
    return environs


def include(envs, args):
    if not args.include:
        return envs
    environs = dict()
    for key, value in envs.items():
        for pattern in args.include:
            if re.search(pattern, key) is not None:
                environs[key] = value
                break
    return environs


def exclude(envs, args):
    environs = envs.copy()
    for key, value in envs.items():
        for pattern in args.exclude:
            if re.search(pattern, key) is not None:
                del environs[key]
                break
    return collections.OrderedDict([(key, environs[key]) for key in sorted(environs)])


def print_envs(envs):
    max_len = max(map(len, envs.keys()))
    for key, value in envs.items():
        print('  {}  ->  {}'.format(key.ljust(max_len), value))


def get_executable(env):
    path = os.path.join(env, BIN)
    for item in EXECUTABLES:
        exe = os.path.join(path, item+EXT)
        if os.path.isfile(exe):
            return [exe]
    raise IOError('The only supported executables are: {}'.format(', '.join(EXECUTABLES)))


def ini_parser():
    ini = configparser.ConfigParser()
    ini.read('condatests.ini')

    section = 'envs'
    if not ini.has_section(section):
        return None

    args = list()
    for option in ini.options(section):
        args.append('--' + option)
        args.extend([value.strip() for value in ini.get(section, option).split(',')])
    return args


def cli_parser(args):
    p = argparse.ArgumentParser(description='Run the tests in conda environments.')
    p.add_argument('-l', '--list', action='store_true', help='list the conda environments and then exit')
    p.add_argument('-s', '--show', action='store_true', help='alias for --list')
    p.add_argument('-i', '--include', default=[], nargs='+', help='the conda environments to include (supports regex)')
    p.add_argument('-x', '--exclude', default=[], nargs='+', help='the conda environments to exclude (supports regex)')
    p.add_argument('-c', '--command', default='setup.py tests', help='the command to execute with each environment')
    return p.parse_args(args)


def main(*args):
    if not args:
        args = ini_parser()
    args = cli_parser(args)

    envs = exclude(include(get_conda_envs(), args), args)
    if not envs:
        print('There are no conda environments that match the include/exclude criteria')
        return

    if args.list or args.show:
        print('Test with the following conda environments:')
        print_envs(envs)
        return

    command = args.command.split()
    typ = command[0]
    if typ.startswith('pytest') or typ.startswith('unittest') or typ.startswith('nose'):
        command.insert(0, '-m')

    for env in envs.values():
        cmd = get_executable(env) + command
        print('\nTesting with ' + ' '.join(cmd))
        if subprocess.call(cmd):
            return

    print('\nAll tests passed with the following conda environments:')
    print_envs(envs)


if __name__ == '__main__':
    try:
        sys.exit(main(*sys.argv[1:]))
    except KeyboardInterrupt:
        pass
