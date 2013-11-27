import time
from functools import partial

import configparser
from fluent.sender import FluentSender
from fluent import event

from .parser import Parser
from .watcher import LogWatcher


class ConfigError(Exception):
    pass


def config_from_inifile(inifile):
    config = configparser.ConfigParser()
    config.read(inifile)

    settings = {}
    try:
        settings["flosculus"] = dict(config["flosculus"])
    except KeyError:
        raise ConfigError(
            "config doesn't have {!r} section".format("flosculus")
        )

    try:
        remote_port = int(settings["flosculus"]["remote_port"])
    except ValueError:
        raise ConfigError(
            "remote_port must be an int: {!r}".format(
                settings["flosculus"]["remote_port"])
        )
    else:
        settings["flosculus"]["remote_port"] = remote_port

    settings["logs"] = {}
    for section, values in config.iteritems():
        if not section.startswith("log:"):
            continue
        path = section.rsplit(":")[1:][0]
        settings["logs"][path] = dict(values)
    return settings


class Flosculus(object):
    def __init__(self, config):
        self._config = config_from_inifile(config)
        self._watcher = partial(LogWatcher, self._config["logs"].keys())
        self._time_format = "%d/%b/%Y:%H:%M:%S"
        self._routes = {}

        for path, values in self._config["logs"].iteritems():
            tag_parts = values["tag"].split(".")
            self._routes[path] = {
                "parser": Parser(values["format"]),
                "sender": FluentSender(
                    tag_parts[0],
                    host=self._config["flosculus"]["remote_host"],
                    port=self._config["flosculus"]["remote_port"],
                ),
                "label": ".".join(tag_parts[1:]),
            }

    def on_recv(self, filename, lines):
        for line in iter(lines):
            route = self._routes.get(filename)
            if not route:
                continue

            parsed_line = route["parser"].parse(line)

            if not parsed_line:
                continue

            ts = time.strptime(
                parsed_line["time"].split()[0], self._time_format)

            event.Event(
                route["label"],
                parsed_line,
                time=int(time.mktime(ts)),
                sender=route["sender"],
            )

    def run(self):
        watcher = self._watcher(self.on_recv)
        watcher.loop()
