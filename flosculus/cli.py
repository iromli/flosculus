"""Flosculusd

Usage:
    flosculusd -c <config>

Options:
    -h --help       Show this screen.
    -v --version    Show version.
"""
from .watcher import LogWatcher
from .sender import Sender

import configs
from docopt import docopt


def main():
    arguments = docopt(__doc__, version="v0.1")
    config = configs.load(arguments["<config>"])

    sender = Sender(
        config["input"]["tag"],
        **dict(format=config["input"]["format"])
    )

    watcher = LogWatcher(config["input"]["path"], sender.on_recv)
    watcher.loop()
