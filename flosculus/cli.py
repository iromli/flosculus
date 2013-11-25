"""Flosculusd

Usage:
    flosculusd -c <config>

Options:
    -h --help       Show this screen.
    -v --version    Show version.
"""
from .core import Flosculus

import configparser
from docopt import docopt


def main():
    arguments = docopt(__doc__, version="v0.1")

    config = configparser.ConfigParser()
    config.read(arguments["<config>"])

    flosculus = Flosculus(config)
    flosculus.run()
