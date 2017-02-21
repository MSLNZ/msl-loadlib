import sys
from distutils.cmd import Command


class ApiDocs(Command):
    """
    A custom command that calls sphinx-apidoc
    see: http://www.sphinx-doc.org/en/latest/man/sphinx-apidoc.html
    """
    description = "builds the api documentation using sphinx-apidoc"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from sphinx.apidoc import main
        main([
            'sphinx-apidoc',
            '--force',  # Overwrite existing files
            '--module-first',  # Put module documentation before submodule documentation
            '--separate',  # Put documentation for each module on its own page
            '-o', './docs/_autosummary',
            'msl',
        ])
        sys.exit(0)


class BuildDocs(Command):
    """
    A custom command that calls sphinx-build
    see: http://www.sphinx-doc.org/en/latest/man/sphinx-build.html
    """
    description = "builds the documentation using sphinx-build"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from sphinx import build_main
        build_main([
            'sphinx-build',
            '-b', 'html',  # builder to use
            '-a',  # generate output for all files
            '-E',  # ignore cached files, forces to re-read all source files from disk
            'docs',  # source directory
            './docs/_build/html', # output directory
        ])
        sys.exit(0)
