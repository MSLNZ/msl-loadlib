#!/bin/bash
# This script will install all pre-requisites for the MSL-LoadLib package.
#
# Essectiallialy getting everything installed so that you can create the 32-bit server 
#   $ python3 freeze_server32.py server32-linux.spec
#
# and compile the 32-bit versions of the C++ and FORTRAN source code:
#   $ g++ -fPIC cpp_lib.cpp -shared -o cpp_lib32.so
#   $ gfortran -fPIC -fno-underscoring fortran_lib.f90 -shared -o fortran_lib32.so
#

sudo apt-get update

# install g++ and gfortran

sudo apt-get -y install build-essential g++ gcc-multilib g++-multilib gfortran

# install Mono

sudo apt-get -y install software-properties-common libglib2.0-dev clang git 

sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF

echo "deb http://download.mono-project.com/repo/debian wheezy main" | sudo tee /etc/apt/sources.list.d/mono-xamarin.list

sudo apt-get update

sudo DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confnew" install mono-devel mono-complete referenceassemblies-pcl ca-certificates-mono nunit-console

# install and update pip

sudo apt-get -y install python3-pip

sudo -H pip3 install --upgrade pip

# install pythonnet (installing from pip3 did not work)

sudo -H pip3 install pycparser

git clone https://github.com/pythonnet/pythonnet.git

cd pythonnet/

sudo python3 setup.py install

# install pyinstaller

sudo -H pip3 install pyinstaller

# freeze server32

cd ~

git clone https://github.com/MSLNZ/msl-loadlib.git

cd msl-loadlib/msl/loadlib/

python3 freeze_server32.py server32-linux.spec



