"""Flosculusd

Usage:
    flosculusd -c <config>

Options:
    -h --help       Show this screen.
    -v --version    Show version.
"""
from .core import Flosculus
from ._meta import __version__

import configparser
from docopt import docopt


def main():
    arguments = docopt(__doc__, version="v{}".format(__version__))

    config = configparser.ConfigParser()
    config.read(arguments["<config>"])

    flosculus = Flosculus(config)
    flosculus.run()
