"""Mocker.

Usage:
  mocker pull <name>[:<tag>]
  mocker (-h | --help)
  mocker --version

Options:
  -h --help     Show this screen.
  --version     Show version.
"""
from docopt import docopt
import mocker

if __name__ == '__main__':
    arguments = docopt(__doc__, version=mocker.__version__)
    print(arguments)
