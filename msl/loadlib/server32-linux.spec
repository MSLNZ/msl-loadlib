# -*- mode: python -*-

# Created using Python 3.6.8 and PyInstaller 3.4

block_cipher = None


a = Analysis(['/home/joe/msl-loadlib/msl/loadlib/start_server32.py'],
             pathex=['/home/joe/msl-loadlib/msl/loadlib'],
             binaries=[],
             datas=[('/home/joe/miniconda3/envs/loadlib/lib/python3.6/site-packages/Python.Runtime.dll', '.'), ('/home/joe/miniconda3/envs/loadlib/lib/python3.6/site-packages/clr.cpython-36m-i386-linux-gnu.so', '.'), ('/lib/i386-linux-gnu/libexpat.so.1', '.'), ('/lib/i386-linux-gnu/libglib-2.0.so.0', '.'), ('/lib/i386-linux-gnu/libpcre.so.3', '.'), ('/usr/lib/libmonosgen-2.0.so.1', '.')],
             hiddenimports=['msl.examples.loadlib', 'clr', '__future__', '_dummy_thread', '_thread', 'abc', 'aifc', 'argparse', 'array', 'ast', 'asynchat', 'asyncio', 'asyncore', 'atexit', 'audioop', 'base64', 'bdb', 'binascii', 'binhex', 'bisect', 'builtins', 'bz2', 'calendar', 'cgi', 'cgitb', 'chunk', 'cmath', 'cmd', 'code', 'codecs', 'codeop', 'collections', 'collections.abc', 'colorsys', 'compileall', 'concurrent.futures', 'configparser', 'contextlib', 'copy', 'copyreg', 'cProfile', 'crypt', 'csv', 'ctypes', 'curses', 'curses.ascii', 'curses.panel', 'curses.textpad', 'datetime', 'dbm', 'dbm.dumb', 'dbm.gnu', 'dbm.ndbm', 'decimal', 'difflib', 'dis', 'doctest', 'dummy_threading', 'email', 'email.charset', 'email.contentmanager', 'email.encoders', 'email.errors', 'email.generator', 'email.header', 'email.headerregistry', 'email.iterators', 'email.message', 'email.mime', 'email.parser', 'email.policy', 'email.utils', 'encodings.idna', 'encodings.mbcs', 'encodings.utf_8_sig', 'enum', 'errno', 'faulthandler', 'fcntl', 'filecmp', 'fileinput', 'fnmatch', 'formatter', 'fpectl', 'fractions', 'ftplib', 'functools', 'gc', 'getopt', 'getpass', 'gettext', 'glob', 'grp', 'gzip', 'hashlib', 'heapq', 'hmac', 'html', 'html.entities', 'html.parser', 'http', 'http.client', 'http.cookiejar', 'http.cookies', 'http.server', 'imaplib', 'imghdr', 'imp', 'importlib', 'importlib.abc', 'importlib.machinery', 'importlib.util', 'inspect', 'io', 'ipaddress', 'itertools', 'json', 'json.tool', 'keyword', 'lib2to3', 'linecache', 'locale', 'logging', 'logging.config', 'logging.handlers', 'lzma', 'macpath', 'mailbox', 'mailcap', 'marshal', 'math', 'mimetypes', 'mmap', 'modulefinder', 'multiprocessing', 'multiprocessing.connection', 'multiprocessing.dummy', 'multiprocessing.managers', 'multiprocessing.pool', 'multiprocessing.sharedctypes', 'netrc', 'nis', 'nntplib', 'numbers', 'operator', 'optparse', 'os', 'os.path', 'ossaudiodev', 'parser', 'pathlib', 'pdb', 'pickle', 'pickletools', 'pipes', 'pkgutil', 'platform', 'plistlib', 'poplib', 'posix', 'pprint', 'profile', 'pstats', 'pty', 'pwd', 'py_compile', 'pyclbr', 'pydoc', 'queue', 'quopri', 'random', 're', 'readline', 'reprlib', 'resource', 'rlcompleter', 'runpy', 'sched', 'secrets', 'select', 'selectors', 'shelve', 'shlex', 'shutil', 'signal', 'site', 'smtpd', 'smtplib', 'sndhdr', 'socket', 'socketserver', 'spwd', 'sqlite3', 'ssl', 'stat', 'statistics', 'string', 'stringprep', 'struct', 'subprocess', 'sunau', 'symbol', 'symtable', 'sys', 'sysconfig', 'syslog', 'tabnanny', 'tarfile', 'telnetlib', 'tempfile', 'termios', 'test', 'test.support', 'textwrap', 'threading', 'time', 'timeit', 'token', 'tokenize', 'trace', 'traceback', 'tracemalloc', 'tty', 'types', 'typing', 'unicodedata', 'unittest', 'unittest.mock', 'urllib', 'urllib.error', 'urllib.parse', 'urllib.request', 'urllib.response', 'urllib.robotparser', 'uu', 'uuid', 'venv', 'warnings', 'wave', 'weakref', 'webbrowser', 'wsgiref', 'wsgiref.handlers', 'wsgiref.headers', 'wsgiref.simple_server', 'wsgiref.util', 'wsgiref.validate', 'xdrlib', 'xml', 'xml.dom', 'xml.dom.minidom', 'xml.dom.pulldom', 'xml.etree.ElementTree', 'xml.parsers.expat', 'xml.parsers.expat.errors', 'xml.parsers.expat.model', 'xml.sax', 'xml.sax.handler', 'xml.sax.saxutils', 'xml.sax.xmlreader', 'xmlrpc.client', 'xmlrpc.server', 'zipapp', 'zipfile', 'zipimport', 'zlib'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['__main__', 'distutils', 'distutils.archive_util', 'distutils.bcppcompiler', 'distutils.ccompiler', 'distutils.cmd', 'distutils.command', 'distutils.command.bdist', 'distutils.command.bdist_dumb', 'distutils.command.bdist_msi', 'distutils.command.bdist_packager', 'distutils.command.bdist_rpm', 'distutils.command.bdist_wininst', 'distutils.command.build', 'distutils.command.build_clib', 'distutils.command.build_ext', 'distutils.command.build_py', 'distutils.command.build_scripts', 'distutils.command.check', 'distutils.command.clean', 'distutils.command.config', 'distutils.command.install', 'distutils.command.install_data', 'distutils.command.install_headers', 'distutils.command.install_lib', 'distutils.command.install_scripts', 'distutils.command.register', 'distutils.command.sdist', 'distutils.core', 'distutils.cygwinccompiler', 'distutils.debug', 'distutils.dep_util', 'distutils.dir_util', 'distutils.dist', 'distutils.errors', 'distutils.extension', 'distutils.fancy_getopt', 'distutils.file_util', 'distutils.filelist', 'distutils.log', 'distutils.msvccompiler', 'distutils.spawn', 'distutils.sysconfig', 'distutils.text_file', 'distutils.unixccompiler', 'distutils.util', 'distutils.version', 'ensurepip', 'tkinter', 'tkinter.scrolledtext', 'tkinter.tix', 'tkinter.ttk', 'turtle', 'turtledemo'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='server32-linux',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
