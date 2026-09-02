#!/bin/bash

# USAGE
# -----
# Install the specified version, enable optimizations and run the python test suite:
# ./install-python 3.15.0
#
# Install the specified version, skip optimizations and skip running the python test suite:
# ./install-python 3.15.0 --skip

set -e

LDFLAGS="-L/usr/local/lib -Wl,-rpath,/usr/local/lib"
CONFIG="--enable-shared --prefix=/usr"

# Python version without alpha/beta/rc identifier, e.g., 3.15.0rc1 -> 3.15.0
py_version=$(echo "$1" | awk -F "." '{printf "%d.%d.%d", $1, $2, $3}')
tarfile=Python-$1.tar.xz

if [[ -z "$1" ]]; then
  echo "Must specify a python version to install, e.g.,"
  echo "$0 3.15.0"
  echo "or to disable optimizations and running the tests, run"
  echo "$0 3.15.0 --skip"
  exit 1
fi

curl -O  https://www.python.org/ftp/python/$py_version/$tarfile
tar -xf $tarfile

cd Python-$1
if [[ "$2" == "--skip" ]]; then
  ./configure $CONFIG LDFLAGS="$LDFLAGS"
  make -j$(nproc)
else
  ./configure $CONFIG LDFLAGS="$LDFLAGS" --enable-optimizations --with-lto
  make -j$(nproc)
  make test -j$(nproc)
fi
echo "Installing Python $1 ..."
make install > /dev/null

cd ..
rm -rf Python-$1
rm $tarfile

echo Buildtime: $(date -d@${SECONDS} -u +%H:%M:%S) [HH:MM:SS]
