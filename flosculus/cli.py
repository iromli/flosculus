"""Flosculusd

Usage:
    flosculusd (-c <config>|--init)

Options:
    -h --help       Show this screen.
    -v --version    Show version.
"""
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)
import sys

import logbook
from docopt import docopt

from ._defaults import DEFAULT_CONFIG
from ._meta import __version__
from .core import Flosculus


def main():
    logger = logbook.Logger(__name__)
    arguments = docopt(__doc__, version=__version__)

    if arguments["--init"]:
        print(DEFAULT_CONFIG.strip())
        sys.exit(0)

    flosculus = Flosculus(arguments["<config>"])

    try:
        flosculus.run()
    except KeyboardInterrupt:
        logger.warn("Cancelled by user")
