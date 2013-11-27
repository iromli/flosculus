"""Flosculusd

Usage:
    flosculusd -c <config>

Options:
    -h --help       Show this screen.
    -v --version    Show version.
"""
from .core import Flosculus
from ._meta import __version__

from docopt import docopt


def main():
    arguments = docopt(__doc__, version="v{}".format(__version__))

    flosculus = Flosculus(arguments["<config>"])
    flosculus.run()
