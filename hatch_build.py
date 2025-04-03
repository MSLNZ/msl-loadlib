"""Build custom wheels.

Each wheel bundles only the relevant files for the target platform.
This is not like building a C extension, but only helps to reduce
the file size of each wheel.

Command to build all wheels

$ hatch build -t custom

or, for example, to build a wheel for 32-bit Windows

$ hatch build -t custom:win32

The corresponding table that is defined in pyproject.toml is

[tool.hatch.build.targets.custom]
versions = [ ... ]

See https://hatch.pypa.io/latest/plugins/builder/custom/
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from hatchling.builders.wheel import WheelBuilder

if TYPE_CHECKING:
    from collections.abc import Iterable

    from hatchling.builders.plugin.interface import IncludedFile

# files that endswith() any of the following characters are added to the wheel
include = (".py", "py.typed", ".jar", ".class")

# the keys used here must be the same as the values in the "versions" array
# in the [tool.hatch.build.targets.custom] table of pyproject.toml
versions: dict[str, tuple[str, ...]] = {
    "linux_i686": (*include, "lib32.so", "linux", "linux.config", "dotnet_lib32.dll"),
    "linux_x86_64": (*include, ".so", "linux", "linux.config", "dotnet_lib32.dll", "dotnet_lib64.dll"),
    "macos_arm64": (*include, "libarm64.dylib"),
    "macos_x86_64": (*include, "lib64.dylib", "dotnet_lib32.dll", "dotnet_lib64.dll"),
    "win32": (*include, ".dll", ".exe", ".exe.config"),
    "win_amd64": (*include, ".dll", ".exe", ".exe.config"),
}


class CustomWheelBuilder(WheelBuilder):
    """Build custom wheels."""

    current_api: str = ""

    def build_linux_i686(self, directory: str, **build_data: Any) -> str:
        """Update the tag for a linux_i686 build."""
        self.current_api = "linux_i686"
        build_data["tag"] = "py3-none-manylinux1_i686"
        return self.build_standard(directory, **build_data)

    def build_linux_x86_64(self, directory: str, **build_data: Any) -> str:
        """Update the tag for a linux_x86_64 build."""
        self.current_api = "linux_x86_64"
        build_data["tag"] = "py3-none-manylinux1_x86_64"
        return self.build_standard(directory, **build_data)

    def build_macos_arm64(self, directory: str, **build_data: Any) -> str:
        """Update the tag for a macos_arm64 build."""
        self.current_api = "macos_arm64"
        build_data["tag"] = "py3-none-macosx_11_0_arm64"
        return self.build_standard(directory, **build_data)

    def build_macos_x86_64(self, directory: str, **build_data: Any) -> str:
        """Update the tag for a macos_x86_64 build."""
        self.current_api = "macos_x86_64"
        build_data["tag"] = "py3-none-macosx_10_6_x86_64"
        return self.build_standard(directory, **build_data)

    def build_win32(self, directory: str, **build_data: Any) -> str:
        """Update the tag for a win32 build."""
        self.current_api = "win32"
        build_data["tag"] = "py3-none-win32"
        return self.build_standard(directory, **build_data)

    def build_win_amd64(self, directory: str, **build_data: Any) -> str:
        """Update the tag for a win_amd64 build."""
        self.current_api = "win_amd64"
        build_data["tag"] = "py3-none-win_amd64"
        return self.build_standard(directory, **build_data)

    def get_version_api(self) -> dict[str, Callable[..., str]]:  # pyright: ignore[reportImplicitOverride]
        """Overrides abstractmethod BuilderInterface.get_version_api()."""
        return {
            "linux_i686": self.build_linux_i686,
            "linux_x86_64": self.build_linux_x86_64,
            "macos_arm64": self.build_macos_arm64,
            "macos_x86_64": self.build_macos_x86_64,
            "win32": self.build_win32,
            "win_amd64": self.build_win_amd64,
        }

    def recurse_included_files(self) -> Iterable[IncludedFile]:  # pyright: ignore[reportImplicitOverride]
        """Overrides WheelBuilder.recurse_included_files()."""
        for file in super().recurse_project_files():
            if file.path.endswith(versions[self.current_api]):
                yield file


def get_builder() -> type[CustomWheelBuilder]:
    """Adding this function fixes the following error.

    ValueError: Multiple subclasses of `BuilderInterface` found in `hatch_build.py`,
    select one by defining a function named `get_builder`
    """
    return CustomWheelBuilder
