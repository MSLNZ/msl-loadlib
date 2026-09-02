#!/bin/bash

if [[ -z "$1" ]]; then
  echo "Specify a msl-loadlib tag to build the server, e.g.,"
  echo "$0 1.2.0"
  exit 1
fi

git clone --depth 1 https://github.com/MSLNZ/msl-loadlib.git
cd msl-loadlib

git config user.email "mock@docker.com"
git config user.name "mocker"
git tag -a v$1 -m "mock v$1"

pip3 install -U pip
pip3 install pyinstaller
pip3 install .

cd ..
freeze32 --import msl.examples.loadlib

echo
./server32-linux -m msl-loadlib/tests/check_server32_imports.py 2> /dev/null

echo "server32-linux --version"
./server32-linux --version

echo
echo "server32-linux is compatible with $(getconf GNU_LIBC_VERSION)"

cp server32-linux /home/server32-linux
rm -rf msl-loadlib/

echo
echo Buildtime: $(date -d@${SECONDS} -u +%H:%M:%S) [HH:MM:SS]
