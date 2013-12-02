"""Flosculusd

Usage:
    flosculusd (-c <config>|--init)

Options:
    -h --help       Show this screen.
    -v --version    Show version.
"""
from __future__ import print_function
import sys

import logbook
from docopt import docopt

from .core import Flosculus
from ._meta import __version__
from ._defaults import DEFAULT_CONFIG

logger = logbook.Logger(__name__)


def main():
    arguments = docopt(__doc__, version="v{}".format(__version__))

    if arguments["--init"]:
        print(DEFAULT_CONFIG.strip())
        sys.exit(0)

    flosculus = Flosculus(arguments["<config>"])

    try:
        flosculus.run()
    except KeyboardInterrupt:
        logger.warn("Cancelled by user")
