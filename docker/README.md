Helper files and commands to freeze `server32-linux`.

Creates a docker image that contains the necessary packages to build a specified version of Python from source. After Python is installed, the 32-bit server is frozen.

1. Build the docker image.

   ```console
   docker build --platform linux/386 -t server32:latest .
   ```

2. Run the docker container.

   ```console
   docker run --mount type=bind,source="$PWD",target=/home --rm --platform linux/386 -it server32:latest
   ```

3. Install a version of Python that the 32-bit server will be frozen with. The following command will build Python with Profile Guided Optimization and Link Time Optimization enabled and it will run the Python test suite.

   *The i686 platform is no longer supported by the CPython core team, see [PEP-11](https://peps.python.org/pep-0011/), so running the tests is useful to know if there are issues with the version of Python you want to install.*

   ```console
   ./install-python.sh 3.15.0
   ```

   To skip building with optimizations and to skip running the tests, include the `--skip` flag.

   ```console
   ./install-python.sh 3.15.0 --skip
   ```

4. Freeze the 32-bit server. Specify the `msl-loadlib` version that this server will be bundled with.

   ```console
   ./freeze-server32.sh 1.2.0
   ```

5. Exit the container,

   ```console
   exit
   ```

   and the `server32-linux` executable is located in the current directory (on the host running docker).

   ```console
   ./server32-linux --version
   ```
