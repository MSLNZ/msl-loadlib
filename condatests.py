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

IS_WINDOWS = sys.platform == 'win32'
if IS_WINDOWS:
    CONDA_DIR, PYTHON_DIR, EXT = 'Scripts', '', '.exe'
    # Avoid getting "LookupError: unknown encoding: cp65001"
    if os.environ.get('PYTHONIOENCODING') is None:
        os.environ['PYTHONIOENCODING'] = 'utf-8'
else:
    CONDA_DIR, PYTHON_DIR, EXT = 'bin', 'bin', ''

EXECUTABLES = {'python', 'pypy', 'pypy3'}
CREATE_ENV_PREFIX = 'condatestsenv-'
INI_PATH = 'condatests.ini'


def get_conda_envs():
    try:
        p = subprocess.Popen(['conda', 'info', '--json'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except:
        # if calling this script from a virtual environment then a FileNotFoundError is raised
        # make sure conda is available
        base_dir = os.path.dirname(sys.executable)
        while True:
            parent_dir = os.path.abspath(os.path.join(base_dir, os.pardir))
            if len(parent_dir) <= 3:
                sys.exit('conda is not available on PATH')

            exe = os.path.join(parent_dir, CONDA_DIR, 'conda'+EXT)
            if os.path.isfile(exe):
                os.environ['PATH'] += os.pathsep + os.path.dirname(exe)
                return get_conda_envs()

            base_dir = parent_dir

    out, err = p.communicate()
    if err:
        sys.exit(err.decode())
    info = json.loads(out.decode('utf-8'))
    environs = dict()
    for env in info['envs']:
        if env == info['root_prefix']:
            key = 'base'
        else:
            key = re.sub(r'python', 'py', os.path.basename(env), flags=re.IGNORECASE)  # analogous with tox
        environs[key] = env
    return environs


def sort_envs(envs):
    return collections.OrderedDict([(key, envs[key]) for key in sorted(envs)])


def include(envs, args):
    environs = dict()
    if not args.include:
        return environs
    for key, value in envs.items():
        for pattern in args.include:
            if pattern == '*':
                pattern = '.*'
            if re.search(pattern, key):
                environs[key] = value
                break
    return sort_envs(environs)


def exclude(envs, args):
    environs = envs.copy()
    for key, value in envs.items():
        for pattern in args.exclude:
            if pattern == '*':
                pattern = '.*'
            if re.search(pattern, key):
                del environs[key]
                break
    return sort_envs(environs)


def print_envs(envs):
    if not envs:
        return
    max_len = max(map(len, envs.keys()))
    for key, value in envs.items():
        print('  {}  ->  {}'.format(key.ljust(max_len), value))


def get_executable(base_exec_path):
    path = os.path.join(base_exec_path, PYTHON_DIR)
    for item in EXECUTABLES:
        if os.path.isfile(os.path.join(path, item+EXT)):
            return [item]
    raise IOError('The only supported executables are: {}'.format(', '.join(EXECUTABLES)))


def ini_parser(path):
    ini = configparser.ConfigParser()
    ini.read(path)

    section = 'envs'
    if not ini.has_section(section):
        return {}

    def get_values(name):
        line = ini.get(section, name, fallback='')
        delim = ',' if ',' in line else None
        return [value.strip() for value in line.split(delim)]

    return {
        'create': get_values('create'),
        'include': get_values('include'),
        'exclude': get_values('exclude'),
        'requires': get_values('requires'),
        'command': ini.get(section, 'command', fallback=''),
    }


def cli_parser(args):
    p = argparse.ArgumentParser(description='Run the tests in conda environments.')
    p.add_argument('-l', '--list', action='store_true', help='list the conda environments that will be used '
                                                             'for the tests and then exit')
    p.add_argument('-s', '--show', action='store_true', help='alias for --list')
    p.add_argument('-c', '--create', default=[], nargs='+', help='the Python version numbers to use to create '
                                                                 'conda environments (e.g., 2 3.6 3.7.2)')
    p.add_argument('-m', '--command', default='pytest', help='the command to execute with each conda '
                                                             'environment [default: python -m pytest]')
    p.add_argument('-i', '--include', default=[], nargs='+', help='the conda environments to include (supports regex)')
    p.add_argument('-x', '--exclude', default=[], nargs='+', help='the conda environments to exclude (supports regex)')
    p.add_argument('-f', '--ini', default=INI_PATH, help='the path to the configuration file '
                                                         '[default: {}]'.format(INI_PATH))
    p.add_argument('-r', '--requires', default=[], nargs='+', help='additional packages to install for the tests '
                                                                   '(can also be a path to a file)')
    return p.parse_args(args)


def create_env(name, base_env_path, args):
    print('Creating the {!r} environment'.format(name))
    path = os.path.join(base_env_path, 'envs', name)
    p = subprocess.Popen(['conda', 'create', '--name', name, 'python=' + name[len(CREATE_ENV_PREFIX):], '--yes'],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if err:
        err = err.decode()
        if not err.lstrip().startswith('==> WARNING: A newer version of conda exists. <=='):
            sys.exit(err)

    test_packages = []
    if 'setup.py' in args.command or 'pytest' in args.command:
        test_packages.extend(['pytest', 'pytest-cov'])
        if 'setup.py' in args.command:
            test_packages.append('pytest-runner')
    elif 'nosetests' in args.command:
        test_packages.append('nose')

    ret = install_packages(name, test_packages)
    if ret:
        print(ret)
        remove_env(name)
        sys.exit()
    return path


def install_packages(env_name, packages_or_files):
    if not packages_or_files:
        return ''

    files = []
    packages = []
    for item in packages_or_files:
        if os.path.isfile(item):
            files.append('--file={}'.format(item))
        else:
            packages.append(item)
    packages.extend(files)

    print('Installing {} in the {!r} environment'.format(', '.join(packages), env_name))
    cmd = ['conda', 'install', '--name', env_name, '--channel', 'conda-forge', '--yes']
    p = subprocess.Popen(cmd + packages, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    err = err.decode()
    if not err.lstrip().startswith('==> WARNING: A newer version of conda exists. <=='):
        return err
    return ''


def remove_env(name):
    print('Removing the {!r} environment'.format(name))
    subprocess.call(['conda', 'remove', '--name', name, '--all', '--yes'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def main(*args):
    args = cli_parser(args)
    if os.path.isfile(args.ini):
        info = ini_parser(args.ini)
        if info:
            args.create.extend(info['create'])
            args.include.extend(info['include'])
            args.exclude.extend(info['exclude'])
            args.requires.extend(info['requires'])
            if info['command']:
                args.command = info['command']

    test_envs = collections.OrderedDict()

    for c in sorted(args.create):
        name = CREATE_ENV_PREFIX + c
        test_envs[name] = 'Python {} environment'.format(c)

    all_envs = get_conda_envs()
    inc_envs = include(all_envs, args) if args.include else all_envs
    if not args.include and not args.exclude:
        test_envs.update(all_envs)
    else:
        test_envs.update(exclude(inc_envs, args))

    if args.list or args.show:
        print('Test with the following conda environments:')
        print_envs(test_envs)
        return

    if not test_envs:
        print('No conda environments are being created nor match the include/exclude criteria')
        return

    command = args.command.split()
    if not command:
        print('You must specify the command to execute to run the tests')
        return
    typ = command[0]
    if typ.startswith('pytest') or typ.startswith('unittest') or typ.startswith('nose'):
        command.insert(0, '-m')

    executable = None if IS_WINDOWS else '/bin/bash'
    for name, path in test_envs.items():
        print('')

        if name.startswith(CREATE_ENV_PREFIX):
            path = create_env(name, all_envs['base'], args)

        ret = install_packages(name, args.requires)
        if ret:
            print(ret)
            if name.startswith(CREATE_ENV_PREFIX):
                remove_env(name)
            return

        activate = [] if IS_WINDOWS else ['source']
        activate.extend([os.path.join(all_envs['base'], CONDA_DIR, 'activate'), name])
        cmd = activate + ['&&'] + get_executable(path) + command + ['&&', 'conda', 'deactivate']
        print('Testing with the {!r} environment'.format(name))
        ret = subprocess.call(' '.join(cmd), shell=True, executable=executable)

        if name.startswith(CREATE_ENV_PREFIX):
            remove_env(name)

        if ret != 0:
            return

    print('\nAll tests passed with the following conda environments:')
    print_envs(test_envs)


if __name__ == '__main__':
    try:
        sys.exit(main(*sys.argv[1:]))
    except KeyboardInterrupt:
        pass
